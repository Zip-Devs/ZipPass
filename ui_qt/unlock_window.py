from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
)
from PySide6.QtCore import Qt


class UnlockWindow(QDialog):
    """
    Master password dialog.
    Used for:
    - opening existing vault
    - creating new vault (with confirmation)
    """

    def __init__(self, confirm: bool = False, parent=None):
        super().__init__(parent)

        self.confirm = confirm
        self.password: str | None = None

        self.setWindowTitle("ZipPass — Unlock")
        self.setFixedSize(380, 260 if confirm else 220)
        self.setModal(True)

        self.build_ui()

        # focus immediately
        self.password_input.setFocus()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(32, 32, 32, 32)

        # ---- Title ----
        title = QLabel("ZipPass")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(
            "Создайте мастер-пароль"
            if self.confirm
            else "Введите мастер-пароль"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #bdbdbd;")

        # ---- Password ----
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Мастер-пароль")
        self.password_input.setMinimumHeight(38)
        self.password_input.returnPressed.connect(self._accept)

        self.password_confirm = None
        if self.confirm:
            self.password_confirm = QLineEdit()
            self.password_confirm.setEchoMode(QLineEdit.Password)
            self.password_confirm.setPlaceholderText("Повторите пароль")
            self.password_confirm.setMinimumHeight(38)
            self.password_confirm.returnPressed.connect(self._accept)

        # ---- Button ----
        self.ok_button = QPushButton("OK")
        self.ok_button.setObjectName("PrimaryButton")
        self.ok_button.clicked.connect(self._accept)

        # ---- Layout ----
        layout.addWidget(title)
        layout.addSpacing(4)
        layout.addWidget(subtitle)
        layout.addSpacing(12)
        layout.addWidget(self.password_input)

        if self.password_confirm:
            layout.addWidget(self.password_confirm)

        layout.addSpacing(12)
        layout.addWidget(self.ok_button)

    def _accept(self):
        password = self.password_input.text()

        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите мастер-пароль")
            return

        if self.confirm:
            if password != self.password_confirm.text():
                QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
                return

        self.password = password
        self.accept()
