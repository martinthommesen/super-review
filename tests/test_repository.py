from __future__ import annotations

import hashlib
import importlib.util
import re
import stat
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve(strict=True).parents[1]
SKILL = ROOT / "src" / "super-review"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class RepositoryTests(unittest.TestCase):
    def test_version_is_consistent(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertIn(f"Version: {version}", skill_text)
        self.assertRegex(pyproject, rf'(?m)^version = "{re.escape(version)}"$')
        self.assertIn(f"## [{version}]", changelog)

    def test_original_prompt_provenance(self) -> None:
        prompt = ROOT / "docs" / "ORIGINAL_REVIEW_PROMPT.md"
        checksum = ROOT / "docs" / "ORIGINAL_REVIEW_PROMPT.sha256"
        expected, filename = checksum.read_text(encoding="utf-8").split()
        self.assertEqual(filename, prompt.name)
        self.assertEqual(hashlib.sha256(prompt.read_bytes()).hexdigest(), expected)
        self.assertEqual(len(prompt.read_text(encoding="utf-8").splitlines()), 3201)

    def test_required_workbench_documents_exist(self) -> None:
        for relative in (
            "AGENTS.md",
            "README.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CHANGELOG.md",
            "docs/ARCHITECTURE.md",
            "docs/DECISIONS.md",
            "docs/RELEASE.md",
            "docs/REVIEW_HISTORY.md",
            "docs/PROVENANCE.md",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_source_tree_has_no_symlinks_or_bytecode(self) -> None:
        for path in SKILL.rglob("*"):
            info = path.lstat()
            self.assertFalse(stat.S_ISLNK(info.st_mode), str(path))
            self.assertNotIn(path.suffix, {".pyc", ".pyo"})
            self.assertNotIn("__pycache__", path.parts)

    def test_runtime_scripts_are_executable(self) -> None:
        for relative in (
            "scripts/commit_findings.py",
            "scripts/finding_fingerprint.py",
            "scripts/validate_findings.py",
            "tests/run_tests.py",
        ):
            mode = stat.S_IMODE((SKILL / relative).stat().st_mode)
            self.assertTrue(mode & 0o111, f"not executable: {relative} ({oct(mode)})")

    def test_example_report_is_valid(self) -> None:
        validator = load_module(
            "_workbench_validate_findings", SKILL / "scripts" / "validate_findings.py"
        )
        result = validator.validate_path(ROOT / "examples" / "FINDINGS.example.md")
        self.assertTrue(result.ok, result.errors)

    def test_builder_is_deterministic_and_source_exact(self) -> None:
        build = load_module("_workbench_build", ROOT / "scripts" / "build.py")
        verify = load_module("_workbench_verify", ROOT / "scripts" / "verify_dist.py")
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "one" / "super-review-skill.zip"
            second = Path(directory) / "two" / "super-review-skill.zip"
            first_digest = build.build(first)
            second_digest = build.build(second)
            self.assertEqual(first_digest, second_digest)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(verify.verify(first, run_tests=False), first_digest)

    def test_archive_contains_only_distributable_skill(self) -> None:
        build = load_module("_workbench_build_names", ROOT / "scripts" / "build.py")
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "super-review-skill.zip"
            build.build(artifact)
            with zipfile.ZipFile(artifact) as archive:
                names = archive.namelist()
        self.assertTrue(names)
        self.assertTrue(all(name.startswith("super-review/") for name in names))
        self.assertFalse(
            any(name.startswith("super-review-skill-repo/") for name in names)
        )
        self.assertFalse(any("ORIGINAL_REVIEW_PROMPT" in name for name in names))
        self.assertFalse(any(name.endswith("AGENTS.md") for name in names))

    def test_ci_actions_are_commit_pinned(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )
        uses = re.findall(r"(?m)^\s*-?\s*uses:\s*([^\s#]+)", workflow)
        self.assertTrue(uses)
        for action in uses:
            self.assertRegex(action, r"^[^@]+@[0-9a-f]{40}$", action)

    def test_no_repository_tool_targets_the_original_imported_zip(self) -> None:
        for path in (ROOT / "scripts").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("/mnt/data/", text)
            self.assertNotIn("Pasted text(6).txt", text)


if __name__ == "__main__":
    unittest.main()
