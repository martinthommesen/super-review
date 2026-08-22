from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import finding_fingerprint as ff
import validate_findings as vf

DEFAULT_CANONICAL_ROOT = "//example.invalid/super-review/repo"


@dataclass(frozen=True)
class CanonicalRecord:
    record_id: str
    record_type: str
    fingerprint: str
    section: int
    body: str
    roadmap: str | None = None
    feature_subsection: str | None = None
    top_finding: bool = False


def _field(label: str, value: str) -> str:
    if "\n" in value or value.startswith("-") or value.startswith("1."):
        return f"{label}:\n{value}"
    return f"{label}: {value}"


def _render_fields(items: list[tuple[str, str]]) -> str:
    return "\n\n".join(_field(label, value) for label, value in items)


def make_defect(
    *,
    record_id: str = "COR-001",
    classification: str = "Confirmed defect",
    severity: str = "Medium",
    impact: str = "Incorrect requests can be accepted and produce inconsistent state.",
) -> CanonicalRecord:
    category = record_id.split("-", 1)[0]
    record_type = "Defect or risk"
    component = "core/request-boundary"
    statement = "request trust-boundary validation is incomplete"
    fingerprint = ff.compute_fingerprint(
        ff.Identity(record_type, category, component, statement)
    )
    fields = [
        ("Record type", record_type),
        ("ID category", category),
        ("Primary component", component),
        ("Identity statement", statement),
        ("Fingerprint", fingerprint),
        ("Status", "Active"),
        ("Classification", classification),
        ("Severity or priority", severity),
        ("Confidence", "Confirmed"),
        (
            "Affected components",
            "Request parser, domain service, and persisted records.",
        ),
        (
            "Evidence",
            "- `src/request.py:10-24`: validation omits the state invariant.",
        ),
        (
            "Current behavior",
            "The request reaches the domain service without the required invariant.",
        ),
        (
            "Expected or preferred behavior",
            "Reject the invalid state before any side effect.",
        ),
        (
            "Trigger or scenario",
            "A caller supplies a syntactically valid but semantically invalid state.",
        ),
        ("Impact", impact),
        ("Reach", "All callers of the affected request path."),
        ("Root cause", statement),
        (
            "Why existing tests did not catch it",
            "Boundary fixtures cover syntax but not the domain invariant.",
        ),
        (
            "Minimal reproduction",
            "Construct the invalid state and invoke the request handler.",
        ),
        (
            "Recommended action",
            "Validate the invariant at the trust boundary and retain domain enforcement.",
        ),
        (
            "Alternative approaches",
            "1. Boundary and domain validation.\n2. Domain-only validation with typed construction.\n3. Not applicable: keeping the gap is unsafe.",
        ),
        (
            "Preferred option",
            "Boundary and domain validation because it fails early and preserves defense in depth.",
        ),
        (
            "Implementation outline",
            "Update parser validation, typed construction, callers, and regression fixtures.",
        ),
        (
            "Compatibility and migration",
            "No public shape change; invalid requests begin failing explicitly.",
        ),
        (
            "Validation",
            "Unit and integration regression tests for invalid and valid states.",
        ),
        ("Effort", "Small: one boundary and focused tests."),
        (
            "Risk of the proposed change",
            "Low: behavior changes only for invalid input.",
        ),
        ("Dependencies", "None."),
        (
            "Open questions",
            "Not applicable: intended invariant is established by schema and tests.",
        ),
    ]
    body = f"## [{record_id}] Boundary validation permits an invalid state\n\n{_render_fields(fields)}"
    top = severity in {"Critical", "High"}
    return CanonicalRecord(
        record_id, record_type, fingerprint, 6, body, "Now" if top else None, None, top
    )


