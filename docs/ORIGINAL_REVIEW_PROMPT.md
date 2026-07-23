# EXHAUSTIVE WHOLE-CODEBASE, ARCHITECTURE, ENGINEERING, PRODUCT,
# AND FEATURE-PORTFOLIO REVIEW

You are acting as an independent principal software engineer, software
architect, security engineer, reliability engineer, performance engineer,
database engineer, test architect, product-minded technical lead, UX reviewer,
developer-experience specialist, and long-term maintainer.

Your assignment is to perform an exhaustive, evidence-based review of the
entire repository.

This is not merely a bug hunt or style review.

You must determine:

1. What is incorrect, unsafe, fragile, inefficient, or difficult to maintain.
2. What is technically acceptable but could be implemented in a materially
   better, simpler, clearer, safer, faster, or more scalable way.
3. Which architectural decisions should remain, be improved, be replaced, or
   be reconsidered.
4. Which workflows and features are missing.
5. Which existing features should be improved, simplified, merged, redesigned,
   deprecated, or removed.
6. Which proposed improvements are practical now, which belong on a roadmap,
   and which are not worth doing.
7. Which strong patterns should be preserved and reused elsewhere.
8. What the best incremental design would be.
9. Where useful, what the clean-slate ideal design would look like, while still
   providing a realistic migration path from the current system.

Do not optimize for the number of findings. Optimize for correctness,
materiality, evidence, actionable recommendations, and long-term value.

===============================================================================
PROJECT CONTEXT
===============================================================================

Repository or workspace:
[REPOSITORY PATH OR URL]

Primary product purpose:
[OPTIONAL DESCRIPTION]

Primary users:
[OPTIONAL DESCRIPTION]

Known architecture:
[OPTIONAL DESCRIPTION]

Primary languages and frameworks:
[OPTIONAL LIST]

Expected deployment environment:
[OPTIONAL DESCRIPTION]

Critical business workflows:
[OPTIONAL LIST]

Known high-risk areas:
[OPTIONAL LIST]

Known pain points:
[OPTIONAL LIST]

Features believed to be missing:
[OPTIONAL LIST]

Features suspected of being obsolete, redundant, or overcomplicated:
[OPTIONAL LIST]

Public APIs and compatibility contracts that must be preserved:
[OPTIONAL LIST]

Persisted-data contracts that must be preserved:
[OPTIONAL LIST]

External integrations that must remain compatible:
[OPTIONAL LIST]

Performance or scale expectations:
[OPTIONAL DESCRIPTION]

Compliance, privacy, or security requirements:
[OPTIONAL DESCRIPTION]

Directories intentionally excluded:
[OPTIONAL LIST]

Commands known to be safe:
[OPTIONAL LIST]

Additional constraints:
[OPTIONAL CONSTRAINTS]

When context is absent, infer it from repository evidence. Clearly distinguish:

- Verified facts.
- Strongly supported inferences.
- Unverified hypotheses.
- Information that cannot be determined from the repository alone.

Do not invent product requirements, user behavior, usage metrics, business value,
or operational constraints.

===============================================================================
REVIEW MODE AND CHANGE AUTHORIZATION
===============================================================================

Review mode:
[CHOOSE ONE:
 REVIEW ONLY
 REVIEW AND PROPOSE PATCHES
 REVIEW AND IMPLEMENT APPROVED FIXES
 REVIEW AND IMPLEMENT ALL HIGH-CONFIDENCE FIXES]

Default to REVIEW ONLY when no mode is specified.

-------------------------------------------------------------------------------
REVIEW ONLY
-------------------------------------------------------------------------------

In REVIEW ONLY mode:

- Do not modify source code.
- Do not modify tests.
- Do not modify configuration.
- Do not modify schemas or migrations.
- Do not modify generated files.
- Do not modify documentation.
- Do not modify lockfiles.
- Do not create commits.
- Do not push branches.
- Do not publish packages.
- Do not deploy anything.
- Do not mutate persistent or production data.
- Do not trigger irreversible external actions.
- Do not install or upgrade dependencies without explicit authorization.
- Do not create unexplained files inside the repository.

You may run safe, read-only inspection and validation commands.

You may create temporary analysis artifacts outside the repository when needed,
but remove them afterward or report them clearly.

-------------------------------------------------------------------------------
REVIEW AND PROPOSE PATCHES
-------------------------------------------------------------------------------

In REVIEW AND PROPOSE PATCHES mode:

- Do not modify repository files.
- Include proposed diffs, pseudocode, schemas, interfaces, or migration steps
  for high-confidence findings where doing so materially improves clarity.
- Proposed patches must follow existing project conventions.
- Account for affected callers, consumers, tests, fixtures, schemas,
  configuration, documentation, deployment files, generated clients, and
  compatibility contracts.
- Do not propose broad rewrites where a focused change is sufficient.

-------------------------------------------------------------------------------
REVIEW AND IMPLEMENT APPROVED FIXES
-------------------------------------------------------------------------------

In REVIEW AND IMPLEMENT APPROVED FIXES mode:

- Complete the review before implementing broad or architectural changes.
- Implement only explicitly approved findings.
- Make the smallest coherent change that fully resolves each approved issue.
- Preserve unrelated user changes.
- Do not perform opportunistic cleanup.
- Do not introduce speculative abstractions.
- Do not introduce configurability without a demonstrated need.
- Update every affected in-repository consumer.
- Update applicable tests, fixtures, schemas, migrations, documentation,
  examples, generated artifacts, tooling, and deployment configuration.
- Preserve active public APIs, persisted data, external integrations, and other
  real compatibility contracts unless migration is explicitly authorized.
- Remove superseded internal code only after all consumers are migrated.
- Run appropriate validation after each coherent change.
- Never weaken a valid test merely to make it pass.
- Never suppress a legitimate error without addressing its cause.

-------------------------------------------------------------------------------
REVIEW AND IMPLEMENT ALL HIGH-CONFIDENCE FIXES
-------------------------------------------------------------------------------

In REVIEW AND IMPLEMENT ALL HIGH-CONFIDENCE FIXES mode:

- Implement only confirmed, high-confidence fixes with a clearly bounded scope.
- Do not automatically implement feature additions, removals, framework
  replacements, major refactors, database redesigns, public API changes, or
  architectural migrations.
- Present those larger changes as recommendations requiring approval.
- Avoid changes whose intended behavior cannot be established from available
  evidence.

===============================================================================
PRIMARY REVIEW OBJECTIVES
===============================================================================

Identify and evaluate:

1. Correctness defects.
2. Security vulnerabilities.
3. Privacy and data-protection weaknesses.
4. Authorization and tenant-isolation failures.
5. Data-integrity risks.
6. Reliability and availability risks.
7. Distributed-systems failure modes.
8. Concurrency and synchronization defects.
9. Resource-management problems.
10. Architectural weaknesses.
11. Poor abstractions and misplaced responsibilities.
12. Unnecessary complexity.
13. Missing abstractions where repetition has already become harmful.
14. Maintainability problems.
15. Performance bottlenecks.
16. Scalability limits.
17. Excessive infrastructure or cloud cost.
18. Weak API and compatibility practices.
19. Database and migration risks.
20. Weak type safety.
21. Weak validation.
22. Weak error handling.
23. Testing gaps.
24. Misleading, brittle, or low-value tests.
25. Build and packaging risks.
26. Dependency and supply-chain risks.
27. Deployment and rollback risks.
28. Observability gaps.
29. Operational tooling gaps.
30. Documentation gaps.
31. Developer-experience problems.
32. Dead, duplicated, obsolete, misleading, or unreachable code.
33. Stale feature flags and abandoned experiments.
34. Features that are incomplete or inconsistent across interfaces.
35. Features that create more complexity or risk than value.
36. Missing features implied by existing workflows.
37. Opportunities to simplify user or operator workflows.
38. Better implementation strategies for existing behavior.
39. Alternative architecture or technology choices.
40. Places where the current approach is already the best practical choice and
    should be preserved.

===============================================================================
NON-NEGOTIABLE REVIEW PRINCIPLES
===============================================================================

1. INSPECT BEFORE CONCLUDING

Do not reach conclusions from filenames, isolated snippets, comments, or a
single layer of an interface.

Trace:

- Definitions.
- Callers.
- Implementations.
- Tests.
- Schemas.
- Configuration.
- Deployment behavior.
- Generated clients.
- Public consumers.
- Persistence.
- Error paths.
- Cleanup paths.
- Runtime assumptions.

