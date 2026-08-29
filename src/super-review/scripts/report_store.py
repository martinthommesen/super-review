"""Descriptor-bound exact-byte storage for ``FINDINGS.md`` helpers.

Report grammar stays in ``validate_findings.py``. This module owns filesystem
identity, advisory locking, staging, publication, and final byte verification.
"""

from __future__ import annotations

import contextlib
import ctypes
import errno
import hashlib
import os
import secrets
import stat
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO, Callable, Literal


class StoreError(RuntimeError):
    """Base class for rejected or unstable filesystem state."""


class UnsafePathError(StoreError):
    """A requested directory or leaf is not a safe regular filesystem object."""


class StoreConflictError(StoreError):
    """Filesystem state changed during a guarded operation."""


class SafePublicationUnavailable(OSError):
    """The platform cannot provide the required publication guarantees."""


@dataclass(frozen=True)
class FileIdentity:
    device: int
    inode: int

    @classmethod
    def from_stat(cls, value: os.stat_result) -> "FileIdentity":
        return cls(value.st_dev, value.st_ino)

    def matches(self, value: os.stat_result) -> bool:
        return (self.device, self.inode) == (value.st_dev, value.st_ino)

    @property
    def meaningful(self) -> bool:
        return self.inode != 0


@dataclass(frozen=True)
class ExactPayload:
    data: bytes
    digest: str

    @classmethod
    def from_bytes(cls, data: bytes) -> "ExactPayload":
        return cls(data, f"sha256:{hashlib.sha256(data).hexdigest()}")


@dataclass(frozen=True)
class MissingLeaf:
    status: Literal["missing"] = "missing"
    digest: str = "MISSING"
    data: None = None
    identity: None = None
    mode: None = None


@dataclass(frozen=True)
class PresentLeaf:
    payload: ExactPayload
    identity: FileIdentity
    mode: int
    status: Literal["present"] = "present"

    @property
    def digest(self) -> str:
        return self.payload.digest

    @property
    def data(self) -> bytes:
        return self.payload.data


LeafState = MissingLeaf | PresentLeaf


@dataclass(frozen=True)
class PublishReceipt:
    previous: LeafState
    candidate: ExactPayload
    committed: PresentLeaf | None
    status: Literal["validated-dry-run", "committed"]


@dataclass(frozen=True)
class _OwnedLeaf:
    name: str
    identity: FileIdentity


def _same_leaf(left: LeafState, right: LeafState) -> bool:
    if isinstance(left, MissingLeaf) or isinstance(right, MissingLeaf):
        return isinstance(left, MissingLeaf) and isinstance(right, MissingLeaf)
    return left.identity == right.identity and left.payload == right.payload


def _validate_leaf_name(name: str) -> str:
    if not name or name in {".", ".."} or os.path.basename(name) != name:
        raise UnsafePathError(f"unsafe leaf name: {name!r}")
    if os.altsep and os.altsep in name:
        raise UnsafePathError(f"unsafe leaf name: {name!r}")
    return name


_DESCRIPTOR_OPERATIONS_AVAILABLE = all(
    operation in os.supports_dir_fd
    for operation in (os.open, os.stat, os.unlink, os.link)
)

_PRIVATE_DIRECTORY_OPERATIONS_AVAILABLE = all(
    operation in os.supports_dir_fd for operation in (os.mkdir, os.rmdir)
)

# Linux RENAME_EXCHANGE and Darwin RENAME_SWAP coincide at 2 by accident.
# Never pass flags=0: both platforms then perform a plain replacing rename.
_RENAME_EXCHANGE = 2
_RENAME_SWAP = 0x00000002


