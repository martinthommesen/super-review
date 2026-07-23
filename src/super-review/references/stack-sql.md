# SQL and Query-System Deep Checks

Review applicable handwritten SQL, query builders, ORM-generated query behavior, stored logic, analytics queries, and migration SQL for:

- Injection, parameterization, identifier construction, dynamic SQL, privilege boundaries, and sensitive result exposure.
- Null and three-valued logic, implicit casts, collation, timezone/date semantics, precision, rounding, and non-deterministic ordering.
- Join correctness, duplicate amplification, aggregation, grouping, filtering, pagination, cursor stability, and partial-result semantics.
- Query plans, index use, cardinality assumptions, full scans, lock behavior, isolation, deadlocks, hot rows/partitions, and N+1 patterns.
- Transaction boundaries, check-then-write races, idempotency, retry behavior, constraints, triggers, and consistency with application invariants.
- Migration safety, rolling compatibility, locking, backfills, validation, rollback/recovery, and legacy-data handling.

Use query-plan or runtime evidence when available and safe. Do not label a query slow from syntax alone.
