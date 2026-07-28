from __future__ import annotations

import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve(strict=True).parents[2]
SKILL_ROOT = ROOT / "src" / "super-review"
SCRIPTS = SKILL_ROOT / "scripts"
TESTS = SKILL_ROOT / "tests"

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(SCRIPTS))

import report_factory as rf  # noqa: E402
from super_review_companion import MCP_MAX_CONTENT_BYTES  # noqa: E402
from super_review_companion.server import build_server  # noqa: E402
from super_review_companion.skill_loaders import (  # noqa: E402
    SkillLoadError,
    load_helpers,
)
from super_review_companion.wire import digest_bytes  # noqa: E402


def _tool_names(server: Any) -> set[str]:
    tools = asyncio.run(server.list_tools())
    return {tool.name for tool in tools}


def _call_tool(server: Any, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    _content, structured = asyncio.run(server.call_tool(name, arguments))
    assert isinstance(structured, dict)
    return structured


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
        self.assertEqual(
            _tool_names(server),
            {"fingerprint_finding", "validate_findings", "snapshot_findings"},
        )

    def test_enable_commit_exposes_write_tool(self) -> None:
        server = build_server(SKILL_ROOT, enable_commit=True)
        self.assertIn("commit_findings", _tool_names(server))

    def test_companion_does_not_import_private_validator_helpers(self) -> None:
        server_source = (
            ROOT / "companion" / "src" / "super_review_companion" / "server.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("_read_path_no_follow", server_source)
        loaders = (
            ROOT / "companion" / "src" / "super_review_companion" / "skill_loaders.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("_read_path_no_follow", loaders)

    def test_validate_tool_round_trip_and_digest_mismatch(self) -> None:
        server = build_server(SKILL_ROOT, enable_commit=False)
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            content = rf.build_report(canonical_root=str(repo))
            digest = digest_bytes(content.encode("utf-8"))
            ok = _call_tool(
                server,
                "validate_findings",
                {
                    "content": content,
                    "content_sha256": digest,
                    "canonical_root": str(repo),
                },
            )
            self.assertTrue(ok["ok"], ok)
            bad = _call_tool(
                server,
                "validate_findings",
                {"content": content, "content_sha256": "sha256:" + "0" * 64},
            )
            self.assertFalse(bad["ok"])
            self.assertTrue(
                any("content_sha256 mismatch" in error for error in bad["errors"])
            )

    def test_validate_tool_canonical_root_mismatch(self) -> None:
        server = build_server(SKILL_ROOT, enable_commit=False)
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            other = Path(temp_dir) / "other"
            repo.mkdir()
            other.mkdir()
            content = rf.build_report(canonical_root=str(repo))
            digest = digest_bytes(content.encode("utf-8"))
            result = _call_tool(
                server,
                "validate_findings",
                {
                    "content": content,
                    "content_sha256": digest,
                    "canonical_root": str(other),
                },
            )
            self.assertFalse(result["ok"])
            self.assertTrue(result["errors"])

    def test_snapshot_tool_missing_present_and_root_guard(self) -> None:
        server = build_server(SKILL_ROOT, enable_commit=False)
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            path = repo / "FINDINGS.md"
            missing = _call_tool(
                server, "snapshot_findings", {"repo_root": str(repo.resolve())}
            )
            self.assertTrue(missing["ok"])
            self.assertEqual(missing["status"], "missing")
            self.assertIsNone(missing["content"])

            content = rf.build_report(canonical_root=str(repo.resolve()))
            path.write_text(content, encoding="utf-8")
            present = _call_tool(
                server, "snapshot_findings", {"repo_root": str(repo.resolve())}
            )
            self.assertTrue(present["ok"])
            self.assertEqual(present["status"], "present")
            self.assertEqual(present["content"], content)
            self.assertEqual(present["path"], str(path.resolve()))

            relative = _call_tool(
                server,
                "snapshot_findings",
                {"repo_root": "repo"},
            )
            self.assertFalse(relative["ok"])
            self.assertIn("absolute", relative["error"])

            # Passing a file path (even FINDINGS.md) is refused; root must be a dir.
            as_file = _call_tool(
                server,
                "snapshot_findings",
                {"repo_root": str(path.resolve())},
            )
            self.assertFalse(as_file["ok"])

    def test_snapshot_tool_omits_oversize_content(self) -> None:
        server = build_server(SKILL_ROOT, enable_commit=False)
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            path = repo / "FINDINGS.md"
            # Bypass schema validation: snapshot returns exact bytes without validating.
            path.write_bytes(b"x" * (MCP_MAX_CONTENT_BYTES + 1))
            result = _call_tool(
                server, "snapshot_findings", {"repo_root": str(repo.resolve())}
            )
            self.assertTrue(result["ok"])
            self.assertEqual(result["size"], MCP_MAX_CONTENT_BYTES + 1)
            self.assertIsNone(result["content"])
            self.assertIn("above the MCP limit", result["note"])
            self.assertIn("--snapshot --json", result["note"])

    def test_commit_tool_round_trip_and_conflict(self) -> None:
        server = build_server(SKILL_ROOT, enable_commit=True)
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            content = rf.build_report(canonical_root=str(repo))
            digest = digest_bytes(content.encode("utf-8"))
            committed = _call_tool(
                server,
                "commit_findings",
                {
                    "repo_root": str(repo),
                    "content": content,
                    "content_sha256": digest,
                    "expected_sha256": "MISSING",
                },
            )
            self.assertTrue(committed["ok"], committed)
            self.assertEqual(committed["status"], "committed")
            self.assertTrue(committed["post_validate_required"])
            self.assertEqual(
                (repo / "FINDINGS.md").read_text(encoding="utf-8"), content
            )

            conflict = _call_tool(
                server,
                "commit_findings",
                {
                    "repo_root": str(repo),
                    "content": content,
                    "content_sha256": digest,
                    "expected_sha256": "MISSING",
                },
            )
            self.assertFalse(conflict["ok"])
            self.assertEqual(conflict["status"], "conflict")

            wire = _call_tool(
                server,
                "commit_findings",
                {
                    "repo_root": str(repo),
                    "content": content,
                    "content_sha256": "sha256:" + "0" * 64,
                    "expected_sha256": digest,
                },
            )
            self.assertFalse(wire["ok"])
            self.assertEqual(wire["status"], "wire-error")


if __name__ == "__main__":
    unittest.main()
