# PHASE 2 — PRODUCT, DOMAIN, USER, AND FEATURE INVENTORY

Before recommending features, understand what the product currently does.

Infer the domain model from:

- Routes.
- Commands.
- UI pages.
- API endpoints.
- Database schemas.
- Domain models.
- Permissions.
- Jobs.
- Events.
- Configuration.
- Documentation.
- Examples.
- Tests.
- Feature flags.
- Integration adapters.

Build a feature inventory covering:

1. User-facing features.
2. Administrative features.
3. Operator features.
4. Internal-support features.
5. Developer-facing features.
6. Integration features.
7. Security features.
8. Compliance features.
9. Reporting features.
10. Import and export features.
11. Automation features.
12. Notification features.
13. Experimental features.
14. Hidden features.
15. Partially implemented features.
16. Deprecated features.
17. Feature-flagged features.
18. Features exposed through one interface but missing from another.

For each meaningful feature, identify:

- Intended user or actor.
- Problem it appears to solve.
- Entry points.
- Permissions.
- Main implementation components.
- Data it reads or writes.
- External side effects.
- Operational dependencies.
- Tests.
- Documentation.
- Error behavior.
- Known limitations.
- Apparent overlap with other features.
- Evidence of active use, when available.
- Evidence of abandonment, when available.
- Support and maintenance burden, when inferable.

Map key user journeys and operator journeys.

Look for:

- Incomplete workflows.
- Dead ends.
- Workflows requiring unnecessary manual steps.
- Repeated data entry.
- Inconsistent terminology.
- Different behavior across UI, API, CLI, and integrations.
- Missing confirmation for destructive actions.
- Missing undo or recovery paths.
- Missing bulk operations.
- Missing search, filtering, or pagination.
- Missing export or portability.
- Missing auditability.
- Missing status visibility.
- Missing retry or reconciliation controls.
- Missing permission granularity.
- Excessive administrative privilege requirements.
- Features that exist technically but are difficult to discover or use.
- Features whose implementation complexity appears disproportionate to their
  apparent value.

Do not claim that a feature is unused solely because documentation is missing.

PHASE 2 DELIVERABLES:

- Domain summary.
- Actor and permission map.
- Feature inventory.
- User-journey map.
- Operator-journey map.
- Initial list of feature gaps.
- Initial list of redundant or questionable features.

===============================================================================
