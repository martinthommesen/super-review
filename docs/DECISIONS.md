# Design Decisions

## D1 — Explicit invocation only

The skill is too expensive and too write-oriented for broad automatic matching. The description requires an explicit `$super-review`, `@super-review`, or `/super-review` mention, and client metadata disables implicit invocation where supported.

## D2 — One canonical root report

Every run writes `<canonical-root>/FINDINGS.md`. A nested or differently named report would fragment history and make revalidation ambiguous. In review-only mode, it is the sole permitted repository modification.

## D3 — Existing reports are evidence claims, not append-only logs

A prior report may be stale after code changes. Every prior record, summary claim, roadmap item, evidence location, and status must be revalidated. The new file is regenerated from the current canonical record set rather than blindly appended to.

## D4 — Progressive disclosure by applicability

The original prompt is intentionally exhaustive. Its checks are preserved but split into focused directly linked references. Conditional phases can be closed only after bounded evidence establishes absence, and they reopen if later evidence changes applicability.

## D5 — Repository execution is untrusted

Tests, package scripts, Make targets, generators, lifecycle hooks, and linters can execute arbitrary code. The skill inspects commands before execution, prefers isolation without ambient credentials or network, and requires authorization when safety cannot be established.

## D6 — Runtime helpers resolve only from the skill root

Target-relative `scripts/...` is forbidden. A malicious reviewed repository must not be able to shadow the validator or writer. Absolute canonical paths and isolated Python mode are part of the runtime contract.

## D7 — Exact-byte validation and commit

Validation of a path followed by a reread creates a swap race. The writer opens the candidate once without following its final component, reads immutable bytes, validates those bytes, and stages those same bytes. Path mutation is detected separately.

## D8 — Optimistic concurrency plus protected human blocks

Atomic replacement prevents partial files but not lost updates. The writer records and rechecks starting state, refuses digest conflicts, and preserves named human annotation blocks byte for byte.

## D9 — Deterministic stable identities

Sequential IDs alone are not stable enough across regenerated reports. A deterministic root-cause fingerprint anchors identity, while a retired-ID ledger prevents reuse and supports recurrence.

## D10 — Separate canonical record types

Defects, improvements, feature decisions, and positive patterns have different semantics and fields. Keeping them separate prevents severity and roadmap priority from being conflated and lets summaries reference one authoritative record.

## D11 — Shipped tests are intentional

The runtime helpers are security-sensitive and may be installed independently of this workbench. Shipping the focused regression suite allows an extracted package to validate itself and lets release verification test the exact deliverable.

## D12 — Deterministic, side-effect-limited release tooling

Build and verification tools are standard-library-only and write only to explicit output locations. They do not commit, push, publish, deploy, or contact external services. External specification validation is a separate opt-in dependency.

## D13 — One canonical skill behind thin marketplace adapters

Claude Code, GitHub Copilot CLI, and Codex require different marketplace and plugin manifests. Claude and Copilot share a manual-only command adapter that loads `src/super-review/SKILL.md`; their invocation-control frontmatter is not portable under the Agent Skills specification. Codex points directly to the canonical skill and uses `agents/openai.yaml`. No adapter copies or symlinks the skill. Direct installs keep their unqualified invocation, while marketplace namespaces are accepted as explicit invocation without changing review behavior.
