import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from ui_qt.vault_picker import VaultPicker
from ui_qt.unlock_window import UnlockWindow
from ui_qt.main_window import MainWindow

from core.session import Session
from core.vault import load_vault, save_vault


def main():
    app = QApplication(sys.argv)

    picker = VaultPicker()
    if not picker.exec():
        return

    session = Session()

    # ===== Create new vault =====
    if picker.create_new:
        unlock = UnlockWindow(confirm=True)
        if not unlock.exec():
            return

        vault = {
            "meta": {"version": "1.0"},
            "categories": [],
            "entries": [],
        }

        save_vault(vault, unlock.password, picker.selected_path)
        session.unlock(vault, unlock.password)

    # ===== Open existing =====
    else:
        unlock = UnlockWindow()
        if not unlock.exec():
            return

        try:
            vault = load_vault(unlock.password, picker.selected_path)
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", str(e))
            return

        session.unlock(vault, unlock.password)

    win = MainWindow(session)
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