def _rename_exchange(
    source_fd: int,
    source: str,
    destination_fd: int,
    destination: str,
) -> None:
    """Atomically exchange two descriptor-relative names or fail closed."""
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        try:
            exchange, flags = libc.renameat2, _RENAME_EXCHANGE
        except AttributeError:
            exchange, flags = libc.renameatx_np, _RENAME_SWAP
    except (AttributeError, OSError) as exc:
        raise SafePublicationUnavailable(
            "atomic existing-target exchange is unavailable on this platform"
        ) from exc
    exchange.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    exchange.restype = ctypes.c_int
    result = exchange(
        source_fd,
        os.fsencode(_validate_leaf_name(source)),
        destination_fd,
        os.fsencode(_validate_leaf_name(destination)),
        flags,
    )
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number in {
        errno.ENOSYS,
        errno.EINVAL,
        errno.EXDEV,
        getattr(errno, "ENOTSUP", errno.EINVAL),
        getattr(errno, "EOPNOTSUPP", errno.EINVAL),
    }:
        raise SafePublicationUnavailable(
            "atomic existing-target exchange is unavailable on this filesystem"
        )
    raise OSError(error_number, os.strerror(error_number))


class PinnedDirectory:
    """A directory and its namespace binding captured by file descriptor."""

    def __init__(
        self,
        *,
        path: Path,
        label: str,
        identity: FileIdentity,
        directory_fd: int | None,
        parent_path: Path,
        parent_identity: FileIdentity,
        parent_fd: int | None,
    ) -> None:
        self.path = path
        self.label = label
        self.identity = identity
        self._directory_fd = directory_fd
        self._parent_path = parent_path
        self._parent_identity = parent_identity
        self._parent_fd = parent_fd

    @classmethod
    def open(
        cls, path: Path, *, label: str, mutation: bool = False
    ) -> "PinnedDirectory":
        try:
            requested = path.expanduser()
            if not requested.is_absolute():
                requested = Path.cwd() / requested
            canonical = requested.resolve(strict=True)
            before = os.lstat(canonical)
            parent_path = canonical.parent
            parent_before = os.lstat(parent_path)
        except (OSError, RuntimeError, ValueError) as exc:
            raise UnsafePathError(f"cannot resolve {label} {path}: {exc}") from exc
        if not stat.S_ISDIR(before.st_mode):
            raise UnsafePathError(f"{label} is not a directory: {canonical}")
        if not stat.S_ISDIR(parent_before.st_mode):
            raise UnsafePathError(
                f"parent of {label} is not a directory: {parent_path}"
            )

        identity = FileIdentity.from_stat(before)
        parent_identity = FileIdentity.from_stat(parent_before)
        directory_fd: int | None = None
        parent_fd: int | None = None
        descriptor_bound = (
            canonical != canonical.parent
            and identity.meaningful
            and parent_identity.meaningful
            and _DESCRIPTOR_OPERATIONS_AVAILABLE
        )
        if descriptor_bound:
            flags = (
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0)
            )
            try:
                parent_fd = os.open(parent_path, flags)
                opened_parent = os.fstat(parent_fd)
                if not stat.S_ISDIR(
                    opened_parent.st_mode
                ) or not parent_identity.matches(opened_parent):
                    raise StoreConflictError(
                        f"parent of {label} changed while being opened: {parent_path}"
                    )
                from_parent = os.stat(
                    canonical.name, dir_fd=parent_fd, follow_symlinks=False
                )
                if not stat.S_ISDIR(from_parent.st_mode) or not identity.matches(
                    from_parent
                ):
                    raise StoreConflictError(
                        f"{label} changed while being opened: {canonical}"
                    )
                directory_fd = os.open(canonical.name, flags, dir_fd=parent_fd)
                opened = os.fstat(directory_fd)
                if not stat.S_ISDIR(opened.st_mode) or not identity.matches(opened):
                    raise StoreConflictError(
                        f"{label} changed while being opened: {canonical}"
                    )
            except BaseException:
                if directory_fd is not None:
                    os.close(directory_fd)
                if parent_fd is not None:
                    os.close(parent_fd)
                raise

        instance = cls(
            path=canonical,
            label=label,
            identity=identity,
            directory_fd=directory_fd,
            parent_path=parent_path,
            parent_identity=parent_identity,
            parent_fd=parent_fd,
        )
        try:
            instance.assert_path_binding()
            if mutation:
                instance.require_mutation_support()
        except BaseException:
            instance.close()
            raise
        return instance

    @property
    def descriptor_bound(self) -> bool:
        return self._directory_fd is not None and self._parent_fd is not None

    @property
    def directory_fd(self) -> int:
        if self._directory_fd is None:
            raise SafePublicationUnavailable(
                f"safe descriptor-relative access is unavailable for {self.label}"
            )
        return self._directory_fd

    def require_mutation_support(self) -> None:
        if not self.descriptor_bound:
            raise SafePublicationUnavailable(
                f"safe descriptor-relative publication is unavailable for {self.label}"
            )
        try:
            os.fsync(self.directory_fd)
        except OSError as exc:
            raise SafePublicationUnavailable(
                f"directory sync is unavailable for {self.label}: {exc}"
            ) from exc

    def assert_path_binding(self) -> None:
        try:
            parent_now = os.lstat(self._parent_path)
            if not stat.S_ISDIR(
                parent_now.st_mode
            ) or not self._parent_identity.matches(parent_now):
                raise StoreConflictError(
                    f"parent of {self.label} changed during the operation: {self._parent_path}"
                )
            if self._parent_fd is not None:
                parent_opened = os.fstat(self._parent_fd)
                if not self._parent_identity.matches(parent_opened):
                    raise StoreConflictError(
                        f"opened parent of {self.label} changed during the operation"
                    )
                current = os.stat(
                    self.path.name,
                    dir_fd=self._parent_fd,
                    follow_symlinks=False,
                )
            else:
                current = os.lstat(self.path)
        except StoreConflictError:
            raise
        except OSError as exc:
            raise StoreConflictError(
                f"{self.label} changed during the operation: {exc}"
            ) from exc
        if not stat.S_ISDIR(current.st_mode) or not self.identity.matches(current):
            raise StoreConflictError(
                f"{self.label} changed during the operation: {self.path}"
            )
        if self._directory_fd is not None:
            opened = os.fstat(self._directory_fd)
            if not self.identity.matches(opened):
                raise StoreConflictError(
                    f"opened {self.label} changed during the operation"
                )

    def stat_leaf(self, name: str) -> os.stat_result:
        leaf = _validate_leaf_name(name)
        if self._directory_fd is not None:
            return os.stat(leaf, dir_fd=self._directory_fd, follow_symlinks=False)
        return os.lstat(self.path / leaf)

    def open_leaf(self, name: str, flags: int, mode: int = 0o644) -> int:
        leaf = _validate_leaf_name(name)
        if self._directory_fd is not None:
            return os.open(leaf, flags, mode, dir_fd=self._directory_fd)
        return os.open(self.path / leaf, flags, mode)

    def unlink_leaf(self, name: str) -> None:
        leaf = _validate_leaf_name(name)
        if self._directory_fd is not None:
            os.unlink(leaf, dir_fd=self._directory_fd)
        else:
            os.unlink(self.path / leaf)

    def link_from(
        self,
        source_directory: "PinnedDirectory",
        source: str,
        destination: str,
    ) -> None:
        self.require_mutation_support()
        source_directory.require_mutation_support()
        source_leaf = _validate_leaf_name(source)
        destination_leaf = _validate_leaf_name(destination)
        try:
            os.link(
                source_leaf,
                destination_leaf,
                src_dir_fd=source_directory.directory_fd,
                dst_dir_fd=self.directory_fd,
                follow_symlinks=False,
            )
        except (NotImplementedError, TypeError) as exc:
            raise SafePublicationUnavailable(
                f"atomic no-replace creation is unavailable for {self.label}: {exc}"
            ) from exc

    def exchange_with(
        self,
        source_directory: "PinnedDirectory",
        source: str,
        destination: str,
    ) -> None:
        self.require_mutation_support()
        source_directory.require_mutation_support()
        _rename_exchange(
            source_directory.directory_fd,
            source,
            self.directory_fd,
            destination,
        )

    def create_private_child(
        self, *, prefix: str
    ) -> tuple["PinnedDirectory", _OwnedLeaf]:
        self.require_mutation_support()
        if not _PRIVATE_DIRECTORY_OPERATIONS_AVAILABLE:
            raise SafePublicationUnavailable(
                "descriptor-relative private staging directories are unavailable"
            )
        self.assert_path_binding()
        name: str | None = None
        owned: _OwnedLeaf | None = None
        directory_fd: int | None = None
        parent_fd: int | None = None
        for _ in range(128):
            candidate = f"{prefix}{secrets.token_hex(12)}.stage"
            try:
                os.mkdir(candidate, 0o700, dir_fd=self.directory_fd)
                name = candidate
                break
            except FileExistsError:
                continue
        if name is None:
            raise OSError(
                errno.EEXIST, "could not allocate a private staging directory"
            )
        try:
            created = self.stat_leaf(name)
            if not stat.S_ISDIR(created.st_mode):
                raise UnsafePathError(
                    f"private staging path is not a directory: {self.path / name}"
                )
            if stat.S_IMODE(created.st_mode) & 0o077:
                raise UnsafePathError(
                    f"private staging directory is not private: {self.path / name}"
                )
            owned = _OwnedLeaf(name, FileIdentity.from_stat(created))
            if not owned.identity.meaningful:
                raise SafePublicationUnavailable(
                    "private staging directory has no stable filesystem identity"
                )
            flags = (
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0)
            )
            directory_fd = os.open(name, flags, dir_fd=self.directory_fd)
            opened = os.fstat(directory_fd)
            if not stat.S_ISDIR(opened.st_mode) or not owned.identity.matches(opened):
                raise StoreConflictError(
                    f"private staging directory changed while opening: {self.path / name}"
                )
            parent_fd = os.dup(self.directory_fd)
            child = PinnedDirectory(
                path=self.path / name,
                label="private staging directory",
                identity=owned.identity,
                directory_fd=directory_fd,
                parent_path=self.path,
                parent_identity=self.identity,
                parent_fd=parent_fd,
            )
            directory_fd = None
            parent_fd = None
            child.assert_path_binding()
            return child, owned
        except BaseException:
            if directory_fd is not None:
                os.close(directory_fd)
            if parent_fd is not None:
                os.close(parent_fd)
            if owned is not None:
                _rmdir_if_owned(self, owned)
            raise

    def rmdir_leaf(self, name: str) -> None:
        leaf = _validate_leaf_name(name)
        if self._directory_fd is None:
            raise SafePublicationUnavailable(
                f"safe descriptor-relative cleanup is unavailable for {self.label}"
            )
        os.rmdir(leaf, dir_fd=self._directory_fd)

    def sync(self) -> None:
        self.require_mutation_support()
        os.fsync(self.directory_fd)

    def close(self) -> None:
        directory_fd, self._directory_fd = self._directory_fd, None
        parent_fd, self._parent_fd = self._parent_fd, None
        if directory_fd is not None:
            os.close(directory_fd)
        if parent_fd is not None:
            os.close(parent_fd)

    def __enter__(self) -> "PinnedDirectory":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()


