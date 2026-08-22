"""Load shipped skill helpers by absolute skill-root path only."""

from __future__ import annotations

import importlib.util
import os
import stat
import sys
from pathlib import Path
from types import ModuleType


class SkillLoadError(RuntimeError):
    pass


def _require_regular_file(path: Path, *, label: str) -> Path:
    """Reject symlinks and non-regular files, then resolve the path."""
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise SkillLoadError(f"cannot inspect {label} {path}: {exc}") from exc
    if stat.S_ISLNK(info.st_mode):
        raise SkillLoadError(f"refusing symbolic-link {label}: {path}")
    if not stat.S_ISREG(info.st_mode):
        raise SkillLoadError(f"{label} must be a regular file: {path}")
    try:
        return path.resolve(strict=True)
    except OSError as exc:
        raise SkillLoadError(f"cannot resolve {label} {path}: {exc}") from exc


def resolve_skill_root(skill_root: Path) -> Path:
    """Validate an absolute skill root and its required files."""
    root = skill_root.expanduser()
    if not root.is_absolute():
        raise SkillLoadError(f"skill root must be an absolute path, got {skill_root}")
    try:
        info = os.lstat(root)
    except OSError as exc:
        raise SkillLoadError(f"cannot inspect skill root {root}: {exc}") from exc
    if stat.S_ISLNK(info.st_mode):
        raise SkillLoadError(f"refusing symbolic-link skill root: {root}")
    if not stat.S_ISDIR(info.st_mode):
        raise SkillLoadError(f"skill root is not a directory: {root}")
    try:
        resolved = root.resolve(strict=True)
    except OSError as exc:
        raise SkillLoadError(f"cannot resolve skill root {root}: {exc}") from exc
    skill_md = resolved / "SKILL.md"
    _require_regular_file(skill_md, label="SKILL.md")
    scripts = resolved / "scripts"
    try:
        scripts_info = os.lstat(scripts)
    except OSError as exc:
        raise SkillLoadError(f"cannot inspect skill scripts directory: {exc}") from exc
    if stat.S_ISLNK(scripts_info.st_mode) or not stat.S_ISDIR(scripts_info.st_mode):
        raise SkillLoadError(f"unsafe skill scripts directory: {scripts}")
    return resolved


def load_helper(skill_root: Path, filename: str, module_name: str) -> ModuleType:
    """Load one helper from the validated skill scripts directory."""
    root = resolve_skill_root(skill_root)
    leaf = root / "scripts" / filename
    sibling = _require_regular_file(leaf, label="helper")
    try:
        scripts_dir = (root / "scripts").resolve(strict=True)
    except OSError as exc:
        raise SkillLoadError(f"cannot resolve skill scripts directory: {exc}") from exc
    if sibling.parent != scripts_dir:
        raise SkillLoadError(f"helper escapes skill scripts directory: {sibling}")
    spec = importlib.util.spec_from_file_location(module_name, sibling)
    if spec is None or spec.loader is None:
        raise SkillLoadError(f"cannot load helper: {sibling}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
