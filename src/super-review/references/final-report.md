# Final `FINDINGS.md` schema

Produce one coherent current-state report. Place the machine-readable `SUPER-REVIEW-REGISTRY` first, followed by any preserved global human-annotation blocks, then the sections below in this exact high-level order.

A canonical record appears in full only in its designated section. Other sections reference its ID and provide only concise section-specific synthesis. Do not duplicate evidence, impact, alternatives, or implementation plans across summaries.

If a section has no evidence-supported content, keep the required heading and
state `No current canonical records supported: <coverage and evidence basis>`.
Do not add filler.

# 1. Executive Summary

Begin with these exact metadata labels and current values:

```text
Canonical root: <absolute canonical root, including any workspace-resolved root>
Reviewed branch and revision: <branch and revision, or Not available: reason>
Starting repository state: <revision and worktree/directory fingerprint>
Ending repository state: <revision and worktree/directory fingerprint>
Review time: <ISO 8601 timestamp with timezone>
Review mode: <mode>
Starting FINDINGS.md SHA-256: <MISSING, or sha256: followed by 64 lowercase hexadecimal characters>
Existing report revalidated: <Yes | No — file did not exist | Partial — limitation>
Completion status: <Complete | Partial | Blocked>
Material limitations: <specific limitations or None>
```

These values are cross-checked: `MISSING` pairs exactly with `Existing report revalidated: No — file did not exist` (in both directions); `Completion status: Complete` requires `Existing report revalidated` to be `Yes` or `No — file did not exist`; and `Material limitations: None` is rejected when the completion status is `Partial` or `Blocked`.

Then include:

- Overall codebase health.
- Most serious risks, referencing canonical IDs.
- Most important architectural concern, referencing canonical IDs.
- Most valuable simplification, referencing canonical IDs.
- Most valuable alternative implementation, referencing canonical IDs.
- Most valuable feature addition, referencing canonical IDs.
- Strongest feature-removal or consolidation candidate, referencing canonical IDs.
- Most important positive pattern to preserve, referencing canonical IDs.
- Immediate recommended actions, referencing canonical IDs.
- Main review limitations.

Do not claim the report is exhaustive or fully current beyond the stated completion and evidence limits.

# 2. Repository and System Overview

Include:

- Repository structure.
- Languages and frameworks.
- Applications and services.
- Deployment model.
- Data stores.
- Integrations.
- Entry points.
- Trust boundaries.
- Critical workflows.
- Public contracts.
- Persisted-data contracts.
- Generated and vendored boundaries.
- Review-relevant worktree state.

# 3. Coverage Ledger

Provide a table with:

- Area.
- Review depth: deeply reviewed, reviewed, sampled, generated, vendored, excluded by instruction, or unable to review.
- Main contents.
- Main risks or review focus.
- Evidence inspected.
- Reason for reduced coverage, exclusion, or inability, when applicable.

Every meaningful first-party top-level area and project area must appear exactly once. Reduced coverage must have a concrete reason.

# 4. Architecture and Data-Flow Map

Describe:

- Component relationships.
- Responsibility boundaries.
- Dependency direction.
- Data ownership.
- Trust and privilege boundaries.
- Critical request paths.
- Async workflows and actual delivery guarantees.
- Persistence and transaction boundaries.
- Cache ownership and invalidation.
- External dependencies.
- Operational control points.
- Compatibility boundaries.

Use Mermaid or text diagrams when they materially improve understanding. Diagrams are current claims and must be supported by evidence.

# 5. Top Findings

Provide a concise ranked table with:

- Active canonical ID.
- Title.
- Record type.
- Classification or decision.
- Severity or priority.
- Confidence.
- Affected area.
- One-line recommended action or preservation decision.
- Effort.

This is an index, not a second record body. Include every active Critical and High defect or risk. Include other records only when they materially belong among the highest priorities. Never include retired IDs as current findings.

# 6. Detailed Findings

Present all active **Defect or risk** records using `references/record-defect-risk.md`.

Order by:

1. Critical.
2. High.
3. Medium.
4. Low.
5. Informational.

Within each severity, group by root cause or subsystem. Do not place improvements, alternatives, feature decisions, or positive patterns here.

# 7. Better and Different Ways to Implement the System

Present active **Improvement or alternative** records using `references/record-improvement-alternative.md`.

Ensure the set collectively evaluates every major subsystem or workflow considered in phase 17, including:

- Current approach.
- What is good.
- What is unnecessarily difficult.
- Keep-and-harden option.
- Incremental redesign option.
- Alternative approach.
- Clean-slate ideal, when useful.
- Preferred recommendation.
- Migration sequence.
- What should remain unchanged.

An unsupported option must be marked `Not applicable` with a specific evidence-based reason. Do not create an `IMP` or `ALT` record merely to fill a subsystem quota when the current approach is already appropriate; use a `POS` record when the evidence supports preservation.

# 8. Feature Portfolio Recommendations

Present active **Feature decision** records using `references/record-feature-decision.md`. Group each canonical record under exactly one primary decision subsection:

