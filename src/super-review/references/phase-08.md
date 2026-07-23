# PHASE 8 — APIS, CONTRACTS, SCHEMAS, AND EXTERNAL INTEGRATIONS

Review:

- HTTP APIs.
- GraphQL APIs.
- RPC interfaces.
- WebSockets.
- CLI interfaces.
- Library APIs.
- Events.
- Queue messages.
- Webhooks.
- File formats.
- Configuration formats.
- Import and export formats.
- External integration adapters.
- Generated clients.
- Protocol schemas.

Evaluate:

- Input validation.
- Output validation.
- Contract consistency.
- Error semantics.
- Status codes.
- Versioning.
- Deprecation.
- Pagination.
- Filtering.
- Sorting.
- Idempotency.
- Retries.
- Timeouts.
- Cancellation.
- Authentication.
- Authorization.
- Rate limits.
- Backpressure.
- Compatibility.
- Unknown-field handling.
- Enum evolution.
- Field renaming.
- Optional-field behavior.
- Null behavior.
- Timestamp formats.
- Identifier stability.
- Correlation identifiers.
- Request limits.
- Response limits.
- Partial-success semantics.
- Batch behavior.
- Webhook verification.
- Duplicate webhook delivery.
- Out-of-order events.
- Event-schema evolution.
- Poison-message handling.
- Dead-letter handling.
- Replay behavior.
- External dependency degradation.

Look for contracts where:

- Documentation disagrees with implementation.
- Tests encode behavior not documented elsewhere.
- Clients assume fields the server does not guarantee.
- Servers reject safe schema evolution.
- Error shapes differ by endpoint.
- Internal database models leak directly into public APIs.
- External failures leak implementation details.
- Retries can duplicate side effects.
- An endpoint is technically idempotent but not operationally idempotent.
- Versioning exists but is not enforced.
- Deprecated versions have no removal plan.
- Generated code is stale relative to source schemas.

===============================================================================
