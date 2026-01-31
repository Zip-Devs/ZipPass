from PySide6.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QVBoxLayout, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
import os


class VaultPicker(QDialog):
    """
    Select existing .zippass vault or create a new one.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ZipPass")
        self.setFixedSize(360, 200)
        self.setModal(True)

        self.selected_path: str | None = None
        self.create_new: bool = False

        title = QLabel("ZipPass Vault")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: 600;")

        self.open_btn = QPushButton("📂 Открыть существующий vault")
        self.new_btn = QPushButton("➕ Создать новый vault")

        self.open_btn.clicked.connect(self.open_existing)
        self.new_btn.clicked.connect(self.create_new_vault)

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(12)
        layout.addWidget(self.open_btn)
        layout.addWidget(self.new_btn)
        layout.addStretch()

    def open_existing(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть vault",
            "",
            "ZipPass Vault (*.zippass)"
        )
        if not path:
            return

        if not os.path.isfile(path):
            QMessageBox.warning(self, "Ошибка", "Файл не найден")
            return

        self.selected_path = path
        self.create_new = False
        self.accept()

    def create_new_vault(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Создать vault",
            "",
            "ZipPass Vault (*.zippass)"
        )
        if not path:
            return

        if not path.endswith(".zippass"):
            path += ".zippass"

        self.selected_path = path
        self.create_new = True
        self.accept()
