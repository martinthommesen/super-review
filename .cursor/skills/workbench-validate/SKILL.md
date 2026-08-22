---
name: workbench-validate
description: Run and interpret the super-review workbench validation loop (check, lint, cli-test, coverage, spec). Use when verifying workbench changes or preparing a handoff.
---

# Workbench validation

This skill is for the **repository workbench**, not the shipped `super-review` review skill under `src/super-review/`. Do not copy or symlink that package here.

## Commands

```bash
python3 scripts/check.py   # core offline gate (excludes cli/)
make lint                  # root ruff + ty (excludes cli/)
make cli-test              # required when cli/ changed
make coverage              # diagnostic coverage of root/skill suites (drops python -I)
make spec                  # skills-ref (when installed)
```

Narrow loops: `python3 -I tests/run_tests.py` and `python3 -I src/super-review/tests/run_tests.py`.

## Discipline

- Dual-pin any new root dev dependency in both `pyproject.toml` and `requirements-dev.txt`.
- Pre-commit ruff `rev` must match the pinned ruff version (`v` prefix on the tag).
- CLI changes must run `make cli-test`; root check/lint alone are not a full-repo green signal.
- No symlinks in the tree; `scripts/check.py` rejects them.
- Never edit `dist/` or `docs/ORIGINAL_REVIEW_PROMPT.md`.
