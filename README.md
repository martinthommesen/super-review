# Super Review Skill Workbench

This repository is the complete development workspace for the `super-review` Agent Skill. It contains the distributable skill, all bundled helpers and regression tests, deterministic packaging and clean-room verification tools, CI configuration, the original review prompt, design history, and maintainer instructions.

The current skill version is **1.2.0**.

## What the skill does

`super-review` performs a strict, evidence-based whole-repository review spanning engineering, architecture, correctness, security, privacy, reliability, performance, data, APIs, testing, operations, product workflows, UX, developer experience, and feature-portfolio decisions.

Every explicit invocation must create or refresh one canonical report:

```text
<reviewed-repository-root>/FINDINGS.md
```

An existing report is treated as a set of claims to revalidate. Resolved or stale material is removed from active results, surviving findings retain stable identities, protected human annotations survive regeneration, and the final write is digest-gated and atomic.

## Repository layout

```text
.
├── AGENTS.md                         Maintainer rules for coding agents
├── README.md                         Project overview and local workflow
├── CONTRIBUTING.md                   Change and validation workflow
├── SECURITY.md                       Security model and disclosure guidance
├── CHANGELOG.md                      Skill release history
├── VERSION                           Canonical repository version
├── Makefile                          Common development commands
├── pyproject.toml                    Python/tooling metadata
├── requirements-dev.txt              Optional external spec validator
├── src/super-review/                 Exact distributable skill root
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   ├── scripts/
│   └── tests/
├── scripts/                          Repository build and release tooling
├── tests/                            Repository-level regression tests
├── docs/                             Architecture, decisions, history, source prompt
├── examples/FINDINGS.example.md      Valid report example
└── dist/                             Generated release ZIP and checksums
```

`src/super-review/` is the only canonical source for the distributable skill. Never edit `dist/` directly.

## Prerequisites

- Python 3.11 or newer for the complete workbench.
- Python 3 for the bundled skill helpers themselves.
- `make` is convenient but optional.
- `skills-ref` is optional and only needed for the external specification check.

The offline check and build path uses only the Python standard library.

## Start here

Run the complete offline validation pipeline:

```bash
python3 scripts/check.py
```

or:

```bash
make check
```

That command:

1. checks repository structure, versions, source provenance, file types, permissions, and Python syntax;
2. runs the repository tests;
3. runs all bundled skill tests;
4. runs the report validator self-test;
5. generates a release ZIP in a temporary directory;
6. verifies archive safety and exact source parity; and
7. extracts the ZIP and reruns the bundled tests from the extracted package; and
8. removes Python bytecode caches created by nested isolated test processes.

## External Agent Skills specification validation

Create a local environment and install the pinned development dependency:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/spec_validate.py
```

With `uv`:

```bash
uv sync --dev
uv run python scripts/spec_validate.py
```

This invokes the official `skills-ref` reference validator against `src/super-review`.

## Build and verify a release

```bash
python3 scripts/build.py
python3 scripts/verify_dist.py dist/super-review-skill.zip
```

or:

```bash
make build verify
```

The builder creates a deterministic archive containing exactly one top-level `super-review/` directory and writes `dist/SHA256SUMS`. The verifier rejects unsafe paths and symlinks, compares every archived byte with `src/super-review`, checks executable modes, runs ZIP CRC validation, extracts into a temporary directory, and executes the regression suite there.

For the full release gate, including the external specification validator:

```bash
make release
```

No script commits, pushes, publishes, deploys, or creates a GitHub release.

## Install the skill locally

Copy or symlink the canonical source directory into the skill directory used by your agent host. A portable project-level layout is:

```bash
mkdir -p /path/to/project/.agents/skills
cp -R src/super-review /path/to/project/.agents/skills/super-review
```

Alternatively, extract `dist/super-review-skill.zip` into the host's configured skills directory.

Invoke it explicitly:

```text
$super-review /path/to/repository
@super-review /path/to/repository
/super-review /path/to/repository
```

`$super-review` is the preferred Codex form; support for aliases depends on the client.

## Working on the skill

Read `AGENTS.md` before making changes. The short rule is: preserve strictness and invariants, make the smallest coherent change, update every affected reference/helper/test together, and run `python3 scripts/check.py` before considering the change complete.

Important coupling points:

- Report-schema changes require matching updates to record references, `validate_findings.py`, fixtures, tests, and examples.
- Safe-write changes require adversarial regression tests in `test_commit_findings.py`.
- Invocation changes require updates to `SKILL.md`, `agents/openai.yaml`, package tests, README, and release notes.
- Reference restructuring must retain direct `SKILL.md` links and phase-by-phase progressive loading.
- The original source prompt in `docs/ORIGINAL_REVIEW_PROMPT.md` is archival evidence; do not silently rewrite it.

See `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, and `docs/RELEASE.md` for the detailed model.

## Runtime helper examples

Validate a generated report:

```bash
python3 -I /absolute/path/to/super-review/scripts/validate_findings.py /tmp/FINDINGS.candidate.md
```

Compute a deterministic canonical-record fingerprint:

```bash
python3 -I /absolute/path/to/super-review/scripts/finding_fingerprint.py \
  --record-type 'Defect or risk' \
  --category SEC \
  --primary-component 'auth/session' \
  --identity-statement 'session revocation is not enforced at request authorization'
```

Inspect the safe writer's interface:

```bash
python3 -I /absolute/path/to/super-review/scripts/commit_findings.py --help
```

Always resolve these helpers from the trusted loaded skill root, never from the repository under review.

## Licensing

This repository is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
