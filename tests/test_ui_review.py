from embit.psbt import DerivationPath, PSBT
from embit.script import Script
from embit.transaction import Transaction, TransactionInput, TransactionOutput

from app.psbt import review_psbt
from app.psbt.presentation import format_psbt_confirmation
from app.wallet import create_wallet_context, derive_address
from tests.conftest import MNEMONIC, make_prev_tx


def _build_psbt_with_change() -> tuple:
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    child = ctx.account_key.derive("m/0/0")
    prev_script = Script.from_address(derive_address(ctx, 0, 0).address)
    prev_tx = make_prev_tx(prev_script, 100_000)
    destination = Script.from_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
    change = Script.from_address(derive_address(ctx, 1, 0).address)
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(80_000, destination),
            TransactionOutput(15_000, change),
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


def test_format_psbt_confirmation_includes_security_summary() -> None:
    ctx, psbt = _build_psbt_with_change()
    review = review_psbt(psbt, ctx)

    message = format_psbt_confirmation(review, ctx)

    assert ctx.fingerprint in message
    assert ctx.profile.account_path in message
    assert "1/1 input(s)" in message
    assert "80.000 sats" in message
    assert "15.000 sats" in message
    assert "5.000 sats" in message
    assert "Taxa/vB" in message
    assert "Paths dos inputs:" in message
