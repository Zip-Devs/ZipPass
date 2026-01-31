from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QToolButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QMessageBox,
    QSizePolicy,
    QComboBox,
)

from utils.password import estimate_strength, generate_password


class EntryDialog(QDialog):
    """
    Dialog for creating / editing vault entry.
    """

    def __init__(self, parent=None, entry: dict | None = None, vault: dict | None = None):
        super().__init__(parent)

        self.vault = vault or {}
        self._entry = entry or {}

        self.setWindowTitle("Entry")
        self.setModal(True)
        self.resize(460, 340)

        # ================= Widgets =================

        self.service_edit = QLineEdit()
        self.login_edit = QLineEdit()

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com")

        # ---- Category ----
        self.category_combo = QComboBox()
        self.category_combo.addItem("Все", "all")

        for cat in self.vault.get("categories", []):
            self.category_combo.addItem(cat["name"], cat["id"])

        # ---- Password ----
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.eye_btn = QToolButton(text="👁")
        self.eye_btn.setCheckable(True)
        self.eye_btn.setAutoRaise(True)

        self.copy_btn = QToolButton(text="📋")
        self.copy_btn.setAutoRaise(True)

        self.generate_btn = QToolButton(text="↻")
        self.generate_btn.setAutoRaise(True)

        pw_layout = QHBoxLayout()
        pw_layout.setContentsMargins(0, 0, 0, 0)
        pw_layout.addWidget(self.password_edit)
        pw_layout.addWidget(self.eye_btn)
        pw_layout.addWidget(self.copy_btn)
        pw_layout.addWidget(self.generate_btn)

        self.strength_label = QLabel("Strength: —")
        self.strength_label.setAlignment(Qt.AlignRight)
        self.strength_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.note_edit = QTextEdit()
        self.note_edit.setFixedHeight(60)

        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn.setDefault(True)

        # ================= Layout =================

        form = QGridLayout()
        form.setColumnStretch(1, 1)

        form.addWidget(QLabel("Service"), 0, 0)
        form.addWidget(self.service_edit, 0, 1)

        form.addWidget(QLabel("Login"), 1, 0)
        form.addWidget(self.login_edit, 1, 1)

        form.addWidget(QLabel("URL"), 2, 0)
        form.addWidget(self.url_edit, 2, 1)

        form.addWidget(QLabel("Category"), 3, 0)
        form.addWidget(self.category_combo, 3, 1)

        form.addWidget(QLabel("Password"), 4, 0)
        form.addLayout(pw_layout, 4, 1)

        form.addWidget(self.strength_label, 5, 1)

        form.addWidget(QLabel("Note"), 6, 0, Qt.AlignTop)
        form.addWidget(self.note_edit, 6, 1)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.ok_btn)
        buttons.addWidget(self.cancel_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addStretch()
        layout.addLayout(buttons)

        # ================= Connections =================

        self.password_edit.textChanged.connect(self._update_strength)
        self.eye_btn.toggled.connect(self._toggle_password)
        self.copy_btn.clicked.connect(self._copy_password)
        self.generate_btn.clicked.connect(self._generate_password)

        self.ok_btn.clicked.connect(self._accept)
        self.cancel_btn.clicked.connect(self.reject)

        # ================= Load =================

        if entry:
            self._load_entry(entry)

        self._update_strength(self.password_edit.text())

    # ================= Logic =================

    def _load_entry(self, entry: dict) -> None:
        self.service_edit.setText(entry.get("service", ""))
        self.login_edit.setText(entry.get("login", ""))
        self.url_edit.setText(entry.get("url", ""))
        self.password_edit.setText(entry.get("password", ""))
        self.note_edit.setPlainText(entry.get("note", ""))

        cid = entry.get("category_id", "all")
        index = self.category_combo.findData(cid)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)

    def _toggle_password(self, visible: bool) -> None:
        self.password_edit.setEchoMode(
            QLineEdit.Normal if visible else QLineEdit.Password
        )

    def _copy_password(self) -> None:
        if self.password_edit.text():
            self.password_edit.selectAll()
            self.password_edit.copy()

    def _generate_password(self) -> None:
        self.password_edit.setText(generate_password(length=16))

    def _update_strength(self, password: str) -> None:
        if not password:
            self.strength_label.setText("Strength: —")
            self.strength_label.setProperty("strength", "")
            return

        result = estimate_strength(password)
        self.strength_label.setText(
            f"Strength: {result.level} ({result.score}/100)"
        )
        self.strength_label.setProperty("strength", result.level)
        self.strength_label.style().unpolish(self.strength_label)
        self.strength_label.style().polish(self.strength_label)

    def _accept(self) -> None:
        if not self.service_edit.text().strip():
            QMessageBox.warning(self, "Error", "Service name is required")
            return
        self.accept()

    # ================= Public API =================

    def get_entry_data(self) -> dict:
        return {
            "service": self.service_edit.text().strip(),
            "login": self.login_edit.text().strip(),
            "url": self.url_edit.text().strip(),
            "password": self.password_edit.text(),
            "note": self.note_edit.toPlainText().strip(),
            "category_id": self.category_combo.currentData(),
        }
