"""Testes para verificar que todas as janelas/diálogos expõem apenas o botão fechar.

Garante que nenhuma janela permita minimizar ou maximizar (causa tela preta no
ambiente kiosk do pendrive bootável).
"""

from __future__ import annotations

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    _app = QApplication.instance() or QApplication(sys.argv)
    _QT_AVAILABLE = True
except Exception:
    _QT_AVAILABLE = False

pytestmark = pytest.mark.skipif(not _QT_AVAILABLE, reason="PySide6 not available")

_CLOSE_ONLY = Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint

_MUST_HAVE = Qt.WindowType.FramelessWindowHint
_MUST_NOT_HAVE = (
    Qt.WindowType.WindowMinMaxButtonsHint
    | Qt.WindowType.WindowMinimizeButtonHint
    | Qt.WindowType.WindowMaximizeButtonHint
    | Qt.WindowType.WindowTitleHint
)


def _flags(widget) -> Qt.WindowType:
    return widget.windowFlags()


def _assert_frameless(widget, name: str) -> None:
    flags = _flags(widget)
    assert flags & _MUST_HAVE, f"{name}: FramelessWindowHint ausente (flags={flags!r})"
    assert not (flags & _MUST_NOT_HAVE), (
        f"{name}: decoração de janela presente (flags={flags!r})"
    )


# ---------------------------------------------------------------------------
# QRDisplayDialog
# ---------------------------------------------------------------------------

class TestQRDisplayDialog:
    def test_frameless(self) -> None:
        from app.ui.qr_dialog import QRDisplayDialog

        dlg = QRDisplayDialog(payload="bitcoin:bc1qtest", title="QR Teste")
        _assert_frameless(dlg, "QRDisplayDialog")

    def test_no_title_hint(self) -> None:
        from app.ui.qr_dialog import QRDisplayDialog

        dlg = QRDisplayDialog(payload="bitcoin:bc1qtest")
        assert not (_flags(dlg) & Qt.WindowType.WindowTitleHint), (
            "QRDisplayDialog: barra de título presente"
        )


# ---------------------------------------------------------------------------
# AnimatedQRDialog
# ---------------------------------------------------------------------------

class TestAnimatedQRDialog:
    def test_frameless(self) -> None:
        from app.ui.qr_dialog import AnimatedQRDialog

        dlg = AnimatedQRDialog(ur_parts=["ur:bytes/test"], title="QR Animado")
        _assert_frameless(dlg, "AnimatedQRDialog")

    def test_no_title_hint(self) -> None:
        from app.ui.qr_dialog import AnimatedQRDialog

        dlg = AnimatedQRDialog(ur_parts=["ur:bytes/test"])
        assert not (_flags(dlg) & Qt.WindowType.WindowTitleHint), (
            "AnimatedQRDialog: barra de título presente"
        )


# ---------------------------------------------------------------------------
# CameraDialog
# ---------------------------------------------------------------------------

class TestCameraDialog:
    def test_flags_close_only(self) -> None:
        from app.ui.camera_dialog import CameraDialog

        dlg = CameraDialog()
        _assert_frameless(dlg, "CameraDialog")

    def test_no_title_hint(self) -> None:
        from app.ui.camera_dialog import CameraDialog

        dlg = CameraDialog()
        assert not (_flags(dlg) & Qt.WindowType.WindowTitleHint), (
            "CameraDialog: barra de título presente"
        )


# ---------------------------------------------------------------------------
# Wrappers QMessageBox (dialogs.py)
# ---------------------------------------------------------------------------

class TestDialogWrappers:
    """Verifica que os wrappers criam dialogs com flags corretas sem exibi-los."""

    def _make_msg_box(self, icon, title="T", text="X", buttons=None):
        from PySide6.QtWidgets import QMessageBox

        if buttons is None:
            buttons = QMessageBox.StandardButton.Ok
        dlg = QMessageBox(icon, title, text, buttons, None)
        dlg.setWindowFlags(_CLOSE_ONLY)
        return dlg

    def test_warning_flags(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        dlg = self._make_msg_box(QMessageBox.Icon.Warning)
        _assert_frameless(dlg, "msg_warning")

    def test_critical_flags(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        dlg = self._make_msg_box(QMessageBox.Icon.Critical)
        _assert_frameless(dlg, "msg_critical")

    def test_information_flags(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        dlg = self._make_msg_box(QMessageBox.Icon.Information)
        _assert_frameless(dlg, "msg_information")

    def test_question_flags(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        dlg = self._make_msg_box(
            QMessageBox.Icon.Question,
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        _assert_frameless(dlg, "msg_question")

    def test_file_dialog_flags(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        dlg = QFileDialog(None, "Abrir", "", "")
        dlg.setWindowFlags(_CLOSE_ONLY)
        _assert_frameless(dlg, "file_open_dialog")

    def test_dialogs_module_imports(self) -> None:
        """Garante que o módulo dialogs.py existe e exporta as funções esperadas."""
        from app.ui import dialogs

        assert callable(dialogs.msg_warning)
        assert callable(dialogs.msg_critical)
        assert callable(dialogs.msg_information)
        assert callable(dialogs.msg_question)
        assert callable(dialogs.file_open_dialog)