def make_improvement(
    *, record_id: str = "IMP-001", priority: str = "Do not pursue"
) -> CanonicalRecord:
    category = record_id.split("-", 1)[0]
    record_type = "Improvement or alternative"
    component = "core/pipeline"
    statement = "pipeline stages duplicate normalization responsibilities"
    fingerprint = ff.compute_fingerprint(
        ff.Identity(record_type, category, component, statement)
    )
    pre_options = [
        ("Record type", record_type),
        ("ID category", category),
        ("Primary component", component),
        ("Identity statement", statement),
        ("Fingerprint", fingerprint),
        ("Status", "Active"),
        ("Classification", "Workflow simplification"),
        ("Severity or priority", priority),
        ("Confidence", "High"),
        ("Affected components", "Pipeline stages and their callers."),
        (
            "Evidence",
            "- `src/pipeline.py:20-80`: normalization is repeated across stages.",
        ),
        ("Current approach", "Each stage normalizes the same input independently."),
        (
            "Why it appears to exist",
            "Stages were added incrementally and retained local ownership.",
        ),
        ("What it does well", "Each stage remains understandable in isolation."),
        (
            "Actual limitations",
            "Repeated normalization can drift and adds maintenance work.",
        ),
        (
            "Essential versus accidental complexity",
            "Stage boundaries are essential; repeated normalization is accidental.",
        ),
        (
            "Triggering context or scale",
            "The change becomes worthwhile when another stage needs the same normalization.",
        ),
    ]
    options = """
### Option A — Keep and harden

Minimal changes: Document one canonical algorithm and add parity tests.

Benefits: Lowest migration risk.

Costs: Duplication remains.

Risks: Implementations can still drift.

Expected lifetime: Appropriate while the pipeline remains small.

Correct-use conditions: Choose when no new stage requires the behavior.

### Option B — Incremental redesign

Structural change: Introduce one typed normalized input before stage dispatch.

Benefits: Removes drift while preserving stage boundaries.

Costs: Requires caller and fixture migration.

Migration steps: Add the type, migrate one stage at a time, then remove duplicate paths.

Compatibility considerations: Preserve external input and output contracts.

Testing requirements: Parity, failure-path, and integration tests.

Rollback strategy: Retain the old constructors until all stages are validated.

### Option C — Alternative approach

Alternative design: Use a shared stateless normalization function without a new type.

Benefits: Smaller code change.

Costs: Weaker invariant ownership.

New risks: Callers may bypass normalization.

Operational consequences: None beyond ordinary deployment validation.

Team-skill implications: No new specialist knowledge.

Dependency implications: No new dependency.

Migration complexity: Low.

### Option D — Clean-slate ideal, when useful

Ideal design: Parse once into a domain-valid value consumed by every stage.

Incrementally useful parts: The typed normalized input is useful now.

Parts not worth pursuing: A full pipeline rewrite is not justified.

Rewrite judgment: Incremental migration is sufficient.
""".strip()
    post_options = [
        (
            "Recommendation",
            "Do not pursue now; retain the incremental option for the stated trigger.",
        ),
        (
            "Expected benefit",
            "Avoids premature churn while preserving a bounded future path.",
        ),
        (
            "Implementation outline",
            "No current code change; keep parity tests and revisit at the trigger.",
        ),
        (
            "Compatibility and migration",
            "Not applicable: no change is recommended now.",
        ),
        ("Validation", "Reassess when another stage duplicates normalization."),
        ("Effort", "Small: investigation only."),
        (
            "Risk of the proposed change",
            "Low: the current recommendation is to defer.",
        ),
        ("Dependencies", "Evidence of another consumer or material drift."),
        ("Open questions", "Not applicable: the decision threshold is explicit."),
    ]
    body = (
        f"## [{record_id}] Consolidate pipeline normalization only when the trigger is met\n\n"
        f"{_render_fields(pre_options)}\n\n{options}\n\n{_render_fields(post_options)}"
    )
    return CanonicalRecord(
        record_id,
        record_type,
        fingerprint,
        7,
        body,
        vf.PRIORITY_TO_ROADMAP[priority],
    )


