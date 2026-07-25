# Changelog

All notable changes to `super-review` are recorded here.

## [1.4.1] — 2026-07-26

### Fixed

- Removed `disable-model-invocation: true` from the shared Claude and Copilot command adapter. Claude Code routes user-typed slash commands through the model's Skill tool, so the flag rejected every invocation with "cannot be used with Skill tool due to disable-model-invocation"; explicit-only activation remains enforced by the skill description and the `SKILL.md` invocation gate.

## [1.4.0] — 2026-07-23

### Added

- Repository-backed plugin marketplaces for Claude Code, GitHub Copilot CLI, and Codex.
- Thin client plugin manifests that all resolve the single canonical `src/super-review/` skill instead of copying it, including a shared manual-only Claude and Copilot command adapter.
- Regression coverage for marketplace structure, canonical skill targeting, client metadata, and synchronized release versions.

### Fixed

- Prevented fenced examples and protected human annotation blocks from spoofing the canonical repository identity during safe report commits.
- Rejected relative `Canonical root` metadata before validation or commit so report identity cannot depend on the writer's working directory.
- Stopped canonical-root validation from dereferencing report-controlled paths, preventing malformed metadata or remote UNC roots from causing validation crashes or network access.

### Changed

- Added marketplace-qualified explicit invocation forms, used the qualified Codex mention in its starter prompt, and disabled Claude and Copilot model invocation in client-only metadata while retaining portable Agent Skills frontmatter.
- Documented marketplace installation and limited the portable direct-skill path to Codex or hosts with equivalent explicit-only invocation policy.
- Migration note: reports that recorded a relative `Canonical root` must materialize the same workspace-resolved location as an absolute path before validation or commit; the safe-write lifecycle already required absolute report identity.

## [1.3.0] — 2026-07-23

### Fixed

- Refused to commit a candidate whose stated `Canonical root` resolves to a different repository, closing a lost-report hazard when concurrent reviews collide on a shared candidate path. The safe writer now enforces this before the digest-gated write.

### Added

- A `--canonical-root` option on the report validator that requires the validated file to resolve to `<canonical-root>/FINDINGS.md` and its stated `Canonical root` to name that same repository, used by the post-write verification step.
- Adversarial regression coverage for the wrong-repository candidate case, a report that lives outside the repository it claims, and the validator's canonical-root cross-check.

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
