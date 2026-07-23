# PHASE 21 — VALIDATION AND REPRODUCTION

Every executable check in this phase is subject to `references/command-safety.md`. Test, build, lint, package, scanner, Make, migration, and lifecycle commands are repository code and must not be treated as read-only by name alone.

Use the narrowest useful checks while investigating.

Where available and safe, run applicable:

- Format checks.
- Lint checks.
- Type checks.
- Unit tests.
- Integration tests.
- Contract tests.
- End-to-end tests.
- Security scanners.
- Dependency audits.
- Migration validation.
- Schema validation.
- Build commands.
- Packaging commands.
- Documentation builds.
- Static analysis.
- Benchmarks.
- Targeted reproductions.

For every finding, attempt one or more of:

- Static proof.
- Existing failing test.
- New test concept.
- Minimal input.
- Reproduction command.
- Call-path demonstration.
- Schema contradiction.
- Configuration contradiction.
- Concurrency timeline.
- Query-plan evidence.
- Profiling evidence.

Do not:

- Run destructive tests against real data.
- Use production credentials.
- Contact external systems without authorization.
- Perform load testing against shared or production environments.
- Install broad tooling without approval.
- Treat scanner output as confirmed without manual verification.

Record:

- Commands run.
- Results.
- Failures.
- Environmental limitations.
- Checks not run and why.
- Whether generated or modified files appeared.

===============================================================================
