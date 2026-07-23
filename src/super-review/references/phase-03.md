# PHASE 3 — ARCHITECTURE AND SYSTEM DESIGN

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