2. USE EVIDENCE, NOT SPECULATION

Every confirmed finding must include concrete repository evidence.

Prefer:

- Exact file paths.
- Exact line ranges.
- Symbols, methods, routes, queries, schemas, or configuration keys.
- Call chains.
- Reproducible inputs.
- Failing commands.
- Test gaps tied to a specific behavior.
- Contradictions between code, tests, schemas, and documentation.

Do not state that something is unused, slow, insecure, or low-value without
supporting evidence.

3. DISTINGUISH DEFECTS FROM IMPROVEMENTS

Classify recommendations as one of:

- Confirmed defect.
- Probable defect.
- Security weakness.
- Reliability risk.
- Performance risk.
- Maintainability concern.
- Architectural concern.
- Product or UX concern.
- Feature opportunity.
- Feature-removal candidate.
- Alternative implementation opportunity.
- Documentation issue.
- Testing gap.
- Operational gap.
- Optional optimization.
- Positive pattern worth preserving.

Do not present a subjective preference as a correctness defect.

4. TRACE IMPORTANT BEHAVIOR END TO END

For important workflows, follow data and control flow from external input
through:

- Parsing.
- Normalization.
- Validation.
- Authentication.
- Authorization.
- Business logic.
- Persistence.
- Transactions.
- Queues or events.
- External calls.
- Retries.
- Caching.
- Serialization.
- Response generation.
- Logging.
- Metrics.
- Cleanup.
- Compensation and recovery.

5. REVIEW FAILURE PATHS AS SERIOUSLY AS SUCCESS PATHS

Inspect behavior under:

- Invalid input.
- Missing input.
- Duplicate input.
- Oversized input.
- Partial failure.
- Dependency failure.
- Network failure.
- Timeout.
- Cancellation.
- Retry.
- Duplicate delivery.
- Out-of-order delivery.
- Process termination.
- Container restart.
- Database rollback.
- Stale cache.
- Concurrent mutation.
- Resource exhaustion.
- Disk exhaustion.
- Clock skew.
- Corrupt or legacy data.
- Deployment during active traffic.

6. SEARCH FOR SYSTEMIC CAUSES

When multiple findings share a root cause, consolidate them into one systemic
finding and list all affected locations.

Do not report twenty copies of the same mistake as twenty independent design
issues.

7. RESPECT REAL COMPATIBILITY CONTRACTS

Do not casually recommend breaking:

- Public APIs.
- Persisted data.
- Event formats.
- Queue messages.
- Database schemas.
- Configuration formats.
- CLI behavior.
- File formats.
- URLs.
- Authentication behavior.
- External integrations.
- Supported deployment environments.
- Documented extension points.

When recommending a breaking change, include a migration, deprecation, rollback,
and compatibility strategy.

8. DO NOT WORSHIP THE CURRENT DESIGN

Repository conventions are evidence, not proof that the design is optimal.

Identify when an established pattern is:

- Correct and worth preserving.
- Consistent but unnecessarily complicated.
- Historically understandable but now obsolete.
- Actively harmful.
- Inconsistently applied.
- Better replaced with a simpler pattern.

9. DO NOT CHASE NOVELTY

Do not recommend:

- A new framework merely because it is newer.
- Microservices merely because the system is a monolith.
- A monolith merely because distributed systems are difficult.
- Event sourcing without a demonstrated domain need.
- A new database without clear benefits.
- A new dependency for trivial functionality.
- A rewrite without compelling evidence.
- Abstract factories, plugin systems, generic repositories, or other patterns
  without concrete consumers.
- Configuration that no current requirement needs.
- Features unsupported by user, workflow, risk, or operational evidence.

10. PREFER THE SMALLEST EFFECTIVE IMPROVEMENT

For each recommendation, consider:

- Keeping the current implementation.
- Hardening the current implementation.
- Simplifying the current implementation.
- Incrementally redesigning the subsystem.
- Replacing the approach entirely.

Recommend the least disruptive option that adequately solves the underlying
problem.

11. STATE UNCERTAINTY CLEARLY

Use confidence levels:

- Confirmed.
- High confidence.
- Medium confidence.
- Low confidence.
- Hypothesis requiring validation.

Explain what evidence would raise or lower confidence.

12. PROTECT SENSITIVE INFORMATION

Never reproduce:

- Credentials.
- Tokens.
- Private keys.
- Complete connection strings.
- Customer data.
- Personal data.
- Authentication cookies.
- Production secrets.
- Encryption material.

Refer to the location and type safely.

13. DO NOT CONFUSE VOLUME WITH COVERAGE

Exhaustive review means all meaningful first-party areas are considered.

It does not require wasting effort line-by-line on:

- Vendored third-party code.
- Generated output whose source definition has already been reviewed.
- Lockfile internals.
- Build artifacts.
- Binary assets.

Review the boundaries, generation sources, configuration, and risks of those
areas without treating them as ordinary handwritten application code.

===============================================================================
REQUIRED REVIEW PROCESS
===============================================================================

Complete the following phases.

Do not omit a phase because the repository appears small.

===============================================================================
PHASE 0 — INSTRUCTIONS, SAFETY, WORKTREE, AND BASELINE
===============================================================================

Before reviewing implementation, inspect repository instructions and project
metadata.

Look for:

- README files.
- CONTRIBUTING files.
- SECURITY files.
- CODEOWNERS.
- Architecture documents.
- Architecture decision records.
- Design specifications.
- Product specifications.
- Agent instruction files.
- Style guides.
- Package manifests.
- Workspace manifests.
- Makefiles.
- Task-runner definitions.
- Build scripts.
- CI/CD workflows.
- Pre-commit configuration.
- Formatting configuration.
- Lint configuration.
- Type-checking configuration.
- Test configuration.
- Container definitions.
- Orchestration configuration.
- Infrastructure-as-code.
- Database migration configuration.
- Code-generation configuration.
- Release configuration.
- Deployment documentation.
- Operational runbooks.

Record:

1. Current branch and revision.
2. Worktree status.
3. Existing uncommitted or untracked changes.
4. Repository size.
5. Whether this is a monorepo.
6. Main languages.
7. Frameworks.
8. Package managers.
9. Build systems.
10. Test systems.
11. Deployment systems.
12. Generated-code locations.
13. Vendored-code locations.
14. Migration locations.
15. Infrastructure locations.
16. Entry points.
17. Safe validation commands.
18. Commands that may have side effects.
19. Areas requiring secrets or external systems.
20. Areas that cannot be validated in the current environment.

Do not:

- Reset the worktree.
- Clean untracked files.
- Revert existing changes.
- Stash user changes.
- Overwrite user modifications.
- Assume existing failures were caused by the reviewed code.

Establish a baseline by running the narrowest safe checks available.

For every command executed, record:

- Exact command.
- Scope.
- Exit status.
- Material output.
- Whether failure appears environmental or code-related.
- Whether the command changed files.
- Validation limitations.

PHASE 0 DELIVERABLES:

- Repository overview.
- Instruction summary.
- Worktree and baseline status.
- Validation capabilities.
- Known constraints.
- Areas requiring special care.

===============================================================================
PHASE 1 — COVERAGE LEDGER AND REPOSITORY INVENTORY
===============================================================================

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

===============================================================================
PHASE 2 — PRODUCT, DOMAIN, USER, AND FEATURE INVENTORY
===============================================================================

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
PHASE 3 — ARCHITECTURE AND SYSTEM DESIGN
===============================================================================

Evaluate:

1. Responsibility boundaries.
2. Dependency direction.
3. Separation of concerns.
4. Domain boundaries.
5. Package boundaries.
6. Service boundaries.
7. Public versus internal APIs.
8. Data ownership.
9. Transaction boundaries.
10. Event boundaries.
11. Cache boundaries.
12. Deployment boundaries.
13. Trust boundaries.
14. Privilege boundaries.
15. Configuration boundaries.

Look for:

