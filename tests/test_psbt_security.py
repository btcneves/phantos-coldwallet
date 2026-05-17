"""Testes de segurança PSBT e criptografia — rodada 3 de auditoria.

Cobre PSBT-10 a PSBT-17 e CRYPTO-01 a CRYPTO-09.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from embit.psbt import PSBT, DerivationPath
from embit.script import Script, p2wpkh
from embit.transaction import Transaction, TransactionInput, TransactionOutput

from app.psbt import review_psbt, sign_psbt
from app.psbt.core import _looks_like_psbt_v2, _MAX_PSBT_BYTES, parse_psbt
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
def _mock_offline(monkeypatch):
    with patch("app.psbt.core.current_offline_status", return_value=_VERIFIED_OFFLINE):
        yield


def _build_psbt(ctx, *, input_value=100_000, send_value=90_000):
    """Cria PSBT P2WPKH assinável simples."""
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, input_value)
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(
                send_value, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
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
    return psbt


# ---------------------------------------------------------------------------
# PSBT-11 — Output com valor zero deve gerar warning
# ---------------------------------------------------------------------------


def test_psbt_output_value_zero_warns() -> None:
    """PSBT-11: Output com value=0 deve gerar warning explícito."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, 100_000)
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(
                90_000, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
            ),
            TransactionOutput(
                0,
                Script.from_address(  # output zerado suspeito
                    "bc1qv5rmq0kt9yz3pm36wvzct7p3x6mtgehjul0feu"
                ),
            ),
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
    assert any("zero" in w.lower() for w in review.warnings), (
        f"Esperado warning sobre output zero. Warnings: {review.warnings}"
    )


# ---------------------------------------------------------------------------
# PSBT-17 — Output acima do supply máximo de Bitcoin
# ---------------------------------------------------------------------------


def test_psbt_output_above_max_btc_supply_rejected() -> None:
    """PSBT-17: Output com valor > 21M BTC em sats deve gerar erro."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, 100_000)
    MAX_SATS = 2_100_000_000_000_000
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(
                MAX_SATS + 1, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
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
    assert any("supply" in e.lower() or "máximo" in e.lower() for e in review.errors), (
        f"Esperado erro sobre supply máximo. Errors: {review.errors}"
    )


# ---------------------------------------------------------------------------
# PSBT-16 — _looks_like_psbt_v2 via psbt.version
# ---------------------------------------------------------------------------


def test_psbt_v2_detected_via_version_attribute() -> None:
    """PSBT-16: PSBT com version=2 deve ser detectada como PSBTv2."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx)
    psbt.version = 2
    assert _looks_like_psbt_v2(psbt) is True


def test_psbt_v1_not_detected_as_v2() -> None:
    """PSBT-16: PSBT com version=1 não deve ser detectada como PSBTv2."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx)
    psbt.version = 1
    assert _looks_like_psbt_v2(psbt) is False


def test_psbt_v2_detected_via_unknown_field_fallback() -> None:
    """PSBT-16: Fallback via unknown[b'\\xfb'] deve detectar PSBTv2."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx)
    # Simular chave unknown como bytes (sem version attribute)
    if hasattr(psbt, "version"):
        del psbt.version
    psbt.unknown = {b"\xfb": b"\x02\x00\x00\x00"}
    assert _looks_like_psbt_v2(psbt) is True


# ---------------------------------------------------------------------------
# PSBT-12 — sign_psbt não deve mutar o objeto original
# ---------------------------------------------------------------------------


def test_sign_psbt_does_not_mutate_original() -> None:
    """PSBT-12: sign_psbt deve operar em cópia — objeto original não modificado."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx)
    original_b64 = psbt.to_base64()

    result = sign_psbt(psbt, ctx)

    # O objeto original não deve ter sido modificado (assinaturas não adicionadas nele)
    assert psbt.to_base64() == original_b64, (
        "sign_psbt não deve mutar o objeto PSBT original passado pelo caller"
    )
    # O resultado deve conter a versão assinada
    assert result.signed_psbt_base64 != original_b64
    assert result.signatures_added >= 1


# ---------------------------------------------------------------------------
# PSBT-13 — Input sem UTXO com fingerprint match não deve ser signable
# ---------------------------------------------------------------------------


def test_input_without_utxo_not_counted_as_signable() -> None:
    """PSBT-13: Input com fingerprint match mas sem UTXO não deve contar como signable."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    child = ctx.account_key.derive("m/0/0")
    tx = Transaction(
        vin=[TransactionInput(bytes.fromhex("12" * 32), 0)],
        vout=[
            TransactionOutput(
                90_000, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
            )
        ],
    )
    psbt = PSBT(tx)
    # Input SEM witness_utxo ou non_witness_utxo — mas COM derivação correta
    psbt.inputs[0].bip32_derivations[child.get_public_key()] = DerivationPath(
        bytes.fromhex(ctx.fingerprint),
        [0x80000000 + 84, 0x80000000, 0x80000000, 0, 0],
    )

    review = review_psbt(psbt, ctx)

    # Deve ter erro de UTXO ausente
    assert any("utxo" in e.lower() or "ausente" in e.lower() for e in review.errors), (
        f"Esperado erro de UTXO ausente. Errors: {review.errors}"
    )
    # can_sign deve ser False (erro presente)
    assert not review.can_sign


# ---------------------------------------------------------------------------
# PSBT-15 — Limite de tamanho verificado nos bytes PSBT (não no encoding)
# ---------------------------------------------------------------------------


