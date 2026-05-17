from unittest.mock import patch

import pytest
from embit.psbt import DerivationPath, PSBT, PSBTError
from embit.script import Script, p2pkh, p2sh, p2wpkh, p2tr
from embit.transaction import Transaction, TransactionInput, TransactionOutput

from app.psbt import parse_psbt, review_psbt, sign_psbt
from app.psbt.core import _estimate_vbytes, _script_type_from_bytes, psbt_to_binary
from app.security.core import OfflineStatus
from app.wallet import create_wallet_context, derive_address

from tests.conftest import MNEMONIC, make_prev_tx

_VERIFIED_OFFLINE = OfflineStatus(
    verified=True,
    network_active=False,
    has_default_route=False,
    wifi_blocked=True,
    bluetooth_blocked=True,
    suspicious_services=(),
)


@pytest.fixture(autouse=True)
def _mock_offline_verified(monkeypatch):
    """All PSBT tests run as if the device is offline-verified."""
    with patch("app.psbt.core.current_offline_status", return_value=_VERIFIED_OFFLINE):
        yield


def build_signable_psbt(
    passphrase: str = "",
    destination: str = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
    send_value: int = 90_000,
    change_value: int | None = None,
    extra_external_value: int | None = None,
    input_value: int = 100_000,
):
    ctx = create_wallet_context(MNEMONIC, passphrase, "bip84")
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    outputs = [TransactionOutput(send_value, Script.from_address(destination))]
    if extra_external_value is not None:
        outputs.append(
            TransactionOutput(
                extra_external_value,
                Script.from_address("bc1qv5rmq0kt9yz3pm36wvzct7p3x6mtgehjul0feu"),
            )
        )
    if change_value is not None:
        change_script = Script.from_address(derive_address(ctx, 1, 0).address)
        outputs.append(TransactionOutput(change_value, change_script))
    prev_tx = make_prev_tx(prev_script, input_value)
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=outputs,
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = prev_tx.vout[0]
    psbt.inputs[0].non_witness_utxo = prev_tx
    psbt.inputs[0].bip32_derivations[child.get_public_key()] = DerivationPath(
        bytes.fromhex(ctx.fingerprint),
        [0x80000000 + 84, 0x80000000, 0x80000000, 0, 0],
    )
    return ctx, psbt


def test_parse_invalid_psbt_rejected() -> None:
    with pytest.raises(Exception):
        parse_psbt("not a psbt")


def test_parse_valid_psbt_base64() -> None:
    _ctx, psbt = build_signable_psbt()
    parsed = parse_psbt(psbt.to_base64())
    assert len(parsed.inputs) == 1


def test_review_and_sign_psbt() -> None:
    ctx, psbt = build_signable_psbt()
    review = review_psbt(psbt, ctx)
    assert review.can_sign
    assert review.signable_inputs == 1
    assert review.fee_sats == 10_000
    result = sign_psbt(psbt, ctx)
    assert result.signatures_added == 1
    assert result.signed_psbt_base64.startswith("cHNidP")


def test_wrong_wallet_is_blocked() -> None:
    _ctx, psbt = build_signable_psbt()
    wrong = create_wallet_context(MNEMONIC, "different", "bip84")
    review = review_psbt(psbt, wrong)
    assert not review.can_sign
    assert review.errors
    with pytest.raises(PSBTError):
        sign_psbt(psbt, wrong)


def test_correct_passphrase_wallet_signs_and_wrong_passphrase_is_blocked() -> None:
    ctx, psbt = build_signable_psbt(passphrase="TREZOR")
    wrong = create_wallet_context(MNEMONIC, "wrong passphrase", "bip84")

    assert review_psbt(psbt, ctx).can_sign
    assert not review_psbt(psbt, wrong).can_sign
    assert sign_psbt(psbt, ctx).signatures_added == 1


def test_review_warns_on_high_fee_and_unrecognized_change() -> None:
    ctx, psbt = build_signable_psbt(
        send_value=1_000,
        extra_external_value=1_000,
        input_value=250_000,
    )

    review = review_psbt(psbt, ctx)

    assert review.can_sign
    assert review.fee_sats == 248_000
    assert "Nenhum endereço de troco foi reconhecido. Confira com atenção." in review.warnings
    assert "Taxa absoluta acima de 100.000 sats." in review.warnings
    assert "Taxa acima de 200 sats/vB." in review.warnings


