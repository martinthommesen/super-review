---
name: super-review
description: Performs an exhaustive, evidence-based whole-repository engineering, architecture, security, reliability, product, UX, and feature-portfolio review. Use only when the user explicitly invokes $super-review, @super-review, or /super-review for a repository or directory; never auto-select it for a generic review or audit. Every run creates or refreshes the canonical root FINDINGS.md and revalidates all prior report content before merging current findings.
---

# Super Review

Version: 1.3.0

Compatibility: Requires filesystem access to the target repository or directory and permission to create or update its root `FINDINGS.md`. Git and code-search tools are recommended. Python 3 is recommended for the bundled fingerprint, report-validation, safe-write, and test scripts.

## Invocation gate

Run only after an explicit skill mention. Prefer `$super-review` in Codex; accept `@super-review` on mention-based clients and `/super-review` as the requested alias where supported. Do not activate for a generic review, audit, architecture assessment, security review, or codebase analysis.

```text
$super-review [repository path or directory] [optional review mode and context]
@super-review [repository path or directory] [optional review mode and context]
/super-review [repository path or directory] [optional review mode and context]
```

Use the supplied target. If none is supplied, use the current repository or workspace. Resolve the canonical root from the version-control root when available; otherwise use the supplied directory root.

## Trusted skill root

Resolve `SKILL_ROOT` once as the canonical absolute parent directory of this loaded `SKILL.md`. Resolve every bundled reference and helper from `SKILL_ROOT`; never from the current working directory, target repository, or a target-relative `scripts/` path. Before executing a helper, verify that the resolved path remains inside `SKILL_ROOT/scripts` and is a regular non-symlink file from the loaded skill package.

Invoke bundled Python helpers in isolated mode:

```text
python3 -I "$SKILL_ROOT/scripts/<helper>.py" ...
```

Use the platform-equivalent isolated Python invocation when `python3 -I` is unavailable. Do not substitute a same-named repository script.

## Non-negotiable output invariant

Every valid invocation must create or refresh exactly:

```text
<canonical-root>/FINDINGS.md
```

In `REVIEW ONLY`, that file is the sole permitted repository modification. Never write a competing report in a nested package or under another name. Before reading, revalidating, or replacing it, load and follow [the canonical findings lifecycle](references/findings-lifecycle.md). A run is incomplete until the current report is validated and safely written, or a concurrent-edit conflict is reported without overwriting another writer.

## Progressive loading contract

Do not preload the protocol. At activation, load only:

1. [Core mandate, context, review modes, and objectives](references/core-mandate.md).
2. [Evidence and review principles](references/core-principles.md).
3. [Canonical `FINDINGS.md` lifecycle](references/findings-lifecycle.md).
4. [Phase applicability and deep-loading rules](references/phase-applicability.md).

Before any repository-defined command, load [the untrusted-repository command-safety gate](references/command-safety.md).

Consider phases 0–22 in order and apply the applicability guide before deep loading. Load exactly one applicable phase file immediately before performing that phase. A conditional phase may be closed without loading its deep reference only after the guide's bounded absence checks establish that no relevant first-party surface exists. Record `Not applicable — <specific evidence basis>` and reopen the phase if later evidence changes applicability.

| Phase | Reference |
|---|---|
| 0 | [Instructions, safety, worktree, and baseline](references/phase-00.md) |
| 1 | [Coverage ledger and repository inventory](references/phase-01.md) |
| 2 | [Product, domain, user, and feature inventory](references/phase-02.md) |
| 3 | [Architecture and system design](references/phase-03.md) |
| 4 | [End-to-end workflow tracing](references/phase-04.md) |
| 5 | [Correctness and business logic](references/phase-05.md) |
| 6 | [Security, privacy, and abuse resistance](references/phase-06.md) |
| 7 | [Data models, databases, migrations, and integrity](references/phase-07.md) |
| 8 | [APIs, contracts, schemas, and integrations](references/phase-08.md) |
| 9 | [Concurrency, asynchrony, and distributed systems](references/phase-09.md) |
| 10 | [Performance, scalability, and cost](references/phase-10.md) |
| 11 | [Reliability, resilience, and operations](references/phase-11.md) |
| 12 | [Frontend, UX, accessibility, and client behavior](references/phase-12.md) |
| 13 | [Testing and quality strategy](references/phase-13.md) |
| 14 | [Dependencies, build, packaging, and supply chain](references/phase-14.md) |
| 15 | [Configuration, infrastructure, and deployment](references/phase-15.md) |
| 16 | [Maintainability, code quality, and developer experience](references/phase-16.md) |
| 17 | [Better or different implementations](references/phase-17.md) |
| 18 | [Feature portfolio decisions](references/phase-18.md) |
| 19 | [Documentation and knowledge quality](references/phase-19.md) |
| 20 | [Language- and framework-specific dispatcher](references/phase-20.md) |
| 21 | [Validation and reproduction](references/phase-21.md) |
| 22 | [Prioritization and roadmap](references/phase-22.md) |

