# Java and Kotlin Deep Checks

Review applicable first-party JVM, Java, Kotlin, and framework behavior for:

- Nullability boundaries, platform types, optional-value semantics, default values, equality and hash contracts, and mutable collection exposure.
- Transaction proxy boundaries, self-invocation, annotation behavior, isolation, rollback rules, ORM lazy loading, entity leakage, and session lifetime.
- Thread-pool ownership, blocking within async/reactive execution, cancellation, context propagation, virtual-thread or coroutine assumptions, and shutdown.
- Resource closure, stream lifecycle, exception translation, swallowed interrupts, checked/unchecked error boundaries, and partial-success behavior.
- Serialization compatibility, reflection, deserialization safety, validation annotations, schema evolution, and generated-client drift.
- Dependency-injection scopes, initialization order, static/global state, class-loader behavior, build profiles, and environment-specific configuration.

Verify framework annotations and defaults against the actual framework version and configuration; do not infer behavior from annotation names alone.
