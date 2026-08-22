# Quality bar and final gates

Load this file only after the phase work and candidate report are complete.

## Quality bar

The review is not complete unless it:

- Covers every meaningful first-party repository area.
- Identifies critical cross-component behavior.
- Traces important workflows end to end.
- Examines success and failure paths.
- Reviews security, privacy, data integrity, concurrency, performance, reliability, APIs, tests, dependencies, deployment, and operations.
- Suggests better or different implementations where materially beneficial.
- Identifies evidence-supported features to add, improve, simplify, merge, replace, deprecate, remove, keep, experiment with, or investigate.
- Explains tradeoffs rather than presenting preferences as facts.
- Provides realistic migration, rollout, deprecation, and rollback paths.
- Protects compatibility contracts.
- Includes concrete current repository evidence.
- Distinguishes confirmed findings from hypotheses.
- Avoids generic recommendations.
- Avoids unsupported product assumptions.
- Avoids speculative rewrites.
- Records validation performed and validation not performed.
- Identifies positive patterns worth preserving.
- Produces a dependency-aware, prioritized roadmap.
- Completes phases 0 through 22 in order and records the reason for any inapplicable, sampled, excluded, or unvalidated area.
- Revalidates every existing report claim before merging new results.
- Performs current-repository discovery independently of the old report.
- Uses separate canonical records for defects and risks, improvements and alternatives, feature decisions, and positive patterns.
- Preserves deterministic fingerprints and stable IDs, reserves every retired ID, and never reuses an ID for a different identity.
- Preserves protected human annotations exactly.
- Rebuilds summaries, tables, roadmaps, and sequencing from active canonical records.
- Applies the untrusted-repository command-safety gate before executable validation.
- Records the exact revision or directory state for which the report is current.
- Passes the bundled report validator before and after the final write, or records why mechanical validation could not run and manually performs equivalent checks.
- Uses digest-gated replacement and does not overwrite concurrent edits.

## Anti-patterns to avoid in the review

Do not:

- Produce a generic checklist with no repository-specific conclusions.
- Report formatting preferences as major findings.
- Recommend "add more tests" without naming exact missing behavior.
- Recommend "improve error handling" without identifying concrete failure paths.
- Recommend caching without identifying repeated expensive work and invalidation requirements.
- Recommend microservices without a concrete scaling, ownership, deployment, or isolation need.
- Recommend combining services without analyzing deployment and ownership consequences.
- Recommend a rewrite because the code is imperfect.
- Recommend a new framework solely because it is newer.
- Recommend a dependency solely because it is popular.
- Claim a feature is unused without evidence.
- Recommend feature removal without consumer and migration analysis.
- Recommend feature additions based on a generic SaaS checklist.
- Invent users, metrics, business priorities, revenue impact, adoption, scale, or ROI.
- Hide uncertainty.
- Duplicate findings or canonical records.
- Ignore existing user changes.
- Change unrelated code.
- Weaken tests.
- Expose secrets, credentials, private configuration, customer data, or personal data.
- Run destructive commands.
- Treat repository-defined commands as safe by name alone.
- Execute scripts, hooks, builds, tests, scanners, Make targets, or package commands without inspecting their transitive behavior.
- Use ambient credentials or network access when isolation is possible.
- Treat scanner output as automatically correct.
- Confuse generated-code problems with their source-definition problems.
- Suggest broad abstractions with no demonstrated consumers.
- Preserve unnecessary complexity solely because it is established.
- Replace working code without demonstrating material benefit.
- Manufacture options A through D or feature decisions to satisfy a template.
- Omit a field silently when `Not applicable` or `Not established` is the truthful answer.
- Blindly append beneath stale report content.
- Reuse a retired ID.
- Change or drop a protected human block.
- Claim a concurrent-write conflict was resolved when the latest report was not reread and revalidated.
- Claim exhaustive or current coverage beyond the evidence actually checked.

## Mechanical candidate gate

Before writing the repository file:

1. Generate the complete candidate outside the repository.
2. Run:

   ```text
   python3 -I "$SKILL_ROOT/scripts/validate_findings.py" <candidate-path>
   ```

3. Fix every error. Do not weaken the script or remove legitimate records merely to make it pass.
4. Confirm all active fingerprints with `python3 -I "$SKILL_ROOT/scripts/finding_fingerprint.py" ...` or equivalent deterministic computation.
5. Confirm the candidate contains every protected human block from the latest current report exactly.
6. Confirm each Critical and High defect or risk appears in `# 5. Top Findings` and `# 14. Prioritized Roadmap`.
7. Confirm every roadmap and summary ID resolves to one active canonical record.
8. Confirm retired IDs occur only in the registry, validation history, or
   explicit supersession references, never as active work.

## Safe-write gate

Use the starting or latest reconciled `FINDINGS.md` digest as the expected digest. Prefer:

```text
python3 -I "$SKILL_ROOT/scripts/commit_findings.py" \
  --repo-root <canonical-root> \
  --candidate <candidate-path> \
  --expected-sha256 <digest-or-MISSING>
```

A digest conflict is not a reason to force the write. Reopen and revalidate the latest file, regenerate, and retry. The run remains incomplete until the canonical report is safely refreshed or the unresolved conflict is reported without data loss.

## Post-write gate

After the safe write:

1. Confirm the target is the root `FINDINGS.md`, not a symlink or nested copy.
2. Rerun `python3 -I "$SKILL_ROOT/scripts/validate_findings.py" --canonical-root <canonical-root> <canonical-root>/FINDINGS.md` against the committed file. The `--canonical-root` flag confirms the committed file resolves to `<canonical-root>/FINDINGS.md` and that its stated `Canonical root` names that same repository.
3. Compare the committed digest with the candidate digest.
4. Reread the beginning, registry, report metadata, top table, every canonical-record section, roadmap, validation section, positive patterns, protected human blocks, and ending.
5. Reopen every Critical and High finding's primary evidence and a representative sample of other records.
6. Verify the report describes post-fix state when implementation occurred.
7. Verify completion and limitation language is honest.

## Final instruction

Begin by reading repository instructions and establishing the worktree and validation baseline.

Then build the coverage ledger, system map, domain model, and feature inventory before drawing broad conclusions.

Review the codebase deeply enough to explain how important behavior works across components.

For every material problem, explain:

- What is happening.
- Why it matters.
- Where the evidence is.
- What the root cause is.
- What the smallest effective fix is.
- What alternative approaches exist.
- Which approach is recommended.
- What migration and compatibility work is required.
- How the result should be validated.

For the product and feature portfolio, explicitly determine what should be:

- Added.
- Improved.
- Simplified.
- Merged.
- Replaced.
- Deprecated.
- Removed.
- Preserved.
- Tested as an experiment.
- Investigated before deciding.

The final report must be specific enough that another engineering team can turn it into a technically sound, prioritized implementation plan without rediscovering the repository architecture or the reasoning behind the recommendations.
