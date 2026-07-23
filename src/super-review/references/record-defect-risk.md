# Template A — Defect or risk

Use this for confirmed defects, probable defects, security weaknesses, reliability risks, performance risks, architectural concerns that create current risk, data-integrity risks, testing defects, operational gaps, UX defects, documentation defects, and maintainability concerns.

```markdown
## [SEC-001] Finding title

Record type: Defect or risk
ID category: SEC
Primary component: <stable subsystem or workflow>
Identity statement: <underlying root cause, not the visible symptom>
Fingerprint: sha256:<digest>
Status: Active

Classification: <Confirmed defect | Probable defect | Security weakness | Reliability risk | Performance risk | Data-integrity risk | Architectural risk | Maintainability concern | Product or UX concern | Documentation issue | Testing gap | Operational gap>
Severity or priority: <Critical | High | Medium | Low | Informational>
Confidence: <Confirmed | High | Medium | Low | Hypothesis>
Affected components: <components, packages, services, workflows, users, operators, data, or environments>

Evidence:
- `path/to/file.ext:line-line` — current explanation.
- `path/to/other.ext:line-line` — current explanation.
- <relevant command, test, schema, configuration, call path, timeline, or contradiction>.

Current behavior:
<What the system currently does.>

Expected or preferred behavior:
<What it should do and why.>

Trigger or scenario:
<Exact conditions, input, state, ordering, actor, environment, or scale.>

Impact:
<User, data, security, privacy, reliability, performance, maintenance, compatibility, or operational impact.>

Reach:
<Which users, tenants, records, requests, deployments, or workflows are affected.>

Root cause:
<Underlying cause and why the evidence supports it.>

Why existing tests did not catch it:
<Specific coverage, assertion, fixture, environment, or test-design gap; or Not applicable with reason.>

Minimal reproduction:
<Smallest safe input, command, test concept, call sequence, state transition, concurrency timeline, query plan, or static proof.>

Recommended action:
<Specific, minimally disruptive correction.>

Alternative approaches:
1. <Option and tradeoffs.>
2. <Option and tradeoffs.>
3. <Keep current behavior, only when genuinely viable; otherwise Not applicable with reason.>

Preferred option:
<Selection, reasoning, confidence, prerequisites, and evidence that could change it.>

Implementation outline:
<Code, schema, configuration, migration, caller, consumer, fixture, documentation, generated artifact, deployment, and operational touchpoints.>

Compatibility and migration:
<Public API, persisted data, event, deployment, external consumer, deprecation, rollout, and rollback considerations.>

Validation:
<Regression-test level, static checks, reproductions, failure paths, migration checks, security checks, and operational verification.>

Effort:
<Small | Medium | Large | Program-level, with scope basis.>

Risk of the proposed change:
<Low | Medium | High, with explanation and rollback controls.>

Dependencies:
<Prerequisite work, evidence, migration, ownership, telemetry, or coordination.>

Open questions:
<Only questions materially affecting the conclusion, or Not applicable with reason.>
```

For every `SEC` record, also include these fields after `Root cause`:

```markdown
Threat scenario:
<Threat actor and abuse or exploit scenario.>

Attacker prerequisites:
<Required access, capability, timing, position, or knowledge.>

Affected assets:
<Data, identities, permissions, availability, integrity, confidentiality, or systems.>

Exploit path:
<Safe, remediation-oriented path description without unnecessary operational weaponization.>

Existing mitigations:
<Controls that currently reduce likelihood or impact.>

Missing mitigations:
<Controls required to close the issue.>

Defense-in-depth improvement:
<Additional bounded hardening beyond the primary fix.>

Disclosure sensitivity:
<How evidence and reproduction details must be handled.>
```
