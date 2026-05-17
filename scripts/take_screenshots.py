"""
Script de captura automática de screenshots do PhantOS ColdWallet.
Usa PySide6 nativo — sem dependências externas.
Dados exibidos são apenas vetores de demonstração públicos (sem fundos).
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Garante que o PYTHONPATH inclui a raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DISPLAY", ":0")

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from app.ui.main_window import MainWindow  # noqa: E402

SCREENSHOTS_DIR = PROJECT_ROOT / "assets" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Mnemônico público de demonstração — 24 palavras (BIP39 test vector, sem fundos reais)
DEMO_MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon abandon art"
)


def grab_window(window: MainWindow, filename: str) -> None:
    app = QApplication.instance()
    if app:
        app.processEvents()
    # QWidget.grab() funciona sem compositor X11 externo
    pixmap = window.grab()
    out = SCREENSHOTS_DIR / filename
    ok = pixmap.save(str(out), "PNG")
    if ok:
        size = out.stat().st_size // 1024
        print(f"[OK] {filename}  ({pixmap.width()}x{pixmap.height()}px, {size} KB)")
    else:
        print(f"[ERRO] Falha ao salvar {filename}")


def run_sequence(app: QApplication, window: MainWindow) -> None:
    step = 0

    def next_step() -> None:
        nonlocal step

        if step == 0:
            # Tela inicial — Bitcoin rain + UI vazia
            window.resize(1280, 860)
            window.show()
            window.raise_()
            window.activateWindow()

        elif step == 1:
            # Garante combo em "24" e captura tela inicial
            window.words_combo.setCurrentText("24")
            grab_window(window, "01-tela-inicial.png")

            # Carrega mnemônico de demonstração (24 palavras)
            window.mnemonic_edit.setPlainText(DEMO_MNEMONIC)

        elif step == 2:
            # Captura: mnemônico inserido (antes de restaurar)
            grab_window(window, "02-seed-inserida.png")

            # Restaura carteira
            window.restore_wallet()

        elif step == 3:
            # Captura: carteira restaurada + endereços
            grab_window(window, "03-carteira-restaurada.png")

        elif step == 4:
            # Mostra recuperação de todos os tipos de endereço
            window.recover_addresses()

        elif step == 5:
            # Captura: recuperação de endereços (BIP44/49/84/86)
            grab_window(window, "04-recuperar-enderecos.png")

        elif step == 6:
            # Exporta watch-only JSON
            window.export_watch_only()

        elif step == 7:
            # Captura: watch-only JSON
            grab_window(window, "05-watch-only-export.png")

        elif step == 8:
            # Captura final: janela cheia com output
            grab_window(window, "main.png")
            print("\nCaptura concluída.")
            print(f"Screenshots salvas em: {SCREENSHOTS_DIR}")
            app.quit()
            return

        step += 1
        QTimer.singleShot(600, next_step)

    QTimer.singleShot(800, next_step)


def main() -> int:
    app = QApplication(sys.argv)

    from app.main import _stylesheet

    app.setStyleSheet(_stylesheet())

    window = MainWindow(kiosk=False)

    run_sequence(app, window)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