## 8.1 Add

## 8.2 Improve

## 8.3 Simplify

## 8.4 Merge

## 8.5 Replace

## 8.6 Deprecate

## 8.7 Remove

## 8.8 Keep

## 8.9 Experiment or Investigate

Cross-reference related decisions rather than duplicating one feature under multiple subsections. Do not include generic feature brainstorming. Every decision must be tied to repository evidence or explicitly labeled as requiring product validation.

For an empty subsection, state that no recommendation is currently supported and identify the relevant coverage basis.

# 9. Testing and Validation Gaps

Synthesize, by canonical ID:

- Critical workflows lacking tests.
- Incorrect or brittle tests.
- Missing failure-path tests.
- Missing security tests.
- Missing authorization or tenant-isolation tests.
- Missing concurrency and idempotency tests.
- Missing migration tests.
- Missing contract and compatibility tests.
- Missing performance, accessibility, or operational tests when applicable.
- Recommended test additions by priority and smallest adequate test level.

Do not create generic "add more tests" entries. Point to exact behavior and canonical records.

# 10. Security and Privacy Summary

Include:

- Evidence-based threat model.
- Confirmed vulnerabilities and risks by canonical ID.
- Defense-in-depth gaps.
- Sensitive-data risks.
- Authentication, authorization, and tenant-isolation risks.
- Abuse-resistance gaps.
- Supply-chain or build-pipeline security concerns.
- Required immediate mitigations.
- Disclosure and validation limitations.

Do not reproduce secrets or unnecessary exploit details.

# 11. Performance, Reliability, and Operations Summary

Include, by canonical ID:

- Confirmed bottlenecks.
- Likely and scale-dependent risks.
- Reliability and distributed-systems gaps.
- Recovery, reconciliation, and rollback gaps.
- Observability and alerting gaps.
- Operational features that should be added.
- Cost concerns supported by repository evidence.
- Optimizations that should not yet be pursued.
- Measurement or validation still required.

# 12. Dependency, Build, Deployment, and Supply-Chain Summary

Include, by canonical ID:

- Material dependency risks.
- Build reproducibility.
- Package and artifact contents.
- CI/CD permissions and trust boundaries.
- Container risks.
- Deployment and rollback risks.
- Migration and application-release coupling.
- Provenance, integrity, and signing concerns.
- Licensing concerns.
- Recommended changes.

# 13. Documentation and Developer-Experience Summary

Include, by canonical ID:

- Stale, missing, or contradictory documentation.
- Onboarding problems.
- Local-development friction.
- Feedback-loop and test-environment friction.
- Debugging limitations.
- Tooling improvements.
- Important invariants requiring documentation.
- Positive documentation or DX patterns worth preserving.

# 14. Prioritized Roadmap

Organize active records into:

## Now

## Next

## Later

## Investigate

## Do Not Pursue

For each roadmap row, include:

- Active canonical ID or tightly related ID set.
- One-line goal.
- Dependencies.
- Expected value.
- Effort.
- Risk.
- Completion or validation criteria.

The roadmap is derived from canonical records. It must not introduce a new recommendation, change priority independently, or contain a retired ID as active work.

# 15. Suggested Implementation Sequence

Explain the dependency-aware order of work using active canonical IDs.

Account for:

- Security fixes.
- Data migrations.
- Compatibility and deprecation windows.
- Observability needed before risky changes.
- Test foundations.
- Feature deprecation and consumer migration.
- Rollback capability.
- Operational readiness.
- Opportunities to combine work safely without broadening scope.

State sequencing constraints and parallelizable work. Do not repeat complete implementation outlines.

# 16. Validation Performed

List:

- Exact commands and working directories.
- Command-safety classification and isolation used.
- Results and exit status.
- Material bounded output.
- Failures and whether they appear environmental or code-related.
- Files or external state changed by commands.
- Environmental limitations.
- Areas not validated and why.
- Temporary artifacts created outside the repository and their disposition.
- Report-validator results before and after commit.
- Starting and final `FINDINGS.md` digests.
- Concurrent-edit conflicts and reconciliation performed.
- Prior IDs resolved, superseded, consolidated, reactivated, or not currently verifiable since the previous review.

Do not present retired items as active findings. The machine-readable retired ledger remains authoritative for identity reservation.

# 17. Open Questions and Missing Evidence

Include only questions that materially affect conclusions.

For each question, explain:

- Why it matters.
- Current assumption.
- Evidence required.
- Safe evidence-gathering plan.
- How the recommendation, severity, priority, or confidence changes depending on the answer.

# 18. Positive Patterns Worth Preserving

Present all active **Positive pattern** records using `references/record-positive-pattern.md`.

Cover evidence-supported examples of:

- Strong designs.
- Good security controls.
- Useful test patterns.
- Clear abstractions.
- Effective operational practices.
- Good user workflows.
- Components that should serve as patterns elsewhere.

Do not turn the section into generic praise. Every pattern needs current evidence, explicit invariants, scope limits, and future-regression guidance.
