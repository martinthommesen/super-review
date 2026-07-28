from __future__ import annotations

import hashlib
import unittest

from super_review_companion import MCP_MAX_CONTENT_BYTES
from super_review_companion.wire import WireError, encode_content, normalize_digest


class WireContractTests(unittest.TestCase):
    def test_round_trip_utf8(self) -> None:
        content = "café\n报告\n"
        digest = "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()
        self.assertEqual(encode_content(content, digest), content.encode("utf-8"))

    def test_digest_mismatch(self) -> None:
        with self.assertRaisesRegex(WireError, "content_sha256 mismatch"):
            encode_content("hello", "sha256:" + "0" * 64)

    def test_crlf_preserved(self) -> None:
        content = "line1\r\nline2\r\n"
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        self.assertEqual(encode_content(content, digest), content.encode("utf-8"))

    def test_oversize_rejected(self) -> None:
        content = "x" * (MCP_MAX_CONTENT_BYTES + 1)
        digest = "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()
        with self.assertRaisesRegex(WireError, "MCP limit"):
            encode_content(content, digest)

    def test_normalize_digest_prefix(self) -> None:
        raw = "A" * 64
        self.assertEqual(normalize_digest(raw), "sha256:" + "a" * 64)
        self.assertEqual(normalize_digest("sha256:" + raw), "sha256:" + "a" * 64)


if __name__ == "__main__":
    unittest.main()
