# Phase applicability and deep-loading rules

Consider every phase from 0 through 22 in order. Conditional deep loading is an
evidence gate, not permission to reduce review coverage.

## Applicability procedure

For each phase:

1. Use the phase 0 through 2 inventory, manifests, entry points, schemas,
   configuration, tests, generated sources, deployment files, and repository
   instructions to identify relevant code and behavior.
2. If the phase is marked **always**, load its deep reference.
3. If marked **conditional**, load its deep reference whenever any trigger below exists or applicability is uncertain.
4. Close a conditional phase without its deep reference only after bounded
   searches establish that no applicable first-party code or behavior exists.
5. Record the searches, evidence, exclusions, and reason in the coverage ledger.
   Reopen the phase if later evidence shows that it applies.
6. Do not infer absence from filenames alone, missing documentation, one language, or a shallow directory listing.

## Phase matrix

| Phase | Loading rule | Evidence that requires deep loading | Minimum closure when it does not apply |
|---|---|---|---|
| 0 through 6 | Always | Universal baseline, inventory, domain, architecture, workflows, correctness, and security obligations. | Not closable as inapplicable. |
| 7 | Conditional | Database, ORM, schema, migration, structured file state, cache persistence, object storage metadata, durable queues, retention, backup, or deletion behavior. | Record searches for persistence APIs, schema/migration files, durable state, and data contracts. |
| 8 | Conditional | HTTP/RPC/GraphQL, CLI, library API, events, webhooks, file/config formats, protocol schemas, generated clients, or external adapters. Public exposure is not required; internal contracts count. | Record entry-point and contract searches and why no meaningful interface or integration exists. |
| 9 | Conditional | Threads, async tasks, processes, locks, transactions used for coordination, queues, schedulers, retries, background work, caches with concurrent mutation, or distributed components. | Record searches for concurrency primitives, async entry points, jobs, retries, queues, and shutdown behavior. |
| 10 | Conditional | Runtime hot paths, nontrivial data volume, network/database/storage use, user-facing latency, batch work, resource limits, cloud infrastructure, or cost-sensitive operations. | Record why the repository has no meaningful runtime, scale, resource, or operating-cost concerns. |
| 11 | Conditional | Long-running service, deployable application, worker, scheduled automation, external dependency, stateful operation, recovery requirement, alerting, backup, or operator workflow. | Record why reliability, recovery, observability, and operational controls are not applicable beyond universal failure-path checks. |
| 12 | Conditional | Web, desktop, mobile, terminal UI, interactive client, generated user interface, accessibility code, browser/client state, or user-facing navigation/forms. | Record searches for UI entry points, assets, client frameworks, interaction tests, and accessibility configuration. |
| 13 | Always | Every repository has a quality and validation strategy, including an evidenced absence of tests. | Not closable as inapplicable. |
| 14 | Conditional | Dependencies, compiler/build system, package manifest, lockfile, container, CI, code generation, packaging, release artifact, signing, or license obligations. | Record searches for manifests, workflows, generated artifacts, package boundaries, and release paths. |
| 15 | Conditional | Runtime configuration, environment variables, secrets, containers, orchestration, infrastructure-as-code, IAM, networking, storage, deployment, feature flags, or observability infrastructure. | Record searches for configuration and deployment surfaces and why none are first-party responsibilities. |
| 16 through 19 | Always | Maintainability, alternatives, feature portfolio, and knowledge quality apply to every maintained repository or directory. | Not closable as inapplicable. |
| 20 | Always dispatcher; conditional stack references | Load the dispatcher, then only references for languages, frameworks, query systems, and client platforms actually present. | Record detected stacks and why unselected stack references do not apply. |
| 21 through 22 | Always | Validation, reproduction, prioritization, and roadmap are required closure work. | Not closable as inapplicable. |

## Strict absence standard

"Not applicable" must name the inspected evidence and what is absent. Statements
such as "no frontend," "no database," or "small project" are insufficient. If
generated code, vendored code, examples, tests, or configuration imply hidden
behavior, trace its source or owner before closing the phase.
