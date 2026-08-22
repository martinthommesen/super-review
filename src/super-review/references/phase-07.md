# Phase 7: data models, databases, migrations, and integrity

Review:

- Data models.
- Database schemas.
- Constraints.
- Indexes.
- Foreign keys.
- Unique constraints.
- Nullability.
- Defaults.
- Triggers.
- Views.
- Stored procedures.
- Transactions.
- Isolation levels.
- Query construction.
- Object-relational mapping.
- Migration tooling.
- Seed data.
- Backup assumptions.
- Restore assumptions.
- Archival.
- Retention.
- Deletion.
- Replication.
- Read replicas.
- Cache consistency.

Look for:

- Missing constraints.
- Invariants enforced only in application code.
- Incorrect nullability.
- Unsafe defaults.
- Orphaned records.
- Broken cascade behavior.
- Accidental data loss.
- Partial writes.
- Lost updates.
- Write skew.
- Duplicate creation.
- Race-prone "check then insert."
- Incorrect transaction scope.
- Long-running transactions.
- Queries inside loops.
- Missing indexes.
- Redundant indexes.
- Indexes with poor column order.
- Queries that cannot use indexes.
- Full-table scans.
- Unbounded result sets.
- Incorrect pagination.
- N+1 queries.
- Lock contention.
- Deadlocks.
- Hot rows.
- Hot partitions.
- Timestamp misuse.
- Soft-delete inconsistencies.
- Uniqueness that ignores soft-deleted state incorrectly.
- Migrations that lock large tables.
- Non-transactional migration risks.
- Forward-only migrations without recovery.
- Application and migration deployment-order coupling.
- Backfills without checkpointing.
- Backfills without idempotency.
- Schema changes incompatible with rolling deployments.
- Reads and writes assuming different schema versions.
- Legacy data that violates new assumptions.
- Failed-migration recovery gaps.
- Missing reconciliation tools.
- Missing data-integrity checks.
- Retention behavior inconsistent with product claims.
- Data deletion that leaves derived copies behind.

For every risky migration, evaluate:

1. Forward compatibility.
2. Backward compatibility.
3. Rolling-deployment safety.
4. Locking behavior.
5. Data-volume assumptions.
6. Backfill strategy.
7. Retry safety.
8. Rollback strategy.
9. Validation strategy.
10. Operational observability.
