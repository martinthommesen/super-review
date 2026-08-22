# Phase 9: concurrency, asynchrony, and distributed systems

Review:

- Threads.
- Tasks.
- Coroutines.
- Goroutines.
- Processes.
- Locks.
- Transactions.
- Queues.
- Streams.
- Events.
- Schedulers.
- Background jobs.
- Distributed locks.
- Leader election.
- Caches.
- Retries.
- Timeouts.
- Cancellation.
- Shutdown behavior.

Look for:

- Data races.
- Lock-order inversions.
- Deadlocks.
- Livelocks.
- Starvation.
- Lost wakeups.
- Unsafe shared state.
- Blocking work on async executors.
- Async work not awaited.
- Detached tasks with lost errors.
- Unbounded task creation.
- Semaphore leaks.
- Connection leaks.
- File-handle leaks.
- Goroutine or thread leaks.
- Cancellation not propagated.
- Cancellation swallowed.
- Timeout values missing or inconsistent.
- Shutdown dropping work.
- Shutdown waiting forever.
- Duplicate job execution.
- Non-idempotent consumers.
- Missing deduplication.
- Out-of-order message corruption.
- Poison-message loops.
- Retry storms.
- Thundering-herd behavior.
- Distributed locks without fencing.
- Leases renewed incorrectly.
- Clock assumptions.
- Split-brain behavior.
- Events emitted before state is durable.
- Consumers reading state before replication catches up.
- At-least-once delivery treated as exactly once.
- Exactly-once claims unsupported by implementation.
- Missing backpressure.
- Unbounded queues.
- Memory growth under load.
- Fan-out amplification.
- Partial batch failure mishandling.
- Missing reconciliation after partial failure.

For every distributed workflow, state the actual delivery and consistency model:

- At most once.
- At least once.
- Effectively once through idempotency.
- Best effort.
- Strong consistency.
- Eventual consistency.
- Read-your-writes consistency.
- Unknown or inconsistent.