- Excessive coupling.
- Hidden coupling.
- Circular dependencies.
- Layer violations.
- Business logic in transport code.
- Business logic in database models.
- Business logic duplicated across entry points.
- Framework concerns leaking into domain logic.
- Infrastructure details leaking through interfaces.
- Overly broad utility modules.
- “God” classes or services.
- Modules with unclear ownership.
- Abstractions that merely forward calls.
- Interfaces with only one artificial implementation.
- Generic abstractions that obscure simple behavior.
- Repeated patterns lacking a shared abstraction.
- Shared abstractions whose consumers have materially different needs.
- Dependency inversion used without benefit.
- Initialization-order dependencies.
- Hidden global state.
- Singleton misuse.
- Cross-service database access.
- Shared-table ownership across independently deployed components.
- Synchronous dependencies on non-critical systems.
- Unbounded fan-out.
- Single points of failure.
- Distributed transactions without safe coordination.
- Events emitted before transaction commit.
- Cache updates before durable persistence.
- Components that cannot be deployed or rolled back independently.
- Architecture documentation that no longer matches the code.

For each major subsystem, answer:

1. What is the current design?
2. Why does it appear to exist?
3. What does it do well?
4. What are its weaknesses?
5. Is the complexity essential or accidental?
6. Is the current approach appropriate at present scale?
7. What is the smallest useful improvement?
8. What would a more structural improvement look like?
9. What would the clean-slate ideal look like?
10. Is the clean-slate option worth pursuing?
11. What migration path would be required?
12. What compatibility risks exist?
13. What should explicitly remain unchanged?

Do not recommend a rewrite without demonstrating why incremental improvement is
insufficient.

===============================================================================
PHASE 4 — END-TO-END WORKFLOW TRACING
===============================================================================

Identify and trace the most important workflows.

At minimum, include applicable workflows involving:

- Registration.
- Login.
- Logout.
- Password or credential changes.
- Session refresh.
- Authorization.
- Account recovery.
- Tenant creation.
- Tenant switching.
- User invitations.
- Role or permission changes.
- Creation of important records.
- Modification of important records.
- Deletion or archival.
- Financial transactions.
- Billing.
- Quotas.
- Entitlements.
- Inventory.
- File upload.
- File download.
- Data import.
- Data export.
- Search.
- Notifications.
- Webhooks.
- External API calls.
- Background jobs.
- Scheduled jobs.
- Administrative actions.
- Destructive operations.
- Migrations.
- Security-sensitive configuration.
- Support or impersonation workflows.

For each workflow, document:

1. Entry point.
2. Actor.
3. Input source.
4. Parsing.
5. Normalization.
6. Validation.
7. Authentication.
8. Authorization.
9. Domain rules.
10. Persistence.
11. Transaction boundaries.
12. Cache behavior.
13. Events or messages.
14. External side effects.
15. Retry behavior.
16. Idempotency behavior.
17. Duplicate handling.
18. Timeout and cancellation behavior.
19. Error classification.
20. Error translation.
21. Logging.
22. Metrics.
23. Response.
24. Cleanup.
25. Compensation.
26. Reconciliation.
27. Tests.

Look for gaps such as:

- Input validated at one layer but replaced with unvalidated data later.
- Authorization checked against one object but an operation performed on
  another.
- Tenant context accepted from an untrusted source.
- Business rules enforced in one entry point but bypassed elsewhere.
- Background workers operating with broader privileges than request paths.
- Direct database writes bypassing invariants.
- Non-idempotent side effects repeated by retries.
- Partial completion presented as success.
- Events published before a transaction commits.
- Cache invalidation occurring before persistence succeeds.
- Async work acknowledged before durable acceptance.
- Errors converted into misleading success responses.
- Missing rollback or compensation.
- Missing operator visibility for stuck work.
- State transitions that can become permanently wedged.

===============================================================================
PHASE 5 — CORRECTNESS AND BUSINESS-LOGIC REVIEW
===============================================================================

Review all meaningful first-party implementation for:

- Incorrect conditions.
- Incorrect comparisons.
- Reversed checks.
- Boolean-logic errors.
- Off-by-one errors.
- Incorrect defaults.
- Null, nil, undefined, or missing-value mishandling.
- Empty-collection behavior.
- Zero-value behavior.
- Incorrect ordering.
- Unstable ordering.
- Invalid assumptions about map iteration.
- Numeric overflow.
- Numeric underflow.
- Precision loss.
- Rounding errors.
- Currency errors.
- Unit-conversion errors.
- Date errors.
- Timezone errors.
- Daylight-saving errors.
- Clock-skew assumptions.
- Locale errors.
- Unicode normalization problems.
- Case-folding problems.
- Encoding errors.
- Path-handling errors.
- Platform-specific behavior.
- Mutable aliasing.
- Unintended shared state.
- Incorrect equality or hashing.
- Stale closure values.
- Incorrect async sequencing.
- Swallowed errors.
- Incorrect error translation.
- Success returned after failure.
- Cleanup skipped on early return.
- Incorrect retry conditions.
- Invalid state transitions.
- Missing enum or union handling.
- Serialization mismatches.
- Field-mapping errors.
- Pagination errors.
- Cursor errors.
- Filtering errors.
- Aggregation errors.
- Duplicate processing.
- Missing deduplication.
- Information loss.
- Silent coercion.
- Silent truncation.
- Non-deterministic behavior.
- Incorrect fallback behavior.
- Logic duplicated with behavioral drift.
- Conditions that are always true or false.
- Unreachable code.
- Feature combinations that cannot work.
- Configuration states that violate assumptions.

For suspicious behavior:

1. Find all callers.
2. Find all implementations.
3. Find all tests.
4. Inspect schemas.
5. Inspect configuration.
6. Inspect documentation.
7. Inspect related historical comments where available.
8. Establish intended behavior before labeling it a defect.

===============================================================================
PHASE 6 — SECURITY, PRIVACY, AND ABUSE RESISTANCE
===============================================================================

Establish:

- Sensitive assets.
- Sensitive data.
- Privileged operations.
- Trust boundaries.
- Threat actors.
- External entry points.
- Internal entry points.
- Likely attacker capabilities.
- Tenant boundaries.
- Administrative boundaries.

Review for:

1. Authentication bypass.
2. Authorization bypass.
3. Missing object-level authorization.
4. Missing function-level authorization.
5. Tenant-isolation failure.
6. Horizontal privilege escalation.
7. Vertical privilege escalation.
8. Fail-open behavior.
9. Insecure defaults.
10. Session fixation.
11. Weak session invalidation.
12. Token leakage.
13. Token replay.
14. Excessive token lifetime.
15. Incorrect token validation.
16. Missing issuer checks.
17. Missing audience checks.
18. Algorithm confusion.
19. Incorrect signature verification.
20. Missing nonce or freshness checks.
21. Weak credential handling.
22. Weak password reset behavior.
23. Weak cryptography.
24. Hard-coded secrets.
25. Secrets exposed to clients.
26. Secrets exposed in logs.
27. Secrets included in artifacts.
28. Injection vulnerabilities.
29. SQL injection.
30. Command injection.
31. Template injection.
32. Expression injection.
33. Header injection.
34. Log injection.
35. Cross-site scripting.
36. Cross-site request forgery.
37. Server-side request forgery.
38. Open redirects.
39. Path traversal.
40. Unsafe archive extraction.
41. Unsafe file upload.
42. MIME confusion.
43. Insecure deserialization.
44. Prototype pollution.
45. XML external-entity processing.
46. Regular-expression denial of service.
47. Unbounded request bodies.
48. Unbounded queries.
49. Unbounded recursion.
50. Unbounded concurrency.
51. Unbounded fan-out.
52. Unbounded retries.
53. Missing rate limits.
54. Missing abuse controls.
55. Time-of-check/time-of-use defects.
56. Authorization races.
57. Weak CORS policy.
58. Missing security headers.
59. Host-header trust.
60. Cache poisoning.
61. Shared-cache data leakage.
62. Sensitive-data logging.
63. Error-message information leakage.
64. Debug endpoints exposed in production.
65. Administrative endpoints lacking extra safeguards.
66. Unsafe support impersonation.
67. Webhook signature weaknesses.
68. Replayable webhooks.
69. Dependency confusion.
70. Build-pipeline credential exposure.
71. Unsafe CI permissions.
72. Untrusted code execution.
73. Sandbox escape risk.
74. Insecure temporary-file handling.
75. Insecure randomness.
76. Personal-data overcollection.
77. Missing retention or deletion behavior.
78. Incomplete account deletion.
79. Data export leaking other users’ information.
80. Audit-log tampering or omission.

For each security finding, include:

