# super-review companion MCP

Optional MCP front-end for the shipped FINDINGS helpers. It does **not** replace the portable CLI contract in `SKILL.md`.

## Trust model (D14)

- Default to the skill-root CLI. Do not prefer MCP merely because tools are visible.
- Use this companion only when **both** hold:
  1. The host attests the *active resolved* server's scope and executable/endpoint (proving it is not a local/project `.mcp.json` override), **or** managed policy excludes project/local overrides for this server name.
  2. The user affirms in-session (or via host config the agent is told to treat as authoritative) that the companion may be used for this run.
- Never trust the server's self-reported skill root or digests for authorization.
- After any MCP commit that claims success, always re-validate `<canonical-root>/FINDINGS.md` with the skill-root CLI.
- Do **not** install this companion via project-scoped `.mcp.json` in a reviewed repository.

## Write tool gate (D1)

By default the server exposes only read/validate/fingerprint tools (`fingerprint_finding`, `validate_findings`, `snapshot_findings`). Pass `--enable-commit` **only** on hosts that enforce an authorization/invocation gate tying writes to explicit `$/@/`/`super-review` invocation (or equivalent per-write approval). Without that gate, keep commit on the CLI.

## Install

Primary path (from this repository):

```bash
cd companion
uv sync
```

User/tool install:

```bash
uv tool install --from ./companion super-review-companion
```

Companion runtime dependencies (including the MCP SDK) live only in this package's lockfile. They are not added to the workbench root `[dependency-groups].dev`.

## Launch

Bind an absolute skill root — never a path resolved from the reviewed repository's CWD:

```bash
# From a synced companion environment
uv run --project companion super-review-companion \
  --skill-root /absolute/path/to/src/super-review

# After uv tool install
super-review-companion --skill-root /absolute/path/to/src/super-review

# Expose commit_findings only when the host has a write-authorization gate
super-review-companion \
  --skill-root /absolute/path/to/src/super-review \
  --enable-commit
```

Example **user-scoped** Claude Code registration (not project `.mcp.json`):

```bash
claude mcp add --scope user --transport stdio super-review -- \
  /absolute/path/to/super-review-companion \
  --skill-root /absolute/path/to/src/super-review
```

Re-check with host tooling that the *active* resolved entry is this executable and not a project/local override before affirming MCP use.

## Wire contract

MCP `validate_findings` / `commit_findings` take:

- `content`: UTF-8 text (JSON string)
- `content_sha256`: SHA-256 of `content.encode("utf-8")` (`hex` or `sha256:<hex>`)

The server encodes to UTF-8, checks the digest, and passes those immutable bytes to the shipped helpers. Maximum MCP content size is **1 MiB** encoded UTF-8; larger reports must use the CLI path commit with an on-disk candidate.

## Upgrade policy

- Companion version is independent (`companion/pyproject.toml`).
- Compatible skill API additions are documented in the skill minor release notes.
- Breaking companion tool/wire changes bump the companion major version and update skill docs.

## Tests

```bash
cd companion
uv sync
uv run pytest
```

CI runs these in a dedicated job separate from the stdlib-only offline gate.
