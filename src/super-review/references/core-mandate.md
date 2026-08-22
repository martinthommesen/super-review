# Whole-repository review mandate

Perform an independent, evidence-based review of the entire repository. Cover
engineering, architecture, security, reliability, performance, data, tests,
product behavior, UX, developer experience, and long-term maintenance. This is
broader than a bug hunt or style review.

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

## Project context

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

A user-supplied safe-command list grants permission to consider those commands; it is not proof that repository-defined scripts, hooks, wrappers, or lifecycle behavior are safe. Apply the separate command-safety gate before execution.

Additional constraints:
[OPTIONAL CONSTRAINTS]

When context is absent, infer it from repository evidence. Clearly distinguish:

- Verified facts.
- Strongly supported inferences.
- Unverified hypotheses.
- Information that cannot be determined from the repository alone.

Do not invent product requirements, user behavior, usage metrics, business value,
or operational constraints.

## Review mode and change authorization

Review mode:
[CHOOSE ONE:
 REVIEW ONLY
 REVIEW AND PROPOSE PATCHES
 REVIEW AND IMPLEMENT APPROVED FIXES
 REVIEW AND IMPLEMENT ALL HIGH-CONFIDENCE FIXES]

Default to REVIEW ONLY when no mode is specified.

### Review only

In REVIEW ONLY mode, the mandatory canonical root `FINDINGS.md` is the sole permitted repository modification. The following prohibitions apply to every other repository path:

- Do not modify source code.
- Do not modify tests.
- Do not modify configuration.
- Do not modify schemas or migrations.
- Do not modify generated files.
- Do not modify documentation other than the mandatory canonical `FINDINGS.md`.
- Do not modify lockfiles.
- Do not create commits.
- Do not push branches.
- Do not publish packages.
- Do not deploy anything.
- Do not mutate persistent or production data.
- Do not trigger irreversible external actions.
- Do not install or upgrade dependencies without explicit authorization.
- Do not create unexplained files inside the repository.

You may run inspection and validation commands only after they pass the separate untrusted-repository command-safety gate. A command's name, documentation, or presence in project configuration is not sufficient proof of safety.

You may create temporary analysis artifacts outside the repository when needed,
but remove them afterward or report them clearly.

### Review and propose patches

In REVIEW AND PROPOSE PATCHES mode:

- Do not modify repository files other than the mandatory canonical `FINDINGS.md`.
- Include proposed diffs, pseudocode, schemas, interfaces, or migration steps
  for high-confidence findings where doing so materially improves clarity.
- Proposed patches must follow existing project conventions.
- Account for affected callers, consumers, tests, fixtures, schemas,
  configuration, documentation, deployment files, generated clients, and
  compatibility contracts.
- Do not propose broad rewrites where a focused change is sufficient.

### Review and implement approved fixes

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

### Review and implement all high-confidence fixes

In REVIEW AND IMPLEMENT ALL HIGH-CONFIDENCE FIXES mode:

- Implement only confirmed, high-confidence fixes with a clearly bounded scope.
- Do not automatically implement feature additions, removals, framework
  replacements, major refactors, database redesigns, public API changes, or
  architectural migrations.
- Present those larger changes as recommendations requiring approval.
- Avoid changes whose intended behavior cannot be established from available
  evidence.

In every mode, refresh the canonical `FINDINGS.md` from the post-validation, post-fix repository state. The detailed lifecycle, concurrency, and revalidation mechanics live only in `references/findings-lifecycle.md`.

## Primary review objectives

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
