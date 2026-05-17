"""Shared fixtures for the PhantOS test suite."""

from __future__ import annotations

from embit.script import Script
from embit.transaction import Transaction, TransactionInput, TransactionOutput

MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
)


def make_prev_tx(script: Script, value: int) -> Transaction:
    """Build a coinbase-like previous transaction for PSBT test fixtures.

    Providing non_witness_utxo with a matching txid eliminates the embit
    UserWarning that fires when witness_utxo is used without a verifiable
    previous transaction (the Trezor fee-drain mitigation we added to embit).
    """
    return Transaction(
        vin=[TransactionInput(bytes(32), 0xFFFFFFFF)],
        vout=[TransactionOutput(value, script)],
    )
