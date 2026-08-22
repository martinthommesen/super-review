# Contributing

## Before editing

1. Read `AGENTS.md`.
2. Run `python3 scripts/check.py` to establish a baseline.
3. Identify every coupled instruction, helper, fixture, test, example, and document.
4. Keep the change narrowly tied to a demonstrated problem or requirement.

## Development loop

After `uv sync --dev` or `pip install -r requirements-dev.txt`, install the
optional local hooks for Ruff, ty, and CLI checks:

```bash
pre-commit install   # once per clone
pre-commit run --all-files
```

Use the narrowest test while iterating:

```bash
python3 -I src/super-review/tests/run_tests.py
python3 -I tests/run_tests.py
```

Run one test module directly when useful:

```bash
python3 -I src/super-review/tests/test_validate_findings.py
```

Regenerate the example after schema or fixture changes:

```bash
python3 scripts/generate_example.py
```

Before declaring the work complete:

```bash
python3 scripts/check.py
make lint
```

When `cli/` changed, also run (root check/lint intentionally exclude the CLI package):

```bash
make cli-test
```

With development dependencies installed:

```bash
python3 scripts/spec_validate.py
```

## Adding or changing instructions

- State each universal rule once and link to the canonical detailed reference.
- Keep `SKILL.md` focused on activation, routing, invariants, and execution architecture.
- Put deep phase guidance in the directly linked phase reference.
- Put stack-specific guidance behind the phase-20 dispatcher.
- Do not remove applicable checks merely to reduce token count; improve applicability gates and eliminate true duplication instead.
- Explicitly allow evidence-based `Not applicable` rather than forcing speculative content.

## Changing runtime helpers

The shipped helpers are security-sensitive. They must:

- use the Python standard library only;
- resolve bundled sibling modules by trusted canonical path;
- reject unsafe symlink/path behavior;
- avoid ambient imports from the reviewed repository;
- provide precise errors and stable exit codes;
- preserve exact bytes where byte identity is part of the contract;
- receive adversarial tests for every corrected failure mode.

## Changing the report schema

Treat it as a migration across all consumers. Update the normative references, validator, report factory, examples, tests, cross-reference rules, lifecycle behavior, and release notes in one coherent change. Preserve active report compatibility where practical; otherwise document an explicit migration.

## Pull-request checklist

- [ ] Scope is coherent and contains no unrelated cleanup.
- [ ] Non-negotiable invariants remain intact.
- [ ] New failure modes have regression tests.
- [ ] Existing tests were not weakened.
- [ ] `python3 scripts/check.py` passes.
- [ ] `make lint` passes (ruff lint, ruff format check, ty type check).
- [ ] `make cli-test` passes when `cli/` changed.
- [ ] External spec validation passes, or the missing dependency is reported.
- [ ] Version and changelog are updated when behavior is user-visible.
- [ ] Generated `dist/` content was produced by the builder, not edited manually.
