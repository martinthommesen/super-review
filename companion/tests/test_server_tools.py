from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve(strict=True).parents[2]
SKILL_ROOT = ROOT / "src" / "super-review"
SCRIPTS = SKILL_ROOT / "scripts"
TESTS = SKILL_ROOT / "tests"

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(SCRIPTS))

import report_factory as rf  # noqa: E402
from super_review_companion.server import build_server  # noqa: E402
from super_review_companion.skill_loaders import (  # noqa: E402
    SkillLoadError,
    load_helpers,
)
from super_review_companion.wire import digest_bytes, encode_content  # noqa: E402


def _tool_map(server):  # type: ignore[no-untyped-def]
    # FastMCP stores tools in an internal registry; exercise via list + call helpers.
    tools = getattr(server, "_tool_manager").list_tools()
    return {tool.name: tool for tool in tools}


class CompanionServerTests(unittest.TestCase):
    def test_load_helpers_from_absolute_skill_root(self) -> None:
        helpers = load_helpers(SKILL_ROOT)
        self.assertIn("validate", helpers)
        self.assertTrue(hasattr(helpers["validate"], "snapshot"))
        self.assertTrue(hasattr(helpers["commit"], "commit_bytes"))

    def test_relative_skill_root_rejected(self) -> None:
        with self.assertRaises(SkillLoadError):
            load_helpers(Path("src/super-review"))

    def test_default_server_omits_commit_tool(self) -> None:
        server = build_server(SKILL_ROOT, enable_commit=False)
        names = set(_tool_map(server))
        self.assertEqual(
            names,
            {"fingerprint_finding", "validate_findings", "snapshot_findings"},
        )

    def test_enable_commit_exposes_write_tool(self) -> None:
        server = build_server(SKILL_ROOT, enable_commit=True)
        self.assertIn("commit_findings", _tool_map(server))

    def test_validate_and_commit_bytes_round_trip(self) -> None:
        helpers = load_helpers(SKILL_ROOT)
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            content = rf.build_report(canonical_root=str(repo))
            data = content.encode("utf-8")
            digest = digest_bytes(data)
            self.assertEqual(encode_content(content, digest), data)
            validation = helpers["validate"].validate_bytes(data)
            self.assertTrue(validation.ok, validation.errors)
            result = helpers["commit"].commit_bytes(
                repo_root=repo,
                candidate_bytes=data,
                expected_digest="MISSING",
                lock_timeout=1.0,
                dry_run=False,
            )
            self.assertEqual(result["status"], "committed")
            self.assertEqual((repo / "FINDINGS.md").read_bytes(), data)
            snap = helpers["validate"].snapshot(repo / "FINDINGS.md")
            self.assertEqual(snap.status, "present")
            self.assertEqual(snap.data, data)

    def test_companion_does_not_import_private_validator_helpers(self) -> None:
        server_source = (
            ROOT / "companion" / "src" / "super_review_companion" / "server.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("_read_path_no_follow", server_source)
        loaders = (
            ROOT / "companion" / "src" / "super_review_companion" / "skill_loaders.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("_read_path_no_follow", loaders)


if __name__ == "__main__":
    unittest.main()
