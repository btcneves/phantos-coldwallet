#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.security import safe_event  # noqa: E402
from app.ur import decode_crypto_psbt_ur, encode_crypto_psbt_ur_parts  # noqa: E402
from app.wallet import (  # noqa: E402
    create_wallet_context,
    derive_address,
    generate_mnemonic,
    validate_mnemonic,
)
from app.wallet.core import watch_only_json  # noqa: E402

PUBLIC_TEST_MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
)
PUBLIC_TEST_PASSPHRASE = "TREZOR"

EXPECTED_ADDRESSES = {
    "bip44": "1LqBGSKuX5yYUonjxT5qGfpUsXKYYWeabA",
    "bip49": "37VucYSaXLCAsxYyAPfbSi9eh4iEcbShgf",
    "bip84": "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu",
    "bip86": "bc1p5cyxnuxmeuwuvkwfem96lqzszd02n6xdcjrs20cac6yqjjwudpxqkedrcr",
}


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"PASS {name}")


def assert_not_contains(label: str, text: str, forbidden: tuple[str, ...]) -> None:
    lowered = text.lower()
    for index, item in enumerate(forbidden, start=1):
        check(f"{label} omits blocked value {index}", item.lower() not in lowered)


def validate_wallet_core() -> None:
    words12 = generate_mnemonic(12).split()
    words24 = generate_mnemonic(24).split()
    check("generate 12-word BIP39 mnemonic", len(words12) == 12)
    check("generate 24-word BIP39 mnemonic", len(words24) == 24)
    check(
        "validate public BIP39 checksum vector",
        validate_mnemonic(PUBLIC_TEST_MNEMONIC) == PUBLIC_TEST_MNEMONIC,
    )

    try:
        validate_mnemonic("abandon " * 11 + "wrong")
    except ValueError:
        print("PASS reject invalid BIP39 checksum")
    else:
        raise AssertionError("reject invalid BIP39 checksum")

    for profile_id, expected in EXPECTED_ADDRESSES.items():
        ctx = create_wallet_context(PUBLIC_TEST_MNEMONIC, "", profile_id)
        first = derive_address(ctx, 0, 0)
        check(f"derive expected {profile_id} address", first.address == expected)
        if profile_id == "bip86":
            check("BIP86 profile marked experimental", ctx.profile.experimental)
        else:
            check(f"{profile_id} profile not experimental", not ctx.profile.experimental)

    protected = create_wallet_context(PUBLIC_TEST_MNEMONIC, PUBLIC_TEST_PASSPHRASE, "bip84")
    check(
        "passphrase changes wallet fingerprint",
        protected.fingerprint
        != create_wallet_context(PUBLIC_TEST_MNEMONIC, "", "bip84").fingerprint,
    )


def validate_watch_only_export() -> None:
    expected_prefixes = {"bip44": "xpub", "bip49": "ypub", "bip84": "zpub", "bip86": "xpub"}
    for profile_id, prefix in expected_prefixes.items():
        ctx = create_wallet_context(PUBLIC_TEST_MNEMONIC, "", profile_id)
        payload = watch_only_json(ctx)
        parsed = json.loads(payload)
        check(f"{profile_id} watch-only JSON parses", parsed["fingerprint"] == ctx.fingerprint)
        check(f"{profile_id} external descriptor exported", "descriptor_external" in parsed)
        check(f"{profile_id} internal descriptor exported", "descriptor_internal" in parsed)
        check(
            f"{profile_id} canonical xpub exported",
            parsed["extended_public_key"].startswith("xpub"),
        )
        check(
            f"{profile_id} compatible extended public key exported",
            parsed["compatible_extended_public_key"].startswith(prefix),
        )
        assert_not_contains(
            f"{profile_id} watch-only export",
            payload,
            ("xprv", "zprv", "yprv", "private", PUBLIC_TEST_MNEMONIC, PUBLIC_TEST_PASSPHRASE),
        )

    rendered = repr(create_wallet_context(PUBLIC_TEST_MNEMONIC, PUBLIC_TEST_PASSPHRASE, "bip84"))
    assert_not_contains(
        "WalletContext repr",
        rendered,
        (
            "root_key",
            "account_key",
            "account_public_key",
            "xprv",
            "zprv",
            PUBLIC_TEST_MNEMONIC,
            PUBLIC_TEST_PASSPHRASE,
        ),
    )


def validate_redaction_and_ur() -> None:
    for event in (
        "seed criada",
        "mnemonic generated",
        "passphrase incorreta",
        "private key",
        "frase de recuperação inválida",
    ):
        check(f"safe_event redacts {event}", safe_event(event) == "[evento sensível omitido]")

    payload = b"psbt\xff" + bytes(range(256)) * 4
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        parts = encode_crypto_psbt_ur_parts(payload, max_fragment_len=80, redundancy=2)
        decoded = decode_crypto_psbt_ur(parts)
    check("UR multipart roundtrip", decoded == payload)
    check("UR encode/decode stdout quiet", stdout.getvalue() == "")
    check("UR encode/decode stderr quiet", stderr.getvalue() == "")


def validate_ui_lock_if_available() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox

        from app.ui.main_window import MainWindow
    except Exception as exc:
        print(f"SKIPPED UI lock validation: {exc}")
        return

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.mnemonic_input.set_mnemonic(PUBLIC_TEST_MNEMONIC)
    window.passphrase_edit.setText(PUBLIC_TEST_PASSPHRASE)
    window.psbt_edit.setPlainText("cHNidP8=")
    window.output.setPlainText(PUBLIC_TEST_MNEMONIC)
    window.ctx = create_wallet_context(PUBLIC_TEST_MNEMONIC, PUBLIC_TEST_PASSPHRASE, "bip84")

    with patch.object(QMessageBox, "information", return_value=QMessageBox.StandardButton.Ok):
        window.lock_wallet()

    check("UI lock clears context", window.ctx is None)
    check("UI lock clears seed field", window.mnemonic_input.get_mnemonic() == "")
    check("UI lock clears passphrase field", window.passphrase_edit.text() == "")
    check("UI lock clears PSBT field", window.psbt_edit.toPlainText() == "")
    check("UI lock clears output field", window.output.toPlainText() == "")
    app.processEvents()


def main() -> int:
    validate_wallet_core()
    validate_watch_only_export()
    validate_redaction_and_ur()
    validate_ui_lock_if_available()
    print("Wallet flow validation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
