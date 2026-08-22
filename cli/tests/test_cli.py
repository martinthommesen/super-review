from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve(strict=True).parents[2]
SKILL_ROOT = ROOT / "src" / "super-review"
SCRIPTS = SKILL_ROOT / "scripts"
TESTS = SKILL_ROOT / "tests"

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(SCRIPTS))

import report_factory as rf  # noqa: E402
from super_review_cli.__main__ import SKILL_ROOT_ENV, main  # noqa: E402
from super_review_cli.skill_loaders import SkillLoadError, load_helper  # noqa: E402


def run_cli(*argv: str) -> tuple[int, str, str]:
    """Run the CLI and capture both output streams."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = main(list(argv))
    return code, stdout.getvalue(), stderr.getvalue()


def with_root(*argv: str) -> tuple[int, str, str]:
    """Run the CLI with the test skill root."""
    return run_cli("--skill-root", str(SKILL_ROOT), *argv)


class SkillLoaderTests(unittest.TestCase):
    def test_load_helper_from_absolute_skill_root(self) -> None:
        module = load_helper(SKILL_ROOT, "validate_findings.py", "_cli_test_validate")
        self.assertTrue(hasattr(module, "snapshot"))
        self.assertTrue(hasattr(module, "scan_report_structure"))

    def test_relative_skill_root_rejected(self) -> None:
        with self.assertRaises(SkillLoadError):
            load_helper(
                Path("src/super-review"), "validate_findings.py", "_cli_test_rel"
            )


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_candidate(self, text: str | None = None) -> Path:
        """Write a candidate report outside the test repository."""
        candidate = self.base / "candidate.md"
        candidate.write_text(
            text
            if text is not None
            else rf.build_report(canonical_root=str(self.repo)),
            encoding="utf-8",
        )
        return candidate

    def test_skill_root_is_required(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(SKILL_ROOT_ENV, None)
            code, _, err = run_cli("validate", "irrelevant")
        self.assertEqual(code, 2)
        self.assertIn(SKILL_ROOT_ENV, err)

    def test_skill_root_from_environment(self) -> None:
        candidate = self.write_candidate()
        with mock.patch.dict(os.environ, {SKILL_ROOT_ENV: str(SKILL_ROOT)}):
            code, out, _ = run_cli("validate", str(candidate))
        self.assertEqual(code, 0, out)

    def test_relative_skill_root_is_rejected(self) -> None:
        code, _, err = run_cli(
            "--skill-root", "src/super-review", "validate", "irrelevant"
        )
        self.assertEqual(code, 2)
        self.assertIn("absolute", err)

    def test_skill_root_resolution_oserror_maps_to_exit_2(self) -> None:
        # A root whose strict resolution fails after the lstat checks (removed
        # in between, unreadable parent, dead network mount) must appear as
        # the documented usage exit code, never as a traceback.
        with mock.patch.object(
            Path, "resolve", side_effect=OSError("transport endpoint disconnected")
        ):
            code, _, err = run_cli(
                "--skill-root", str(SKILL_ROOT), "validate", "irrelevant"
            )
        self.assertEqual(code, 2)
        self.assertIn("cannot resolve skill root", err)

    def test_scripts_directory_resolution_oserror_maps_to_exit_2(self) -> None:
        # The blanket mock above trips on the first resolve (the skill root);
        # this one fails only the scripts-directory resolution so the later
        # wrapper is exercised too.
        real_resolve = Path.resolve

        def failing_resolve(target: Path, strict: bool = False) -> Path:
            if target.name == "scripts":
                raise OSError("transport endpoint disconnected")
            return real_resolve(target, strict=strict)

        with mock.patch.object(Path, "resolve", failing_resolve):
            code, _, err = run_cli(
                "--skill-root", str(SKILL_ROOT), "validate", "irrelevant"
            )
        self.assertEqual(code, 2)
        self.assertIn("cannot resolve skill scripts directory", err)

    def test_validate_round_trip(self) -> None:
        candidate = self.write_candidate()
        code, out, _ = with_root("validate", str(candidate))
        self.assertEqual(code, 0, out)
        invalid = self.base / "invalid.md"
        invalid.write_text("not a report\n", encoding="utf-8")
        code, _, err = with_root("validate", str(invalid))
        self.assertEqual(code, 1, err)

    def test_validate_canonical_root_mismatch(self) -> None:
        other = self.base / "other"
        other.mkdir()
        report = self.repo / "FINDINGS.md"
        report.write_text(rf.build_report(canonical_root=str(other)), encoding="utf-8")
        code, _, err = with_root(
            "validate", "--canonical-root", str(self.repo), str(report)
        )
        self.assertEqual(code, 1, err)

    def test_snapshot_missing_present_and_metadata_only(self) -> None:
        code, out, _ = with_root("snapshot", str(self.repo), "--json")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["status"], "missing")
        self.assertEqual(payload["digest"], "MISSING")

        data = rf.build_report(canonical_root=str(self.repo)).encode("utf-8")
        (self.repo / "FINDINGS.md").write_bytes(data)
        code, out, _ = with_root("snapshot", str(self.repo), "--json")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["content"].encode("utf-8"), data)
        self.assertEqual(
            payload["digest"], "sha256:" + hashlib.sha256(data).hexdigest()
        )

        code, out, _ = with_root(
            "snapshot", str(self.repo), "--json", "--metadata-only"
        )
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertIsNone(payload["content"])
        self.assertEqual(payload["size"], len(data))

    def test_snapshot_rejects_relative_and_non_directory_roots(self) -> None:
        code, _, err = with_root("snapshot", "relative/repo")
        self.assertEqual(code, 2)
        self.assertIn("absolute", err)
        plain_file = self.base / "file.txt"
        plain_file.write_text("x", encoding="utf-8")
        code, _, err = with_root("snapshot", str(plain_file))
        self.assertEqual(code, 2)
        self.assertIn("not a directory", err)

    def test_commit_round_trip_conflict_and_wrong_repo(self) -> None:
        candidate = self.write_candidate()
        code, out, _ = with_root(
            "commit",
            "--repo-root",
            str(self.repo),
            "--candidate",
            str(candidate),
            "--expected-sha256",
            "MISSING",
        )
        self.assertEqual(code, 0, out)
        committed = (self.repo / "FINDINGS.md").read_bytes()
        self.assertEqual(committed, candidate.read_bytes())

        code, _, err = with_root(
            "commit",
            "--repo-root",
            str(self.repo),
            "--candidate",
            str(candidate),
            "--expected-sha256",
            "MISSING",
        )
        self.assertEqual(code, 3, err)

        other = self.base / "other"
        other.mkdir()
        wrong = self.base / "wrong.md"
        wrong.write_text(rf.build_report(canonical_root=str(other)), encoding="utf-8")
        code, _, err = with_root(
            "commit",
            "--repo-root",
            str(self.repo),
            "--candidate",
            str(wrong),
            "--expected-sha256",
            "sha256:" + hashlib.sha256(committed).hexdigest(),
        )
        self.assertEqual(code, 2, err)
        self.assertIn("does not belong to this repository", err)

    def test_fingerprint_is_deterministic(self) -> None:
        argv = (
            "fingerprint",
            "--record-type",
            "Defect or risk",
            "--category",
            "SEC",
            "--primary-component",
            "auth/session",
            "--identity-statement",
            "session tokens never expire",
        )
        code_one, first, _ = with_root(*argv)
        code_two, second, _ = with_root(*argv)
        self.assertEqual((code_one, code_two), (0, 0))
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("sha256:"))

    def test_hostile_cwd_modules_are_ignored(self) -> None:
        candidate = self.write_candidate()
        hostile = self.base / "cwd"
        hostile.mkdir()
        marker = hostile / "executed.txt"
        payload = (
            "from pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('executed', encoding='utf-8')\n"
            "raise RuntimeError('hostile cwd module loaded')\n"
        )
        (hostile / "validate_findings.py").write_text(payload, encoding="utf-8")
        (hostile / "finding_fingerprint.py").write_text(payload, encoding="utf-8")
        with contextlib.chdir(hostile):
            code, out, _ = with_root("validate", str(candidate))
        self.assertEqual(code, 0, out)
        self.assertFalse(marker.exists(), "a target-relative module was executed")


class ConsoleEntrySmokeTests(unittest.TestCase):
    def test_console_entry_offline_smoke(self) -> None:
        """Run the installed entry point offline (the CI job syncs first)."""
        if shutil.which("uv") is None:
            self.skipTest("uv executable not on PATH")
        completed = subprocess.run(
            [
                "uv",
                "run",
                "--directory",
                str(ROOT / "cli"),
                "--frozen",
                "--offline",
                "super-review",
                "--help",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        for command in ("validate", "snapshot", "commit", "fingerprint"):
            self.assertIn(command, completed.stdout)


if __name__ == "__main__":
    unittest.main()
