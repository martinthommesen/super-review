from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TextIO

from super_review_cli.skill_loaders import SkillLoadError, load_helper

SKILL_ROOT_ENV = "SUPER_REVIEW_SKILL_ROOT"

_HELPER_FILES = {
    "validate": (
        "validate_findings.py",
        "_super_review_cli_validate",
        "validation_main",
    ),
    "snapshot": (
        "validate_findings.py",
        "_super_review_cli_validate",
        "snapshot_main",
    ),
    "commit": ("commit_findings.py", "_super_review_cli_commit", "main"),
    "fingerprint": (
        "finding_fingerprint.py",
        "_super_review_cli_fingerprint",
        "main",
    ),
}

_HELP = """\
usage: super-review [--skill-root PATH] <command> [helper arguments...]

Command-line front end for the super-review FINDINGS helpers. Each command
passes its remaining arguments to the bundled helper from the trusted skill
root. Pass -h after a command to see that helper's options. Helper exit codes
pass through unchanged.

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
    stream.write(_HELP)


def _snapshot_target(repo_root: Path) -> Path:
    try:
        requested = repo_root.expanduser()
    except (OSError, RuntimeError, ValueError) as exc:
        raise SkillLoadError(f"cannot expand repo root {repo_root}: {exc}") from exc
    if not requested.is_absolute():
        raise SkillLoadError(f"repo root must be an absolute path, got {repo_root}")
    return requested / "FINDINGS.md"


def _system_exit_code(exc: SystemExit) -> int:
    if exc.code is None:
        return 0
    if isinstance(exc.code, int):
        return exc.code
    print(exc.code, file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    """Dispatch one command and return its helper's exit code."""
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

    filename, module_name, entry_point = _HELPER_FILES[command]
    try:
        module = load_helper(skill_root, filename, module_name)
        entry = getattr(module, entry_point, None)
        if not callable(entry):
            raise SkillLoadError(
                f"helper {filename} has no callable {entry_point} entry point"
            )
        if command == "snapshot":
            if rest and rest[0] in {"-h", "--help"}:
                target = Path(".")
                forwarded = rest
            elif not rest or rest[0].startswith("-"):
                print(
                    "error: snapshot requires the repository root as its "
                    "first argument",
                    file=sys.stderr,
                )
                return 2
            else:
                target = _snapshot_target(Path(rest[0]))
                forwarded = rest[1:]
        else:
            forwarded = rest
    except SkillLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        if command == "snapshot":
            return int(entry(target, forwarded, prog="super-review snapshot"))
        if command == "validate":
            return int(entry(forwarded, prog="super-review validate"))
        return int(entry(forwarded))
    except SystemExit as exc:
        return _system_exit_code(exc)


if __name__ == "__main__":
    raise SystemExit(main())