def make_feature(
    *, record_id: str = "FEAT-001", decision: str = "Keep", priority: str = "Later"
) -> CanonicalRecord:
    category = record_id.split("-", 1)[0]
    record_type = "Feature decision"
    component = "product/audit-history"
    statement = "audit history provides required operator traceability"
    fingerprint = ff.compute_fingerprint(
        ff.Identity(record_type, category, component, statement)
    )
    fields = [
        ("Record type", record_type),
        ("ID category", category),
        ("Primary component", component),
        ("Identity statement", statement),
        ("Fingerprint", fingerprint),
        ("Status", "Active"),
        ("Decision", decision),
        ("Priority", priority),
        ("Confidence", "High"),
        ("Feature or capability", "Audit history"),
        ("Target actor", "Operator and support engineer."),
        (
            "Problem or opportunity",
            "The capability provides traceability for privileged changes.",
        ),
        (
            "Repository evidence",
            "Routes, persistence, authorization tests, and operator documentation.",
        ),
        ("Current workaround", "Not applicable: the capability already exists."),
        ("Consequence of doing nothing", "The current traceability remains available."),
        (
            "Proposed behavior",
            "Preserve the current capability and its authorization boundary.",
        ),
        (
            "Why this is better",
            "The implementation is bounded and already covers the evidenced workflow.",
        ),
        ("Minimal viable scope", "Keep behavior and strengthen regression coverage."),
        ("Non-goals", "No analytics expansion or new retention policy."),
        (
            "User or operator workflow",
            "Authorized operators search and inspect immutable entries.",
        ),
        ("Required permissions", "Existing least-privilege operator permission."),
        ("Data-model changes", "Not applicable: preserve the existing schema."),
        ("API changes", "Not applicable: preserve the existing contract."),
        ("UI changes", "Not applicable: preserve the existing interface."),
        (
            "Background-processing changes",
            "Not applicable: no background processing is involved.",
        ),
        (
            "Security implications",
            "Preserve authorization, integrity, and sensitive-field redaction.",
        ),
        ("Privacy implications", "Preserve minimization and retention controls."),
        ("Operational impact", "Retain existing monitoring and support workflow."),
        ("Compatibility impact", "No compatibility change."),
        ("Known consumers", "Operator UI and support workflow."),
        (
            "Possible hidden or external consumers",
            "No public API; verify internal exports before refactoring.",
        ),
        ("Usage evidence available", "Reachable routes, tests, and operator docs."),
        (
            "Usage evidence missing",
            "Production frequency is unavailable and not required for preservation.",
        ),
        ("Maintenance burden", "Bounded to one service and one interface."),
        ("Overlap with other features", "No material overlap established."),
        (
            "Alternatives considered",
            "1. Keep current design.\n2. Replace storage: unsupported.\n3. Remove: unsafe and unsupported.",
        ),
        ("Dependencies", "Existing authorization and retention controls."),
        (
            "Implementation touchpoints",
            "Authorization tests and audit-history service.",
        ),
        (
            "Test strategy",
            "Integration tests for permission, ordering, redaction, and retention.",
        ),
        ("Migration strategy", "Not applicable: no migration."),
        ("Rollout or deprecation plan", "Not applicable: preserve current behavior."),
        ("Rollback strategy", "Not applicable: no behavioral change."),
        ("Data-retention implications", "Preserve the established retention policy."),
        ("Success indicators", "Existing workflows and controls continue to pass."),
        (
            "Reconsideration or removal criteria",
            "Reconsider only with replacement traceability and consumer evidence.",
        ),
        ("Final deletion criteria", "Not applicable: keep decision."),
        ("Effort", "Small: regression coverage only."),
        ("Risks", "Accidental weakening during unrelated refactors."),
        (
            "Preservation rationale",
            "The feature is required for traceability and is proportionate.",
        ),
        (
            "Invariants to preserve",
            "Authorization, immutability, ordering, redaction, and retention.",
        ),
        (
            "Tests that protect it",
            "Authorization and integration tests; add retention coverage.",
        ),
        ("Future-refactor constraints", "Do not merge it with mutable activity feeds."),
    ]
    body = f"## [{record_id}] Preserve the bounded audit-history capability\n\n{_render_fields(fields)}"
    return CanonicalRecord(
        record_id,
        record_type,
        fingerprint,
        8,
        body,
        vf.PRIORITY_TO_ROADMAP[priority],
        vf.FEATURE_DECISION_SUBSECTIONS[decision],
    )


def make_positive(*, record_id: str = "POS-001") -> CanonicalRecord:
    """Build the positive-pattern fixture."""
    category = "POS"
    record_type = "Positive pattern"
    component = "security/authorization"
    statement = "authorization is centralized at the domain operation boundary"
    fingerprint = ff.compute_fingerprint(
        ff.Identity(record_type, category, component, statement)
    )
    fields = [
        ("Record type", record_type),
        ("ID category", category),
        ("Primary component", component),
        ("Identity statement", statement),
        ("Fingerprint", fingerprint),
        ("Status", "Active"),
        ("Classification", "Positive pattern worth preserving"),
        ("Severity or priority", "Informational"),
        ("Confidence", "High"),
        ("Affected components", "All entry points invoking the domain operation."),
        ("Evidence", "Shared domain authorization and cross-entry-point tests."),
        ("Why it is valuable", "It prevents policy drift across interfaces."),
        (
            "Why the current design is appropriate",
            "One operation owns the invariant without framework leakage.",
        ),
        (
            "Invariants to preserve",
            "Every entry point must invoke the same authorized operation.",
        ),
        (
            "Tests and controls that protect it",
            "Contract and authorization tests across entry points.",
        ),
        ("Risks of changing it", "Duplicated checks could diverge or be bypassed."),
        (
            "Reuse opportunities",
            "Apply to the adjacent privileged workflow after confirming equivalent policy.",
        ),
        ("Scope limits", "Do not centralize unrelated presentation validation."),
    ]
    body = f"## [{record_id}] Preserve centralized domain authorization\n\n{_render_fields(fields)}"
    return CanonicalRecord(record_id, record_type, fingerprint, 18, body)


