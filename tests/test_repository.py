from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import stat
import sys
import tempfile
import tomllib
import unittest
import zipfile
from pathlib import Path
from types import ModuleType
from unittest import mock

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
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertIn(f"Version: {version}", skill_text)
        self.assertRegex(pyproject, rf'(?m)^version = "{re.escape(version)}"$')
        self.assertIn(f"## [{version}]", changelog)
        self.assertIn(f"current skill version is **{version}**", readme)

        for relative in (
            "src/.claude-plugin/plugin.json",
            "src/.codex-plugin/plugin.json",
            "src/plugin.json",
            ".cursor-plugin/plugin.json",
        ):
            manifest = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual(manifest["version"], version, relative)

        for relative in (
            ".claude-plugin/marketplace.json",
            ".github/plugin/marketplace.json",
        ):
            marketplace = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual(marketplace["plugins"][0]["version"], version, relative)

        copilot_marketplace = json.loads(
            (ROOT / ".github" / "plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(copilot_marketplace["metadata"]["version"], version)

        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn(
            "The current development line named in `VERSION` receives fixes",
            security,
        )

    def test_marketplace_adapters_target_canonical_skill(self) -> None:
        adapters = (
            (
                ".claude-plugin/marketplace.json",
                ".claude-plugin/plugin.json",
                "commands",
                ["./client-adapters/commands/super-review.md"],
            ),
            (
                ".github/plugin/marketplace.json",
                "plugin.json",
                "commands",
                ["./client-adapters/commands"],
            ),
            (
                ".agents/plugins/marketplace.json",
                ".codex-plugin/plugin.json",
                "skills",
                ["./super-review"],
            ),
        )
        expected_plugin_root = (ROOT / "src").resolve(strict=True)

        for (
            marketplace_relative,
            manifest_relative,
            component_field,
            expected_component_paths,
        ) in adapters:
            marketplace = json.loads(
                (ROOT / marketplace_relative).read_text(encoding="utf-8")
            )
            self.assertEqual(marketplace["name"], "super-review")
            self.assertEqual(len(marketplace["plugins"]), 1)
            entry = marketplace["plugins"][0]
            self.assertEqual(entry["name"], "super-review")

            source = entry["source"]
            if isinstance(source, dict):
                self.assertEqual(source["source"], "local")
                source_path = source["path"]
            else:
                source_path = source
            self.assertTrue(source_path.startswith("./"))
            plugin_root = (ROOT / source_path).resolve(strict=True)
            self.assertEqual(plugin_root, expected_plugin_root)

            manifest_path = plugin_root / manifest_relative
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["name"], "super-review")
            component_paths = manifest[component_field]
            if isinstance(component_paths, str):
                component_paths = [component_paths]
            self.assertEqual(component_paths, expected_component_paths)

            if component_field == "commands":
                command_path = plugin_root / component_paths[0]
                if command_path.is_dir():
                    command_path /= "super-review.md"
                command = command_path.read_text(encoding="utf-8")
                canonical_link = (
                    command_path.parent / "../../super-review/SKILL.md"
                ).resolve(strict=True)
                self.assertEqual(
                    canonical_link, (SKILL / "SKILL.md").resolve(strict=True)
                )
                self.assertNotIn("disable-model-invocation", command)
                self.assertIn("../../super-review/SKILL.md", command)
                self.assertIn("$ARGUMENTS", command)
            else:
                for skill_path in component_paths:
                    resolved = (plugin_root / skill_path).resolve(strict=True)
                    self.assertEqual(resolved, SKILL.resolve(strict=True))
                    self.assertTrue((resolved / "SKILL.md").is_file())

        codex_marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            codex_marketplace["plugins"][0]["policy"],
            {
                "installation": "AVAILABLE",
                "authentication": "ON_INSTALL",
            },
        )
        codex_manifest = json.loads(
            (ROOT / "src" / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            codex_manifest["interface"]["defaultPrompt"],
            [
                "$super-review:super-review audit this repository and update its "
                "canonical FINDINGS.md."
            ],
        )

    def test_cursor_plugin_targets_canonical_skill_only(self) -> None:
        manifest = json.loads(
            (ROOT / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "super-review")
        skills = manifest["skills"]
        if isinstance(skills, str):
            skills = [skills]
        self.assertEqual(skills, ["./src/super-review"])
        for skill_path in skills:
            resolved = (ROOT / skill_path).resolve(strict=True)
            self.assertEqual(resolved, SKILL.resolve(strict=True))
            self.assertTrue((resolved / "SKILL.md").is_file())

        commands = manifest["commands"]
        if isinstance(commands, str):
            commands = [commands]
        self.assertEqual(commands, ["./src/client-adapters/cursor/commands"])
        command_path = ROOT / commands[0] / "super-review.md"
        command = command_path.read_text(encoding="utf-8")
        self.assertIn("name: super-review", command)
        self.assertIn("../../../super-review/SKILL.md", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertNotIn("disable-model-invocation", command)
        canonical_link = (
            command_path.parent / "../../../super-review/SKILL.md"
        ).resolve(strict=True)
        self.assertEqual(canonical_link, (SKILL / "SKILL.md").resolve(strict=True))

        # The plugin registers no MCP server (decision D15): the consolidated
        # CLI replaced the companion, so there is no ambient tool surface for
        # Auto-run to invoke. Its executable smoke lives in cli/tests/.
        self.assertNotIn("mcpServers", manifest)
        self.assertFalse(
            (ROOT / "src" / "client-adapters" / "cursor" / "mcp.json").exists()
        )
        self.assertFalse((ROOT / "companion").exists())

    def test_original_prompt_provenance(self) -> None:
        prompt = ROOT / "docs" / "ORIGINAL_REVIEW_PROMPT.md"
        checksum = ROOT / "docs" / "ORIGINAL_REVIEW_PROMPT.sha256"
        expected, filename = checksum.read_text(encoding="utf-8").split()
        self.assertEqual(filename, prompt.name)
        self.assertEqual(hashlib.sha256(prompt.read_bytes()).hexdigest(), expected)
        self.assertEqual(len(prompt.read_text(encoding="utf-8").splitlines()), 3201)

    def test_direct_install_docs_preserve_explicit_invocation(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        direct_install = readme.split("### Direct skill installation", 1)[1].split(
            "## Usage", 1
        )[0]
        self.assertNotIn(".claude/skills", direct_install)
        self.assertIn("Codex", direct_install)
        self.assertIn(
            "Use the marketplace installation for Claude Code and GitHub Copilot CLI",
            direct_install,
        )

    def test_required_workbench_documents_exist(self) -> None:
        for relative in (
            "AGENTS.md",
            "README.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CHANGELOG.md",
            ".pre-commit-config.yaml",
            ".env.example",
            ".github/CODEOWNERS",
            ".claude/agents/workbench-validator.md",
            ".claude/commands/check.md",
            ".claude/commands/lint.md",
            ".cursor/rules/workbench.mdc",
            ".cursor/skills/workbench-validate/SKILL.md",
            "docs/AGENT_OPERATIONS.md",
            "docs/ARCHITECTURE.md",
            "docs/DECISIONS.md",
            "docs/RELEASE.md",
            "docs/REVIEW_HISTORY.md",
            "docs/PROVENANCE.md",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_agent_host_integration_files_have_expected_shape(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("make cli-test", agents)
        self.assertIn("python3 scripts/check.py", agents)
        self.assertIn("Do not commit, push, publish, deploy", agents)

        pre_commit = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        self.assertIn("id: ruff-check", pre_commit)
        self.assertIn("id: cli-check", pre_commit)
        self.assertRegex(pre_commit, r"(?m)^\s*entry:\s*ty check\s*$")
        self.assertIn("files: ^cli/", pre_commit)

        for relative in (
            ".claude/commands/check.md",
            ".claude/commands/lint.md",
            ".claude/agents/workbench-validator.md",
            ".cursor/skills/workbench-validate/SKILL.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("cli-test", text, relative)

        rule = (ROOT / ".cursor" / "rules" / "workbench.mdc").read_text(
            encoding="utf-8"
        )
        self.assertIn("alwaysApply: true", rule)
        self.assertIn("cli-test", rule)

        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("$(UV) run coverage", makefile)
        self.assertNotRegex(makefile, r"(?m)^\t\$\(PYTHON_ENV\) uv run coverage")

    def test_pre_commit_ruff_rev_matches_dev_pin(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
        pre_commit = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        ruff_pins = [
            dep.removeprefix("ruff==")
            for dep in pyproject.get("dependency-groups", {}).get("dev", [])
            if isinstance(dep, str) and dep.startswith("ruff==")
        ]
        self.assertEqual(len(ruff_pins), 1, ruff_pins)
        pinned = ruff_pins[0]
        requirements_match = re.search(r"(?m)^ruff==(\S+)\s*$", requirements)
        self.assertIsNotNone(requirements_match)
        assert requirements_match is not None
        self.assertEqual(pinned, requirements_match.group(1))
        rev_match = re.search(
            r"(?ms)repo:\s*https://github\.com/astral-sh/ruff-pre-commit\s*\n"
            r"\s*rev:\s*(v?[^\s#]+)",
            pre_commit,
        )
        self.assertIsNotNone(rev_match, "ruff-pre-commit rev missing")
        assert rev_match is not None
        rev = rev_match.group(1).removeprefix("v")
        self.assertEqual(rev, pinned)

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
        example = ROOT / "examples" / "FINDINGS.example.md"
        result = validator.validate_path(example)
        self.assertTrue(result.ok, result.errors)
        stated_root = validator.stated_canonical_root(
            example.read_text(encoding="utf-8")
        )
        self.assertIsInstance(stated_root, str)
        with mock.patch.object(validator.os, "name", "nt"):
            self.assertTrue(validator._is_absolute_canonical_root(stated_root))

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
        self.assertIn("super-review/LICENSE", names)
        self.assertFalse(
            any(name.startswith("super-review-skill-repo/") for name in names)
        )
        self.assertFalse(any("ORIGINAL_REVIEW_PROMPT" in name for name in names))
        self.assertFalse(any(name.endswith("AGENTS.md") for name in names))

    def test_distributed_license_copies_match_root_license(self) -> None:
        # Apache-2.0 section 4 requires recipients to receive the license text,
        # so every distributable payload carries a byte-identical copy.
        root_license = (ROOT / "LICENSE").read_bytes()
        self.assertIn(b"Apache License", root_license)
        for relative in ("src/LICENSE", "src/super-review/LICENSE"):
            self.assertEqual((ROOT / relative).read_bytes(), root_license, relative)

    def test_archive_license_bytes_match_root_license(self) -> None:
        build = load_module("_workbench_build_license", ROOT / "scripts" / "build.py")
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "super-review-skill.zip"
            build.build(artifact)
            with zipfile.ZipFile(artifact) as archive:
                archived = archive.read("super-review/LICENSE")
        self.assertEqual(archived, (ROOT / "LICENSE").read_bytes())

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
