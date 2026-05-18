from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

_CLOSE_ONLY = Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint


def msg_warning(
    parent: QWidget | None,
    title: str,
    text: str,
    buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    default: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
) -> QMessageBox.StandardButton:
    dlg = QMessageBox(QMessageBox.Icon.Warning, title, text, buttons, parent)
    dlg.setDefaultButton(default)
    dlg.setWindowFlags(_CLOSE_ONLY)
    dlg.exec()
    return dlg.standardButton(dlg.clickedButton())


def msg_critical(
    parent: QWidget | None,
    title: str,
    text: str,
    buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    default: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
) -> QMessageBox.StandardButton:
    dlg = QMessageBox(QMessageBox.Icon.Critical, title, text, buttons, parent)
    dlg.setDefaultButton(default)
    dlg.setWindowFlags(_CLOSE_ONLY)
    dlg.exec()
    return dlg.standardButton(dlg.clickedButton())


def msg_information(
    parent: QWidget | None,
    title: str,
    text: str,
    buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    default: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
) -> QMessageBox.StandardButton:
    dlg = QMessageBox(QMessageBox.Icon.Information, title, text, buttons, parent)
    dlg.setDefaultButton(default)
    dlg.setWindowFlags(_CLOSE_ONLY)
    dlg.exec()
    return dlg.standardButton(dlg.clickedButton())


def msg_question(
    parent: QWidget | None,
    title: str,
    text: str,
    buttons: QMessageBox.StandardButton = (
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    ),
    default: QMessageBox.StandardButton = QMessageBox.StandardButton.No,
) -> QMessageBox.StandardButton:
    dlg = QMessageBox(QMessageBox.Icon.Question, title, text, buttons, parent)
    dlg.setDefaultButton(default)
    dlg.setWindowFlags(_CLOSE_ONLY)
    dlg.exec()
    return dlg.standardButton(dlg.clickedButton())


def file_open_dialog(
    parent: QWidget | None,
    title: str,
    directory: str = "",
    name_filter: str = "",
) -> tuple[str, str]:
    dlg = QFileDialog(parent, title, directory, name_filter)
    dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
    dlg.setWindowFlags(_CLOSE_ONLY)
    if dlg.exec():
        files = dlg.selectedFiles()
        return (files[0] if files else "", dlg.selectedNameFilter())
    return ("", "")