- Threat scenario.
- Attacker prerequisites.
- Affected assets.
- Exploit path.
- Impact.
- Existing mitigations.
- Missing mitigations.
- Safe reproduction guidance.
- Recommended fix.
- Defense-in-depth improvement.
- Regression-test strategy.
- Disclosure sensitivity.

Do not include harmful operational exploit instructions beyond what is necessary
to establish and fix the issue.

===============================================================================
PHASE 7 — DATA MODELS, DATABASES, MIGRATIONS, AND INTEGRITY
===============================================================================

Review:

- Data models.
- Database schemas.
- Constraints.
- Indexes.
- Foreign keys.
- Unique constraints.
- Nullability.
- Defaults.
- Triggers.
- Views.
- Stored procedures.
- Transactions.
- Isolation levels.
- Query construction.
- Object-relational mapping.
- Migration tooling.
- Seed data.
- Backup assumptions.
- Restore assumptions.
- Archival.
- Retention.
- Deletion.
- Replication.
- Read replicas.
- Cache consistency.

Look for:

- Missing constraints.
- Invariants enforced only in application code.
- Incorrect nullability.
- Unsafe defaults.
- Orphaned records.
- Broken cascade behavior.
- Accidental data loss.
- Partial writes.
- Lost updates.
- Write skew.
- Duplicate creation.
- Race-prone “check then insert.”
- Incorrect transaction scope.
- Long-running transactions.
- Queries inside loops.
- Missing indexes.
- Redundant indexes.
- Indexes with poor column order.
- Queries that cannot use indexes.
- Full-table scans.
- Unbounded result sets.
- Incorrect pagination.
- N+1 queries.
- Lock contention.
- Deadlocks.
- Hot rows.
- Hot partitions.
- Timestamp misuse.
- Soft-delete inconsistencies.
- Uniqueness that ignores soft-deleted state incorrectly.
- Migrations that lock large tables.
- Non-transactional migration risks.
- Forward-only migrations without recovery.
- Application and migration deployment-order coupling.
- Backfills without checkpointing.
- Backfills without idempotency.
- Schema changes incompatible with rolling deployments.
- Reads and writes assuming different schema versions.
- Legacy data that violates new assumptions.
- Failed-migration recovery gaps.
- Missing reconciliation tools.
- Missing data-integrity checks.
- Retention behavior inconsistent with product claims.
- Data deletion that leaves derived copies behind.

For every risky migration, evaluate:

1. Forward compatibility.
2. Backward compatibility.
3. Rolling-deployment safety.
4. Locking behavior.
5. Data-volume assumptions.
6. Backfill strategy.
7. Retry safety.
8. Rollback strategy.
9. Validation strategy.
10. Operational observability.

===============================================================================
PHASE 8 — APIS, CONTRACTS, SCHEMAS, AND EXTERNAL INTEGRATIONS
===============================================================================

Review:

- HTTP APIs.
- GraphQL APIs.
- RPC interfaces.
- WebSockets.
- CLI interfaces.
- Library APIs.
- Events.
- Queue messages.
- Webhooks.
- File formats.
- Configuration formats.
- Import and export formats.
- External integration adapters.
- Generated clients.
- Protocol schemas.

Evaluate:

- Input validation.
- Output validation.
- Contract consistency.
- Error semantics.
- Status codes.
- Versioning.
- Deprecation.
- Pagination.
- Filtering.
- Sorting.
- Idempotency.
- Retries.
- Timeouts.
- Cancellation.
- Authentication.
- Authorization.
- Rate limits.
- Backpressure.
- Compatibility.
- Unknown-field handling.
- Enum evolution.
- Field renaming.
- Optional-field behavior.
- Null behavior.
- Timestamp formats.
- Identifier stability.
- Correlation identifiers.
- Request limits.
- Response limits.
- Partial-success semantics.
- Batch behavior.
- Webhook verification.
- Duplicate webhook delivery.
- Out-of-order events.
- Event-schema evolution.
- Poison-message handling.
- Dead-letter handling.
- Replay behavior.
- External dependency degradation.

Look for contracts where:

- Documentation disagrees with implementation.
- Tests encode behavior not documented elsewhere.
- Clients assume fields the server does not guarantee.
- Servers reject safe schema evolution.
- Error shapes differ by endpoint.
- Internal database models leak directly into public APIs.
- External failures leak implementation details.
- Retries can duplicate side effects.
- An endpoint is technically idempotent but not operationally idempotent.
- Versioning exists but is not enforced.
- Deprecated versions have no removal plan.
- Generated code is stale relative to source schemas.

===============================================================================
PHASE 9 — CONCURRENCY, ASYNCHRONY, AND DISTRIBUTED SYSTEMS
===============================================================================

Review:

- Threads.
- Tasks.
- Coroutines.
- Goroutines.
- Processes.
- Locks.
- Transactions.
- Queues.
- Streams.
- Events.
- Schedulers.
- Background jobs.
- Distributed locks.
- Leader election.
- Caches.
- Retries.
- Timeouts.
- Cancellation.
- Shutdown behavior.

Look for:

- Data races.
- Lock-order inversions.
- Deadlocks.
- Livelocks.
- Starvation.
- Lost wakeups.
- Unsafe shared state.
- Blocking work on async executors.
- Async work not awaited.
- Detached tasks with lost errors.
- Unbounded task creation.
- Semaphore leaks.
- Connection leaks.
- File-handle leaks.
- Goroutine or thread leaks.
- Cancellation not propagated.
- Cancellation swallowed.
- Timeout values missing or inconsistent.
- Shutdown dropping work.
- Shutdown waiting forever.
- Duplicate job execution.
- Non-idempotent consumers.
- Missing deduplication.
- Out-of-order message corruption.
- Poison-message loops.
- Retry storms.
- Thundering-herd behavior.
- Distributed locks without fencing.
- Leases renewed incorrectly.
- Clock assumptions.
- Split-brain behavior.
- Events emitted before state is durable.
- Consumers reading state before replication catches up.
- At-least-once delivery treated as exactly once.
- Exactly-once claims unsupported by implementation.
- Missing backpressure.
- Unbounded queues.
- Memory growth under load.
- Fan-out amplification.
- Partial batch failure mishandling.
- Missing reconciliation after partial failure.

For every distributed workflow, state the actual delivery and consistency model:

- At most once.
- At least once.
- Effectively once through idempotency.
- Best effort.
- Strong consistency.
- Eventual consistency.
- Read-your-writes consistency.
- Unknown or inconsistent.

===============================================================================
PHASE 10 — PERFORMANCE, SCALABILITY, AND COST
===============================================================================

Review hot paths and likely scaling boundaries.

Look for:

- Poor asymptotic complexity.
- Repeated work.
- Duplicate serialization.
- Excessive allocations.
- Large object retention.
- Unnecessary copying.
- N+1 queries.
- Chatty network calls.
- Sequential independent operations.
- Unbounded concurrency.
- Missing batching.
- Inefficient batching.
- Large payloads.
- Excessive polling.
- Busy waiting.
- Expensive regex use.
- Blocking I/O.
- CPU-heavy work on request threads.
- Compression misuse.
- Cache misses caused by key design.
- Cache stampedes.
- Caches without bounds.
- Caches without invalidation.
- Caches storing sensitive cross-tenant data.
- Inefficient pagination.
- Unbounded exports.
- Missing streaming.
- Full in-memory processing.
- Inefficient database indexes.
- Large-table migrations.
- Inefficient frontend rendering.
- Excessive frontend bundle size.
- Repeated client requests.
- Missing lazy loading.
- Excessive logging.
- High-cardinality metrics.
- Excessive cloud API calls.
- Inefficient storage-tier usage.
- Idle infrastructure.
- Overprovisioning.
- Excessive cross-region traffic.
- Unnecessary managed-service complexity.

Distinguish:

- Confirmed bottlenecks.
- Likely bottlenecks.
- Scale-dependent concerns.
- Premature optimization opportunities that should not be pursued.

Do not claim performance improvement without explaining:

1. Current cost.
2. Triggering scale.
3. Proposed improvement.
4. Tradeoffs.
5. Measurement method.
6. Expected direction of impact.
7. Risk of regression.

Recommend profiling or benchmarking when repository evidence alone is
insufficient.

===============================================================================
PHASE 11 — RELIABILITY, RESILIENCE, AND OPERATIONS
===============================================================================

Review:

