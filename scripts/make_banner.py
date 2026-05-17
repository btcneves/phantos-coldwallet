"""
Gera banner.gif animado para o README do GitHub.
Captura o BitcoinRainWidget com título e frase de Satoshi Nakamoto.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DISPLAY", ":0")

from PySide6.QtCore import Qt, QTimer  # noqa: E402
from PySide6.QtGui import QFont, QPixmap  # noqa: E402
from PySide6.QtWidgets import QApplication, QLabel, QWidget  # noqa: E402

from app.ui.bitcoin_rain import BitcoinRainWidget  # noqa: E402
from PIL import Image  # noqa: E402

LOGO_DIR = PROJECT_ROOT / "assets" / "logo"
LOGO_DIR.mkdir(parents=True, exist_ok=True)

# ── Dimensões do banner ──────────────────────────────────────────────
W, H = 1200, 280

# ── Frase de Satoshi Nakamoto ────────────────────────────────────────
QUOTE_LINE1 = '"The root problem with conventional currency is all the trust that\'s required to make it work."'
QUOTE_LINE2 = "— Satoshi Nakamoto, 2009"

FRAMES: list[Image.Image] = []
FRAME_COUNT = 36  # ~3 segundos a 85ms por frame
FRAME_DELAY = 85  # ms entre frames no GIF


def pixmap_to_pil(pixmap: QPixmap) -> Image.Image:
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        tmp = f.name
    pixmap.save(tmp, "PNG")
    img = Image.open(tmp).copy()
    Path(tmp).unlink(missing_ok=True)
    return img


def build_window() -> tuple[QWidget, BitcoinRainWidget]:
    win = QWidget()
    win.setFixedSize(W, H)
    win.setStyleSheet("background: #0A0A0A;")
    win.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

    rain = BitcoinRainWidget(win)
    rain.setGeometry(0, 0, W, H)

    # ── Título ₿ PhantOS ColdWallet ₿ ───────────────────────────────
    title = QLabel("₿  PhantOS ColdWallet  ₿", win)
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    font_title = QFont("Courier New", 34, QFont.Weight.Black)
    title.setFont(font_title)
    title.setStyleSheet("color: #F7931A;background: transparent;letter-spacing: 3px;")
    title.setGeometry(0, 38, W, 54)

    # ── Subtítulo ───────────────────────────────────────────────────
    sub = QLabel("Carteira Bitcoin offline de código aberto", win)
    sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
    sub.setFont(QFont("Courier New", 13, QFont.Weight.Medium))
    sub.setStyleSheet("color: #FFD700; background: transparent; letter-spacing: 1px;")
    sub.setGeometry(0, 100, W, 26)

    # ── Frase de Satoshi ────────────────────────────────────────────
    quote_line1 = QLabel(
        '"The root problem with conventional currency is all the trust that\'s required to make it work."',
        win,
    )
    quote_line1.setAlignment(Qt.AlignmentFlag.AlignCenter)
    quote_line1.setFont(QFont("Courier New", 10, QFont.Weight.Normal))
    quote_line1.setStyleSheet("color: #C8A060;background: transparent;font-style: italic;")
    quote_line1.setGeometry(0, 152, W, 22)

    quote_line2 = QLabel("— Satoshi Nakamoto, 2009", win)
    quote_line2.setAlignment(Qt.AlignmentFlag.AlignCenter)
    quote_line2.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
    quote_line2.setStyleSheet("color: #A08050;background: transparent;letter-spacing: 1px;")
    quote_line2.setGeometry(0, 178, W, 22)

    # ── Linha separadora laranja ─────────────────────────────────────
    sep = QLabel(win)
    sep.setGeometry(80, 218, W - 160, 1)
    sep.setStyleSheet("background: #F7931A;")

    # ── Status bar minimalista ───────────────────────────────────────
    status = QLabel(
        "₿  OFFLINE  ·  AIR-GAP  ·  BIP39  ·  PSBT  ·  UR  ·  MIT LICENSE",
        win,
    )
    status.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status.setFont(QFont("Courier New", 9))
    status.setStyleSheet("color: #00CC55;background: transparent;letter-spacing: 2px;")
    status.setGeometry(0, 234, W, 20)

    return win, rain


def capture_frame(win: QWidget) -> Image.Image:
    app = QApplication.instance()
    if app:
        app.processEvents()
    return pixmap_to_pil(win.grab())


def run(app: QApplication) -> None:
    win, rain = build_window()
    win.show()

    frame_idx = 0

    def tick() -> None:
        nonlocal frame_idx
        FRAMES.append(capture_frame(win))
        frame_idx += 1
        if frame_idx >= FRAME_COUNT:
            timer.stop()
            save_gif()
            app.quit()

    # Deixa a animação "aquecer" antes de capturar
    QTimer.singleShot(400, lambda: None)

    timer = QTimer()
    timer.setInterval(FRAME_DELAY)
    timer.timeout.connect(tick)
    QTimer.singleShot(500, timer.start)


def save_gif() -> None:
    if not FRAMES:
        print("[ERRO] Nenhum frame capturado.")
        return

    out = LOGO_DIR / "banner.gif"

    first = FRAMES[0].convert("RGBA")
    rest = [f.convert("RGBA") for f in FRAMES[1:]]

    # Converte para paleta com dithering para melhor qualidade
    first_p = first.quantize(colors=128, dither=Image.Dither.FLOYDSTEINBERG)
    rest_p = [f.quantize(colors=128, dither=Image.Dither.FLOYDSTEINBERG) for f in rest]

    first_p.save(
        out,
        format="GIF",
        save_all=True,
        append_images=rest_p,
        loop=0,
        duration=FRAME_DELAY,
        optimize=False,
    )

    size_kb = out.stat().st_size // 1024
    print(
        f"[OK] {out.name}  ({FRAMES[0].width}x{FRAMES[0].height}px, {len(FRAMES)} frames, {size_kb} KB)"
    )


def main() -> int:
    app = QApplication(sys.argv)
    run(app)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
