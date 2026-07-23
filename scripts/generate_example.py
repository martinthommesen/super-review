#!/usr/bin/env python3
"""Regenerate the valid example FINDINGS.md from canonical shipped fixtures."""

from __future__ import annotations

import importlib.util
import os
import stat
import sys
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve(strict=True).parents[1]
SKILL_ROOT = REPO_ROOT / "src" / "super-review"
TESTS_ROOT = SKILL_ROOT / "tests"
SCRIPTS_ROOT = SKILL_ROOT / "scripts"
OUTPUT = REPO_ROOT / "examples" / "FINDINGS.example.md"


def _load(name: str, path: Path) -> ModuleType:
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise RuntimeError(f"unsafe module path: {path}")
    spec = importlib.util.spec_from_file_location(name, path.resolve(strict=True))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    sys.path.insert(0, str(SCRIPTS_ROOT))
    factory = _load("_super_review_report_factory", TESTS_ROOT / "report_factory.py")
    records = [
        factory.make_defect(record_id="COR-001", severity="High"),
        factory.make_improvement(record_id="IMP-001", priority="Do not pursue"),
        factory.make_feature(record_id="FEAT-001", decision="Keep", priority="Later"),
        factory.make_positive(record_id="POS-001"),
    ]
    report = factory.build_report(records)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(report, encoding="utf-8", newline="\n")

    validator = _load("_super_review_validator", SCRIPTS_ROOT / "validate_findings.py")
    result = validator.validate_path(OUTPUT)
    if not result.ok:
        raise RuntimeError("generated example is invalid:\n" + "\n".join(result.errors))
    print(f"generated: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
