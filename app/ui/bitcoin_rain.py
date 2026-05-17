from __future__ import annotations

import secrets

from PySide6.QtCore import QTimer
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
)
from PySide6.QtWidgets import QLabel, QWidget

_CHARS = (
    "₿₿₿₿₿₿₿₿₿₿"
    "0100110100110011010000001100111010"
    "₿₿₿₿1001₿₿₿0011₿₿10001₿₿₿₿₿₿₿₿"
    "010010110100000001100111₿₿₿₿₿₿₿₿"
)
_CHAR_H = 18
_CHAR_W = 14
_RNG = secrets.SystemRandom()


class _Column:
    __slots__ = ("x", "y", "speed", "length", "chars")

    def __init__(self, x: int, win_h: int) -> None:
        self.x = x
        self.y = float(_RNG.randint(-win_h, 0))
        self.speed = _RNG.uniform(0.8, 2.8)
        self.length = _RNG.randint(6, 22)
        self.chars = [_RNG.choice(_CHARS) for _ in range(self.length)]

    def reset(self, win_h: int) -> None:
        self.y = float(_RNG.randint(-200, -40))
        self.speed = _RNG.uniform(0.8, 2.8)
        self.length = _RNG.randint(6, 22)
        self.chars = [_RNG.choice(_CHARS) for _ in range(self.length)]


class BitcoinRainWidget(QWidget):
    """Widget de fundo com chuva de ₿ estilo Matrix na cor Bitcoin orange."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._columns: list[_Column] = []
        self._labels: list[QLabel] = []

        self._font = QFont("Courier New", 11)
        self._font.setBold(True)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(55)

    # ------------------------------------------------------------------
    # Public helpers

    def add_overlay_label(self, label: QLabel) -> None:
        from PySide6.QtCore import Qt as _Qt

        label.setParent(self)
        label.setAttribute(_Qt.WidgetAttribute.WA_TranslucentBackground)
        label.setStyleSheet(label.styleSheet() + " background: transparent;")
        self._labels.append(label)
        self._position_labels()
        label.show()

    # ------------------------------------------------------------------
    # Qt overrides

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._ensure_columns()
        self._position_labels()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # Solid black base
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        painter.setFont(self._font)
        h = self.height()

        for col in self._columns:
            tail = col.length
            for i in range(tail):
                y = int(col.y) - i * _CHAR_H
                if y < -_CHAR_H or y > h + _CHAR_H:
                    continue
                char = col.chars[i % len(col.chars)]
                if i == 0:
                    # Bright head — near white
                    painter.setPen(QColor(255, 220, 140))
                elif i == 1:
                    painter.setPen(QColor(255, 180, 60, 230))
                elif i <= 3:
                    painter.setPen(QColor(247, 147, 26, 200 - i * 30))
                else:
                    alpha = max(15, 170 - i * (150 // max(tail, 1)))
                    painter.setPen(QColor(200, 100, 10, alpha))
                painter.drawText(col.x, y, char)

        # Vertical gradient vignette so text labels are legible
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(0, 0, 0, 120))
        grad.setColorAt(0.25, QColor(0, 0, 0, 40))
        grad.setColorAt(0.75, QColor(0, 0, 0, 40))
        grad.setColorAt(1.0, QColor(0, 0, 0, 160))
        painter.fillRect(self.rect(), grad)

        painter.end()

    # ------------------------------------------------------------------
    # Private

    def _ensure_columns(self) -> None:
        needed = max(1, self.width() // _CHAR_W + 2)
        while len(self._columns) < needed:
            x = len(self._columns) * _CHAR_W + _RNG.randint(0, _CHAR_W // 2)
            self._columns.append(_Column(x, self.height()))

    def _tick(self) -> None:
        h = self.height()
        for col in self._columns:
            col.y += col.speed
            if col.y - col.length * _CHAR_H > h:
                col.reset(h)
        self.update()

    def _position_labels(self) -> None:
        w = self.width()
        h = self.height()
        n = len(self._labels)
        if n == 0:
            return
        # Distribute labels vertically, centered
        padding_top = max(8, (h - n * 44) // 2)
        for i, lbl in enumerate(self._labels):
            lbl.setGeometry(0, padding_top + i * 44, w, 42)
