import pytest

from app.psbt import parse_psbt
from app.ur import decode_crypto_psbt_ur, encode_crypto_psbt_ur, encode_crypto_psbt_ur_parts
from tests.test_psbt import build_signable_psbt


def test_single_part_crypto_psbt_ur_roundtrip() -> None:
    payload = b"psbt\xffsmall-test"
    encoded = encode_crypto_psbt_ur(payload)
    assert encoded.startswith("ur:crypto-psbt/")
    assert decode_crypto_psbt_ur(encoded) == payload


def test_multipart_crypto_psbt_ur_roundtrip() -> None:
    payload = b"psbt\xff" + bytes(range(256)) * 6
    parts = encode_crypto_psbt_ur_parts(payload, max_fragment_len=80, redundancy=2)
    assert len(parts) > 1
    assert all(part.startswith("ur:crypto-psbt/") for part in parts)
    assert decode_crypto_psbt_ur(parts) == payload


def test_multipart_crypto_psbt_ur_decode_is_quiet(capsys) -> None:
    payload = b"psbt\xff" + bytes(range(256)) * 6
    parts = encode_crypto_psbt_ur_parts(payload, max_fragment_len=80, redundancy=2)

    assert decode_crypto_psbt_ur(parts) == payload

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_multipart_crypto_psbt_ur_accepts_shuffled_duplicate_parts() -> None:
    payload = b"psbt\xff" + bytes(range(256)) * 6
    parts = encode_crypto_psbt_ur_parts(payload, max_fragment_len=80, redundancy=3)
    shuffled = list(reversed(parts)) + parts[:3]

    assert decode_crypto_psbt_ur(shuffled) == payload


def test_multipart_crypto_psbt_ur_rejects_missing_parts() -> None:
    payload = b"psbt\xff" + bytes(range(256)) * 6
    parts = encode_crypto_psbt_ur_parts(payload, max_fragment_len=80, redundancy=1)

    with pytest.raises(ValueError):
        decode_crypto_psbt_ur(parts[:1])


def test_multipart_crypto_psbt_ur_rejects_mixed_types() -> None:
    payload = b"psbt\xff" + bytes(range(256)) * 6
    parts = encode_crypto_psbt_ur_parts(payload, max_fragment_len=80, redundancy=2)
    parts[0] = parts[0].replace("crypto-psbt", "crypto-output", 1)

    with pytest.raises(Exception):
        decode_crypto_psbt_ur(parts)


def test_multipart_crypto_psbt_ur_rejects_corrupted_part() -> None:
    payload = b"psbt\xff" + bytes(range(256)) * 6
    parts = encode_crypto_psbt_ur_parts(payload, max_fragment_len=80, redundancy=1)
    parts[0] = parts[0][:-1] + ("a" if parts[0][-1] != "a" else "b")

    with pytest.raises(Exception):
        decode_crypto_psbt_ur(parts)


def test_parse_psbt_accepts_newline_separated_multipart_ur() -> None:
    _ctx, psbt = build_signable_psbt()
    parts = encode_crypto_psbt_ur_parts(psbt.serialize(), max_fragment_len=80, redundancy=2)

    parsed = parse_psbt("\n".join(parts))

    assert len(parsed.inputs) == len(psbt.inputs)
