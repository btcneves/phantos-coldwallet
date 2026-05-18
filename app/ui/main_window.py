from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.i18n import current_language, set_language, tr
from app.psbt import parse_psbt, review_psbt, sign_psbt
from app.psbt.core import psbt_to_binary
from app.psbt.presentation import format_psbt_confirmation
from app.psbt.models import PsbtReview
from app.security import current_offline_status, safe_event
from app.ui.bitcoin_rain import BitcoinRainWidget
from app.ui.bip39_input import Bip39SeedWidget
from app.ui.camera_dialog import CameraDialog
from app.ui.dialogs import (
    file_open_dialog,
    msg_critical,
    msg_information,
    msg_question,
    msg_warning,
)
from app.ui.qr_dialog import AnimatedQRDialog, QRDisplayDialog
from app.ur import encode_crypto_psbt_ur_parts
from app.wallet.core import (
    SUPPORTED_PROFILES,
    create_wallet_context,
    derive_addresses,
    generate_mnemonic,
    recover_overview,
    watch_only_json,
)
from app.wallet.models import WalletContext

from embit.psbt import PSBT


class MainWindow(QMainWindow):
    ctx: WalletContext | None
    loaded_psbt: PSBT | None

    def __init__(self, kiosk: bool = False) -> None:
        super().__init__()
        self.ctx = None
        self.loaded_psbt = None
        self._status_label: QLabel | None = None
        self._subtitle_lbl: QLabel | None = None
        self._lang_btn: QPushButton | None = None
        self._form: QFormLayout | None = None
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("PhantOS ColdWallet")
        self.setMinimumSize(1100, 780)
        self.setCentralWidget(self._build())
        self._retranslate()
        if kiosk:
            self.showFullScreen()

    # ------------------------------------------------------------------
    # Layout

    def _build(self) -> QWidget:
        root = QWidget()
        root.setObjectName("RootWidget")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())

        content = QWidget()
        content.setObjectName("ContentPanel")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 14, 28, 14)
        cl.setSpacing(10)
        cl.addLayout(self._build_status_row())
        cl.addLayout(self._build_actions())
        cl.addLayout(self._build_form())
        cl.addWidget(self._build_output(), stretch=1)
        cl.addLayout(self._build_psbt_row())
        layout.addWidget(content, stretch=1)

        return root

    def _build_header(self) -> BitcoinRainWidget:
        rain = BitcoinRainWidget()
        rain.setFixedHeight(190)

        title = QLabel("₿  PhantOS ColdWallet  ₿")
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("JetBrains Mono", 30, QFont.Weight.Black))

        self._subtitle_lbl = QLabel()
        self._subtitle_lbl.setObjectName("HeaderSubtitle")
        self._subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tagline = QLabel('"Vires in Numeris"  —  Satoshi Nakamoto, 2008')
        tagline.setObjectName("HeaderTagline")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        rain.add_overlay_label(title)
        rain.add_overlay_label(self._subtitle_lbl)
        rain.add_overlay_label(tagline)

        return rain

    def _build_status_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        status_lbl = QLabel()
        status_lbl.setObjectName("SecurityStatus")
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label = status_lbl

        self._lang_btn = QPushButton()
        self._lang_btn.setObjectName("LangToggle")
        self._lang_btn.setToolTip("Toggle language / Alternar idioma")
        self._lang_btn.setFixedHeight(36)
        self._lang_btn.clicked.connect(self._toggle_language)

        row.addWidget(status_lbl, stretch=1)
        row.addWidget(self._lang_btn)
        return row

    def _build_actions(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        self._new_btn = QPushButton()
        self._restore_btn = QPushButton()
        self._recover_btn = QPushButton()
        self._export_btn = QPushButton()
        self._export_qr = QPushButton()
        self._sign_btn = QPushButton()
        self._lock_btn = QPushButton()

        for btn in (
            self._new_btn,
            self._restore_btn,
            self._recover_btn,
            self._export_btn,
            self._export_qr,
            self._sign_btn,
            self._lock_btn,
        ):
            btn.setMinimumHeight(46)
            row.addWidget(btn)

        self._new_btn.clicked.connect(self.generate_wallet)
        self._restore_btn.clicked.connect(self.restore_wallet)
        self._recover_btn.clicked.connect(self.recover_addresses)
        self._export_btn.clicked.connect(self.export_watch_only)
        self._export_qr.clicked.connect(self.show_wallet_qr)
        self._sign_btn.clicked.connect(self.sign_transaction)
        self._lock_btn.clicked.connect(self.lock_wallet)

        return row

    def _build_form(self) -> QFormLayout:
        form = QFormLayout()
        form.setSpacing(10)
        self._form = form

        self.words_combo = QComboBox()
        self.words_combo.addItems(["24", "12"])
        self.words_combo.currentTextChanged.connect(self._on_word_count_changed)

        self.profile_combo = QComboBox()
        for profile in SUPPORTED_PROFILES:
            suffix = "  ⚠ experimental" if profile.experimental else ""
            self.profile_combo.addItem(f"{profile.name}{suffix}", profile.id)
        self.profile_combo.currentIndexChanged.connect(self._on_profile_changed)

        self.mnemonic_input = Bip39SeedWidget(word_count=24)

        self.passphrase_edit = QLineEdit()
        self.passphrase_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("", self.words_combo)
        form.addRow("", self.profile_combo)
        form.addRow("", self.mnemonic_input)
        form.addRow("", self.passphrase_edit)

        return form

    def _build_output(self) -> QTextEdit:
        self.output = QTextEdit()
        self.output.setObjectName("OutputArea")
        self.output.setReadOnly(True)
        return self.output

    def _build_psbt_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        self.psbt_edit = QTextEdit()
        self.psbt_edit.setFixedHeight(90)

        self._load_file_btn = QPushButton()
        self._load_file_btn.setMinimumHeight(46)
        self._scan_btn = QPushButton()
        self._scan_btn.setMinimumHeight(46)

        row.addWidget(self.psbt_edit, stretch=1)
        row.addWidget(self._load_file_btn)
        row.addWidget(self._scan_btn)

        self._load_file_btn.clicked.connect(self.load_psbt_file)
        self._scan_btn.clicked.connect(self.scan_psbt_qr)

        return row

    # ------------------------------------------------------------------
    # i18n

    def _toggle_language(self) -> None:
        next_lang = "en_US" if current_language() == "pt_BR" else "pt_BR"
        set_language(next_lang)
        self._retranslate()

    def _retranslate(self) -> None:
        self._new_btn.setText(tr("btn.new_wallet"))
        self._restore_btn.setText(tr("btn.restore_seed"))
        self._recover_btn.setText(tr("btn.recover_addresses"))
        self._export_btn.setText(tr("btn.export_watch_only"))
        self._export_qr.setText(tr("btn.qr_wallet"))
        self._sign_btn.setText(tr("btn.sign_psbt"))
        self._lock_btn.setText(tr("btn.lock"))
        self._load_file_btn.setText(tr("btn.load_psbt"))
        self._scan_btn.setText(tr("btn.scan_qr"))

        if self._form is not None:
            for widget, key in (
                (self.words_combo, "form.words"),
                (self.profile_combo, "form.type"),
                (self.mnemonic_input, "form.seed"),
                (self.passphrase_edit, "form.passphrase"),
            ):
                lbl = self._form.labelForField(widget)
                if isinstance(lbl, QLabel):
                    lbl.setText(tr(key))

        self.mnemonic_input.setPlaceholderText(tr("ph.mnemonic"))
        self.passphrase_edit.setPlaceholderText(tr("ph.passphrase"))
        self.output.setPlaceholderText(tr("ph.output"))
        self.psbt_edit.setPlaceholderText(tr("ph.psbt"))

        if self._subtitle_lbl is not None:
            self._subtitle_lbl.setText(tr("hdr.subtitle"))

        if self._lang_btn is not None:
            label = "EN" if current_language() == "pt_BR" else "PT"
            self._lang_btn.setText(label)

        self._refresh_security_status()

    # ------------------------------------------------------------------
    # Security status bar

    def _refresh_security_status(self) -> None:
        if self._status_label is None:
            return
        status = current_offline_status()
        if status.verified:
            net_txt = tr("sec.net_blocked")
            wifi_txt = tr("sec.wifi_blocked")
            bt_txt = tr("sec.bt_blocked")
            verdict = tr("sec.offline_verified")
        else:
            if status.network_active and status.nftables_drop_active:
                net_txt = tr("sec.net_nft_drop")
            elif status.network_active:
                net_txt = tr("sec.net_active")
            else:
                net_txt = tr("sec.net_inactive")
            wifi_txt = tr("sec.wifi_active") if not status.wifi_blocked else tr("sec.wifi_blocked")
            bt_txt = tr("sec.bt_active") if not status.bluetooth_blocked else tr("sec.bt_blocked")
            verdict = tr("sec.online_warning")
        parts = [
            tr("sec.terminal"),
            net_txt,
            wifi_txt,
            bt_txt,
            verdict,
        ]
        self._status_label.setText("    ·    ".join(parts))

    # ------------------------------------------------------------------
    # Wallet actions

    def generate_wallet(self) -> None:
        words = int(self.words_combo.currentText())
        mnemonic = generate_mnemonic(words)
        self.mnemonic_input.set_mnemonic(mnemonic)
        msg_warning(self, tr("msg.write_down.title"), tr("msg.write_down.body"))
        self._load_context_from_fields(clear_inputs=False)

    def restore_wallet(self) -> None:
        self._load_context_from_fields(clear_inputs=True)

    def _load_context_from_fields(self, *, clear_inputs: bool) -> None:
        try:
            self.ctx = create_wallet_context(
                self.mnemonic_input.get_mnemonic(),
                self.passphrase_edit.text(),
                self.profile_combo.currentData(),
            )
            self.passphrase_edit.clear()
            if clear_inputs:
                self.mnemonic_input.clear()
            first = derive_addresses(self.ctx, change=0, count=5)
            lines = [
                "═══════════════════════════════════════════════",
                tr("out.wallet_loaded"),
                "═══════════════════════════════════════════════",
                f"  {tr('out.fingerprint')} : {self.ctx.fingerprint}",
                f"  {tr('out.type')}        : {self.ctx.profile.name}",
                f"  {tr('out.path')}     : {self.ctx.profile.account_path}",
                "",
                tr("out.recv_addresses"),
            ]
            lines.extend(f"  [{item.index}]  {item.address}" for item in first)
            lines += [
                "",
                tr("out.ext_descriptor"),
                f"  {self.ctx.external_descriptor}",
                "",
                tr("out.ext_pubkey"),
                f"  {self.ctx.account_compat_xpub}",
                "═══════════════════════════════════════════════",
            ]
            self.output.setPlainText("\n".join(lines))
        except Exception as exc:
            msg_critical(self, tr("msg.restore_error.title"), safe_event(str(exc)))

    def closeEvent(self, event):  # noqa: N802
        self.lock_wallet()
        event.accept()

    def lock_wallet(self) -> None:
        self.ctx = None
        self.loaded_psbt = None
        self.mnemonic_input.clear()
        self.passphrase_edit.clear()
        self.psbt_edit.clear()
        self.output.clear()
        msg_information(self, tr("msg.locked.title"), tr("msg.locked.body"))

    def recover_addresses(self) -> None:
        try:
            rows = recover_overview(
                self.mnemonic_input.get_mnemonic(),
                self.passphrase_edit.text(),
                count=0,
            )
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
            self.output.setPlainText("\n".join(lines))
        except Exception as exc:
            msg_critical(self, tr("msg.recovery_error.title"), safe_event(str(exc)))
        finally:
            self.passphrase_edit.clear()
            # SYS-09: limpa o campo de seed após recover_addresses para não deixar
            # a mnemonic exposta na UI após a operação de recuperação.
            self.mnemonic_input.clear()

    def export_watch_only(self) -> None:
        if self.ctx is None:
            self.restore_wallet()
        if self.ctx is None:
            return
        self.output.setPlainText(watch_only_json(self.ctx))

    def show_wallet_qr(self) -> None:
        if self.ctx is None:
            self.restore_wallet()
        if self.ctx is None:
            return
        xpub = self.ctx.account_compat_xpub
        descriptor = self.ctx.external_descriptor
        payload = xpub if len(descriptor) > 500 else descriptor
        kind = tr("qr.wallet.kind_xpub") if payload == xpub else tr("qr.wallet.kind_descriptor")
        dlg = QRDisplayDialog(
            payload=payload,
            title=tr("qr.wallet.title"),
            description=(
                f"{tr('qr.wallet.scan_with')}\n"
                + tr("qr.wallet.type_kind", profile=self.ctx.profile.name, kind=kind)
            ),
            parent=self,
        )
        dlg.exec()

    def scan_psbt_qr(self) -> None:
        dlg = CameraDialog(parent=self)
        dlg.qr_scanned.connect(self._on_psbt_qr_scanned)
        dlg.exec()

    def _on_psbt_qr_scanned(self, text: str) -> None:
        try:
            lines = [ln for ln in text.strip().splitlines() if ln.strip()]
            if len(lines) > 1 and lines[0].lower().startswith("ur:"):
                import base64
                from app.ur.core import decode_crypto_psbt_ur

                psbt_bytes = decode_crypto_psbt_ur(lines)
                b64 = base64.b64encode(psbt_bytes).decode()
                self.psbt_edit.setPlainText(b64)
            else:
                self.psbt_edit.setPlainText(text.strip())
            self._show_psbt_review()
        except Exception as exc:
            msg_warning(
                self,
                tr("msg.qr_scanned.title"),
                tr("msg.qr_scanned.body", exc=exc, text=text[:200]),
            )

    # ------------------------------------------------------------------
    # PSBT actions

    def load_psbt_file(self) -> None:
        path, _ = file_open_dialog(
            self, tr("dlg.load_psbt"), str(Path.home()), tr("dlg.psbt_filter")
        )
        if not path:
            return
        data = Path(path).read_bytes()
        try:
            self.loaded_psbt = parse_psbt(data)
            self.psbt_edit.setPlainText(self.loaded_psbt.to_base64())
            self._show_psbt_review()
        except Exception as exc:
            msg_critical(self, tr("msg.psbt_invalid.title"), str(exc))

    def sign_transaction(self) -> None:
        offline = current_offline_status()
        self._refresh_security_status()
        if not offline.verified:
            issues = []
            if offline.network_active:
                issues.append(tr("iss.net_active"))
            if offline.has_default_route:
                issues.append(tr("iss.default_route"))
            if not offline.wifi_blocked:
                issues.append(tr("iss.wifi_unblocked"))
            if not offline.bluetooth_blocked:
                issues.append(tr("iss.bt_unblocked"))
            if offline.suspicious_services:
                issues.append(tr("iss.services") + ", ".join(offline.suspicious_services))
            detail = "\n".join(f"  • {i}" for i in issues) or f"  • {tr('iss.status_unverified')}"
            msg_critical(
                self, tr("msg.signing_blocked.title"), tr("msg.signing_blocked.body", detail=detail)
            )
            return
        if self.ctx is None:
            self.restore_wallet()
        if self.ctx is None:
            return
        try:
            self.loaded_psbt = parse_psbt(self.psbt_edit.toPlainText())
            review = review_psbt(self.loaded_psbt, self.ctx)
            if review.errors:
                self._render_review(review)
                msg_critical(self, tr("msg.cannot_sign.title"), "\n".join(review.errors))
                return
            self._render_review(review)
            if any("PSBTv2" in w for w in review.warnings):
                resp = msg_warning(
                    self,
                    tr("msg.psbtv2_warn.title"),
                    tr("msg.psbtv2_warn.body"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if resp != QMessageBox.StandardButton.Yes:
                    return
            confirm = msg_question(
                self,
                tr("msg.confirm_sign.title"),
                format_psbt_confirmation(review, self.ctx),
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return
            result = sign_psbt(self.loaded_psbt, self.ctx)
            parts = encode_crypto_psbt_ur_parts(psbt_to_binary(result.signed_psbt_base64))
            self.output.setPlainText(
                "\n".join(
                    [
                        "═══════════════════════════════════════════════",
                        tr("out.psbt_signed"),
                        "═══════════════════════════════════════════════",
                        f"{tr('out.sigs_added')} {result.signatures_added}",
                        "",
                        "  ── Base64 ──",
                        f"  {result.signed_psbt_base64}",
                        "",
                        tr("out.ur_crypto"),
                        *[f"  {p}" for p in parts[:8]],
                        "═══════════════════════════════════════════════",
                    ]
                )
            )
            AnimatedQRDialog(
                ur_parts=parts,
                description=tr("qr.animated.scan"),
                parent=self,
            ).exec()
            # SYS-19: clear the unsigned PSBT from the input field after signing
            # to prevent accidental re-use or leakage of the original unsigned transaction.
            self.psbt_edit.clear()
            self.loaded_psbt = None
        except Exception as exc:
            msg_critical(self, tr("msg.sign_failed.title"), str(exc))

    # ------------------------------------------------------------------
    # Words / profile selection helpers

    def _on_word_count_changed(self, text: str) -> None:
        try:
            self.mnemonic_input.set_word_count(int(text))
        except ValueError:
            pass

    def _on_profile_changed(self) -> None:
        if self.profile_combo.currentData() == "bip86":
            msg_warning(self, tr("msg.taproot_warn.title"), tr("msg.taproot_warn.body"))

    # ------------------------------------------------------------------
    # PSBT review helpers

    def _show_psbt_review(self) -> None:
        if self.ctx is None:
            self.restore_wallet()
        if self.ctx is not None and self.loaded_psbt is not None:
            self._render_review(review_psbt(self.loaded_psbt, self.ctx))

    def _render_review(self, review: PsbtReview) -> None:
        fee_val = review.fee_sats if review.fee_sats is not None else tr("out.fee_unknown")
        fee_rate_val = review.fee_rate_sat_vb if review.fee_rate_sat_vb is not None else "—"
        lines = [
            "═══════════════════════════════════════════════",
            tr("out.psbt_review"),
            "═══════════════════════════════════════════════",
            f"{tr('out.inputs')} {review.input_count}",
            f"{tr('out.outputs')} {review.output_count}",
            f"{tr('out.sent')} {review.total_output_sats} sats",
            f"{tr('out.fee')} {fee_val} sats",
            f"{tr('out.fee_rate')} {fee_rate_val}",
            "",
            tr("out.destinations"),
        ]
        for out in review.outputs:
            tag = tr("out.change_tag") if out.is_change else tr("out.dest_tag")
            addr = out.address or tr("out.unknown_addr")
            lines.append(f"  [{out.index}] {tag}  {out.value_sats} sats  →  {addr}")
        if review.warnings:
            lines += ["", tr("out.warnings")]
            lines += [f"     {w}" for w in review.warnings]
        if review.errors:
            lines += ["", tr("out.errors")]
            lines += [f"     {e}" for e in review.errors]
        lines.append("═══════════════════════════════════════════════")
        self.output.setPlainText("\n".join(lines))
