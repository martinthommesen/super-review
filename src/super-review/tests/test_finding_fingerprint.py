from __future__ import annotations

import unittest

import finding_fingerprint as ff


class FingerprintTests(unittest.TestCase):
    def test_normalization_is_stable(self) -> None:
        left = ff.Identity(
            "Defect or risk",
            "sec",
            "Auth\\Session",
            "  Missing   issuer validation  ",
        )
        right = ff.Identity(
            "defect or risk",
            "SEC",
            "auth/session",
            "missing issuer validation",
        )
        self.assertEqual(ff.compute_fingerprint(left), ff.compute_fingerprint(right))

    def test_volatile_evidence_is_not_part_of_identity(self) -> None:
        identity = ff.Identity(
            "Defect or risk", "COR", "service", "state transition skips validation"
        )
        self.assertRegex(ff.compute_fingerprint(identity), r"^sha256:[0-9a-f]{64}$")

    def test_empty_component_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "primary component"):
            ff.compute_fingerprint(ff.Identity("Defect or risk", "COR", "", "cause"))


if __name__ == "__main__":
    unittest.main()
