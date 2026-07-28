# AGENTS.md

These instructions apply to the entire repository.

## Mission

Maintain `super-review` as a strict, evidence-driven, explicit-invocation Agent Skill. Preserve its exhaustive review coverage while keeping activation and phase loading efficient, safe, deterministic, and testable.

## Canonical paths

- `src/super-review/` is the canonical distributable skill.
- `src/super-review/SKILL.md` is the activation entrypoint.
- `src/super-review/references/` contains normative progressively loaded protocol material.
- `src/super-review/scripts/` contains runtime helpers shipped with the skill.
- `src/super-review/tests/` tests the shipped package and runtime helpers.
- Root `scripts/` contains repository-only build, check, and release tooling.
- Root `tests/` tests repository packaging and maintenance invariants.
- `companion/` is an optional MCP front-end with its own pins/lock/CI; it is not part of the portable skill ZIP.
- `dist/` is generated. Never edit it manually.
- `docs/ORIGINAL_REVIEW_PROMPT.md` is archival source material. Do not rewrite it as part of ordinary refactoring.

## Non-negotiable skill invariants

Do not weaken or remove these without an explicit design decision and matching regression coverage:

1. The skill activates only after an explicit mention.
2. Every valid run creates or refreshes exactly `<canonical-root>/FINDINGS.md`.
3. An existing report is fully revalidated before current findings are merged.
4. Prior report content never limits independent current-repository discovery.
5. Review-only mode permits no repository write other than the canonical report.
6. Repository commands and lifecycle hooks are untrusted until inspected and safely gated.
7. Bundled helpers resolve from the trusted skill root, never the target working directory.
8. Candidate report bytes are read once, validated as immutable bytes, and those same bytes are committed.
9. Concurrent report changes stop or force a revalidation/merge; they are never overwritten blindly.
10. Protected human annotation blocks survive byte for byte.
11. Canonical IDs are deterministic, retired IDs are never reused, and summaries reference canonical records.
12. Defects/risks, improvements/alternatives, feature decisions, and positive patterns remain distinct record types.
13. Progressive disclosure changes loading time, not applicable review coverage.
14. The final report remains evidence-based, uncertainty-aware, migration-conscious, and free of filler.

## Change discipline

- Make the smallest coherent change that fully addresses the issue.
- Inspect affected instructions, helpers, tests, fixtures, examples, schemas, and release tooling before editing.
- Reuse current patterns. Do not introduce speculative abstractions or dependencies.
- Keep shipped runtime helpers dependency-free unless a concrete requirement justifies a reviewed change.
- The optional MCP companion under `companion/` may depend on the MCP SDK; keep those pins out of root `[dependency-groups].dev` / `requirements-dev.txt`.
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

When `companion/` changed, also run:

```bash
make companion-test
```

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

- Keep `VERSION`, `pyproject.toml`, the `Version:` line in `SKILL.md`, and `CHANGELOG.md` consistent.
- Bump patch for compatible fixes, minor for compatible capability/schema additions, and major for intentional incompatible report or invocation changes.
- Build only through `scripts/build.py`; it creates a deterministic ZIP and checksum.
- Follow `docs/RELEASE.md`. Release tooling must remain local and side-effect-free beyond generated `dist/` files.
