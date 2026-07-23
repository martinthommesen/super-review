# Changelog

All notable changes to `super-review` are recorded here.

## [1.2.0] — 2026-07-22

### Fixed

- Removed non-portable frontmatter fields from the shipped entrypoint.
- Bound helper execution to the trusted absolute skill root and isolated Python mode.
- Closed candidate validation/write races by reading once through a no-follow descriptor, validating immutable bytes, and committing those same bytes.
- Rejected symlink candidates, hard-link aliases, repository-local candidate files, path replacements, oversized reports, and concurrent report creation or mutation.
- Hardened the report validator for required metadata, enum values, mandatory fields, unresolved placeholders, fenced Markdown, protected human blocks, report-path races, registry placement, and roadmap mapping.

### Added

- A 45-test shipped regression suite covering helper-path isolation, report semantics, Markdown parsing, links, symlinks, hard links, candidate races, digest conflicts, protected annotations, exact bytes, and package structure.
- Explicit Codex implicit-invocation opt-out metadata.
- Stack-specific progressive-disclosure references and conditional phase applicability.

## [1.1.0] — 2026-07-22

### Changed

- Split the monolithic review protocol into phase-oriented and schema-oriented references.
- Narrowed activation to explicit invocation.
- Added an untrusted-repository command-execution boundary.
- Added report digest checks, protected human annotations, deterministic record fingerprints, retired-ID tracking, separate canonical record types, and resumable external checkpoints.

### Added

- Initial report validator, fingerprint generator, and digest-gated safe writer.

## [1.0.0] — 2026-07-22

### Added

- Initial Agent Skill packaging of the exhaustive whole-codebase review prompt.
- Mandatory canonical root `FINDINGS.md` behavior with prior-report revalidation.
