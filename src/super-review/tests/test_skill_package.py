from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Pin a symlink-resolved temp root (the default macOS TMPDIR is a symlink)
# so temporary paths compare as physical paths.
tempfile.tempdir = str(Path(tempfile.gettempdir()).resolve())

ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTests(unittest.TestCase):
    def assert_no_script_bytecode(self) -> None:
        self.assertFalse((ROOT / "scripts" / "__pycache__").exists())
        self.assertEqual(list((ROOT / "scripts").glob("*.py[co]")), [])

    def test_frontmatter_is_portable_and_explicit_only(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertFalse(
            text.startswith("\ufeff"), "SKILL.md must not contain a UTF-8 BOM"
        )
        parts = text.split("---", 2)
        self.assertEqual(parts[0], "")
        frontmatter: dict[str, str] = {}
        for line in parts[1].splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

        self.assertEqual(set(frontmatter), {"name", "description"})
        self.assertEqual(frontmatter["name"], "super-review")
        self.assertEqual(ROOT.name, frontmatter["name"])
        self.assertRegex(frontmatter["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertTrue(frontmatter["description"])
        self.assertLessEqual(len(frontmatter["description"]), 1024)
        self.assertNotIn("<", frontmatter["description"])
        self.assertNotIn(">", frontmatter["description"])
        self.assertIn("$super-review", frontmatter["description"])
        self.assertIn("@super-review", frontmatter["description"])
        self.assertIn("/super-review", frontmatter["description"])

    def test_codex_policy_disables_implicit_invocation(self) -> None:
        policy = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertEqual(
            policy,
            "policy:\n  allow_implicit_invocation: false\n",
        )

    def test_all_relative_markdown_links_resolve(self) -> None:
        missing: list[str] = []
        for path in [ROOT / "SKILL.md", *(ROOT / "references").glob("*.md")]:
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (path.parent / target.split("#", 1)[0]).resolve()
                if not resolved.exists():
                    missing.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertEqual(missing, [])

    def test_references_are_linked_directly_from_skill(self) -> None:
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        linked_from_skill = {
            target.split("#", 1)[0]
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", skill_text)
            if target.startswith("references/")
        }
        expected = {
            f"references/{path.name}" for path in (ROOT / "references").glob("*.md")
        }
        self.assertEqual(linked_from_skill, expected)

        nested: list[str] = []
        for path in (ROOT / "references").glob("*.md"):
            for target in re.findall(
                r"\[[^\]]+\]\(([^)]+)\)",
                path.read_text(encoding="utf-8"),
            ):
                if "://" not in target and not target.startswith("#"):
                    nested.append(f"{path.name} -> {target}")
        self.assertEqual(nested, [])

    def test_no_target_relative_helper_invocations(self) -> None:
        checked = [ROOT / "SKILL.md", *(ROOT / "references").glob("*.md")]
        violations: list[str] = []
        for path in checked:
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1
            ):
                if re.search(r"python3(?:\s+-I)?\s+scripts/", line):
                    violations.append(f"{path.relative_to(ROOT)}:{number}: {line}")
        self.assertEqual(violations, [])

    def test_isolated_helpers_start_successfully(self) -> None:
        for script in (
            "finding_fingerprint.py",
            "validate_findings.py",
            "commit_findings.py",
        ):
            completed = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-B",
                    str(ROOT / "scripts" / script),
                    "--help",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(
                completed.returncode,
                0,
                f"{script} failed under isolated mode:\n{completed.stderr}",
            )
        self.assert_no_script_bytecode()

    def test_phase_applicability_is_linked(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/phase-applicability.md", text)

    def test_helpers_ignore_hostile_cwd_modules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            marker = cwd / "executed.txt"
            payload = (
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('executed', encoding='utf-8')\n"
                "raise RuntimeError('hostile cwd module loaded')\n"
            )
            (cwd / "validate_findings.py").write_text(payload, encoding="utf-8")
            (cwd / "finding_fingerprint.py").write_text(payload, encoding="utf-8")

            commands = [
                [
                    sys.executable,
                    "-I",
                    "-B",
                    str(ROOT / "scripts" / "commit_findings.py"),
                    "--help",
                ],
                [
                    sys.executable,
                    "-I",
                    "-B",
                    str(ROOT / "scripts" / "validate_findings.py"),
                    "--self-test",
                ],
            ]
            for command in commands:
                completed = subprocess.run(
                    command,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    completed.returncode,
                    0,
                    f"hostile-cwd isolation failed: {completed.stderr}",
                )
            self.assertFalse(marker.exists(), "a target-relative module was executed")
        self.assert_no_script_bytecode()


if __name__ == "__main__":
    unittest.main()
