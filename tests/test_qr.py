from app.qr import decode_qr_image, make_qr_png_bytes


def test_qr_png_generation() -> None:
    payload = "bitcoin:bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"
    png = make_qr_png_bytes(payload)
    assert png.startswith(b"\x89PNG")
    assert len(png) > 100
    assert decode_qr_image(png) == payload