def test_review_recognizes_wallet_change_output() -> None:
    ctx, psbt = build_signable_psbt(send_value=80_000, change_value=15_000)

    review = review_psbt(psbt, ctx)

    assert review.can_sign
    assert review.fee_sats == 5_000
    assert any(output.is_change for output in review.outputs)
    assert "Nenhum endereço de troco foi reconhecido. Confira com atenção." not in review.warnings


# ---------------------------------------------------------------------------
# Malicious / edge-case fixtures
# ---------------------------------------------------------------------------


def _build_psbt_no_utxo() -> tuple:
    """PSBT where the input has no witness_utxo set."""
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    child = ctx.account_key.derive("m/0/0")
    tx = Transaction(
        vin=[TransactionInput(bytes.fromhex("aa" * 32), 0)],
        vout=[
            TransactionOutput(
                90_000, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
            )
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].bip32_derivations[child.get_public_key()] = DerivationPath(
        bytes.fromhex(ctx.fingerprint),
        [0x80000000 + 84, 0x80000000, 0x80000000, 0, 0],
    )
    return ctx, psbt


def _build_psbt_negative_fee() -> tuple:
    """PSBT where outputs exceed declared input value (negative fee)."""
    return build_signable_psbt(send_value=150_000, input_value=50_000)


def _build_psbt_absurd_fee() -> tuple:
    """PSBT with fee >> 100_000 sats."""
    return build_signable_psbt(send_value=1_000, input_value=10_000_000)


def _build_psbt_wrong_path() -> tuple:
    """PSBT where fingerprint matches wallet but derivation path is BIP44 (wrong profile)."""
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    child_wrong = ctx.root_key.derive("m/44'/0'/0'/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, 100_000)
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(
                90_000, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
            )
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = prev_tx.vout[0]
    psbt.inputs[0].non_witness_utxo = prev_tx
    psbt.inputs[0].bip32_derivations[child_wrong.get_public_key()] = DerivationPath(
        bytes.fromhex(ctx.fingerprint),
        [0x80000000 + 44, 0x80000000, 0x80000000, 0, 0],
    )
    return ctx, psbt


def _build_psbt_nonstandard_output() -> tuple:
    """PSBT with an OP_RETURN output that has no valid address."""
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, 100_000)
    op_return = Script(b"\x6a\x08" + b"\xde\xad\xbe\xef" * 2)
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(
                90_000, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
            ),
            TransactionOutput(0, op_return),
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = prev_tx.vout[0]
    psbt.inputs[0].non_witness_utxo = prev_tx
    psbt.inputs[0].bip32_derivations[child.get_public_key()] = DerivationPath(
        bytes.fromhex(ctx.fingerprint),
        [0x80000000 + 84, 0x80000000, 0x80000000, 0, 0],
    )
    return ctx, psbt


def _build_psbt_change_beyond_gap() -> tuple:
    """PSBT with change address at index 200 (just beyond default scan limit of 200)."""
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, 100_000)
    far_change_script = Script.from_address(derive_address(ctx, 1, 200).address)
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(
                80_000, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
            ),
            TransactionOutput(15_000, far_change_script),
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = prev_tx.vout[0]
    psbt.inputs[0].non_witness_utxo = prev_tx
    psbt.inputs[0].bip32_derivations[child.get_public_key()] = DerivationPath(
        bytes.fromhex(ctx.fingerprint),
        [0x80000000 + 84, 0x80000000, 0x80000000, 0, 0],
    )
    return ctx, psbt


