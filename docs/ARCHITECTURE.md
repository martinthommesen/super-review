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

Claude, Copilot, and Codex catalogs resolve `src/` as their plugin root. Claude and Copilot share a thin command adapter that loads `src/super-review/SKILL.md`; explicit-only activation is enforced by the skill description and invocation gate rather than client invocation-control frontmatter, which is not portable and blocks the Skill-tool path Claude Code uses even for user-typed commands. Codex resolves `src/super-review/` directly and uses its existing client policy metadata. Cursor's plugin root is the repository itself: it points `skills` at `./src/super-review` and ships a thin Cursor command under `src/client-adapters/cursor/commands/`; it registers no MCP server (see D15). Marketplace namespaces may qualify the invocation name, but the loaded `SKILL.md`, references, helpers, tests, and review policy are the same bytes on every client.

### Repository workbench

Root `scripts/`, root `tests/`, docs, CI, build metadata, marketplace catalogs, and marketplace adapter manifests exist only for maintainers or repository-backed installation. They do not enter the portable direct-skill archive. That archive includes Codex's explicit-only policy and is suitable for other direct-install hosts only when they provide an equivalent invocation gate; Claude and Copilot use the marketplace adapters instead.

### Consolidated CLI

`cli/` is a consolidated `super-review` console command over the shipped FINDINGS helpers, replacing the earlier MCP companion (decision D15). It is outside the portable ZIP and every marketplace payload (those still resolve from `src/` only), has its own `pyproject.toml`, lockfile, and CI job, and its runtime is dependency-free. Each subcommand resolves the requested helper from the explicit trusted skill root (`skill_loaders.py`: absolute root, symlink and escape checks) and forwards its arguments verbatim to that helper's `main`, so flag surfaces and exit codes are identical to direct `python3 -I` invocation. `snapshot` accepts only a repository root and derives `<repo-root>/FINDINGS.md`. There is no server: nothing runs unless explicitly invoked.

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
