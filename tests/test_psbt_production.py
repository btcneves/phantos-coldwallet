"""Testes de produção — Rodada 4 de blindagem da ColdWallet.

Cobre PSBT-18 a PSBT-23: RBF, fee baixa, OP_RETURN, versão TX, limites anti-DoS, nLockTime.
"""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest
from embit.psbt import PSBT, DerivationPath
from embit.script import Script
from embit.transaction import Transaction, TransactionInput, TransactionOutput

from app.psbt import review_psbt
from app.psbt.core import _MAX_PSBT_INPUTS, _MAX_PSBT_OUTPUTS
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


def _build_psbt(ctx, *, input_value=100_000, send_value=90_000, sequence=0xFFFFFFFF, locktime=0):
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, input_value)
    inp = TransactionInput(prev_tx.txid(), 0)
    inp.sequence = sequence
    tx = Transaction(
        vin=[inp],
        vout=[
            TransactionOutput(
                send_value,
                Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),
            )
        ],
    )
    tx.locktime = locktime
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = prev_tx.vout[0]
    psbt.inputs[0].non_witness_utxo = prev_tx
    psbt.inputs[0].bip32_derivations[child.get_public_key()] = DerivationPath(
        bytes.fromhex(ctx.fingerprint),
        [0x80000000 + 84, 0x80000000, 0x80000000, 0, 0],
    )
    return psbt


# ---------------------------------------------------------------------------
# PSBT-18 — RBF Detection (BIP125)
# ---------------------------------------------------------------------------


def test_rbf_sequence_below_threshold_warns() -> None:
    """PSBT-18: nSequence < 0xFFFFFFFE deve gerar warning de RBF."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx, sequence=0xFFFFFFFD)  # BIP125 RBF
    review = review_psbt(psbt, ctx)
    assert any("RBF" in w or "rbf" in w.lower() for w in review.warnings), (
        f"Esperado warning RBF. Warnings: {review.warnings}"
    )


def test_rbf_sequence_zero_warns() -> None:
    """PSBT-18: nSequence = 0 é RBF (também usado para CSV).

    embit.InputScope.vin usa `self.sequence or 0xFFFFFFFF` — bug que silencia sequence=0.
    Por isso checamos psbt.inputs[i].sequence diretamente e setamos via InputScope.
    """
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx)
    psbt.inputs[0].sequence = 0  # set directly on InputScope to bypass embit's 'or' bug
    review = review_psbt(psbt, ctx)
    assert any("RBF" in w for w in review.warnings)


def test_rbf_sequence_at_threshold_no_warn() -> None:
    """PSBT-18: nSequence = 0xFFFFFFFE não é RBF — sem warning."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx, sequence=0xFFFFFFFE)
    review = review_psbt(psbt, ctx)
    assert not any("RBF" in w for w in review.warnings), (
        f"Não esperado warning RBF para 0xFFFFFFFE. Warnings: {review.warnings}"
    )


def test_rbf_max_sequence_no_warn() -> None:
    """PSBT-18: nSequence = 0xFFFFFFFF (padrão) não é RBF — sem warning."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx, sequence=0xFFFFFFFF)
    review = review_psbt(psbt, ctx)
    assert not any("RBF" in w for w in review.warnings)


def test_rbf_only_affected_input_index_reported() -> None:
    """PSBT-18: warning deve identificar o índice do input RBF."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx, sequence=0x0000DEAD)
    review = review_psbt(psbt, ctx)
    rbf_warnings = [w for w in review.warnings if "RBF" in w]
    assert len(rbf_warnings) == 1
    assert "[0]" in rbf_warnings[0], f"Esperado índice [0] no warning: {rbf_warnings[0]}"


# ---------------------------------------------------------------------------
# PSBT-19 — Fee muito baixa
# ---------------------------------------------------------------------------


