"""Remove project-generated caches without traversing dependency environments."""

from __future__ import annotations

import contextlib
import os
import shutil
import stat
from pathlib import Path
from typing import Iterable, Iterator

PRUNED_DIRECTORIES = frozenset({".git", ".venv", "dist", "node_modules"})


class SafeCleanupUnavailable(RuntimeError):
    """The platform cannot keep cleanup bound to opened directories."""


class CleanupConflictError(RuntimeError):
    """A cleanup root changed while it was in use."""


def _raise_walk_error(error: OSError) -> None:
    raise error


def _require_safe_cleanup(*, list_directory: bool = False) -> None:
    unavailable = [
        name
        for name, operation in (
            ("openat", os.open),
            ("fstatat", os.stat),
            ("unlinkat", os.unlink),
        )
        if operation not in os.supports_dir_fd
    ]
    if not hasattr(os, "fwalk"):
        unavailable.append("fwalk")
    if not getattr(os, "O_DIRECTORY", 0):
        unavailable.append("O_DIRECTORY")
    if not getattr(os, "O_NOFOLLOW", 0):
        unavailable.append("O_NOFOLLOW")
    if os.stat not in os.supports_follow_symlinks:
        unavailable.append("no-follow stat")
    if not getattr(shutil.rmtree, "avoids_symlink_attacks", False):
        unavailable.append("fd-safe rmtree")
    if list_directory and os.listdir not in os.supports_fd:
        unavailable.append("descriptor listdir")
    if unavailable:
        detail = ", ".join(unavailable)
        raise SafeCleanupUnavailable(
            f"descriptor-safe cleanup is unavailable ({detail})"
        )


def _same_identity(left: os.stat_result, right: os.stat_result) -> bool:
    return (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)


@contextlib.contextmanager
def _pinned_directory(
    path: Path, *, missing_ok: bool = False, list_directory: bool = False
) -> Iterator[tuple[Path, int] | None]:
    _require_safe_cleanup(list_directory=list_directory)
    requested = path.expanduser()
    if not requested.is_absolute():
        requested = Path.cwd() / requested
    try:
        before = os.lstat(requested)
    except FileNotFoundError:
        if missing_ok:
            yield None
            return
        raise
    if stat.S_ISLNK(before.st_mode):
        raise SafeCleanupUnavailable(
            f"refusing symbolic-link cleanup root: {requested}"
        )
    if not stat.S_ISDIR(before.st_mode):
        raise SafeCleanupUnavailable(f"cleanup root is not a directory: {requested}")

    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    directory_fd = os.open(requested, flags)
    try:
        opened = os.fstat(directory_fd)
        if not stat.S_ISDIR(opened.st_mode) or not _same_identity(before, opened):
            raise CleanupConflictError(
                f"cleanup root changed while being opened: {requested}"
            )
        yield requested, directory_fd
        try:
            after = os.lstat(requested)
        except OSError as exc:
            raise CleanupConflictError(
                f"cleanup root changed during traversal: {requested}: {exc}"
            ) from exc
        if (
            not stat.S_ISDIR(after.st_mode)
            or not _same_identity(opened, after)
            or not _same_identity(opened, os.fstat(directory_fd))
        ):
            raise CleanupConflictError(
                f"cleanup root changed during traversal: {requested}"
            )
    finally:
        os.close(directory_fd)


def iter_project_paths(
    root: Path, *, pruned_directories: Iterable[str] = PRUNED_DIRECTORIES
) -> Iterator[Path]:
    """Yield project paths without descending into generated or dependency trees."""
    pruned = frozenset(pruned_directories)
    for current, child_directories, filenames in os.walk(
        root, topdown=True, onerror=_raise_walk_error, followlinks=False
    ):
        current_path = Path(current)
        retained: list[str] = []
        for name in child_directories:
            path = current_path / name
            if name in pruned:
                continue
            yield path
            if not path.is_symlink():
                retained.append(name)
        child_directories[:] = retained
        for filename in filenames:
            yield current_path / filename


def remove_generated(
    root: Path,
    *,
    directory_names: Iterable[str],
    suffixes: Iterable[str],
) -> None:
    removable_directories = frozenset(directory_names)
    removable_suffixes = frozenset(suffixes)
    with _pinned_directory(root) as pinned:
        assert pinned is not None
        _, root_fd = pinned
        for _, child_directories, filenames, current_fd in os.fwalk(
            ".",
            topdown=True,
            onerror=_raise_walk_error,
            follow_symlinks=False,
            dir_fd=root_fd,
        ):
            retained: list[str] = []
            for name in child_directories:
                if name in PRUNED_DIRECTORIES:
                    continue
                try:
                    info = os.stat(name, dir_fd=current_fd, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                if stat.S_ISLNK(info.st_mode):
                    continue
                if not stat.S_ISDIR(info.st_mode):
                    raise CleanupConflictError(
                        f"directory entry changed during cleanup: {name}"
                    )
                if name in removable_directories:
                    shutil.rmtree(name, dir_fd=current_fd)
                    continue
                retained.append(name)
            child_directories[:] = retained
            for filename in filenames:
                if Path(filename).suffix not in removable_suffixes:
                    continue
                try:
                    info = os.stat(filename, dir_fd=current_fd, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                if stat.S_ISLNK(info.st_mode):
                    continue
                os.unlink(filename, dir_fd=current_fd)


def remove_directory_contents(
    directory: Path, *, preserve_names: Iterable[str] = (), missing_ok: bool = False
) -> None:
    """Remove direct children without following the directory or child symlinks."""
    preserved = frozenset(preserve_names)
    with _pinned_directory(
        directory, missing_ok=missing_ok, list_directory=True
    ) as pinned:
        if pinned is None:
            return
        _, directory_fd = pinned
        for name in os.listdir(directory_fd):
            if name in preserved:
                continue
            try:
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            if stat.S_ISDIR(info.st_mode):
                shutil.rmtree(name, dir_fd=directory_fd)
            else:
                os.unlink(name, dir_fd=directory_fd)
