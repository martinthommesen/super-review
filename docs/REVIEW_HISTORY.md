# Review history

## Initial packaging

The original exhaustive review prompt was converted into an Agent Skill with a mandatory repository-root `FINDINGS.md` report. Existing reports were made subject to complete revalidation before new findings were merged.

## External review round 1

The first review identified a monolithic protocol, broad trigger/write coupling, an insufficient untrusted-command boundary, lost-update risk, unstable identifiers, mixed record semantics, duplicated lifecycle rules, and potential filler from mandatory alternatives.

The 1.1.0 revision introduced phase-oriented progressive disclosure, explicit invocation, command isolation policy, digest-gated report replacement, protected human annotations, deterministic fingerprints, retired IDs, separate record types, external checkpoints, and evidence-based `Not applicable` handling.

## External review round 2

The second review found frontmatter portability issues, target-relative helper invocation, a candidate-byte time-of-check/time-of-use race, validator semantic gaps, and insufficient adversarial tests.

The 1.2.0 revision moved compatibility text into the body, used minimal frontmatter, bound helpers to the absolute skill root, committed the exact bytes validated, rejected unsafe path forms and concurrent changes, hardened Markdown and schema validation, and expanded the shipped suite to 45 tests.

## Workbench packaging

This repository wrapper added reproducible local development, deterministic release creation, clean-room archive verification, CI, source provenance, maintainer documentation, and repository-level tests without changing the then-current 1.2.0 skill source. Later releases evolve the skill source itself; see `CHANGELOG.md`.

## Marketplace and companion releases

Releases 1.3.0 through 1.5.0 added the wrong-repository commit guard, marketplace packaging behind thin client adapters, the explicit-invocation command-adapter fix, the `commit_bytes` write core, and an optional MCP companion front-end.

## External review round 3

The third round used two independent reviews. It found different fence grammars
in the validator and writer, a Windows `os.fchmod` crash, reference values that
did not match the validator, missing license text, an MCP snapshot tool that
could read other workspaces, weak registry and metadata checks, network-capable
offline validation, and stale suppressions and documentation.

Version 1.6.0 moved structural parsing into one scanner, fixed writer behavior
across platforms, tightened registry and metadata checks, rejected unknown
record fields, packaged the license, replaced MCP with a CLI under D15, and made
the offline gate independent of the network.
