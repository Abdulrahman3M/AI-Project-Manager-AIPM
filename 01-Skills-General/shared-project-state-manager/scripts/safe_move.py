"""Windows handle-bound, no-replace moves for the optional state utility."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from contextlib import contextmanager
import errno
import os
from pathlib import Path
import stat


class _FileInfo(ctypes.Structure):
    _fields_ = [
        ("attributes", wintypes.DWORD), ("created", wintypes.FILETIME),
        ("accessed", wintypes.FILETIME), ("written", wintypes.FILETIME),
        ("volume", wintypes.DWORD), ("size_high", wintypes.DWORD),
        ("size_low", wintypes.DWORD), ("links", wintypes.DWORD),
        ("index_high", wintypes.DWORD), ("index_low", wintypes.DWORD),
    ]


class _RenameInfo(ctypes.Structure):
    _fields_ = [("flags", wintypes.DWORD), ("root", wintypes.HANDLE),
                ("name_length", wintypes.DWORD), ("name", wintypes.WCHAR * 1)]


class _BasicInfo(ctypes.Structure):
    _fields_ = [("created", ctypes.c_longlong), ("accessed", ctypes.c_longlong),
                ("written", ctypes.c_longlong), ("changed", ctypes.c_longlong),
                ("attributes", wintypes.DWORD)]


def _api():
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                   wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(_FileInfo)]
    kernel.GetFileInformationByHandle.restype = wintypes.BOOL
    kernel.SetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetFileInformationByHandle.restype = wintypes.BOOL
    kernel.SetFilePointerEx.argtypes = [wintypes.HANDLE, ctypes.c_longlong, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetFilePointerEx.restype = wintypes.BOOL
    kernel.ReadFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
    kernel.ReadFile.restype = wintypes.BOOL
    kernel.WriteFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
    kernel.WriteFile.restype = wintypes.BOOL
    kernel.SetEndOfFile.argtypes = [wintypes.HANDLE]
    kernel.SetEndOfFile.restype = wintypes.BOOL
    kernel.FlushFileBuffers.argtypes = [wintypes.HANDLE]
    kernel.FlushFileBuffers.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    return kernel


def _open_checked(kernel, path: Path, access: int, sharing: int, creation: int = 3):
    handle = kernel.CreateFileW(str(path), access, sharing, None, creation, 0x02200080, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    info = _FileInfo()
    if not kernel.GetFileInformationByHandle(handle, ctypes.byref(info)):
        error = ctypes.get_last_error()
        kernel.CloseHandle(handle)
        raise ctypes.WinError(error)
    if info.attributes & 0x400:
        kernel.CloseHandle(handle)
        raise OSError(errno.ELOOP, f"Reparse point is not allowed: {path}")
    return handle, info


def _rename_windows_handle(kernel, handle, destination: Path) -> None:
    encoded = str(destination).encode("utf-16-le")
    size = max(ctypes.sizeof(_RenameInfo), _RenameInfo.name.offset + len(encoded) + 2)
    buffer = ctypes.create_string_buffer(size)
    info = _RenameInfo.from_buffer(buffer)
    info.flags = 0
    info.root = None
    info.name_length = len(encoded)
    ctypes.memmove(ctypes.addressof(buffer) + _RenameInfo.name.offset, encoded, len(encoded))
    if not kernel.SetFileInformationByHandle(handle, 3, buffer, size):
        raise ctypes.WinError(ctypes.get_last_error())


@contextmanager
def locked_directories(*directories: Path):
    """Hold every existing ancestor against rename or replacement on Windows."""
    if os.name != "nt":
        raise OSError(errno.ENOTSUP, "Handle-bound directory protection is unavailable on this platform")
    kernel = _api()
    handles = []
    seen = set()
    try:
        for parent in directories:
            parent = Path(parent).absolute()
            for directory in (*reversed(parent.parents), parent):
                key = os.path.normcase(str(directory))
                if key in seen:
                    continue
                handle, _ = _open_checked(kernel, directory, 0x80000000, 0x3)
                handles.append(handle)
                seen.add(key)
        yield kernel
    finally:
        for handle in reversed(handles):
            kernel.CloseHandle(handle)


def ensure_directory(path: Path) -> None:
    """Create directories while holding their already-open ancestry stable."""
    if os.name != "nt":
        raise OSError(errno.ENOTSUP, "Handle-bound directory creation is unavailable on this platform")
    path = Path(path).absolute()
    kernel = _api()
    handles = []
    try:
        for directory in (*reversed(path.parents), path):
            try:
                handle, _ = _open_checked(kernel, directory, 0x80000000, 0x3)
            except OSError as error:
                if getattr(error, "winerror", None) not in (2, 3):
                    raise
                try:
                    directory.mkdir()
                except FileExistsError:
                    pass
                handle, _ = _open_checked(kernel, directory, 0x80000000, 0x3)
            handles.append(handle)
    finally:
        for handle in reversed(handles):
            kernel.CloseHandle(handle)


class _LockedRecord:
    def __init__(self, kernel, handle, info, read_only=False):
        self.kernel, self.handle, self.read_only = kernel, handle, read_only
        self.identity = [str(info.volume), str((info.index_high << 32) | info.index_low)]

    def _rewind(self) -> None:
        if not self.kernel.SetFilePointerEx(self.handle, 0, None, 0):
            raise ctypes.WinError(ctypes.get_last_error())

    def read(self) -> bytes:
        info = _FileInfo()
        if not self.kernel.GetFileInformationByHandle(self.handle, ctypes.byref(info)):
            raise ctypes.WinError(ctypes.get_last_error())
        size = (info.size_high << 32) | info.size_low
        if size > 1024 * 1024:
            raise OSError(errno.EFBIG, "Quarantine record exceeds one MiB")
        self._rewind()
        if not size:
            return b""
        buffer = ctypes.create_string_buffer(size)
        read = wintypes.DWORD()
        if not self.kernel.ReadFile(self.handle, buffer, size, ctypes.byref(read), None) or read.value != size:
            raise ctypes.WinError(ctypes.get_last_error())
        return buffer.raw[:size]

    def write(self, data: bytes) -> None:
        if self.read_only:
            raise OSError(errno.EACCES, "Record was opened read-only")
        if len(data) > 1024 * 1024:
            raise OSError(errno.EFBIG, "Quarantine record exceeds one MiB")
        self._rewind()
        written = wintypes.DWORD()
        buffer = ctypes.create_string_buffer(data, max(1, len(data)))
        if not self.kernel.WriteFile(self.handle, buffer, len(data), ctypes.byref(written), None) or written.value != len(data):
            raise ctypes.WinError(ctypes.get_last_error())
        if not self.kernel.SetEndOfFile(self.handle) or not self.kernel.FlushFileBuffers(self.handle):
            raise ctypes.WinError(ctypes.get_last_error())


@contextmanager
def locked_record(path: Path, *, create: bool = False, read_only: bool = False):
    """Open one record exclusively without following links or replacing a file."""
    path = Path(path).absolute()
    with locked_directories(path.parent) as kernel:
        if create and read_only:
            raise ValueError("A new record cannot be opened read-only")
        handle, info = _open_checked(kernel, path, 0x80000000 if read_only else 0xC0000000, 0, 1 if create else 3)
        try:
            yield _LockedRecord(kernel, handle, info, read_only)
        finally:
            kernel.CloseHandle(handle)


def move_noreplace(source: Path, destination: Path, expected=None) -> None:
    """Rename the inspected object while holding its directory ancestry stable.

    Other operating systems fail closed until an equivalent handle-bound rename
    is implemented and verified. No copy-and-delete fallback is attempted.
    """
    if os.name != "nt":
        raise OSError(errno.ENOTSUP, "Handle-bound no-replace move is unavailable on this platform")
    source, destination = Path(source).absolute(), Path(destination).absolute()
    expected = expected if expected is not None else source.lstat()
    if stat.S_ISLNK(expected.st_mode) or getattr(expected, "st_file_attributes", 0) & 0x400:
        raise OSError(errno.ELOOP, "Source is a link or reparse point")
    with locked_directories(source.parent, destination.parent) as kernel:
        handle, info = _open_checked(kernel, source, 0x10080, 0x1)
        try:
            identity = (info.volume, (info.index_high << 32) | info.index_low)
            if not expected.st_ino or identity != (expected.st_dev & 0xffffffff, expected.st_ino):
                raise OSError(errno.ESTALE, "Source identity changed during preflight")
            _rename_windows_handle(kernel, handle, destination)
        finally:
            kernel.CloseHandle(handle)


def delete_nofollow(target: Path, expected=None) -> None:
    """Delete a tree by locked Windows handles, never following reparse points."""
    if os.name != "nt":
        raise OSError(errno.ENOTSUP, "Handle-bound deletion is unavailable on this platform")
    target = Path(target).absolute()
    expected = expected if expected is not None else target.lstat()
    handles = []
    with locked_directories(target.parent) as kernel:
        def collect(path: Path, before) -> None:
            if stat.S_ISLNK(before.st_mode) or getattr(before, "st_file_attributes", 0) & 0x400:
                raise OSError(errno.ELOOP, f"Linked path is not allowed: {path}")
            handle, info = _open_checked(kernel, path, 0x80010000, 0x1)
            handles.append(handle)
            identity = (info.volume, (info.index_high << 32) | info.index_low)
            if not before.st_ino or identity != (before.st_dev & 0xffffffff, before.st_ino):
                raise OSError(errno.ESTALE, f"Path identity changed during preflight: {path}")
            if info.attributes & 0x10:
                for child in path.iterdir():
                    collect(child, child.lstat())

        try:
            collect(target, expected)
            while handles:
                handle = handles[-1]
                disposition = ctypes.c_ubyte(1)
                if not kernel.SetFileInformationByHandle(handle, 4, ctypes.byref(disposition), ctypes.sizeof(disposition)):
                    raise ctypes.WinError(ctypes.get_last_error())
                kernel.CloseHandle(handle)
                handles.pop()
        finally:
            for handle in reversed(handles):
                kernel.CloseHandle(handle)


def clear_readonly_nofollow(target: Path, recursive: bool = True, protected_names=frozenset()) -> int:
    """Clear Windows readonly attributes only after locking and checking the tree."""
    if os.name != "nt":
        raise OSError(errno.ENOTSUP, "Handle-bound attribute changes are unavailable on this platform")
    target = Path(target).absolute()
    expected = target.lstat()
    handles = []
    with locked_directories(target.parent) as kernel:
        def collect(path: Path, before) -> None:
            if path.name.casefold() in protected_names:
                raise OSError(errno.EACCES, f"Protected path is not allowed: {path}")
            if stat.S_ISLNK(before.st_mode) or getattr(before, "st_file_attributes", 0) & 0x400:
                raise OSError(errno.ELOOP, f"Linked path is not allowed: {path}")
            handle, info = _open_checked(kernel, path, 0x180, 0x1)
            handles.append((handle, info.attributes))
            if not before.st_ino or (info.volume, (info.index_high << 32) | info.index_low) != (before.st_dev & 0xffffffff, before.st_ino):
                raise OSError(errno.ESTALE, f"Path identity changed during preflight: {path}")
            if recursive and info.attributes & 0x10:
                for child in path.iterdir():
                    collect(child, child.lstat())

        try:
            collect(target, expected)
            changed = 0
            for handle, attributes in handles:
                if attributes & 1:
                    basic = _BasicInfo(0, 0, 0, 0, (attributes & ~1) or 0x80)
                    if not kernel.SetFileInformationByHandle(handle, 0, ctypes.byref(basic), ctypes.sizeof(basic)):
                        raise ctypes.WinError(ctypes.get_last_error())
                    changed += 1
            return changed
        finally:
            for handle, _ in reversed(handles):
                kernel.CloseHandle(handle)
