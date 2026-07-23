# PHASE 10 — PERFORMANCE, SCALABILITY, AND COST

Review hot paths and likely scaling boundaries.

Look for:

- Poor asymptotic complexity.
- Repeated work.
- Duplicate serialization.
- Excessive allocations.
- Large object retention.
- Unnecessary copying.
- N+1 queries.
- Chatty network calls.
- Sequential independent operations.
- Unbounded concurrency.
- Missing batching.
- Inefficient batching.
- Large payloads.
- Excessive polling.
- Busy waiting.
- Expensive regex use.
- Blocking I/O.
- CPU-heavy work on request threads.
- Compression misuse.
- Cache misses caused by key design.
- Cache stampedes.
- Caches without bounds.
- Caches without invalidation.
- Caches storing sensitive cross-tenant data.
- Inefficient pagination.
- Unbounded exports.
- Missing streaming.
- Full in-memory processing.
- Inefficient database indexes.
- Large-table migrations.
- Inefficient frontend rendering.
- Excessive frontend bundle size.
- Repeated client requests.
- Missing lazy loading.
- Excessive logging.
- High-cardinality metrics.
- Excessive cloud API calls.
- Inefficient storage-tier usage.
- Idle infrastructure.
- Overprovisioning.
- Excessive cross-region traffic.
- Unnecessary managed-service complexity.

Distinguish:

- Confirmed bottlenecks.
- Likely bottlenecks.
- Scale-dependent concerns.
- Premature optimization opportunities that should not be pursued.

Do not claim performance improvement without explaining:

1. Current cost.
2. Triggering scale.
3. Proposed improvement.
4. Tradeoffs.
5. Measurement method.
6. Expected direction of impact.
7. Risk of regression.

Recommend profiling or benchmarking when repository evidence alone is
insufficient.

===============================================================================
