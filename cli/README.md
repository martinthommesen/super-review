# super-review command-line interface

This package exposes the shipped FINDINGS helpers as a `super-review` command.
It replaced the MCP companion under decision D15. There is no server or
registered tool endpoint. Each operation requires a shell command and arguments.

The CLI does not replace the portable contract in `SKILL.md`. The skill still
invokes helpers directly with
`python3 -I "$SKILL_ROOT/scripts/<helper>.py"`. This package calls the same code.

## Trust model

- Supply the trusted skill root with `--skill-root /abs/path/to/super-review` or
  `SUPER_REVIEW_SKILL_ROOT`. The CLI never infers it from the working directory.
- `skill_loaders.py` resolves helpers by absolute path under
  `<skill-root>/scripts/` and rejects symlinks and path escapes. It does not load
  helpers from `sys.path` or the target repository.
- The `commit` command delegates to `commit_findings.py`. It adds no second
  write implementation.

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

Each command passes its remaining arguments to the helper. Put `-h` after the
command to see its options. Exit codes pass through unchanged. `validate` uses
0 for success, 1 for an invalid report, and 2 for usage errors. `commit` uses 0
for success, 2 for validation, 3 for conflicts, and 4 for I/O errors.

```bash
# Validate a candidate or committed report
super-review --skill-root "$SKILL_ROOT" validate /tmp/FINDINGS.candidate.md
super-review --skill-root "$SKILL_ROOT" validate --canonical-root /repo /repo/FINDINGS.md

# Snapshot <repo-root>/FINDINGS.md by exact bytes
super-review --skill-root "$SKILL_ROOT" snapshot /repo --json --metadata-only
super-review --skill-root "$SKILL_ROOT" snapshot /repo --out /tmp/current-findings.bytes

# Commit only if the starting digest matches
super-review --skill-root "$SKILL_ROOT" commit \
  --repo-root /repo --candidate /tmp/FINDINGS.candidate.md \
  --expected-sha256 MISSING

# Compute a record fingerprint
super-review --skill-root "$SKILL_ROOT" fingerprint \
  --record-type "Defect or risk" --category SEC \
  --primary-component auth/session --identity-statement "session tokens never expire"
```

`snapshot` accepts a repository root, not a file path. It always reads
`<repo-root>/FINDINGS.md`.

## Development

```bash
make cli-test        # from the repository root; runs uv sync, ruff, and pytest
```

The runtime uses only the Python standard library. Development dependencies are
pinned in `pyproject.toml` and locked in `uv.lock`.
