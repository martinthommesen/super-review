<!-- SUPER-REVIEW-REGISTRY
{
  "active": {
    "COR-001": "sha256:9fd9891994eaf555479976364dd5c61c85c4b509a9704fadb439b0746fd45971",
    "FEAT-001": "sha256:d984b21bfdbe98cf72734818001110a982150cf0ac9c50a34050f96267300315",
    "IMP-001": "sha256:e8bfab07b42d48f62a123972eb7dede03748ff65655d27fd215f6660d5359939",
    "POS-001": "sha256:378e24d290f2d6fc97047b3c2217575968376337a537fe7b1cd00caad3db290e"
  },
  "next_sequence": {
    "COR": 2,
    "FEAT": 2,
    "IMP": 2,
    "POS": 2
  },
  "retired": {},
  "schema_version": 2
}
-->

# 1. Executive Summary

Canonical root: //example.invalid/super-review/repo
Reviewed branch and revision: main at abc123
Starting repository state: abc123 clean
Ending repository state: abc123 clean
Review time: 2026-07-22T12:00:00+02:00
Review mode: REVIEW ONLY
Starting FINDINGS.md SHA-256: MISSING
Existing report revalidated: No — file did not exist
Completion status: Complete
Material limitations: None

# 2. Repository and System Overview

No current canonical records supported: test fixture.

# 3. Coverage Ledger

No current canonical records supported: test fixture.

# 4. Architecture and Data-Flow Map

No current canonical records supported: test fixture.

# 5. Top Findings

- COR-001: [COR-001] Boundary validation permits an invalid state

# 6. Detailed Findings

## [COR-001] Boundary validation permits an invalid state

Record type: Defect or risk

ID category: COR

Primary component: core/request-boundary

Identity statement: request trust-boundary validation is incomplete

Fingerprint: sha256:9fd9891994eaf555479976364dd5c61c85c4b509a9704fadb439b0746fd45971

Status: Active

Classification: Confirmed defect

Severity or priority: High

Confidence: Confirmed

Affected components: Request parser, domain service, and persisted records.

Evidence:
- `src/request.py:10-24`: validation omits the state invariant.

Current behavior: The request reaches the domain service without the required invariant.

Expected or preferred behavior: Reject the invalid state before any side effect.

Trigger or scenario: A caller supplies a syntactically valid but semantically invalid state.

Impact: Incorrect requests can be accepted and produce inconsistent state.

Reach: All callers of the affected request path.

Root cause: request trust-boundary validation is incomplete

Why existing tests did not catch it: Boundary fixtures cover syntax but not the domain invariant.

Minimal reproduction: Construct the invalid state and invoke the request handler.

Recommended action: Validate the invariant at the trust boundary and retain domain enforcement.

Alternative approaches:
1. Boundary and domain validation.
2. Domain-only validation with typed construction.
3. Not applicable: keeping the gap is unsafe.

Preferred option: Boundary and domain validation because it fails early and preserves defense in depth.

Implementation outline: Update parser validation, typed construction, callers, and regression fixtures.

Compatibility and migration: No public shape change; invalid requests begin failing explicitly.

Validation: Unit and integration regression tests for invalid and valid states.

Effort: Small: one boundary and focused tests.

Risk of the proposed change: Low: behavior changes only for invalid input.

Dependencies: None.

Open questions: Not applicable: intended invariant is established by schema and tests.

# 7. Better and Different Ways to Implement the System

## [IMP-001] Consolidate pipeline normalization only when the trigger is met

Record type: Improvement or alternative

ID category: IMP

Primary component: core/pipeline

Identity statement: pipeline stages duplicate normalization responsibilities

Fingerprint: sha256:e8bfab07b42d48f62a123972eb7dede03748ff65655d27fd215f6660d5359939

Status: Active

Classification: Workflow simplification

Severity or priority: Do not pursue

Confidence: High

Affected components: Pipeline stages and their callers.

Evidence:
- `src/pipeline.py:20-80`: normalization is repeated across stages.

