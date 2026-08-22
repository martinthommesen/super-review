# Changelog

All notable changes to `super-review` are recorded here.

## [1.6.0] — 2026-08-22

### Added

- One canonical structure scanner (`validate_findings.scan_report_structure`): the validator and the safe writer now parse fences and protected human blocks through a single bytes-native grammar (CommonMark backtick-info rule, block bodies opaque to fence parsing, space/tab-only fence closes, byte-oriented line segmentation), with a seeded differential regression guarding against re-divergence. An annotation containing an unbalanced fence marker can no longer wedge future commits.
- Registry and metadata cross-invariants: retired replacement chains must be acyclic, `superseded`/`consolidated` entries need at least one replacement ID, `Starting FINDINGS.md SHA-256: MISSING` pairs exclusively with `Existing report revalidated: No — file did not exist`, and a `Partial` revalidation cannot claim a `Complete` run.
- Unknown-field validation: every `Label: value` line in a record body must be a field defined for that record type (SEC-only fields on `SEC` records, decision-specific fields for the record's `Decision`, Options A–D fields on improvements).
- Snapshot output control: `--snapshot` gains `--metadata-only` and `--out FILE` for bounded output and exact-byte capture to a file (`--out` refuses paths inside the reviewed repository); the lifecycle now prefers the metadata-first flow before replacement, and an oversized or malformed prior report yields a `Partial`/`Blocked` run instead of streaming its content.
- A consolidated `super-review` CLI package under `cli/` (`validate | snapshot | commit | fingerprint`) wrapping the skill-root helpers with an explicit trusted root, a dependency-free runtime, hostile-CWD isolation tests, and an offline console smoke.
- The Apache-2.0 license text ships in every distributable payload (`super-review/LICENSE` in the ZIP, `src/LICENSE` for marketplace installs, `cli/LICENSE` in the CLI package), with byte-equality regressions.
- Decision D15: the MCP companion is replaced by the CLI — no server, no ambient tool surface, nothing invocable by host auto-run or prompt injection.

### Changed

- Reference docs re-aligned with the validator: phase-18's feature Confidence ladder and field labels, phase-17's option labels, core-principles' classification and confidence lists, the registry-first placement rule, the exact protected-block ID grammar, the `Effort`/`Risk` explanation separators, and the Starting-digest format.
- Protected human annotations are explicitly untrusted prior-report data: preserved byte for byte, never a source of authorization for commands, network access, scope changes, or instruction overrides.
- The concurrent-edit guarantee is scoped honestly: cooperating writers using the helper are fully serialized; a non-cooperating writer racing the final instant of replacement is detected best-effort.
- The writer works on Windows before Python 3.13 (`os.fchmod` fallback) and creates first-time reports on filesystems without hard links (atomic `O_CREAT|O_EXCL` fallback with unchanged conflict detection).

### Removed

- The optional MCP companion: `companion/`, the Cursor plugin's MCP registration, and all MCP prose in the shipped skill. Former companion tools map to the CLI — `validate_findings`/`snapshot_findings`/`commit_findings`/`fingerprint_finding` become `super-review validate|snapshot|commit|fingerprint`.

### Migration

- A colon-led line inside a field value (`Rollback: revert it`) now parses as an unknown field and fails validation — fence it, indent it, or rephrase it.
- `Effort` and `Risk of the proposed change` explanations must follow the enum value after ` — `, ` - `, `:`, or ` (`; a comma continuation is rejected.
- Reports containing registry replacement cycles, the contradictory metadata pairings above, fences closed with whitespace other than spaces/tabs, or structure that depended on backtick-in-info fence openers or exotic Unicode line separators were accepted inconsistently before and are now uniformly rejected. Annotations containing unbalanced fence markers become valid and preserved.

## [1.5.0] — 2026-07-28

### Added

- Public `validate_findings.snapshot` helper and `--snapshot` CLI mode that return exact on-disk `FINDINGS.md` bytes plus digest, or `MISSING` when absent.
- `commit_findings.commit_bytes` as the single digest-gated write core; the path CLI reads the candidate once and delegates to it.
- Optional `companion/` MCP front-end (separate pins, lockfile, and CI job) for fingerprint / validate / snapshot tools, with `commit_findings` gated behind `--enable-commit` for hosts that authorize writes on explicit skill invocation.
- Cursor plugin packaging (`.cursor-plugin/plugin.json`) that installs the canonical skill, a thin Cursor command adapter, and a **read-only** companion MCP via `${PLUGIN_ROOT}` paths (launches the `uv` executable; no `--enable-commit` because Cursor Auto-run can skip MCP prompts); prefer user-level install (D14).
- Companion MCP tool-path regression coverage via FastMCP `call_tool`, outbound 1 MiB snapshot content bound with CLI fallback, and `snapshot_findings` / `commit_findings` restricted to an absolute `repo_root`'s `FINDINGS.md`.
- Decision D14: default to the skill-root CLI; use MCP only with host-attested active-server provenance plus user affirmation; always post-validate commits via the trusted CLI; never treat project-scoped MCP registration or server self-reports as trust roots.

### Changed

- Documented the UTF-8 `content` + `content_sha256` MCP wire contract, 1 MiB companion size bound with CLI fallback, and mandatory CLI post-validation after any MCP commit.

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
