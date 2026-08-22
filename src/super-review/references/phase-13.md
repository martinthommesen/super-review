# Phase 13: testing and quality strategy

Inventory:

- Unit tests.
- Integration tests.
- End-to-end tests.
- Contract tests.
- Snapshot tests.
- Property tests.
- Fuzz tests.
- Performance tests.
- Load tests.
- Security tests.
- Migration tests.
- UI tests.
- Accessibility tests.
- Smoke tests.
- Deployment verification.
- Test fixtures.
- Test factories.
- Mocks.
- Fakes.
- Test utilities.

Evaluate:

- Coverage of critical workflows.
- Coverage of failure paths.
- Coverage of authorization.
- Coverage of tenant isolation.
- Coverage of retries.
- Coverage of idempotency.
- Coverage of concurrency.
- Coverage of migrations.
- Coverage of compatibility.
- Coverage of malformed input.
- Coverage of boundary values.
- Test determinism.
- Test isolation.
- Test speed.
- Test readability.
- Test maintenance cost.
- Fixture realism.
- Mock fidelity.
- Assertions that prove intended behavior.
- Tests that pass without exercising meaningful behavior.
- Overmocking.
- Brittle implementation-coupled tests.
- Snapshot overuse.
- Missing assertions.
- Flaky timing assumptions.
- Randomness without reproducible seeds.
- Shared global test state.
- Production behavior disabled in tests.
- Test-only code paths that hide defects.
- Database tests that do not match production semantics.
- Migrations never tested from real prior versions.
- External integration contracts not verified.
- Security controls tested only through happy paths.

For every major finding, propose the most appropriate regression-test level:

- Unit.
- Integration.
- Contract.
- End-to-end.
- Property-based.
- Fuzz.
- Concurrency.
- Load.
- Migration.
- Security.

Do not propose end-to-end tests when a smaller deterministic test proves the
behavior adequately.