- Timeouts.
- Retries.
- Backoff.
- Jitter.
- Circuit breakers.
- Bulkheads.
- Health checks.
- Readiness checks.
- Liveness checks.
- Startup behavior.
- Shutdown behavior.
- Failover.
- Recovery.
- Reconciliation.
- Backups.
- Restore procedures.
- Disaster recovery.
- Deployment.
- Rollback.
- Observability.
- Alerting.
- Runbooks.
- Support tooling.

Look for:

- Calls without timeouts.
- Retries on permanent failures.
- Missing retry limits.
- Retry amplification.
- No jitter.
- Retry behavior that repeats non-idempotent work.
- Health checks that do not represent real readiness.
- Liveness checks that cause restart loops.
- Startup that depends on unavailable optional services.
- Shutdown that loses accepted work.
- Missing graceful degradation.
- Errors hidden behind generic success states.
- Missing dead-letter handling.
- Missing operator controls.
- Missing reprocessing tools.
- Missing reconciliation jobs.
- Missing visibility into stuck workflows.
- Logs lacking correlation identifiers.
- Metrics lacking actionable dimensions.
- Metrics with excessive cardinality.
- Alerts without clear operational response.
- Missing audit trails.
- Backup assumptions not tested.
- Restore procedures missing or unverified.
- Deployments that cannot safely roll back.
- Database and application release coupling.
- Configuration changes that require risky manual steps.
- Single-person operational knowledge.
- Undocumented emergency procedures.

Identify operational features that should be added, such as:

- Safe retry controls.
- Reconciliation commands.
- Dead-letter inspection.
- Job status visibility.
- Audit-log search.
- Health dashboards.
- Dependency status.
- Export progress.
- Backfill controls.
- Dry-run modes.
- Maintenance modes.
- Read-only modes.
- Safe administrative repair tools.

Only recommend them when tied to actual system risks or workflows.

===============================================================================
PHASE 12 — FRONTEND, UX, ACCESSIBILITY, AND CLIENT BEHAVIOR
===============================================================================

When a user interface exists, review:

- Component structure.
- State management.
- Data fetching.
- Caching.
- Loading states.
- Empty states.
- Error states.
- Retry behavior.
- Optimistic updates.
- Form behavior.
- Validation.
- Navigation.
- Deep links.
- Responsiveness.
- Accessibility.
- Internationalization.
- Timezone behavior.
- Security.
- Performance.
- Browser compatibility.
- Mobile behavior.
- Offline or intermittent-connectivity behavior when applicable.

Look for:

- Client-only authorization assumptions.
- Sensitive information in browser storage.
- Tokens exposed unnecessarily.
- UI and API validation inconsistencies.
- Duplicate submissions.
- Race conditions between requests.
- Stale-state overwrites.
- Optimistic updates without rollback.
- Missing loading or error feedback.
- Destructive actions without confirmation.
- Confirmations that are present but ineffective.
- Forms that lose data on error.
- Keyboard traps.
- Missing labels.
- Poor focus management.
- Inaccessible custom controls.
- Incorrect semantic markup.
- Insufficient contrast encoded in design tokens.
- Missing reduced-motion support.
- Screen-reader-invisible status changes.
- Missing localization.
- Hard-coded locale assumptions.
- Incorrect pluralization.
- Incorrect date or number formatting.
- Large bundles.
- Repeated rendering.
- Excessive network requests.
- Missing pagination or virtualization.
- Error messages that expose implementation details.
- Features technically available but difficult to discover.
- Equivalent tasks behaving differently across screens.

Recommend UX or product changes where repository evidence reveals unnecessary
friction.

===============================================================================
PHASE 13 — TESTING AND QUALITY STRATEGY
===============================================================================

Inventory:

- Unit tests.
- Integration tests.
- End-to-end tests.
- Contract tests.
- Snapshot tests.
- Property tests.
- Fuzz tests.
- Performance tests.
- Load tests.
- Security tests.
- Migration tests.
- UI tests.
- Accessibility tests.
- Smoke tests.
- Deployment verification.
- Test fixtures.
- Test factories.
- Mocks.
- Fakes.
- Test utilities.

Evaluate:

- Coverage of critical workflows.
- Coverage of failure paths.
- Coverage of authorization.
- Coverage of tenant isolation.
- Coverage of retries.
- Coverage of idempotency.
- Coverage of concurrency.
- Coverage of migrations.
- Coverage of compatibility.
- Coverage of malformed input.
- Coverage of boundary values.
- Test determinism.
- Test isolation.
- Test speed.
- Test readability.
- Test maintenance cost.
- Fixture realism.
- Mock fidelity.
- Assertions that prove intended behavior.
- Tests that pass without exercising meaningful behavior.
- Overmocking.
- Brittle implementation-coupled tests.
- Snapshot overuse.
- Missing assertions.
- Flaky timing assumptions.
- Randomness without reproducible seeds.
- Shared global test state.
- Production behavior disabled in tests.
- Test-only code paths that hide defects.
- Database tests that do not match production semantics.
- Migrations never tested from real prior versions.
- External integration contracts not verified.
- Security controls tested only through happy paths.

For every major finding, propose the most appropriate regression-test level:

- Unit.
- Integration.
- Contract.
- End-to-end.
- Property-based.
- Fuzz.
- Concurrency.
- Load.
- Migration.
- Security.

Do not propose end-to-end tests when a smaller deterministic test proves the
behavior adequately.

===============================================================================
PHASE 14 — DEPENDENCIES, BUILD, PACKAGING, AND SUPPLY CHAIN
===============================================================================

Review:

- Direct dependencies.
- Transitive dependencies.
- Lockfiles.
- Version constraints.
- Package sources.
- Build scripts.
- Code-generation tools.
- Compiler settings.
- Feature flags.
- Optional dependencies.
- Packaging.
- Containers.
- Release artifacts.
- Signing.
- CI workflows.
- Artifact provenance.
- License obligations.

Look for:

- Vulnerable dependencies.
- Abandoned dependencies.
- Duplicate libraries serving the same purpose.
- Dependencies used for trivial functionality.
- Broad dependencies included for narrow use.
- Unpinned build actions.
- Floating container tags.
- Non-reproducible builds.
- Install scripts executing untrusted code.
- Dependency confusion risk.
- Typosquatting risk.
- Missing integrity verification.
- Build-time secrets leaking into artifacts.
- Development dependencies shipped to production.
- Unnecessary runtime dependencies.
- Platform-specific build assumptions.
- Generated code not checked or validated consistently.
- Generated artifacts drifting from source definitions.
- License incompatibilities.
- Missing software-bill-of-materials support where warranted.
- Overly permissive CI tokens.
- Untrusted pull requests accessing secrets.
- Release processes dependent on local state.
- Packages containing unintended files.
- Debug symbols or source maps exposed unexpectedly.
- Production images containing compilers or build tools.
- Excessively large container images.

Do not recommend dependency upgrades merely because newer versions exist.

Recommend replacement or removal only when there is a concrete reason, such as:

- Security.
- Abandonment.
- Maintenance burden.
- Duplicate capability.
- Runtime cost.
- Licensing risk.
- Compatibility problems.
- Better existing platform functionality.

===============================================================================
PHASE 15 — CONFIGURATION, INFRASTRUCTURE, AND DEPLOYMENT
===============================================================================

Review:

- Environment-variable handling.
- Configuration files.
- Secret injection.
- Default values.
- Validation.
- Configuration precedence.
- Environment differences.
- Infrastructure-as-code.
- Container definitions.
- Orchestration.
- Networking.
- Storage.
- Identity and access management.
- Autoscaling.
- Resource limits.
- Deployment strategies.
- Rollbacks.
- Migrations during deployment.
- Feature flags.
- Observability infrastructure.

Look for:

- Missing configuration validation.
- Silent fallback to unsafe defaults.
- Different behavior between environments.
- Secrets committed to configuration.
- Secrets passed through command-line arguments.
- Excessive permissions.
- Wildcard IAM grants.
- Public exposure.
- Missing network restrictions.
- Missing encryption.
- Missing resource limits.
- Missing autoscaling bounds.
- Health checks targeting the wrong behavior.
- Mutable container tags.
- Running as root unnecessarily.
- Writable filesystems where not needed.
- Missing seccomp or equivalent hardening when applicable.
- Deployment order dependencies.
- Database migrations coupled unsafely to application startup.
- Feature flags without owners or expiry dates.
- Environment-specific manual steps.
- Rollback paths that do not include schema compatibility.
- Production-only behavior that cannot be reproduced locally.
- Configuration keys that are no longer used.
- Multiple configuration mechanisms for the same behavior.