def _build_psbt_partially_signable() -> tuple:
    """PSBT with 2 inputs: first belongs to our wallet, second to an unknown wallet."""
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    child = ctx.account_key.derive("m/0/0")
    our_script = Script.from_address(derive_address(ctx, 0, 0).address)
    other_script = Script.from_address(derive_address(ctx, 0, 1).address)
    prev_tx0 = make_prev_tx(our_script, 60_000)
    prev_tx1 = make_prev_tx(other_script, 40_000)
    tx = Transaction(
        vin=[
            TransactionInput(prev_tx0.txid(), 0),
            TransactionInput(prev_tx1.txid(), 0),
        ],
        vout=[
            TransactionOutput(
                90_000, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
            )
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = prev_tx0.vout[0]
    psbt.inputs[0].non_witness_utxo = prev_tx0
    psbt.inputs[0].bip32_derivations[child.get_public_key()] = DerivationPath(
        bytes.fromhex(ctx.fingerprint),
        [0x80000000 + 84, 0x80000000, 0x80000000, 0, 0],
    )
    psbt.inputs[1].witness_utxo = prev_tx1.vout[0]
    psbt.inputs[1].non_witness_utxo = prev_tx1
    # No derivation info on input 1 → not ours
    return ctx, psbt


def test_missing_utxo_is_rejected() -> None:
    ctx, psbt = _build_psbt_no_utxo()
    review = review_psbt(psbt, ctx)
    assert not review.can_sign
    assert any("UTXO ausente" in e for e in review.errors)
    with pytest.raises(PSBTError):
        sign_psbt(psbt, ctx)


def test_negative_fee_is_rejected() -> None:
    ctx, psbt = _build_psbt_negative_fee()
    review = review_psbt(psbt, ctx)
    assert not review.can_sign
    assert any("negativa" in e for e in review.errors)
    with pytest.raises(PSBTError):
        sign_psbt(psbt, ctx)


def test_absurd_fee_warns_but_does_not_block() -> None:
    ctx, psbt = _build_psbt_absurd_fee()
    review = review_psbt(psbt, ctx)
    assert review.can_sign
    assert "Taxa absoluta acima de 100.000 sats." in review.warnings


def test_divergent_fingerprint_is_rejected() -> None:
    ctx, psbt = build_signable_psbt()
    wrong_ctx = create_wallet_context(MNEMONIC, "different_passphrase", "bip84")
    review = review_psbt(psbt, wrong_ctx)
    assert not review.can_sign
    assert any("não contém inputs assináveis" in e for e in review.errors)
    with pytest.raises(PSBTError):
        sign_psbt(psbt, wrong_ctx)


def test_wrong_derivation_path_with_correct_fingerprint_is_rejected() -> None:
    ctx, psbt = _build_psbt_wrong_path()
    review = review_psbt(psbt, ctx)
    assert not review.can_sign
    assert any("derivation path" in e and "m/44'" in e for e in review.errors)
    with pytest.raises(PSBTError):
        sign_psbt(psbt, ctx)


def test_nonstandard_output_warns() -> None:
    ctx, psbt = _build_psbt_nonstandard_output()
    review = review_psbt(psbt, ctx)
    assert review.can_sign
    # PSBT-20: OP_RETURN com value=0 gera warning específico; "endereço não reconhecido"
    # é reservado para scripts não-OP_RETURN sem endereço válido.
    assert any("OP_RETURN" in w for w in review.warnings)


def test_change_beyond_gap_warns() -> None:
    ctx, psbt = _build_psbt_change_beyond_gap()
    review = review_psbt(psbt, ctx)
    assert review.can_sign
    assert "Nenhum endereço de troco foi reconhecido. Confira com atenção." in review.warnings
    assert not any(output.is_change for output in review.outputs)


def test_psbt_v2_warns() -> None:
    ctx, psbt = build_signable_psbt()
    psbt.unknown = {b"\xfb": b"\x02\x00\x00\x00"}
    review = review_psbt(psbt, ctx)
    assert review.can_sign
    assert any("PSBTv2" in w for w in review.warnings)


def test_taproot_input_warns() -> None:
    ctx, psbt = build_signable_psbt()
    psbt.inputs[0].taproot_internal_key = b"\x02" * 32
    review = review_psbt(psbt, ctx)
    assert review.can_sign
    assert any("Taproot" in w for w in review.warnings)


def test_partially_signable_inputs() -> None:
    ctx, psbt = _build_psbt_partially_signable()
    review = review_psbt(psbt, ctx)
    assert review.can_sign
    assert review.signable_inputs == 1
    assert review.input_count == 2
    assert any("Apenas 1 de 2" in warning for warning in review.warnings)


def test_experimental_profile_warns() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip86")
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    destination = Script.from_address(derive_address(ctx, 0, 1).address)
    prev_tx = make_prev_tx(prev_script, 100_000)
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[TransactionOutput(90_000, destination)],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = prev_tx.vout[0]
    psbt.inputs[0].non_witness_utxo = prev_tx
    psbt.inputs[0].taproot_bip32_derivations[child.get_public_key()] = (
        [],
        DerivationPath(
            bytes.fromhex(ctx.fingerprint),
            [0x80000000 + 86, 0x80000000, 0x80000000, 0, 0],
        ),
    )

    review = review_psbt(psbt, ctx)

    assert review.can_sign
    assert any("experimental" in warning for warning in review.warnings)


def test_signable_input_rejects_mismatched_utxo_script() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    child = ctx.account_key.derive("m/0/0")
    # UTXO belongs to index 1, but bip32_derivations claim it's index 0
    wrong_script = Script.from_address(derive_address(ctx, 0, 1).address)
    prev_tx = make_prev_tx(wrong_script, 100_000)
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(
                90_000, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
            )
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = prev_tx.vout[0]
    psbt.inputs[0].non_witness_utxo = prev_tx
    psbt.inputs[0].bip32_derivations[child.get_public_key()] = DerivationPath(
        bytes.fromhex(ctx.fingerprint),
        [0x80000000 + 84, 0x80000000, 0x80000000, 0, 0],
    )

    review = review_psbt(psbt, ctx)

    assert not review.can_sign
    assert any("scriptPubKey" in error for error in review.errors)


def test_duplicate_prevout_is_rejected() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, 60_000)
    txid = prev_tx.txid()
    tx = Transaction(
        vin=[TransactionInput(txid, 0), TransactionInput(txid, 0)],
        vout=[
            TransactionOutput(
                90_000, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
            )
        ],
    )
    psbt = PSBT(tx)
    for inp in psbt.inputs:
        inp.witness_utxo = prev_tx.vout[0]
        inp.non_witness_utxo = prev_tx
        inp.bip32_derivations[child.get_public_key()] = DerivationPath(
            bytes.fromhex(ctx.fingerprint),
            [0x80000000 + 84, 0x80000000, 0x80000000, 0, 0],
        )

    review = review_psbt(psbt, ctx)

    assert not review.can_sign
    assert any("duplicado" in error for error in review.errors)


def test_dust_output_warns() -> None:
    ctx, psbt = build_signable_psbt(send_value=500, input_value=10_000)

    review = review_psbt(psbt, ctx)

    assert review.can_sign
    assert any("poeira" in warning for warning in review.warnings)


# ---------------------------------------------------------------------------
# vbytes estimation accuracy
# ---------------------------------------------------------------------------


def _psbt_with_utxo_script(script: Script, input_value: int = 100_000) -> PSBT:
    """Minimal single-input single-output PSBT with a given UTXO script."""
    tx = Transaction(
        vin=[TransactionInput(bytes.fromhex("ab" * 32), 0)],
        vout=[
            TransactionOutput(
                90_000,
                Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),
            )
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = TransactionOutput(input_value, script)
    return psbt


def test_vbytes_p2wpkh_1in_1out_near_110() -> None:
    from embit.ec import PrivateKey

    pk = PrivateKey(b"\x01" * 32).get_public_key()
    psbt = _psbt_with_utxo_script(p2wpkh(pk))
    vbytes = _estimate_vbytes(psbt)
    assert vbytes is not None
    # Standard 1-in 1-out P2WPKH is ~110 vbytes (141 is for 1-in 2-out with change)
    assert 100 <= vbytes <= 120, f"P2WPKH vbytes out of range: {vbytes}"


def test_vbytes_p2wpkh_less_than_legacy() -> None:
    """SegWit (P2WPKH) must produce fewer vbytes than equivalent legacy (P2PKH)."""
    from embit.ec import PrivateKey

    pk = PrivateKey(b"\x02" * 32).get_public_key()
    segwit = _estimate_vbytes(_psbt_with_utxo_script(p2wpkh(pk)))
    legacy = _estimate_vbytes(_psbt_with_utxo_script(p2pkh(pk)))
    assert segwit is not None and legacy is not None
    assert segwit < legacy, f"Expected segwit ({segwit}) < legacy ({legacy})"


def test_vbytes_p2tr_less_than_p2wpkh() -> None:
    """Taproot key-path is smaller than P2WPKH (smaller witness)."""
    from embit.ec import PrivateKey

    pk = PrivateKey(b"\x03" * 32).get_public_key()
    taproot = _estimate_vbytes(_psbt_with_utxo_script(p2tr(pk)))
    segwit = _estimate_vbytes(_psbt_with_utxo_script(p2wpkh(pk)))
    assert taproot is not None and segwit is not None
    assert taproot < segwit, f"Expected taproot ({taproot}) < segwit ({segwit})"


def test_vbytes_p2sh_p2wpkh_between_legacy_and_segwit() -> None:
    """P2SH-P2WPKH should be larger than P2WPKH but smaller than P2PKH."""
    from embit.ec import PrivateKey

    pk = PrivateKey(b"\x04" * 32).get_public_key()
    nested = _estimate_vbytes(_psbt_with_utxo_script(p2sh(p2wpkh(pk))))
    segwit = _estimate_vbytes(_psbt_with_utxo_script(p2wpkh(pk)))
    legacy = _estimate_vbytes(_psbt_with_utxo_script(p2pkh(pk)))
    assert nested is not None and segwit is not None and legacy is not None
    assert segwit < nested < legacy, (
        f"P2SH-P2WPKH ({nested}) not between P2WPKH ({segwit}) and P2PKH ({legacy})"
    )


def test_vbytes_no_utxo_falls_back_to_nonzero() -> None:
    """Missing witness_utxo still produces a non-zero estimate (fallback to P2WPKH)."""
    ctx, psbt = _build_psbt_no_utxo()
    vbytes = _estimate_vbytes(psbt)
    assert vbytes is not None and vbytes > 0


def test_vbytes_missing_utxo_triggers_warning() -> None:
    """review_psbt warns when vbytes estimate is approximate (no witness_utxo)."""
    ctx, psbt = _build_psbt_no_utxo()
    review = review_psbt(psbt, ctx)
    assert any("vbytes" in w.lower() or "aproximada" in w.lower() for w in review.warnings)


# ---------------------------------------------------------------------------
# Script type detection
# ---------------------------------------------------------------------------


def test_script_type_from_bytes_p2wpkh() -> None:
    from embit.ec import PrivateKey

    pk = PrivateKey(b"\x01" * 32).get_public_key()
    script = p2wpkh(pk)
    assert _script_type_from_bytes(bytes(script.data)) == "p2wpkh"


def test_script_type_from_bytes_p2pkh() -> None:
    from embit.ec import PrivateKey

    pk = PrivateKey(b"\x01" * 32).get_public_key()
    script = p2pkh(pk)
    assert _script_type_from_bytes(bytes(script.data)) == "p2pkh"


def test_script_type_from_bytes_p2tr() -> None:
    from embit.ec import PrivateKey

    pk = PrivateKey(b"\x01" * 32).get_public_key()
    script = p2tr(pk)
    assert _script_type_from_bytes(bytes(script.data)) == "p2tr"


def test_script_type_from_bytes_p2sh() -> None:
    from embit.ec import PrivateKey

    pk = PrivateKey(b"\x01" * 32).get_public_key()
    script = p2sh(p2wpkh(pk))
    assert _script_type_from_bytes(bytes(script.data)) == "p2sh"


def test_script_type_from_bytes_unknown() -> None:
    assert _script_type_from_bytes(b"\xff\x01\x02") == "unknown"


def test_parse_psbt_rejects_oversized_input() -> None:
    with pytest.raises(ValueError, match="tamanho máximo"):
        parse_psbt("x" * 1_000_001)


def test_parse_psbt_rejects_oversized_bytes() -> None:
    with pytest.raises(ValueError, match="tamanho máximo"):
        parse_psbt(b"x" * 1_000_001)


def test_psbt_to_binary_roundtrip() -> None:
    _, psbt = build_signable_psbt()
    b64 = psbt.to_base64()
    raw = psbt_to_binary(b64)
    assert raw[:5] == b"psbt\xff"


def test_psbt_to_binary_rejects_invalid_base64() -> None:
    with pytest.raises(Exception):
        psbt_to_binary("não-é-base64!!!")


def test_sign_psbt_raises_when_no_signatures_added() -> None:
    from unittest.mock import MagicMock
    from embit.psbt import PSBTError

    ctx, psbt = build_signable_psbt()
    psbt_mock = MagicMock()
    psbt_mock.sign_with.return_value = 0

    with pytest.raises(PSBTError, match="Nenhuma assinatura"):
        from app.psbt.core import sign_psbt as _sign

        review = review_psbt(psbt, ctx)
        assert review.can_sign
        # Bypass review and force 0-signature path
        with patch("app.psbt.core.review_psbt") as mock_review:
            mock_review.return_value = review
            psbt_mock.fee.return_value = review.fee_sats
            psbt_mock.to_base64.return_value = psbt.to_base64()
            _sign(psbt_mock, ctx)
