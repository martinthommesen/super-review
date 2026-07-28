# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This repo is the development workbench for the `super-review` Agent Skill. Read `AGENTS.md` before substantive edits — it defines 14 non-negotiable skill invariants, change discipline, and a coupled-change matrix that override anything here.

## Commands

- `make check` (= `python3 scripts/check.py`) — full offline gate: structure/version/provenance checks, all tests, build + dist verification. Run before declaring any work done.
- Narrow test loops (custom runners, not pytest): `python3 -I src/super-review/tests/run_tests.py`, `python3 -I tests/run_tests.py`, or a single module e.g. `python3 -I src/super-review/tests/test_validate_findings.py`.
- `make lint` — ruff lint + ruff format check + ty type check (via `uv run`; deps come from `uv sync --dev`). Run alongside `make check` before completion. `make fmt` reformats.
- `make spec` — external spec validation; requires `skills-ref` (`uv sync --dev` or `pip install -r requirements-dev.txt`). If unavailable, report it — don't skip silently.
- `make release` = clean + check + spec + build + verify.

## Non-negotiable rules

- `src/super-review/` is the only canonical source. Never edit `dist/` (generated; verifier enforces byte parity) or `docs/ORIGINAL_REVIEW_PROMPT.md` (archival, sha256-pinned).
- Shipped runtime helpers (`src/super-review/scripts/`) must stay stdlib-only and resolve sibling modules from the skill root, never the target repo/CWD (import-shadowing threat model). Repo tooling (`scripts/`) is also stdlib-only. The optional MCP companion lives under `companion/` with its own dependency pins.
- User-visible changes require bumping all four version locations together: `VERSION`, `pyproject.toml`, the `Version:` line in `src/super-review/SKILL.md`, and `CHANGELOG.md`.
- Dev-tool pins live in two places that must match: `[dependency-groups].dev` in `pyproject.toml` (uv path) and `requirements-dev.txt` (CI pip path).
- Report-schema changes are a migration: update references, `validate_findings.py`, `tests/report_factory.py`, fixtures, `examples/` (via `make example`), tests, and changelog together — see the coupling matrix in `AGENTS.md`.
- Changes to the safe writer (`commit_findings.py`) require adversarial regression tests (symlink/hard-link/descriptor swaps, digest conflicts, annotation preservation).
- Never commit, push, publish, or deploy from repository tooling.
