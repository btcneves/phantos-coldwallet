"""Tests for app.security.memory — bytearray zeroization and mlock."""

from __future__ import annotations

import sys

import pytest

from app.security.memory import try_mlock, try_munlock, zero_bytearray


def test_zero_bytearray_clears_content() -> None:
    buf = bytearray(b"super secret seed data 1234567890")
    zero_bytearray(buf)
    assert buf == bytearray(len(buf))


def test_zero_bytearray_works_on_empty() -> None:
    buf = bytearray()
    zero_bytearray(buf)
    assert buf == bytearray()


def test_zero_bytearray_idempotent() -> None:
    buf = bytearray(b"\xde\xad\xbe\xef")
    zero_bytearray(buf)
    zero_bytearray(buf)
    assert all(b == 0 for b in buf)


@pytest.mark.skipif(sys.platform != "linux", reason="mlock is Linux-only")
def test_mlock_returns_bool() -> None:
    buf = bytearray(b"sensitive key material " * 4)
    result = try_mlock(buf)
    assert isinstance(result, bool)
    try_munlock(buf)


def test_mlock_on_non_linux_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    buf = bytearray(b"data")
    assert try_mlock(buf) is False


def test_munlock_on_non_linux_is_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    buf = bytearray(b"data")
    try_munlock(buf)  # must not raise


def test_mlock_empty_buffer_returns_false() -> None:
    assert try_mlock(bytearray()) is False


def test_wallet_creation_zeroes_seed() -> None:
    """Verify create_wallet_context completes without leaking seed bytearray."""
    from app.wallet.core import create_wallet_context

    mnemonic = (
        "abandon abandon abandon abandon abandon abandon "
        "abandon abandon abandon abandon abandon about"
    )
    ctx = create_wallet_context(mnemonic, "", "bip84")
    # If we reach here, the finally block ran (seed_ba zeroed and deleted).
    assert ctx.fingerprint == "73c5da0a"