def read_optional_exact(
    directory: PinnedDirectory, name: str, *, max_bytes: int, label: str
) -> LeafState:
    leaf = _validate_leaf_name(name)
    directory.assert_path_binding()
    try:
        before = directory.stat_leaf(leaf)
    except FileNotFoundError:
        directory.assert_path_binding()
        return MissingLeaf()
    except OSError as exc:
        raise UnsafePathError(
            f"cannot inspect {label} {directory.path / leaf}: {exc}"
        ) from exc
    if stat.S_ISLNK(before.st_mode):
        raise UnsafePathError(
            f"refusing symbolic-link {label}: {directory.path / leaf}"
        )
    if not stat.S_ISREG(before.st_mode):
        raise UnsafePathError(
            f"{label} must be a regular file: {directory.path / leaf}"
        )
    if before.st_size > max_bytes:
        raise UnsafePathError(
            f"{label} exceeds {max_bytes} byte safety limit: {directory.path / leaf}"
        )

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = directory.open_leaf(leaf, flags)
    except OSError as exc:
        raise StoreConflictError(
            f"{label} changed before it could be opened: {directory.path / leaf}: {exc}"
        ) from exc
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            raise UnsafePathError(
                f"opened {label} is not a regular file: {directory.path / leaf}"
            )
        identity = FileIdentity.from_stat(opened)
        if not identity.matches(before):
            raise StoreConflictError(
                f"{label} changed between inspection and open: {directory.path / leaf}"
            )
        if opened.st_size > max_bytes:
            raise UnsafePathError(
                f"{label} exceeds {max_bytes} byte safety limit: {directory.path / leaf}"
            )

        chunks: list[bytes] = []
        total = 0
        while True:
            read_size = min(1024 * 1024, max_bytes + 1 - total)
            chunk = os.read(fd, read_size)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > max_bytes:
                raise UnsafePathError(
                    f"{label} exceeds {max_bytes} byte safety limit: {directory.path / leaf}"
                )
        after_fd = os.fstat(fd)
    finally:
        os.close(fd)

    try:
        after_path = directory.stat_leaf(leaf)
    except OSError as exc:
        raise StoreConflictError(
            f"{label} changed while being read: {directory.path / leaf}: {exc}"
        ) from exc
    if not identity.matches(after_fd) or not identity.matches(after_path):
        raise StoreConflictError(
            f"{label} path changed while being read: {directory.path / leaf}"
        )
    if any(
        getattr(opened, field, None) != getattr(after_fd, field, None)
        for field in ("st_size", "st_mtime_ns", "st_ctime_ns")
    ):
        raise StoreConflictError(
            f"{label} contents changed while being read: {directory.path / leaf}"
        )
    directory.assert_path_binding()
    return PresentLeaf(
        payload=ExactPayload.from_bytes(b"".join(chunks)),
        identity=identity,
        mode=stat.S_IMODE(opened.st_mode),
    )


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    offset = 0
    while offset < len(view):
        written = os.write(fd, view[offset:])
        if written <= 0:
            raise OSError(errno.EIO, "write returned no progress")
        offset += written


