from __future__ import annotations

from io import BytesIO

import qrcode
from PIL import Image


def make_qr_png_bytes(payload: str, box_size: int = 8, border: int = 4) -> bytes:
    if not payload:
        raise ValueError("Payload vazio não pode virar QR Code.")
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    out = BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def decode_qr_image(image_bytes: bytes) -> str:
    try:
        import zxingcpp
    except Exception as exc:  # pragma: no cover - dependency is part of runtime install.
        raise RuntimeError("zxing-cpp não está disponível para leitura de QR.") from exc

    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    result = zxingcpp.read_barcode(image)
    if result is None:
        raise ValueError("Nenhum QR Code reconhecido na imagem.")
    return result.text