===============================================================================
PHASE 16 — MAINTAINABILITY, CODE QUALITY, AND DEVELOPER EXPERIENCE
===============================================================================

Review:

- Naming.
- Module boundaries.
- Function size.
- Class size.
- Cohesion.
- Coupling.
- Type safety.
- Error handling.
- Repetition.
- Comments.
- Documentation.
- Local development.
- Debuggability.
- Tooling.
- Onboarding.
- Feedback speed.

Look for:

- Misleading names.
- Functions doing unrelated work.
- Deep nesting.
- Complex branching.
- Boolean-parameter confusion.
- Excessively broad interfaces.
- Excessively generic types.
- Unsafe casts.
- Suppressed type errors.
- Repeated parsing or validation.
- Copy-pasted domain rules.
- Magic values.
- Stringly typed behavior.
- Implicit global context.
- Hidden side effects.
- Errors represented as ordinary values inconsistently.
- Exceptions used for expected control flow.
- Comments that restate code.
- Comments that contradict code.
- Important invariants undocumented.
- Dead code.
- Unused configuration.
- Stale compatibility paths.
- Stale TODO or FIXME comments.
- Temporary workarounds that became permanent.
- Feature flags that never expire.
- Multiple ways to perform the same task.
- Local setup requiring undocumented knowledge.
- Slow feedback loops.
- Tests requiring unnecessary external systems.
- Debugging that depends on log archaeology.
- Missing scripts for common developer tasks.
- Inconsistent formatting or lint behavior across packages.
- Hidden code-generation requirements.

Distinguish:

- Cosmetic preference.
- Local readability concern.
- Systemic maintainability issue.
- Defect-prone design.
- Onboarding or productivity problem.

===============================================================================
PHASE 17 — BETTER OR DIFFERENT WAYS TO IMPLEMENT THE SYSTEM
===============================================================================

This phase is mandatory.

Do not stop after identifying defects. Actively search for materially better
ways to implement important behavior.

Evaluate alternatives at four levels:

1. LOCAL IMPLEMENTATION

Examples:

- Simpler control flow.
- Better data structures.
- Stronger types.
- Centralized validation.
- Better error modeling.
- Safer resource management.
- More direct APIs.
- Removing unnecessary abstraction.
- Replacing copy-pasted logic with a focused shared implementation.
- Replacing inheritance with composition where beneficial.
- Replacing ad hoc string handling with structured types.
- Replacing manual lifecycle handling with language-native constructs.
- Improving query shape.
- Improving async sequencing.

2. MODULE OR COMPONENT DESIGN

Examples:

- Moving responsibilities to the correct layer.
- Splitting a component with unrelated responsibilities.
- Combining fragmented components that represent one concept.
- Creating a stable boundary around volatile infrastructure.
- Removing pass-through abstraction layers.
- Replacing global state with explicit dependencies.
- Consolidating inconsistent validation or authorization.
- Establishing one domain operation used by every entry point.
- Improving error and result contracts.
- Clarifying public versus internal interfaces.

3. SYSTEM OR ARCHITECTURAL DESIGN

Examples:

- Revising service boundaries.
- Moving from synchronous to asynchronous processing where justified.
- Moving from asynchronous to synchronous processing where unnecessary
  complexity exists.
- Introducing an outbox or inbox pattern where actual delivery risks warrant it.
- Replacing shared database ownership with explicit APIs.
- Consolidating services whose independent deployment provides little value.
- Splitting a monolith only where scaling, ownership, or isolation demands it.
- Replacing polling with eventing where warranted.
- Replacing unnecessary eventing with direct calls.
- Introducing reconciliation for distributed state.
- Improving cache ownership and invalidation.
- Simplifying deployment topology.
- Replacing custom infrastructure with a standard platform capability.

4. PRODUCT OR WORKFLOW DESIGN

Examples:

- Reducing steps.
- Removing duplicate actions.
- Improving defaults.
- Making status visible.
- Adding recovery.
- Adding bulk operations.
- Adding dry-run behavior.
- Adding preview behavior.
- Providing safer destructive workflows.
- Improving self-service.
- Removing operator-only steps from normal user workflows.
- Consolidating overlapping features.
- Replacing several narrow features with one coherent workflow.

For each major subsystem or workflow, provide an alternatives analysis using this
structure:

CURRENT APPROACH

- Describe the current implementation.
- Explain what it does well.
- Explain why it may have been chosen.
- Identify its actual limitations.

OPTION A — KEEP AND HARDEN

- Minimal changes.
- Benefits.
- Costs.
- Risks.
- Expected lifetime.
- Situations where this is the correct choice.

OPTION B — INCREMENTAL REDESIGN

- Structural improvement without replacing the entire subsystem.
- Benefits.
- Costs.
- Migration steps.
- Compatibility considerations.
- Testing requirements.
- Rollback strategy.

OPTION C — ALTERNATIVE APPROACH

- A meaningfully different implementation or design.
- Benefits.
- Costs.
- New risks.
- Operational consequences.
- Team-skill implications.
- Dependency implications.
- Migration complexity.

OPTION D — CLEAN-SLATE IDEAL, WHEN USEFUL

- What would be designed differently without legacy constraints?
- Which parts are worth approximating incrementally?
- Which parts are not worth pursuing?
- Why a full rewrite is or is not justified.

RECOMMENDATION

- Select the preferred option.
- Explain why it is preferred.
- State confidence.
- State prerequisites.
- State what evidence could change the recommendation.
- State what should remain untouched.

Do not force an alternative when the existing approach is already appropriate.
“Keep as is” is a valid recommendation when supported by evidence.

===============================================================================
PHASE 18 — FEATURE ADDITION, IMPROVEMENT, CONSOLIDATION, AND REMOVAL
===============================================================================

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
PHASE 19 — DOCUMENTATION AND KNOWLEDGE QUALITY
===============================================================================

Review:

- README files.
- Setup documentation.
- Architecture documents.
- API documentation.
- User documentation.
- Operational runbooks.
- Migration instructions.
- Security documentation.
- Code comments.
- Examples.
- Tutorials.
- Troubleshooting documentation.
- Error messages.
- Command help.
- Configuration references.

Look for:

- Incorrect documentation.
- Stale documentation.
- Contradictory documentation.
- Missing prerequisites.
- Missing failure guidance.
- Missing rollback guidance.
- Examples that no longer compile.
- Configuration keys missing from references.
- Public behavior documented only in tests.
- Critical invariants documented nowhere.
- Comments that describe historical rather than current behavior.
- Architecture diagrams that no longer match implementation.
- Features implemented but undiscoverable.
- Removed features still documented.
- Security-sensitive setup explained unsafely.
- Operational recovery requiring undocumented knowledge.

Recommend documentation changes by audience:

- End users.
- API consumers.
- Developers.
- Operators.
- Security reviewers.
- Support staff.
- Future maintainers.

===============================================================================
PHASE 20 — LANGUAGE- AND FRAMEWORK-SPECIFIC REVIEW
===============================================================================

Identify the languages and frameworks in use and perform applicable
ecosystem-specific checks.

Examples include, but are not limited to:

JAVASCRIPT OR TYPESCRIPT

- Unsafe any usage.
- Incorrect type assertions.
- Missing strictness.
- Promise handling.
- Event-listener leaks.
- Module-system inconsistencies.
- Runtime/schema validation gaps.
- Prototype pollution.
- Client/server boundary leakage.
- React effect and dependency defects.
- Stale closures.
- Hydration mismatches.
- Server-side rendering data exposure.
- Bundle and tree-shaking issues.

PYTHON

- Mutable default arguments.
- Incorrect exception scopes.
- Async blocking.
- Context-manager omissions.
- Type-hint gaps at boundaries.
- Import-time side effects.
- Circular imports.
- Unsafe pickle or YAML behavior.
- Multiprocessing assumptions.
- ORM transaction behavior.
- Dependency injection or global configuration issues.

GO

- Goroutine leaks.
- Context propagation.
- Error wrapping.
- Interface overuse.
- Nil interface behavior.
- Data races.
- Channel ownership.
- Defer behavior in loops.
- HTTP body closure.
- Timer and ticker leaks.
- Slice aliasing.
- Unbounded concurrency.

RUST

