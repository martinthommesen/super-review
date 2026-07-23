from __future__ import annotations

import contextlib
import ntpath
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import report_factory as rf
import validate_findings as vf


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
            "Canonical root: /tmp/repo", "Canonical root:", 1
        )
        self.assert_invalid_with(report, "metadata 'Canonical root' must not be empty")

    def test_duplicate_required_metadata_is_rejected(self) -> None:
        report = rf.build_report().replace(
            "Canonical root: /tmp/repo",
            "Canonical root: /tmp/repo\nCanonical root: /tmp/other",
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
            "# 2. Repository and System Overview\n\nNo current canonical records supported — test fixture.",
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
            "# 2. Repository and System Overview\n\nNo current canonical records supported — test fixture.",
            "# 2. Repository and System Overview\n\n" + snippet,
            1,
        )
        result = vf.validate_text(report)
        self.assertTrue(result.ok, result.errors)

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
        report = rf.build_report(canonical_root="/srv/project")
        self.assertEqual(vf.stated_canonical_root(report), "/srv/project")

    def test_canonical_root_error_accepts_matching_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = rf.build_report(canonical_root=temp_dir)
            self.assertIsNone(vf.canonical_root_error(report, temp_dir))

    def test_canonical_root_error_flags_mismatch(self) -> None:
        report = rf.build_report(canonical_root="/srv/project")
        message = vf.canonical_root_error(report, "/srv/other")
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
        legacy_ntpath = mock.Mock(wraps=ntpath)
        legacy_ntpath.isabs.side_effect = lambda value: (
            value.startswith("\\") or ntpath.isabs(value)
        )
        with (
            mock.patch.object(vf.os, "name", "nt"),
            mock.patch.object(vf.os, "path", legacy_ntpath),
        ):
            for stated in (r"\repo", r"\nested\..", r"C:repo"):
                with self.subTest(stated=stated):
                    self.assert_invalid_with(
                        rf.build_report(canonical_root=stated),
                        "must be an absolute path",
                    )
            for stated in (r"C:\repo", r"\\server\share\repo"):
                with self.subTest(stated=stated):
                    result = vf.validate_text(rf.build_report(canonical_root=stated))
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
            report = root / "FINDINGS.md"
            report.write_text(
                rf.build_report(canonical_root="/somewhere/else"), encoding="utf-8"
            )
            self.assertTrue(vf.validate_path(report).ok)
            result = vf.validate_path(report, canonical_root=root)
            self.assertFalse(result.ok)
            self.assertTrue(
                any("does not match" in error for error in result.errors),
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
        # A report physically in repo B whose metadata (and the --canonical-root
        # argument) both name repo A must not pass: metadata agreement is not
        # proof the file lives in that repository.
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


if __name__ == "__main__":
    unittest.main()
