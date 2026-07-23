# PHASE 16 — MAINTAINABILITY, CODE QUALITY, AND DEVELOPER EXPERIENCE

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