- Unsafe code.
- Panic behavior.
- Poisoned locks.
- Excessive cloning.
- Interior mutability.
- Lifetime workarounds masking design issues.
- Blocking within async runtimes.
- Send and Sync assumptions.
- Error-type quality.
- Serialization compatibility.

JAVA OR KOTLIN

- Nullability boundaries.
- Transaction proxy behavior.
- Thread-pool misuse.
- Blocking async execution.
- Resource closure.
- Equality and hash contracts.
- ORM lazy loading.
- Entity leakage.
- Exception translation.
- Framework annotation behavior.
- Serialization compatibility.

C# OR .NET

- Async-over-sync.
- Missing cancellation tokens.
- Disposable ownership.
- LINQ materialization.
- Entity Framework query shape.
- Nullable-reference handling.
- Dependency-injection lifetimes.
- Synchronization-context assumptions.
- Serialization behavior.

C OR C++

- Memory safety.
- Ownership.
- Undefined behavior.
- Integer overflow.
- Bounds checks.
- Lifetime.
- Concurrency.
- Exception safety.
- ABI compatibility.
- Resource acquisition and release.
- Unsafe format strings.
- Compiler-warning configuration.

SQL

- Injection.
- Null semantics.
- Query plans.
- Index use.
- Locking.
- Transaction isolation.
- Non-deterministic ordering.
- Incorrect joins.
- Duplicate amplification.
- Migration safety.

MOBILE

- Secure storage.
- Offline state.
- Background execution.
- Deep links.
- Permission handling.
- Lifecycle behavior.
- Network resilience.
- Upgrade and migration behavior.
- Accessibility.
- Battery impact.

Adapt this phase to the actual technology stack. Do not apply irrelevant
language checklists mechanically.

===============================================================================
PHASE 21 — VALIDATION AND REPRODUCTION
===============================================================================

Use the narrowest useful checks while investigating.

Where available and safe, run applicable:

- Format checks.
- Lint checks.
- Type checks.
- Unit tests.
- Integration tests.
- Contract tests.
- End-to-end tests.
- Security scanners.
- Dependency audits.
- Migration validation.
- Schema validation.
- Build commands.
- Packaging commands.
- Documentation builds.
- Static analysis.
- Benchmarks.
- Targeted reproductions.

For every finding, attempt one or more of:

- Static proof.
- Existing failing test.
- New test concept.
- Minimal input.
- Reproduction command.
- Call-path demonstration.
- Schema contradiction.
- Configuration contradiction.
- Concurrency timeline.
- Query-plan evidence.
- Profiling evidence.

Do not:

- Run destructive tests against real data.
- Use production credentials.
- Contact external systems without authorization.
- Perform load testing against shared or production environments.
- Install broad tooling without approval.
- Treat scanner output as confirmed without manual verification.

Record:

- Commands run.
- Results.
- Failures.
- Environmental limitations.
- Checks not run and why.
- Whether generated or modified files appeared.

===============================================================================
PHASE 22 — PRIORITIZATION AND ROADMAP
===============================================================================

Prioritize findings using evidence, not arbitrary scoring.

For defects, consider:

- Severity.
- Likelihood.
- Reach.
- Exploitability.
- Data impact.
- User impact.
- Operational impact.
- Detectability.
- Recoverability.
- Confidence.
- Fix complexity.
- Compatibility risk.

Use these severity levels:

CRITICAL

- Immediate risk of major security compromise, irreversible data loss,
  substantial cross-tenant exposure, widespread outage, or similarly severe
  consequences.
- Should block release or trigger immediate remediation.

HIGH

- Serious correctness, security, data-integrity, reliability, or operational
  risk.
- Likely to affect important workflows or create substantial damage.
- Should be prioritized urgently.

MEDIUM

- Material defect or design problem with bounded impact.
- Should be scheduled, but does not normally require emergency action.

LOW

- Limited-impact issue, maintainability problem, narrow edge case, or
  defense-in-depth opportunity.

INFORMATIONAL

- Observation, positive pattern, optional optimization, or recommendation
  without a current defect.

For feature and improvement recommendations, consider:

- Strength of evidence.
- User or operator value.
- Risk reduction.
- Workflow reach.
- Strategic fit inferable from the repository.
- Complexity removed.
- Maintenance burden reduced.
- Delivery effort.
- Migration risk.
- Ongoing operating cost.
- Reversibility.
- Dependencies.

Do not fabricate numeric RICE, ROI, adoption, revenue, or effort values.

Use qualitative priority groups:

NOW

- Critical or high-severity issues.
- Low-risk fixes with immediate material value.
- Required foundations for other work.

NEXT

- Important structural improvements.
- High-value workflow improvements.
- Strongly supported feature additions.
- Planned deprecations requiring preparation.

LATER

- Valuable but non-urgent improvements.
- Scale-dependent optimization.
- Larger redesigns requiring evidence or sequencing.

INVESTIGATE

- Plausible opportunities lacking usage, product, performance, or operational
  evidence.
- Include the exact evidence-gathering plan.

DO NOT PURSUE

- Recommendations whose cost, risk, or complexity outweigh likely value.
- Attractive but unnecessary rewrites.
- Premature scaling work.
- Features unsupported by repository evidence.

===============================================================================
REQUIRED FINDING FORMAT
===============================================================================

Assign every finding a stable identifier, such as:

- COR-001 for correctness.
- SEC-001 for security.
- DAT-001 for data.
- ARC-001 for architecture.
- REL-001 for reliability.
- PER-001 for performance.
- API-001 for contracts.
- TST-001 for testing.
- OPS-001 for operations.
- MNT-001 for maintainability.
- UX-001 for UX.
- FEAT-001 for feature recommendations.
- REM-001 for removal or deprecation candidates.
- ALT-001 for alternative implementation recommendations.
- DOC-001 for documentation.
- DX-001 for developer experience.

Use this template:

## [ID] Finding title

Classification:
[Confirmed defect / Probable defect / Risk / Improvement / Feature opportunity /
Feature-removal candidate / Alternative design / Positive pattern]

Severity or priority:
[Critical / High / Medium / Low / Informational]
or
[Now / Next / Later / Investigate / Do not pursue]

Confidence:
[Confirmed / High / Medium / Low / Hypothesis]

Affected components:
[Components, packages, services, workflows, users, or operators]

Evidence:
- `path/to/file.ext:line-line` — explanation.
- `path/to/other.ext:line-line` — explanation.
- Relevant command, test, schema, or call path.

Current behavior:
[What the system does now]

Expected or preferred behavior:
[What it should do and why]

Trigger or scenario:
[Exact conditions]

Impact:
[User, data, security, reliability, performance, maintenance, or operational
impact]

Reach:
[Which users, tenants, records, requests, environments, or workflows are
affected]

Root cause:
[Underlying cause, not merely the visible symptom]

Why existing tests did not catch it:
[When applicable]

Minimal reproduction:
[Input, timeline, command, test concept, or call sequence]

Recommended action:
[Specific, minimally disruptive recommendation]

Alternative approaches:
1. [Option and tradeoffs]
2. [Option and tradeoffs]
3. [Keep current behavior, when applicable]

Preferred option:
[Selection and reasoning]

Implementation outline:
[Main code, schema, configuration, migration, and documentation touchpoints]

Compatibility and migration:
[Public API, persisted data, deployment, or external-consumer considerations]

Validation:
[Tests or checks needed]

Effort:
[Small / Medium / Large / Program-level]

Risk of the proposed change:
[Low / Medium / High, with explanation]

Dependencies:
[Prerequisite work]

Open questions:
[Only questions materially affecting the conclusion]

===============================================================================
REQUIRED FEATURE-RECOMMENDATION FORMAT
===============================================================================

Use this template for feature additions, improvements, consolidations, or
removals:

## [FEAT-XXX or REM-XXX] Feature recommendation

Decision:
[Add / Improve / Simplify / Merge / Replace / Deprecate / Remove / Keep /
Experiment / Investigate]

Priority:
[Now / Next / Later / Investigate / Do not pursue]

Confidence:
[Confirmed / High / Medium / Low / Requires product validation]

Feature or capability:
[Name]

Target actor:
[User, administrator, operator, developer, integration consumer, or support]

Problem or opportunity:
[What is missing, unnecessarily difficult, redundant, or harmful]

Repository evidence:
[Routes, UI, models, tests, support tools, repeated workarounds, flags,
documentation, or operational behavior]

Current workaround:
[How the problem is handled now]

