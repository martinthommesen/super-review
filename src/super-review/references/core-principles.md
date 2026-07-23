# Non-Negotiable Review Principles

1. INSPECT BEFORE CONCLUDING

Do not reach conclusions from filenames, isolated snippets, comments, or a
single layer of an interface.

Trace:

- Definitions.
- Callers.
- Implementations.
- Tests.
- Schemas.
- Configuration.
- Deployment behavior.
- Generated clients.
- Public consumers.
- Persistence.
- Error paths.
- Cleanup paths.
- Runtime assumptions.

2. USE EVIDENCE, NOT SPECULATION

Every confirmed finding must include concrete repository evidence.

Prefer:

- Exact file paths.
- Exact line ranges.
- Symbols, methods, routes, queries, schemas, or configuration keys.
- Call chains.
- Reproducible inputs.
- Failing commands.
- Test gaps tied to a specific behavior.
- Contradictions between code, tests, schemas, and documentation.

Do not state that something is unused, slow, insecure, or low-value without
supporting evidence.

3. DISTINGUISH DEFECTS FROM IMPROVEMENTS

Classify recommendations as one of:

- Confirmed defect.
- Probable defect.
- Security weakness.
- Reliability risk.
- Performance risk.
- Maintainability concern.
- Architectural concern.
- Product or UX concern.
- Feature opportunity.
- Feature-removal candidate.
- Alternative implementation opportunity.
- Documentation issue.
- Testing gap.
- Operational gap.
- Optional optimization.
- Positive pattern worth preserving.

Do not present a subjective preference as a correctness defect.

4. TRACE IMPORTANT BEHAVIOR END TO END

For important workflows, follow data and control flow from external input
through:

- Parsing.
- Normalization.
- Validation.
- Authentication.
- Authorization.
- Business logic.
- Persistence.
- Transactions.
- Queues or events.
- External calls.
- Retries.
- Caching.
- Serialization.
- Response generation.
- Logging.
- Metrics.
- Cleanup.
- Compensation and recovery.

5. REVIEW FAILURE PATHS AS SERIOUSLY AS SUCCESS PATHS

Inspect behavior under:

- Invalid input.
- Missing input.
- Duplicate input.
- Oversized input.
- Partial failure.
- Dependency failure.
- Network failure.
- Timeout.
- Cancellation.
- Retry.
- Duplicate delivery.
- Out-of-order delivery.
- Process termination.
- Container restart.
- Database rollback.
- Stale cache.
- Concurrent mutation.
- Resource exhaustion.
- Disk exhaustion.
- Clock skew.
- Corrupt or legacy data.
- Deployment during active traffic.

6. SEARCH FOR SYSTEMIC CAUSES

When multiple findings share a root cause, consolidate them into one systemic
finding and list all affected locations.

Do not report twenty copies of the same mistake as twenty independent design
issues.

7. RESPECT REAL COMPATIBILITY CONTRACTS

Do not casually recommend breaking:

- Public APIs.
- Persisted data.
- Event formats.
- Queue messages.
- Database schemas.
- Configuration formats.
- CLI behavior.
- File formats.
- URLs.
- Authentication behavior.
- External integrations.
- Supported deployment environments.
- Documented extension points.

When recommending a breaking change, include a migration, deprecation, rollback,
and compatibility strategy.

8. DO NOT WORSHIP THE CURRENT DESIGN

Repository conventions are evidence, not proof that the design is optimal.

Identify when an established pattern is:

- Correct and worth preserving.
- Consistent but unnecessarily complicated.
- Historically understandable but now obsolete.
- Actively harmful.
- Inconsistently applied.
- Better replaced with a simpler pattern.

9. DO NOT CHASE NOVELTY

Do not recommend:

- A new framework merely because it is newer.
- Microservices merely because the system is a monolith.
- A monolith merely because distributed systems are difficult.
- Event sourcing without a demonstrated domain need.
- A new database without clear benefits.
- A new dependency for trivial functionality.
- A rewrite without compelling evidence.
- Abstract factories, plugin systems, generic repositories, or other patterns
  without concrete consumers.
- Configuration that no current requirement needs.
- Features unsupported by user, workflow, risk, or operational evidence.

10. PREFER THE SMALLEST EFFECTIVE IMPROVEMENT

For each recommendation, consider:

- Keeping the current implementation.
- Hardening the current implementation.
- Simplifying the current implementation.
- Incrementally redesigning the subsystem.
- Replacing the approach entirely.

Recommend the least disruptive option that adequately solves the underlying
problem.

11. STATE UNCERTAINTY CLEARLY

Use confidence levels:

- Confirmed.
- High confidence.
- Medium confidence.
- Low confidence.
- Hypothesis requiring validation.

Explain what evidence would raise or lower confidence.

12. PROTECT SENSITIVE INFORMATION

Never reproduce:

- Credentials.
- Tokens.
- Private keys.
- Complete connection strings.
- Customer data.
- Personal data.
- Authentication cookies.
- Production secrets.
- Encryption material.

Refer to the location and type safely.

13. DO NOT CONFUSE VOLUME WITH COVERAGE

Exhaustive review means all meaningful first-party areas are considered.

It does not require wasting effort line-by-line on:

- Vendored third-party code.
- Generated output whose source definition has already been reviewed.
- Lockfile internals.
- Build artifacts.
- Binary assets.

Review the boundaries, generation sources, configuration, and risks of those
areas without treating them as ordinary handwritten application code.

===============================================================================
REQUIRED REVIEW PROCESS
===============================================================================

Complete the following phases.

Do not omit a phase because the repository appears small.
