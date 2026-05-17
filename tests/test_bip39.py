import pytest

from app.wallet import create_wallet_context, generate_mnemonic, validate_mnemonic

from tests.conftest import MNEMONIC


def test_validate_known_bip39_vector() -> None:
    assert validate_mnemonic(MNEMONIC) == MNEMONIC


def test_invalid_seed_is_rejected() -> None:
    with pytest.raises(ValueError):
        validate_mnemonic("abandon " * 11 + "wrong")


def test_generate_12_and_24_word_mnemonics() -> None:
    assert len(generate_mnemonic(12).split()) == 12
    assert len(generate_mnemonic(24).split()) == 24


def test_passphrase_changes_wallet() -> None:
    plain = create_wallet_context(MNEMONIC, "", "bip84")
    protected = create_wallet_context(MNEMONIC, "correct horse battery staple", "bip84")
    assert plain.account_xpub != protected.account_xpub


def test_generate_mnemonic_rejects_invalid_word_count() -> None:
    with pytest.raises(ValueError, match="12 ou 24"):
        generate_mnemonic(15)


def test_generate_mnemonic_produces_valid_bip39() -> None:
    for words in (12, 24):
        m = generate_mnemonic(words)
        assert validate_mnemonic(m) == m


def test_create_wallet_context_rejects_invalid_network() -> None:
    with pytest.raises(ValueError, match="Rede não suportada"):
        create_wallet_context(MNEMONIC, "", "bip84", "rede_inexistente")
