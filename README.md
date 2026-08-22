# super-review

[![CI](https://github.com/martinthommesen/super-review/actions/workflows/ci.yml/badge.svg)](https://github.com/martinthommesen/super-review/actions/workflows/ci.yml)

`super-review` is an Agent Skill that performs an exhaustive, evidence-based review of an entire repository — engineering, architecture, correctness, security, privacy, reliability, performance, data, APIs, testing, operations, UX, developer experience, and feature-portfolio decisions — and maintains exactly one canonical report:

```text
<reviewed-repository-root>/FINDINGS.md
```

It works with Claude Code, GitHub Copilot CLI, Codex, Cursor, and other hosts that load Agent Skills. The current skill version is **1.5.0**.

## Why it is different

- **One living report, not a stream of one-off reviews.** An existing `FINDINGS.md` is treated as a set of claims to revalidate: resolved or stale material is retired, surviving findings keep stable canonical IDs, and every run merges revalidated prior content with fresh independent discovery.
- **Evidence over vibes.** Confirmed findings require current repository evidence. Facts, supported inferences, hypotheses, and missing evidence are labeled as such; inapplicable areas are closed with an explicit evidence-based reason, never silently skipped.
- **Safe by construction.** The reviewed repository is treated as potentially malicious. Repository-defined commands pass a command-safety gate, bundled helpers are resolved only from the trusted skill root (never from the target repo), and the final report write is digest-gated, exact-byte, and atomic — a concurrent edit is detected and merged rather than blindly overwritten. Cooperating writers using the helper are fully serialized; a non-cooperating writer racing the final instant of replacement is detected best-effort, up to the last pre-replacement read and post-write verification. Protected human annotations survive regeneration.
- **Deterministic identities.** Each canonical record gets a reproducible fingerprint, so findings can be tracked, deduplicated, and retired across runs.
- **Explicit invocation only.** The skill never auto-activates for a generic "review this" request; it runs only when named directly.

## Review scope

A run walks up to 23 ordered phases, progressively loading only the instructions each phase needs: baseline and safety, repository inventory, product and feature inventory, architecture, end-to-end workflow tracing, correctness, security and privacy, data and migrations, APIs and integrations, concurrency and distributed systems, performance and cost, reliability and operations, frontend/UX/accessibility, testing strategy, dependencies and supply chain, configuration and deployment, maintainability, better-implementation alternatives, feature-portfolio decisions, documentation, stack-specific deep dives (JavaScript/TypeScript, Python, Go, Rust, Java/Kotlin, C#/.NET, C/C++, SQL, mobile), validation and reproduction, and prioritization/roadmap.

See [`examples/FINDINGS.example.md`](examples/FINDINGS.example.md) for a valid report.

## Installation

### Marketplace installation

Each marketplace installs the same canonical skill from `src/super-review/`.

#### Claude Code

```bash
claude plugin marketplace add martinthommesen/super-review
claude plugin install super-review@super-review
```

Invoke the installed plugin explicitly as `/super-review:super-review`.

#### GitHub Copilot CLI

```bash
copilot plugin marketplace add martinthommesen/super-review
copilot plugin install super-review@super-review
```

Invoke the installed skill explicitly as `/super-review`.

#### Codex

```bash
codex plugin marketplace add martinthommesen/super-review
codex plugin add super-review@super-review
```

Invoke the installed plugin explicitly as `$super-review:super-review`.

#### Cursor

This repository is a Cursor plugin (`.cursor-plugin/plugin.json`). It installs the canonical skill and a thin command adapter — nothing else. The plugin registers no MCP server (decision D15): programmatic access to the FINDINGS helpers goes through the consolidated [`super-review` CLI](cli/README.md), which runs only when explicitly invoked with explicit arguments, so Cursor Auto-run has no ambient tool surface to call.

Install from the Cursor marketplace once published, or add this repository as a local/team marketplace plugin and install `super-review`.

Requirements on the machine: `python3` for the bundled helpers.

Invoke the skill explicitly (for example via the plugin command or by naming `$super-review` / `@super-review` / `/super-review` per the skill gate).

### Direct skill installation

The distributable skill is the `src/super-review/` directory. Its bundled Codex policy disables implicit invocation, so it can be installed directly for personal or project use:

```bash
# Codex — personal (all projects)
cp -R src/super-review ~/.agents/skills/super-review

# Codex — project-level
cp -R src/super-review /path/to/project/.agents/skills/super-review
```

Use the marketplace installation for Claude Code and GitHub Copilot CLI; copying only the portable skill would omit the command adapter their slash invocation resolves. Other Agent Skills hosts may use the direct archive only when they provide equivalent explicit-only invocation policy.

Build the deterministic release archive and extract it into a compatible host's skills directory:

```bash
make build verify   # produces dist/super-review-skill.zip + dist/SHA256SUMS
```

## Usage

Invoke the skill explicitly with a target repository or directory (defaults to the current workspace):

```text
$super-review /path/to/repository                # direct Codex install
$super-review:super-review /path/to/repository   # Codex marketplace plugin
@super-review /path/to/repository                # mention-based clients
/super-review /path/to/repository                # Copilot or direct slash alias
/super-review:super-review /path/to/repository   # Claude Code marketplace plugin
```

Optional arguments select a review mode and supply context. The default mode is `REVIEW ONLY`, in which the root `FINDINGS.md` is the sole permitted repository modification — the skill never infers permission for source changes, dependency installation, network access, commits, or any irreversible action.

On completion the skill reports the report path, the reviewed revision, whether the prior report was fully revalidated, the highest-priority active findings, and validation status — the full report lives in `FINDINGS.md`, not the chat.

### Requirements

- A host with filesystem access to the target repository and permission to create or update its root `FINDINGS.md`.
- Python 3 recommended — the bundled helpers are standard-library-only and run in isolated mode (`python3 -I`).
- Git and code-search tools recommended.

## Bundled helpers

The skill ships three stdlib-only scripts, always resolved from the trusted skill root:

- `validate_findings.py` — validates a generated report against the canonical schema (also self-tests) and can `--snapshot` exact on-disk bytes/digest.
- `finding_fingerprint.py` — computes the deterministic canonical-record fingerprint used for finding identity.
- `commit_findings.py` — the digest-gated, annotation-preserving, atomic report writer (`commit_bytes` core with a path CLI front-end).

```bash
python3 -I "$SKILL_ROOT/scripts/validate_findings.py" /tmp/FINDINGS.candidate.md
python3 -I "$SKILL_ROOT/scripts/commit_findings.py" --help
```

### Consolidated CLI

`cli/` packages a `super-review` console command (`validate | snapshot | commit | fingerprint`) that wraps the same skill-root helpers. It replaced the earlier MCP companion (decision D15): a CLI has no server and no ambient tool surface, so nothing can invoke it except an explicit shell command with an explicit trusted skill root. It is **not** in the portable skill ZIP. See [`cli/README.md`](cli/README.md).

## This repository

This repo contains the skill plus its development and release workbench: `src/super-review/` is the only canonical source (never edit `dist/`), `scripts/` holds the offline check/build/verify pipeline, `tests/` and `src/super-review/tests/` hold the regression suites, and `docs/` records architecture, decisions, and provenance.

```bash
make check     # full offline gate: structure, versions, tests, clean-room build + byte-parity verify
make lint      # ruff lint + format check, ty type check
make release   # clean + check + spec + build + verify
```

Contributions: read [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`AGENTS.md`](AGENTS.md) first — the skill's strictness guarantees are protected by non-negotiable invariants and regression tests. Security model and disclosure: [`SECURITY.md`](SECURITY.md). No runtime environment variables are required; [`.env.example`](.env.example) documents that empty secret surface, and CI runs gitleaks. Release history: [`CHANGELOG.md`](CHANGELOG.md). No repository script commits, pushes, publishes, or deploys.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
