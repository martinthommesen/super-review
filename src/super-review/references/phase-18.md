# PHASE 18 — FEATURE ADDITION, IMPROVEMENT, CONSOLIDATION, AND REMOVAL

Strict anti-filler rule: consider every decision category, but include a canonical feature-decision record only when repository evidence or an explicitly identified product-validation need supports it. For an empty category, state that no recommendation is currently supported and cite the coverage basis; do not brainstorm generic features.

This phase is mandatory.

Review the feature portfolio, not just the implementation.

Classify each significant recommendation as one of:

- ADD.
- IMPROVE.
- SIMPLIFY.
- MERGE.
- REPLACE.
- DEPRECATE.
- REMOVE.
- KEEP.
- EXPERIMENT.
- INVESTIGATE.

-------------------------------------------------------------------------------
FEATURES TO ADD
-------------------------------------------------------------------------------

Identify missing features only when repository evidence indicates a real gap.

Valid evidence may include:

- An incomplete user journey.
- Repeated manual operator intervention.
- Failure states with no recovery mechanism.
- Missing security controls.
- Missing auditability.
- Missing self-service functionality.
- Duplicated implementation work caused by absent platform capability.
- Repeated support-oriented code.
- A documented requirement not implemented.
- Tests or schemas implying intended functionality.
- Partial implementations.
- Feature flags for unfinished work.
- Existing APIs lacking an equivalent interface.
- Common operations requiring direct database manipulation.
- Reliability risks requiring operational controls.

Potential feature categories include:

- User-facing workflow completion.
- Bulk operations.
- Search and filtering.
- Import and export.
- Undo or recovery.
- Preview or dry-run modes.
- Audit logs.
- History.
- Approval workflows.
- Granular permissions.
- Self-service recovery.
- Retry or replay controls.
- Reconciliation.
- Job-status visibility.
- Administrative diagnostics.
- Data portability.
- Accessibility support.
- Localization.
- Notification preferences.
- Integration management.
- API idempotency.
- Rate-limit visibility.
- Usage or quota visibility.
- Maintenance controls.
- Safe data-repair tools.
- Feature-flag management.
- Observability dashboards.

For every proposed feature addition, provide:

1. Feature name.
2. Recommendation classification.
3. Problem being solved.
4. Target actor or user.
5. Evidence of the gap.
6. Current workaround.
7. Consequence of doing nothing.
8. Proposed behavior.
9. Minimal viable scope.
10. Explicit non-goals.
11. User or operator workflow.
12. Required permissions.
13. Data-model changes.
14. API changes.
15. UI changes.
16. Background-processing changes.
17. Security implications.
18. Privacy implications.
19. Operational implications.
20. Compatibility implications.
21. Dependencies.
22. Implementation touchpoints.
23. Test strategy.
24. Migration strategy.
25. Rollout strategy.
26. Rollback strategy.
27. Success indicators.
28. Kill or reconsideration criteria.
29. Estimated effort:
    - Small.
    - Medium.
    - Large.
    - Program-level.
30. Confidence:
    - Confirmed need.
    - Strongly indicated.
    - Plausible.
    - Requires product validation.

Do not invent numerical usage, revenue, conversion, or adoption estimates.

-------------------------------------------------------------------------------
FEATURES TO IMPROVE OR SIMPLIFY
-------------------------------------------------------------------------------

Identify features that:

- Require too many steps.
- Have unclear behavior.
- Have inconsistent implementations.
- Produce avoidable support burden.
- Have poor failure recovery.
- Have unsafe defaults.
- Have confusing permissions.
- Expose implementation details.
- Duplicate other capabilities.
- Require excessive configuration.
- Create avoidable operational complexity.
- Are implemented differently across UI, API, CLI, or integrations.
- Could be made more discoverable.
- Could use progressive disclosure rather than exposing all complexity.
- Could use a safer or clearer default workflow.

For every improvement, identify:

