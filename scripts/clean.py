#!/usr/bin/env python3
"""Remove generated local artifacts without touching canonical source files."""

from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve(strict=True).parents[1]


def main() -> int:
    for directory_name in (
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    ):
        for path in REPO_ROOT.rglob(directory_name):
            if path.is_dir():
                shutil.rmtree(path)
    for pattern in ("*.pyc", "*.pyo"):
        for path in REPO_ROOT.rglob(pattern):
            path.unlink(missing_ok=True)
    dist = REPO_ROOT / "dist"
    if dist.exists():
        for path in dist.iterdir():
            if path.name != ".gitkeep":
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink(missing_ok=True)
    print("cleaned generated artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
