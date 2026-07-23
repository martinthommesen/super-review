#!/usr/bin/env python3
"""Validate a Super Review FINDINGS.md report.

The validator is dependency-free and intentionally strict. It checks Markdown
structure outside fenced code, canonical record schemas and values, deterministic
fingerprints, the identifier registry, protected human blocks, report metadata,
and summary/roadmap cross-reference invariants.
"""

from __future__ import annotations

import argparse
import errno
import importlib.util
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Iterable

MAX_REPORT_BYTES = 64 * 1024 * 1024


def _load_sibling(module_name: str, filename: str) -> ModuleType:
    """Load a sibling module by trusted script path, including under Python -I."""
    script_dir = Path(__file__).resolve(strict=True).parent
    leaf = script_dir / filename
    try:
        info = os.lstat(leaf)
    except OSError as exc:
        raise RuntimeError(
            f"cannot inspect bundled sibling module {leaf}: {exc}"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise RuntimeError(f"unsafe bundled sibling module: {leaf}")
    sibling = leaf.resolve(strict=True)
    if sibling.parent != script_dir:
        raise RuntimeError(f"bundled sibling escapes script directory: {sibling}")
    spec = importlib.util.spec_from_file_location(module_name, sibling)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load bundled sibling module: {sibling}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_FINGERPRINT = _load_sibling(
    "_super_review_finding_fingerprint", "finding_fingerprint.py"
)
Identity = _FINGERPRINT.Identity
compute_fingerprint = _FINGERPRINT.compute_fingerprint

EXPECTED_SECTIONS = [
    "Executive Summary",
    "Repository and System Overview",
    "Coverage Ledger",
    "Architecture and Data-Flow Map",
    "Top Findings",
    "Detailed Findings",
    "Better and Different Ways to Implement the System",
    "Feature Portfolio Recommendations",
    "Testing and Validation Gaps",
    "Security and Privacy Summary",
    "Performance, Reliability, and Operations Summary",
    "Dependency, Build, Deployment, and Supply-Chain Summary",
    "Documentation and Developer-Experience Summary",
    "Prioritized Roadmap",
    "Suggested Implementation Sequence",
    "Validation Performed",
    "Open Questions and Missing Evidence",
    "Positive Patterns Worth Preserving",
]

FEATURE_SUBSECTIONS = [
    "8.1 Add",
    "8.2 Improve",
    "8.3 Simplify",
    "8.4 Merge",
    "8.5 Replace",
    "8.6 Deprecate",
    "8.7 Remove",
    "8.8 Keep",
    "8.9 Experiment or Investigate",
]
ROADMAP_SUBSECTIONS = ["Now", "Next", "Later", "Investigate", "Do Not Pursue"]
TYPE_TO_SECTION = {
    "Defect or risk": 6,
    "Improvement or alternative": 7,
    "Feature decision": 8,
    "Positive pattern": 18,
}
TYPE_PREFIXES = {
    "Defect or risk": {
        "COR",
        "SEC",
        "DAT",
        "ARC",
        "REL",
        "PER",
        "API",
        "TST",
        "OPS",
        "MNT",
        "UX",
        "DOC",
        "DX",
    },
    "Improvement or alternative": {"IMP", "ALT"},
    "Feature decision": {"FEAT", "REM"},
    "Positive pattern": {"POS"},
}
ALL_PREFIXES = set().union(*TYPE_PREFIXES.values())
ID_RE = re.compile(r"\b(?:" + "|".join(sorted(ALL_PREFIXES)) + r")-\d{3,}\b")
ID_FULL_RE = re.compile(r"^(?P<prefix>[A-Z]{2,5})-(?P<number>\d{3,})$")
FINGERPRINT_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
DIGEST_OR_MISSING_RE = re.compile(r"^(?:MISSING|sha256:[0-9a-f]{64})$")
RECORD_HEADING_RE = re.compile(r"^## \[(?P<id>[A-Z]{2,5}-\d{3,})\] (?P<title>\S.*)$")
SECTION_RE = re.compile(r"^# (?P<number>\d+)\. (?P<title>.+?)\s*$")
HUMAN_START_RE = re.compile(
    r'^<!-- SUPER-REVIEW:HUMAN-START id="(?P<id>[a-z0-9][a-z0-9._-]{0,63})" -->$'
)
HUMAN_END_RE = re.compile(
    r'^<!-- SUPER-REVIEW:HUMAN-END id="(?P<id>[a-z0-9][a-z0-9._-]{0,63})" -->$'
)
FIELD_RE = re.compile(r"^(?P<label>[A-Za-z][A-Za-z0-9 /-]*):\s*(?P<value>.*)$")

COMMON_FIELDS = {
    "Record type",
    "ID category",
    "Primary component",
    "Identity statement",
    "Fingerprint",
    "Status",
}
DEFECT_FIELDS = COMMON_FIELDS | {
    "Classification",
    "Severity or priority",
    "Confidence",
    "Affected components",
    "Evidence",
    "Current behavior",
    "Expected or preferred behavior",
    "Trigger or scenario",
    "Impact",
    "Reach",
    "Root cause",
    "Why existing tests did not catch it",
    "Minimal reproduction",
    "Recommended action",
    "Alternative approaches",
    "Preferred option",
    "Implementation outline",
    "Compatibility and migration",
    "Validation",
    "Effort",
    "Risk of the proposed change",
    "Dependencies",
    "Open questions",
}
SECURITY_FIELDS = {
    "Threat scenario",
    "Attacker prerequisites",
    "Affected assets",
    "Exploit path",
    "Existing mitigations",
    "Missing mitigations",
    "Defense-in-depth improvement",
    "Disclosure sensitivity",
}
IMPROVEMENT_FIELDS = COMMON_FIELDS | {
    "Classification",
    "Severity or priority",
    "Confidence",
    "Affected components",
    "Evidence",
    "Current approach",
    "Why it appears to exist",
    "What it does well",
    "Actual limitations",
    "Essential versus accidental complexity",
    "Triggering context or scale",
    "Recommendation",
    "Expected benefit",
    "Implementation outline",
    "Compatibility and migration",
    "Validation",
    "Effort",
    "Risk of the proposed change",
    "Dependencies",
    "Open questions",
}
FEATURE_FIELDS = COMMON_FIELDS | {
    "Decision",
    "Priority",
    "Confidence",
    "Feature or capability",
    "Target actor",
    "Problem or opportunity",
    "Repository evidence",
    "Current workaround",
    "Consequence of doing nothing",
    "Proposed behavior",
    "Why this is better",
    "Minimal viable scope",
    "Non-goals",
    "User or operator workflow",
    "Required permissions",
    "Data-model changes",
    "API changes",
    "UI changes",
    "Background-processing changes",
    "Security implications",
    "Privacy implications",
    "Operational impact",
    "Compatibility impact",
    "Known consumers",
    "Possible hidden or external consumers",
    "Usage evidence available",
    "Usage evidence missing",
    "Maintenance burden",
    "Overlap with other features",
    "Alternatives considered",
    "Dependencies",
    "Implementation touchpoints",
    "Test strategy",
    "Migration strategy",
    "Rollout or deprecation plan",
    "Rollback strategy",
    "Data-retention implications",
    "Success indicators",
    "Reconsideration or removal criteria",
    "Final deletion criteria",
    "Effort",
    "Risks",
}
POSITIVE_FIELDS = COMMON_FIELDS | {
    "Classification",
    "Severity or priority",
    "Confidence",
    "Affected components",
    "Evidence",
    "Why it is valuable",
    "Why the current design is appropriate",
    "Invariants to preserve",
    "Tests and controls that protect it",
    "Risks of changing it",
    "Reuse opportunities",
    "Scope limits",
}
REQUIRED_FIELDS = {
    "Defect or risk": DEFECT_FIELDS,
    "Improvement or alternative": IMPROVEMENT_FIELDS,
    "Feature decision": FEATURE_FIELDS,
    "Positive pattern": POSITIVE_FIELDS,
}

OPTION_FIELDS = {
    "### Option A — Keep and harden": {
        "Minimal changes",
        "Benefits",
        "Costs",
        "Risks",
        "Expected lifetime",
        "Correct-use conditions",
    },
    "### Option B — Incremental redesign": {
        "Structural change",
        "Benefits",
        "Costs",
        "Migration steps",
        "Compatibility considerations",
        "Testing requirements",
        "Rollback strategy",
    },
    "### Option C — Alternative approach": {
        "Alternative design",
        "Benefits",
        "Costs",
        "New risks",
        "Operational consequences",
        "Team-skill implications",
        "Dependency implications",
        "Migration complexity",
    },
    "### Option D — Clean-slate ideal, when useful": {
        "Ideal design",
        "Incrementally useful parts",
        "Parts not worth pursuing",
        "Rewrite judgment",
    },
}
OPTION_LOCAL_FIELDS = set().union(*OPTION_FIELDS.values())

SEVERITY_VALUES = {
    "Defect or risk": {"Critical", "High", "Medium", "Low", "Informational"},
    "Improvement or alternative": {
        "Now",
        "Next",
        "Later",
        "Investigate",
        "Do not pursue",
    },
    "Feature decision": {"Now", "Next", "Later", "Investigate", "Do not pursue"},
    "Positive pattern": {"Informational"},
}
CONFIDENCE_VALUES = {
    "Defect or risk": {"Confirmed", "High", "Medium", "Low", "Hypothesis"},
    "Improvement or alternative": {"Confirmed", "High", "Medium", "Low", "Hypothesis"},
    "Feature decision": {
        "Confirmed",
        "High",
        "Medium",
        "Low",
        "Requires product validation",
    },
    "Positive pattern": {"Confirmed", "High", "Medium", "Low"},
}
FEATURE_DECISIONS = {
    "Add",
    "Improve",
    "Simplify",
    "Merge",
    "Replace",
    "Deprecate",
    "Remove",
    "Keep",
    "Experiment",
    "Investigate",
}
FEATURE_DECISION_SUBSECTIONS = {
    "Add": "8.1 Add",
    "Improve": "8.2 Improve",
    "Simplify": "8.3 Simplify",
    "Merge": "8.4 Merge",
    "Replace": "8.5 Replace",
    "Deprecate": "8.6 Deprecate",
    "Remove": "8.7 Remove",
    "Keep": "8.8 Keep",
    "Experiment": "8.9 Experiment or Investigate",
    "Investigate": "8.9 Experiment or Investigate",
}
FEATURE_DECISION_FIELDS = {
    "Improve": {
        "Current workflow",
        "Friction or risk",
        "Behavior preserved",
        "Behavior changed",
        "Potential downside",
        "Validation required",
    },
    "Simplify": {
        "Current workflow",
        "Friction or risk",
        "Behavior preserved",
        "Behavior changed",
        "Potential downside",
        "Validation required",
    },
    "Merge": {
        "Features involved",
        "Shared purpose",
        "Meaningful differences",
        "Differences retained as modes or options",
        "Proposed unified model",
        "Documentation migration",
        "Deprecation sequence",
    },
    "Replace": {
        "Existing feature",
        "Replacement behavior",
        "Why improvement alone is insufficient",
        "Compatibility period",
        "Data conversion",
        "User communication requirements",
    },
    "Deprecate": {
        "Concrete removal evidence",
        "Security or reliability risk",
        "Consequence of removal",
        "Required telemetry or validation before removal",
        "Compatibility window",
        "Deprecation notice strategy",
    },
    "Remove": {
        "Concrete removal evidence",
        "Security or reliability risk",
        "Consequence of removal",
        "Required telemetry or validation before removal",
        "Compatibility window",
        "Deprecation notice strategy",
    },
    "Keep": {
        "Preservation rationale",
        "Invariants to preserve",
        "Tests that protect it",
        "Future-refactor constraints",
    },
    "Experiment": {
        "Experiment hypothesis",
        "Minimal experiment",
        "Expected signal",
        "Guardrail indicators",
        "Failure or stop conditions",
        "Data required",
        "Experimental-code isolation",
        "Feature-flag owner",
        "Expiration or review date",
        "Cleanup plan",
    },
    "Investigate": {"Evidence-gathering plan", "Decision threshold"},
}
ALL_FEATURE_SPECIFIC_FIELDS = set().union(*FEATURE_DECISION_FIELDS.values())
ALL_KNOWN_FIELDS = (
    DEFECT_FIELDS
    | SECURITY_FIELDS
    | IMPROVEMENT_FIELDS
    | FEATURE_FIELDS
    | POSITIVE_FIELDS
    | OPTION_LOCAL_FIELDS
    | ALL_FEATURE_SPECIFIC_FIELDS
)
ALLOWED_RETIRED_STATUSES = {"resolved", "superseded", "consolidated", "invalidated"}

CLASSIFICATION_VALUES = {
    "Defect or risk": {
        "Confirmed defect",
        "Probable defect",
        "Security weakness",
        "Reliability risk",
        "Performance risk",
        "Data-integrity risk",
        "Architectural risk",
        "Maintainability concern",
        "Product or UX concern",
        "Documentation issue",
        "Testing gap",
        "Operational gap",
    },
    "Improvement or alternative": {
        "Improvement",
        "Alternative implementation opportunity",
        "Architectural alternative",
        "Optional optimization",
        "Workflow simplification",
    },
    "Positive pattern": {"Positive pattern worth preserving"},
}

PRIORITY_TO_ROADMAP = {
    "Now": "Now",
    "Next": "Next",
    "Later": "Later",
    "Investigate": "Investigate",
    "Do not pursue": "Do Not Pursue",
}

EFFORT_VALUES = {"Small", "Medium", "Large", "Program-level"}
CHANGE_RISK_VALUES = {"Low", "Medium", "High"}
REVIEW_MODES = {
    "REVIEW ONLY",
    "REVIEW AND PROPOSE PATCHES",
    "REVIEW AND IMPLEMENT APPROVED FIXES",
    "REVIEW AND IMPLEMENT ALL HIGH-CONFIDENCE FIXES",
}
REPORT_METADATA_LABELS = [
    "Canonical root",
    "Reviewed branch and revision",
    "Starting repository state",
    "Ending repository state",
    "Review time",
    "Review mode",
    "Starting FINDINGS.md SHA-256",
    "Existing report revalidated",
    "Completion status",
    "Material limitations",
]

FENCE_OPEN_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
ANGLE_TOKEN_RE = re.compile(r"<(?P<token>[^>\n]{1,240})>")
BRACKET_PLACEHOLDER_RE = re.compile(
    r"\[(?:OPTIONAL|REQUIRED|CHOOSE ONE|INSERT|DESCRIBE|EXPLAIN|TODO|TBD)(?:[^\]]*)\]",
    re.IGNORECASE,
)
PLACEHOLDER_LITERALS = (
    "FULL_HEX_DIGEST",
    "PREFIX-NNN",
    "<digest-or-MISSING>",
    "<candidate-path>",
    "<canonical-root>",
    "<skill-root>",
)
PLACEHOLDER_WORDS = {
    "value",
    "name",
    "path",
    "mode",
    "digest",
    "description",
    "reason",
    "evidence",
    "component",
    "workflow",
    "title",
    "record prefix",
}


@dataclass(frozen=True)
class HumanBlock:
    block_id: str
    start_line: int
    end_line: int
    raw: str


@dataclass(frozen=True)
class FieldValue:
    label: str
    value: str
    start_line: int


@dataclass
class Record:
    record_id: str
    title: str
    start_line: int
    end_line: int
    section_number: int
    subsection: str | None
    fields: dict[str, str]
    field_lines: dict[str, int]
    field_occurrences: dict[str, list[FieldValue]]
    structural_body: str
    content_body: str


@dataclass
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _line_error(line: int, message: str) -> str:
    return f"line {line}: {message}"


def _ranges_overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] <= right[1] and right[0] <= left[1]


