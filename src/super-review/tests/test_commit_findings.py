from __future__ import annotations

import contextlib
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import commit_findings as cf
import report_factory as rf


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def add_global_human_block(report: str, body: str = "Human decision.\n") -> str:
    marker = "-->\n"
    end = report.index(marker) + len(marker)
    block = (
        '<!-- SUPER-REVIEW:HUMAN-START id="global-decisions" -->\n'
        + body
        + '<!-- SUPER-REVIEW:HUMAN-END id="global-decisions" -->\n'
    )
    return report[:end] + block + report[end:]


class CommitFindingsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.candidate = self.base / "candidate.md"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def report(self, records=None) -> str:
        return rf.build_report(records, canonical_root=str(self.repo))

    def write_candidate(self, text: str | None = None) -> bytes:
        data = (text if text is not None else self.report()).encode("utf-8")
        self.candidate.write_bytes(data)
        return data

    def commit(self, expected: str = "MISSING") -> dict[str, str]:
        return cf.commit(
            repo_root=self.repo,
            candidate_path=self.candidate,
            expected_digest=expected,
            lock_timeout=1.0,
            dry_run=False,
        )

    def test_commits_valid_candidate_exactly(self) -> None:
        expected_bytes = self.write_candidate()
        result = self.commit()
        self.assertEqual(result["status"], "committed")
        self.assertEqual((self.repo / "FINDINGS.md").read_bytes(), expected_bytes)

    def test_candidate_symlink_is_rejected(self) -> None:
        target = self.base / "real-candidate.md"
        target.write_text(rf.build_report(), encoding="utf-8")
        try:
            self.candidate.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        with self.assertRaisesRegex(cf.CommitError, "symbolic-link candidate"):
            self.commit()

    def test_target_symlink_is_rejected(self) -> None:
        self.write_candidate()
        external = self.base / "external.md"
        external.write_text(rf.build_report(), encoding="utf-8")
        try:
            (self.repo / "FINDINGS.md").symlink_to(external)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        with self.assertRaisesRegex(cf.CommitError, "symbolic-link target"):
            self.commit(expected=digest(external.read_bytes()))

    def test_candidate_inside_repository_is_rejected(self) -> None:
        inside = self.repo / "candidate.md"
        inside.write_text(rf.build_report(), encoding="utf-8")
        with self.assertRaisesRegex(cf.CommitError, "outside the repository root"):
            cf.commit(
                repo_root=self.repo,
                candidate_path=inside,
                expected_digest="MISSING",
                lock_timeout=1.0,
                dry_run=False,
            )

    def test_digest_conflict_does_not_overwrite(self) -> None:
        current = rf.build_report().encode("utf-8")
        (self.repo / "FINDINGS.md").write_bytes(current)
        self.write_candidate()
        with self.assertRaises(cf.ConflictError):
            self.commit(expected="sha256:" + "0" * 64)
        self.assertEqual((self.repo / "FINDINGS.md").read_bytes(), current)

    def test_existing_target_change_after_staging_is_not_overwritten(self) -> None:
        current = rf.build_report().encode("utf-8")
        target = self.repo / "FINDINGS.md"
        target.write_bytes(current)
        self.write_candidate(
            self.report().replace(
                "Material limitations: None",
                "Material limitations: Candidate update.",
                1,
            )
        )
        concurrent = (
            rf.build_report()
            .replace(
                "Material limitations: None",
                "Material limitations: Concurrent update.",
                1,
            )
            .encode("utf-8")
        )
        original_write_temp = cf._write_temp

        def stage_then_change(root: Path, candidate: bytes, mode: int | None) -> Path:
            staged = original_write_temp(root, candidate, mode)
            target.write_bytes(concurrent)
            return staged

        with mock.patch.object(cf, "_write_temp", side_effect=stage_then_change):
            with self.assertRaises(cf.ConflictError):
                self.commit(expected=digest(current))

        self.assertEqual(target.read_bytes(), concurrent)

    def test_protected_human_block_cannot_be_removed(self) -> None:
        current = add_global_human_block(self.report()).encode("utf-8")
        (self.repo / "FINDINGS.md").write_bytes(current)
        self.write_candidate(self.report())
        with self.assertRaisesRegex(cf.CommitError, "omits protected human block"):
            self.commit(expected=digest(current))
        self.assertEqual((self.repo / "FINDINGS.md").read_bytes(), current)

    def test_protected_human_block_survives_byte_for_byte(self) -> None:
        current_text = add_global_human_block(self.report(), "  Manual decision.  \n")
        current = current_text.encode("utf-8")
        (self.repo / "FINDINGS.md").write_bytes(current)
        candidate_text = current_text.replace(
            "Material limitations: None", "Material limitations: None observed"
        )
        candidate = self.write_candidate(candidate_text)
        self.commit(expected=digest(current))
        committed = (self.repo / "FINDINGS.md").read_bytes()
        self.assertEqual(committed, candidate)
        self.assertIn(b"  Manual decision.  \n", committed)

    def test_candidate_mutation_after_validation_cannot_change_committed_bytes(
        self,
    ) -> None:
        original_bytes = self.write_candidate()
        original_validate = cf.validate_bytes

        def validate_then_mutate(data: bytes, *, source: str):
            result = original_validate(data, source=source)
            self.candidate.write_text("not a valid report\n", encoding="utf-8")
            return result

        with mock.patch.object(cf, "validate_bytes", side_effect=validate_then_mutate):
            self.commit()

        self.assertEqual((self.repo / "FINDINGS.md").read_bytes(), original_bytes)
        self.assertNotEqual(self.candidate.read_bytes(), original_bytes)

    def test_candidate_path_replacement_after_validation_cannot_change_committed_bytes(
        self,
    ) -> None:
        original_bytes = self.write_candidate()
        replacement = self.base / "replacement.md"
        replacement.write_text("not a valid report\n", encoding="utf-8")
        original_validate = cf.validate_bytes

        def validate_then_replace(data: bytes, *, source: str):
            result = original_validate(data, source=source)
            os.replace(replacement, self.candidate)
            return result

        with mock.patch.object(cf, "validate_bytes", side_effect=validate_then_replace):
            self.commit()

        self.assertEqual((self.repo / "FINDINGS.md").read_bytes(), original_bytes)
        self.assertEqual(
            self.candidate.read_text(encoding="utf-8"), "not a valid report\n"
        )

    def test_invalid_candidate_is_not_committed(self) -> None:
        self.write_candidate("not a report\n")
        with self.assertRaisesRegex(cf.CommitError, "validation failed"):
            self.commit()
        self.assertFalse((self.repo / "FINDINGS.md").exists())

    def test_oversized_candidate_is_rejected_before_validation(self) -> None:
        self.candidate.write_bytes(b"x" * 65)
        with mock.patch.object(cf, "MAX_REPORT_BYTES", 64):
            with self.assertRaisesRegex(cf.CommitError, "byte safety limit"):
                self.commit()
        self.assertFalse((self.repo / "FINDINGS.md").exists())

    def test_dry_run_does_not_write(self) -> None:
        self.write_candidate()
        result = cf.commit(
            repo_root=self.repo,
            candidate_path=self.candidate,
            expected_digest="MISSING",
            lock_timeout=1.0,
            dry_run=True,
        )
        self.assertEqual(result["status"], "validated-dry-run")
        self.assertFalse((self.repo / "FINDINGS.md").exists())

    def test_commits_crlf_candidate_exactly(self) -> None:
        candidate = self.report().replace("\n", "\r\n").encode("utf-8")
        self.candidate.write_bytes(candidate)
        self.commit()
        self.assertEqual((self.repo / "FINDINGS.md").read_bytes(), candidate)

    def test_hard_link_candidate_to_target_is_rejected(self) -> None:
        current = self.report().encode("utf-8")
        target = self.repo / "FINDINGS.md"
        target.write_bytes(current)
        try:
            self.candidate.hardlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"hard links unavailable: {exc}")
        with self.assertRaisesRegex(cf.CommitError, "hard link"):
            self.commit(expected=digest(current))

    def test_candidate_for_another_repository_is_rejected(self) -> None:
        other = self.base / "other-repo"
        other.mkdir()
        self.write_candidate(rf.build_report(canonical_root=str(other)))
        with self.assertRaisesRegex(
            cf.CommitError, "does not belong to this repository"
        ):
            self.commit()
        self.assertFalse((self.repo / "FINDINGS.md").exists())

    def test_relative_canonical_root_is_rejected_from_destination_cwd(self) -> None:
        (self.repo / "nested").mkdir()
        self.write_candidate(rf.build_report(canonical_root="./nested/.."))
        with contextlib.chdir(self.repo):
            with self.assertRaisesRegex(cf.CommitError, "must be an absolute path"):
                self.commit()
        self.assertFalse((self.repo / "FINDINGS.md").exists())

    def test_missing_target_creation_detects_concurrent_writer(self) -> None:
        self.write_candidate()
        target = self.repo / "FINDINGS.md"
        concurrent = rf.build_report().replace(
            "Material limitations: None",
            "Material limitations: Concurrent writer created this report.",
            1,
        )
        original_link = cf.os.link
        injected = False

        def create_then_link(src, dst, *args, **kwargs):
            nonlocal injected
            if not injected:
                injected = True
                target.write_text(concurrent, encoding="utf-8")
            return original_link(src, dst, *args, **kwargs)

        with mock.patch.object(cf.os, "link", side_effect=create_then_link):
            with self.assertRaises(cf.ConflictError):
                self.commit()
        self.assertEqual(target.read_text(encoding="utf-8"), concurrent)


if __name__ == "__main__":
    unittest.main()
