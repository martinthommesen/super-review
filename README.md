# super-review

[![CI](https://github.com/martinthommesen/super-review/actions/workflows/ci.yml/badge.svg)](https://github.com/martinthommesen/super-review/actions/workflows/ci.yml)

`super-review` is an Agent Skill for evidence-based repository reviews. It
maintains one canonical report:

```text
<reviewed-repository-root>/FINDINGS.md
```

It works with Claude Code, GitHub Copilot CLI, Codex, Cursor, and other Agent
Skills hosts. The current skill version is **1.6.1**.

## What it does

- Revalidates the existing `FINDINGS.md` before adding current results. Resolved
  claims are retired, and surviving findings keep their IDs.
- Requires current repository evidence for confirmed findings. It labels
  inference, uncertainty, missing evidence, and inapplicable checks.
- Treats the target repository as untrusted. Helpers load from the installed
  skill, and report writes use exact bytes, digest checks, and atomic replacement.
- Gives each canonical record a reproducible fingerprint for deduplication and
  retirement across runs.
- Runs only when the user names the skill explicitly.

## Review scope

A run considers 23 ordered phases. They cover repository and product mapping,
architecture, workflows, correctness, security, data, APIs, concurrency,
performance, operations, user interfaces, tests, dependencies, deployment,
maintainability, implementation alternatives, feature decisions, documentation,
language-specific checks, reproduction, and prioritization. The skill loads the
detailed instructions for one applicable phase at a time.

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

This repository is a Cursor plugin (`.cursor-plugin/plugin.json`). It installs
the canonical skill and a small command adapter. It registers no MCP server.
Direct programmatic access goes through the [`super-review` CLI](cli/README.md),
which runs only as an explicit shell command. See decision D15.

Install from the Cursor marketplace once published, or add this repository as a local/team marketplace plugin and install `super-review`.

The bundled helpers require `python3`.

Invoke the plugin command or name `$super-review`, `@super-review`, or
`/super-review`, as supported by the host.

### Direct skill installation

The distributable skill is the `src/super-review/` directory. Its bundled Codex policy disables implicit invocation, so it can be installed directly for personal or project use:

```bash
# Codex: personal install for all projects
cp -R src/super-review ~/.agents/skills/super-review

# Codex: project install
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

Optional arguments select a review mode and add context. The default is
`REVIEW ONLY`. In that mode, the root `FINDINGS.md` is the only permitted
repository change. The skill does not infer permission to change source, install
dependencies, use the network, commit, or take irreversible actions.

On completion, the skill reports the file path, reviewed revision, prior-report
revalidation status, highest-priority active findings, and validation result.
The detailed review stays in `FINDINGS.md`.

### Requirements

- A host with filesystem access to the target repository and permission to create or update its root `FINDINGS.md`.
- Python 3 is recommended. The bundled helpers use only the standard library
  and run in isolated mode with `python3 -I`.
- Git and code-search tools recommended.

## Bundled helpers

The skill ships three stdlib-only scripts, always resolved from the trusted skill root:

- `validate_findings.py`: validates the report schema, runs its self-test, and
  can snapshot exact on-disk bytes and their digest.
- `finding_fingerprint.py`: computes canonical-record fingerprints.
- `commit_findings.py`: validates and atomically writes a report only when the
  starting digest still matches.

```bash
python3 -I "$SKILL_ROOT/scripts/validate_findings.py" /tmp/FINDINGS.candidate.md
python3 -I "$SKILL_ROOT/scripts/commit_findings.py" --help
```

### Command-line interface

`cli/` packages a `super-review` command with `validate`, `snapshot`, `commit`,
and `fingerprint` subcommands. It calls the same helpers from an explicit trusted
skill root. The CLI replaced the MCP companion under decision D15 and is not in
the portable skill ZIP. See [`cli/README.md`](cli/README.md).

## This repository

This repository contains the skill and its development tooling.
`src/super-review/` is the canonical source, `scripts/` contains the offline
check and release pipeline, the two `tests/` trees contain regression suites,
and `docs/` records architecture, decisions, and provenance. Never edit `dist/`
by hand.

```bash
make check     # full offline gate: structure, versions, tests, clean-room build + byte-parity verify
make lint      # ruff lint + format check, ty type check
make release   # clean + check + spec + build + verify
```

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`AGENTS.md`](AGENTS.md) before
contributing. [`SECURITY.md`](SECURITY.md) defines the threat model and disclosure
process. The skill requires no runtime environment variables, and CI runs
gitleaks. See [`CHANGELOG.md`](CHANGELOG.md) for release history. Repository
scripts never commit, push, publish, or deploy.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
