from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from app.i18n import tr
from app.qr.core import make_qr_png_bytes


class QRDisplayDialog(QDialog):
    """Shows a static QR Code with payload and description."""

    def __init__(
        self,
        payload: str,
        title: str = "QR Code",
        description: str = "",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        if description:
            lbl = QLabel(description)
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)

        qr_lbl = QLabel()
        qr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            png = make_qr_png_bytes(payload, box_size=8)
            pix = QPixmap()
            pix.loadFromData(png)
            pix = pix.scaled(
                400,
                400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            qr_lbl.setPixmap(pix)
        except Exception as exc:
            qr_lbl.setText(tr("qr.error_generate") + str(exc))
        layout.addWidget(qr_lbl)

        preview = payload if len(payload) <= 80 else payload[:78] + "…"
        hint = QLabel(preview)
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("font-size: 11px; color: #b7c2d0;")
        layout.addWidget(hint)

        close_btn = QPushButton(tr("qr.close"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setMinimumSize(480, 560)


class AnimatedQRDialog(QDialog):
    """Shows animated QR with UR crypto-psbt parts for scanning by a watch-only wallet."""

    def __init__(
        self,
        ur_parts: list[str],
        title: str = "",
        description: str = "",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title or tr("qr.animated.title"))
        self.setModal(True)
        self._pixmaps: list[QPixmap] = []
        self._current = 0
        self._prerender(ur_parts)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        if description:
            lbl = QLabel(description)
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)

        self._qr_lbl = QLabel()
        self._qr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._qr_lbl)

        self._counter_lbl = QLabel()
        self._counter_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._counter_lbl.setStyleSheet("font-size: 12px; color: #b7c2d0;")
        layout.addWidget(self._counter_lbl)

        close_btn = QPushButton(tr("qr.close"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setMinimumSize(480, 560)
        self._show_frame(0)

        if len(self._pixmaps) > 1:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._advance)
            self._timer.start(300)

    def _prerender(self, ur_parts: list[str]) -> None:
        seen: set[str] = set()
        for part in ur_parts:
            if part in seen:
                continue
            seen.add(part)
            if len(seen) > 60:
                break
            try:
                png = make_qr_png_bytes(part, box_size=6)
                pix = QPixmap()
                pix.loadFromData(png)
                pix = pix.scaled(
                    380,
                    380,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._pixmaps.append(pix)
            except Exception as exc:
                self._last_prerender_error = str(exc)

    def _show_frame(self, index: int) -> None:
        if not self._pixmaps:
            self._qr_lbl.setText(tr("qr.animated.error"))
            return
        self._qr_lbl.setPixmap(self._pixmaps[index])
        self._counter_lbl.setText(tr("qr.animated.frame", n=index + 1, total=len(self._pixmaps)))

    def _advance(self) -> None:
        self._current = (self._current + 1) % len(self._pixmaps)
        self._show_frame(self._current)

    def closeEvent(self, event) -> None:
        if hasattr(self, "_timer"):
            self._timer.stop()
        super().closeEvent(event)
