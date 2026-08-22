# super-review CLI

Consolidated command-line front-end for the shipped FINDINGS helpers. It replaces the earlier MCP companion (decision D15): there is no server and no ambient tool surface — every operation is an explicit shell invocation with explicit arguments, so nothing here can be reached by a host's auto-run machinery or by prompt injection.

The CLI does **not** replace the portable contract in `SKILL.md`. The skill itself keeps invoking the helpers directly (`python3 -I "$SKILL_ROOT/scripts/<helper>.py"`); this package is a convenience wrapper around the same bytes.

## Trust model

- The trusted skill root is always explicit: `--skill-root /abs/path/to/super-review` or the `SUPER_REVIEW_SKILL_ROOT` environment variable. It is never inferred from the current working directory.
- Helpers are resolved only from `<skill-root>/scripts/` by absolute path, with symlink and escape checks (`skill_loaders.py`), never from `sys.path` or the target repository.
- Commits stay digest-gated, exact-byte, annotation-preserving, and atomic — the CLI adds no write path of its own; it forwards to `commit_findings.py`.

## Install

From this repository:

```bash
cd cli
uv sync --frozen
uv run super-review --help
```

As a tool:

```bash
uv tool install --from /path/to/super-review/cli super-review-cli
super-review --skill-root /path/to/super-review/src/super-review validate --help
```

## Commands

Each command forwards its remaining arguments to the underlying helper, so `-h` after a command prints that helper's full flag surface, and exit codes pass through unchanged (validate: 0 ok, 1 invalid, 2 usage; commit: 0 ok, 2 validation, 3 conflict, 4 I/O).

```bash
# Validate a candidate (or a committed report with --canonical-root):
super-review --skill-root "$SKILL_ROOT" validate /tmp/FINDINGS.candidate.md
super-review --skill-root "$SKILL_ROOT" validate --canonical-root /repo /repo/FINDINGS.md

# Exact-byte snapshot of <repo-root>/FINDINGS.md (repo root must be absolute):
super-review --skill-root "$SKILL_ROOT" snapshot /repo --json --metadata-only
super-review --skill-root "$SKILL_ROOT" snapshot /repo --out /tmp/current-findings.bytes

# Digest-gated commit:
super-review --skill-root "$SKILL_ROOT" commit \
  --repo-root /repo --candidate /tmp/FINDINGS.candidate.md \
  --expected-sha256 MISSING

# Deterministic record fingerprint:
super-review --skill-root "$SKILL_ROOT" fingerprint \
  --record-type "Defect or risk" --category SEC \
  --primary-component auth/session --identity-statement "session tokens never expire"
```

`snapshot` takes a repository root, not a file path — the report path is always derived as `<repo-root>/FINDINGS.md`, so the command cannot be pointed at arbitrary files.

## Development

```bash
make cli-test        # from the repository root: uv sync --frozen, ruff, pytest
```

The package is stdlib-only at runtime; dev dependencies (pytest, ruff) are pinned in `pyproject.toml` and locked in `uv.lock`.
