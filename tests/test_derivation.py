import pytest

from app.wallet import create_wallet_context, derive_address, derive_addresses

from tests.conftest import MNEMONIC

TREZOR_PASSPHRASE = "TREZOR"


def test_bip44_first_address() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip44")
    assert derive_address(ctx, 0, 0).address == "1LqBGSKuX5yYUonjxT5qGfpUsXKYYWeabA"
    assert ctx.account_compat_xpub.startswith("xpub")


def test_bip49_first_address() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip49")
    assert derive_address(ctx, 0, 0).address == "37VucYSaXLCAsxYyAPfbSi9eh4iEcbShgf"
    assert ctx.account_compat_xpub.startswith("ypub")


def test_bip84_first_address() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    assert derive_address(ctx, 0, 0).address == "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"
    assert ctx.account_compat_xpub.startswith("zpub")


def test_bip84_restoration_is_deterministic_without_passphrase() -> None:
    first = create_wallet_context(MNEMONIC, "", "bip84")
    second = create_wallet_context(MNEMONIC, "", "bip84")

    first_addresses = [item.address for item in derive_addresses(first, change=0, count=5)]
    second_addresses = [item.address for item in derive_addresses(second, change=0, count=5)]

    assert first.fingerprint == second.fingerprint == "73c5da0a"
    assert first.account_xpub == second.account_xpub
    assert first.external_descriptor == second.external_descriptor
    assert first_addresses == second_addresses


def test_bip84_passphrase_vectors_are_distinct_and_repeatable() -> None:
    correct = create_wallet_context(MNEMONIC, TREZOR_PASSPHRASE, "bip84")
    repeated = create_wallet_context(MNEMONIC, TREZOR_PASSPHRASE, "bip84")
    wrong = create_wallet_context(MNEMONIC, "wrong passphrase", "bip84")
    no_passphrase = create_wallet_context(MNEMONIC, "", "bip84")

    assert correct.fingerprint == repeated.fingerprint == "b4e3f5ed"
    assert derive_address(correct, 0, 0).address == ("bc1qv5rmq0kt9yz3pm36wvzct7p3x6mtgehjul0feu")
    assert derive_address(correct, 0, 0).address == derive_address(repeated, 0, 0).address
    assert derive_address(wrong, 0, 0).address == ("bc1qkf3vr0mg9q79gm5ljgp994v6gu6t02kg0jjd3g")
    assert derive_address(wrong, 0, 0).address != derive_address(correct, 0, 0).address
    assert derive_address(wrong, 0, 0).address != derive_address(no_passphrase, 0, 0).address


def test_bip86_first_address() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip86")
    assert derive_address(ctx, 0, 0).address == (
        "bc1p5cyxnuxmeuwuvkwfem96lqzszd02n6xdcjrs20cac6yqjjwudpxqkedrcr"
    )
    assert ctx.profile.experimental is True


def test_derive_address_rejects_invalid_change() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    with pytest.raises(ValueError):
        derive_address(ctx, change=2, index=0)


def test_derive_address_rejects_negative_index() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    with pytest.raises(ValueError):
        derive_address(ctx, change=0, index=-1)


def test_derive_addresses_rejects_count_out_of_range() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    with pytest.raises(ValueError):
        derive_addresses(ctx, change=0, count=0)
    with pytest.raises(ValueError):
        derive_addresses(ctx, change=0, count=1001)
