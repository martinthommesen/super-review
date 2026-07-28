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

Change discipline, coupled-change matrix, required validation, and versioning/release rules: [`docs/AGENT_OPERATIONS.md`](docs/AGENT_OPERATIONS.md).
