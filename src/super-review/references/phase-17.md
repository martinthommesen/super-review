# PHASE 17 — BETTER OR DIFFERENT WAYS TO IMPLEMENT THE SYSTEM

Strict anti-filler rule: perform the alternatives analysis for every major subsystem or workflow, but do not manufacture options. Any unsupported option or field must say `Not applicable — <specific evidence-based reason>` or `Not established — <missing evidence>`. A supported `Keep as is` conclusion remains fully valid.

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
