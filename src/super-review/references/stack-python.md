# Python Deep Checks

Review applicable first-party Python and framework behavior for:

- Mutable default arguments, shared class state, descriptor behavior, late binding, iterator consumption, and truthiness or sentinel mistakes.
- Exception scope, exception chaining, broad catches, cancellation handling, cleanup, context-manager omissions, and errors hidden by `finally` or fallback paths.
- Blocking work in async code, task lifecycle, event-loop ownership, thread/process boundaries, multiprocessing start-method assumptions, and resource leaks.
- Type-hint gaps at trust boundaries, unsafe casts, runtime/schema validation, dataclass/model defaults, and serialization compatibility.
- Import-time side effects, circular imports, global configuration, dependency-injection lifetimes, plugin discovery, and module shadowing.
- Unsafe pickle, YAML, archive, template, subprocess, path, and dynamic import behavior.
- ORM session and transaction scope, lazy loading, query shape, migration semantics, connection lifecycle, and test/production database differences.

Use configured Python versions, type checkers, linters, package metadata, and framework semantics as evidence. Do not assume a framework default without verifying configuration and version.
