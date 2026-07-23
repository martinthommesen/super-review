# JavaScript and TypeScript Deep Checks

Review applicable first-party JavaScript, TypeScript, Node.js, browser, React, server-rendering, bundler, and package-runtime behavior for:

- Unsafe `any`, incorrect type assertions, missing strictness, and compile-time types that lack runtime/schema validation at trust boundaries.
- Promise creation, awaiting, rejection handling, cancellation, async sequencing, detached work, and event-listener cleanup.
- Module-system inconsistencies, side-effectful imports, environment-bound code, package export maps, and client/server boundary leakage.
- Prototype pollution, unsafe dynamic property access, object-merging behavior, serialization mismatches, and untrusted code execution.
- React effect dependencies, stale closures, state races, hydration mismatches, server-side rendering data exposure, and cleanup behavior.
- Bundle composition, tree shaking, duplicated dependencies, source-map exposure, browser compatibility, and generated client drift.

Trace framework abstractions to runtime behavior and configured compiler/bundler settings. Do not report type-system or framework preferences without a concrete consequence.
