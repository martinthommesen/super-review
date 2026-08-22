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

        claude_settings = json.loads(
            (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
        )
        hook_command = claude_settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.assertIn("normcase", hook_command)

        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("$(UV) run --locked coverage", makefile)
        self.assertNotRegex(makefile, r"\$\(UV\) run (?!--locked)")
        self.assertIn("$(PYTHON_ENV) $(UV) sync --locked", makefile)
        self.assertRegex(makefile, r"(?m)^release: .*\bcli-test\b")

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

    def test_root_entrypoint_scripts_are_executable(self) -> None:
        for path in sorted((ROOT / "scripts").glob("*.py")):
            if not path.read_bytes().startswith(b"#!"):
                continue
            mode = stat.S_IMODE(path.stat().st_mode)
            self.assertTrue(mode & 0o111, f"not executable: {path.name} ({oct(mode)})")

    def test_workspace_hygiene_preserves_dependency_environments(self) -> None:
        hygiene = load_module(
            "_workbench_workspace_hygiene", ROOT / "scripts" / "workspace_hygiene.py"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_cache = root / "src" / "__pycache__"
            environment_cache = root / ".venv" / "lib" / "__pycache__"
            distribution_cache = root / "dist" / "__pycache__"
            for cache in (source_cache, environment_cache, distribution_cache):
                cache.mkdir(parents=True)
                (cache / "module.pyc").write_bytes(b"cache")
            hygiene.remove_generated(
                root,
                directory_names=("__pycache__",),
                suffixes=(".pyc", ".pyo"),
            )
            self.assertFalse(source_cache.exists())
            self.assertTrue((environment_cache / "module.pyc").exists())
            self.assertTrue((distribution_cache / "module.pyc").exists())

            visited = set(hygiene.iter_project_paths(root))
            self.assertIn(root / "src", visited)
            visited_parts = {path.relative_to(root).parts for path in visited}
            self.assertFalse(
                any(parts and parts[0] == ".venv" for parts in visited_parts)
            )
            self.assertFalse(
                any(parts and parts[0] == "dist" for parts in visited_parts)
            )

    def test_workspace_cleanup_stays_bound_to_opened_directory(self) -> None:
        hygiene = load_module(
            "_workbench_workspace_hygiene_bound",
            ROOT / "scripts" / "workspace_hygiene.py",
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "repo"
            pivot = root / "pivot"
            moved = root / "pivot-original"
            local_cache = pivot / "__pycache__"
            outside_cache = base / "outside" / "__pycache__"
            local_cache.mkdir(parents=True)
            outside_cache.mkdir(parents=True)
            (local_cache / "local.pyc").write_bytes(b"local")
            outside_victim = outside_cache / "outside.pyc"
            outside_victim.write_bytes(b"outside")
            probe = root / "symlink-probe"
            try:
                probe.symlink_to(base / "outside", target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            probe.unlink()

            original_fwalk = hygiene.os.fwalk
            swapped = False

            def swap_before_descendant_yield(*args, **kwargs):
                nonlocal swapped
                for item in original_fwalk(*args, **kwargs):
                    current = item[0]
                    if not swapped and Path(current) == Path("pivot"):
                        pivot.rename(moved)
                        pivot.symlink_to(base / "outside", target_is_directory=True)
                        swapped = True
                    yield item

            with mock.patch.object(
                hygiene.os, "fwalk", side_effect=swap_before_descendant_yield
            ):
                hygiene.remove_generated(
                    root,
                    directory_names=("__pycache__",),
                    suffixes=(".pyc", ".pyo"),
                )

            self.assertTrue(swapped)
            self.assertTrue(outside_victim.exists())
            self.assertFalse((moved / "__pycache__").exists())

    def test_workspace_cleanup_rejects_leaf_symlink_swap(self) -> None:
        hygiene = load_module(
            "_workbench_workspace_hygiene_leaf_swap",
            ROOT / "scripts" / "workspace_hygiene.py",
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "repo"
            cache = root / "src" / "__pycache__"
            moved = root / "src" / "saved-cache"
            outside = base / "outside"
            cache.mkdir(parents=True)
            outside.mkdir()
            (cache / "local.pyc").write_bytes(b"local")
            outside_victim = outside / "outside.pyc"
            outside_victim.write_bytes(b"outside")
            probe = root / "symlink-probe"
            try:
                probe.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            probe.unlink()

            original_rmtree = hygiene.shutil.rmtree
            injected = False

            def swap_then_remove(path, *args, **kwargs):
                nonlocal injected
                if not injected:
                    cache.rename(moved)
                    cache.symlink_to(outside, target_is_directory=True)
                    injected = True
                return original_rmtree(path, *args, **kwargs)

            guarded_rmtree = mock.Mock(side_effect=swap_then_remove)
            guarded_rmtree.avoids_symlink_attacks = True
            with mock.patch.object(hygiene.shutil, "rmtree", guarded_rmtree):
                with self.assertRaises(OSError):
                    hygiene.remove_generated(
                        root,
                        directory_names=("__pycache__",),
                        suffixes=(".pyc", ".pyo"),
                    )

            self.assertTrue(injected)
            self.assertTrue(outside_victim.exists())
            self.assertTrue((moved / "local.pyc").exists())

    def test_workspace_cleanup_fails_closed_without_safe_rmtree(self) -> None:
        hygiene = load_module(
            "_workbench_workspace_hygiene_capability",
            ROOT / "scripts" / "workspace_hygiene.py",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "__pycache__"
            cache.mkdir()
            with mock.patch.object(
                hygiene.shutil.rmtree, "avoids_symlink_attacks", False
            ):
                with self.assertRaisesRegex(
                    hygiene.SafeCleanupUnavailable, "fd-safe rmtree"
                ):
                    hygiene.remove_generated(
                        root,
                        directory_names=("__pycache__",),
                        suffixes=(".pyc", ".pyo"),
                    )
            self.assertTrue(cache.exists())

    def test_directory_contents_cleanup_refuses_symlink_root(self) -> None:
        hygiene = load_module(
            "_workbench_workspace_hygiene_contents",
            ROOT / "scripts" / "workspace_hygiene.py",
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            outside = base / "outside"
            outside.mkdir()
            victim = outside / "artifact.zip"
            victim.write_bytes(b"outside")
            dist = base / "dist"
            try:
                dist.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            with self.assertRaisesRegex(
                hygiene.SafeCleanupUnavailable, "symbolic-link cleanup root"
            ):
                hygiene.remove_directory_contents(
                    dist, preserve_names=(".gitkeep",), missing_ok=True
                )
            self.assertEqual(victim.read_bytes(), b"outside")

    def test_directory_contents_cleanup_preserves_named_files(self) -> None:
        hygiene = load_module(
            "_workbench_workspace_hygiene_contents_control",
            ROOT / "scripts" / "workspace_hygiene.py",
        )
        with tempfile.TemporaryDirectory() as directory:
            dist = Path(directory) / "dist"
            nested = dist / "package"
            nested.mkdir(parents=True)
            keep = dist / ".gitkeep"
            keep.write_bytes(b"keep")
            (dist / "artifact.zip").write_bytes(b"artifact")
            (nested / "module.py").write_bytes(b"source")

            hygiene.remove_directory_contents(
                dist, preserve_names=(".gitkeep",), missing_ok=True
            )

            self.assertEqual(keep.read_bytes(), b"keep")
            self.assertEqual([path.name for path in dist.iterdir()], [".gitkeep"])

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
        for relative in ("src/LICENSE", "src/super-review/LICENSE", "cli/LICENSE"):
            self.assertEqual((ROOT / relative).read_bytes(), root_license, relative)

    def test_mode_normalization_matches_between_build_and_verify(self) -> None:
        build = load_module("_workbench_build_modes", ROOT / "scripts" / "build.py")
        verify = load_module(
            "_workbench_verify_modes", ROOT / "scripts" / "verify_dist.py"
        )
        for source_mode, archive_mode in {
            0o400: 0o644,
            0o444: 0o644,
            0o600: 0o644,
            0o640: 0o644,
            0o664: 0o644,
            0o500: 0o755,
            0o555: 0o755,
            0o700: 0o755,
            0o750: 0o755,
            0o775: 0o755,
        }.items():
            self.assertEqual(
                build._normalized_mode(source_mode), archive_mode, oct(source_mode)
            )
            self.assertEqual(
                verify._normalized_mode(source_mode), archive_mode, oct(source_mode)
            )

    def test_build_normalizes_restrictive_source_modes(self) -> None:
        build = load_module(
            "_workbench_build_restrictive", ROOT / "scripts" / "build.py"
        )
        verify = load_module(
            "_workbench_verify_restrictive", ROOT / "scripts" / "verify_dist.py"
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "skill"
            (source / "scripts").mkdir(parents=True)
            plain = source / "SKILL.md"
            plain.write_text("stub\n", encoding="utf-8")
            plain.chmod(0o600)
            executable = source / "scripts" / "validate_findings.py"
            executable.write_text("print('stub')\n", encoding="utf-8")
            executable.chmod(0o700)
            artifact = base / "super-review-skill.zip"
            with (
                mock.patch.object(build, "SOURCE_ROOT", source),
                mock.patch.object(verify, "SOURCE_ROOT", source),
            ):
                build.build(artifact)
                verify.verify(artifact, run_tests=False)
            with zipfile.ZipFile(artifact) as archive:
                modes = {
                    info.filename: (info.external_attr >> 16) & 0o777
                    for info in archive.infolist()
                }
        self.assertEqual(modes["super-review/SKILL.md"], 0o644)
        self.assertEqual(modes["super-review/scripts/validate_findings.py"], 0o755)

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