def _find_fenced_ranges(lines: list[str]) -> tuple[list[tuple[int, int]], list[str]]:
    ranges: list[tuple[int, int]] = []
    errors: list[str] = []
    open_char: str | None = None
    open_length = 0
    open_line = 0

    for index, line in enumerate(lines, start=1):
        if open_char is None:
            match = FENCE_OPEN_RE.fullmatch(line)
            if match:
                fence = match.group("fence")
                open_char = fence[0]
                open_length = len(fence)
                open_line = index
            continue

        if re.fullmatch(rf" {{0,3}}{re.escape(open_char)}{{{open_length},}}\s*", line):
            ranges.append((open_line, index))
            open_char = None
            open_length = 0
            open_line = 0

    if open_char is not None:
        ranges.append((open_line, len(lines)))
        errors.append(_line_error(open_line, "fenced code block is not closed"))
    return ranges, errors


def _line_set(ranges: Iterable[tuple[int, int]]) -> set[int]:
    result: set[int] = set()
    for start, end in ranges:
        result.update(range(start, end + 1))
    return result


def _find_human_blocks(
    lines: list[str], ignored_lines: set[int]
) -> tuple[list[HumanBlock], list[str]]:
    blocks: list[HumanBlock] = []
    errors: list[str] = []
    open_id: str | None = None
    open_line = 0
    seen: set[str] = set()

    for index, line in enumerate(lines, start=1):
        if index in ignored_lines:
            continue
        start_match = HUMAN_START_RE.fullmatch(line)
        end_match = HUMAN_END_RE.fullmatch(line)
        if start_match:
            block_id = start_match.group("id")
            if open_id is not None:
                errors.append(
                    _line_error(
                        index, f"nested human block {block_id!r} inside {open_id!r}"
                    )
                )
                continue
            if block_id in seen:
                errors.append(
                    _line_error(index, f"duplicate human block id {block_id!r}")
                )
            open_id = block_id
            open_line = index
            seen.add(block_id)
        elif end_match:
            block_id = end_match.group("id")
            if open_id is None:
                errors.append(
                    _line_error(index, f"human block end {block_id!r} has no start")
                )
                continue
            if block_id != open_id:
                errors.append(
                    _line_error(
                        index,
                        f"human block end {block_id!r} does not match open block {open_id!r}",
                    )
                )
                continue
            raw = "\n".join(lines[open_line - 1 : index])
            blocks.append(HumanBlock(block_id, open_line, index, raw))
            open_id = None
            open_line = 0

    if open_id is not None:
        errors.append(_line_error(open_line, f"human block {open_id!r} is not closed"))
    return blocks, errors


