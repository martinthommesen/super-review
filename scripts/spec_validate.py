#!/usr/bin/env python3
"""Run the external Agent Skills reference validator against the source skill."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve(strict=True).parents[1]
SKILL_ROOT = REPO_ROOT / "src" / "super-review"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", nargs="?", type=Path, default=SKILL_ROOT)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        from skills_ref import read_properties, validate
    except ImportError:
        print(
            "skills-ref is not installed. Run `python -m pip install -r requirements-dev.txt` "
            "or `uv sync --dev`.",
            file=sys.stderr,
        )
        return 2

    skill = args.skill.expanduser().resolve(strict=True)
    errors = validate(skill)
    if errors:
        print("Agent Skills validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    properties = read_properties(skill)
    if properties.name != "super-review":
        print(f"unexpected skill name: {properties.name!r}", file=sys.stderr)
        return 1
    print(f"Agent Skills validation passed: {skill}")
    print(f"name: {properties.name}")
    print(f"description length: {len(properties.description)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
