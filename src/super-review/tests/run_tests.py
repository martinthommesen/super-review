#!/usr/bin/env python3
"""Run the bundled regression suite from the trusted skill tree."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# The suite asserts the scripts tree stays free of bytecode; in-process helper
# imports must not write any even when the runner is launched without -B.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve(strict=True).parents[1]
TESTS = ROOT / "tests"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(SCRIPTS))


def main() -> int:
    suite = unittest.defaultTestLoader.discover(str(TESTS), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
