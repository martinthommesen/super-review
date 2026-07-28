# Architecture

## System boundaries

The workbench has two deliberately separate layers.

### Shipped skill

`src/super-review/` is copied verbatim into the release archive. It contains:

- `SKILL.md`: explicit invocation gate, trusted-root resolution, non-negotiable output invariant, progressive-loading router, execution architecture, and completion contract;
- `references/`: normative protocol material loaded only when applicable;
- `scripts/`: dependency-free runtime helpers for record fingerprints, report validation, and exact-byte safe commits;
- `tests/`: regression suite that travels with the package so an installed copy can validate itself;
- `agents/openai.yaml`: client-specific opt-out from implicit invocation where supported.

### Marketplace adapters

The repository exposes four client-native marketplace/plugin catalogs without duplicating the skill:

- `.claude-plugin/marketplace.json` with `src/.claude-plugin/plugin.json` for Claude Code;
- `.github/plugin/marketplace.json` with `src/plugin.json` for GitHub Copilot CLI;
- `.agents/plugins/marketplace.json` with `src/.codex-plugin/plugin.json` for Codex;
- `.cursor-plugin/plugin.json` for Cursor (repo-root single-plugin manifest).

Claude, Copilot, and Codex catalogs resolve `src/` as their plugin root. Claude and Copilot share a thin command adapter that loads `src/super-review/SKILL.md`; explicit-only activation is enforced by the skill description and invocation gate rather than client invocation-control frontmatter, which is not portable and blocks the Skill-tool path Claude Code uses even for user-typed commands. Codex resolves `src/super-review/` directly and uses its existing client policy metadata. Cursor's plugin root is the repository itself: it points `skills` at `./src/super-review`, ships a thin Cursor command under `src/client-adapters/cursor/commands/`, and registers the optional companion MCP from `src/client-adapters/cursor/mcp.json` using `${PLUGIN_ROOT}` so the companion binds to the installed skill copy. Marketplace namespaces may qualify the invocation name, but the loaded `SKILL.md`, references, helpers, tests, and review policy are the same bytes on every client.

### Repository workbench

Root `scripts/`, root `tests/`, docs, CI, build metadata, marketplace catalogs, and marketplace adapter manifests exist only for maintainers or repository-backed installation. They do not enter the portable direct-skill archive. That archive includes Codex's explicit-only policy and is suitable for other direct-install hosts only when they provide an equivalent invocation gate; Claude and Copilot use the marketplace adapters instead.

### Optional MCP companion

`companion/` is an optional typed front-end over the shipped FINDINGS helpers. It is outside the portable ZIP and every marketplace payload (those still resolve from `src/` only). The companion has its own `pyproject.toml`, lockfile, and CI job so the MCP SDK never enters the stdlib-only skill or root `scripts/` trees. See decision D14: default to the skill-root CLI; use MCP only with host-attested active-server provenance plus user affirmation; always post-validate commits via the CLI; expose `commit_findings` only when the host gates writes to explicit skill invocation with a gate Auto-run/allowlist modes cannot skip. The bundled Cursor MCP entry therefore stays read-only.

Helper APIs used by the companion:

- `finding_fingerprint.compute_fingerprint`
- `validate_findings.validate_bytes` and public `validate_findings.snapshot`
- `commit_findings.commit_bytes` (path `commit()` reads the candidate once, then delegates here)

MCP validate/commit tools transport UTF-8 text plus `content_sha256` of the encoded bytes, with a 1 MiB companion size bound and CLI fallback above it.

## Instruction loading

Activation loads only `SKILL.md`. The entrypoint then loads four universal references: mandate, principles, findings lifecycle, and phase applicability. It loads command safety before repository-defined execution, one phase at a time, applicable stack references only for detected technologies, record schemas only for record types that exist, and final-report/quality gates during assembly and completion.

This preserves exhaustive applicable coverage without loading the full protocol before repository evidence exists.

## Report lifecycle

A run follows this state model:

1. Resolve canonical repository root and report path.
2. Read exact existing report bytes and compute the starting digest, or record `MISSING`.
3. Parse and revalidate every prior canonical record and derived claim.
4. Independently review the current repository through phases 0–22.
5. Canonicalize current records and preserve or retire IDs according to fingerprints.
6. Generate a complete candidate outside the reviewed repository.
7. Validate the candidate's exact bytes.
8. Recheck the live target digest and protected human blocks.
9. Stage the same validated bytes beside the target and atomically replace it.
10. Reread and validate the committed report.

A concurrent change causes a conflict, not a forced overwrite.

## Canonical record model

There are four record types:

- defects and risks;
- improvements and alternatives;
- feature decisions;
- positive patterns.

Each record has a stable ID and a deterministic fingerprint derived from record type, category, primary component, and a stable identity statement. Volatile evidence such as line numbers, severity, or revision hashes is excluded. Retired IDs remain reserved so a recurring root cause can recover its original identity and no historical ID is accidentally reused.

Summary tables, roadmap items, and cross-references point to canonical IDs instead of duplicating record bodies.

## Helper trust model

The target repository is untrusted. Runtime helpers are invoked from the absolute loaded skill root with isolated Python mode. Sibling modules are loaded by canonical file path after regular-file and no-symlink checks. The reviewed repository's current working directory and import path are not trusted resolution sources.

`commit_findings.py` exposes a single write core, `commit_bytes`, that validates and writes an immutable byte sequence under digest concurrency and annotation preservation. The path CLI reads the candidate once without following its final component, applies path-only location and hard-link checks, then delegates to `commit_bytes`. `validate_findings.snapshot` provides an exact-byte read of an existing report (or `MISSING`) for prior-report revalidation and concurrency bookkeeping; the snapshot digest is advisory because commit recomputes starting state.

## Build model

`scripts/build.py` enumerates regular non-symlink files from `src/super-review`, assigns stable ZIP timestamps, preserves intended Unix modes, orders paths lexicographically, compresses deterministically, writes through a temporary file, and atomically replaces the artifact. It then writes a SHA-256 checksum.

`scripts/verify_dist.py` independently compares the ZIP against source, validates paths and modes, performs CRC checks, extracts safely, and reruns shipped tests from the extracted package.

Marketplace clients install from `src/` through their client-specific manifest. The portable ZIP remains a byte-exact archive of only `src/super-review/`; marketplace metadata cannot fork or replace the canonical skill.