Current approach: Each stage normalizes the same input independently.

Why it appears to exist: Stages were added incrementally and retained local ownership.

What it does well: Each stage remains understandable in isolation.

Actual limitations: Repeated normalization can drift and adds maintenance work.

Essential versus accidental complexity: Stage boundaries are essential; repeated normalization is accidental.

Triggering context or scale: The change becomes worthwhile when another stage needs the same normalization.

### Option A — Keep and harden

Minimal changes: Document one canonical algorithm and add parity tests.

Benefits: Lowest migration risk.

Costs: Duplication remains.

Risks: Implementations can still drift.

Expected lifetime: Appropriate while the pipeline remains small.

Correct-use conditions: Choose when no new stage requires the behavior.

### Option B — Incremental redesign

Structural change: Introduce one typed normalized input before stage dispatch.

Benefits: Removes drift while preserving stage boundaries.

Costs: Requires caller and fixture migration.

Migration steps: Add the type, migrate one stage at a time, then remove duplicate paths.

Compatibility considerations: Preserve external input and output contracts.

Testing requirements: Parity, failure-path, and integration tests.

Rollback strategy: Retain the old constructors until all stages are validated.

### Option C — Alternative approach

Alternative design: Use a shared stateless normalization function without a new type.

Benefits: Smaller code change.

Costs: Weaker invariant ownership.

New risks: Callers may bypass normalization.

Operational consequences: None beyond ordinary deployment validation.

Team-skill implications: No new specialist knowledge.

Dependency implications: No new dependency.

Migration complexity: Low.

### Option D — Clean-slate ideal, when useful

Ideal design: Parse once into a domain-valid value consumed by every stage.

Incrementally useful parts: The typed normalized input is useful now.

Parts not worth pursuing: A full pipeline rewrite is not justified.

Rewrite judgment: Incremental migration is sufficient.

Recommendation: Do not pursue now; retain the incremental option for the stated trigger.

Expected benefit: Avoids premature churn while preserving a bounded future path.

Implementation outline: No current code change; keep parity tests and revisit at the trigger.

Compatibility and migration: Not applicable: no change is recommended now.

Validation: Reassess when another stage duplicates normalization.

Effort: Small: investigation only.

Risk of the proposed change: Low: the current recommendation is to defer.

Dependencies: Evidence of another consumer or material drift.

Open questions: Not applicable: the decision threshold is explicit.

# 8. Feature Portfolio Recommendations

## 8.1 Add

No current canonical records supported: test fixture.

## 8.2 Improve

No current canonical records supported: test fixture.

## 8.3 Simplify

No current canonical records supported: test fixture.

## 8.4 Merge

No current canonical records supported: test fixture.

## 8.5 Replace

No current canonical records supported: test fixture.

## 8.6 Deprecate

No current canonical records supported: test fixture.

## 8.7 Remove

No current canonical records supported: test fixture.

## 8.8 Keep

## [FEAT-001] Preserve the bounded audit-history capability

Record type: Feature decision

ID category: FEAT

Primary component: product/audit-history

Identity statement: audit history provides required operator traceability

Fingerprint: sha256:d984b21bfdbe98cf72734818001110a982150cf0ac9c50a34050f96267300315

Status: Active

Decision: Keep

Priority: Later

Confidence: High

Feature or capability: Audit history

Target actor: Operator and support engineer.

Problem or opportunity: The capability provides traceability for privileged changes.

Repository evidence: Routes, persistence, authorization tests, and operator documentation.

Current workaround: Not applicable: the capability already exists.

Consequence of doing nothing: The current traceability remains available.

Proposed behavior: Preserve the current capability and its authorization boundary.

Why this is better: The implementation is bounded and already covers the evidenced workflow.

Minimal viable scope: Keep behavior and strengthen regression coverage.

Non-goals: No analytics expansion or new retention policy.

User or operator workflow: Authorized operators search and inspect immutable entries.

Required permissions: Existing least-privilege operator permission.

