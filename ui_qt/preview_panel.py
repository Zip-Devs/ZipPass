from __future__ import annotations

import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QMessageBox,
)

from utils.icons import get_favicon


class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._entry = None
        self.setObjectName("Preview")

        # ===== Title with icon =====
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)

        self.title_label = QLabel("No entry selected")
        self.title_label.setObjectName("PreviewTitle")

        title_row = QHBoxLayout()
        title_row.addWidget(self.icon_label)
        title_row.addWidget(self.title_label)
        title_row.addStretch()

        # ===== Fields =====
        self.login_edit = QLineEdit()
        self.login_edit.setReadOnly(True)

        self.password_edit = QLineEdit()
        self.password_edit.setReadOnly(True)
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.note_edit = QTextEdit()
        self.note_edit.setReadOnly(True)
        self.note_edit.setFixedHeight(80)

        # ===== Actions =====
        self.copy_login_btn = QToolButton(text="🔑")
        self.copy_password_btn = QToolButton(text="🔐")
        self.eye_btn = QToolButton(text="👁")
        self.eye_btn.setCheckable(True)
        self.open_site_btn = QToolButton(text="🌐")

        actions = QHBoxLayout()
        actions.addWidget(self.copy_login_btn)
        actions.addWidget(self.copy_password_btn)
        actions.addWidget(self.eye_btn)
        actions.addStretch()
        actions.addWidget(self.open_site_btn)

        # ===== Layout =====
        layout = QVBoxLayout(self)
        layout.addLayout(title_row)
        layout.addLayout(actions)
        layout.addWidget(QLabel("Login"))
        layout.addWidget(self.login_edit)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password_edit)
        layout.addWidget(QLabel("Note"))
        layout.addWidget(self.note_edit)
        layout.addStretch()

        # ===== Connections =====
        self.copy_login_btn.clicked.connect(self._copy_login)
        self.copy_password_btn.clicked.connect(self._copy_password)
        self.eye_btn.toggled.connect(self._toggle_password)
        self.open_site_btn.clicked.connect(self._open_site)

        self._set_enabled(False)

    # ================= API =================

    def clear(self):
        self._entry = None
        self.icon_label.clear()
        self.title_label.setText("No entry selected")
        self.login_edit.clear()
        self.password_edit.clear()
        self.note_edit.clear()
        self.eye_btn.setChecked(False)
        self._set_enabled(False)

    def set_entry(self, entry: dict):
        self._entry = entry

        self.title_label.setText(entry.get("service", ""))
        self.login_edit.setText(entry.get("login", ""))
        self.password_edit.setText(entry.get("password", ""))
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.note_edit.setPlainText(entry.get("note", ""))

        icon = get_favicon(entry.get("url", ""))
        if icon:
            self.icon_label.setPixmap(icon.pixmap(24, 24))
        else:
            self.icon_label.clear()

        self.eye_btn.setChecked(False)
        self._set_enabled(True)

    # ================= Internals =================

    def _set_enabled(self, enabled: bool):
        for w in (
            self.copy_login_btn,
            self.copy_password_btn,
            self.eye_btn,
            self.open_site_btn,
        ):
            w.setEnabled(enabled)

    def _copy_login(self):
        if self.login_edit.text():
            self.login_edit.selectAll()
            self.login_edit.copy()

    def _copy_password(self):
        if self.password_edit.text():
            self.password_edit.selectAll()
            self.password_edit.copy()

    def _toggle_password(self, visible: bool):
        self.password_edit.setEchoMode(
            QLineEdit.Normal if visible else QLineEdit.Password
        )

    def _open_site(self):
        if not self._entry:
            return

        url = self._entry.get("url")
        if not url:
            QMessageBox.information(self, "No URL", "This entry has no website.")
            return

        webbrowser.open(url)
