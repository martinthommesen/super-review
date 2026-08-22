"""Console entry point: ``super-review <command>`` over the skill-root helpers.

The CLI is a thin dispatcher. Every subcommand forwards its remaining
arguments verbatim to the corresponding bundled helper's own ``main``, so flag
surfaces, output, and exit codes stay identical to direct
``python3 -I "$SKILL_ROOT/scripts/<helper>.py"`` invocations (validate: 0/1/2;
commit: 0/2/3/4). The trusted skill root is always explicit — ``--skill-root``
or ``SUPER_REVIEW_SKILL_ROOT`` — and is never inferred from the current
working directory. There is no server and no ambient tool surface: nothing
runs unless invoked with explicit arguments.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TextIO

from super_review_cli.skill_loaders import SkillLoadError, load_helper

SKILL_ROOT_ENV = "SUPER_REVIEW_SKILL_ROOT"

_HELPER_FILES = {
    "validate": ("validate_findings.py", "_super_review_cli_validate"),
    "snapshot": ("validate_findings.py", "_super_review_cli_validate"),
    "commit": ("commit_findings.py", "_super_review_cli_commit"),
    "fingerprint": ("finding_fingerprint.py", "_super_review_cli_fingerprint"),
}

_HELP = """\
usage: super-review [--skill-root PATH] <command> [helper arguments...]

Consolidated front-end for the super-review FINDINGS helpers. Each command
forwards its remaining arguments verbatim to the bundled helper resolved from
the trusted skill root; pass -h after a command to see that helper's full flag
surface. Helper exit codes pass through unchanged.

commands:
  validate     validate a FINDINGS.md candidate or committed report
  snapshot     exact-byte snapshot of <repo-root>/FINDINGS.md (or MISSING);
               the repository root must be the first argument
  commit       digest-gated, annotation-preserving atomic report commit
  fingerprint  compute a deterministic canonical-record fingerprint

options:
  --skill-root PATH  absolute path to the installed super-review skill root
                     (the directory containing SKILL.md); defaults to the
                     SUPER_REVIEW_SKILL_ROOT environment variable
  -h, --help         show this message and exit
"""


def _print_help(stream: TextIO) -> None:
    """Write the command-line usage and command help text to a stream."""
    stream.write(_HELP)


def _snapshot_target(repo_root: Path) -> Path:
    """Derive <repo-root>/FINDINGS.md from an absolute existing directory."""
    requested = repo_root.expanduser()
    if not requested.is_absolute():
        raise SkillLoadError(f"repo root must be an absolute path, got {repo_root}")
    try:
        resolved = requested.resolve(strict=True)
    except OSError as exc:
        raise SkillLoadError(f"cannot resolve repo root {repo_root}: {exc}") from exc
    if not resolved.is_dir():
        raise SkillLoadError(f"repo root is not a directory: {resolved}")
    return resolved / "FINDINGS.md"


def main(argv: list[str] | None = None) -> int:
    """
    Dispatch a super-review command to its helper module.
    
    Parameters:
    	argv (list[str] | None): Command-line arguments without the program name. If omitted, uses the process arguments.
    
    Returns:
    	int: The helper's exit code, or `2` for invalid arguments, missing configuration, or helper-loading errors.
    """
    arguments = list(sys.argv[1:] if argv is None else argv)

    skill_root: Path | None = None
    index = 0
    while index < len(arguments):
        token = arguments[index]
        if token in {"-h", "--help"}:
            _print_help(sys.stdout)
            return 0
        if token == "--skill-root":
            if index + 1 >= len(arguments):
                print("error: --skill-root requires a value", file=sys.stderr)
                return 2
            skill_root = Path(arguments[index + 1])
            index += 2
            continue
        if token.startswith("--skill-root="):
            skill_root = Path(token.split("=", 1)[1])
            index += 1
            continue
        break

    if index >= len(arguments):
        _print_help(sys.stderr)
        print("error: a command is required", file=sys.stderr)
        return 2
    command = arguments[index]
    rest = arguments[index + 1 :]
    if command not in _HELPER_FILES:
        _print_help(sys.stderr)
        print(f"error: unknown command {command!r}", file=sys.stderr)
        return 2

    if skill_root is None:
        from_env = os.environ.get(SKILL_ROOT_ENV, "")
        skill_root = Path(from_env) if from_env else None
    if skill_root is None:
        print(
            f"error: --skill-root or {SKILL_ROOT_ENV} is required",
            file=sys.stderr,
        )
        return 2

    filename, module_name = _HELPER_FILES[command]
    try:
        module = load_helper(skill_root, filename, module_name)
        if command == "snapshot":
            if not rest or rest[0].startswith("-"):
                print(
                    "error: snapshot requires the repository root as its "
                    "first argument",
                    file=sys.stderr,
                )
                return 2
            target = _snapshot_target(Path(rest[0]))
            forwarded = ["--snapshot", *rest[1:], str(target)]
        else:
            forwarded = rest
    except SkillLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return int(module.main(forwarded))


if __name__ == "__main__":
    raise SystemExit(main())