Data-model changes: Not applicable: preserve the existing schema.

API changes: Not applicable: preserve the existing contract.

UI changes: Not applicable: preserve the existing interface.

Background-processing changes: Not applicable: no background processing is involved.

Security implications: Preserve authorization, integrity, and sensitive-field redaction.

Privacy implications: Preserve minimization and retention controls.

Operational impact: Retain existing monitoring and support workflow.

Compatibility impact: No compatibility change.

Known consumers: Operator UI and support workflow.

Possible hidden or external consumers: No public API; verify internal exports before refactoring.

Usage evidence available: Reachable routes, tests, and operator docs.

Usage evidence missing: Production frequency is unavailable and not required for preservation.

Maintenance burden: Bounded to one service and one interface.

Overlap with other features: No material overlap established.

Alternatives considered:
1. Keep current design.
2. Replace storage: unsupported.
3. Remove: unsafe and unsupported.

Dependencies: Existing authorization and retention controls.

Implementation touchpoints: Authorization tests and audit-history service.

Test strategy: Integration tests for permission, ordering, redaction, and retention.

Migration strategy: Not applicable: no migration.

Rollout or deprecation plan: Not applicable: preserve current behavior.

Rollback strategy: Not applicable: no behavioral change.

Data-retention implications: Preserve the established retention policy.

Success indicators: Existing workflows and controls continue to pass.

Reconsideration or removal criteria: Reconsider only with replacement traceability and consumer evidence.

Final deletion criteria: Not applicable: keep decision.

Effort: Small: regression coverage only.

Risks: Accidental weakening during unrelated refactors.

Preservation rationale: The feature is required for traceability and is proportionate.

Invariants to preserve: Authorization, immutability, ordering, redaction, and retention.

Tests that protect it: Authorization and integration tests; add retention coverage.

Future-refactor constraints: Do not merge it with mutable activity feeds.

## 8.9 Experiment or Investigate

No current canonical records supported: test fixture.

# 9. Testing and Validation Gaps

No current canonical records supported: test fixture.

# 10. Security and Privacy Summary

No current canonical records supported: test fixture.

# 11. Performance, Reliability, and Operations Summary

No current canonical records supported: test fixture.

# 12. Dependency, Build, Deployment, and Supply-Chain Summary

No current canonical records supported: test fixture.

# 13. Documentation and Developer-Experience Summary

No current canonical records supported: test fixture.

# 14. Prioritized Roadmap

## Now

- COR-001: fixture roadmap item.

## Next

No current canonical records supported: test fixture.

## Later

- FEAT-001: fixture roadmap item.

## Investigate

No current canonical records supported: test fixture.

## Do Not Pursue

- IMP-001: fixture roadmap item.

# 15. Suggested Implementation Sequence

No current canonical records supported: test fixture.

# 16. Validation Performed

No current canonical records supported: test fixture.

# 17. Open Questions and Missing Evidence

No current canonical records supported: test fixture.

# 18. Positive Patterns Worth Preserving

## [POS-001] Preserve centralized domain authorization

Record type: Positive pattern

ID category: POS

Primary component: security/authorization

Identity statement: authorization is centralized at the domain operation boundary

Fingerprint: sha256:378e24d290f2d6fc97047b3c2217575968376337a537fe7b1cd00caad3db290e

Status: Active

Classification: Positive pattern worth preserving

Severity or priority: Informational

Confidence: High

Affected components: All entry points invoking the domain operation.

Evidence: Shared domain authorization and cross-entry-point tests.

Why it is valuable: It prevents policy drift across interfaces.

Why the current design is appropriate: One operation owns the invariant without framework leakage.

Invariants to preserve: Every entry point must invoke the same authorized operation.

Tests and controls that protect it: Contract and authorization tests across entry points.

Risks of changing it: Duplicated checks could diverge or be bypassed.

Reuse opportunities: Apply to the adjacent privileged workflow after confirming equivalent policy.

Scope limits: Do not centralize unrelated presentation validation.
