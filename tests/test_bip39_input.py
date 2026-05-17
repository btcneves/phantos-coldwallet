"""Tests for app.ui.bip39_input — BIP39 seed word autocomplete widget.

Runs offscreen (no display required) via QT_QPA_PLATFORM=offscreen.
"""

from __future__ import annotations

import os
import sys

import pytest

# Force offscreen Qt platform before any PySide6 import.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Known-valid BIP39 test mnemonic (all-abandon + about — standard test vector).
MNEMONIC_12 = (
    "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
)
MNEMONIC_24 = (
    "abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon art"
)

try:
    from PySide6.QtWidgets import QApplication

    _app = QApplication.instance() or QApplication(sys.argv)
    _QT_AVAILABLE = True
except Exception:
    _QT_AVAILABLE = False

pytestmark = pytest.mark.skipif(not _QT_AVAILABLE, reason="PySide6 not available")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def seed_widget_24():
    from app.ui.bip39_input import Bip39SeedWidget

    w = Bip39SeedWidget(word_count=24)
    return w


@pytest.fixture()
def seed_widget_12():
    from app.ui.bip39_input import Bip39SeedWidget

    w = Bip39SeedWidget(word_count=12)
    return w


# ---------------------------------------------------------------------------
# BIP39_WORDS sanity checks (no Qt needed, runs always)
# ---------------------------------------------------------------------------


def test_wordlist_has_2048_entries() -> None:
    from app.ui.bip39_input import BIP39_WORDS

    assert len(BIP39_WORDS) == 2048


def test_wordlist_starts_with_abandon() -> None:
    from app.ui.bip39_input import BIP39_WORDS

    assert BIP39_WORDS[0] == "abandon"


def test_wordlist_ends_with_zoo() -> None:
    from app.ui.bip39_input import BIP39_WORDS

    assert BIP39_WORDS[-1] == "zoo"


def test_wordlist_contains_satoshi() -> None:
    from app.ui.bip39_input import BIP39_WORDS

    assert "satoshi" in BIP39_WORDS


def test_wordlist_no_duplicates() -> None:
    from app.ui.bip39_input import BIP39_WORDS

    assert len(BIP39_WORDS) == len(set(BIP39_WORDS))


def test_wordlist_all_lowercase() -> None:
    from app.ui.bip39_input import BIP39_WORDS

    assert all(w == w.lower() for w in BIP39_WORDS)


def test_word_set_matches_list() -> None:
    from app.ui.bip39_input import BIP39_WORDS, _WORD_SET

    assert _WORD_SET == set(BIP39_WORDS)


# ---------------------------------------------------------------------------
# Bip39SeedWidget — structural / API tests
# ---------------------------------------------------------------------------


def test_default_word_count_is_24(seed_widget_24) -> None:
    assert len(seed_widget_24._fields) == 24


def test_12_word_mode_has_12_fields(seed_widget_12) -> None:
    assert len(seed_widget_12._fields) == 12


def test_set_mnemonic_12_populates_fields(seed_widget_12) -> None:
    seed_widget_12.set_mnemonic(MNEMONIC_12)
    words = MNEMONIC_12.split()
    for i, field in enumerate(seed_widget_12._fields):
        assert field.get_word() == words[i]


def test_get_mnemonic_returns_space_joined(seed_widget_12) -> None:
    seed_widget_12.set_mnemonic(MNEMONIC_12)
    assert seed_widget_12.get_mnemonic() == MNEMONIC_12


def test_to_plain_text_compat(seed_widget_12) -> None:
    """toPlainText() must be a QTextEdit-compatible alias for get_mnemonic()."""
    seed_widget_12.set_mnemonic(MNEMONIC_12)
    assert seed_widget_12.toPlainText() == MNEMONIC_12


def test_set_plain_text_compat(seed_widget_12) -> None:
    seed_widget_12.setPlainText(MNEMONIC_12)
    assert seed_widget_12.get_mnemonic() == MNEMONIC_12


def test_clear_empties_all_fields(seed_widget_12) -> None:
    seed_widget_12.set_mnemonic(MNEMONIC_12)
    seed_widget_12.clear()
    assert seed_widget_12.get_mnemonic() == ""
    for field in seed_widget_12._fields:
        assert field.get_word() == ""


def test_checksum_valid_after_correct_12_mnemonic(seed_widget_12) -> None:
    seed_widget_12.set_mnemonic(MNEMONIC_12)
    assert seed_widget_12.checksum_valid is True


def test_checksum_invalid_for_wrong_last_word(seed_widget_12) -> None:
    # Replace "about" with "abandon" — fails BIP39 checksum.
    bad = " ".join(["abandon"] * 12)
    seed_widget_12.set_mnemonic(bad)
    assert seed_widget_12.checksum_valid is False


def test_checksum_invalid_when_incomplete(seed_widget_12) -> None:
    seed_widget_12.set_mnemonic("abandon abandon abandon")
    assert seed_widget_12.checksum_valid is False


def test_switch_24_to_12_preserves_words(seed_widget_24) -> None:
    seed_widget_24.set_mnemonic(MNEMONIC_24)
    first_12 = MNEMONIC_24.split()[:12]
    seed_widget_24.set_word_count(12)
    assert len(seed_widget_24._fields) == 12
    for i, word in enumerate(first_12):
        assert seed_widget_24._fields[i].get_word() == word


def test_switch_12_to_24_adds_empty_fields(seed_widget_12) -> None:
    seed_widget_12.set_mnemonic(MNEMONIC_12)
    seed_widget_12.set_word_count(24)
    assert len(seed_widget_12._fields) == 24
    # First 12 preserved, rest empty.
    for i in range(12, 24):
        assert seed_widget_12._fields[i].get_word() == ""


def test_mnemonic_changed_signal_emitted(seed_widget_12) -> None:
    received: list[str] = []
    seed_widget_12.mnemonic_changed.connect(received.append)
    seed_widget_12.set_mnemonic(MNEMONIC_12)
    assert len(received) >= 1
    assert received[-1] == MNEMONIC_12


def test_normalises_uppercase_input(seed_widget_12) -> None:
    upper = MNEMONIC_12.upper()
    seed_widget_12.set_mnemonic(upper)
    assert seed_widget_12.get_mnemonic() == MNEMONIC_12


def test_set_placeholder_text_is_noop(seed_widget_12) -> None:
    """setPlaceholderText must not raise (QTextEdit compatibility)."""
    seed_widget_12.setPlaceholderText("anything")


# ---------------------------------------------------------------------------
# _WordLineEdit — unit tests
# ---------------------------------------------------------------------------


def test_word_line_edit_get_word_empty() -> None:
    from app.ui.bip39_input import _WordLineEdit

    field = _WordLineEdit(0)
    assert field.get_word() == ""


def test_word_line_edit_set_word() -> None:
    from app.ui.bip39_input import _WordLineEdit

    field = _WordLineEdit(0)
    field.set_word("abandon")
    assert field.get_word() == "abandon"


def test_word_line_edit_set_word_uppercase_normalised() -> None:
    from app.ui.bip39_input import _WordLineEdit

    field = _WordLineEdit(0)
    field.set_word("ABANDON")
    assert field.get_word() == "abandon"


def test_word_line_edit_placeholder_shows_number() -> None:
    from app.ui.bip39_input import _WordLineEdit

    field = _WordLineEdit(4)
    assert field.placeholderText() == "#5"
