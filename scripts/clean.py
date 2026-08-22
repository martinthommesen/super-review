#!/usr/bin/env python3
"""Remove generated local artifacts without touching canonical source files."""

from __future__ import annotations

from pathlib import Path

from workspace_hygiene import remove_directory_contents, remove_generated

REPO_ROOT = Path(__file__).resolve(strict=True).parents[1]


def main() -> int:
    remove_generated(
        REPO_ROOT,
        directory_names=(
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        ),
        suffixes=(".pyc", ".pyo"),
    )
    remove_directory_contents(
        REPO_ROOT / "dist", preserve_names=(".gitkeep",), missing_ok=True
    )
    print("cleaned generated artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
