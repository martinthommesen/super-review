from __future__ import annotations

import contextlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import report_factory as rf
import validate_findings as vf

# Pin a symlink-resolved temp root (the default macOS TMPDIR is a symlink)
# so stated canonical roots match resolved review destinations.
tempfile.tempdir = str(Path(tempfile.gettempdir()).resolve())


class ValidateFindingsTests(unittest.TestCase):
    def assert_invalid_with(self, report: str, fragment: str) -> None:
        result = vf.validate_text(report)
        self.assertFalse(result.ok, result.errors)
        self.assertTrue(
            any(fragment in error for error in result.errors),
            f"expected {fragment!r} in errors: {result.errors}",
        )

    def test_minimal_report_is_valid(self) -> None:
        result = vf.validate_text(rf.build_report())
        self.assertTrue(result.ok, result.errors)

    def test_each_canonical_record_type_is_valid(self) -> None:
        report = rf.build_report(
            [
                rf.make_defect(),
                rf.make_improvement(priority="Do not pursue"),
                rf.make_feature(),
                rf.make_positive(),
            ]
        )
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_empty_required_metadata_is_rejected(self) -> None:
        report = rf.build_report().replace(
            f"Canonical root: {rf.DEFAULT_CANONICAL_ROOT}", "Canonical root:", 1
        )
        self.assert_invalid_with(report, "metadata 'Canonical root' must not be empty")

    def test_duplicate_required_metadata_is_rejected(self) -> None:
        report = rf.build_report().replace(
            f"Canonical root: {rf.DEFAULT_CANONICAL_ROOT}",
            f"Canonical root: {rf.DEFAULT_CANONICAL_ROOT}\n"
            "Canonical root: //other.invalid/super-review/repo",
            1,
        )
        self.assert_invalid_with(report, "must appear exactly once")

    def test_review_time_requires_timezone(self) -> None:
        report = rf.build_report().replace(
            "Review time: 2026-07-22T12:00:00+02:00",
            "Review time: 2026-07-22T12:00:00",
            1,
        )
        self.assert_invalid_with(report, "Review time must include a timezone")

    def test_arbitrary_classification_is_rejected(self) -> None:
        report = rf.build_report(
            [rf.make_defect(classification="Whatever sounds plausible")]
        )
        self.assert_invalid_with(report, "invalid Classification")

    def test_empty_mandatory_impact_is_rejected(self) -> None:
        report = rf.build_report([rf.make_defect(impact="")])
        self.assert_invalid_with(report, "field 'Impact' must not be empty")

    def test_unresolved_angle_placeholder_is_rejected(self) -> None:
        report = rf.build_report([rf.make_defect(impact="<What should be written>")])
        self.assert_invalid_with(report, "unresolved template placeholder")

    def test_do_not_pursue_maps_to_capitalized_roadmap_heading(self) -> None:
        report = rf.build_report([rf.make_improvement(priority="Do not pursue")])
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_headings_and_ids_inside_fenced_code_are_ignored(self) -> None:
        report = rf.build_report()
        fenced = """```markdown
# 99. Not a report section
# 1. Executive Summary
## [COR-999] Not a canonical record
Classification: Arbitrary
<What should be written>
```
"""
        report = report.replace(
            "# 2. Repository and System Overview\n\nNo current canonical records supported: test fixture.",
            "# 2. Repository and System Overview\n\n" + fenced,
            1,
        )
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_field_label_inside_fence_does_not_satisfy_required_field(self) -> None:
        report = rf.build_report([rf.make_defect()])
        report = report.replace(
            "Impact: Incorrect requests can be accepted and produce inconsistent state.",
            "```text\nImpact: fake value\n```",
            1,
        )
        self.assert_invalid_with(report, "missing required fields: Impact")

    def test_registry_inside_protected_human_block_is_rejected(self) -> None:
        report = rf.build_report()
        registry_end = report.index("-->\n") + len("-->\n")
        wrapped = (
            '<!-- SUPER-REVIEW:HUMAN-START id="registry-wrapper" -->\n'
            + report[:registry_end]
            + '<!-- SUPER-REVIEW:HUMAN-END id="registry-wrapper" -->\n'
            + report[registry_end:]
        )
        self.assert_invalid_with(
            wrapped, "SUPER-REVIEW-REGISTRY must not be inside a protected human block"
        )

    def test_human_markers_inside_fenced_code_are_ignored(self) -> None:
        report = rf.build_report()
        snippet = """```markdown
<!-- SUPER-REVIEW:HUMAN-START id="example" -->
<!-- SUPER-REVIEW:HUMAN-END id="example" -->
```
"""
        report = report.replace(
            "# 2. Repository and System Overview\n\nNo current canonical records supported: test fixture.",
            "# 2. Repository and System Overview\n\n" + snippet,
            1,
        )
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_backtick_info_fence_line_is_prose(self) -> None:
        report = rf.build_report().replace(
            "# 2. Repository and System Overview\n\nNo current canonical records supported: test fixture.",
            "# 2. Repository and System Overview\n\n```python`x\nprose after the non-fence line.",
            1,
        )
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_fence_marker_inside_annotation_is_protected_content(self) -> None:
        report = rf.add_global_human_block(
            rf.build_report(), "Decision.\n```\nrationale\n"
        )
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)
        blocks = vf.extract_human_blocks(report)
        self.assertIn("global-decisions", blocks)
        self.assertIn("```", blocks["global-decisions"])

    def test_exotic_line_separators_do_not_split_lines(self) -> None:
        report = rf.build_report().replace(
            "# 2. Repository and System Overview\n\nNo current canonical records supported: test fixture.",
            "# 2. Repository and System Overview\n\nprose\x0b```",
            1,
        )
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_close_fence_allows_only_space_and_tab(self) -> None:
        base = (
            "# 2. Repository and System Overview\n\n"
            "No current canonical records supported: test fixture."
        )
        good = rf.build_report().replace(
            base,
            "# 2. Repository and System Overview\n\n```text\nexample\n``` \t",
            1,
        )
        result = vf.validate_text(good)
        self.assertTrue(result.ok, result.errors)
        bad = rf.build_report().replace(
            base,
            "# 2. Repository and System Overview\n\n```text\nexample\n```\u00a0",
            1,
        )
        self.assert_invalid_with(bad, "fenced code block is not closed")

    def test_unclosed_fence_is_rejected(self) -> None:
        report = rf.build_report().replace(
            "# 18. Positive Patterns Worth Preserving",
            "```text\n# 18. Positive Patterns Worth Preserving",
            1,
        )
        self.assert_invalid_with(report, "fenced code block is not closed")

    def test_required_metadata_must_start_section_in_order(self) -> None:
        report = rf.build_report().replace(
            "# 1. Executive Summary\n\nCanonical root:",
            "# 1. Executive Summary\n\nPremature prose.\n\nCanonical root:",
            1,
        )
        self.assert_invalid_with(report, "must begin with metadata label")

    def test_literal_generic_angle_token_in_inline_code_is_allowed(self) -> None:
        report = rf.build_report(
            [
                rf.make_defect(
                    impact="The typed boundary uses `<T>` and remains concrete."
                )
            ]
        )
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_validate_path_rejects_symbolic_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            real = root / "real.md"
            link = root / "link.md"
            real.write_text(rf.build_report(), encoding="utf-8")
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            result = vf.validate_path(link)
            self.assertFalse(result.ok)
            self.assertTrue(
                any("symbolic-link" in error for error in result.errors),
                result.errors,
            )

    def test_validate_path_detects_replacement_during_read(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report = root / "FINDINGS.md"
            replacement = root / "replacement.md"
            report.write_text(rf.build_report(), encoding="utf-8")
            replacement.write_text("not a report\n", encoding="utf-8")
            original_read = vf.os.read
            replaced = False

            def read_then_replace(fd: int, size: int) -> bytes:
                nonlocal replaced
                chunk = original_read(fd, size)
                if not chunk and not replaced:
                    replaced = True
                    os.replace(replacement, report)
                return chunk

            with mock.patch.object(vf.os, "read", side_effect=read_then_replace):
                result = vf.validate_path(report)

            self.assertFalse(result.ok)
            self.assertTrue(
                any("changed while being read" in error for error in result.errors),
                result.errors,
            )

    def test_stated_canonical_root_reads_summary_metadata(self) -> None:
        report = rf.build_report(canonical_root=rf.DEFAULT_CANONICAL_ROOT)
        self.assertEqual(vf.stated_canonical_root(report), rf.DEFAULT_CANONICAL_ROOT)

    def test_canonical_root_error_accepts_matching_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = rf.build_report(canonical_root=temp_dir)
            self.assertIsNone(vf.canonical_root_error(report, temp_dir))

    def test_canonical_root_error_flags_mismatch(self) -> None:
        report = rf.build_report(canonical_root="//project.invalid/super-review/repo")
        with mock.patch.object(vf.os, "name", "nt"):
            message = vf.canonical_root_error(
                report, "//other.invalid/super-review/repo"
            )
        self.assertIsInstance(message, str)
        self.assertIn("does not match", message or "")

    def test_canonical_root_mismatch_does_not_resolve_untrusted_path(self) -> None:
        stated = "//attacker.invalid/share/repo"
        expected = "//trusted.invalid/share/repo"
        report = rf.build_report(canonical_root=stated)
        original_realpath = vf.os.path.realpath

        def guarded_realpath(value):
            if vf.os.fspath(value) == stated:
                raise AssertionError("report-controlled path was resolved")
            return original_realpath(value)

        with mock.patch.object(vf.os.path, "realpath", side_effect=guarded_realpath):
            message = vf.canonical_root_error(report, expected)
        self.assertIsInstance(message, str)
        self.assertIn("does not match", message or "")

    def test_canonical_root_error_rejects_relative_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            (Path(temp_dir) / "nested").mkdir()
            with contextlib.chdir(temp_dir):
                for stated in ("nested/..", "./nested/.."):
                    with self.subTest(stated=stated):
                        report = rf.build_report(canonical_root=stated)
                        self.assert_invalid_with(report, "must be an absolute path")
                        message = vf.canonical_root_error(report, temp_dir)
                        self.assertIsInstance(message, str)
                        self.assertIn("must be an absolute path", message or "")

    def test_windows_canonical_root_requires_drive_or_unc_share(self) -> None:
        with mock.patch.object(vf.os, "name", "nt"):
            for stated in (
                r"\repo",
                r"\nested\..",
                r"C:repo",
                "\\\\",
                r"\\server",
                "//",
                "//server",
            ):
                with self.subTest(stated=stated):
                    self.assert_invalid_with(
                        rf.build_report(canonical_root=stated),
                        "must be an absolute path",
                    )
            for stated in (r"C:\repo", r"\\server\share\repo"):
                with self.subTest(stated=stated):
                    result = vf.validate_text(rf.build_report(canonical_root=stated))
                    self.assertTrue(result.ok, result.errors)
            for report in (vf.minimal_valid_report(), rf.build_report()):
                result = vf.validate_text(report)
                self.assertTrue(result.ok, result.errors)

    def test_canonical_root_ignores_spoofed_summary_headings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            actual = base / "actual"
            spoofed = base / "spoofed"
            actual.mkdir()
            spoofed.mkdir()
            prefixes = {
                "fenced": (
                    "```markdown\n"
                    "# 1. Executive Summary\n"
                    f"Canonical root: {spoofed}\n"
                    "```\n\n"
                ),
                "protected-human-block": (
                    '<!-- SUPER-REVIEW:HUMAN-START id="summary-example" -->\n'
                    "# 1. Executive Summary\n"
                    f"Canonical root: {spoofed}\n"
                    '<!-- SUPER-REVIEW:HUMAN-END id="summary-example" -->\n\n'
                ),
            }
            for name, prefix in prefixes.items():
                with self.subTest(name=name):
                    report = rf.build_report(canonical_root=str(actual)).replace(
                        "# 1. Executive Summary",
                        prefix + "# 1. Executive Summary",
                        1,
                    )
                    validation = vf.validate_text(report)
                    self.assertTrue(validation.ok, validation.errors)
                    self.assertEqual(vf.stated_canonical_root(report), str(actual))
                    self.assertIsNone(vf.canonical_root_error(report, actual))
                    self.assertIsNotNone(vf.canonical_root_error(report, spoofed))

    def test_validate_path_enforces_canonical_root_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            other = root / "other"
            other.mkdir()
            report = root / "FINDINGS.md"
            report.write_text(
                rf.build_report(canonical_root=str(other)), encoding="utf-8"
            )
            self.assertTrue(vf.validate_path(report).ok)
            result = vf.validate_path(report, canonical_root=root)
            self.assertFalse(result.ok)
            self.assertTrue(
                any("does not match" in error for error in result.errors),
                result.errors,
            )

    def test_validate_path_reports_unresolvable_canonical_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report = root / "FINDINGS.md"
            report.write_bytes(
                rf.build_report(canonical_root=f"{root}\0suffix").encode("utf-8")
            )
            result = vf.validate_path(report, canonical_root=root)
            self.assertFalse(result.ok)
            self.assertTrue(
                any("NUL byte" in error for error in result.errors), result.errors
            )
            self.assertTrue(
                any("cannot be resolved" in error for error in result.errors),
                result.errors,
            )

    def test_validate_path_accepts_matching_canonical_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report = root / "FINDINGS.md"
            report.write_text(
                rf.build_report(canonical_root=str(root)), encoding="utf-8"
            )
            self.assertTrue(vf.validate_path(report, canonical_root=root).ok)

    def test_validate_path_requires_report_to_live_at_canonical_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            repo_a = base / "repo-a"
            repo_b = base / "repo-b"
            repo_a.mkdir()
            repo_b.mkdir()
            report = repo_b / "FINDINGS.md"
            report.write_text(
                rf.build_report(canonical_root=str(repo_a)), encoding="utf-8"
            )
            result = vf.validate_path(report, canonical_root=repo_a)
            self.assertFalse(result.ok)
            self.assertTrue(
                any("is not the canonical" in error for error in result.errors),
                result.errors,
            )

    def test_validate_path_rejects_report_outside_named_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            root = base / "repo"
            other = base / "other"
            root.mkdir()
            other.mkdir()
            report = root / "FINDINGS.md"
            report.write_text(
                rf.build_report(canonical_root=str(root)), encoding="utf-8"
            )
            result = vf.validate_path(report, canonical_root=other)
            self.assertFalse(result.ok)

    def test_snapshot_missing_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "FINDINGS.md"
            result = vf.snapshot(path)
            self.assertEqual(result.status, "missing")
            self.assertEqual(result.digest, "MISSING")
            self.assertIsNone(result.data)
            self.assertEqual(result.human_block_ids(), [])

    def test_snapshot_returns_exact_bytes_and_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "FINDINGS.md"
            text = (
                rf.build_report()
                .replace(
                    "-->\n",
                    '-->\n<!-- SUPER-REVIEW:HUMAN-START id="global-decisions" -->\n'
                    "Keep.\n"
                    '<!-- SUPER-REVIEW:HUMAN-END id="global-decisions" -->\n',
                    1,
                )
                .replace("\n", "\r\n")
            )
            data = text.encode("utf-8")
            path.write_bytes(data)
            result = vf.snapshot(path)
            self.assertEqual(result.status, "present")
            self.assertEqual(result.data, data)
            self.assertEqual(
                result.digest,
                "sha256:" + __import__("hashlib").sha256(data).hexdigest(),
            )
            self.assertEqual(result.human_block_ids(), ["global-decisions"])

    def test_snapshot_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            real = base / "real.md"
            link = base / "FINDINGS.md"
            real.write_text(rf.build_report(), encoding="utf-8")
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            with self.assertRaises(vf.SnapshotError):
                vf.snapshot(link)

    def test_snapshot_reports_path_expansion_failure(self) -> None:
        with mock.patch.object(
            Path, "expanduser", side_effect=RuntimeError("unknown home")
        ):
            with self.assertRaisesRegex(vf.SnapshotError, "cannot resolve report path"):
                vf.snapshot(Path("~/FINDINGS.md"))

    def test_validate_path_reports_path_expansion_failure(self) -> None:
        with mock.patch.object(
            Path, "expanduser", side_effect=RuntimeError("unknown home")
        ):
            result = vf.validate_path(Path("~/FINDINGS.md"))
        self.assertFalse(result.ok)
        self.assertIn("cannot resolve report path", result.errors[0])

    def test_unknown_field_on_defect_is_rejected(self) -> None:
        report = rf.build_report([rf.make_defect()]).replace(
            "Dependencies: None.",
            "Dependencies: None.\n\nGuardrail indicators: Not a defect field.",
            1,
        )
        self.assert_invalid_with(
            report, "has unknown field 'Guardrail indicators' for record type"
        )

    def test_security_fields_are_unknown_outside_sec_records(self) -> None:
        report = rf.build_report([rf.make_defect()]).replace(
            "Dependencies: None.",
            "Dependencies: None.\n\nThreat scenario: Only SEC records carry this.",
            1,
        )
        self.assert_invalid_with(
            report, "has unknown field 'Threat scenario' for record type"
        )

    def test_option_fields_are_unknown_outside_improvements(self) -> None:
        report = rf.build_report([rf.make_defect()]).replace(
            "Dependencies: None.",
            "Dependencies: None.\n\nRewrite judgment: Options belong to improvements.",
            1,
        )
        self.assert_invalid_with(
            report, "has unknown field 'Rewrite judgment' for record type"
        )

    def test_option_local_field_under_wrong_option_is_rejected(self) -> None:
        report = rf.build_report([rf.make_improvement()]).replace(
            "Minimal changes: Document one canonical algorithm and add parity tests.",
            "Rewrite judgment: This field belongs to Option D.",
            1,
        )
        self.assert_invalid_with(report, "does not belong under Option A")

    def test_option_local_field_before_option_a_is_rejected(self) -> None:
        report = rf.build_report([rf.make_improvement()]).replace(
            "### Option A — Keep and harden",
            "Minimal changes: Misplaced before the option heading.\n\n"
            "### Option A — Keep and harden",
            1,
        )
        self.assert_invalid_with(report, "appears before Option A")

    def test_unknown_option_heading_is_rejected(self) -> None:
        report = rf.build_report([rf.make_improvement()]).replace(
            "Recommendation: Do not pursue now; retain the incremental option for the stated trigger.",
            "### Option E — Unsupported\n\n"
            "Recommendation: Do not pursue now; retain the incremental option for the stated trigger.",
            1,
        )
        self.assert_invalid_with(report, "must contain Options A-D exactly once")

    def test_shared_option_fields_remain_valid_in_each_defined_scope(self) -> None:
        report = rf.build_report([rf.make_improvement()])
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_other_decision_fields_are_unknown_on_feature(self) -> None:
        report = rf.build_report([rf.make_feature()]).replace(
            "Risks: Accidental weakening during unrelated refactors.",
            "Risks: Accidental weakening during unrelated refactors.\n\n"
            "Experiment hypothesis: Keep records do not carry experiment fields.",
            1,
        )
        self.assert_invalid_with(
            report, "has unknown field 'Experiment hypothesis' for record type"
        )

    def test_colon_led_prose_inside_value_is_rejected(self) -> None:
        report = rf.build_report([rf.make_defect()]).replace(
            "Minimal reproduction: Construct the invalid state and invoke the request handler.",
            "Minimal reproduction:\nConstruct the invalid state.\n"
            "Rollback: revert the commit afterwards.",
            1,
        )
        self.assert_invalid_with(report, "has unknown field 'Rollback' for record type")

    def test_registry_replacement_cycle_is_rejected(self) -> None:
        retired = {
            "COR-101": rf.make_retired_entry(
                status="superseded", replacement_ids=("COR-102",), seed="cycle-a"
            ),
            "COR-102": rf.make_retired_entry(
                status="superseded", replacement_ids=("COR-101",), seed="cycle-b"
            ),
        }
        self.assert_invalid_with(
            rf.build_report(retired=retired),
            "form a cycle involving: COR-101, COR-102",
        )

    def test_registry_three_node_replacement_cycle_is_rejected(self) -> None:
        retired = {
            "COR-101": rf.make_retired_entry(
                status="superseded", replacement_ids=("COR-102",), seed="tri-a"
            ),
            "COR-102": rf.make_retired_entry(
                status="consolidated", replacement_ids=("COR-103",), seed="tri-b"
            ),
            "COR-103": rf.make_retired_entry(
                status="superseded", replacement_ids=("COR-101",), seed="tri-c"
            ),
        }
        self.assert_invalid_with(
            rf.build_report(retired=retired),
            "form a cycle involving: COR-101, COR-102, COR-103",
        )

    def test_registry_self_replacement_is_rejected(self) -> None:
        retired = {
            "COR-101": rf.make_retired_entry(
                status="superseded", replacement_ids=("COR-101",), seed="self"
            )
        }
        self.assert_invalid_with(
            rf.build_report(retired=retired), "COR-101 cannot replace itself"
        )

    def test_reverse_terminal_pruning_preserves_cycle_reachability(self) -> None:
        edges = {
            "terminal-parent": {"terminal"},
            "terminal": set(),
            "cycle-a": {"cycle-b"},
            "cycle-b": {"cycle-a"},
            "branch": {"terminal", "cycle-a"},
        }
        self.assertEqual(
            vf._nodes_forming_or_reaching_cycles(edges),
            {"cycle-a", "cycle-b", "branch"},
        )

    def test_invalid_retired_target_shape_does_not_crash_cycle_validation(
        self,
    ) -> None:
        retired = {
            "COR-101": rf.make_retired_entry(
                status="superseded",
                replacement_ids=("COR-102",),
                seed="source",
            ),
            "COR-102": rf.make_retired_entry(status="resolved", seed="target"),
        }
        retired["COR-102"]["replacement_ids"] = "not-an-array"
        self.assert_invalid_with(
            rf.build_report(retired=retired),
            "replacement_ids must be a string array",
        )

    def test_long_replacement_chain_uses_iterative_pruning(self) -> None:
        count = 50_000
        edges = {
            f"COR-{index:05d}": {f"COR-{index + 1:05d}"} for index in range(count - 1)
        }
        edges[f"COR-{count - 1:05d}"] = set()
        self.assertEqual(vf._nodes_forming_or_reaching_cycles(edges), set())

    def test_registry_replacement_chain_to_resolved_is_valid(self) -> None:
        retired = {
            "COR-101": rf.make_retired_entry(
                status="superseded", replacement_ids=("COR-102",), seed="chain-a"
            ),
            "COR-102": rf.make_retired_entry(status="resolved", seed="chain-b"),
        }
        result = vf.validate_text(rf.build_report(retired=retired))
        self.assertTrue(result.ok, result.errors)

    def test_registry_replacement_into_active_is_valid(self) -> None:
        retired = {
            "COR-101": rf.make_retired_entry(
                status="superseded", replacement_ids=("COR-002",), seed="into-active"
            ),
        }
        report = rf.build_report([rf.make_defect(record_id="COR-002")], retired=retired)
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_registry_superseded_requires_replacement(self) -> None:
        retired = {
            "COR-101": rf.make_retired_entry(status="superseded", seed="bare-super"),
        }
        self.assert_invalid_with(
            rf.build_report(retired=retired),
            "status superseded requires at least one replacement ID",
        )

    def test_registry_consolidated_requires_replacement(self) -> None:
        retired = {
            "COR-101": rf.make_retired_entry(status="consolidated", seed="bare-consol"),
        }
        self.assert_invalid_with(
            rf.build_report(retired=retired),
            "status consolidated requires at least one replacement ID",
        )

    def test_registry_resolved_allows_informational_replacement(self) -> None:
        retired = {
            "COR-101": rf.make_retired_entry(
                status="resolved", replacement_ids=("COR-102",), seed="resolved-ptr"
            ),
            "COR-102": rf.make_retired_entry(status="invalidated", seed="resolved-tgt"),
        }
        result = vf.validate_text(rf.build_report(retired=retired))
        self.assertTrue(result.ok, result.errors)

    def test_metadata_missing_start_rejects_revalidated_yes(self) -> None:
        self.assert_invalid_with(
            rf.build_report(revalidated="Yes"),
            "must be 'No — file did not exist' when Starting FINDINGS.md SHA-256 is MISSING",
        )

    def test_metadata_existing_digest_rejects_file_did_not_exist(self) -> None:
        self.assert_invalid_with(
            rf.build_report(starting_digest="sha256:" + "a" * 64),
            "Starting FINDINGS.md SHA-256 must be MISSING when Existing report "
            "revalidated is 'No — file did not exist'",
        )

    def test_metadata_partial_revalidation_rejects_complete(self) -> None:
        self.assert_invalid_with(
            rf.build_report(
                starting_digest="sha256:" + "a" * 64,
                revalidated="Partial — only sections 6 through 8 were rechecked",
            ),
            "Completion status must be Partial or Blocked when Existing report "
            "revalidated is Partial",
        )

    def test_metadata_partial_revalidation_with_partial_completion_is_valid(
        self,
    ) -> None:
        report = rf.build_report(
            starting_digest="sha256:" + "a" * 64,
            revalidated="Partial — only sections 6 through 8 were rechecked",
            completion="Partial",
            material_limitations="Only sections 6 through 8 were revalidated.",
        )
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_metadata_revalidated_yes_with_digest_is_valid(self) -> None:
        report = rf.build_report(
            starting_digest="sha256:" + "b" * 64, revalidated="Yes"
        )
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

    def test_snapshot_cli_metadata_only_and_out(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            path = repo / "FINDINGS.md"
            data = rf.build_report().replace("\n", "\r\n").encode("utf-8")
            path.write_bytes(data)
            out = Path(temp_dir) / "snapshot.bin"
            stdout = tempfile.TemporaryFile(mode="w+")
            try:
                with contextlib.redirect_stdout(stdout):
                    code = vf.main(
                        ["--snapshot", "--json", "--out", str(out), str(path)]
                    )
                self.assertEqual(code, 0)
                stdout.seek(0)
                payload = json.loads(stdout.read())
            finally:
                stdout.close()
            self.assertIsNone(payload["content"])
            self.assertIsNone(payload["content_base64"])
            self.assertEqual(payload["content_path"], str(out))
            self.assertTrue(str(payload["content_sha256"]).startswith("sha256:"))
            self.assertEqual(out.read_bytes(), data)

            stderr = tempfile.TemporaryFile(mode="w+")
            try:
                with contextlib.redirect_stderr(stderr):
                    code = vf.main(
                        ["--snapshot", "--json", "--out", str(out), str(path)]
                    )
            finally:
                stderr.close()
            self.assertEqual(code, 1, "--out must refuse an existing file")

            stdout = tempfile.TemporaryFile(mode="w+")
            try:
                with contextlib.redirect_stdout(stdout):
                    code = vf.main(
                        ["--snapshot", "--json", "--metadata-only", str(path)]
                    )
                self.assertEqual(code, 0)
                stdout.seek(0)
                payload = json.loads(stdout.read())
            finally:
                stdout.close()
            self.assertIsNone(payload["content"])
            self.assertEqual(payload["size"], len(data))

            inside = repo / "copy.bin"
            stderr = tempfile.TemporaryFile(mode="w+")
            try:
                with contextlib.redirect_stderr(stderr):
                    code = vf.main(
                        ["--snapshot", "--json", "--out", str(inside), str(path)]
                    )
                stderr.seek(0)
                message = stderr.read()
            finally:
                stderr.close()
            self.assertEqual(code, 2, "--out inside the reviewed tree must refuse")
            self.assertIn("outside the reviewed repository", message)
            self.assertFalse(inside.exists())

    def test_snapshot_out_refuses_swapped_output_directory(self) -> None:
        if os.open not in os.supports_dir_fd:
            self.skipTest("directory-descriptor support unavailable")
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            repo = base / "repo"
            repo.mkdir()
            path = repo / "FINDINGS.md"
            path.write_bytes(rf.build_report().encode("utf-8"))
            outdir = base / "outdir"
            outdir.mkdir()
            moved = base / "moved"
            out = outdir / "snapshot.bin"
            probe = base / "symlink-probe"
            try:
                probe.symlink_to(repo)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            probe.unlink()

            real_resolve = Path.resolve
            calls = {"outdir": 0}

            def swapping_resolve(target: Path, strict: bool = False) -> Path:
                if target == outdir:
                    calls["outdir"] += 1
                    if calls["outdir"] == 2 and not outdir.is_symlink():
                        os.rename(outdir, moved)
                        os.symlink(repo, outdir)
                return real_resolve(target, strict=strict)

            stderr = tempfile.TemporaryFile(mode="w+")
            try:
                with (
                    mock.patch.object(Path, "resolve", swapping_resolve),
                    contextlib.redirect_stderr(stderr),
                ):
                    code = vf.main(
                        ["--snapshot", "--json", "--out", str(out), str(path)]
                    )
                stderr.seek(0)
                message = stderr.read()
            finally:
                stderr.close()
            self.assertEqual(code, 1, message)
            self.assertTrue(
                "changed" in message or "outside the reviewed repository" in message,
                message,
            )
            self.assertFalse((repo / "snapshot.bin").exists())

    def test_snapshot_out_keeps_reviewed_repository_identity_pinned(self) -> None:
        if os.open not in os.supports_dir_fd:
            self.skipTest("directory-descriptor support unavailable")
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            repo = base / "repo"
            repo.mkdir()
            path = repo / "FINDINGS.md"
            path.write_bytes(rf.build_report().encode("utf-8"))
            moved = base / "moved"
            out = moved / "snapshot.bin"
            original_snapshot = vf._snapshot_from_pinned

            def swap_after_snapshot(directory, report_name: str):
                result = original_snapshot(directory, report_name)
                os.rename(repo, moved)
                repo.mkdir()
                return result

            stderr = tempfile.TemporaryFile(mode="w+")
            try:
                with (
                    mock.patch.object(
                        vf,
                        "_snapshot_from_pinned",
                        side_effect=swap_after_snapshot,
                    ),
                    contextlib.redirect_stderr(stderr),
                ):
                    code = vf.main(
                        ["--snapshot", "--json", "--out", str(out), str(path)]
                    )
                stderr.seek(0)
                message = stderr.read()
            finally:
                stderr.close()
            self.assertEqual(code, 1, message)
            self.assertIn("changed", message)
            self.assertFalse(out.exists())

    def test_snapshot_read_keeps_reviewed_repository_identity_pinned(self) -> None:
        if os.open not in os.supports_dir_fd:
            self.skipTest("directory-descriptor support unavailable")
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            repo = base / "repo"
            repo.mkdir()
            path = repo / "FINDINGS.md"
            path.write_bytes(rf.build_report().encode("utf-8"))
            moved = base / "moved"
            outside = base / "outside"
            outside.mkdir()
            secret = b"private bytes\n"
            (outside / "FINDINGS.md").write_bytes(secret)
            original_snapshot = vf._snapshot_from_pinned

            def swap_before_snapshot(directory, report_name: str):
                os.rename(repo, moved)
                os.symlink(outside, repo)
                return original_snapshot(directory, report_name)

            stdout = tempfile.TemporaryFile(mode="w+")
            stderr = tempfile.TemporaryFile(mode="w+")
            try:
                with (
                    mock.patch.object(
                        vf,
                        "_snapshot_from_pinned",
                        side_effect=swap_before_snapshot,
                    ),
                    contextlib.redirect_stdout(stdout),
                    contextlib.redirect_stderr(stderr),
                ):
                    code = vf.main(["--snapshot", "--json", str(path)])
                stdout.seek(0)
                output = stdout.read()
                stderr.seek(0)
                message = stderr.read()
            finally:
                stdout.close()
                stderr.close()
            self.assertEqual(code, 1, message)
            self.assertIn("changed", message)
            self.assertNotIn(secret.decode("utf-8").strip(), output)

    def test_snapshot_out_symlinked_parent_into_repo_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            repo = base / "repo"
            repo.mkdir()
            path = repo / "FINDINGS.md"
            path.write_bytes(rf.build_report().encode("utf-8"))
            outdir = base / "outdir"
            try:
                outdir.symlink_to(repo)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            out = outdir / "copy.bin"
            stderr = tempfile.TemporaryFile(mode="w+")
            try:
                with contextlib.redirect_stderr(stderr):
                    code = vf.main(
                        ["--snapshot", "--json", "--out", str(out), str(path)]
                    )
                stderr.seek(0)
                message = stderr.read()
            finally:
                stderr.close()
            self.assertEqual(code, 2, message)
            self.assertIn("outside the reviewed repository", message)
            self.assertFalse((repo / "copy.bin").exists())

    def test_snapshot_out_without_dir_fd_support(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            repo = base / "repo"
            repo.mkdir()
            path = repo / "FINDINGS.md"
            data = rf.build_report().encode("utf-8")
            path.write_bytes(data)
            out = base / "snapshot.bin"
            stderr = tempfile.TemporaryFile(mode="w+")
            try:
                with (
                    mock.patch.object(
                        vf._REPORT_STORE,
                        "_DESCRIPTOR_OPERATIONS_AVAILABLE",
                        False,
                    ),
                    contextlib.redirect_stderr(stderr),
                ):
                    code = vf.main(
                        ["--snapshot", "--json", "--out", str(out), str(path)]
                    )
            finally:
                stderr.close()
            self.assertEqual(code, 1)
            self.assertFalse(out.exists())

    def test_snapshot_out_write_failure_leaves_no_partial_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            repo = base / "repo"
            repo.mkdir()
            path = repo / "FINDINGS.md"
            path.write_bytes(rf.build_report().encode("utf-8"))
            out = base / "snapshot.bin"

            def partial_write(fd: int, data: bytes) -> None:
                os.write(fd, data[:10])
                raise OSError("simulated write failure")

            stderr = tempfile.TemporaryFile(mode="w+")
            try:
                with (
                    mock.patch.object(
                        vf._REPORT_STORE, "_write_all", side_effect=partial_write
                    ),
                    contextlib.redirect_stderr(stderr),
                ):
                    code = vf.main(
                        ["--snapshot", "--json", "--out", str(out), str(path)]
                    )
            finally:
                stderr.close()
            self.assertEqual(code, 1)
            self.assertFalse(out.exists())
            self.assertEqual(list(base.glob(".snapshot.bin.super-review.*.stage")), [])

    def test_snapshot_out_foreign_replacement_is_not_reported_as_success(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            repo = base / "repo"
            repo.mkdir()
            path = repo / "FINDINGS.md"
            path.write_bytes(rf.build_report().encode("utf-8"))
            out = base / "snapshot.bin"
            foreign = b"foreign bytes\n"
            original_link = vf._REPORT_STORE.PinnedDirectory.link_from

            def replace_after_link(
                directory, source_directory, source: str, destination: str
            ) -> None:
                original_link(directory, source_directory, source, destination)
                directory.unlink_leaf(destination)
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                fd = directory.open_leaf(destination, flags, 0o644)
                try:
                    os.write(fd, foreign)
                finally:
                    os.close(fd)

            stderr = tempfile.TemporaryFile(mode="w+")
            try:
                with (
                    mock.patch.object(
                        vf._REPORT_STORE.PinnedDirectory,
                        "link_from",
                        autospec=True,
                        side_effect=replace_after_link,
                    ),
                    contextlib.redirect_stderr(stderr),
                ):
                    code = vf.main(
                        ["--snapshot", "--json", "--out", str(out), str(path)]
                    )
            finally:
                stderr.close()
            self.assertEqual(code, 1)
            self.assertEqual(out.read_bytes(), foreign)

    def test_snapshot_flags_require_snapshot_mode(self) -> None:
        stderr = tempfile.TemporaryFile(mode="w+")
        try:
            with contextlib.redirect_stderr(stderr):
                code = vf.main(["--metadata-only", "irrelevant-path"])
        finally:
            stderr.close()
        self.assertEqual(code, 2)

    def test_snapshot_cli_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "FINDINGS.md"
            data = rf.build_report().encode("utf-8")
            path.write_bytes(data)
            stdout = tempfile.TemporaryFile(mode="w+")
            try:
                with contextlib.redirect_stdout(stdout):
                    code = vf.main(["--snapshot", "--json", str(path)])
                self.assertEqual(code, 0)
                stdout.seek(0)
                payload = json.loads(stdout.read())
            finally:
                stdout.close()
            self.assertEqual(payload["status"], "present")
            self.assertTrue(str(payload["digest"]).startswith("sha256:"))
            self.assertEqual(payload["content"].encode("utf-8"), data)


if __name__ == "__main__":
    unittest.main()
