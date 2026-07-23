# Review History

## Initial packaging

The original exhaustive review prompt was converted into an Agent Skill with a mandatory repository-root `FINDINGS.md` report. Existing reports were made subject to complete revalidation before new findings were merged.

## External review round 1

The first review identified a monolithic protocol, broad trigger/write coupling, an insufficient untrusted-command boundary, lost-update risk, unstable identifiers, mixed record semantics, duplicated lifecycle rules, and potential filler from mandatory alternatives.

The 1.1.0 revision introduced phase-oriented progressive disclosure, explicit invocation, command isolation policy, digest-gated report replacement, protected human annotations, deterministic fingerprints, retired IDs, separate record types, external checkpoints, and evidence-based `Not applicable` handling.

## External review round 2

The second review found frontmatter portability issues, target-relative helper invocation, a candidate-byte time-of-check/time-of-use race, validator semantic gaps, and insufficient adversarial tests.

The 1.2.0 revision moved compatibility text into the body, used minimal frontmatter, bound helpers to the absolute skill root, committed the exact bytes validated, rejected unsafe path forms and concurrent changes, hardened Markdown and schema validation, and expanded the shipped suite to 45 tests.

## Workbench packaging

This repository wrapper adds reproducible local development, deterministic release creation, clean-room archive verification, CI, source provenance, maintainer documentation, and repository-level tests without changing the 1.2.0 skill source.
