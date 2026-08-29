# Changelog

All notable changes to `super-review` are recorded here.

## [1.6.1] (2026-08-29)

### Fixed

- The safe writer can refresh an existing `FINDINGS.md` on macOS. The
  atomic exchange now probes `renameat2` first and then Darwin's
  `renameatx_np` with `RENAME_SWAP`. The descriptor-relative
  security model and the fail-closed guard are unchanged. Filesystems
  without an atomic swap, such as HFS+ and ExFAT, still fail closed with
  no partial write. Regression tests pin the Darwin symbol selection and
  the nonzero swap flag. (#26)

### Changed

- `SKILL.md`, `references/final-report.md`, and
  `references/findings-lifecycle.md` state that `Canonical root` must be
  the physical, symlink-resolved path. On macOS, a stated `/tmp` or
  `/var` path does not match the resolved `/private` destination and is
  rejected.
- CI runs the offline pipeline on macOS as well as Ubuntu. Every test
  suite pins a symlink-resolved temporary root, so the suites pass
  under the symlinked default macOS `TMPDIR`.

## [1.6.0] (2026-08-22)

### Added

- `validate_findings.scan_report_structure` is now the only scanner for fences
  and protected blocks. The validator and writer share its byte-level grammar.
  A seeded differential test prevents the two callers from diverging.
- Registry validation rejects replacement cycles and requires replacement IDs
  for `superseded` and `consolidated` entries. Metadata validation rejects
  contradictory digest, revalidation, and completion values.
- Record validation rejects `Label: value` fields that the record type or feature
  decision does not define.
- Snapshot mode supports `--metadata-only` and `--out FILE`. Output files must be
  outside the reviewed repository. Supported platforms pin the parent directory
  before writing so a concurrent path swap cannot redirect the file.
- `cli/` provides `validate`, `snapshot`, `commit`, and `fingerprint` commands.
  The runtime has no third-party dependencies and requires an explicit skill root.
- Every distributable contains the Apache-2.0 license text. Tests require all
  packaged copies to match the root license byte for byte.
- Decision D15 replaced the MCP companion with the CLI. The repository no longer
  registers a server that host automation or injected instructions can call.

### Fixed

- Commit and CLI snapshot operations now stay bound to pinned directory
  descriptors. Candidates are prepared in private pinned directories. Existing
  targets use one atomic exchange with displaced-inode verification and conflict
  recovery, while missing targets use atomic no-replace hard links. Failed
  post-exchange checks preserve the private recovery leaf and never attempt a
  second pathname exchange. Publication verifies the final inode and exact bytes
  and rejects repository or output-directory rebinding.
- The consolidated CLI invokes command-specific validator entry points. `validate`
  can no longer select snapshot or self-test modes, every subcommand has predictable
  help exit behavior, and failed helper imports restore reserved `sys.modules`
  entries.
- Improvement option fields are checked against their actual Option A through D
  range. Shared fields remain valid in every range that defines them.
- Registry replacement chains use linear reverse terminal pruning, avoiding
  quadratic validation time for large valid registries.
- Verification commands use locked dependency state. Tests suppress project
  bytecode, cleanup and tree checks prune dependency environments, and the
  repository suite checks root entrypoint modes. Cleanup stays bound to opened
  directory descriptors and refuses platforms without symlink-safe removal.

### Changed

- Reference files now match the validator's field values, option labels, registry
  placement, protected-block IDs, explanation separators, and digest format.
- Protected annotations remain byte-exact but grant no authority to run commands,
  use the network, change scope, or override instructions.
- The advisory lock serializes writers that use the helper. Atomic exchange
  preserves a non-cooperating writer's displaced target when the publication
  window detects a conflict. Recovery avoids a second exchange whose source name
  could change after validation.
- Safe publication requires descriptor-relative operations, descriptor-based mode
  setting, directory sync, hard links for a missing final leaf, and name exchange
  for an existing final leaf. Unsupported platforms and filesystems return an
  error without publishing a new report.
- Removed dead CLI and fixture wrappers. Code comments and documentation now state
  the mechanism or contract instead of narrating the implementation.

### Removed

- Removed `companion/`, Cursor's MCP registration, and MCP instructions from the
  shipped skill. The old tool operations map to `super-review validate`,
  `snapshot`, `commit`, and `fingerprint`.

### Migration

- A colon-led line inside a field value, such as `Rollback: revert it`, now
  parses as an unknown field. Fence, indent, or rephrase the line.
- `Effort` and `Risk of the proposed change` explanations must follow the enum value after ` — `, ` - `, `:`, or ` (`; a comma continuation is rejected.
- Reports with replacement cycles, contradictory metadata, invalid fence closing
  whitespace, or backticks in backtick-fence info strings are now rejected
  consistently. Unicode line separators remain content instead of becoming
  structural line breaks. Unbalanced fence markers inside protected annotations
  remain valid content.

## [1.5.0] (2026-07-28)

### Added

- Public `validate_findings.snapshot` helper and `--snapshot` CLI mode that return exact on-disk `FINDINGS.md` bytes plus digest, or `MISSING` when absent.
- `commit_findings.commit_bytes` as the single digest-gated write core; the path CLI reads the candidate once and delegates to it.
- Optional `companion/` MCP front-end (separate pins, lockfile, and CI job) for fingerprint / validate / snapshot tools, with `commit_findings` gated behind `--enable-commit` for hosts that authorize writes on explicit skill invocation.
- Cursor plugin packaging (`.cursor-plugin/plugin.json`) that installs the canonical skill, a thin Cursor command adapter, and a **read-only** companion MCP via `${PLUGIN_ROOT}` paths (launches the `uv` executable; no `--enable-commit` because Cursor Auto-run can skip MCP prompts); prefer user-level install (D14).
- Companion MCP tool-path regression coverage via FastMCP `call_tool`, outbound 1 MiB snapshot content bound with CLI fallback, and `snapshot_findings` / `commit_findings` restricted to an absolute `repo_root`'s `FINDINGS.md`.
- Decision D14: default to the skill-root CLI; use MCP only with host-attested active-server provenance plus user affirmation; always post-validate commits via the trusted CLI; never treat project-scoped MCP registration or server self-reports as trust roots.

### Changed

- Documented the UTF-8 `content` + `content_sha256` MCP wire contract, 1 MiB companion size bound with CLI fallback, and mandatory CLI post-validation after any MCP commit.

## [1.4.1] (2026-07-26)

### Fixed

- Removed `disable-model-invocation: true` from the shared Claude and Copilot command adapter. Claude Code routes user-typed slash commands through the model's Skill tool, so the flag rejected every invocation with "cannot be used with Skill tool due to disable-model-invocation"; explicit-only activation remains enforced by the skill description and the `SKILL.md` invocation gate.

## [1.4.0] (2026-07-23)

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

## [1.3.0] (2026-07-23)

### Fixed

- Refused to commit a candidate whose stated `Canonical root` resolves to a different repository, closing a lost-report hazard when concurrent reviews collide on a shared candidate path. The safe writer now enforces this before the digest-gated write.

### Added

- A `--canonical-root` option on the report validator that requires the validated file to resolve to `<canonical-root>/FINDINGS.md` and its stated `Canonical root` to name that same repository, used by the post-write verification step.
- Adversarial regression coverage for the wrong-repository candidate case, a report that lives outside the repository it claims, and the validator's canonical-root cross-check.

## [1.2.0] (2026-07-22)

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

## [1.1.0] (2026-07-22)

### Changed

- Split the monolithic review protocol into phase-oriented and schema-oriented references.
- Narrowed activation to explicit invocation.
- Added an untrusted-repository command-execution boundary.
- Added report digest checks, protected human annotations, deterministic record fingerprints, retired-ID tracking, separate canonical record types, and resumable external checkpoints.

### Added

- Initial report validator, fingerprint generator, and digest-gated safe writer.

## [1.0.0] (2026-07-22)

### Added

- Initial Agent Skill packaging of the exhaustive whole-codebase review prompt.
- Mandatory canonical root `FINDINGS.md` behavior with prior-report revalidation.