def make_retired_entry(
    *,
    status: str = "resolved",
    replacement_ids: tuple[str, ...] = (),
    seed: str = "retired-fixture",
) -> dict:
    """Return a well-formed retired-registry entry with a seed-unique fingerprint."""
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return {
        "fingerprint": f"sha256:{digest}",
        "status": status,
        "replacement_ids": list(replacement_ids),
    }


def build_report(
    records: list[CanonicalRecord] | None = None,
    *,
    canonical_root: str = DEFAULT_CANONICAL_ROOT,
    retired: dict[str, dict] | None = None,
    starting_digest: str = "MISSING",
    revalidated: str = "No — file did not exist",
    completion: str = "Complete",
    material_limitations: str = "None",
) -> str:
    """Build a complete report fixture."""
    records = records or []
    retired = retired or {}
    active = {record.record_id: record.fingerprint for record in records}
    next_sequence: dict[str, int] = {}
    for record_id in [*active, *retired]:
        prefix, number = record_id.split("-", 1)
        next_sequence[prefix] = max(next_sequence.get(prefix, 1), int(number) + 1)
    registry = {
        "schema_version": 2,
        "active": active,
        "retired": retired,
        "next_sequence": next_sequence,
    }

    section_bodies: dict[int, str] = {
        1: "\n".join(
            [
                f"Canonical root: {canonical_root}",
                "Reviewed branch and revision: main at abc123",
                "Starting repository state: abc123 clean",
                "Ending repository state: abc123 clean",
                "Review time: 2026-07-22T12:00:00+02:00",
                "Review mode: REVIEW ONLY",
                f"Starting FINDINGS.md SHA-256: {starting_digest}",
                f"Existing report revalidated: {revalidated}",
                f"Completion status: {completion}",
                f"Material limitations: {material_limitations}",
            ]
        )
    }

    top = [record for record in records if record.top_finding]
    section_bodies[5] = (
        "\n".join(
            f"- {record.record_id}: {record.body.splitlines()[0][3:]}" for record in top
        )
        if top
        else "No current canonical records supported: no Critical or High records in fixture."
    )

    for section in (6, 7, 18):
        selected = [record.body for record in records if record.section == section]
        section_bodies[section] = (
            "\n\n".join(selected)
            if selected
            else "No current canonical records supported: test fixture."
        )

    feature_chunks: list[str] = []
    for subsection in vf.FEATURE_SUBSECTIONS:
        selected = [
            record.body
            for record in records
            if record.section == 8 and record.feature_subsection == subsection
        ]
        body = (
            "\n\n".join(selected)
            if selected
            else "No current canonical records supported: test fixture."
        )
        feature_chunks.append(f"## {subsection}\n\n{body}")
    section_bodies[8] = "\n\n".join(feature_chunks)

    roadmap_chunks: list[str] = []
    for subsection in vf.ROADMAP_SUBSECTIONS:
        selected = [record for record in records if record.roadmap == subsection]
        body = (
            "\n".join(
                f"- {record.record_id}: fixture roadmap item." for record in selected
            )
            if selected
            else "No current canonical records supported: test fixture."
        )
        roadmap_chunks.append(f"## {subsection}\n\n{body}")
    section_bodies[14] = "\n\n".join(roadmap_chunks)

    chunks = [
        "<!-- SUPER-REVIEW-REGISTRY",
        json.dumps(registry, indent=2, sort_keys=True),
        "-->",
        "",
    ]
    for number, title in enumerate(vf.EXPECTED_SECTIONS, start=1):
        chunks.extend(
            [
                f"# {number}. {title}",
                "",
                section_bodies.get(
                    number, "No current canonical records supported: test fixture."
                ),
                "",
            ]
        )
    return "\n".join(chunks).rstrip() + "\n"


def add_global_human_block(report: str, body: str = "Manual decision.\n") -> str:
    marker = "\n-->\n\n# 1. Executive Summary"
    block = (
        "\n-->\n\n"
        '<!-- SUPER-REVIEW:HUMAN-START id="global-decisions" -->\n'
        + body.rstrip("\n")
        + "\n"
        '<!-- SUPER-REVIEW:HUMAN-END id="global-decisions" -->\n\n'
        "# 1. Executive Summary"
    )
    if marker not in report:
        raise ValueError("report registry terminator not found")
    return report.replace(marker, block, 1)
