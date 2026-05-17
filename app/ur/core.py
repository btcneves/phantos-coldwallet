from __future__ import annotations

from urtypes import PSBT as UrPsbt

from app.ur.vendor.foundation_ur.ur import UR
from app.ur.vendor.foundation_ur.ur_decoder import URDecoder
from app.ur.vendor.foundation_ur.ur_encoder import UREncoder

CRYPTO_PSBT_TYPE = "crypto-psbt"


def encode_crypto_psbt_ur(psbt_bytes: bytes) -> str:
    if not psbt_bytes:
        raise ValueError("PSBT vazia não pode ser codificada em UR.")
    ur = UR(CRYPTO_PSBT_TYPE, UrPsbt(psbt_bytes).to_cbor())
    return UREncoder.encode(ur)


def encode_crypto_psbt_ur_parts(
    psbt_bytes: bytes,
    max_fragment_len: int = 400,
    min_fragment_len: int = 10,
    redundancy: int = 2,
) -> list[str]:
    if redundancy < 1:
        raise ValueError("redundancy deve ser pelo menos 1.")
    ur = UR(CRYPTO_PSBT_TYPE, UrPsbt(psbt_bytes).to_cbor())
    encoder = UREncoder(ur, max_fragment_len=max_fragment_len, min_fragment_len=min_fragment_len)
    if encoder.is_single_part():
        return [encoder.next_part()]
    parts: list[str] = []
    target = max(
        encoder.fountain_encoder.seq_len() * redundancy, encoder.fountain_encoder.seq_len()
    )
    for _ in range(target):
        parts.append(encoder.next_part())
    return parts


def decode_crypto_psbt_ur(payload: str | list[str]) -> bytes:
    if isinstance(payload, str):
        ur = URDecoder.decode(payload)
    else:
        decoder = URDecoder()
        for part in payload:
            decoder.receive_part(part)
            if decoder.is_complete():
                break
        if not decoder.is_success():
            raise ValueError("UR multipart incompleto ou inválido.")
        ur = decoder.result_message()
        if not hasattr(ur, "type"):
            raise ValueError("Decodificação UR falhou: resultado inválido.")
    if ur.type != CRYPTO_PSBT_TYPE:
        raise ValueError(f"Tipo UR inesperado: {ur.type}")
    return bytes(UrPsbt.from_cbor(ur.cbor).data)