- Current workflow.
- Friction or risk.
- Evidence.
- Proposed workflow.
- Behavior preserved.
- Behavior changed.
- Compatibility impact.
- Migration or rollout path.
- Expected benefit.
- Potential downside.
- Validation required.

-------------------------------------------------------------------------------
FEATURES TO MERGE
-------------------------------------------------------------------------------

Identify features that:

- Solve substantially the same problem.
- Maintain separate code paths with behavioral drift.
- Differ only through historical implementation details.
- Force users to choose between concepts they should not need to distinguish.
- Have separate settings that conflict.
- Duplicate permissions, routes, models, or UI.

For every merge recommendation, identify:

- Features involved.
- Shared purpose.
- Meaningful differences.
- Whether differences should remain as modes or options.
- Proposed unified model.
- Data migration.
- API compatibility.
- UI migration.
- Documentation migration.
- Deprecation sequence.
- Rollback strategy.

-------------------------------------------------------------------------------
FEATURES TO REPLACE
-------------------------------------------------------------------------------

Recommend replacement when a feature:

- Solves the wrong problem.
- Has a fundamentally unsafe design.
- Is too constrained to meet current implied requirements.
- Creates repeated workarounds.
- Is technically expensive to maintain.
- Has an incompatible mental model.
- Duplicates a stronger platform capability.
- Cannot reasonably be repaired incrementally.

For every replacement recommendation, include:

- Existing feature.
- Replacement behavior.
- Why improvement alone is insufficient.
- Migration path.
- Compatibility period.
- Data conversion.
- User communication requirements.
- Rollback plan.
- Risks introduced by the replacement.

-------------------------------------------------------------------------------
FEATURES TO DEPRECATE OR REMOVE
-------------------------------------------------------------------------------

Search for:

- Dead routes.
- Unreachable UI.
- Unused commands.
- Orphaned models.
- Abandoned integrations.
- Expired experiments.
- Permanently disabled flags.
- Permanently enabled flags.
- Deprecated API versions.
- Duplicate implementations.
- Compatibility layers with no remaining consumers.
- Legacy configuration.
- Features documented as obsolete.
- Features with no tests, no documentation, and no reachable entry point.
- Features whose risk or maintenance burden substantially exceeds apparent
  value.
- Features superseded by a better workflow.
- Operator-only functionality that should be replaced with a safer tool.

Do not recommend public feature removal solely because code appears old.

For every deprecation or removal candidate, provide:

1. Feature or capability.
2. Concrete evidence.
3. Known consumers.
4. Possible hidden or external consumers.
5. Usage evidence available.
6. Usage evidence missing.
7. Maintenance burden.
8. Security or reliability risk.
9. Overlap with other features.
10. Consequence of removal.
11. Required telemetry or validation before removal.
12. Deprecation notice strategy.
13. Migration path.
14. Compatibility window.
15. Data-retention implications.
16. Rollback strategy.
17. Final deletion criteria.
18. Confidence.

When usage cannot be established, recommend instrumentation or investigation
rather than immediate removal.

-------------------------------------------------------------------------------
FEATURES TO KEEP
-------------------------------------------------------------------------------

Explicitly identify important features and implementations that should remain.

For each, explain:

- Why it is valuable.
- Why the current design is appropriate.
- Which invariants should be preserved.
- Which tests protect it.
- Which future refactors must not accidentally remove or weaken it.

-------------------------------------------------------------------------------
EXPERIMENTS
-------------------------------------------------------------------------------

Feature experiments must include:

- Hypothesis.
- Target user or workflow.
- Minimal experiment.
- Expected signal.
- Guardrail metrics.
- Failure or stop conditions.
- Data required.
- Privacy implications.
- How experimental code will be isolated.
- Feature-flag owner.
- Expiration or review date.
- Cleanup plan.

Do not recommend permanent feature flags without lifecycle ownership.

===============================================================================
