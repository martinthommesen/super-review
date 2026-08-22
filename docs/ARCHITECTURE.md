# Architecture

## System boundaries

The workbench separates shipped files from maintainer tooling.

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

Claude, Copilot, and Codex resolve `src/` as their plugin root. Claude and
Copilot share a command adapter that loads `src/super-review/SKILL.md`. The skill
description and invocation gate enforce explicit activation. Client frontmatter
cannot enforce this portably and blocks Claude Code's Skill-tool path even for a
user-typed command.

Codex resolves `src/super-review/` and uses `agents/openai.yaml`. Cursor uses the
repository as its plugin root, points `skills` at `./src/super-review`, and adds
the command under `src/client-adapters/cursor/commands/`. Cursor registers no MCP
server. See D15. Every client loads the same skill files.

### Repository workbench

Root `scripts/`, root `tests/`, docs, CI, build metadata, marketplace catalogs, and marketplace adapter manifests exist only for maintainers or repository-backed installation. They do not enter the portable direct-skill archive. That archive includes Codex's explicit-only policy and is suitable for other direct-install hosts only when they provide an equivalent invocation gate; Claude and Copilot use the marketplace adapters instead.

### Command-line interface

`cli/` packages the shipped FINDINGS helpers as a `super-review` command. It is
outside the portable ZIP and marketplace skill payloads. Cursor installs the
repository but wires only the canonical skill and command adapter.

The package has its own build metadata, lockfile, and CI job. Its runtime uses
only the Python standard library. `skill_loaders.py` loads each helper from an
explicit skill root after absolute-path, symlink, and escape checks. Subcommands
use command-specific helper entry points and preserve their exit codes. `validate`
cannot select snapshot or self-test modes. `snapshot` accepts a repository root,
derives `<repo-root>/FINDINGS.md`, pins that directory before reading, and exposes
only snapshot options. No server runs in the background.

## Instruction loading

Activation loads only `SKILL.md`. The entrypoint then loads four universal references: mandate, principles, findings lifecycle, and phase applicability. It loads command safety before repository-defined execution, one phase at a time, applicable stack references only for detected technologies, record schemas only for record types that exist, and final-report/quality gates during assembly and completion.

This preserves exhaustive applicable coverage without loading the full protocol before repository evidence exists.

## Report lifecycle

A run follows this state model:

1. Resolve canonical repository root and report path.
2. Read exact existing report bytes and compute the starting digest, or record `MISSING`.
3. Parse and revalidate every prior canonical record and derived claim.
4. Independently review the current repository through phases 0 through 22.
5. Canonicalize current records and preserve or retire IDs according to fingerprints.
6. Generate a complete candidate outside the reviewed repository.
7. Validate the candidate's exact bytes.
8. Pin the repository directory, then recheck the live target digest and
   protected human blocks through that descriptor.
9. Stage the same validated bytes in a pinned private directory and publish
   through descriptors. Missing targets use atomic no-replace hard links.
   Existing targets use one atomic exchange so the displaced inode remains
   available for verification or conflict recovery.
10. Reread and validate the committed report.

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

`commit_findings.py` exposes a single write core, `commit_bytes`, that validates an
immutable byte sequence under digest concurrency and annotation preservation.
`report_store.py` owns pinned directory identity, advisory locking, stable target
reads, staging, publication, cleanup, directory sync, and final inode and byte
verification. The path front end reads the candidate once without following its
final component, applies location and hard-link checks, then delegates those
captured bytes. Snapshot `--out` uses the same complete-stage and atomic-link
publication path. Existing-report commits atomically exchange the staged and
current names, then verify the displaced inode. A failed post-exchange check does
not trigger another pathname exchange. The private directory is preserved as a
recovery quarantine, avoiding a second source-name race. Platforms without the
required descriptor-relative, no-replace, or exchange primitives fail before
publication.
`validate_findings.snapshot` provides an exact-byte read of an existing report,
or `MISSING`, for prior-report revalidation and concurrency bookkeeping.

Portable standard-library APIs cannot identify every privileged bind-mount alias
to a repository subdirectory. Callers must not choose snapshot output through
such an alias.

## Build model

`scripts/build.py` enumerates regular non-symlink files from `src/super-review`, assigns stable ZIP timestamps, preserves intended Unix modes, orders paths lexicographically, compresses deterministically, writes through a temporary file, and atomically replaces the artifact. It then writes a SHA-256 checksum.

`scripts/verify_dist.py` independently compares the ZIP against source, validates paths and modes, performs CRC checks, extracts safely, and reruns shipped tests from the extracted package.

Marketplace clients install from `src/` through their client-specific manifest. The portable ZIP remains a byte-exact archive of only `src/super-review/`; marketplace metadata cannot fork or replace the canonical skill.
