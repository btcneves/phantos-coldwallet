from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PsbtInputReview:
    index: int
    value_sats: int | None
    fingerprint_matches: bool
    derivation_path: str | None


@dataclass(frozen=True)
class PsbtOutputReview:
    index: int
    value_sats: int
    address: str | None
    is_change: bool


@dataclass(frozen=True)
class PsbtReview:
    version: int | None
    input_count: int
    output_count: int
    inputs: list[PsbtInputReview]
    outputs: list[PsbtOutputReview]
    total_input_sats: int | None
    total_output_sats: int
    fee_sats: int | None
    estimated_vbytes: int | None
    fee_rate_sat_vb: float | None
    signable_inputs: int
    warnings: list[str]
    errors: list[str]

    @property
    def can_sign(self) -> bool:
        return not self.errors and self.signable_inputs > 0


@dataclass(frozen=True)
class SignedPsbtResult:
    signed_psbt_base64: str
    signatures_added: int
    final_tx_hex: str | None = None
