# Template C — Feature decision

Use this for add, improve, simplify, merge, replace, deprecate, remove, keep, experiment, or investigate decisions. Every decision must be tied to repository evidence or explicitly labeled as requiring product validation.

```markdown
## [FEAT-001] Feature decision title

Record type: Feature decision
ID category: <FEAT | REM>
Primary component: <stable product capability or workflow>
Identity statement: <stable problem, opportunity, overlap, obsolescence basis, or preserved value>
Fingerprint: sha256:<digest>
Status: Active

Decision: <Add | Improve | Simplify | Merge | Replace | Deprecate | Remove | Keep | Experiment | Investigate>
Priority: <Now | Next | Later | Investigate | Do not pursue>
Confidence: <Confirmed | High | Medium | Low | Requires product validation>
Feature or capability: <name>
Target actor: <user, administrator, operator, developer, integration consumer, support, or other actor>

Problem or opportunity:
<What is missing, unnecessarily difficult, redundant, risky, harmful, or worth preserving.>

Repository evidence:
<Routes, UI, models, schemas, tests, support tools, repeated workarounds, flags, documentation, operations, permissions, or reachable entry points.>

Current workaround:
<How the need is handled now, or Not applicable with reason.>

Consequence of doing nothing:
<Current risk, friction, maintenance burden, or lost capability without fabricated metrics.>

Proposed behavior:
<Precise behavior or preservation decision.>

Why this is better:
<User value, risk reduction, simplification, cost direction, maintainability, or preservation value supported by evidence.>

Minimal viable scope:
<Smallest coherent scope.>

Non-goals:
<What remains deliberately out of scope.>

User or operator workflow:
<Steps, states, errors, recovery, permissions, and visibility.>

Required permissions:
<Authorization and tenant boundaries.>

Data-model changes:
<Schema, retention, migration, ownership, or Not applicable with reason.>

API changes:
<Contracts, versioning, compatibility, or Not applicable with reason.>

UI changes:
<Interfaces, accessibility, localization, or Not applicable with reason.>

Background-processing changes:
<Jobs, events, retries, idempotency, reconciliation, or Not applicable with reason.>

Security implications:
<Threats and controls.>

Privacy implications:
<Data minimization, retention, deletion, export, consent, or Not applicable with reason.>

Operational impact:
<Deployment, observability, support, recovery, maintenance, and cost direction.>

Compatibility impact:
<Public APIs, persisted data, integrations, configuration, UI behavior, rollout, and coexistence.>

Known consumers:
<Known internal, public, generated, operational, or external consumers.>

Possible hidden or external consumers:
<Risk and evidence-gathering plan.>

Usage evidence available:
<Reachability, telemetry, tests, docs, support paths, or other evidence.>

Usage evidence missing:
<What cannot be established and how to establish it.>

Maintenance burden:
<Implementation, operational, support, and security burden.>

Overlap with other features:
<Shared purpose, behavioral differences, drift, and proposed unification.>

Alternatives considered:
1. <Alternative and tradeoffs.>
2. <Alternative and tradeoffs.>
3. <Do nothing or keep current behavior and tradeoffs.>

Dependencies:
<Prerequisite records, telemetry, migration, design, ownership, or external coordination.>

Implementation touchpoints:
<Components, schemas, APIs, UI, jobs, permissions, docs, generators, deployment, and operations.>

Test strategy:
<Unit, integration, contract, end-to-end, property, fuzz, concurrency, load, migration, security, accessibility, or operational tests as applicable.>

Migration strategy:
<Data, API, configuration, user, consumer, and operational migration.>

Rollout or deprecation plan:
<Stages, flags, warning period, compatibility window, communication, observability, and ownership.>

Rollback strategy:
<Safe reversal and data implications.>

Data-retention implications:
<Retention, archival, deletion, derived copies, and export implications.>

Success indicators:
<Observable qualitative or repository-supported indicators without fabricated targets.>

Reconsideration or removal criteria:
<Conditions that stop, reverse, or retire the change.>

Final deletion criteria:
<For deprecation/removal, exact consumer, telemetry, migration, retention, and rollback gates; otherwise Not applicable with reason.>

Effort:
<Small | Medium | Large | Program-level.>

Risks:
<Main delivery, compatibility, security, operational, product, and maintenance risks.>
```

Append the decision-specific block below that matches `Decision`. Do not append unrelated blocks merely to increase volume.

## Improve or simplify block

```markdown
Current workflow:
<Current steps and behavior.>

Friction or risk:
<Specific friction, inconsistency, unsafe default, support burden, or failure-recovery weakness.>

Behavior preserved:
<Behavior and contracts that remain unchanged.>

Behavior changed:
<Precise change.>

Potential downside:
<Tradeoffs and regressions to guard against.>

Validation required:
<Exact evidence and tests needed.>
```

## Merge block

```markdown
Features involved:
<Capabilities being merged.>

Shared purpose:
<Common user or system purpose.>

Meaningful differences:
<Differences that are real rather than historical drift.>

Differences retained as modes or options:
<Which differences remain and why.>

Proposed unified model:
<Unified concepts, state, routes, permissions, APIs, and UI.>

Documentation migration:
<Documentation, help, examples, and terminology changes.>

Deprecation sequence:
<Safe sequence for old paths.>
```

## Replace block

```markdown
Existing feature:
<Feature being replaced.>

Replacement behavior:
<Replacement behavior.>

Why improvement alone is insufficient:
<Evidence that bounded improvement cannot solve the problem.>

Compatibility period:
<Coexistence and support window.>

Data conversion:
<Conversion, validation, retry, and rollback.>

User communication requirements:
<Required communication and support.>
```

## Deprecate or remove block

```markdown
Concrete removal evidence:
<Reachability, consumer, flag, telemetry, documentation, test, and operational evidence.>

Security or reliability risk:
<Risk of retaining the capability.>

Consequence of removal:
<User, consumer, data, operational, and compatibility impact.>

Required telemetry or validation before removal:
<Exact evidence gates.>

Compatibility window:
<Warning and support period.>

Deprecation notice strategy:
<Channels, owner, timing, and migration guidance.>
```

## Keep block

```markdown
Preservation rationale:
<Why the capability is valuable and the current design is appropriate.>

Invariants to preserve:
<Behavior future changes must retain.>

Tests that protect it:
<Existing tests and missing protections.>

Future-refactor constraints:
<What must not be accidentally removed or weakened.>
```

## Experiment block

```markdown
Experiment hypothesis:
<Testable hypothesis.>

Minimal experiment:
<Smallest isolated experiment.>

Expected signal:
<Observable signal without invented targets.>

Guardrail indicators:
<Safety, privacy, reliability, or workflow guardrails.>

Failure or stop conditions:
<When to stop.>

Data required:
<Minimum data and retention.>

Experimental-code isolation:
<How production paths remain safe and cleanup stays bounded.>

Feature-flag owner:
<Named role or owner.>

Expiration or review date:
<Concrete date or evidence-based review trigger.>

Cleanup plan:
<Removal or promotion plan.>
```

## Investigate block

```markdown
Evidence-gathering plan:
<Instrumentation, interviews, telemetry, static proof, tests, benchmarks, or operational evidence needed.>

Decision threshold:
<What evidence would support add, improve, keep, deprecate, remove, or do not pursue.>
```

When usage cannot be established, use `Investigate` and specify instrumentation or evidence collection rather than recommending immediate removal.
