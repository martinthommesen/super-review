# PHASE 1 — COVERAGE LEDGER AND REPOSITORY INVENTORY

Create a coverage ledger for every top-level directory and meaningful project
area.

For each area, mark it as:

- Deeply reviewed.
- Reviewed.
- Sampled.
- Generated.
- Vendored.
- Excluded by instruction.
- Unable to review.

Include a reason for anything not deeply reviewed.

Inventory:

1. Applications.
2. Services.
3. Libraries.
4. Packages.
5. Executables.
6. CLI tools.
7. Frontend applications.
8. Mobile applications.
9. Workers.
10. Scheduled jobs.
11. Background processors.
12. Webhook handlers.
13. API servers.
14. API clients.
15. Database layers.
16. Data pipelines.
17. Event or message consumers.
18. Event or message producers.
19. Caches.
20. Search systems.
21. Storage systems.
22. Authentication components.
23. Authorization components.
24. Administrative tools.
25. Internal tools.
26. Feature-flag systems.
27. Experiment systems.
28. Logging and observability components.
29. Infrastructure definitions.
30. Deployment definitions.
31. Tests and fixtures.
32. Mock services.
33. Code generators.
34. Schemas and protocol definitions.
35. User-facing documentation.
36. Developer documentation.
37. Operational documentation.

Identify:

- Public entry points.
- Internal entry points.
- External trust boundaries.
- Process boundaries.
- Network boundaries.
- Tenant boundaries.
- Privilege boundaries.
- Data ownership.
- Side-effect ownership.
- Critical paths.
- Single points of failure.
- Cross-package dependencies.
- Circular dependencies.
- Orphaned packages.
- Duplicate subsystems.
- Deprecated paths.
- Hidden or undocumented interfaces.

PHASE 1 DELIVERABLES:

- Coverage ledger.
- Repository map.
- Component responsibility map.
- Dependency map.
- Trust-boundary map.
- Data-ownership map.
- Entry-point inventory.
