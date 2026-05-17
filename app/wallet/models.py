from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DerivationProfile:
    id: str
    name: str
    simple_label: str
    bip: int
    account_path: str
    address_prefix_hint: str
    script_type: str
    descriptor_function: str
    slip132_public_key: str
    experimental: bool = False


@dataclass(frozen=True)
class AddressRecord:
    index: int
    change: int
    path: str
    address: str
    type: str
    fingerprint: str
    descriptor: str


@dataclass
class WalletContext:
    fingerprint: str
    network: str
    profile: DerivationProfile
    root_key: Any = field(repr=False)
    account_key: Any = field(repr=False)
    account_public_key: Any = field(repr=False)
    account_xpub: str
    account_compat_xpub: str
    external_descriptor: str
    internal_descriptor: str


@dataclass(frozen=True)
class WatchOnlyExport:
    fingerprint: str
    network: str
    account: int
    derivation_path: str
    script_type: str
    descriptor_external: str
    descriptor_internal: str
    extended_public_key: str
    compatible_extended_public_key: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "fingerprint": self.fingerprint,
            "network": self.network,
            "account": self.account,
            "derivation_path": self.derivation_path,
            "script_type": self.script_type,
            "descriptor_external": self.descriptor_external,
            "descriptor_internal": self.descriptor_internal,
            "extended_public_key": self.extended_public_key,
            "compatible_extended_public_key": self.compatible_extended_public_key,
        }
