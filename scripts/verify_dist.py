#!/usr/bin/env python3
"""Verify a release ZIP against source and test it from a clean extraction."""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve(strict=True).parents[1]
SOURCE_ROOT = REPO_ROOT / "src" / "super-review"
DEFAULT_ARTIFACT = REPO_ROOT / "dist" / "super-review-skill.zip"
ARCHIVE_ROOT = "super-review"
FORBIDDEN_PARTS = {"__pycache__"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
EXECUTABLE_PATHS = {
    "scripts/commit_findings.py",
    "scripts/finding_fingerprint.py",
    "scripts/validate_findings.py",
    "tests/run_tests.py",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_files() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in sorted(SOURCE_ROOT.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(SOURCE_ROOT)
        if any(part in FORBIDDEN_PARTS for part in relative.parts):
            continue
        if path.suffix in FORBIDDEN_SUFFIXES:
            continue
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise RuntimeError(f"source symlink is forbidden: {relative}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(info.st_mode):
            raise RuntimeError(f"source non-regular file is forbidden: {relative}")
        result[relative.as_posix()] = path
    return result


def _validate_name(name: str) -> str:
    pure = PurePosixPath(name)
    if pure.is_absolute() or not pure.parts:
        raise RuntimeError(f"unsafe archive path: {name!r}")
    if any(part in {"", ".", ".."} for part in pure.parts):
        raise RuntimeError(f"unsafe archive path: {name!r}")
    if pure.parts[0] != ARCHIVE_ROOT or len(pure.parts) < 2:
        raise RuntimeError(f"archive entry is outside {ARCHIVE_ROOT}/: {name!r}")
    return PurePosixPath(*pure.parts[1:]).as_posix()


def _run(command: list[str], cwd: Path) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def verify(artifact: Path, *, run_tests: bool = True) -> str:
    artifact = artifact.expanduser().resolve(strict=True)
    artifact_info = artifact.lstat()
    if stat.S_ISLNK(artifact_info.st_mode) or not stat.S_ISREG(artifact_info.st_mode):
        raise RuntimeError(f"artifact must be a regular non-symlink file: {artifact}")

    expected = _source_files()
    seen: dict[str, zipfile.ZipInfo] = {}
    with zipfile.ZipFile(artifact, "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP CRC validation failed")
        for info in archive.infolist():
            if info.is_dir():
                raise RuntimeError(
                    f"unexpected explicit directory entry: {info.filename}"
                )
            relative = _validate_name(info.filename)
            if relative in seen:
                raise RuntimeError(f"duplicate archive path: {relative}")
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise RuntimeError(f"archive contains a symbolic link: {relative}")
            if mode and not stat.S_ISREG(mode):
                raise RuntimeError(f"archive contains a non-regular entry: {relative}")
            seen[relative] = info

        missing = sorted(set(expected) - set(seen))
        extra = sorted(set(seen) - set(expected))
        if missing or extra:
            raise RuntimeError(
                f"archive/source mismatch; missing={missing}, extra={extra}"
            )

        for relative, source in expected.items():
            archived = archive.read(seen[relative])
            source_bytes = source.read_bytes()
            if archived != source_bytes:
                raise RuntimeError(
                    f"byte mismatch for {relative}: "
                    f"source={_sha256_bytes(source_bytes)}, archive={_sha256_bytes(archived)}"
                )
            archive_mode = (seen[relative].external_attr >> 16) & 0o777
            source_mode = stat.S_IMODE(source.stat().st_mode)
            # The builder normalizes modes to git's model (0644/0755 by
            # executable bit); verify against that expectation, not the
            # umask-dependent working-tree mode.
            normalized_mode = 0o755 if source_mode & 0o111 else 0o644
            if archive_mode != normalized_mode:
                raise RuntimeError(
                    f"mode mismatch for {relative}: expected={oct(normalized_mode)}, archive={oct(archive_mode)}"
                )
            expected_executable = relative in EXECUTABLE_PATHS
            if bool(archive_mode & 0o111) != expected_executable:
                raise RuntimeError(
                    f"unexpected executable mode for {relative}: {oct(archive_mode)}"
                )

        with tempfile.TemporaryDirectory(prefix="super-review-release-") as directory:
            extraction_root = Path(directory)
            for relative, info in seen.items():
                destination = extraction_root / ARCHIVE_ROOT / Path(relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(info))
                os.chmod(destination, (info.external_attr >> 16) & 0o777)

            extracted_skill = extraction_root / ARCHIVE_ROOT
            for relative, source in expected.items():
                extracted = extracted_skill / Path(relative)
                if extracted.read_bytes() != source.read_bytes():
                    raise RuntimeError(f"post-extraction byte mismatch: {relative}")

            if run_tests:
                _run(
                    [
                        sys.executable,
                        "-I",
                        "-B",
                        str(extracted_skill / "tests" / "run_tests.py"),
                    ],
                    extracted_skill,
                )
                _run(
                    [
                        sys.executable,
                        "-I",
                        "-B",
                        str(extracted_skill / "scripts" / "validate_findings.py"),
                        "--self-test",
                    ],
                    extracted_skill,
                )

    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    checksum = artifact.parent / "SHA256SUMS"
    if checksum.exists():
        expected_line = f"{digest}  {artifact.name}"
        lines = [
            line.strip()
            for line in checksum.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if expected_line not in lines:
            raise RuntimeError(
                f"{checksum} does not contain the artifact's current digest"
            )
    return digest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--skip-tests", action="store_true", help="skip clean-room test execution"
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    digest = verify(args.artifact, run_tests=not args.skip_tests)
    print(f"verified: {args.artifact.expanduser().resolve(strict=True)}")
    print(f"sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
