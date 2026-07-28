---
name: workbench-validate
description: Run and interpret the super-review workbench validation loop (check, lint, coverage, spec). Use when verifying workbench changes or preparing a handoff.
---

# Workbench validation

This skill is for the **repository workbench**, not the shipped `super-review` review skill under `src/super-review/`. Do not copy or symlink that package here.

## Commands

```bash
python3 scripts/check.py   # full offline gate
make lint                  # ruff + ty
make coverage              # both suites under coverage.py (drops python -I)
make spec                  # skills-ref (when installed)
```

Narrow loops: `python3 -I tests/run_tests.py` and `python3 -I src/super-review/tests/run_tests.py`.

## Discipline

- Dual-pin any new dev dependency in both `pyproject.toml` and `requirements-dev.txt`.
- Pre-commit ruff `rev` must match the pinned ruff version (`v` prefix on the tag).
- No symlinks in the tree; `scripts/check.py` rejects them.
- Never edit `dist/` or `docs/ORIGINAL_REVIEW_PROMPT.md`.
