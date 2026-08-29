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
from types import ModuleType
from unittest import mock

# Pin a symlink-resolved temp root (the default macOS TMPDIR is a symlink)
# so temporary paths compare as physical paths.
tempfile.tempdir = str(Path(tempfile.gettempdir()).resolve())

ROOT = Path(__file__).resolve(strict=True).parents[2]
SKILL_ROOT = ROOT / "src" / "super-review"
SCRIPTS = SKILL_ROOT / "scripts"
TESTS = SKILL_ROOT / "tests"

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(SCRIPTS))

import report_factory as rf
from super_review_cli.__main__ import SKILL_ROOT_ENV, main
from super_review_cli.skill_loaders import SkillLoadError, load_helper


def run_cli(*argv: str) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = main(list(argv))
    return code, stdout.getvalue(), stderr.getvalue()


def with_root(*argv: str) -> tuple[int, str, str]:
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

    def test_import_failures_restore_module_state(self) -> None:
        cases = {
            "oserror": "raise OSError('broken filesystem')\n",
            "importerror": "raise ImportError('missing dependency')\n",
            "syntaxerror": "def broken(:\n",
            "runtimeerror": "raise RuntimeError('broken helper')\n",
            "systemexit": "raise SystemExit(7)\n",
        }
        for name, source in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "SKILL.md").write_text("fixture\n", encoding="utf-8")
                scripts = root / "scripts"
                scripts.mkdir()
                (scripts / "helper.py").write_text(source, encoding="utf-8")
                module_name = f"_cli_failed_import_{name}"
                with self.assertRaises(SkillLoadError):
                    load_helper(root, "helper.py", module_name)
                self.assertNotIn(module_name, sys.modules)

    def test_import_failure_restores_existing_module(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("fixture\n", encoding="utf-8")
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "helper.py").write_text(
                "raise RuntimeError('broken helper')\n", encoding="utf-8"
            )
            module_name = "_cli_existing_module"
            previous = ModuleType(module_name)
            sys.modules[module_name] = previous
            try:
                with self.assertRaises(SkillLoadError):
                    load_helper(root, "helper.py", module_name)
                self.assertIs(sys.modules[module_name], previous)
            finally:
                sys.modules.pop(module_name, None)


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_candidate(self, text: str | None = None) -> Path:
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
        with mock.patch.object(
            Path, "resolve", side_effect=OSError("transport endpoint disconnected")
        ):
            code, _, err = run_cli(
                "--skill-root", str(SKILL_ROOT), "validate", "irrelevant"
            )
        self.assertEqual(code, 2)
        self.assertIn("cannot resolve skill root", err)

    def test_skill_root_expand_error_maps_to_exit_2(self) -> None:
        with mock.patch.object(
            Path, "expanduser", side_effect=RuntimeError("unknown home")
        ):
            code, _, err = run_cli(
                "--skill-root", str(SKILL_ROOT), "validate", "irrelevant"
            )
        self.assertEqual(code, 2)
        self.assertIn("cannot expand skill root", err)

    def test_scripts_directory_resolution_oserror_maps_to_exit_2(self) -> None:
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

    def test_validate_cannot_select_snapshot_or_self_test_modes(self) -> None:
        arbitrary = self.base / "arbitrary.txt"
        arbitrary.write_text("private bytes\n", encoding="utf-8")
        code, out, err = with_root("validate", "--snapshot", "--json", str(arbitrary))
        self.assertEqual(code, 2, (out, err))
        self.assertNotIn("private bytes", out)
        code, _, _ = with_root("validate", "--self-test")
        self.assertEqual(code, 2)

    def test_each_subcommand_help_returns_zero(self) -> None:
        for command in ("validate", "snapshot", "commit", "fingerprint"):
            with self.subTest(command=command):
                code, out, err = with_root(command, "--help")
                self.assertEqual(code, 0, (out, err))
                self.assertIn("usage:", out)

    def test_snapshot_rejects_internal_self_test_mode(self) -> None:
        code, _, err = with_root("snapshot", str(self.repo), "--self-test")
        self.assertEqual(code, 2, err)

    def test_missing_transitive_helper_maps_to_load_error(self) -> None:
        copied = self.base / "skill"
        shutil.copytree(SKILL_ROOT, copied)
        (copied / "scripts" / "report_store.py").unlink()
        names = (
            "_super_review_finding_fingerprint",
            "_super_review_report_store",
        )
        before = {name: sys.modules.get(name) for name in names}
        code, _, err = run_cli("--skill-root", str(copied), "validate", "irrelevant")
        self.assertEqual(code, 2)
        self.assertIn("cannot load helper", err)
        for name, previous in before.items():
            if previous is None:
                self.assertNotIn(name, sys.modules)
            else:
                self.assertIs(sys.modules.get(name), previous)

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
        self.assertEqual(code, 1)
        self.assertIn("not a directory", err)

    def test_snapshot_reports_repository_symlink_loop(self) -> None:
        first = self.base / "loop-a"
        second = self.base / "loop-b"
        try:
            first.symlink_to(second)
            second.symlink_to(first)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        code, _, err = with_root("snapshot", str(first))
        self.assertEqual(code, 1)
        self.assertIn("cannot resolve reviewed repository", err)

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