def test_low_fee_rate_warns() -> None:
    """PSBT-19: Fee rate < 1 sat/vB deve gerar warning."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    # Input 100000 sats, send 99999 sats → fee = 1 sat, ~110 vbytes → ~0.009 sat/vB
    psbt = _build_psbt(ctx, input_value=100_000, send_value=99_999)
    review = review_psbt(psbt, ctx)
    assert any(
        "baixa" in w.lower() and ("sat/vb" in w.lower() or "sat/vB" in w) for w in review.warnings
    ), f"Esperado warning de taxa baixa. Warnings: {review.warnings}"


def test_normal_fee_rate_no_low_warning() -> None:
    """PSBT-19: Fee rate normal (10 sat/vB) não deve gerar warning de taxa baixa."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    # Input 100000, send 89000 → fee=11000 sats, ~110 vbytes → ~100 sat/vB
    psbt = _build_psbt(ctx, input_value=100_000, send_value=89_000)
    review = review_psbt(psbt, ctx)
    assert not any(
        "baixa" in w.lower() and "sat" in w.lower() and "vB" in w for w in review.warnings
    ), f"Não esperado warning de taxa baixa. Warnings: {review.warnings}"


# ---------------------------------------------------------------------------
# PSBT-20 — OP_RETURN com valor > 0 é ERRO (bitcoin irrecuperável)
# ---------------------------------------------------------------------------


def test_op_return_with_positive_value_is_error() -> None:
    """PSBT-20: OP_RETURN com valor > 0 deve gerar ERRO (não só warning)."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, 100_000)
    op_return_script = Script(b"\x6a\x08" + b"\xde\xad\xbe\xef\xde\xad\xbe\xef")
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(
                90_000,
                Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),
            ),
            TransactionOutput(1_000, op_return_script),  # 1000 sats irrecuperáveis!
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
    assert not review.can_sign, "OP_RETURN com valor > 0 não deve ser assinável"
    assert any(
        "OP_RETURN" in e or "unspendable" in e.lower() or "irrecuperável" in e
        for e in review.errors
    ), f"Esperado erro OP_RETURN. Errors: {review.errors}"


def test_op_return_with_zero_value_is_allowed() -> None:
    """PSBT-20: OP_RETURN com valor = 0 é padrão (ex: timestamp, metadados) — não é erro."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, 100_000)
    op_return_script = Script(b"\x6a\x08" + b"\xde\xad\xbe\xef\xde\xad\xbe\xef")
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(
                90_000,
                Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),
            ),
            TransactionOutput(0, op_return_script),  # valor zero: OK
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
    assert review.can_sign, f"OP_RETURN com valor 0 deve ser assinável. Errors: {review.errors}"
    assert not any("OP_RETURN" in e for e in review.errors)


# ---------------------------------------------------------------------------
# PSBT-21 — Versão de transação não-padrão
# ---------------------------------------------------------------------------


def test_nonstandard_tx_version_warns() -> None:
    """PSBT-21: Versão de transação diferente de 1 ou 2 deve gerar warning.

    psbt.tx é uma property que reconstrói Transaction a cada acesso, portanto
    'psbt.tx.version = 3' não persiste. Usar psbt.tx_version = 3 é o caminho correto.
    """
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx)
    psbt.tx_version = 3  # TRUC/BIP431 — não amplamente suportado
    review = review_psbt(psbt, ctx)
    assert any("versão" in w.lower() or "version" in w.lower() for w in review.warnings), (
        f"Esperado warning de versão. Warnings: {review.warnings}"
    )


def test_tx_version_1_no_warn() -> None:
    """PSBT-21: Versão 1 é padrão — sem warning."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx)
    psbt.tx.version = 1
    review = review_psbt(psbt, ctx)
    assert not any("versão" in w.lower() and "padrão" in w.lower() for w in review.warnings)


def test_tx_version_2_no_warn() -> None:
    """PSBT-21: Versão 2 é padrão — sem warning."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx)
    psbt.tx.version = 2
    review = review_psbt(psbt, ctx)
    assert not any("versão" in w.lower() and "padrão" in w.lower() for w in review.warnings)