def extract_human_blocks(text: str) -> dict[str, str]:
    """Return protected blocks by ID, raising ValueError on malformed input."""
    lines = text.splitlines()
    fence_ranges, fence_errors = _find_fenced_ranges(lines)
    if fence_errors:
        raise ValueError("; ".join(fence_errors))
    blocks, errors = _find_human_blocks(lines, _line_set(fence_ranges))
    if errors:
        raise ValueError("; ".join(errors))
    return {block.block_id: block.raw for block in blocks}


def _extract_registry(
    lines: list[str], ignored_lines: set[int]
) -> tuple[dict | None, tuple[int, int] | None, list[str]]:
    starts = [
        i
        for i, line in enumerate(lines, start=1)
        if i not in ignored_lines and line == "<!-- SUPER-REVIEW-REGISTRY"
    ]
    errors: list[str] = []
    if len(starts) != 1:
        errors.append(
            f"expected exactly one SUPER-REVIEW-REGISTRY block, found {len(starts)}"
        )
        return None, None, errors
    start = starts[0]
    end = None
    for i in range(start + 1, len(lines) + 1):
        if i not in ignored_lines and lines[i - 1] == "-->":
            end = i
            break
    if end is None:
        errors.append(_line_error(start, "SUPER-REVIEW-REGISTRY block is not closed"))
        return None, None, errors

    json_text = "\n".join(lines[start : end - 1])
    try:
        registry = json.loads(json_text)
    except json.JSONDecodeError as exc:
        errors.append(
            _line_error(start + exc.lineno, f"invalid registry JSON: {exc.msg}")
        )
        return None, (start, end), errors
    if not isinstance(registry, dict):
        errors.append(_line_error(start, "registry JSON must be an object"))
        return None, (start, end), errors
    return registry, (start, end), errors


def _validate_registry(
    registry: dict | None,
) -> tuple[set[str], set[str], dict[str, str], list[str]]:
    errors: list[str] = []
    if registry is None:
        return set(), set(), {}, errors

    required_keys = {"schema_version", "active", "retired", "next_sequence"}
    missing = required_keys - set(registry)
    extra = set(registry) - required_keys
    if missing:
        errors.append(f"registry missing keys: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"registry has unsupported keys: {', '.join(sorted(extra))}")
    if registry.get("schema_version") != 2:
        errors.append("registry schema_version must be 2")

    active = registry.get("active", {})
    retired = registry.get("retired", {})
    next_sequence = registry.get("next_sequence", {})
    if not isinstance(active, dict):
        errors.append("registry active must be an object")
        active = {}
    if not isinstance(retired, dict):
        errors.append("registry retired must be an object")
        retired = {}
    if not isinstance(next_sequence, dict):
        errors.append("registry next_sequence must be an object")
        next_sequence = {}

    active_ids: set[str] = set()
    retired_ids: set[str] = set()
    active_fingerprints: dict[str, str] = {}
    all_fingerprints: dict[str, str] = {}
    max_numbers: dict[str, int] = {}
    replacement_map: dict[str, list[str]] = {}

    for record_id, fingerprint in active.items():
        match = ID_FULL_RE.fullmatch(record_id) if isinstance(record_id, str) else None
        if not match or match.group("prefix") not in ALL_PREFIXES:
            errors.append(f"registry active contains invalid ID {record_id!r}")
            continue
        if not isinstance(fingerprint, str) or not FINGERPRINT_RE.fullmatch(
            fingerprint
        ):
            errors.append(f"registry active {record_id} has invalid fingerprint")
            continue
        active_ids.add(record_id)
        active_fingerprints[record_id] = fingerprint
        other = all_fingerprints.get(fingerprint)
        if other and other != record_id:
            errors.append(
                f"fingerprint {fingerprint} is assigned to both {other} and {record_id}"
            )
        all_fingerprints[fingerprint] = record_id
        prefix = match.group("prefix")
        max_numbers[prefix] = max(
            max_numbers.get(prefix, 0), int(match.group("number"))
        )

    for record_id, entry in retired.items():
        match = ID_FULL_RE.fullmatch(record_id) if isinstance(record_id, str) else None
        if not match or match.group("prefix") not in ALL_PREFIXES:
            errors.append(f"registry retired contains invalid ID {record_id!r}")
            continue
        if not isinstance(entry, dict):
            errors.append(f"registry retired {record_id} must be an object")
            continue
        required = {"fingerprint", "status", "replacement_ids"}
        missing_entry = required - set(entry)
        extra_entry = set(entry) - required
        if missing_entry:
            errors.append(
                f"registry retired {record_id} missing: {', '.join(sorted(missing_entry))}"
            )
        if extra_entry:
            errors.append(
                f"registry retired {record_id} has unsupported keys: {', '.join(sorted(map(str, extra_entry)))}"
            )
        fingerprint = entry.get("fingerprint")
        status = entry.get("status")
        replacements = entry.get("replacement_ids")
        if not isinstance(fingerprint, str) or not FINGERPRINT_RE.fullmatch(
            fingerprint
        ):
            errors.append(f"registry retired {record_id} has invalid fingerprint")
        else:
            other = all_fingerprints.get(fingerprint)
            if other and other != record_id:
                errors.append(
                    f"fingerprint {fingerprint} is assigned to both {other} and {record_id}"
                )
            all_fingerprints[fingerprint] = record_id
        if status not in ALLOWED_RETIRED_STATUSES:
            errors.append(
                f"registry retired {record_id} status must be one of: "
                f"{', '.join(sorted(ALLOWED_RETIRED_STATUSES))}"
            )
        if not isinstance(replacements, list) or not all(
            isinstance(item, str) for item in replacements
        ):
            errors.append(
                f"registry retired {record_id} replacement_ids must be a string array"
            )
        else:
            replacement_map[record_id] = replacements
        retired_ids.add(record_id)
        prefix = match.group("prefix")
        max_numbers[prefix] = max(
            max_numbers.get(prefix, 0), int(match.group("number"))
        )

    overlap = active_ids & retired_ids
    if overlap:
        errors.append(
            f"IDs cannot be both active and retired: {', '.join(sorted(overlap))}"
        )

    known_ids = active_ids | retired_ids
    for record_id, replacements in replacement_map.items():
        for replacement in replacements:
            if replacement == record_id:
                errors.append(f"registry retired {record_id} cannot replace itself")
            if replacement not in known_ids:
                errors.append(
                    f"registry retired {record_id} references unknown replacement ID {replacement}"
                )

    for prefix, max_number in max_numbers.items():
        value = next_sequence.get(prefix)
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"registry next_sequence.{prefix} must be an integer")
        elif value <= max_number:
            errors.append(
                f"registry next_sequence.{prefix} must be greater than allocated value {max_number}"
            )
    for prefix, value in next_sequence.items():
        if prefix not in ALL_PREFIXES:
            errors.append(
                f"registry next_sequence contains unsupported prefix {prefix!r}"
            )
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            errors.append(f"registry next_sequence.{prefix} must be a positive integer")

    return active_ids, retired_ids, active_fingerprints, errors


