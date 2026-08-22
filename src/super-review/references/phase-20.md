# Phase 20: language- and framework-specific review

Load this dispatcher for every review. Detect the actual languages, query systems, frameworks, runtimes, and client platforms from manifests, build files, imports, generated sources, tests, deployment artifacts, and entry points.

Then load only the applicable stack references linked directly from `SKILL.md`. Do not load a stack reference merely because vendored, generated, fixture, or documentation-only code mentions that stack.

For frameworks or languages not listed, derive equivalent checks from official semantics, repository configuration, compiler or runtime guarantees, and established ecosystem failure modes. Do not apply irrelevant checklists mechanically. Record every selected stack reference and the evidence for excluding others.

Cross-check stack-specific conclusions against the universal correctness, security, data, concurrency, performance, reliability, testing, dependency, deployment, and maintainability phases. A language idiom is not proof that behavior is correct, and a generic concern is not a finding without repository evidence.
