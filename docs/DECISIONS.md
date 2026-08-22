# Design decisions

## D1: Explicit invocation only

The skill is too expensive and too write-oriented for broad automatic matching. The description requires an explicit `$super-review`, `@super-review`, or `/super-review` mention, and client metadata disables implicit invocation where supported.

## D2: One canonical root report

Every run writes `<canonical-root>/FINDINGS.md`. A nested or differently named report would fragment history and make revalidation ambiguous. In review-only mode, it is the sole permitted repository modification.

## D3: Existing reports are evidence claims, not append-only logs

A prior report may be stale after code changes. Every prior record, summary claim, roadmap item, evidence location, and status must be revalidated. The new file is regenerated from the current canonical record set rather than blindly appended to.

## D4: Progressive disclosure by applicability

The original prompt is intentionally exhaustive. Its checks are preserved but split into focused directly linked references. Conditional phases can be closed only after bounded evidence establishes absence, and they reopen if later evidence changes applicability.

## D5: Repository execution is untrusted

Tests, package scripts, Make targets, generators, lifecycle hooks, and linters can execute arbitrary code. The skill inspects commands before execution, prefers isolation without ambient credentials or network, and requires authorization when safety cannot be established.

## D6: Runtime helpers resolve only from the skill root

Target-relative `scripts/...` is forbidden. A malicious reviewed repository must not be able to shadow the validator or writer. Absolute canonical paths and isolated Python mode are part of the runtime contract.

## D7: Exact-byte validation and commit

Validation of a path followed by a reread creates a swap race. The writer opens the candidate once without following its final component, reads immutable bytes, validates those bytes, and stages those same bytes. Path mutation is detected separately.

## D8: Optimistic concurrency plus protected human blocks

Atomic replacement prevents partial files but not lost updates. The writer records and rechecks starting state, refuses digest conflicts, and preserves named human annotation blocks byte for byte.

## D9: Deterministic stable identities

Sequential IDs alone are not stable enough across regenerated reports. A deterministic root-cause fingerprint anchors identity, while a retired-ID ledger prevents reuse and supports recurrence.

## D10: Separate canonical record types

Defects, improvements, feature decisions, and positive patterns have different semantics and fields. Keeping them separate prevents severity and roadmap priority from being conflated and lets summaries reference one authoritative record.

## D11: Shipped tests are intentional

The runtime helpers are security-sensitive and may be installed independently of this workbench. Shipping the focused regression suite allows an extracted package to validate itself and lets release verification test the exact deliverable.

## D12: Deterministic, side-effect-limited release tooling

Build and verification tools are standard-library-only and write only to explicit output locations. They do not commit, push, publish, deploy, or contact external services. External specification validation is a separate opt-in dependency.

## D13: One canonical skill behind thin marketplace adapters

Claude Code, GitHub Copilot CLI, Codex, and Cursor require different marketplace and plugin manifests. Claude and Copilot share a thin command adapter that loads `src/super-review/SKILL.md`. The adapter originally set `disable-model-invocation: true`, but Claude Code routes even user-typed slash commands through the model's Skill tool, so the flag made the command impossible to invoke at all; the adapter now relies on the skill description and the `SKILL.md` invocation gate for explicit-only activation. Codex points directly to the canonical skill and uses `agents/openai.yaml`. Cursor uses a repo-root `.cursor-plugin/plugin.json` that points `skills` at `./src/super-review` and adds a thin Cursor command adapter (no MCP registration; see D15). No adapter copies or symlinks the skill. Codex direct installs keep their unqualified invocation. Marketplace namespaces are accepted as explicit invocation without changing review behavior.

## D14: Optional MCP companion requires enforceable host trust (superseded by D15)

An optional companion MCP may front the FINDINGS helpers, but MCP configuration is a weaker trust anchor than `$SKILL_ROOT`. Hosts such as Claude Code resolve duplicate server names with local and project scope above user scope, so a reviewed repository's `.mcp.json` can override a user-scoped companion by name. Agents generally cannot observe that precedence from tool names alone, and a lookalike server can lie about any self-reported skill root or digest.

Therefore:

1. The skill defaults to the skill-root CLI and never prefers MCP merely because tools are visible.
2. MCP use requires host-attested provenance of the *active resolved* server
   (scope and executable or endpoint), plus explicit user affirmation for the
   run. Use the CLI if the host cannot prove that a project or local
   configuration did not override the server.
3. Server handshake values are not a trust root.
4. After any MCP commit that claims success, post-validate `<canonical-root>/FINDINGS.md` with the skill-root CLI.
5. On hosts without a write-authorization gate tied to explicit skill invocation, the companion must not expose `commit_findings`; commit remains CLI-only. Per-call MCP approval UIs that Auto-run, allowlist, or classifier modes can skip are not such a gate. The bundled Cursor plugin therefore ships the companion read-only (no `--enable-commit`).
6. Do not recommend project-scoped companion installation in reviewed repositories.

The companion lives outside the portable skill ZIP under `companion/`, with its own dependency pins and CI job.

## D15: Replace the MCP companion with a command-line interface

D14 could not enforce its trust conditions. Once registered, an MCP server lets
host automation or an injected instruction call tools without a human decision
for each call. Most hosts cannot attest which configuration supplied the active
server. A user-scoped server also shares one launch configuration across every
workspace, so its snapshot tool could read another repository by absolute path.
Removing the server closes those paths.

The companion is replaced by `cli/`, a consolidated `super-review` console command (`validate | snapshot | commit | fingerprint`) that forwards to the same skill-root helpers:

1. No server runs. Each operation requires an explicit shell command and arguments.
2. The trusted skill root stays explicit (`--skill-root` or `SUPER_REVIEW_SKILL_ROOT`) and is resolved with the same symlink/escape checks (D6); it is never inferred from the working directory.
3. `snapshot` accepts only a repository root and derives `<repo-root>/FINDINGS.md`, so the command cannot be pointed at arbitrary files.
4. The CLI delegates commits to `commit_findings.py`, preserving the digest
   check, annotations, and exit codes.
5. The CLI runtime is dependency-free; the MCP SDK leaves the repository entirely.

The shipped skill keeps its portable
`python3 -I "$SKILL_ROOT/scripts/<helper>.py"` contract. The CLI stays outside
the ZIP under `cli/` with its own pins, lockfile, and CI job.
