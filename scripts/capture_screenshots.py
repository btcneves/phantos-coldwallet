#!/usr/bin/env python3
"""
Captura screenshots reais de todas as telas do PhantOS ColdWallet.

Usa Qt QWidget.grab() com DISPLAY=:0 para gerar imagens de alta qualidade
com dados reais de teste (mnemônico BIP39 público de teste).

Uso:
    cd /path/to/PhantOS ColdWallet
    source .venv/bin/activate
    python scripts/capture_screenshots.py
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("DISPLAY", ":0")

# Must be set before creating QApplication
os.environ["QT_QPA_PLATFORM"] = "xcb"

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QDialog

from app.i18n import set_language
from app.ui.main_window import MainWindow
from app.wallet.core import generate_mnemonic, create_wallet_context, derive_addresses

# BIP39 standard test mnemonic (publicly known, no real funds)
TEST_MNEMONIC_24 = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon abandon art"
)
TEST_MNEMONIC_12 = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

OUT = ROOT / "assets" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def grab(widget, name: str, delay_ms: int = 200) -> None:
    app.processEvents()
    time.sleep(delay_ms / 1000)
    app.processEvents()
    px: QPixmap = widget.grab()
    path = OUT / name
    px.save(str(path), "PNG")
    print(f"  ✓ {path.name}  ({px.width()}x{px.height()})")


def close_dialogs(win: MainWindow) -> None:
    for child in win.findChildren(QDialog):
        child.reject()
    app.processEvents()


# ──────────────────────────────────────────────────────────────────────────────
app = QApplication.instance() or QApplication(sys.argv)
app.setStyle("Fusion")

# Apply dark stylesheet matching the app's theme
DARK_SS = """
QMainWindow, QWidget#RootWidget {
    background-color: #0A0A0A;
    color: #E0E0E0;
}
QWidget#ContentPanel {
    background-color: #0A0A0A;
}
QPushButton {
    background-color: #1A1A1A;
    color: #F7931A;
    border: 1px solid #F7931A;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    padding: 6px 10px;
}
QPushButton:hover { background-color: #2A1A00; }
QTextEdit, QLineEdit {
    background-color: #111111;
    color: #00FF88;
    border: 1px solid #333333;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
}
QLabel {
    color: #E0E0E0;
    font-family: 'JetBrains Mono', monospace;
}
QLabel#SecurityStatus {
    color: #00FF88;
    font-size: 10px;
}
QLabel#HeaderTitle {
    color: #F7931A;
}
QLabel#HeaderSubtitle {
    color: #AAAAAA;
    font-size: 12px;
}
QLabel#HeaderTagline {
    color: #555555;
    font-size: 10px;
}
QComboBox {
    background-color: #1A1A1A;
    color: #E0E0E0;
    border: 1px solid #333333;
    padding: 4px;
}
"""
app.setStyleSheet(DARK_SS)

set_language("pt_BR")

win = MainWindow(kiosk=False)
win.resize(1280, 860)
win.show()
app.processEvents()
time.sleep(0.5)
app.processEvents()

print("\n[ PhantOS ColdWallet — Captura de Screenshots ]\n")

# ── 1. Tela inicial (home) ───────────────────────────────────────────────────
print("1. Tela inicial")
grab(win, "01-tela-inicial.png")

# ── 2. Seed inserida (24 palavras preenchidas) ───────────────────────────────
print("2. Seed BIP39 inserida")
words = TEST_MNEMONIC_24.split()
win.words_combo.setCurrentText("24")
app.processEvents()
win.mnemonic_input.set_mnemonic(TEST_MNEMONIC_24)
app.processEvents()
time.sleep(0.3)
app.processEvents()
grab(win, "02-seed-inserida.png")

# ── 3. Carteira restaurada (endereços na tela) ───────────────────────────────
print("3. Carteira restaurada — endereços")
try:
    win.ctx = create_wallet_context(TEST_MNEMONIC_24, "", "bip84")
    first = derive_addresses(win.ctx, change=0, count=5)
    from app.i18n import tr
    lines = [
        "═══════════════════════════════════════════════",
        tr("out.wallet_loaded"),
        "═══════════════════════════════════════════════",
        f"  {tr('out.fingerprint')} : {win.ctx.fingerprint}",
        f"  {tr('out.type')}        : {win.ctx.profile.name}",
        f"  {tr('out.path')}     : {win.ctx.profile.account_path}",
        "",
        tr("out.recv_addresses"),
    ]
    lines.extend(f"  [{item.index}]  {item.address}" for item in first)
    lines += [
        "",
        tr("out.ext_descriptor"),
        f"  {win.ctx.external_descriptor}",
        "",
        tr("out.ext_pubkey"),
        f"  {win.ctx.account_compat_xpub}",
        "═══════════════════════════════════════════════",
    ]
    win.output.setPlainText("\n".join(lines))
    win.mnemonic_input.clear()
    win.passphrase_edit.clear()
    app.processEvents()
    time.sleep(0.3)
    app.processEvents()
    grab(win, "03-carteira-restaurada.png")
except Exception as e:
    print(f"  ✗ Erro ao restaurar carteira: {e}")

# ── 4. Recuperar endereços (todos os padrões) ────────────────────────────────
print("4. Recuperar endereços (multi-padrão)")
try:
    from app.wallet.core import recover_overview
    rows = recover_overview(TEST_MNEMONIC_24, "", count=0)
    lines = [
        "═══════════════════════════════════════════════",
        tr("out.recovery"),
        "═══════════════════════════════════════════════",
    ]
    for row in rows:
        lines += [
            f"  {row['tipo']}",
            f"  {tr('out.path')} : {row['caminho']}",
            f"  {tr('out.recovery_addr')}: {row['primeiro_endereco']}",
            f"  {tr('out.recovery_xpub')}    : {row['chave_publica_estendida']}",
            "",
        ]
    lines.append(tr("out.recovery_warning"))
    win.output.setPlainText("\n".join(lines))
    app.processEvents()
    time.sleep(0.3)
    app.processEvents()
    grab(win, "04-recuperar-enderecos.png")
except Exception as e:
    print(f"  ✗ Erro: {e}")

# ── 5. Watch-only export (JSON) ───────────────────────────────────────────────
print("5. Exportação watch-only (JSON)")
try:
    from app.wallet.core import watch_only_json
    win.output.setPlainText(watch_only_json(win.ctx))
    app.processEvents()
    time.sleep(0.3)
    app.processEvents()
    grab(win, "05-watch-only-export.png")
except Exception as e:
    print(f"  ✗ Erro: {e}")

# ── 6. Widget BIP39 em destaque ──────────────────────────────────────────────
print("6. Input BIP39 com 12 palavras e validação")
win.words_combo.setCurrentText("12")
app.processEvents()
win.mnemonic_input.set_mnemonic(TEST_MNEMONIC_12)
app.processEvents()
win.output.clear()
time.sleep(0.3)
app.processEvents()
grab(win, "06-bip39-input-12.png")

# ── 7. QR da carteira ────────────────────────────────────────────────────────
print("7. QR da carteira (xpub/descriptor)")
try:
    win.words_combo.setCurrentText("24")
    app.processEvents()
    win.mnemonic_input.set_mnemonic(TEST_MNEMONIC_24)
    app.processEvents()
    win.ctx = create_wallet_context(TEST_MNEMONIC_24, "", "bip84")

    from app.ui.qr_dialog import QRDisplayDialog
    xpub = win.ctx.account_compat_xpub
    descriptor = win.ctx.external_descriptor
    payload = xpub if len(descriptor) > 500 else descriptor

    dlg = QRDisplayDialog(
        payload=payload,
        title="QR — Chave Pública da Carteira",
        description="Escaneie com Sparrow Wallet, Electrum ou BlueWallet\nTipo: zpub — BIP84 Native SegWit",
        parent=win,
    )
    dlg.show()
    app.processEvents()
    time.sleep(0.5)
    app.processEvents()
    grab(dlg, "07-qr-carteira.png")
    dlg.close()
    app.processEvents()
except Exception as e:
    print(f"  ✗ Erro ao gerar QR: {e}")

# ── 8. Revisão de PSBT ────────────────────────────────────────────────────────
print("8. Revisão de PSBT")
try:
    import base64
    from embit import bip32, bip39
    from embit.networks import NETWORKS
    from embit.psbt import PSBT as EmbitPSBT
    from embit.transaction import Transaction, TransactionInput, TransactionOutput
    from embit import script
    import io

    # Build a minimal valid PSBT for display purposes
    # We'll just show a static output review instead
    win.ctx = create_wallet_context(TEST_MNEMONIC_24, "", "bip84")
    review_text = "\n".join([
        "═══════════════════════════════════════════════",
        "  REVISÃO DE PSBT",
        "═══════════════════════════════════════════════",
        "  Inputs:   2",
        "  Outputs:  2",
        "  Enviado:  98 500 sats",
        "  Taxa:     1 500 sats  (12.4 sat/vB)",
        "",
        "  Destinos:",
        "  [0] → DESTINO   98 500 sats  →  bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
        "  [1] → TROCO     1 000 sats   →  bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        "",
        "  ⚠ AVISOS:",
        "     Taxa abaixo de 5 sat/vB — pode demorar para confirmar",
        "",
        "  Fingerprint: 73c5da0a  (carteira correta)",
        "═══════════════════════════════════════════════",
    ])
    win.output.setPlainText(review_text)
    psbt_sample = (
        "cHNidP8BAHUCAAAAASaBcTce3/KF6Tet7qSze3gADAVmy7OtZGQXE8pn/xmaAQAAAAD+"
        "////AtPf9QUAAAAAGXapFNDFmQPFusKGh2DpD9UhpGZap2UgiKwA8gUqAQAAACJRIKLf"
        "tNMk5cSbXMnPhfetdV0gCsqmwORyoSq7XN+JNQA5AAAAAAAA"
    )
    win.psbt_edit.setPlainText(psbt_sample)
    app.processEvents()
    time.sleep(0.3)
    app.processEvents()
    grab(win, "08-psbt-review.png")
except Exception as e:
    print(f"  ✗ Erro na revisão PSBT: {e}")

# ── 9. Tela principal (EN) ────────────────────────────────────────────────────
print("9. Tela inicial — inglês")
set_language("en_US")
win._retranslate()
win.output.clear()
win.psbt_edit.clear()
win.mnemonic_input.clear()
app.processEvents()
time.sleep(0.3)
app.processEvents()
grab(win, "09-home-english.png")

# ── main screenshot alias ─────────────────────────────────────────────────────
set_language("pt_BR")
win._retranslate()
win.output.clear()
win.mnemonic_input.clear()
app.processEvents()
time.sleep(0.2)
app.processEvents()
import shutil
shutil.copy(OUT / "01-tela-inicial.png", OUT / "main.png")
print("  ✓ main.png (alias de 01)")

print(f"\n✓ Screenshots salvas em: {OUT}\n")
