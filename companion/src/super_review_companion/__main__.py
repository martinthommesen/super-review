"""CLI entrypoint for the super-review companion MCP server."""

from __future__ import annotations

import argparse
from pathlib import Path

from super_review_companion.server import create_server_from_args


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Optional MCP front-end for super-review FINDINGS helpers. "
            "Default to the skill-root CLI unless host provenance and user "
            "affirmation allow companion use (D14)."
        )
    )
    parser.add_argument(
        "--skill-root",
        type=Path,
        required=True,
        help="Absolute path to the installed super-review skill root (directory containing SKILL.md)",
    )
    parser.add_argument(
        "--enable-commit",
        action="store_true",
        help=(
            "Expose commit_findings. Only enable on hosts that gate writes to "
            "explicit super-review invocation or equivalent per-write approval (D1)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    server = create_server_from_args(args.skill_root, enable_commit=args.enable_commit)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
