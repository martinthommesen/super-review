# Rust deep checks

Review applicable first-party Rust behavior for:

- `unsafe` blocks and contracts, FFI boundaries, aliasing, lifetime assumptions, pinning, and soundness of custom abstractions.
- Panic behavior, unwinding versus abort configuration, poisoned locks, error propagation, and cleanup under early return or cancellation.
- Blocking work inside async runtimes, task cancellation, detached tasks, executor assumptions, lock use across await points, and resource ownership.
- `Send` and `Sync` assumptions, interior mutability, atomic ordering, concurrency invariants, and shared-state design.
- Excessive cloning, allocation or copying, borrow-workarounds that mask design problems, and hidden performance costs.
- Error-type quality, exhaustive enum handling, feature flags, conditional compilation, serialization compatibility, and versioned persisted/public formats.

Treat compiler acceptance as necessary but not sufficient; verify semantic invariants, external contracts, and unsafe assumptions with current evidence.
