# PHASE 4 — END-TO-END WORKFLOW TRACING

Identify and trace the most important workflows.

At minimum, include applicable workflows involving:

- Registration.
- Login.
- Logout.
- Password or credential changes.
- Session refresh.
- Authorization.
- Account recovery.
- Tenant creation.
- Tenant switching.
- User invitations.
- Role or permission changes.
- Creation of important records.
- Modification of important records.
- Deletion or archival.
- Financial transactions.
- Billing.
- Quotas.
- Entitlements.
- Inventory.
- File upload.
- File download.
- Data import.
- Data export.
- Search.
- Notifications.
- Webhooks.
- External API calls.
- Background jobs.
- Scheduled jobs.
- Administrative actions.
- Destructive operations.
- Migrations.
- Security-sensitive configuration.
- Support or impersonation workflows.

For each workflow, document:

1. Entry point.
2. Actor.
3. Input source.
4. Parsing.
5. Normalization.
6. Validation.
7. Authentication.
8. Authorization.
9. Domain rules.
10. Persistence.
11. Transaction boundaries.
12. Cache behavior.
13. Events or messages.
14. External side effects.
15. Retry behavior.
16. Idempotency behavior.
17. Duplicate handling.
18. Timeout and cancellation behavior.
19. Error classification.
20. Error translation.
21. Logging.
22. Metrics.
23. Response.
24. Cleanup.
25. Compensation.
26. Reconciliation.
27. Tests.

Look for gaps such as:

- Input validated at one layer but replaced with unvalidated data later.
- Authorization checked against one object but an operation performed on
  another.
- Tenant context accepted from an untrusted source.
- Business rules enforced in one entry point but bypassed elsewhere.
- Background workers operating with broader privileges than request paths.
- Direct database writes bypassing invariants.
- Non-idempotent side effects repeated by retries.
- Partial completion presented as success.
- Events published before a transaction commits.
- Cache invalidation occurring before persistence succeeds.
- Async work acknowledged before durable acceptance.
- Errors converted into misleading success responses.
- Missing rollback or compensation.
- Missing operator visibility for stuck work.
- State transitions that can become permanently wedged.

===============================================================================
