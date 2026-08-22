# Phase 11: reliability, resilience, and operations

Review:

- Timeouts.
- Retries.
- Backoff.
- Jitter.
- Circuit breakers.
- Bulkheads.
- Health checks.
- Readiness checks.
- Liveness checks.
- Startup behavior.
- Shutdown behavior.
- Failover.
- Recovery.
- Reconciliation.
- Backups.
- Restore procedures.
- Disaster recovery.
- Deployment.
- Rollback.
- Observability.
- Alerting.
- Runbooks.
- Support tooling.

Look for:

- Calls without timeouts.
- Retries on permanent failures.
- Missing retry limits.
- Retry amplification.
- No jitter.
- Retry behavior that repeats non-idempotent work.
- Health checks that do not represent real readiness.
- Liveness checks that cause restart loops.
- Startup that depends on unavailable optional services.
- Shutdown that loses accepted work.
- Missing graceful degradation.
- Errors hidden behind generic success states.
- Missing dead-letter handling.
- Missing operator controls.
- Missing reprocessing tools.
- Missing reconciliation jobs.
- Missing visibility into stuck workflows.
- Logs lacking correlation identifiers.
- Metrics lacking actionable dimensions.
- Metrics with excessive cardinality.
- Alerts without clear operational response.
- Missing audit trails.
- Backup assumptions not tested.
- Restore procedures missing or unverified.
- Deployments that cannot safely roll back.
- Database and application release coupling.
- Configuration changes that require risky manual steps.
- Single-person operational knowledge.
- Undocumented emergency procedures.

Identify operational features that should be added, such as:

- Safe retry controls.
- Reconciliation commands.
- Dead-letter inspection.
- Job status visibility.
- Audit-log search.
- Health dashboards.
- Dependency status.
- Export progress.
- Backfill controls.
- Dry-run modes.
- Maintenance modes.
- Read-only modes.
- Safe administrative repair tools.

Only recommend them when tied to actual system risks or workflows.
