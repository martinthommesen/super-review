# Canonical Record Schemas

Load this file only when canonicalizing review results. It separates defects and risks, improvements and alternatives, feature decisions, and positive patterns so each conclusion has one authoritative record.

## Canonicalization rules

- Every material conclusion appears in full exactly once as one canonical record.
- Summary tables, domain summaries, security summaries, roadmaps, and implementation sequences reference canonical IDs instead of repeating record bodies.
- Consolidate records that share one root cause or decision basis. List all affected locations in the surviving record.
- Use current repository evidence. A scanner result, comment, filename, age, or subjective preference is not sufficient by itself.
- Every field is mandatory unless the template marks it conditional. When evidence does not support a field, write `Not applicable — <specific evidence-based reason>` or `Not established — <missing evidence and validation needed>`. Do not omit fields or manufacture content.
- Active records use `Status: Active`. Resolved, superseded, consolidated, and invalidated identities exist only in the retired registry and concise validation history, not as active canonical records.
- Use deterministic identity and ID rules from `references/findings-lifecycle.md`.

## Allowed prefixes

### Defects and risks

- `COR` — correctness and business logic.
- `SEC` — security, privacy, authorization, abuse resistance, or sensitive-data risk.
- `DAT` — data model, persistence, migration, or integrity.
- `ARC` — architecture, responsibility, dependency, or systemic design risk.
- `REL` — reliability, resilience, distributed workflow, or availability.
- `PER` — performance, scalability, resource, or cost risk.
- `API` — API, schema, event, file-format, or compatibility contract.
- `TST` — testing strategy or misleading/brittle test defect.
- `OPS` — operations, observability, deployment, rollback, infrastructure, or supply-chain risk.
- `MNT` — maintainability or code-quality concern.
- `UX` — UX, accessibility, internationalization, or client-behavior concern.
- `DOC` — documentation or knowledge-quality issue.
- `DX` — developer-experience or tooling issue.

### Improvements and alternatives

- `IMP` — materially better implementation or workflow without a current defect.
- `ALT` — alternative component, system, architecture, or technology design.

### Feature decisions

- `FEAT` — add, improve, simplify, merge, replace, keep, experiment, or investigate.
- `REM` — deprecate or remove.

### Positive patterns

- `POS` — design, control, workflow, test, operational practice, or abstraction worth preserving.

## Common identity header

Every canonical record begins with:

```markdown
## [PREFIX-NNN] Concise title

Record type: <Defect or risk | Improvement or alternative | Feature decision | Positive pattern>
ID category: <PREFIX>
Primary component: <stable logical subsystem or workflow>
Identity statement: <stable root cause, design limitation, decision basis, or preserved invariant>
Fingerprint: sha256:<64 lowercase hexadecimal characters>
Status: Active
```

`ID category` must match the ID prefix. `Fingerprint` must match the deterministic value for the four identity fields.

# Derived references

- `# 5. Top Findings` contains concise rows pointing to active IDs. It must not duplicate full evidence or recommendations.
- Sections 6, 7, 8, and 18 contain the full canonical records for their respective record types.
- Other summaries cite canonical IDs and add only scope-specific synthesis.
- `# 14. Prioritized Roadmap` references active IDs. Retired IDs may appear only in the registry, historical validation notes, or explicit supersession references.
- If a report section has no supported records, state that clearly with the coverage and evidence basis; do not insert placeholder or generic recommendations.
