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

The repository exposes three client-native marketplace catalogs without duplicating the skill:

- `.claude-plugin/marketplace.json` with `src/.claude-plugin/plugin.json` for Claude Code;
- `.github/plugin/marketplace.json` with `src/plugin.json` for GitHub Copilot CLI;
- `.agents/plugins/marketplace.json` with `src/.codex-plugin/plugin.json` for Codex.

Every catalog resolves `src/` as its plugin root. Claude and Copilot share a manual-only command adapter that loads `src/super-review/SKILL.md`, keeping their invocation-control extension out of portable Agent Skills frontmatter. Codex resolves `src/super-review/` directly and uses its existing client policy metadata. Marketplace namespaces may qualify the invocation name, but the loaded `SKILL.md`, references, helpers, tests, and review policy are the same bytes on every client.

### Repository workbench

Root `scripts/`, root `tests/`, docs, CI, build metadata, marketplace catalogs, and marketplace adapter manifests exist only for maintainers or repository-backed installation. They do not enter the portable direct-skill archive.

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

`commit_findings.py` reads candidate bytes once and never rereads the candidate path after validation. It validates and writes the same immutable byte sequence, while separately detecting candidate and target path mutation.

## Build model

`scripts/build.py` enumerates regular non-symlink files from `src/super-review`, assigns stable ZIP timestamps, preserves intended Unix modes, orders paths lexicographically, compresses deterministically, writes through a temporary file, and atomically replaces the artifact. It then writes a SHA-256 checksum.

`scripts/verify_dist.py` independently compares the ZIP against source, validates paths and modes, performs CRC checks, extracts safely, and reruns shipped tests from the extracted package.

Marketplace clients install from `src/` through their client-specific manifest. The portable ZIP remains a byte-exact archive of only `src/super-review/`; marketplace metadata cannot fork or replace the canonical skill.