def test_psbt_size_limit_checked_after_hex_decode() -> None:
    """PSBT-15: PSBT hex que expande para > MAX bytes deve ser rejeitado."""
    # Cria um hex string que ao decodificar excede o limite
    oversized_hex = "70736274ff" + "00" * (_MAX_PSBT_BYTES + 1)
    with pytest.raises((ValueError, Exception)):
        parse_psbt(oversized_hex)


# ---------------------------------------------------------------------------
# PSBT-10 — P2SH redeem_script injetado deve ser detectado
# ---------------------------------------------------------------------------


def test_p2sh_injected_redeem_script_blocked() -> None:
    """PSBT-10: redeem_script diferente do p2wpkh(pubkey) esperado deve gerar erro."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip49")  # P2SH-P2WPKH
    child = ctx.account_key.derive("m/0/0")
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
    psbt.inputs[0].bip32_derivations[child.get_public_key()] = DerivationPath(
        bytes.fromhex(ctx.fingerprint),
        [0x80000000 + 49, 0x80000000, 0x80000000, 0, 0],
    )
    # Injeta redeem_script de outro pubkey (atacante)
    attacker_key = (
        create_wallet_context("zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong")
        .account_key.derive("m/0/0")
        .get_public_key()
    )
    psbt.inputs[0].redeem_script = p2wpkh(attacker_key)

    review = review_psbt(psbt, ctx)
    assert any("redeem" in e.lower() or "injet" in e.lower() for e in review.errors), (
        f"Esperado erro de redeem_script injetado. Errors: {review.errors}"
    )


# ---------------------------------------------------------------------------
# CRYPTO-03 — ec_privkey_negate(zero) deve lançar ValueError
# ---------------------------------------------------------------------------


def test_ec_privkey_negate_zero_raises() -> None:
    """CRYPTO-03: ec_privkey_negate com chave zero deve lançar ValueError."""
    from embit.util.py_secp256k1 import ec_privkey_negate

    with pytest.raises(ValueError):
        ec_privkey_negate(b"\x00" * 32)


def test_ec_privkey_negate_order_raises() -> None:
    """CRYPTO-03: ec_privkey_negate com chave == ORDER deve lançar ValueError."""
    from embit.util.py_secp256k1 import ec_privkey_negate
    from embit.util.key import SECP256K1_ORDER

    order_bytes = SECP256K1_ORDER.to_bytes(32, "big")
    with pytest.raises(ValueError):
        ec_privkey_negate(order_bytes)


# ---------------------------------------------------------------------------
# CRYPTO-09 — ec_pubkey_add para ponto no infinito deve lançar ValueError
# ---------------------------------------------------------------------------


def test_ec_pubkey_add_infinity_raises() -> None:
    """CRYPTO-09: ec_pubkey_add deve lançar ValueError quando ponto resulta em infinito."""
    from embit.util import py_secp256k1
    from embit.util.py_secp256k1 import ec_pubkey_parse
    from embit.ec import PrivateKey

    # Obter public key interna ANTES de fazer qualquer patch
    priv = PrivateKey(bytes.fromhex("01" * 32))
    pub_sec = priv.get_public_key().sec()
    pub_internal = ec_pubkey_parse(pub_sec)

    # Patch apenas do método affine na curva real (mantém on_curve, is_x_coord, etc.)
    real_curve = py_secp256k1._key.SECP256K1
    original_affine = real_curve.affine
    real_curve.affine = lambda point: None  # simula ponto no infinito
    try:
        with pytest.raises(ValueError, match="infinity"):
            py_secp256k1.ec_pubkey_add(pub_internal, b"\x01" * 32)
    finally:
        real_curve.affine = original_affine


# ---------------------------------------------------------------------------
# CRYPTO-07 — schnorrsig_sign com retorno None deve lançar ValueError
# ---------------------------------------------------------------------------


def test_schnorrsig_sign_none_raises() -> None:
    """CRYPTO-07: sign_schnorr retornando None deve lançar ValueError no wrapper."""
    from embit.util import py_secp256k1

    # Patch apenas do sign_schnorr para retornar None (keypair_create usa o módulo original)
    original_sign = py_secp256k1._key.sign_schnorr
    py_secp256k1._key.sign_schnorr = lambda *a, **kw: None
    try:
        from embit.ec import PrivateKey

        privkey = PrivateKey(bytes.fromhex("01" * 32))
        keypair = privkey.serialize() + privkey.get_public_key().sec()
        with pytest.raises(ValueError, match="Failed to sign"):
            py_secp256k1.schnorrsig_sign(b"\xab" * 32, keypair[:32], extra_data=b"\x00" * 32)
    finally:
        py_secp256k1._key.sign_schnorr = original_sign


# ---------------------------------------------------------------------------
# CRYPTO-06 — bip32.child com índice inválido deve lançar HDError
# ---------------------------------------------------------------------------


def test_bip32_child_invalid_index_raises_hderror() -> None:
    """CRYPTO-06: ec_privkey_add falhando deve produzir HDError com mensagem clara."""
    from embit.bip32 import HDKey, HDError
    from embit import bip39

    seed = bip39.mnemonic_to_seed(MNEMONIC)
    root = HDKey.from_seed(seed)

    with patch("embit.bip32.secp256k1") as mock_secp:
        mock_secp.ec_privkey_add.side_effect = ValueError("bad key")
        with pytest.raises(HDError, match="Invalid child key"):
            root.child(0)


# ---------------------------------------------------------------------------
# PSBT-16 — _looks_like_psbt_v2: versão None não é PSBTv2
# ---------------------------------------------------------------------------


def test_psbt_version_none_not_v2() -> None:
    """PSBT-16: PSBT sem version (None) não deve ser detectada como PSBTv2."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx)
    if hasattr(psbt, "version"):
        psbt.version = None
    assert _looks_like_psbt_v2(psbt) is False