For phase 20, load only the directly linked stack references supported by repository evidence: [JavaScript and TypeScript](references/stack-javascript-typescript.md), [Python](references/stack-python.md), [Go](references/stack-go.md), [Rust](references/stack-rust.md), [Java and Kotlin](references/stack-java-kotlin.md), [C# and .NET](references/stack-dotnet.md), [C and C++](references/stack-c-cpp.md), [SQL and query systems](references/stack-sql.md), and [mobile clients](references/stack-mobile.md).

Before canonicalizing records, load [identity and cross-reference rules](references/record-core.md), then only the templates needed for actual records: [defects and risks](references/record-defect-risk.md), [improvements and alternatives](references/record-improvement-alternative.md), [feature decisions](references/record-feature-decision.md), and [positive patterns](references/record-positive-pattern.md). Before report assembly, load [the final report schema](references/final-report.md). Before completion, load [the quality bar and final gates](references/quality-bar.md).

All referenced rules are normative. Progressive loading changes when instructions enter context, not whether applicable checks are performed.

## Execution architecture

1. Resolve instructions, authorization, mode, target, root, exclusions, compatibility contracts, and supplied context.
2. Snapshot repository state and the exact `FINDINGS.md` bytes/digest. Preserve protected human blocks and build the prior-report revalidation ledger.
3. Establish command safety before executable validation.
4. Perform phases 0–22 in order while maintaining coverage and evidence ledgers.
5. Checkpoint long-running analysis outside the repository, bound to root, revision, worktree state, and starting report digest; invalidate stale phase results after changes.
6. Revalidate every prior claim, then perform independent current-repository discovery. The old report never limits coverage.
7. Canonicalize by root cause or decision basis; compute deterministic fingerprints; preserve active and retired IDs; derive summaries and roadmap from canonical records.
8. Generate the candidate outside the repository. Run `python3 -I "$SKILL_ROOT/scripts/validate_findings.py" <candidate-path>` and fix every error.
9. Reread the current report immediately before replacement. Use `python3 -I "$SKILL_ROOT/scripts/commit_findings.py" ...` or a demonstrably equivalent exact-byte, digest-gated, annotation-preserving atomic write that also refuses a candidate whose stated canonical root belongs to a different repository. On conflict, reread, revalidate, merge, regenerate, and retry; never force an overwrite.
10. Reread the committed file, rerun the absolute-path validator with `--canonical-root <canonical-root>`, and verify the stated canonical root, revision, completion status, IDs, summaries, roadmap, validation record, annotations, and ending.

## Review modes and evidence

Use the requested mode; default to `REVIEW ONLY`. The root `FINDINGS.md` update applies in every mode. Never infer permission for source changes, dependency installation, network or secret access, production systems, migrations, public-contract changes, feature removal, deployment, publication, commits, pushes, or irreversible actions.

Confirmed and high-confidence records require current repository evidence. Distinguish facts, supported inferences, hypotheses, and unavailable evidence. Trace important behavior through callers, consumers, tests, schemas, configuration, persistence, deployment, failures, retries, cleanup, compensation, and compatibility paths. Manually verify scanner output and protect secrets and personal data.

Exhaustiveness means every meaningful first-party area and required review dimension is considered; it does not mean manufacturing findings. For unsupported or inapplicable fields, alternatives, categories, or subsystem analyses, write `Not applicable — <specific evidence-based reason>` or `Not established — <missing evidence>`.

## Completion response

After safe write and revalidation, report only:

- Exact `FINDINGS.md` path.
- Reviewed branch, revision, or directory state.
- Whether the prior report was fully revalidated.
- Highest-priority active canonical IDs, or that none were confirmed.
- Validation status and material limitations.

Do not duplicate the full report in chat unless explicitly requested.
