# Template B — Improvement or alternative

Use this when the current behavior is technically acceptable but a materially simpler, clearer, safer, faster, more scalable, more maintainable, or operationally stronger approach is supported by evidence. Do not label it as a defect.

```markdown
## [IMP-001] Improvement title

Record type: Improvement or alternative
ID category: <IMP | ALT>
Primary component: <stable subsystem or workflow>
Identity statement: <stable design limitation or alternative-decision basis>
Fingerprint: sha256:<digest>
Status: Active

Classification: <Improvement | Alternative implementation opportunity | Architectural alternative | Optional optimization | Workflow simplification>
Severity or priority: <Now | Next | Later | Investigate | Do not pursue>
Confidence: <Confirmed | High | Medium | Low | Hypothesis>
Affected components: <components, workflows, users, operators, or maintainers>

Evidence:
- <current implementation, repeated work, operational burden, workflow friction, scale boundary, or comparative evidence>.

Current approach:
<Describe the implementation or workflow.>

Why it appears to exist:
<Historical, product, framework, scale, compatibility, or ownership rationale supported by evidence.>

What it does well:
<Strengths and invariants worth preserving.>

Actual limitations:
<Material complexity, risk, cost, friction, or constraint.>

Essential versus accidental complexity:
<Which complexity is required and which is avoidable.>

Triggering context or scale:
<When the improvement becomes worthwhile; do not invent metrics.>

### Option A — Keep and harden

Minimal changes:
<Changes, or Not applicable with reason.>

Benefits:
<Benefits.>

Costs:
<Delivery and ongoing costs.>

Risks:
<Risks and regression exposure.>

Expected lifetime:
<How long this option remains appropriate.>

Correct-use conditions:
<When this is the preferred choice.>

### Option B — Incremental redesign

Structural change:
<Bounded redesign, or Not applicable with reason.>

Benefits:
<Benefits.>

Costs:
<Costs.>

Migration steps:
<Sequence.>

Compatibility considerations:
<Contracts and coexistence.>

Testing requirements:
<Validation.>

Rollback strategy:
<Rollback.>

### Option C — Alternative approach

Alternative design:
<Meaningfully different approach, or Not applicable with reason.>

Benefits:
<Benefits.>

Costs:
<Costs.>

New risks:
<New failure modes.>

Operational consequences:
<Deployment, support, observability, and recovery.>

Team-skill implications:
<Required expertise and ownership.>

Dependency implications:
<New, removed, or changed dependencies.>

Migration complexity:
<Complexity and compatibility.>

### Option D — Clean-slate ideal, when useful

Ideal design:
<What would differ without legacy constraints, or Not applicable with reason.>

Incrementally useful parts:
<Parts worth approximating.>

Parts not worth pursuing:
<Parts whose cost or risk exceeds value.>

Rewrite judgment:
<Why a full rewrite is or is not justified.>

Recommendation:
<Select the preferred option, explain why, state confidence and prerequisites, identify evidence that could change it, and state what must remain untouched.>

Expected benefit:
<Risk reduction, simplification, performance direction, workflow value, or maintenance value without fabricated numbers.>

Implementation outline:
<Code, schema, configuration, caller, consumer, test, migration, documentation, rollout, and operational touchpoints.>

Compatibility and migration:
<Contracts, coexistence, deprecation, rollout, rollback, and data implications.>

Validation:
<Measurement, tests, benchmarks, profiling, failure checks, and acceptance criteria.>

Effort:
<Small | Medium | Large | Program-level, optionally followed by " — <scope basis>">

Risk of the proposed change:
<Low | Medium | High, optionally followed by " — <explanation>">

Dependencies:
<Prerequisites.>

Open questions:
<Material questions, or Not applicable with reason.>
```

Options A–D are analytical lenses, not a quota for speculative prose. An option can be `Not applicable` only with a concrete evidence-based reason.