def _masked_lines(lines: list[str], ranges: Iterable[tuple[int, int]]) -> list[str]:
    masked = list(lines)
    for start, end in ranges:
        for index in range(start - 1, min(end, len(masked))):
            masked[index] = ""
    return masked


def _parse_sections(lines: list[str]) -> tuple[dict[int, tuple[int, int]], list[str]]:
    matches: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines, start=1):
        match = SECTION_RE.fullmatch(line)
        if match:
            matches.append((index, int(match.group("number")), match.group("title")))

    errors: list[str] = []
    if len(matches) != len(EXPECTED_SECTIONS):
        errors.append(
            f"expected {len(EXPECTED_SECTIONS)} numbered report sections, found {len(matches)}"
        )

    section_ranges: dict[int, tuple[int, int]] = {}
    for expected_number, expected_title in enumerate(EXPECTED_SECTIONS, start=1):
        candidates = [item for item in matches if item[1] == expected_number]
        if len(candidates) != 1:
            errors.append(
                f"expected exactly one '# {expected_number}. {expected_title}' heading, "
                f"found {len(candidates)}"
            )
            continue
        line_number, _, actual_title = candidates[0]
        if actual_title != expected_title:
            errors.append(
                _line_error(
                    line_number,
                    f"section {expected_number} title must be {expected_title!r}, "
                    f"found {actual_title!r}",
                )
            )

    ordered = sorted(matches)
    if [number for _, number, _ in ordered] != list(
        range(1, len(EXPECTED_SECTIONS) + 1)
    ):
        errors.append(
            "numbered report sections must appear exactly once in order from 1 through 18"
        )

    for position, (line_number, number, _title) in enumerate(ordered):
        end = (
            ordered[position + 1][0] - 1 if position + 1 < len(ordered) else len(lines)
        )
        section_ranges[number] = (line_number, end)
    return section_ranges, errors


def _parse_field_occurrences(
    structural_lines: list[str], content_lines: list[str], absolute_first_line: int
) -> dict[str, list[FieldValue]]:
    occurrences: dict[str, list[FieldValue]] = {}
    current_label: str | None = None
    current_line = 0
    current_parts: list[str] = []

    def finish() -> None:
        nonlocal current_label, current_line, current_parts
        if current_label is None:
            return
        value = "\n".join(current_parts).strip()
        occurrences.setdefault(current_label, []).append(
            FieldValue(current_label, value, current_line)
        )
        current_label = None
        current_line = 0
        current_parts = []

    for offset, structural in enumerate(structural_lines):
        content = content_lines[offset]
        if structural.startswith("### "):
            finish()
            continue
        match = FIELD_RE.fullmatch(structural)
        if match:
            finish()
            current_label = match.group("label")
            current_line = absolute_first_line + offset
            inline = match.group("value").strip()
            current_parts = [inline] if inline else []
            continue
        if current_label is not None:
            current_parts.append(content)
    finish()
    return occurrences


def _parse_records(
    structural_lines: list[str],
    content_lines: list[str],
    section_ranges: dict[int, tuple[int, int]],
) -> tuple[list[Record], list[str]]:
    headings: list[tuple[int, re.Match[str]]] = []
    for index, line in enumerate(structural_lines, start=1):
        match = RECORD_HEADING_RE.fullmatch(line)
        if match:
            headings.append((index, match))

    records: list[Record] = []
    errors: list[str] = []
    seen_ids: set[str] = set()

    def section_for_line(line_number: int) -> int:
        for number, (start, end) in section_ranges.items():
            if start <= line_number <= end:
                return number
        return 0

    for index, match in headings:
        record_id = match.group("id")
        title = match.group("title").strip()
        if record_id in seen_ids:
            errors.append(
                _line_error(
                    index, f"duplicate canonical record heading for {record_id}"
                )
            )
        seen_ids.add(record_id)

        end = len(structural_lines)
        for candidate in range(index + 1, len(structural_lines) + 1):
            line = structural_lines[candidate - 1]
            if line.startswith("# ") or line.startswith("## "):
                end = candidate - 1
                break

        section_number = section_for_line(index)
        subsection: str | None = None
        if section_number in section_ranges:
            section_start, _ = section_ranges[section_number]
            for candidate in range(index - 1, section_start, -1):
                prior = structural_lines[candidate - 1]
                if prior.startswith("## ") and not RECORD_HEADING_RE.fullmatch(prior):
                    subsection = prior[3:].strip()
                    break

        structural_body_lines = structural_lines[index:end]
        content_body_lines = content_lines[index:end]
        occurrences = _parse_field_occurrences(
            structural_body_lines, content_body_lines, index + 1
        )
        fields = {label: values[0].value for label, values in occurrences.items()}
        field_lines = {
            label: values[0].start_line for label, values in occurrences.items()
        }
        records.append(
            Record(
                record_id=record_id,
                title=title,
                start_line=index,
                end_line=end,
                section_number=section_number,
                subsection=subsection,
                fields=fields,
                field_lines=field_lines,
                field_occurrences=occurrences,
                structural_body="\n".join(structural_body_lines),
                content_body="\n".join(content_body_lines),
            )
        )
    return records, errors


def _section_text(
    lines: list[str], section_ranges: dict[int, tuple[int, int]], number: int
) -> str:
    if number not in section_ranges:
        return ""
    start, end = section_ranges[number]
    return "\n".join(lines[start - 1 : end])


def _validate_subsections(
    section_text: str, expected: list[str], section_number: int
) -> list[str]:
    errors: list[str] = []
    found: list[str] = []
    for line in section_text.splitlines():
        if line.startswith("## ") and not RECORD_HEADING_RE.fullmatch(line):
            found.append(line[3:].strip())
    filtered = [item for item in found if item in expected]
    if filtered != expected:
        errors.append(
            f"section {section_number} must contain required subsections once and in order: "
            f"{', '.join(expected)}"
        )
    for item in expected:
        count = found.count(item)
        if count != 1:
            errors.append(
                f"section {section_number} expected subsection {item!r} once, found {count}"
            )
    return errors


