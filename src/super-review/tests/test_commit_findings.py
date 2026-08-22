from __future__ import annotations

import contextlib
import errno
import hashlib
import os
import random
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

    def test_commit_bytes_writes_exact_payload(self) -> None:
        payload = self.report().encode("utf-8")
        result = cf.commit_bytes(
            repo_root=self.repo,
            candidate_bytes=payload,
            expected_digest="MISSING",
            lock_timeout=1.0,
            dry_run=False,
        )
        self.assertEqual(result["status"], "committed")
        self.assertEqual((self.repo / "FINDINGS.md").read_bytes(), payload)

    def test_commit_bytes_rejects_non_utf8(self) -> None:
        with self.assertRaisesRegex(cf.CommitError, "validation failed|UTF-8"):
            cf.commit_bytes(
                repo_root=self.repo,
                candidate_bytes=b"\xff\xfe not utf-8",
                expected_digest="MISSING",
                lock_timeout=1.0,
                dry_run=False,
            )
        self.assertFalse((self.repo / "FINDINGS.md").exists())

    def test_commit_bytes_normalizes_expected_digest_via_conflict(self) -> None:
        current = self.report().encode("utf-8")
        (self.repo / "FINDINGS.md").write_bytes(current)
        with self.assertRaises(cf.ConflictError):
            cf.commit_bytes(
                repo_root=self.repo,
                candidate_bytes=current,
                expected_digest="MISSING",
                lock_timeout=1.0,
                dry_run=False,
            )
        self.assertEqual((self.repo / "FINDINGS.md").read_bytes(), current)

    def test_commit_bytes_canonical_root_mismatch(self) -> None:
        other = self.base / "other-repo"
        other.mkdir()
        payload = rf.build_report(canonical_root=str(other)).encode("utf-8")
        with self.assertRaisesRegex(
            cf.CommitError, "does not belong to this repository"
        ):
            cf.commit_bytes(
                repo_root=self.repo,
                candidate_bytes=payload,
                expected_digest="MISSING",
                lock_timeout=1.0,
                dry_run=False,
            )

    def test_commit_bytes_preserves_annotations(self) -> None:
        current_text = add_global_human_block(self.report(), "Keep me.\n")
        current = current_text.encode("utf-8")
        (self.repo / "FINDINGS.md").write_bytes(current)
        candidate = current_text.replace(
            "Material limitations: None",
            "Material limitations: Updated via bytes.",
            1,
        ).encode("utf-8")
        cf.commit_bytes(
            repo_root=self.repo,
            candidate_bytes=candidate,
            expected_digest=digest(current),
            lock_timeout=1.0,
            dry_run=False,
        )
        committed = (self.repo / "FINDINGS.md").read_bytes()
        self.assertEqual(committed, candidate)
        self.assertIn(b"Keep me.\n", committed)

    def test_commit_bytes_oversized_payload_rejected(self) -> None:
        with mock.patch.object(cf, "MAX_REPORT_BYTES", 64):
            with self.assertRaisesRegex(cf.CommitError, "byte safety limit"):
                cf.commit_bytes(
                    repo_root=self.repo,
                    candidate_bytes=b"x" * 65,
                    expected_digest="MISSING",
                    lock_timeout=1.0,
                    dry_run=False,
                )

    def test_commit_works_without_os_fchmod(self) -> None:
        """Windows before Python 3.13 lacks os.fchmod; chmod fallback must hold."""
        expected_bytes = self.write_candidate()
        with mock.patch.object(cf.os, "fchmod", None):
            result = self.commit()
        self.assertEqual(result["status"], "committed")
        target = self.repo / "FINDINGS.md"
        self.assertEqual(target.read_bytes(), expected_bytes)
        self.assertEqual(os.stat(target).st_mode & 0o777, 0o644)

    def test_missing_target_creation_without_hardlink_support(self) -> None:
        expected_bytes = self.write_candidate()
        with mock.patch.object(
            cf.os, "link", side_effect=OSError(errno.EPERM, "hard links unsupported")
        ):
            result = self.commit()
        self.assertEqual(result["status"], "committed")
        target = self.repo / "FINDINGS.md"
        self.assertEqual(target.read_bytes(), expected_bytes)
        self.assertEqual(os.stat(target).st_mode & 0o777, 0o644)

    def test_fallback_failure_leaves_no_partial_report(self) -> None:
        self.write_candidate()
        target = self.repo / "FINDINGS.md"
        with (
            mock.patch.object(
                cf.os,
                "link",
                side_effect=OSError(errno.EPERM, "hard links unsupported"),
            ),
            mock.patch.object(
                cf.os, "replace", side_effect=OSError(errno.EIO, "device error")
            ),
        ):
            with self.assertRaises(OSError):
                self.commit()
        # The placeholder is cleaned up; the visible path never held a
        # partially written candidate.
        self.assertFalse(target.exists())

    def test_fallback_cleanup_spares_foreign_replacement(self) -> None:
        self.write_candidate()
        target = self.repo / "FINDINGS.md"
        foreign = b"foreign writer content\n"
        foreign_source = self.base / "foreign.md"

        def swap_then_fail(src, dst, *args, **kwargs):
            foreign_source.write_bytes(foreign)
            os.rename(foreign_source, target)
            raise OSError(errno.EIO, "device error")

        with (
            mock.patch.object(
                cf.os,
                "link",
                side_effect=OSError(errno.EPERM, "hard links unsupported"),
            ),
            mock.patch.object(cf.os, "replace", side_effect=swap_then_fail),
        ):
            with self.assertRaises(OSError):
                self.commit()
        # The identity-guarded cleanup must not delete the other writer's file.
        self.assertEqual(target.read_bytes(), foreign)

    def test_fallback_creation_detects_concurrent_writer(self) -> None:
        self.write_candidate()
        target = self.repo / "FINDINGS.md"
        concurrent = rf.build_report().replace(
            "Material limitations: None",
            "Material limitations: Concurrent writer created this report.",
            1,
        )

        def write_then_refuse(src, dst, *args, **kwargs):
            """
            Write concurrent content to the target and raise a permission error to simulate unsupported hard links.
            
            Raises:
                OSError: Always raised with errno.EPERM.
            """
            target.write_text(concurrent, encoding="utf-8")
            raise OSError(errno.EPERM, "hard links unsupported")

        with mock.patch.object(cf.os, "link", side_effect=write_then_refuse):
            with self.assertRaises(cf.ConflictError):
                self.commit()
        self.assertEqual(target.read_text(encoding="utf-8"), concurrent)

    def test_commit_accepts_annotation_containing_fence_marker(self) -> None:
        first = add_global_human_block(self.report(), "Decision.\n```\nrationale\n")
        data = self.write_candidate(first)
        self.commit()
        target = self.repo / "FINDINGS.md"
        self.assertEqual(target.read_bytes(), data)
        second = first.replace(
            "Material limitations: None", "Material limitations: None observed", 1
        )
        updated = self.write_candidate(second)
        self.commit(expected=digest(data))
        self.assertEqual(target.read_bytes(), updated)

    def test_non_utf8_current_target_blocks_still_verified(self) -> None:
        current = (
            b"\xff\xfe binary prefix\n"
            b'<!-- SUPER-REVIEW:HUMAN-START id="keep" -->\n'
            b"payload\n"
            b'<!-- SUPER-REVIEW:HUMAN-END id="keep" -->\n'
        )
        (self.repo / "FINDINGS.md").write_bytes(current)
        self.write_candidate()
        with self.assertRaisesRegex(cf.CommitError, "omits protected human block"):
            self.commit(expected=digest(current))

    def test_writer_and_validator_share_one_scanner(self) -> None:
        """Differential guard: the writer must hold no structure parser of its own."""
        self.assertFalse(hasattr(cf, "FENCE_OPEN_BYTES_RE"))
        rng = random.Random(0)
        atoms = [
            b"```\n",
            b"````\n",
            b"~~~\n",
            b"```python`x\n",
            b"   ```\n",
            b"``` \t\n",
            b"```\xc2\xa0\n",
            b"~~~ info\n",
            b"plain prose\n",
            b"text\xe2\x80\xa8more\n",
            b'<!-- SUPER-REVIEW:HUMAN-START id="a" -->\n',
            b'<!-- SUPER-REVIEW:HUMAN-END id="a" -->\n',
            b'<!-- SUPER-REVIEW:HUMAN-START id="b" -->\n',
            b'<!-- SUPER-REVIEW:HUMAN-END id="b" -->\n',
            b'<!-- SUPER-REVIEW:HUMAN-END id="c" -->\n',
            b"line\r\n",
            b"line\r",
            b"\n",
        ]
        validator = cf._VALIDATOR
        for _ in range(300):
            data = b"".join(rng.choice(atoms) for _ in range(rng.randrange(0, 12)))
            scan = validator.scan_report_structure(data)
            if scan.errors:
                with self.assertRaises(cf.CommitError):
                    cf._parse_human_blocks_bytes(data)
            else:
                expected = {block.block_id: block.raw for block in scan.blocks}
                self.assertEqual(cf._parse_human_blocks_bytes(data), expected)

    def test_hard_linked_target_alone_is_not_refused(self) -> None:
        """Atomic replace may detach a hard-linked target pathname safely."""
        current = self.report().encode("utf-8")
        target = self.repo / "FINDINGS.md"
        target.write_bytes(current)
        alias = self.base / "alias-FINDINGS.md"
        try:
            alias.hardlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"hard links unavailable: {exc}")
        candidate = self.report().replace(
            "Material limitations: None",
            "Material limitations: Target had an external hard link.",
            1,
        )
        payload = self.write_candidate(candidate)
        self.commit(expected=digest(current))
        self.assertEqual(target.read_bytes(), payload)
        # The alias still holds the previous inode contents after replace.
        self.assertEqual(alias.read_bytes(), current)


if __name__ == "__main__":
    unittest.main()