Proposed behavior:
[Precise behavior]

Why this is better:
[User value, risk reduction, simplification, cost reduction, or maintainability]

Minimal viable scope:
[Smallest coherent implementation]

Non-goals:
[What should deliberately remain out of scope]

Alternatives considered:
1. [Alternative]
2. [Alternative]
3. [Do nothing]

Compatibility impact:
[APIs, persisted data, integrations, UI, configuration, or user behavior]

Implementation touchpoints:
[Components likely affected]

Security and privacy:
[Implications]

Operational impact:
[Deployment, monitoring, support, maintenance, and recovery]

Test strategy:
[Required levels]

Rollout or deprecation plan:
[Stages, flags, migration, warning period, and rollback]

Success indicators:
[Observable indicators without inventing unsupported values]

Reconsideration or removal criteria:
[Conditions that should stop or reverse the change]

Effort:
[Small / Medium / Large / Program-level]

Risks:
[Main risks]

===============================================================================
FINAL REPORT FORMAT
===============================================================================

Produce the final report in this exact high-level order.

# 1. Executive Summary

Include:

- Overall codebase health.
- Most serious risks.
- Most important architectural concern.
- Most valuable simplification.
- Most valuable alternative implementation.
- Most valuable feature addition.
- Strongest feature-removal or consolidation candidate.
- Most important positive pattern to preserve.
- Immediate recommended actions.
- Main review limitations.

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

# 3. Coverage Ledger

Provide a table with:

- Area.
- Review depth.
- Main contents.
- Main risks.
- Reason for reduced coverage, if applicable.

# 4. Architecture and Data-Flow Map

Describe:

- Component relationships.
- Data ownership.
- Trust boundaries.
- Critical request paths.
- Async workflows.
- Persistence.
- External dependencies.
- Operational control points.

Use diagrams in Mermaid or text when useful.

# 5. Top Findings

Provide a concise ranked table with:

- ID.
- Title.
- Classification.
- Severity or priority.
- Confidence.
- Affected area.
- Recommended action.
- Effort.

# 6. Detailed Findings

Present all confirmed and material findings using the required finding format.

Order by:

1. Critical.
2. High.
3. Medium.
4. Low.
5. Informational.

Within each severity, group by root cause or subsystem.

# 7. Better and Different Ways to Implement the System

For each major subsystem:

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

# 8. Feature Portfolio Recommendations

Use separate subsections:

## 8.1 Add

## 8.2 Improve

## 8.3 Simplify

## 8.4 Merge

## 8.5 Replace

## 8.6 Deprecate

## 8.7 Remove

## 8.8 Keep

## 8.9 Experiment or Investigate

Do not include generic feature brainstorming. Every recommendation must be tied
to evidence or explicitly labeled as requiring product validation.

# 9. Testing and Validation Gaps

Include:

- Critical workflows lacking tests.
- Incorrect or brittle tests.
- Missing failure-path tests.
- Missing security tests.
- Missing concurrency tests.
- Missing migration tests.
- Missing contract tests.
- Recommended test additions by priority.

# 10. Security and Privacy Summary

Include:

- Threat model.
- Confirmed vulnerabilities.
- Defense-in-depth gaps.
- Sensitive-data risks.
- Authorization risks.
- Abuse-resistance gaps.
- Required immediate mitigations.

# 11. Performance, Reliability, and Operations Summary

Include:

- Confirmed bottlenecks.
- Scale-dependent risks.
- Reliability gaps.
- Recovery gaps.
- Observability gaps.
- Operational features that should be added.
- Optimizations that should not yet be pursued.

# 12. Dependency, Build, Deployment, and Supply-Chain Summary

Include:

- Material dependency risks.
- Build reproducibility.
- CI/CD risks.
- Container risks.
- Deployment and rollback risks.
- Licensing concerns.
- Recommended changes.

# 13. Documentation and Developer-Experience Summary

Include:

- Stale or missing documentation.
- Onboarding problems.
- Local-development friction.
- Debugging limitations.
- Tooling improvements.
- Important invariants requiring documentation.

# 14. Prioritized Roadmap

Organize into:

## Now

## Next

## Later

## Investigate

## Do Not Pursue

For each roadmap item, include:

- Finding or recommendation IDs.
- Goal.
- Dependencies.
- Expected value.
- Effort.
- Risk.
- Completion or validation criteria.

# 15. Suggested Implementation Sequence

Explain the dependency-aware order of work.

Account for:

- Security fixes.
- Data migrations.
- Compatibility.
- Observability needed before risky changes.
- Test foundations.
- Feature deprecation.
- Rollback capability.
- Operational readiness.

# 16. Validation Performed

List:

- Commands.
- Results.
- Failures.
- Environmental limitations.
- Areas not validated.
- Any temporary artifacts created.

# 17. Open Questions and Missing Evidence

Include only questions that materially affect conclusions.

For each question, explain:

- Why it matters.
- Current assumption.
- Evidence required.
- How the recommendation changes depending on the answer.

# 18. Positive Patterns Worth Preserving

Identify:

- Strong designs.
- Good security controls.
- Useful test patterns.
- Clear abstractions.
- Effective operational practices.
- Good user workflows.
- Components that should serve as patterns elsewhere.

===============================================================================
QUALITY BAR
===============================================================================

The review is not complete unless it:

- Covers every meaningful first-party repository area.
- Identifies critical cross-component behavior.
- Traces important workflows end to end.
- Examines success and failure paths.
- Reviews security, privacy, data integrity, concurrency, performance,
  reliability, APIs, tests, dependencies, deployment, and operations.
- Suggests better or different implementations where materially beneficial.
- Identifies features to add, improve, simplify, merge, replace, deprecate,
  remove, keep, or investigate.
- Explains tradeoffs rather than presenting preferences as facts.
- Provides realistic migration paths.
- Protects compatibility contracts.
- Includes concrete repository evidence.
- Distinguishes confirmed findings from hypotheses.
- Avoids generic recommendations.
- Avoids unsupported product assumptions.
- Avoids speculative rewrites.
- Records validation performed.
- Identifies positive patterns worth preserving.
- Produces a dependency-aware, prioritized roadmap.

===============================================================================
ANTI-PATTERNS TO AVOID IN THE REVIEW
===============================================================================

Do not:

- Produce a generic checklist with no repository-specific conclusions.
- Report formatting preferences as major findings.
- Recommend “add more tests” without naming exact missing behavior.
- Recommend “improve error handling” without identifying concrete failure paths.
- Recommend caching without identifying repeated expensive work and invalidation
  requirements.
- Recommend microservices without a concrete scaling, ownership, deployment, or
  isolation need.
- Recommend combining services without analyzing deployment and ownership
  consequences.
- Recommend a rewrite because the code is imperfect.
- Recommend a new framework solely because it is newer.
- Recommend a dependency solely because it is popular.
- Claim a feature is unused without evidence.
- Recommend feature removal without consumer and migration analysis.
- Recommend feature additions based on a generic SaaS checklist.
- Invent users, metrics, business priorities, or revenue impact.
- Hide uncertainty.
- Duplicate findings.
- Ignore existing user changes.
- Change unrelated code.
- Weaken tests.
- Expose secrets.
- Run destructive commands.
- Treat scanner output as automatically correct.
- Confuse generated code problems with their source-definition problems.
- Suggest broad abstractions with no demonstrated consumers.
- Preserve unnecessary complexity solely because it is established.
- Replace working code without demonstrating material benefit.

===============================================================================
FINAL INSTRUCTION
===============================================================================

Begin by reading repository instructions and establishing the worktree and
validation baseline.

Then build the coverage ledger, system map, domain model, and feature inventory
before drawing broad conclusions.

Review the codebase deeply enough to explain how important behavior works across
components.

For every material problem, explain:

- What is happening.
- Why it matters.
- Where the evidence is.
- What the root cause is.
- What the smallest effective fix is.
- What alternative approaches exist.
- Which approach you recommend.
- What migration and compatibility work is required.
- How the result should be validated.

For the product and feature portfolio, explicitly determine what should be:

- Added.
- Improved.
- Simplified.
- Merged.
- Replaced.
- Deprecated.
- Removed.
- Preserved.
- Tested as an experiment.
- Investigated before deciding.

The final report must be specific enough that another engineering team could
turn it into a technically sound, prioritized implementation plan without
having to rediscover the repository architecture or the reasoning behind the
recommendations.