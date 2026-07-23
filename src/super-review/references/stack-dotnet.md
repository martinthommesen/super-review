# C# and .NET Deep Checks

Review applicable first-party C#, .NET, ASP.NET, and Entity Framework behavior for:

- Async-over-sync, unobserved tasks, missing cancellation tokens, synchronization-context assumptions, and thread-pool starvation.
- `IDisposable`/`IAsyncDisposable` ownership, stream and response lifetimes, pooled-resource handling, and cleanup on exceptions.
- Nullable-reference boundaries, null-forgiving operators, value/default semantics, equality, records, mutable exposure, and unsafe casts.
- LINQ deferred execution and repeated enumeration, materialization, query translation, client-side evaluation, Entity Framework query shape, tracking, and transaction scope.
- Dependency-injection lifetimes, captive dependencies, singleton state, hosted-service startup/shutdown, and configuration binding/validation.
- Serialization behavior, model binding, validation, authorization filters, exception middleware, versioning, and persisted/public contract compatibility.

Verify runtime and framework versions, compiler settings, analyzers, and deployment model before drawing conclusions.