def _meaningful(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    semantic = re.sub(r"[\s#>*_`~|\-+.\d:;,[\](){}]", "", stripped)
    return bool(semantic)


def _choice_with_optional_explanation(value: str, choices: set[str]) -> bool:
    return any(
        value == choice
        or value.startswith(choice + " —")
        or value.startswith(choice + " -")
        or value.startswith(choice + ":")
        or value.startswith(choice + " (")
        for choice in choices
    )


def _placeholder_in_line(line: str) -> str | None:
    for literal in PLACEHOLDER_LITERALS:
        if literal in line:
            return literal
    bracket = BRACKET_PLACEHOLDER_RE.search(line)
    if bracket:
        return bracket.group(0)
    for match in ANGLE_TOKEN_RE.finditer(line):
        token = match.group("token").strip()
        lowered = token.casefold()
        if lowered.startswith(("http://", "https://", "mailto:")):
            continue
        if re.fullmatch(
            r"/?(?:details|summary|br|sub|sup|kbd|code|em|strong)", lowered
        ):
            continue
        if len(token) == 1 and token.isalpha() and token.isupper():
            continue
        if (
            any(character.isspace() for character in token)
            or "|" in token
            or lowered in PLACEHOLDER_WORDS
            or lowered.startswith(
                (
                    "what ",
                    "describe ",
                    "explain ",
                    "insert ",
                    "exact ",
                    "stable ",
                    "specific ",
                    "current ",
                    "smallest ",
                    "absolute ",
                )
            )
        ):
            return match.group(0)
    return None


def _validate_option_sections(record: Record) -> list[str]:
    errors: list[str] = []
    options = {
        "### Option A — Keep and harden": {
            "Minimal changes",
            "Benefits",
            "Costs",
            "Risks",
            "Expected lifetime",
            "Correct-use conditions",
        },
        "### Option B — Incremental redesign": {
            "Structural change",
            "Benefits",
            "Costs",
            "Migration steps",
            "Compatibility considerations",
            "Testing requirements",
            "Rollback strategy",
        },
        "### Option C — Alternative approach": {
            "Alternative design",
            "Benefits",
            "Costs",
            "New risks",
            "Operational consequences",
            "Team-skill implications",
            "Dependency implications",
            "Migration complexity",
        },
        "### Option D — Clean-slate ideal, when useful": {
            "Ideal design",
            "Incrementally useful parts",
            "Parts not worth pursuing",
            "Rewrite judgment",
        },
    }
    structural_lines = record.structural_body.splitlines()
    content_lines = record.content_body.splitlines()
    positions: list[tuple[int, str]] = []
    for index, line in enumerate(structural_lines):
        if line in options:
            positions.append((index, line))
    if [heading for _, heading in positions] != list(options):
        errors.append(
            _line_error(
                record.start_line,
                f"{record.record_id} must contain Options A-D exactly once and in order",
            )
        )
        return errors

    for position_index, (start, heading) in enumerate(positions):
        end = (
            positions[position_index + 1][0]
            if position_index + 1 < len(positions)
            else len(structural_lines)
        )
        occurrences = _parse_field_occurrences(
            structural_lines[start + 1 : end],
            content_lines[start + 1 : end],
            record.start_line + start + 2,
        )
        for label in sorted(options[heading]):
            values = occurrences.get(label, [])
            if not values:
                errors.append(
                    _line_error(
                        record.start_line + start + 1,
                        f"{record.record_id} {heading[4:]} missing field {label!r}",
                    )
                )
            elif len(values) != 1:
                errors.append(
                    _line_error(
                        values[1].start_line,
                        f"{record.record_id} {heading[4:]} duplicates field {label!r}",
                    )
                )
            elif not _meaningful(values[0].value):
                errors.append(
                    _line_error(
                        values[0].start_line,
                        f"{record.record_id} {heading[4:]} field {label!r} must not be empty",
                    )
                )
    return errors


def _validate_records(
    records: list[Record], active_ids: set[str], active_fingerprints: dict[str, str]
) -> tuple[dict[str, Record], list[str]]:
    errors: list[str] = []
    by_id: dict[str, Record] = {}
    fingerprints_seen: dict[str, str] = {}

    for record in records:
        by_id[record.record_id] = record
        match = ID_FULL_RE.fullmatch(record.record_id)
        if not match or match.group("prefix") not in ALL_PREFIXES:
            errors.append(
                _line_error(
                    record.start_line, f"invalid canonical record ID {record.record_id}"
                )
            )
            continue
        prefix = match.group("prefix")

        record_type = record.fields.get("Record type", "")
        if record_type not in TYPE_TO_SECTION:
            errors.append(
                _line_error(
                    record.start_line,
                    f"{record.record_id} has invalid or missing Record type {record_type!r}",
                )
            )
            continue

        expected_section = TYPE_TO_SECTION[record_type]
        if record.section_number != expected_section:
            errors.append(
                _line_error(
                    record.start_line,
                    f"{record.record_id} type {record_type!r} must be in section "
                    f"{expected_section}, found section {record.section_number}",
                )
            )
        if prefix not in TYPE_PREFIXES[record_type]:
            errors.append(
                _line_error(
                    record.start_line,
                    f"{record.record_id} prefix is not valid for record type {record_type!r}",
                )
            )

        category = record.fields.get("ID category", "")
        if category != prefix:
            errors.append(
                _line_error(
                    record.start_line,
                    f"{record.record_id} ID category must be {prefix!r}, found {category!r}",
                )
            )

        required_fields = set(REQUIRED_FIELDS[record_type])
        if prefix == "SEC":
            required_fields |= SECURITY_FIELDS

        decision = ""
        if record_type == "Feature decision":
            decision = record.fields.get("Decision", "")
            if decision not in FEATURE_DECISIONS:
                errors.append(
                    _line_error(
                        record.field_lines.get("Decision", record.start_line),
                        f"{record.record_id} has invalid Decision {decision!r}",
                    )
                )
            else:
                required_fields |= FEATURE_DECISION_FIELDS.get(decision, set())
                expected_subsection = FEATURE_DECISION_SUBSECTIONS[decision]
                if record.subsection != expected_subsection:
                    errors.append(
                        _line_error(
                            record.start_line,
                            f"{record.record_id} decision {decision} must be under subsection "
                            f"{expected_subsection!r}, found {record.subsection!r}",
                        )
                    )
                if decision in {"Deprecate", "Remove"} and prefix != "REM":
                    errors.append(
                        _line_error(
                            record.start_line,
                            f"{record.record_id} decision {decision} must use REM prefix",
                        )
                    )
                if decision not in {"Deprecate", "Remove"} and prefix != "FEAT":
                    errors.append(
                        _line_error(
                            record.start_line,
                            f"{record.record_id} decision {decision} must use FEAT prefix",
                        )
                    )

        missing_fields = required_fields - set(record.field_occurrences)
        if missing_fields:
            errors.append(
                _line_error(
                    record.start_line,
                    f"{record.record_id} missing required fields: {', '.join(sorted(missing_fields))}",
                )
            )

        for label in sorted(required_fields & set(record.field_occurrences)):
            occurrences = record.field_occurrences[label]
            if len(occurrences) != 1:
                errors.append(
                    _line_error(
                        occurrences[1].start_line,
                        f"{record.record_id} required field {label!r} appears {len(occurrences)} times",
                    )
                )
            if not _meaningful(occurrences[0].value):
                errors.append(
                    _line_error(
                        occurrences[0].start_line,
                        f"{record.record_id} field {label!r} must not be empty",
                    )
                )

        if record.fields.get("Status") != "Active":
            errors.append(
                _line_error(
                    record.field_lines.get("Status", record.start_line),
                    f"{record.record_id} Status must be 'Active'",
                )
            )

        if record_type in CLASSIFICATION_VALUES:
            classification = record.fields.get("Classification", "")
            if classification not in CLASSIFICATION_VALUES[record_type]:
                errors.append(
                    _line_error(
                        record.field_lines.get("Classification", record.start_line),
                        f"{record.record_id} invalid Classification {classification!r} for {record_type}",
                    )
                )

        priority_label = (
            "Priority" if record_type == "Feature decision" else "Severity or priority"
        )
        priority = record.fields.get(priority_label, "")
        if priority not in SEVERITY_VALUES[record_type]:
            errors.append(
                _line_error(
                    record.field_lines.get(priority_label, record.start_line),
                    f"{record.record_id} invalid {priority_label} {priority!r} for {record_type}",
                )
            )
        confidence = record.fields.get("Confidence", "")
        if confidence not in CONFIDENCE_VALUES[record_type]:
            errors.append(
                _line_error(
                    record.field_lines.get("Confidence", record.start_line),
                    f"{record.record_id} invalid Confidence {confidence!r} for {record_type}",
                )
            )

        effort = record.fields.get("Effort")
        if effort is not None and not _choice_with_optional_explanation(
            effort, EFFORT_VALUES
        ):
            errors.append(
                _line_error(
                    record.field_lines.get("Effort", record.start_line),
                    f"{record.record_id} invalid Effort {effort!r}",
                )
            )
        change_risk = record.fields.get("Risk of the proposed change")
        if change_risk is not None and not _choice_with_optional_explanation(
            change_risk, CHANGE_RISK_VALUES
        ):
            errors.append(
                _line_error(
                    record.field_lines.get(
                        "Risk of the proposed change", record.start_line
                    ),
                    f"{record.record_id} invalid Risk of the proposed change {change_risk!r}",
                )
            )

        fingerprint = record.fields.get("Fingerprint", "")
        if not FINGERPRINT_RE.fullmatch(fingerprint):
            errors.append(
                _line_error(
                    record.field_lines.get("Fingerprint", record.start_line),
                    f"{record.record_id} has invalid Fingerprint",
                )
            )
        else:
            try:
                expected = compute_fingerprint(
                    Identity(
                        record_type=record_type,
                        category=category,
                        primary_component=record.fields.get("Primary component", ""),
                        identity_statement=record.fields.get("Identity statement", ""),
                    )
                )
            except ValueError as exc:
                errors.append(
                    _line_error(
                        record.start_line,
                        f"{record.record_id} identity is invalid: {exc}",
                    )
                )
            else:
                if fingerprint != expected:
                    errors.append(
                        _line_error(
                            record.field_lines.get("Fingerprint", record.start_line),
                            f"{record.record_id} fingerprint does not match deterministic "
                            f"identity; expected {expected}",
                        )
                    )
            other = fingerprints_seen.get(fingerprint)
            if other and other != record.record_id:
                errors.append(
                    _line_error(
                        record.start_line,
                        f"fingerprint {fingerprint} is used by both {other} and {record.record_id}",
                    )
                )
            fingerprints_seen[fingerprint] = record.record_id

        registry_fingerprint = active_fingerprints.get(record.record_id)
        if registry_fingerprint != fingerprint:
            errors.append(
                _line_error(
                    record.start_line,
                    f"{record.record_id} registry fingerprint does not match canonical record",
                )
            )

        if record_type == "Improvement or alternative":
            errors.extend(_validate_option_sections(record))

    record_ids = set(by_id)
    missing_records = active_ids - record_ids
    extra_records = record_ids - active_ids
    if missing_records:
        errors.append(
            f"registry active IDs without canonical records: {', '.join(sorted(missing_records))}"
        )
    if extra_records:
        errors.append(
            f"canonical records absent from registry active: {', '.join(sorted(extra_records))}"
        )
    return by_id, errors


def _validate_cross_references(
    lines: list[str],
    section_ranges: dict[int, tuple[int, int]],
    active_ids: set[str],
    retired_ids: set[str],
    records: dict[str, Record],
) -> list[str]:
    errors: list[str] = []
    text = "\n".join(lines)
    known = active_ids | retired_ids
    referenced = set(ID_RE.findall(text))
    unknown = referenced - known
    if unknown:
        errors.append(f"unknown ID references: {', '.join(sorted(unknown))}")

    top_ids = set(ID_RE.findall(_section_text(lines, section_ranges, 5)))
    roadmap_text = _section_text(lines, section_ranges, 14)
    roadmap_ids = set(ID_RE.findall(roadmap_text))
    roadmap_locations: dict[str, set[str]] = {}
    current_subsection: str | None = None
    for line in roadmap_text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            current_subsection = heading if heading in ROADMAP_SUBSECTIONS else None
            continue
        if current_subsection is not None:
            for record_id in ID_RE.findall(line):
                roadmap_locations.setdefault(record_id, set()).add(current_subsection)

    for record_id, locations in roadmap_locations.items():
        if len(locations) > 1:
            errors.append(
                f"roadmap ID {record_id} appears in multiple priority groups: "
                f"{', '.join(sorted(locations))}"
            )

    retired_in_top = top_ids & retired_ids
    retired_in_roadmap = roadmap_ids & retired_ids
    if retired_in_top:
        errors.append(
            f"retired IDs cannot appear in Top Findings: {', '.join(sorted(retired_in_top))}"
        )
    if retired_in_roadmap:
        errors.append(
            f"retired IDs cannot appear as roadmap work: {', '.join(sorted(retired_in_roadmap))}"
        )
    if top_ids - active_ids:
        errors.append(
            f"Top Findings references non-active IDs: {', '.join(sorted(top_ids - active_ids))}"
        )
    if roadmap_ids - active_ids:
        errors.append(
            f"Roadmap references non-active IDs: {', '.join(sorted(roadmap_ids - active_ids))}"
        )

    for record_id, record in records.items():
        record_type = record.fields.get("Record type")
        priority = record.fields.get(
            "Priority" if record_type == "Feature decision" else "Severity or priority"
        )
        if record_type == "Defect or risk" and priority in {"Critical", "High"}:
            if record_id not in top_ids:
                errors.append(
                    f"{record_id} is {priority} but is missing from Top Findings"
                )
            if record_id not in roadmap_ids:
                errors.append(
                    f"{record_id} is {priority} but is missing from the Prioritized Roadmap"
                )
            elif roadmap_locations.get(record_id) != {"Now"}:
                errors.append(
                    f"{record_id} is {priority} and must appear under roadmap subsection 'Now'"
                )
        if record_type in {"Improvement or alternative", "Feature decision"}:
            expected_heading = PRIORITY_TO_ROADMAP.get(priority or "")
            if record_id not in roadmap_ids:
                errors.append(
                    f"{record_id} is an active {record_type.lower()} but is missing from the "
                    "Prioritized Roadmap"
                )
            elif expected_heading is None or roadmap_locations.get(record_id) != {
                expected_heading
            }:
                errors.append(
                    f"{record_id} priority is {priority!r} but roadmap placement is "
                    f"{sorted(roadmap_locations.get(record_id, set()))}"
                )
    return errors


def _summary_metadata_values(section_lines: list[str]) -> dict[str, str]:
    """First-occurrence value for each Executive Summary metadata label.

    This is the single reader of report metadata values, shared by structural
    validation and by :func:`stated_canonical_root`, so the two never drift.
    """
    values: dict[str, str] = {}
    for line in section_lines:
        for label in REPORT_METADATA_LABELS:
            prefix = label + ":"
            if line.startswith(prefix) and label not in values:
                values[label] = line[len(prefix) :].strip()
    return values


def _validate_report_metadata(section_one: str) -> list[str]:
    errors: list[str] = []
    section_lines = section_one.splitlines()
    values = _summary_metadata_values(section_lines)
    lines_by_label: dict[str, list[int]] = {
        label: [] for label in REPORT_METADATA_LABELS
    }

    heading_index = next(
        (
            index
            for index, line in enumerate(section_lines)
            if line == "# 1. Executive Summary"
        ),
        None,
    )
    if heading_index is not None:
        nonblank_after_heading = [
            (index + 1, line)
            for index, line in enumerate(
                section_lines[heading_index + 1 :], start=heading_index + 1
            )
            if line.strip()
        ]
        for position, label in enumerate(REPORT_METADATA_LABELS):
            if position >= len(nonblank_after_heading):
                errors.append(
                    f"Executive Summary must begin with metadata label {label!r} in required order"
                )
                break
            _, line = nonblank_after_heading[position]
            if not line.startswith(label + ":"):
                errors.append(
                    f"Executive Summary must begin with metadata label {label!r} in required order"
                )
                break

    for index, line in enumerate(section_lines, start=1):
        for label in REPORT_METADATA_LABELS:
            if line.startswith(label + ":"):
                lines_by_label[label].append(index)

    for label in REPORT_METADATA_LABELS:
        count = len(lines_by_label[label])
        if count != 1:
            errors.append(
                f"Executive Summary metadata label {label!r} must appear exactly once, found {count}"
            )
            continue
        value = values.get(label, "")
        if not _meaningful(value):
            errors.append(f"Executive Summary metadata {label!r} must not be empty")
        placeholder = _placeholder_in_line(value)
        if placeholder:
            errors.append(
                f"Executive Summary metadata {label!r} contains unresolved placeholder {placeholder}"
            )

    review_time = values.get("Review time", "")
    if review_time:
        try:
            parsed = datetime.fromisoformat(review_time.replace("Z", "+00:00"))
        except ValueError:
            errors.append(
                "Executive Summary Review time must be a valid ISO 8601 timestamp"
            )
        else:
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                errors.append("Executive Summary Review time must include a timezone")

    canonical_root = values.get("Canonical root", "")
    if canonical_root and not os.path.isabs(canonical_root):
        errors.append("Executive Summary Canonical root must be an absolute path")

    review_mode = values.get("Review mode", "")
    if review_mode and review_mode not in REVIEW_MODES:
        errors.append(f"Executive Summary Review mode is invalid: {review_mode!r}")

    starting_digest = values.get("Starting FINDINGS.md SHA-256", "")
    if (
        starting_digest
        and starting_digest != "MISSING"
        and not re.fullmatch(r"sha256:[0-9a-f]{64}", starting_digest)
    ):
        errors.append(
            "Executive Summary Starting FINDINGS.md SHA-256 must be MISSING or sha256:<64 lowercase hex>"
        )

    revalidated = values.get("Existing report revalidated", "")
    if revalidated and not (
        revalidated == "Yes"
        or revalidated == "No — file did not exist"
        or revalidated.startswith("Partial — ")
    ):
        errors.append(
            "Executive Summary Existing report revalidated must be 'Yes', "
            "'No — file did not exist', or 'Partial — <specific limitation>'"
        )

    completion = values.get("Completion status", "")
    if completion and completion not in {"Complete", "Partial", "Blocked"}:
        errors.append(
            "Executive Summary Completion status must be Complete, Partial, or Blocked"
        )
    limitations = values.get("Material limitations", "")
    if completion in {"Partial", "Blocked"} and limitations == "None":
        errors.append(
            "Executive Summary Material limitations must explain a Partial or Blocked review"
        )
    return errors


def validate_text(text: str) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if "\x00" in text:
        return ValidationResult(["report contains a NUL byte"], warnings)
    if not text.endswith("\n"):
        warnings.append("report should end with a newline")

    lines = text.splitlines()
    fence_ranges, fence_errors = _find_fenced_ranges(lines)
    errors.extend(fence_errors)
    fenced_lines = _line_set(fence_ranges)

    human_blocks, human_errors = _find_human_blocks(lines, fenced_lines)
    errors.extend(human_errors)
    human_ranges = [(block.start_line, block.end_line) for block in human_blocks]

    registry_starts_in_human_blocks = [
        index
        for index, line in enumerate(lines, start=1)
        if line == "<!-- SUPER-REVIEW-REGISTRY"
        and any(start <= index <= end for start, end in human_ranges)
    ]
    for index in registry_starts_in_human_blocks:
        errors.append(
            _line_error(
                index,
                "SUPER-REVIEW-REGISTRY must not be inside a protected human block",
            )
        )

    registry, registry_range, registry_errors = _extract_registry(lines, fenced_lines)
    errors.extend(registry_errors)
    if registry_range:
        for block in human_blocks:
            if _ranges_overlap(registry_range, (block.start_line, block.end_line)):
                errors.append(
                    _line_error(
                        registry_range[0],
                        "SUPER-REVIEW-REGISTRY must not be inside a protected human block",
                    )
                )
        first_nonblank = next(
            (index for index, line in enumerate(lines, start=1) if line.strip()), None
        )
        if first_nonblank != registry_range[0]:
            errors.append(
                "SUPER-REVIEW-REGISTRY must be the first nonblank report content"
            )

    active_ids, retired_ids, active_fingerprints, registry_validation_errors = (
        _validate_registry(registry)
    )
    errors.extend(registry_validation_errors)

    structural_ranges = [*fence_ranges, *human_ranges]
    content_ranges = list(human_ranges)
    if registry_range:
        structural_ranges.append(registry_range)
        content_ranges.append(registry_range)
    structural = _masked_lines(lines, structural_ranges)
    content = _masked_lines(lines, content_ranges)

    section_ranges, section_errors = _parse_sections(structural)
    errors.extend(section_errors)
    if (
        registry_range
        and 1 in section_ranges
        and registry_range[0] > section_ranges[1][0]
    ):
        errors.append("SUPER-REVIEW-REGISTRY must appear before # 1. Executive Summary")

    if section_ranges:
        errors.extend(
            _validate_subsections(
                _section_text(structural, section_ranges, 8), FEATURE_SUBSECTIONS, 8
            )
        )
        errors.extend(
            _validate_subsections(
                _section_text(structural, section_ranges, 14), ROADMAP_SUBSECTIONS, 14
            )
        )
        errors.extend(
            _validate_report_metadata(_section_text(structural, section_ranges, 1))
        )

    records, record_parse_errors = _parse_records(structural, content, section_ranges)
    errors.extend(record_parse_errors)
    records_by_id, record_errors = _validate_records(
        records, active_ids, active_fingerprints
    )
    errors.extend(record_errors)
    errors.extend(
        _validate_cross_references(
            structural, section_ranges, active_ids, retired_ids, records_by_id
        )
    )

    for index, line in enumerate(structural, start=1):
        placeholder = _placeholder_in_line(line)
        if placeholder:
            errors.append(
                _line_error(index, f"unresolved template placeholder {placeholder}")
            )
        stripped = line.strip()
        if re.fullmatch(r"\[[A-Z][A-Z0-9 _/-]*\]", stripped):
            errors.append(
                _line_error(index, f"unresolved template placeholder {stripped}")
            )

    return ValidationResult(errors, warnings)


def validate_bytes(data: bytes, *, source: str = "<bytes>") -> ValidationResult:
    if len(data) > MAX_REPORT_BYTES:
        return ValidationResult(
            [f"{source} exceeds {MAX_REPORT_BYTES} byte safety limit"], []
        )
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return ValidationResult([f"{source} is not valid UTF-8: {exc}"], [])
    return validate_text(text)


def _read_path_no_follow(path: Path) -> tuple[bytes | None, str | None]:
    try:
        before = os.lstat(path)
    except OSError as exc:
        return None, f"cannot inspect {path}: {exc}"
    if stat.S_ISLNK(before.st_mode):
        return None, f"refusing symbolic-link report path: {path}"
    if not stat.S_ISREG(before.st_mode):
        return None, f"report path must be a regular file: {path}"
    if before.st_size > MAX_REPORT_BYTES:
        return None, f"{path} exceeds {MAX_REPORT_BYTES} byte safety limit"

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        if exc.errno in {errno.ELOOP, getattr(errno, "EMLINK", -1)}:
            return None, f"refusing symbolic-link report path: {path}"
        return None, f"cannot open {path}: {exc}"
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            return None, f"report path must be a regular file: {path}"
        if getattr(before, "st_ino", 0) and (
            before.st_ino != opened.st_ino or before.st_dev != opened.st_dev
        ):
            return None, f"report path changed between inspection and open: {path}"
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, MAX_REPORT_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_REPORT_BYTES:
                return None, f"{path} exceeds {MAX_REPORT_BYTES} byte safety limit"
        after = os.fstat(fd)
        if any(
            getattr(opened, name, None) != getattr(after, name, None)
            for name in ("st_size", "st_mtime_ns", "st_ctime_ns")
        ):
            return None, f"report path changed while being read: {path}"
        try:
            after_path = os.lstat(path)
        except OSError as exc:
            return None, f"report path changed while being read {path}: {exc}"
        if stat.S_ISLNK(after_path.st_mode) or not stat.S_ISREG(after_path.st_mode):
            return None, f"report path changed while being read: {path}"
        if getattr(opened, "st_ino", 0) and (
            opened.st_ino != after_path.st_ino or opened.st_dev != after_path.st_dev
        ):
            return None, f"report path changed while being read: {path}"
        return b"".join(chunks), None
    finally:
        os.close(fd)


def stated_canonical_root(text: str) -> str | None:
    """Return the report's stated ``Canonical root`` metadata value, if present.

    Isolates the structurally parsed Executive Summary and reads its metadata
    through :func:`_summary_metadata_values`, so fenced examples and protected
    human annotations cannot spoof the repository identity.
    """
    lines = text.splitlines()
    fence_ranges, fence_errors = _find_fenced_ranges(lines)
    if fence_errors:
        return None
    human_blocks, human_errors = _find_human_blocks(lines, _line_set(fence_ranges))
    if human_errors:
        return None
    structural = _masked_lines(
        lines,
        [
            *fence_ranges,
            *((block.start_line, block.end_line) for block in human_blocks),
        ],
    )
    section_ranges, section_errors = _parse_sections(structural)
    if section_errors or 1 not in section_ranges:
        return None
    start, end = section_ranges[1]
    return _summary_metadata_values(structural[start - 1 : end]).get("Canonical root")


def canonical_root_error(
    text: str, expected_root: os.PathLike[str] | str
) -> str | None:
    """Report why the stated canonical root does not match ``expected_root``.

    Returns ``None`` when the report states an absolute ``Canonical root`` that
    resolves to the same location the report is being committed to or verified
    against. This is the location check that keeps a report generated for one
    repository from being written into, or accepted as, another repository's
    ``FINDINGS.md``.
    """
    stated = stated_canonical_root(text)
    if not stated:
        return "report is missing the 'Canonical root' metadata value"
    if not os.path.isabs(stated):
        return f"stated Canonical root {stated!r} must be an absolute path"
    expected_real = os.path.realpath(os.fspath(expected_root))
    stated_real = os.path.realpath(os.path.expanduser(stated))
    if stated_real != expected_real:
        return (
            f"stated Canonical root {stated!r} does not match the review destination "
            f"{expected_real} (it resolves to {stated_real})"
        )
    return None


def validate_path(
    path: Path, canonical_root: os.PathLike[str] | str | None = None
) -> ValidationResult:
    canonical = path.expanduser()
    if not canonical.is_absolute():
        canonical = Path.cwd() / canonical
    data, error = _read_path_no_follow(canonical)
    if error:
        return ValidationResult([error], [])
    assert data is not None
    result = validate_bytes(data, source=str(canonical))
    if canonical_root is not None:
        # Tie three things together: the file must physically be
        # <canonical-root>/FINDINGS.md, and its stated Canonical root must name
        # that same repository. Checking only the metadata would accept a report
        # that lives in a different repository but merely claims this one.
        expected_file = os.path.join(
            os.path.realpath(os.fspath(canonical_root)), "FINDINGS.md"
        )
        actual_file = os.path.realpath(canonical)
        if actual_file != expected_file:
            result.errors.append(
                f"report path {actual_file} is not the canonical {expected_file}"
            )
        root_error = canonical_root_error(
            data.decode("utf-8", errors="replace"), canonical_root
        )
        if root_error:
            result.errors.append(root_error)
    return result


def minimal_valid_report() -> str:
    registry = {
        "schema_version": 2,
        "active": {},
        "retired": {},
        "next_sequence": {},
    }
    section_bodies = {
        1: "\n".join(
            [
                "Canonical root: /tmp/repo",
                "Reviewed branch and revision: main at abc123",
                "Starting repository state: abc123 clean",
                "Ending repository state: abc123 clean",
                "Review time: 2026-07-22T12:00:00+02:00",
                "Review mode: REVIEW ONLY",
                "Starting FINDINGS.md SHA-256: MISSING",
                "Existing report revalidated: No — file did not exist",
                "Completion status: Complete",
                "Material limitations: None",
            ]
        ),
        8: "\n\n".join(
            f"## {name}\n\nNo current canonical records supported — test fixture."
            for name in FEATURE_SUBSECTIONS
        ),
        14: "\n\n".join(
            f"## {name}\n\nNo current canonical records supported — test fixture."
            for name in ROADMAP_SUBSECTIONS
        ),
    }
    chunks = [
        "<!-- SUPER-REVIEW-REGISTRY",
        json.dumps(registry, indent=2, sort_keys=True),
        "-->",
        "",
    ]
    for number, title in enumerate(EXPECTED_SECTIONS, start=1):
        chunks.append(f"# {number}. {title}")
        chunks.append("")
        chunks.append(
            section_bodies.get(
                number, "No current canonical records supported — test fixture."
            )
        )
        chunks.append("")
    return "\n".join(chunks).rstrip() + "\n"


def run_self_test() -> int:
    valid = minimal_valid_report()
    result = validate_text(valid)
    if not result.ok:
        print("self-test failure: valid fixture rejected", file=sys.stderr)
        for error in result.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    invalid = valid.replace('"schema_version": 2', '"schema_version": 1', 1)
    result = validate_text(invalid)
    if result.ok or not any("schema_version" in error for error in result.errors):
        print("self-test failure: invalid registry fixture accepted", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as temp_dir:
        report = Path(temp_dir) / "FINDINGS.md"
        report.write_text(valid, encoding="utf-8")
        if not validate_path(report).ok:
            print(
                "self-test failure: path validation rejected valid fixture",
                file=sys.stderr,
            )
            return 1

    print("validate_findings.py self-test passed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a Super Review FINDINGS.md report."
    )
    parser.add_argument(
        "path", nargs="?", type=Path, help="candidate or committed FINDINGS.md"
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable validation output"
    )
    parser.add_argument("--quiet", action="store_true", help="suppress success output")
    parser.add_argument(
        "--canonical-root",
        type=Path,
        default=None,
        help="also require the report's stated Canonical root to resolve to this directory",
    )
    parser.add_argument(
        "--self-test", action="store_true", help="run built-in smoke tests"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        return run_self_test()
    if args.path is None:
        print("error: path is required unless --self-test is used", file=sys.stderr)
        return 2

    result = validate_path(args.path, canonical_root=args.canonical_root)
    if args.json:
        print(
            json.dumps(
                {"ok": result.ok, "errors": result.errors, "warnings": result.warnings},
                indent=2,
                sort_keys=True,
            )
        )
    else:
        for warning in result.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        if result.errors:
            print(
                f"FINDINGS validation failed with {len(result.errors)} error(s):",
                file=sys.stderr,
            )
            for error in result.errors:
                print(f"  - {error}", file=sys.stderr)
        elif not args.quiet:
            print(f"FINDINGS validation passed: {args.path}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
