"""UTF-8 text + content digest wire contract for MCP tool inputs."""

from __future__ import annotations

import hashlib
import re

from super_review_companion import MCP_MAX_CONTENT_BYTES

DIGEST_RE = re.compile(r"^(?:sha256:)?([0-9a-fA-F]{64})$")


class WireError(ValueError):
    pass


def normalize_digest(value: str) -> str:
    match = DIGEST_RE.fullmatch(value)
    if not match:
        raise WireError("digest must be 64 hexadecimal characters or sha256:<64 hex>")
    return f"sha256:{match.group(1).lower()}"


def normalize_expected_digest(value: str) -> str:
    if value == "MISSING":
        return value
    return normalize_digest(value)


def encode_content(content: str, content_sha256: str) -> bytes:
    """Return immutable UTF-8 bytes after verifying the caller-supplied digest."""
    try:
        data = content.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise WireError(f"content is not encodable as UTF-8: {exc}") from exc
    if len(data) > MCP_MAX_CONTENT_BYTES:
        raise WireError(
            f"content exceeds MCP limit of {MCP_MAX_CONTENT_BYTES} bytes; "
            "use the skill-root CLI path commit with an on-disk candidate"
        )
    expected = normalize_digest(content_sha256)
    actual = f"sha256:{hashlib.sha256(data).hexdigest()}"
    if actual != expected:
        raise WireError(
            f"content_sha256 mismatch: expected {expected}, computed {actual}"
        )
    return data


def digest_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"
