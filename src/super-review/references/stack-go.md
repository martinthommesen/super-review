# Go deep checks

Review applicable first-party Go behavior for:

- Goroutine leaks, context propagation, cancellation, deadline ownership, unbounded concurrency, and shutdown coordination.
- Channel ownership, close/send races, nil channels or interfaces, select behavior, lost errors, and synchronization discipline.
- Error wrapping, sentinel and typed-error matching, partial results, deferred cleanup, and `defer` behavior in loops.
- HTTP body closure and draining, timer and ticker lifecycle, connection reuse, resource limits, and retry safety.
- Slice aliasing, map concurrency, zero values, copying locks, pointer lifetimes, loop-variable capture, and data races.
- Interface overuse, implicit implementation drift, serialization compatibility, build tags, platform behavior, and module boundaries.

Use the race detector or other executable checks only after the command-safety gate. Establish ownership and lifecycle rather than flagging concurrency primitives by presence alone.
