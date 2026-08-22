#!/usr/bin/env python3
"""Validate and publish exact FINDINGS.md bytes with conflict recovery.

The helper pins the destination, serializes cooperating writers, and verifies
the digest-gated target before and after publication. Failures detected after
an existing-target exchange preserve the remaining recovery leaf instead of
attempting a second exchange.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import stat
import sys
from pathlib import Path
from types import ModuleType

_SCRIPT_DIR = Path(__file__).resolve(strict=True).parent


def _load_sibling(module_name: str, filename: str) -> ModuleType:
    """Load a bundled sibling by canonical path, never by import search."""
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
    previous = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except (Exception, SystemExit):
        if previous is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous
        raise
    return module


_VALIDATOR = _load_sibling("_super_review_validate_findings", "validate_findings.py")
_REPORT_STORE = _VALIDATOR._REPORT_STORE
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
    try:
        expanded = path.expanduser()
    except (OSError, RuntimeError, ValueError) as exc:
        raise CommitError(f"cannot expand candidate path {path}: {exc}") from exc
    if not expanded.name:
        raise CommitError(f"path has no filename: {path}")
    try:
        parent = expanded.parent.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
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


def _parse_human_blocks_bytes(data: bytes) -> dict[str, bytes]:
    """Extract exact protected blocks with the validator's canonical scanner."""
    scan = _VALIDATOR.scan_report_structure(data)
    if scan.errors:
        raise CommitError("; ".join(scan.errors))
    return {block.block_id: block.raw for block in scan.blocks}


def _verify_human_blocks(current: bytes, candidate: bytes) -> None:
    """Reject a candidate that drops or changes a protected block."""
    current_blocks = _parse_human_blocks_bytes(current)
    candidate_blocks = _parse_human_blocks_bytes(candidate)
    for block_id, raw in current_blocks.items():
        if block_id not in candidate_blocks:
            raise CommitError(f"candidate omits protected human block {block_id!r}")
        if candidate_blocks[block_id] != raw:
            raise CommitError(f"candidate changes protected human block {block_id!r}")


def _open_store(repo_root: Path) -> object:
    try:
        return _REPORT_STORE.ReportStore.open(
            repo_root, max_bytes=MAX_REPORT_BYTES, mutation=False
        )
    except _REPORT_STORE.UnsafePathError as exc:
        raise CommitError(str(exc)) from exc
    except _REPORT_STORE.StoreConflictError as exc:
        raise ConflictError(str(exc)) from exc


def _commit_captured(
    *,
    store: object,
    candidate_bytes: bytes,
    expected_digest: str,
    lock_timeout: float,
    dry_run: bool,
    source: str,
    candidate_stat: os.stat_result | None,
) -> dict[str, str]:
    if len(candidate_bytes) > MAX_REPORT_BYTES:
        raise CommitError(f"{source} exceeds {MAX_REPORT_BYTES} byte safety limit")
    validation = validate_bytes(candidate_bytes, source=source)
    if not validation.ok:
        detail = "\n".join(f"  - {item}" for item in validation.errors)
        raise CommitError(f"candidate report validation failed:\n{detail}")

    assert isinstance(store, _REPORT_STORE.ReportStore)
    try:
        store.directory.assert_path_binding()
    except _REPORT_STORE.StoreConflictError as exc:
        raise ConflictError(str(exc)) from exc
    location_error = canonical_root_error(
        candidate_bytes.decode("utf-8"),
        store.root,
        expected_is_resolved=True,
    )
    if location_error:
        raise CommitError(
            f"candidate does not belong to this repository: {location_error}"
        )
    try:
        store.directory.assert_path_binding()
        if not dry_run:
            store.directory.require_mutation_support()
    except _REPORT_STORE.StoreConflictError as exc:
        raise ConflictError(str(exc)) from exc

    candidate = _REPORT_STORE.ExactPayload.from_bytes(candidate_bytes)
    candidate_identity = None
    if candidate_stat is not None:
        captured_identity = _REPORT_STORE.FileIdentity.from_stat(candidate_stat)
        if captured_identity.meaningful:
            candidate_identity = captured_identity
    try:
        receipt = store.compare_and_publish(
            candidate=candidate,
            expected_digest=_normalize_expected(expected_digest),
            candidate_identity=candidate_identity,
            lock_timeout=max(0.0, lock_timeout),
            dry_run=dry_run,
            guard_current=lambda current: _verify_human_blocks(
                current, candidate_bytes
            ),
        )
    except _REPORT_STORE.UnsafePathError as exc:
        raise CommitError(str(exc)) from exc
    except _REPORT_STORE.StoreConflictError as exc:
        raise ConflictError(str(exc)) from exc

    result = {
        "path": str(store.root / store.TARGET),
        "previous_sha256": receipt.previous.digest,
        "candidate_sha256": candidate.digest,
        "status": receipt.status,
    }
    if receipt.committed is not None:
        result["committed_sha256"] = receipt.committed.digest
    return result


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
    """Validate and publish one immutable candidate byte sequence."""
    store = _open_store(repo_root)
    assert isinstance(store, _REPORT_STORE.ReportStore)
    with store:
        return _commit_captured(
            store=store,
            candidate_bytes=candidate_bytes,
            expected_digest=expected_digest,
            lock_timeout=lock_timeout,
            dry_run=dry_run,
            source=source,
            candidate_stat=candidate_stat,
        )


def commit(
    *,
    repo_root: Path,
    candidate_path: Path,
    expected_digest: str,
    lock_timeout: float,
    dry_run: bool,
) -> dict[str, str]:
    """Read an outside-repository candidate once, then publish those bytes."""
    store = _open_store(repo_root)
    assert isinstance(store, _REPORT_STORE.ReportStore)
    with store:
        target = store.root / store.TARGET
        candidate = _canonical_leaf(candidate_path)
        if candidate == target:
            raise CommitError("candidate must be generated outside the target path")
        if _is_within(candidate, store.root):
            raise CommitError("candidate must be outside the repository root")
        candidate_bytes, candidate_info = _read_regular_bytes_no_follow(
            candidate, label="candidate"
        )
        return _commit_captured(
            store=store,
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
