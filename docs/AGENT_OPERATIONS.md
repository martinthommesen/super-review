# Agent operations

Workbench change discipline, coupling, validation, and release rules for
`super-review`. Read [`AGENTS.md`](../AGENTS.md) first for mission, canonical
paths, and the 14 non-negotiable skill invariants.

## Change discipline

- Make the smallest coherent change that fully addresses the issue.
- Inspect affected instructions, helpers, tests, fixtures, examples, schemas, and release tooling before editing.
- Reuse current patterns. Do not introduce speculative abstractions or dependencies.
- Keep shipped runtime helpers dependency-free unless a concrete requirement justifies a reviewed change.
- The consolidated CLI under `cli/` keeps its own dev pins and lockfile; keep those pins out of root `[dependency-groups].dev` / `requirements-dev.txt`. Its runtime stays dependency-free.
- Preserve public behavior, report compatibility, protected annotations, and stable IDs unless a migration is explicitly designed.
- Avoid formatting churn and unrelated cleanup.
- Never weaken a test merely to make it pass.
- Do not commit, push, publish, deploy, delete data, or modify external systems from repository tooling.

## Coupled changes

When changing report structure or semantics, update all of:

- relevant `references/record-*.md` and `references/final-report.md`;
- `scripts/validate_findings.py`;
- `tests/report_factory.py`;
- validator and writer regression tests;
- `examples/FINDINGS.example.md`;
- documentation and changelog when user-visible.

When changing safe-write behavior, add an adversarial regression for symlinks, hard links, descriptor/path replacement, candidate mutation, digest conflicts, annotation preservation, or exact-byte behavior as applicable.

When changing loading or invocation behavior, update `SKILL.md`, client metadata, package tests, README, architecture/decision docs, and release notes.

## Required validation

During iteration, run the narrowest relevant test. Before completion, run:

```bash
python3 scripts/check.py
make lint
```

When `cli/` changed, also run:

```bash
make cli-test
```

Root `python3 scripts/check.py` and `make lint` intentionally exclude `cli/`; do not treat them as a full-repository green signal when CLI files change.

When `skills-ref` is installed, also run:

```bash
python3 scripts/spec_validate.py
```

Before shipping, run:

```bash
python3 scripts/build.py
python3 scripts/verify_dist.py dist/super-review-skill.zip
```

Report what changed, what passed, and any validation that could not run.

## Versioning and release

- Keep every enforced version location consistent: `VERSION`, `pyproject.toml`, the `Version:` line in `SKILL.md`, `CHANGELOG.md`, the README version sentence, and all versioned plugin/marketplace manifests (full list: `docs/RELEASE.md` step 1; enforced by `tests/test_repository.py`).
- Bump patch for compatible fixes, minor for compatible capability/schema additions, and major for intentional incompatible report or invocation changes.
- Build only through `scripts/build.py`; it creates a deterministic ZIP and checksum.
- Follow `docs/RELEASE.md`. Release tooling must remain local and side-effect-free beyond generated `dist/` files.
