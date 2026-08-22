#!/usr/bin/env python3
"""Build a deterministic super-review skill ZIP from the canonical source tree."""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve(strict=True).parents[1]
SOURCE_ROOT = REPO_ROOT / "src" / "super-review"
DEFAULT_OUTPUT = REPO_ROOT / "dist" / "super-review-skill.zip"
ARCHIVE_ROOT = "super-review"
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
FORBIDDEN_NAMES = {".DS_Store"}
FORBIDDEN_PARTS = {"__pycache__"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


def _iter_source_files() -> list[Path]:
    if not SOURCE_ROOT.is_dir():
        raise RuntimeError(f"missing canonical skill source: {SOURCE_ROOT}")

    files: list[Path] = []
    for path in sorted(SOURCE_ROOT.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(SOURCE_ROOT)
        if any(part in FORBIDDEN_PARTS for part in relative.parts):
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
            continue
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise RuntimeError(f"source tree contains a symbolic link: {relative}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(info.st_mode):
            raise RuntimeError(f"source tree contains a non-regular file: {relative}")
        files.append(path)
    if not files:
        raise RuntimeError("canonical skill source contains no files")
    return files


def _normalized_mode(source_mode: int) -> int:
    """Reduce a source mode to Git's 0644 or 0755 model."""
    return 0o755 if source_mode & 0o111 else 0o644


def _zip_info(path: Path) -> zipfile.ZipInfo:
    """Create deterministic ZIP metadata for one source file."""
    relative = path.relative_to(SOURCE_ROOT).as_posix()
    info = zipfile.ZipInfo(f"{ARCHIVE_ROOT}/{relative}", date_time=ZIP_TIME)
    info.create_system = 3
    mode = _normalized_mode(stat.S_IMODE(path.stat().st_mode))
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    info.flag_bits |= 0x800
    return info


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(output: Path) -> str:
    output = output.expanduser().resolve(strict=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    source_files = _iter_source_files()

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(
            temporary,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            strict_timestamps=True,
        ) as archive:
            archive.comment = b""
            for path in source_files:
                archive.writestr(
                    _zip_info(path),
                    path.read_bytes(),
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)

    digest = _sha256(output)
    checksum_path = output.parent / "SHA256SUMS"
    checksum_text = f"{digest}  {output.name}\n"
    checksum_path.write_text(checksum_text, encoding="utf-8", newline="\n")
    return digest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"release ZIP path (default: {DEFAULT_OUTPUT.relative_to(REPO_ROOT)})",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    digest = build(args.output)
    print(f"built: {args.output.expanduser().resolve(strict=True)}")
    print(f"sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
