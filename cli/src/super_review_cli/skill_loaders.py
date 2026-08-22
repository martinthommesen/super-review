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
    """Validate a path as a regular, non-symbolic-link file.
    
    Parameters:
    	path (Path): Path to inspect.
    	label (str): Descriptive label used in validation errors.
    
    Returns:
    	Path: The strictly resolved file path."""
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise SkillLoadError(f"cannot inspect {label} {path}: {exc}") from exc
    if stat.S_ISLNK(info.st_mode):
        raise SkillLoadError(f"refusing symbolic-link {label}: {path}")
    if not stat.S_ISREG(info.st_mode):
        raise SkillLoadError(f"{label} must be a regular file: {path}")
    return path.resolve(strict=True)


def resolve_skill_root(skill_root: Path) -> Path:
    """
    Validate and resolve the root directory of a skill.
    
    Parameters:
    	skill_root (Path): Absolute path to the skill directory.
    
    Returns:
    	Path: Resolved skill-root path containing a regular `SKILL.md` file and a safe `scripts` directory.
    
    Raises:
    	SkillLoadError: If the path is invalid, inaccessible, symbolic-linked, or lacks the required skill files and directories.
    """
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
    resolved = root.resolve(strict=True)
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
    """
    Load a helper module from a skill's scripts directory.
    
    Parameters:
        skill_root (Path): Absolute path to the skill root.
        filename (str): Helper filename within the scripts directory.
        module_name (str): Name to assign to the loaded module.
    
    Returns:
        ModuleType: The loaded helper module.
    
    Raises:
        SkillLoadError: If the skill root, helper file, or module specification is invalid.
    """
    root = resolve_skill_root(skill_root)
    leaf = root / "scripts" / filename
    sibling = _require_regular_file(leaf, label="helper")
    if sibling.parent != (root / "scripts").resolve(strict=True):
        raise SkillLoadError(f"helper escapes skill scripts directory: {sibling}")
    spec = importlib.util.spec_from_file_location(module_name, sibling)
    if spec is None or spec.loader is None:
        raise SkillLoadError(f"cannot load helper: {sibling}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_helpers(skill_root: Path) -> dict[str, ModuleType]:
    """Load the skill's fingerprinting, validation, and commit helper modules.
    
    Parameters:
    	skill_root (Path): Root directory of the skill containing the helper scripts.
    
    Returns:
    	dict[str, ModuleType]: Helper modules keyed by ``"fingerprint"``, ``"validate"``, and ``"commit"``.
    """
    return {
        "fingerprint": load_helper(
            skill_root,
            "finding_fingerprint.py",
            "_super_review_companion_fingerprint",
        ),
        "validate": load_helper(
            skill_root,
            "validate_findings.py",
            "_super_review_companion_validate",
        ),
        "commit": load_helper(
            skill_root,
            "commit_findings.py",
            "_super_review_companion_commit",
        ),
    }
