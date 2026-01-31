import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from core.session import Session
from core.vault import load_vault, save_vault

from ui_qt.vault_picker import VaultPicker
from ui_qt.unlock_window import UnlockWindow
from ui_qt.main_window import MainWindow


def create_empty_vault() -> dict:
    return {
        "meta": {"version": "1.0"},
        "categories": [],
        "entries": [],
    }


def main():
    app = QApplication(sys.argv)

    # 🎨 QSS
    try:
        with open("ui_qt/styles/dark.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    session = Session()

    # ===============================
    # 1️⃣ Pick or create vault
    # ===============================
    picker = VaultPicker()
    if not picker.exec():
        return

    # ===============================
    # 2️⃣ Create new vault
    # ===============================
    if picker.create_new:
        unlock = UnlockWindow(confirm=True)
        if not unlock.exec():
            return

        vault = create_empty_vault()

        try:
            save_vault(vault, unlock.password, picker.selected_path)
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", str(e))
            return

        session.unlock(
            vault,
            unlock.password,
            picker.selected_path
        )

    # ===============================
    # 3️⃣ Open existing vault
    # ===============================
    else:
        unlock = UnlockWindow(confirm=False)
        if not unlock.exec():
            return

        try:
            vault = load_vault(unlock.password, picker.selected_path)
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", str(e))
            return

        session.unlock(
            vault,
            unlock.password,
            picker.selected_path
        )

    # ===============================
    # 4️⃣ Open main window
    # ===============================
    window = MainWindow(session)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
