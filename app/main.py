from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import os
import sys


# SYS-11: Desabilitar AT-SPI (Assistive Technology) para evitar que processos externos
# leiam conteúdo de campos de seed words via D-Bus de acessibilidade.
os.environ.setdefault("QT_ACCESSIBILITY", "0")
os.environ.setdefault("NO_AT_BRIDGE", "1")

# SYS-14: Desabilitar core dumps e restringir acesso a /proc/PID/mem via PR_SET_DUMPABLE.
try:
    _libc = ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6", use_errno=True)
    _PR_SET_DUMPABLE = 4
    _libc.prctl(_PR_SET_DUMPABLE, 0, 0, 0, 0)
except Exception:
    pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PhantOS ColdWallet")
    parser.add_argument("--kiosk", action="store_true", help="abrir em fullscreen/kiosk")
    args = parser.parse_args(argv)

    try:
        from PySide6.QtWidgets import QApplication

        from app.ui.main_window import MainWindow
    except Exception as exc:
        print(
            "PySide6 não está disponível. Instale as dependências com `python3 -m pip install -e .[dev]`."
        )
        print(f"Erro: {exc}")
        return 2

    app = QApplication(sys.argv)
    app.setStyleSheet(_stylesheet())
    window = MainWindow(kiosk=args.kiosk)
    if not args.kiosk:
        window.show()
    return app.exec()


def _stylesheet() -> str:
    return """
    /* ── Base ── */
    QMainWindow, QDialog {
        background: #0A0A0A;
    }
    QWidget {
        background: #0A0A0A;
        color: #E8E0D0;
        font-family: "JetBrains Mono", "Cascadia Code", "Fira Mono", "Courier New", monospace;
        font-size: 13px;
    }

    /* ── Central content panel ── */
    QWidget#ContentPanel {
        background: #0D0F12;
        border-top: 2px solid #F7931A;
    }

    /* ── Header labels (on rain background) ── */
    QLabel#HeaderTitle {
        color: #F7931A;
        font-size: 32px;
        font-weight: 900;
        letter-spacing: 3px;
        background: transparent;
    }
    QLabel#HeaderSubtitle {
        color: #FFD700;
        font-size: 14px;
        letter-spacing: 1.5px;
        background: transparent;
    }
    QLabel#HeaderTagline {
        color: #888070;
        font-size: 12px;
        font-style: italic;
        letter-spacing: 0.5px;
        background: transparent;
    }

    /* ── Security status bar ── */
    QLabel#SecurityStatus {
        background: #001A0D;
        border: 1px solid #00CC55;
        border-radius: 4px;
        padding: 8px 20px;
        color: #00FF88;
        font-size: 11px;
        letter-spacing: 1.2px;
    }

    /* ── Language toggle button ── */
    QPushButton#LangToggle {
        background: #0D0F12;
        color: #A09070;
        border: 1px solid #3A3020;
        border-radius: 4px;
        padding: 4px 14px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        min-width: 54px;
    }
    QPushButton#LangToggle:hover {
        background: #1A1200;
        border-color: #F7931A;
        color: #F7931A;
    }
    QPushButton#LangToggle:pressed {
        background: #D4780D;
        color: #000;
    }

    /* ── Buttons ── */
    QPushButton {
        background: #1A1200;
        color: #F7931A;
        border: 1px solid #F7931A;
        border-radius: 4px;
        padding: 8px 14px;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 0.5px;
    }
    QPushButton:hover {
        background: #F7931A;
        color: #000000;
        border-color: #FFB347;
    }
    QPushButton:pressed {
        background: #D4780D;
        color: #000000;
    }
    QPushButton:disabled {
        background: #1A1A1A;
        color: #555555;
        border-color: #333333;
    }

    /* ── Input fields ── */
    QTextEdit, QLineEdit {
        background: #080B0E;
        border: 1px solid #3A2800;
        border-radius: 4px;
        padding: 8px 10px;
        color: #E8E0D0;
        selection-background-color: #F7931A;
        selection-color: #000000;
    }
    QTextEdit:focus, QLineEdit:focus {
        border-color: #F7931A;
    }
    QTextEdit#OutputArea {
        border-color: #2A2000;
        color: #C8BC9C;
        font-size: 13px;
        line-height: 1.6;
    }

    /* ── ComboBox ── */
    QComboBox {
        background: #080B0E;
        border: 1px solid #3A2800;
        border-radius: 4px;
        padding: 7px 10px;
        color: #E8E0D0;
    }
    QComboBox:focus {
        border-color: #F7931A;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox QAbstractItemView {
        background: #0D0F12;
        border: 1px solid #F7931A;
        color: #E8E0D0;
        selection-background-color: #F7931A;
        selection-color: #000000;
    }

    /* ── Form labels ── */
    QFormLayout QLabel {
        color: #C4B896;
        font-size: 13px;
        font-weight: 500;
    }

    /* ── Scrollbars ── */
    QScrollBar:vertical {
        background: #0D0F12;
        width: 7px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: #F7931A;
        border-radius: 3px;
        min-height: 20px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }

    /* ── QR & Camera dialogs ── */
    QDialog {
        background: #0A0A0A;
    }
    QDialog QLabel {
        color: #E8E0D0;
    }

    /* ── Message boxes ── */
    QMessageBox {
        background: #0D0F12;
    }
    QMessageBox QLabel {
        color: #E8E0D0;
        font-size: 14px;
        line-height: 1.5;
    }
    """


if __name__ == "__main__":
    raise SystemExit(main())