def _unlink_if_owned(directory: PinnedDirectory, owned: _OwnedLeaf) -> None:
    with contextlib.suppress(OSError, StoreError):
        current = directory.stat_leaf(owned.name)
        if owned.identity.matches(current):
            directory.unlink_leaf(owned.name)


def _rmdir_if_owned(directory: PinnedDirectory, owned: _OwnedLeaf) -> None:
    with contextlib.suppress(OSError, StoreError):
        current = directory.stat_leaf(owned.name)
        if owned.identity.matches(current) and stat.S_ISDIR(current.st_mode):
            directory.rmdir_leaf(owned.name)


def _read_fd_exact(fd: int, *, max_bytes: int) -> bytes:
    os.lseek(fd, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    total = 0
    while True:
        read_size = min(1024 * 1024, max_bytes + 1 - total)
        chunk = os.read(fd, read_size)
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > max_bytes:
            raise StoreConflictError("staging file grew beyond the payload limit")
    return b"".join(chunks)


@dataclass
class _StagedLeaf:
    parent: PinnedDirectory
    directory: PinnedDirectory
    directory_owner: _OwnedLeaf
    leaf: _OwnedLeaf
    fd: int
    cleanup_identities: set[FileIdentity] = field(default_factory=set)
    preserve: bool = False

    def __post_init__(self) -> None:
        self.cleanup_identities.add(self.leaf.identity)

    @property
    def name(self) -> str:
        return self.leaf.name

    @property
    def identity(self) -> FileIdentity:
        return self.leaf.identity

    def verify_candidate(self, payload: ExactPayload, *, max_bytes: int) -> None:
        self.directory.assert_path_binding()
        opened_before = os.fstat(self.fd)
        current = self.directory.stat_leaf(self.name)
        if (
            not stat.S_ISREG(opened_before.st_mode)
            or not self.identity.matches(opened_before)
            or not self.identity.matches(current)
        ):
            raise StoreConflictError("staging path no longer names the prepared inode")
        data = _read_fd_exact(self.fd, max_bytes=max_bytes)
        opened_after = os.fstat(self.fd)
        if (
            not self.identity.matches(opened_after)
            or ExactPayload.from_bytes(data) != payload
            or any(
                getattr(opened_before, field_name, None)
                != getattr(opened_after, field_name, None)
                for field_name in ("st_size", "st_mtime_ns", "st_ctime_ns")
            )
        ):
            raise StoreConflictError("staging bytes changed before publication")
        self.directory.assert_path_binding()

    def allow_cleanup(self, identity: FileIdentity) -> None:
        self.cleanup_identities.add(identity)

    def preserve_recovery_leaf(self) -> None:
        self.preserve = True

    @property
    def recovery_path(self) -> Path:
        return self.directory.path / self.name

    def close(self) -> None:
        with contextlib.suppress(OSError):
            os.close(self.fd)
        if not self.preserve:
            with contextlib.suppress(OSError, StoreError):
                current = self.directory.stat_leaf(self.name)
                identity = FileIdentity.from_stat(current)
                if identity in self.cleanup_identities:
                    self.directory.unlink_leaf(self.name)
        self.directory.close()
        _rmdir_if_owned(self.parent, self.directory_owner)


def _stage_exact(
    directory: PinnedDirectory, payload: ExactPayload, *, mode: int, prefix: str
) -> _StagedLeaf:
    directory.require_mutation_support()
    directory.assert_path_binding()
    private_directory, directory_owner = directory.create_private_child(prefix=prefix)
    flags = (
        os.O_RDWR
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_BINARY", 0)
    )
    fd: int | None = None
    owned: _OwnedLeaf | None = None
    name = "payload"
    try:
        fd = private_directory.open_leaf(name, flags, 0o600)
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            raise UnsafePathError(f"staging leaf is not a regular file: {name}")
        owned = _OwnedLeaf(name, FileIdentity.from_stat(opened))
        fchmod = getattr(os, "fchmod", None)
        if fchmod is None:
            raise SafePublicationUnavailable(
                "descriptor-based mode setting is unavailable for staged publication"
            )
        fchmod(fd, stat.S_IMODE(mode))
        _write_all(fd, payload.data)
        os.fsync(fd)
        after_write = os.fstat(fd)
        if after_write.st_size != len(payload.data) or not owned.identity.matches(
            after_write
        ):
            raise StoreConflictError("staging file changed while being written")
    except BaseException:
        if fd is not None:
            os.close(fd)
        if owned is not None:
            _unlink_if_owned(private_directory, owned)
        private_directory.close()
        _rmdir_if_owned(directory, directory_owner)
        raise
    assert fd is not None
    current = private_directory.stat_leaf(name)
    if owned is None or not owned.identity.matches(current):
        if owned is not None:
            _unlink_if_owned(private_directory, owned)
        os.close(fd)
        private_directory.close()
        _rmdir_if_owned(directory, directory_owner)
        raise StoreConflictError("staging path changed after it was written")
    private_directory.assert_path_binding()
    return _StagedLeaf(
        parent=directory,
        directory=private_directory,
        directory_owner=directory_owner,
        leaf=owned,
        fd=fd,
    )


class AdvisoryLock:
    """Persistent out-of-repository lock keyed by repository identity."""

    def __init__(
        self, identity: FileIdentity, canonical_path: Path, timeout_seconds: float
    ) -> None:
        key_source = (
            f"{identity.device}:{identity.inode}"
            if identity.meaningful
            else str(canonical_path)
        )
        key = hashlib.sha256(os.fsencode(key_source)).hexdigest()
        uid = getattr(os, "getuid", lambda: "user")()
        lock_dir = Path(tempfile.gettempdir()) / f"super-review-locks-{uid}"
        lock_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = os.lstat(lock_dir)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise UnsafePathError(f"unsafe advisory-lock directory: {lock_dir}")
        with contextlib.suppress(OSError):
            os.chmod(lock_dir, 0o700)
        self.path = lock_dir / f"{key}.lock"
        self.timeout_seconds = timeout_seconds
        self.handle: BinaryIO | None = None

    def __enter__(self) -> "AdvisoryLock":
        flags = (
            os.O_RDWR
            | os.O_CREAT
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_BINARY", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        fd: int | None = None
        try:
            fd = os.open(self.path, flags, 0o600)
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise UnsafePathError(
                    f"advisory lock is not a regular file: {self.path}"
                )
            handle = os.fdopen(fd, "r+b", closefd=True)
            fd = None
            if handle.seek(0, os.SEEK_END) == 0:
                handle.write(b"\0")
                handle.flush()
            deadline = time.monotonic() + self.timeout_seconds
            if os.name == "nt":
                import msvcrt

                while True:
                    try:
                        handle.seek(0)
                        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                        break
                    except OSError:
                        if time.monotonic() >= deadline:
                            raise StoreConflictError(
                                f"timed out acquiring advisory lock {self.path}"
                            )
                        time.sleep(0.05)
            else:
                import fcntl

                while True:
                    try:
                        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except BlockingIOError:
                        if time.monotonic() >= deadline:
                            raise StoreConflictError(
                                f"timed out acquiring advisory lock {self.path}"
                            )
                        time.sleep(0.05)
            self.handle = handle
            return self
        except BaseException:
            if fd is not None:
                os.close(fd)
            handle = locals().get("handle")
            if handle is not None:
                handle.close()
            self.handle = None
            raise

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        handle, self.handle = self.handle, None
        if handle is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                with contextlib.suppress(OSError):
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                with contextlib.suppress(OSError):
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


def _publish_exact(
    directory: PinnedDirectory,
    *,
    name: str,
    payload: ExactPayload,
    expected: LeafState,
    max_bytes: int,
) -> PresentLeaf:
    directory.require_mutation_support()
    current = read_optional_exact(directory, name, max_bytes=max_bytes, label="target")
    if not _same_leaf(current, expected):
        raise StoreConflictError("target changed before candidate staging")
    del current
    mode = expected.mode if isinstance(expected, PresentLeaf) else 0o644
    staged = _stage_exact(
        directory,
        payload,
        mode=mode,
        prefix=f".{name}.super-review.",
    )
    published_new = False
    exchanged = False
    try:
        staged.verify_candidate(payload, max_bytes=max_bytes)
        current = read_optional_exact(
            directory, name, max_bytes=max_bytes, label="target"
        )
        if not _same_leaf(current, expected):
            raise StoreConflictError(
                "target changed after candidate staging; refusing to overwrite it"
            )
        del current
        directory.assert_path_binding()
        if isinstance(expected, MissingLeaf):
            try:
                directory.link_from(staged.directory, staged.name, name)
            except FileExistsError as exc:
                raise StoreConflictError(
                    f"{name} appeared before creation; refusing to overwrite it"
                ) from exc
            except OSError as exc:
                appeared = read_optional_exact(
                    directory, name, max_bytes=max_bytes, label="target"
                )
                if isinstance(appeared, PresentLeaf):
                    raise StoreConflictError(
                        f"{name} appeared before creation; refusing to overwrite it"
                    ) from exc
                raise SafePublicationUnavailable(
                    f"cannot atomically create {name} without hard-link support: {exc}"
                ) from exc
            published_new = True
        else:
            try:
                directory.exchange_with(staged.directory, staged.name, name)
            except FileNotFoundError as exc:
                raise StoreConflictError(
                    "target or staging leaf disappeared before atomic exchange"
                ) from exc
            exchanged = True
            committed_now = read_optional_exact(
                directory, name, max_bytes=max_bytes, label="committed target"
            )
            displaced = read_optional_exact(
                staged.directory,
                staged.name,
                max_bytes=max_bytes,
                label="displaced target",
            )
            if (
                not isinstance(committed_now, PresentLeaf)
                or committed_now.identity != staged.identity
                or committed_now.payload != payload
                or not _same_leaf(displaced, expected)
            ):
                raise StoreConflictError(
                    "atomic exchange observed a concurrent target or staging change"
                )
            del committed_now, displaced
        directory.sync()
        if exchanged:
            staged.directory.sync()
        committed = read_optional_exact(
            directory, name, max_bytes=max_bytes, label="committed target"
        )
        if (
            not isinstance(committed, PresentLeaf)
            or committed.identity != staged.identity
            or committed.payload != payload
        ):
            raise StoreConflictError(
                "post-write verification found different target bytes or identity"
            )
        try:
            directory.assert_path_binding()
        except StoreConflictError as exc:
            raise StoreConflictError(
                f"{exc}; exact publication may have occurred in the originally pinned directory"
            ) from exc
        if isinstance(expected, PresentLeaf):
            staged.allow_cleanup(expected.identity)
        return committed
    except BaseException as exc:
        if exchanged:
            staged.preserve_recovery_leaf()
            raise StoreConflictError(
                f"{exc}; the exchange was not reversed because a second pathname "
                "exchange cannot be authorized safely; inspect the canonical target "
                f"and recovery data at {staged.recovery_path}"
            ) from exc
        if published_new:
            _unlink_if_owned(directory, _OwnedLeaf(name, staged.identity))
        raise
    finally:
        staged.close()


CurrentGuard = Callable[[bytes], None]


class ReportStore:
    """One pinned repository and its complete guarded publication operation."""

    TARGET = "FINDINGS.md"

    def __init__(self, directory: PinnedDirectory, *, max_bytes: int) -> None:
        self.directory = directory
        self.max_bytes = max_bytes

    @classmethod
    def open(cls, repo_root: Path, *, max_bytes: int, mutation: bool) -> "ReportStore":
        return cls(
            PinnedDirectory.open(repo_root, label="repository root", mutation=mutation),
            max_bytes=max_bytes,
        )

    @property
    def root(self) -> Path:
        return self.directory.path

    @property
    def identity(self) -> FileIdentity:
        return self.directory.identity

    def snapshot(self) -> LeafState:
        return read_optional_exact(
            self.directory,
            self.TARGET,
            max_bytes=self.max_bytes,
            label="target",
        )

    def compare_and_publish(
        self,
        *,
        candidate: ExactPayload,
        expected_digest: str,
        candidate_identity: FileIdentity | None,
        lock_timeout: float,
        dry_run: bool,
        guard_current: CurrentGuard,
    ) -> PublishReceipt:
        with AdvisoryLock(self.identity, self.root, lock_timeout):
            current = self.snapshot()
            if (
                candidate_identity is not None
                and isinstance(current, PresentLeaf)
                and candidate_identity == current.identity
            ):
                raise UnsafePathError(
                    "candidate must not be the target through a hard link"
                )
            if current.digest != expected_digest:
                raise StoreConflictError(
                    f"FINDINGS.md changed: expected {expected_digest}, found {current.digest}; reread, revalidate, and regenerate"
                )
            guard_current(b"" if isinstance(current, MissingLeaf) else current.data)

            repeated = self.snapshot()
            if not _same_leaf(repeated, current):
                raise StoreConflictError(
                    "FINDINGS.md changed before publication; reread and regenerate"
                )
            guard_current(b"" if isinstance(repeated, MissingLeaf) else repeated.data)
            if dry_run:
                return PublishReceipt(current, candidate, None, "validated-dry-run")
            current = repeated
            del repeated

            committed = _publish_exact(
                self.directory,
                name=self.TARGET,
                payload=candidate,
                expected=current,
                max_bytes=self.max_bytes,
            )
            return PublishReceipt(current, candidate, committed, "committed")

    def close(self) -> None:
        self.directory.close()

    def __enter__(self) -> "ReportStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()


def _identity_in_ancestry(path: Path, identity: FileIdentity) -> bool:
    current = path
    while True:
        try:
            info = os.lstat(current)
        except OSError:
            return True
        if identity.matches(info):
            return True
        if current == current.parent:
            return False
        current = current.parent


def publish_new_exact(
    output_path: Path,
    data: bytes,
    *,
    forbidden_directory: PinnedDirectory,
    max_bytes: int,
) -> Path:
    """Publish complete bytes outside one already pinned directory."""
    try:
        requested = output_path.expanduser()
        if not requested.is_absolute():
            requested = Path.cwd() / requested
    except (OSError, RuntimeError, ValueError) as exc:
        raise UnsafePathError(
            f"cannot resolve snapshot output {output_path}: {exc}"
        ) from exc
    leaf = _validate_leaf_name(requested.name)
    repository = forbidden_directory
    repository.assert_path_binding()
    with PinnedDirectory.open(
        requested.parent, label="snapshot output directory", mutation=True
    ) as output:
        repository.assert_path_binding()
        output_candidate = output.path / leaf
        if output_candidate.is_relative_to(repository.path) or _identity_in_ancestry(
            output.path, repository.identity
        ):
            raise UnsafePathError(
                f"--out must be outside the reviewed repository ({repository.path})"
            )
        expected = read_optional_exact(
            output, leaf, max_bytes=max_bytes, label="snapshot output"
        )
        if isinstance(expected, PresentLeaf):
            raise StoreConflictError(
                f"snapshot output already exists: {output_candidate}"
            )
        _publish_exact(
            output,
            name=leaf,
            payload=ExactPayload.from_bytes(data),
            expected=expected,
            max_bytes=max_bytes,
        )
        repository.assert_path_binding()
        return output_candidate
