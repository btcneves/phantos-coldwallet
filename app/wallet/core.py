from __future__ import annotations

import ctypes
import json
import secrets

from embit import bip32, bip39, networks
from embit.script import p2pkh, p2sh, p2tr, p2wpkh

from app.descriptors import descriptor_body, descriptor_pair
from app.security.memory import try_mlock, try_munlock, zero_bytearray
from app.wallet.models import AddressRecord, DerivationProfile, WalletContext, WatchOnlyExport


def _zero_str_best_effort(s: str) -> None:
    """Tenta zerará string Python — limitado pela imutabilidade do tipo.

    str em Python é imutável e interned pelo runtime; este método converte
    para bytearray e zera os bytes, mas não garante que o objeto str original
    seja apagado da memória. É a melhor prática possível sem suporte nativo.
    """
    try:
        b = s.encode("utf-8")
        ba = bytearray(b)
        for i in range(len(ba)):
            ba[i] = 0
        # Tenta sobrescrever o buffer interno via ctypes (não portável, falha silenciosa).
        # Layout CPython PyBytesObject: refcnt(8)+type(8)+size(8)+hash(8) = 32 bytes antes dos dados.
        try:
            raw = (ctypes.c_char * len(b)).from_address(id(b) + ctypes.sizeof(ctypes.c_ssize_t) * 4)
            for i in range(len(b)):
                raw[i] = b"\x00"
        except Exception:
            pass
    except Exception:
        pass


SUPPORTED_PROFILES: tuple[DerivationProfile, ...] = (
    DerivationProfile(
        id="bip84",
        name="BIP84 Native SegWit",
        simple_label="Endereço moderno iniciado com bc1q",
        bip=84,
        account_path="m/84'/0'/0'",
        address_prefix_hint="bc1q",
        script_type="p2wpkh",
        descriptor_function="wpkh",
        slip132_public_key="zpub",
    ),
    DerivationProfile(
        id="bip49",
        name="BIP49 Nested SegWit",
        simple_label="Endereço iniciado com 3",
        bip=49,
        account_path="m/49'/0'/0'",
        address_prefix_hint="3",
        script_type="p2sh-p2wpkh",
        descriptor_function="sh-wpkh",
        slip132_public_key="ypub",
    ),
    DerivationProfile(
        id="bip44",
        name="BIP44 Legacy",
        simple_label="Endereço antigo iniciado com 1",
        bip=44,
        account_path="m/44'/0'/0'",
        address_prefix_hint="1",
        script_type="p2pkh",
        descriptor_function="pkh",
        slip132_public_key="xpub",
    ),
    DerivationProfile(
        id="bip86",
        name="BIP86 Taproot",
        simple_label="Endereço Taproot iniciado com bc1p",
        bip=86,
        account_path="m/86'/0'/0'",
        address_prefix_hint="bc1p",
        script_type="p2tr",
        descriptor_function="tr",
        slip132_public_key="xpub",
        experimental=True,
    ),
)


def generate_mnemonic(words: int = 24) -> str:
    if words not in {12, 24}:
        raise ValueError("PhantOS permite gerar seeds de 12 ou 24 palavras.")
    entropy_len = 16 if words == 12 else 32
    return bip39.mnemonic_from_bytes(secrets.token_bytes(entropy_len))


def validate_mnemonic(mnemonic: str) -> str:
    normalized = " ".join(mnemonic.strip().lower().split())
    count = len(normalized.split())
    if count not in {12, 15, 18, 21, 24}:
        raise ValueError("A seed deve ter 12, 15, 18, 21 ou 24 palavras BIP39.")
    if not bip39.mnemonic_is_valid(normalized):
        raise ValueError(
            "Uma ou mais palavras não pertencem à lista BIP39 ou o checksum é inválido."
        )
    return normalized


def get_profile(profile_id: str) -> DerivationProfile:
    for profile in SUPPORTED_PROFILES:
        if profile.id == profile_id:
            return profile
    raise ValueError(f"Tipo de carteira não suportado: {profile_id}")


