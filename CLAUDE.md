# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This repository is the development workbench for the `super-review` Agent Skill.
Read `AGENTS.md` before substantive edits. It defines the 14 non-negotiable
invariants. `docs/AGENT_OPERATIONS.md` defines change discipline, coupled files,
validation, and versioning, and takes precedence over this file.

## Commands

- `make check` runs the full offline gate: structure, versions, provenance,
  tests, build, and distribution verification.
- `make cli-test` syncs the CLI environment and runs its lint and test suite.
  Run it whenever `cli/` changes.
- Narrow test loops (custom runners, not pytest): `python3 -I src/super-review/tests/run_tests.py`, `python3 -I tests/run_tests.py`, or a single module e.g. `python3 -I src/super-review/tests/test_validate_findings.py`.
- `make lint` runs Ruff lint, Ruff format check, and ty through `uv`. Run it
  with `make check`. `make fmt` reformats.
- `make spec` runs external validation and requires `skills-ref`. Install it with
  `uv sync --dev` or `pip install -r requirements-dev.txt`. Report if it cannot run.
- `make release` = clean + check + spec + build + verify.

## Non-negotiable rules

- `src/super-review/` is the only canonical source. Never edit `dist/` (generated; verifier enforces byte parity) or `docs/ORIGINAL_REVIEW_PROMPT.md` (archival, sha256-pinned).
- Shipped runtime helpers (`src/super-review/scripts/`) must stay stdlib-only and resolve sibling modules from the skill root, never the target repo/CWD (import-shadowing threat model). Repo tooling (`scripts/`) is also stdlib-only. The consolidated CLI lives under `cli/` with its own dependency pins.
- User-visible changes bump every enforced version location together: `VERSION`, `pyproject.toml`, the `Version:` line in `src/super-review/SKILL.md`, `CHANGELOG.md`, the README version sentence, and all versioned plugin/marketplace manifests. `docs/RELEASE.md` step 1 lists the full set; `tests/test_repository.py` enforces it.
- Dev-tool pins live in two places that must match: `[dependency-groups].dev` in `pyproject.toml` (uv path) and `requirements-dev.txt` (CI pip path).
- Treat report-schema changes as migrations. Update references, the validator,
  report factory, fixtures, generated example, tests, and changelog together.
- Changes to the safe writer (`commit_findings.py`) require adversarial regression tests (symlink/hard-link/descriptor swaps, digest conflicts, annotation preservation).
- Never commit, push, publish, or deploy from repository tooling.