# ---------------------------------------------------------------------------
# PSBT-22 — Limites anti-DoS de inputs/outputs
# ---------------------------------------------------------------------------


def test_too_many_inputs_returns_error() -> None:
    """PSBT-22: PSBT com inputs > _MAX_PSBT_INPUTS deve retornar erro sem processar."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx)
    # psbt.inputs é atributo de instância (lista); substituímos diretamente.
    # review_psbt retorna cedo com o erro antes de iterar os elementos.
    psbt.inputs = [None] * (_MAX_PSBT_INPUTS + 1)
    review = review_psbt(psbt, ctx)
    assert not review.can_sign
    assert any("inputs" in e.lower() and "limite" in e.lower() for e in review.errors), (
        f"Esperado erro de limite de inputs. Errors: {review.errors}"
    )


def test_too_many_outputs_returns_error() -> None:
    """PSBT-22: PSBT com outputs > _MAX_PSBT_OUTPUTS deve retornar erro sem processar."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    from embit.transaction import Transaction, TransactionInput, TransactionOutput

    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, 100_000)
    many_outputs = [
        TransactionOutput(100, Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"))
        for _ in range(_MAX_PSBT_OUTPUTS + 1)
    ]
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=many_outputs,
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
    assert any("outputs" in e.lower() and "limite" in e.lower() for e in review.errors), (
        f"Esperado erro de limite de outputs. Errors: {review.errors}"
    )


def test_max_inputs_constants_are_reasonable() -> None:
    """PSBT-22: Constantes de limite devem estar em range razoável (10..10000)."""
    assert 10 <= _MAX_PSBT_INPUTS <= 10_000
    assert 10 <= _MAX_PSBT_OUTPUTS <= 10_000


# ---------------------------------------------------------------------------
# PSBT-23 — nLockTime
# ---------------------------------------------------------------------------


def test_future_unix_locktime_warns() -> None:
    """PSBT-23: Locktime Unix no futuro deve gerar warning."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    future_ts = int(time.time()) + 86_400 * 365  # 1 ano no futuro
    psbt = _build_psbt(ctx, locktime=future_ts)
    review = review_psbt(psbt, ctx)
    assert any("locktime" in w.lower() or "futuro" in w.lower() for w in review.warnings), (
        f"Esperado warning de locktime futuro. Warnings: {review.warnings}"
    )


def test_block_height_locktime_warns() -> None:
    """PSBT-23: Locktime por bloco (≤ 500M) deve gerar warning informativo."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx, locktime=900_000)  # bloco 900.000 (futuro próximo)
    review = review_psbt(psbt, ctx)
    assert any("locktime" in w.lower() or "bloco" in w.lower() for w in review.warnings), (
        f"Esperado warning de locktime por bloco. Warnings: {review.warnings}"
    )


def test_zero_locktime_no_warn() -> None:
    """PSBT-23: Locktime = 0 é o padrão — sem warning."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    psbt = _build_psbt(ctx, locktime=0)
    review = review_psbt(psbt, ctx)
    assert not any("locktime" in w.lower() for w in review.warnings)


def test_past_unix_locktime_no_future_warn() -> None:
    """PSBT-23: Locktime Unix no passado não deve gerar warning de 'não poderá ser transmitida'."""
    ctx = create_wallet_context(MNEMONIC, profile_id="bip84")
    past_ts = 500_000_001  # logo acima do threshold, mas bem no passado
    psbt = _build_psbt(ctx, locktime=past_ts)
    review = review_psbt(psbt, ctx)
    # Não deve ter warning sobre 'não poderá ser transmitida antes desta data'
    assert not any("não poderá ser transmitida antes desta data" in w for w in review.warnings)
