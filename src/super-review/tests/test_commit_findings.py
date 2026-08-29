from __future__ import annotations

import contextlib
import errno
import hashlib
import os
import random
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import commit_findings as cf
import report_factory as rf

# Pin a symlink-resolved temp root (the default macOS TMPDIR is a symlink)
# so stated canonical roots match resolved review destinations.
tempfile.tempdir = str(Path(tempfile.gettempdir()).resolve())


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


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

    def test_repository_symlink_loop_is_reported_without_traceback(self) -> None:
        self.write_candidate()
        first = self.base / "loop-a"
        second = self.base / "loop-b"
        try:
            first.symlink_to(second)
            second.symlink_to(first)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        with self.assertRaisesRegex(cf.CommitError, "cannot resolve repository root"):
            cf.commit(
                repo_root=first,
                candidate_path=self.candidate,
                expected_digest="MISSING",
                lock_timeout=1.0,
                dry_run=False,
            )

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
        original_stage = cf._REPORT_STORE._stage_exact

        def stage_then_change(directory, payload, *, mode: int, prefix: str):
            staged = original_stage(directory, payload, mode=mode, prefix=prefix)
            target.write_bytes(concurrent)
            return staged

        with mock.patch.object(
            cf._REPORT_STORE, "_stage_exact", side_effect=stage_then_change
        ):
            with self.assertRaises(cf.ConflictError):
                self.commit(expected=digest(current))

        self.assertEqual(target.read_bytes(), concurrent)

    def test_protected_human_block_cannot_be_removed(self) -> None:
        current = rf.add_global_human_block(self.report(), "Human decision.\n").encode(
            "utf-8"
        )
        (self.repo / "FINDINGS.md").write_bytes(current)
        self.write_candidate(self.report())
        with self.assertRaisesRegex(cf.CommitError, "omits protected human block"):
            self.commit(expected=digest(current))
        self.assertEqual((self.repo / "FINDINGS.md").read_bytes(), current)

    def test_protected_human_block_survives_byte_for_byte(self) -> None:
        current_text = rf.add_global_human_block(
            self.report(), "  Manual decision.  \n"
        )
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
        current_text = rf.add_global_human_block(self.report(), "Keep me.\n")
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

    def test_commit_fails_closed_without_descriptor_mode_setting(self) -> None:
        self.write_candidate()
        with mock.patch.object(cf.os, "fchmod", None):
            with self.assertRaises(cf._REPORT_STORE.SafePublicationUnavailable):
                self.commit()
        self.assertFalse((self.repo / "FINDINGS.md").exists())

    def test_commit_fails_closed_without_descriptor_operations(self) -> None:
        self.write_candidate()
        with mock.patch.object(
            cf._REPORT_STORE,
            "_DESCRIPTOR_OPERATIONS_AVAILABLE",
            False,
        ):
            with self.assertRaises(cf._REPORT_STORE.SafePublicationUnavailable):
                self.commit()
        self.assertFalse((self.repo / "FINDINGS.md").exists())

    def test_missing_target_fails_closed_without_hardlink_support(self) -> None:
        self.write_candidate()
        with mock.patch.object(
            cf.os, "link", side_effect=OSError(errno.EPERM, "hard links unsupported")
        ):
            with self.assertRaises(cf._REPORT_STORE.SafePublicationUnavailable):
                self.commit()
        self.assertFalse((self.repo / "FINDINGS.md").exists())

    def test_failed_staging_leaves_no_partial_report(self) -> None:
        self.write_candidate()
        target = self.repo / "FINDINGS.md"

        def partial_write(fd: int, data: bytes) -> None:
            os.write(fd, data[:10])
            raise OSError(errno.EIO, "device error")

        with mock.patch.object(
            cf._REPORT_STORE, "_write_all", side_effect=partial_write
        ):
            with self.assertRaises(OSError):
                self.commit()
        self.assertFalse(target.exists())
        self.assertEqual(list(self.repo.glob(".FINDINGS.md.super-review.*.stage")), [])

    def test_repository_root_swap_cannot_redirect_publication(self) -> None:
        self.write_candidate()
        moved = self.base / "moved-repository"
        outside = self.base / "outside"
        outside.mkdir()
        original_link = cf._REPORT_STORE.PinnedDirectory.link_from

        probe = self.base / "symlink-probe"
        try:
            probe.symlink_to(outside)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        probe.unlink()

        def swap_then_link(
            directory, source_directory, source: str, destination: str
        ) -> None:
            os.rename(self.repo, moved)
            os.symlink(outside, self.repo)
            original_link(directory, source_directory, source, destination)

        with mock.patch.object(
            cf._REPORT_STORE.PinnedDirectory,
            "link_from",
            autospec=True,
            side_effect=swap_then_link,
        ):
            with self.assertRaises(cf.ConflictError):
                self.commit()
        self.assertFalse((outside / "FINDINGS.md").exists())
        self.assertFalse((moved / "FINDINGS.md").exists())

    def test_foreign_replacement_after_exchange_preserves_displaced_target(
        self,
    ) -> None:
        current = self.report().encode("utf-8")
        target = self.repo / "FINDINGS.md"
        target.write_bytes(current)
        self.write_candidate(
            self.report().replace(
                "Material limitations: None",
                "Material limitations: Candidate update.",
                1,
            )
        )
        foreign = b"foreign bytes\n"
        original_exchange = cf._REPORT_STORE.PinnedDirectory.exchange_with
        injected = False

        def exchange_then_foreign(
            directory, source_directory, source: str, destination: str
        ) -> None:
            nonlocal injected
            original_exchange(directory, source_directory, source, destination)
            if injected:
                return
            injected = True
            directory.unlink_leaf(destination)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            fd = directory.open_leaf(destination, flags, 0o644)
            try:
                os.write(fd, foreign)
            finally:
                os.close(fd)

        with mock.patch.object(
            cf._REPORT_STORE.PinnedDirectory,
            "exchange_with",
            autospec=True,
            side_effect=exchange_then_foreign,
        ):
            with self.assertRaises(cf.ConflictError):
                self.commit(expected=digest(current))
        self.assertEqual(target.read_bytes(), foreign)
        recovery = list(self.repo.glob(".FINDINGS.md.super-review.*.stage/payload"))
        self.assertEqual(len(recovery), 1)
        self.assertEqual(recovery[0].read_bytes(), current)

    def test_target_change_at_exchange_is_quarantined_without_losing_blocks(
        self,
    ) -> None:
        current = self.report().encode("utf-8")
        target = self.repo / "FINDINGS.md"
        target.write_bytes(current)
        candidate = self.write_candidate(
            self.report().replace(
                "Material limitations: None",
                "Material limitations: Candidate update.",
                1,
            )
        )
        concurrent = rf.add_global_human_block(
            self.report(), "Concurrent human decision.\n"
        ).encode("utf-8")
        original_exchange = cf._REPORT_STORE.PinnedDirectory.exchange_with
        injected = False

        def change_then_exchange(
            directory, source_directory, source: str, destination: str
        ) -> None:
            nonlocal injected
            if not injected:
                injected = True
                target.write_bytes(concurrent)
            original_exchange(directory, source_directory, source, destination)

        with mock.patch.object(
            cf._REPORT_STORE.PinnedDirectory,
            "exchange_with",
            autospec=True,
            side_effect=change_then_exchange,
        ):
            with self.assertRaises(cf.ConflictError):
                self.commit(expected=digest(current))
        self.assertEqual(target.read_bytes(), candidate)
        recovery = list(self.repo.glob(".FINDINGS.md.super-review.*.stage/payload"))
        self.assertEqual(len(recovery), 1)
        self.assertEqual(recovery[0].read_bytes(), concurrent)

    def test_replaced_displaced_leaf_is_never_promoted_by_recovery(self) -> None:
        current = self.report().encode("utf-8")
        target = self.repo / "FINDINGS.md"
        target.write_bytes(current)
        candidate = self.write_candidate(
            self.report().replace(
                "Material limitations: None",
                "Material limitations: Candidate update.",
                1,
            )
        )
        attacker = b"X" * len(current)
        original_exchange = cf._REPORT_STORE.PinnedDirectory.exchange_with
        injected = False
        exchange_calls = 0

        def exchange_then_replace_source(
            directory, source_directory, source: str, destination: str
        ) -> None:
            nonlocal exchange_calls, injected
            exchange_calls += 1
            original_exchange(directory, source_directory, source, destination)
            if injected:
                return
            injected = True
            source_directory.unlink_leaf(source)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            fd = source_directory.open_leaf(source, flags, 0o600)
            try:
                os.write(fd, attacker)
            finally:
                os.close(fd)

        with mock.patch.object(
            cf._REPORT_STORE.PinnedDirectory,
            "exchange_with",
            autospec=True,
            side_effect=exchange_then_replace_source,
        ):
            with self.assertRaisesRegex(cf.ConflictError, "exchange was not reversed"):
                self.commit(expected=digest(current))
        self.assertEqual(exchange_calls, 1)
        self.assertEqual(target.read_bytes(), candidate)
        recovery = list(self.repo.glob(".FINDINGS.md.super-review.*.stage/payload"))
        self.assertEqual(len(recovery), 1)
        self.assertEqual(recovery[0].read_bytes(), attacker)

    def test_replaced_staging_leaf_cannot_reach_existing_target(self) -> None:
        current = self.report().encode("utf-8")
        target = self.repo / "FINDINGS.md"
        target.write_bytes(current)
        self.write_candidate(
            self.report().replace(
                "Material limitations: None",
                "Material limitations: Candidate update.",
                1,
            )
        )
        original_stage = cf._REPORT_STORE._stage_exact

        def stage_then_replace(directory, payload, *, mode: int, prefix: str):
            staged = original_stage(directory, payload, mode=mode, prefix=prefix)
            staged.directory.unlink_leaf(staged.name)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            fd = staged.directory.open_leaf(staged.name, flags, 0o600)
            try:
                os.write(fd, b"X" * len(payload.data))
            finally:
                os.close(fd)
            return staged

        with mock.patch.object(
            cf._REPORT_STORE, "_stage_exact", side_effect=stage_then_replace
        ):
            with self.assertRaises(cf.ConflictError):
                self.commit(expected=digest(current))
        self.assertEqual(target.read_bytes(), current)
        recovery = list(self.repo.glob(".FINDINGS.md.super-review.*.stage/payload"))
        self.assertEqual(len(recovery), 1)
        self.assertEqual(
            recovery[0].read_bytes(), b"X" * len(self.candidate.read_bytes())
        )

    def test_existing_target_fails_closed_without_atomic_exchange(self) -> None:
        current = self.report().encode("utf-8")
        target = self.repo / "FINDINGS.md"
        target.write_bytes(current)
        self.write_candidate(
            self.report().replace(
                "Material limitations: None",
                "Material limitations: Candidate update.",
                1,
            )
        )
        unavailable = cf._REPORT_STORE.SafePublicationUnavailable(
            "atomic exchange unavailable"
        )
        with mock.patch.object(
            cf._REPORT_STORE, "_rename_exchange", side_effect=unavailable
        ):
            with self.assertRaises(cf._REPORT_STORE.SafePublicationUnavailable):
                self.commit(expected=digest(current))
        self.assertEqual(target.read_bytes(), current)
        self.assertEqual(list(self.repo.glob(".FINDINGS.md.super-review.*.stage")), [])

    def test_exchange_uses_darwin_swap_flag_when_renameat2_is_absent(self) -> None:
        exchange = mock.Mock(return_value=0)
        # A bare Mock would auto-create renameat2 and skip the Darwin branch.
        libc = mock.Mock(spec=["renameatx_np"], renameatx_np=exchange)
        with mock.patch.object(cf._REPORT_STORE.ctypes, "CDLL", return_value=libc):
            cf._REPORT_STORE._rename_exchange(3, "a", 4, "b")
        exchange.assert_called_once()
        flags = exchange.call_args.args[-1]
        self.assertEqual(flags, cf._REPORT_STORE._RENAME_SWAP)
        self.assertNotEqual(flags, 0)

    def test_exchange_fails_closed_when_no_exchange_symbol_exists(self) -> None:
        with mock.patch.object(cf._REPORT_STORE.ctypes, "CDLL", return_value=object()):
            with self.assertRaises(cf._REPORT_STORE.SafePublicationUnavailable):
                cf._REPORT_STORE._rename_exchange(3, "a", 4, "b")

    def test_existing_target_mode_is_preserved(self) -> None:
        current = self.report().encode("utf-8")
        target = self.repo / "FINDINGS.md"
        target.write_bytes(current)
        target.chmod(0o600)
        self.write_candidate(
            self.report().replace(
                "Material limitations: None",
                "Material limitations: Candidate update.",
                1,
            )
        )
        self.commit(expected=digest(current))
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_advisory_lock_timeout_closes_its_handle(self) -> None:
        if os.name == "nt":
            self.skipTest("POSIX flock test")
        identity = cf._REPORT_STORE.FileIdentity.from_stat(self.repo.stat())
        lock = cf._REPORT_STORE.AdvisoryLock(identity, self.repo, 0.0)
        with mock.patch("fcntl.flock", side_effect=BlockingIOError):
            with self.assertRaisesRegex(
                cf._REPORT_STORE.StoreConflictError, "timed out"
            ):
                lock.__enter__()
        self.assertIsNone(lock.handle)

    def test_commit_accepts_annotation_containing_fence_marker(self) -> None:
        first = rf.add_global_human_block(self.report(), "Decision.\n```\nrationale\n")
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
        self.assertEqual(alias.read_bytes(), current)


if __name__ == "__main__":
    unittest.main()
