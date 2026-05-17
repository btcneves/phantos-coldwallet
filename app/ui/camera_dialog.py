from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from app.i18n import tr

try:
    from PySide6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices, QVideoSink

    _HAS_MULTIMEDIA = True
except ImportError:
    QCamera = None  # type: ignore[assignment,misc]
    QMediaCaptureSession = None  # type: ignore[assignment,misc]
    QMediaDevices = None  # type: ignore[assignment,misc]
    QVideoSink = None  # type: ignore[assignment,misc]
    _HAS_MULTIMEDIA = False


class CameraDialog(QDialog):
    """Opens the webcam and decodes QR Codes (including animated UR multipart).

    Emits qr_scanned(str) with the QR content when detected.
    For UR multipart (animated crypto-psbt), accumulates parts until the decoder completes.
    """

    qr_scanned = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("cam.title"))
        self.setModal(True)
        self._camera: "QCamera | None" = None
        self._session: "QMediaCaptureSession | None" = None
        self._sink: "QVideoSink | None" = None
        self._last_frame = None
        self._result: str | None = None
        self._ur_parts: list[str] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        if not _HAS_MULTIMEDIA:
            layout.addWidget(QLabel(tr("cam.no_multimedia")))
            layout.addWidget(self._cancel_btn())
            self.setMinimumSize(340, 120)
            return

        cameras = QMediaDevices.videoInputs()
        if not cameras:
            layout.addWidget(QLabel(tr("cam.no_camera")))
            layout.addWidget(self._cancel_btn())
            self.setMinimumSize(380, 140)
            return

        self._frame_lbl = QLabel()
        self._frame_lbl.setMinimumSize(480, 360)
        self._frame_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._frame_lbl.setStyleSheet("background: #000;")
        layout.addWidget(self._frame_lbl)

        self._status_lbl = QLabel(tr("cam.status"))
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_lbl.setWordWrap(True)
        layout.addWidget(self._status_lbl)

        layout.addWidget(self._cancel_btn())
        self.setMinimumSize(520, 480)

        self._setup_camera(cameras[0])

        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self._process_frame)
        self._scan_timer.start(200)

    # ------------------------------------------------------------------
    def _cancel_btn(self) -> QPushButton:
        btn = QPushButton(tr("cam.cancel"))
        btn.clicked.connect(self.reject)
        return btn

    def _setup_camera(self, device) -> None:
        self._sink = QVideoSink()
        self._session = QMediaCaptureSession()
        self._camera = QCamera(device)
        self._session.setCamera(self._camera)
        self._session.setVideoSink(self._sink)
        self._sink.videoFrameChanged.connect(self._on_frame)
        self._camera.start()

    def _on_frame(self, frame) -> None:
        self._last_frame = frame

    def _process_frame(self) -> None:
        frame = self._last_frame
        if frame is None or not frame.isValid():
            return
        self._last_frame = None

        qimg = frame.toImage()
        if qimg.isNull():
            return

        pix = QPixmap.fromImage(qimg).scaled(
            480,
            360,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        self._frame_lbl.setPixmap(pix)

        decoded = self._decode_qr(qimg)
        if decoded:
            self._handle_decoded(decoded)

    def _decode_qr(self, qimg: QImage) -> str | None:
        try:
            import zxingcpp
            from PIL import Image

            rgb = qimg.convertToFormat(QImage.Format.Format_RGB888)
            w, h, bpl = rgb.width(), rgb.height(), rgb.bytesPerLine()
            pil_img = Image.frombytes(
                "RGB", (w, h), bytes(rgb.bits())[: h * bpl], "raw", "RGB", bpl
            )
            result = zxingcpp.read_barcode(pil_img)
            if result and result.text:
                return result.text
        except Exception:
            return None
        return None

    def _handle_decoded(self, text: str) -> None:
        lower = text.lower()
        if lower.startswith("ur:"):
            self._handle_ur_part(text)
        else:
            self._finish(text)

    def _handle_ur_part(self, part: str) -> None:
        if part in self._ur_parts:
            return

        self._ur_parts.append(part)
        n = len(self._ur_parts)

        try:
            from app.ur.vendor.foundation_ur.ur_decoder import URDecoder

            decoder = URDecoder()
            for p in self._ur_parts:
                decoder.receive_part(p)
                if decoder.is_complete():
                    break

            if decoder.is_complete() and decoder.is_success():
                self._finish(self._ur_parts[0] if n == 1 else "\n".join(self._ur_parts))
            else:
                self._status_lbl.setText(tr("cam.ur_parts", n=n))
        except Exception:
            if n == 1:
                self._finish(part)
            else:
                self._status_lbl.setText(tr("cam.ur_parts", n=n))

    def _finish(self, text: str) -> None:
        self._result = text
        self._stop()
        self.qr_scanned.emit(text)
        self.accept()

    def _stop(self) -> None:
        if hasattr(self, "_scan_timer"):
            self._scan_timer.stop()
        if self._camera:
            self._camera.stop()

    def result_text(self) -> str | None:
        return self._result

    def reject(self) -> None:
        self._stop()
        super().reject()

    def closeEvent(self, event) -> None:
        self._stop()
        super().closeEvent(event)