def create_wallet_context(
    mnemonic: str,
    passphrase: str = "",  # nosec B107
    profile_id: str = "bip84",
    network: str = "main",
) -> WalletContext:
    normalized = validate_mnemonic(mnemonic)
    profile = get_profile(profile_id)
    net = _network(network)

    # Keep seed in a bytearray so we can zero it after use regardless of exceptions.
    # mlock pins the pages in RAM (no swap) on Linux; fails silently elsewhere.
    seed_ba = bytearray(bip39.mnemonic_to_seed(normalized, passphrase))
    if not try_mlock(seed_ba):
        import sys

        print(
            "[PhantOS] AVISO: mlock falhou — seed não bloqueada em RAM (swap inativo)",
            file=sys.stderr,
        )
    try:
        root = bip32.HDKey.from_seed(bytes(seed_ba), version=net["xprv"])
    finally:
        zero_bytearray(seed_ba)
        try_munlock(seed_ba)
        del seed_ba
        # M-14: mnemonic e passphrase são str imutáveis em Python; não podem ser zerados
        # com garantia, mas tentamos sobrescrever os bytes codificados como melhor esforço.
        _zero_str_best_effort(normalized)
        if passphrase:
            _zero_str_best_effort(passphrase)
    account = root.derive(_embit_path(profile.account_path))
    account_public = account.to_public()
    fingerprint = root.my_fingerprint.hex()
    canonical_xpub = account_public.to_base58(net["xpub"])
    compat_key = account_public.to_base58(net[profile.slip132_public_key])
    external, internal = descriptor_pair(
        profile.descriptor_function,
        fingerprint,
        profile.account_path,
        canonical_xpub,
    )
    return WalletContext(
        fingerprint=fingerprint,
        network=network,
        profile=profile,
        # SYS-08 AVISO DE SEGURANÇA: root_key (HDKey privada) persiste no WalletContext enquanto
        # o contexto existir em memória. Faça ctx = None (lock_wallet) imediatamente após assinar.
        root_key=root,
        account_key=account_public,
        account_public_key=account_public,
        account_xpub=canonical_xpub,
        account_compat_xpub=compat_key,
        external_descriptor=external,
        internal_descriptor=internal,
    )


def derive_address(ctx: WalletContext, change: int = 0, index: int = 0) -> AddressRecord:
    if change not in {0, 1}:
        raise ValueError("change deve ser 0 para recebimento ou 1 para troco.")
    if index < 0:
        raise ValueError("index não pode ser negativo.")
    child = ctx.account_public_key.derive(f"m/{change}/{index}")
    address = _address_for_profile(ctx.profile, child, _network(ctx.network))
    desc = descriptor_body(
        ctx.profile.descriptor_function,
        ctx.fingerprint,
        ctx.profile.account_path,
        ctx.account_xpub,
        change,
    )
    return AddressRecord(
        index=index,
        change=change,
        path=f"{ctx.profile.account_path}/{change}/{index}",
        address=address,
        type=f"{ctx.profile.name} {'troco' if change else 'recebimento'}",
        fingerprint=ctx.fingerprint,
        descriptor=desc,
    )


def derive_addresses(ctx: WalletContext, change: int = 0, count: int = 20) -> list[AddressRecord]:
    if count < 1 or count > 1000:
        raise ValueError("A quantidade deve ficar entre 1 e 1000 endereços.")
    return [derive_address(ctx, change=change, index=i) for i in range(count)]


def recover_overview(
    mnemonic: str,
    passphrase: str = "",  # nosec B107
    network: str = "main",
    count: int = 1,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for profile in SUPPORTED_PROFILES:
        ctx = create_wallet_context(mnemonic, passphrase, profile.id, network)
        first = derive_address(ctx, change=0, index=0)
        rows.append(
            {
                "tipo": profile.name,
                "caminho": profile.account_path,
                "primeiro_endereco": first.address,
                "descriptor": ctx.external_descriptor,
                "chave_publica_estendida": ctx.account_compat_xpub,
                "experimental": str(profile.experimental),
            }
        )
    return rows[:count] if count else rows


def watch_only_export(ctx: WalletContext) -> WatchOnlyExport:
    account = int(ctx.profile.account_path.split("/")[-1].replace("'", ""))
    return WatchOnlyExport(
        fingerprint=ctx.fingerprint,
        network=ctx.network,
        account=account,
        derivation_path=ctx.profile.account_path,
        script_type=ctx.profile.script_type,
        descriptor_external=ctx.external_descriptor,
        descriptor_internal=ctx.internal_descriptor,
        extended_public_key=ctx.account_xpub,
        compatible_extended_public_key=ctx.account_compat_xpub,
    )


def watch_only_json(ctx: WalletContext) -> str:
    return json.dumps(watch_only_export(ctx).to_dict(), indent=2, ensure_ascii=False)


def known_addresses(ctx: WalletContext, change: int, limit: int = 200) -> set[str]:
    return {record.address for record in derive_addresses(ctx, change=change, count=limit)}


def _network(network: str) -> dict:
    if network not in networks.NETWORKS:
        raise ValueError(f"Rede não suportada: {network}")
    return networks.NETWORKS[network]


def _embit_path(path: str) -> str:
    return path.replace("'", "h")


def _address_for_profile(profile: DerivationProfile, child_key, net: dict) -> str:
    public_key = child_key.get_public_key()
    if profile.id == "bip44":
        return p2pkh(public_key).address(net)
    if profile.id == "bip49":
        return p2sh(p2wpkh(public_key)).address(net)
    if profile.id == "bip84":
        return p2wpkh(public_key).address(net)
    if profile.id == "bip86":
        return p2tr(public_key).address(net)
    raise ValueError(f"Perfil não suportado: {profile.id}")
