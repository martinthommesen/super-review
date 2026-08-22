#!/usr/bin/env python3
"""Digest-gated, annotation-preserving commit of validated FINDINGS.md bytes.

The candidate is opened once without following its final path component. Those
exact immutable bytes are validated, staged, and committed. The helper never
re-reads the candidate path after validation.

Concurrency scope: the advisory lock and digest gate fully serialize
cooperating writers that use this helper. A non-cooperating writer racing the
final instant of replacement can still win or lose that race; such writers are
detected best-effort, up to the last pre-replacement read and the post-write
verification.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import re
import stat
import sys
import tempfile
import time
from pathlib import Path
from types import ModuleType
from typing import BinaryIO

_SCRIPT_DIR = Path(__file__).resolve(strict=True).parent


def _load_sibling(module_name: str, filename: str) -> ModuleType:
    """Load a bundled sibling by canonical path, never by cwd or import search."""
    leaf = _SCRIPT_DIR / filename
    try:
        info = os.lstat(leaf)
    except OSError as exc:
        raise RuntimeError(
            f"cannot inspect bundled sibling module {leaf}: {exc}"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise RuntimeError(f"unsafe bundled sibling module: {leaf}")
    sibling = leaf.resolve(strict=True)
    if sibling.parent != _SCRIPT_DIR:
        raise RuntimeError(f"bundled sibling escapes script directory: {sibling}")
    spec = importlib.util.spec_from_file_location(module_name, sibling)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load bundled sibling module: {sibling}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_VALIDATOR = _load_sibling("_super_review_validate_findings", "validate_findings.py")
validate_bytes = _VALIDATOR.validate_bytes
canonical_root_error = _VALIDATOR.canonical_root_error
MAX_REPORT_BYTES = _VALIDATOR.MAX_REPORT_BYTES

EXIT_VALIDATION = 2
EXIT_CONFLICT = 3
EXIT_IO = 4

DIGEST_RE = re.compile(r"^(?:sha256:)?([0-9a-fA-F]{64})$")


class CommitError(RuntimeError):
    pass


class ConflictError(CommitError):
    pass


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _canonical_leaf(path: Path) -> Path:
    expanded = path.expanduser()
    if not expanded.name:
        raise CommitError(f"path has no filename: {path}")
    try:
        parent = expanded.parent.resolve(strict=True)
    except OSError as exc:
        raise CommitError(f"cannot resolve parent of {path}: {exc}") from exc
    return parent / expanded.name


def _normalize_expected(value: str) -> str:
    if value == "MISSING":
        return value
    match = DIGEST_RE.fullmatch(value)
    if not match:
        raise ValueError(
            "expected digest must be MISSING, 64 hexadecimal characters, or sha256:<64 hex>"
        )
    return f"sha256:{match.group(1).lower()}"


def _digest(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _same_identity(*infos: os.stat_result) -> bool:
    identities = {(info.st_dev, info.st_ino) for info in infos}
    return len(identities) == 1


def _read_regular_bytes_no_follow(
    path: Path, *, label: str
) -> tuple[bytes, os.stat_result]:
    try:
        before = os.lstat(path)
    except OSError as exc:
        raise CommitError(f"cannot inspect {label} {path}: {exc}") from exc
    if stat.S_ISLNK(before.st_mode):
        raise CommitError(f"refusing symbolic-link {label}: {path}")
    if not stat.S_ISREG(before.st_mode):
        raise CommitError(f"{label} must be a regular file: {path}")
    if before.st_size > MAX_REPORT_BYTES:
        raise CommitError(
            f"{label} exceeds {MAX_REPORT_BYTES} byte safety limit: {path}"
        )

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_BINARY", 0)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags | no_follow)
    except OSError as exc:
        raise CommitError(
            f"cannot open {label} without following a symlink {path}: {exc}"
        ) from exc
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            raise CommitError(f"opened {label} is not a regular file: {path}")
        if opened.st_size > MAX_REPORT_BYTES:
            raise CommitError(
                f"{label} exceeds {MAX_REPORT_BYTES} byte safety limit: {path}"
            )
        if not _same_identity(before, opened):
            raise CommitError(
                f"{label} path changed between inspection and open: {path}"
            )

        chunks: list[bytes] = []
        total = 0
        while True:
            read_size = min(1024 * 1024, MAX_REPORT_BYTES + 1 - total)
            chunk = os.read(fd, read_size)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_REPORT_BYTES:
                raise CommitError(
                    f"{label} exceeds {MAX_REPORT_BYTES} byte safety limit: {path}"
                )
        after_fd = os.fstat(fd)
    finally:
        os.close(fd)

    try:
        after_path = os.lstat(path)
    except OSError as exc:
        raise CommitError(f"{label} changed while being read {path}: {exc}") from exc
    if stat.S_ISLNK(after_path.st_mode) or not _same_identity(
        before, opened, after_fd, after_path
    ):
        raise CommitError(f"{label} path changed while being read: {path}")
    if any(
        getattr(opened, field, None) != getattr(after_fd, field, None)
        for field in ("st_size", "st_mtime_ns", "st_ctime_ns")
    ):
        raise CommitError(f"{label} contents changed while being read: {path}")
    return b"".join(chunks), opened


def _read_target(target: Path) -> tuple[str, bytes, os.stat_result | None]:
    try:
        os.lstat(target)
    except FileNotFoundError:
        return "MISSING", b"", None
    except OSError as exc:
        raise CommitError(f"cannot inspect {target}: {exc}") from exc
    data, info = _read_regular_bytes_no_follow(target, label="target")
    return _digest(data), data, info


def _parse_human_blocks_bytes(data: bytes) -> dict[str, bytes]:
    """Extract protected blocks byte-for-byte via the canonical shared scanner.

    The validator's ``scan_report_structure`` is the single structure grammar;
    the writer holds no parser of its own, so bytes can never be structurally
    valid to one program and invalid to the other.
    """
    scan = _VALIDATOR.scan_report_structure(data)
    if scan.errors:
        raise CommitError("; ".join(scan.errors))
    return {block.block_id: block.raw for block in scan.blocks}


def _verify_human_blocks(current: bytes, candidate: bytes) -> None:
    current_blocks = _parse_human_blocks_bytes(current)
    candidate_blocks = _parse_human_blocks_bytes(candidate)
    for block_id, raw in current_blocks.items():
        if block_id not in candidate_blocks:
            raise CommitError(f"candidate omits protected human block {block_id!r}")
        if candidate_blocks[block_id] != raw:
            raise CommitError(f"candidate changes protected human block {block_id!r}")


class AdvisoryLock:
    """Out-of-repository advisory lock shared by bundled commit invocations."""

    def __init__(self, root: Path, timeout_seconds: float) -> None:
        key = hashlib.sha256(os.fsencode(str(root))).hexdigest()
        uid = getattr(os, "getuid", lambda: "user")()
        lock_dir = Path(tempfile.gettempdir()) / f"super-review-locks-{uid}"
        lock_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = os.lstat(lock_dir)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise CommitError(f"unsafe advisory-lock directory: {lock_dir}")
        with contextlib.suppress(OSError):
            os.chmod(lock_dir, 0o700)
        self.path = lock_dir / f"{key}.lock"
        self.timeout_seconds = timeout_seconds
        self.handle: BinaryIO | None = None

    def __enter__(self) -> "AdvisoryLock":
        flags = (
            os.O_RDWR
            | os.O_CREAT
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_BINARY", 0)
        )
        flags |= getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(self.path, flags, 0o600)
        except OSError as exc:
            raise CommitError(f"cannot open advisory lock {self.path}: {exc}") from exc
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            os.close(fd)
            raise CommitError(f"advisory lock is not a regular file: {self.path}")
        self.handle = os.fdopen(fd, "r+b", closefd=True)
        if self.handle.seek(0, os.SEEK_END) == 0:
            self.handle.write(b"\0")
            self.handle.flush()
        deadline = time.monotonic() + self.timeout_seconds

        if os.name == "nt":
            import msvcrt

            while True:
                try:
                    self.handle.seek(0)
                    msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise ConflictError(
                            f"timed out acquiring advisory lock {self.path}"
                        )
                    time.sleep(0.05)
        else:
            import fcntl

            while True:
                try:
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise ConflictError(
                            f"timed out acquiring advisory lock {self.path}"
                        )
                    time.sleep(0.05)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        if self.handle is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self.handle.seek(0)
                with contextlib.suppress(OSError):
                    msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                with contextlib.suppress(OSError):
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()
            self.handle = None


def _set_mode(fd: int, path: Path, mode: int) -> None:
    fchmod = getattr(os, "fchmod", None)
    if fchmod is not None:
        fchmod(fd, mode)
    else:
        # Windows before Python 3.13 lacks os.fchmod; the descriptor's path
        # was just created by this process, so chmod by name is equivalent.
        os.chmod(path, mode)


def _write_temp(root: Path, candidate: bytes, mode: int | None) -> Path:
    fd, raw_path = tempfile.mkstemp(
        prefix=".FINDINGS.md.super-review.", suffix=".tmp", dir=root
    )
    temp_path = Path(raw_path)
    try:
        _set_mode(fd, temp_path, stat.S_IMODE(mode if mode is not None else 0o644))
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(candidate)
            handle.flush()
            os.fsync(handle.fileno())
        return temp_path
    except BaseException:
        with contextlib.suppress(OSError):
            os.close(fd)
        with contextlib.suppress(OSError):
            temp_path.unlink()
        raise


def _fsync_directory(path: Path) -> None:
    flags = getattr(os, "O_DIRECTORY", 0) | os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        return
    try:
        with contextlib.suppress(OSError):
            os.fsync(fd)
    finally:
        os.close(fd)


def commit_bytes(
    *,
    repo_root: Path,
    candidate_bytes: bytes,
    expected_digest: str,
    lock_timeout: float,
    dry_run: bool,
    source: str = "<bytes>",
    candidate_stat: os.stat_result | None = None,
) -> dict[str, str]:
    """Validate and commit immutable candidate bytes under digest concurrency.

    This is the single write core. Path-based ``commit()`` reads the candidate
    once without following its final component, then delegates here. Optional
    ``candidate_stat`` enables the path-only hard-link-to-target refusal.
    """
    if len(candidate_bytes) > MAX_REPORT_BYTES:
        raise CommitError(f"{source} exceeds {MAX_REPORT_BYTES} byte safety limit")

    requested_root = repo_root.expanduser().absolute()
    root = requested_root.resolve(strict=True)
    if not root.is_dir():
        raise CommitError(f"repository root is not a directory: {root}")

    target = root / "FINDINGS.md"
    validation = validate_bytes(candidate_bytes, source=source)
    if not validation.ok:
        detail = "\n".join(f"  - {item}" for item in validation.errors)
        raise CommitError(f"candidate report validation failed:\n{detail}")

    # The candidate must belong to this repository. A report generated for a
    # different root (for example, two concurrent reviews colliding on a shared
    # candidate path) is refused rather than written into the wrong FINDINGS.md.
    location_error = canonical_root_error(
        candidate_bytes.decode("utf-8"), requested_root
    )
    if location_error:
        raise CommitError(
            f"candidate does not belong to this repository: {location_error}"
        )
    candidate_digest = _digest(candidate_bytes)

    with AdvisoryLock(root, lock_timeout):
        actual_digest, current_bytes, current_info = _read_target(target)
        if (
            candidate_stat is not None
            and current_info is not None
            and _same_identity(candidate_stat, current_info)
        ):
            raise CommitError("candidate must not be the target through a hard link")
        if actual_digest != expected_digest:
            raise ConflictError(
                f"FINDINGS.md changed: expected {expected_digest}, found {actual_digest}; reread, revalidate, and regenerate"
            )
        _verify_human_blocks(current_bytes, candidate_bytes)

        second_digest, second_bytes, second_info = _read_target(target)
        if second_digest != expected_digest:
            raise ConflictError(
                f"FINDINGS.md changed before replacement: expected {expected_digest}, found {second_digest}"
            )
        _verify_human_blocks(second_bytes, candidate_bytes)

        if dry_run:
            return {
                "path": str(target),
                "previous_sha256": actual_digest,
                "candidate_sha256": candidate_digest,
                "status": "validated-dry-run",
            }

        temp_path = _write_temp(
            root,
            candidate_bytes,
            second_info.st_mode if second_info is not None else 0o644,
        )
        try:
            final_digest, final_bytes, _ = _read_target(target)
            if final_digest != expected_digest:
                raise ConflictError(
                    "FINDINGS.md changed after candidate staging; refusing to overwrite concurrent edits"
                )
            _verify_human_blocks(final_bytes, candidate_bytes)

            if expected_digest == "MISSING":
                link = getattr(os, "link", None)
                created_via_link = False
                if link is not None:
                    try:
                        try:
                            link(temp_path, target, follow_symlinks=False)
                        except (NotImplementedError, TypeError):
                            # Platforms lacking follow_symlinks support still
                            # get an atomic create-if-absent from plain link.
                            link(temp_path, target)
                        created_via_link = True
                    except FileExistsError as exc:
                        raise ConflictError(
                            "FINDINGS.md appeared before creation; refusing to overwrite it"
                        ) from exc
                    except OSError:
                        # Filesystems without hard-link support (some SMB,
                        # FUSE, and exFAT mounts) refuse link entirely; the
                        # O_CREAT|O_EXCL create below is equally atomic.
                        created_via_link = False
                if not created_via_link:
                    creation_flags = (
                        os.O_WRONLY
                        | os.O_CREAT
                        | os.O_EXCL
                        | getattr(os, "O_CLOEXEC", 0)
                        | getattr(os, "O_BINARY", 0)
                    )
                    try:
                        creation_fd = os.open(target, creation_flags, 0o644)
                    except FileExistsError as exc:
                        raise ConflictError(
                            "FINDINGS.md appeared before creation; refusing to overwrite it"
                        ) from exc
                    try:
                        _set_mode(creation_fd, target, 0o644)
                        with os.fdopen(creation_fd, "wb", closefd=True) as handle:
                            handle.write(candidate_bytes)
                            handle.flush()
                            os.fsync(handle.fileno())
                    except BaseException:
                        with contextlib.suppress(OSError):
                            os.unlink(target)
                        raise
                temp_path.unlink()
            else:
                os.replace(temp_path, target)
            _fsync_directory(root)
        finally:
            with contextlib.suppress(FileNotFoundError):
                temp_path.unlink()

        committed_digest, committed_bytes, _ = _read_target(target)
        if committed_digest != candidate_digest or committed_bytes != candidate_bytes:
            raise CommitError(
                f"post-write verification failed: expected {candidate_digest}, found {committed_digest}"
            )

    return {
        "path": str(target),
        "previous_sha256": actual_digest,
        "candidate_sha256": candidate_digest,
        "committed_sha256": candidate_digest,
        "status": "committed",
    }


def commit(
    *,
    repo_root: Path,
    candidate_path: Path,
    expected_digest: str,
    lock_timeout: float,
    dry_run: bool,
) -> dict[str, str]:
    """Path front-end: read the candidate once, then delegate to ``commit_bytes``."""
    requested_root = repo_root.expanduser().absolute()
    root = requested_root.resolve(strict=True)
    if not root.is_dir():
        raise CommitError(f"repository root is not a directory: {root}")

    target = root / "FINDINGS.md"
    candidate = _canonical_leaf(candidate_path)
    if candidate == target:
        raise CommitError("candidate must be generated outside the target path")
    if _is_within(candidate, root):
        raise CommitError("candidate must be outside the repository root")

    # Open once, without following the final component. Validate and commit these
    # exact bytes even if the path is renamed or replaced afterward.
    candidate_bytes, candidate_info = _read_regular_bytes_no_follow(
        candidate, label="candidate"
    )
    return commit_bytes(
        repo_root=repo_root,
        candidate_bytes=candidate_bytes,
        expected_digest=expected_digest,
        lock_timeout=lock_timeout,
        dry_run=dry_run,
        source=str(candidate),
        candidate_stat=candidate_info,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely replace a root FINDINGS.md only when its digest still matches."
    )
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--lock-timeout", type=float, default=30.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        expected = _normalize_expected(args.expected_sha256)
        result = commit(
            repo_root=args.repo_root,
            candidate_path=args.candidate,
            expected_digest=expected,
            lock_timeout=max(0.0, args.lock_timeout),
            dry_run=args.dry_run,
        )
    except ConflictError as exc:
        print(f"conflict: {exc}", file=sys.stderr)
        return EXIT_CONFLICT
    except (CommitError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_VALIDATION
    except OSError as exc:
        print(f"I/O error: {exc}", file=sys.stderr)
        return EXIT_IO

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['status']}: {result['path']}")
        print(f"previous: {result['previous_sha256']}")
        print(f"candidate: {result['candidate_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
