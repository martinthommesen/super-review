"""FastMCP server wrapping trusted skill-root FINDINGS helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from super_review_companion import MCP_MAX_CONTENT_BYTES, __version__
from super_review_companion.skill_loaders import SkillLoadError, load_helpers
from super_review_companion.wire import (
    WireError,
    digest_bytes,
    encode_content,
    normalize_expected_digest,
)


def build_server(skill_root: Path, *, enable_commit: bool = False) -> FastMCP:
    helpers = load_helpers(skill_root)
    fingerprint_mod = helpers["fingerprint"]
    validate_mod = helpers["validate"]
    commit_mod = helpers["commit"]

    mcp = FastMCP(
        "super-review",
        instructions=(
            "Optional typed front-end for super-review FINDINGS helpers. "
            "Default to the skill-root CLI unless the user affirmed companion use "
            "and the host attested the active server's provenance. "
            "After any commit_findings success, always post-validate via the "
            "trusted CLI. Never treat server self-reports as a trust root."
        ),
    )

    @mcp.tool()
    def fingerprint_finding(
        record_type: str,
        category: str,
        primary_component: str,
        identity_statement: str,
    ) -> dict[str, Any]:
        """Compute a deterministic canonical-record fingerprint."""
        identity = fingerprint_mod.Identity(
            record_type=record_type,
            category=category,
            primary_component=primary_component,
            identity_statement=identity_statement,
        )
        fingerprint = fingerprint_mod.compute_fingerprint(identity)
        return {
            "fingerprint": fingerprint,
            "canonical_identity": fingerprint_mod.canonical_identity(identity),
        }

    @mcp.tool()
    def validate_findings(
        content: str,
        content_sha256: str,
        canonical_root: str | None = None,
    ) -> dict[str, Any]:
        """Validate UTF-8 FINDINGS candidate bytes via content + content_sha256."""
        try:
            data = encode_content(content, content_sha256)
        except WireError as exc:
            return {
                "ok": False,
                "errors": [str(exc)],
                "warnings": [],
                "mcp_max_content_bytes": MCP_MAX_CONTENT_BYTES,
            }
        result = validate_mod.validate_bytes(data, source="<mcp-content>")
        payload: dict[str, Any] = {
            "ok": result.ok,
            "errors": list(result.errors),
            "warnings": list(result.warnings),
            "content_sha256": digest_bytes(data),
            "mcp_max_content_bytes": MCP_MAX_CONTENT_BYTES,
        }
        if canonical_root is not None and result.ok:
            root_error = validate_mod.canonical_root_error(content, canonical_root)
            if root_error:
                payload["ok"] = False
                payload["errors"] = [root_error]
        return payload

    @mcp.tool()
    def snapshot_findings(path: str) -> dict[str, Any]:
        """Return exact on-disk FINDINGS.md bytes/digest, or MISSING if absent.

        The digest is advisory. Agents needing prior-report revalidation must use
        the returned content bytes when within the MCP size bound. Larger reports
        require the skill-root CLI snapshot. commit_bytes recomputes starting state.
        """
        target = Path(path)
        if target.name != "FINDINGS.md":
            return {
                "ok": False,
                "error": "snapshot path basename must be FINDINGS.md",
            }
        try:
            result = validate_mod.snapshot(target)
        except validate_mod.SnapshotError as exc:
            return {"ok": False, "error": str(exc)}
        size = 0 if result.data is None else len(result.data)
        payload: dict[str, Any] = {
            "ok": True,
            "status": result.status,
            "digest": result.digest,
            "size": size,
            "human_block_ids": result.human_block_ids(),
            "content": None,
            "content_sha256": None,
            "mcp_max_content_bytes": MCP_MAX_CONTENT_BYTES,
            "note": (
                "Snapshot digest is advisory; commit recomputes starting state. "
                "Use content bytes for prior-report revalidation when present."
            ),
        }
        if result.data is None:
            return payload
        if size > MCP_MAX_CONTENT_BYTES:
            payload["content"] = None
            payload["content_sha256"] = result.digest
            payload["note"] = (
                f"on-disk report is {size} bytes, above the MCP limit of "
                f"{MCP_MAX_CONTENT_BYTES}; use the skill-root CLI snapshot "
                "(`validate_findings.py --snapshot`) for exact bytes"
            )
            return payload
        try:
            payload["content"] = result.data.decode("utf-8")
            payload["content_sha256"] = result.digest
        except UnicodeDecodeError:
            payload["ok"] = False
            payload["error"] = (
                "on-disk report is not valid UTF-8; use the skill-root CLI snapshot"
            )
            payload["content"] = None
            payload["content_sha256"] = result.digest
        return payload

    if enable_commit:

        @mcp.tool()
        def commit_findings(
            repo_root: str,
            content: str,
            content_sha256: str,
            expected_sha256: str,
            lock_timeout: float = 30.0,
            dry_run: bool = False,
        ) -> dict[str, Any]:
            """Commit UTF-8 FINDINGS bytes when expected_sha256 still matches.

            Hosts must gate this tool behind explicit skill invocation approval.
            After success, always post-validate via the skill-root CLI.
            """
            try:
                data = encode_content(content, content_sha256)
                expected = normalize_expected_digest(expected_sha256)
            except WireError as exc:
                return {
                    "ok": False,
                    "status": "wire-error",
                    "error": str(exc),
                    "mcp_max_content_bytes": MCP_MAX_CONTENT_BYTES,
                    "post_validate_required": True,
                    "post_validate_hint": (
                        'python3 -I "$SKILL_ROOT/scripts/validate_findings.py" '
                        "--canonical-root <canonical-root> "
                        "<canonical-root>/FINDINGS.md"
                    ),
                }
            try:
                result = commit_mod.commit_bytes(
                    repo_root=Path(repo_root),
                    candidate_bytes=data,
                    expected_digest=expected,
                    lock_timeout=max(0.0, lock_timeout),
                    dry_run=dry_run,
                    source="<mcp-content>",
                )
            except commit_mod.ConflictError as exc:
                return {
                    "ok": False,
                    "status": "conflict",
                    "error": str(exc),
                    "post_validate_required": True,
                }
            except commit_mod.CommitError as exc:
                return {
                    "ok": False,
                    "status": "error",
                    "error": str(exc),
                    "post_validate_required": True,
                }
            except OSError as exc:
                return {
                    "ok": False,
                    "status": "io-error",
                    "error": str(exc),
                    "post_validate_required": True,
                }
            return {
                "ok": True,
                **result,
                "post_validate_required": True,
                "post_validate_hint": (
                    'python3 -I "$SKILL_ROOT/scripts/validate_findings.py" '
                    "--canonical-root <canonical-root> "
                    "<canonical-root>/FINDINGS.md"
                ),
                "companion_version": __version__,
            }

    return mcp


def create_server_from_args(
    skill_root: Path, *, enable_commit: bool = False
) -> FastMCP:
    try:
        return build_server(skill_root, enable_commit=enable_commit)
    except SkillLoadError as exc:
        raise SystemExit(f"error: {exc}") from exc
