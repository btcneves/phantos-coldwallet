from app.descriptors import add_checksum
from app.wallet import create_wallet_context
from app.wallet.core import watch_only_export

from tests.conftest import MNEMONIC


def test_descriptor_has_checksum() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    assert ctx.external_descriptor.startswith("wpkh([73c5da0a/84h/0h/0h]")
    assert "#" in ctx.external_descriptor


def test_all_watch_only_descriptors_have_checksum_when_supported() -> None:
    for profile_id, expected_prefix in (
        ("bip84", "wpkh([73c5da0a/84h/0h/0h]"),
        ("bip49", "sh(wpkh([73c5da0a/49h/0h/0h]"),
        ("bip44", "pkh([73c5da0a/44h/0h/0h]"),
        ("bip86", "tr([73c5da0a/86h/0h/0h]"),
    ):
        ctx = create_wallet_context(MNEMONIC, "", profile_id)
        assert ctx.external_descriptor.startswith(expected_prefix)
        assert ctx.internal_descriptor.startswith(expected_prefix.replace("/0/*", "/1/*"))
        assert "#" in ctx.external_descriptor
        assert "#" in ctx.internal_descriptor


def test_descriptor_checksum_is_stable() -> None:
    assert add_checksum("wpkh([73c5da0a/84h/0h/0h]xpub/0/*)") == (
        "wpkh([73c5da0a/84h/0h/0h]xpub/0/*)#ehmvkm6l"
    )


def test_watch_only_export_contains_modern_and_compat_formats() -> None:
    ctx = create_wallet_context(MNEMONIC, "", "bip84")
    export = watch_only_export(ctx)
    assert export.descriptor_external == ctx.external_descriptor
    assert export.extended_public_key.startswith("xpub")
    assert export.compatible_extended_public_key.startswith("zpub")
