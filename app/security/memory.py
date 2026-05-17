"""Best-effort memory protection for sensitive byte arrays.

Provides two guarantees, explicitly scoped:

  1. zero_bytearray()  — overwrites the *content* of a bytearray we control.
                          Works reliably for bytearrays created in this process.

  2. try_mlock()       — asks the kernel to lock the pages in RAM (no swap).
                          Best-effort: fails silently when RLIMIT_MEMLOCK is
                          insufficient or when not on Linux.

Known limitations (intentionally documented):
  - Python str and bytes are immutable; their content cannot be zeroed
    without CPython internals hacks.  Callers must use bytearray from the
    start when zeroing matters.
  - embit creates its own copies of key material (bytes objects) that are
    outside this module's control.  mlock mitigates swap exposure for those
    copies even though we cannot zero them.
  - mlock requires sufficient locked-memory budget (RLIMIT_MEMLOCK, default
    64 KiB–8 MiB on most Linux systems).  A 64-byte seed fits comfortably.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import sys


def zero_bytearray(buf: bytearray) -> None:
    """Overwrite every byte of *buf* with 0x00 in place.

    Uses slice assignment (bytearray is mutable, no copy is made).
    Call this in a finally block to ensure execution even on exceptions.
    """
    buf[:] = b"\x00" * len(buf)


def try_mlock(buf: bytearray) -> bool:
    """Lock the pages backing *buf* in RAM on Linux (prevent swap).

    Returns True if mlock(2) succeeded, False otherwise (non-Linux,
    libc not found, permission denied, limit exceeded, etc.).
    """
    if sys.platform != "linux" or len(buf) == 0:
        return False
    try:
        c_buf = (ctypes.c_char * len(buf)).from_buffer(buf)
        libc_name = ctypes.util.find_library("c")
        if libc_name is None:
            return False
        libc = ctypes.CDLL(libc_name, use_errno=True)
        return libc.mlock(ctypes.addressof(c_buf), ctypes.c_size_t(len(buf))) == 0
    except Exception:  # pragma: no cover
        return False


def try_mlockall() -> bool:
    """Lock all current and future memory pages in RAM on Linux (prevent swap).

    More effective than try_mlock() for individual buffers since it covers all
    internal copies created by Python runtime and third-party libraries.
    Requires CAP_IPC_LOCK capability or sufficient RLIMIT_MEMLOCK.
    Returns True if mlockall succeeded, False otherwise.
    """
    if sys.platform != "linux":
        return False
    try:
        libc_name = ctypes.util.find_library("c")
        if libc_name is None:
            return False
        libc = ctypes.CDLL(libc_name, use_errno=True)
        MCL_CURRENT = 1
        MCL_FUTURE = 2
        return libc.mlockall(MCL_CURRENT | MCL_FUTURE) == 0
    except Exception:  # pragma: no cover
        return False


def try_munlock(buf: bytearray) -> None:
    """Unlock pages previously locked by try_mlock.  Best-effort, no-op on failure."""
    if sys.platform != "linux" or len(buf) == 0:
        return
    try:
        c_buf = (ctypes.c_char * len(buf)).from_buffer(buf)
        libc_name = ctypes.util.find_library("c")
        if libc_name is None:
            return
        libc = ctypes.CDLL(libc_name, use_errno=True)
        libc.munlock(ctypes.addressof(c_buf), ctypes.c_size_t(len(buf)))
    except Exception:  # pragma: no cover
        return
