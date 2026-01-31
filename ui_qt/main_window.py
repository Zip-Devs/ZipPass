from PySide6.QtCore import (
    Qt,
    QSize,
    QSortFilterProxyModel,
    QTimer,
    QEvent,
)
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTreeView,
    QLineEdit,
    QSplitter,
    QHBoxLayout,
    QVBoxLayout,
    QToolBar,
    QMessageBox,
    QMenu,
    QInputDialog,
    QFileDialog,
)

from ui_qt.entry_dialog import EntryDialog
from ui_qt.preview_panel import PreviewPanel
from ui_qt.models.entries_model import EntriesModel
from core.vault import save_vault
from utils.csv_io import export_to_csv, import_from_csv

import os


class MainWindow(QMainWindow):
    def __init__(self, session):
        super().__init__()

        if not session.is_unlocked:
            raise RuntimeError("Session is locked")

        self.session = session
        self.vault = session.vault

        self.setWindowTitle("ZipPass")
        self.setMinimumSize(1100, 620)

        self.build_ui()
        self.build_toolbar()

        # ===== Auto-lock timer =====
        self._lock_timer = QTimer(self)
        self._lock_timer.setInterval(1000)
        self._lock_timer.timeout.connect(self.session.check_inactivity)
        self._lock_timer.start()

        self.session.on_lock = self._on_session_locked

        # ===== Shortcuts =====
        select_all = QAction(self)
        select_all.setShortcut("Ctrl+A")
        select_all.triggered.connect(self.entries_view.selectAll)
        self.addAction(select_all)

        delete_selected = QAction(self)
        delete_selected.setShortcut("Delete")
        delete_selected.triggered.connect(self.delete_selected_entries)
        self.addAction(delete_selected)

        delete_all = QAction(self)
        delete_all.setShortcut("Ctrl+Shift+Delete")
        delete_all.triggered.connect(self.delete_all_entries)
        self.addAction(delete_all)

    # ================= Auto-lock =================

    def _on_session_locked(self, reason: str):
        QMessageBox.information(
            self,
            "Session locked",
            f"Session locked ({reason})"
        )
        self.close()

    def mousePressEvent(self, event):
        self.session.notify_activity()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        self.session.notify_activity()
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.session.notify_focus_lost()
        super().focusOutEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            self.session.notify_minimized()
        super().changeEvent(event)

    # ================= Toolbar =================

    def build_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))

        self.act_add = QAction("➕ Добавить", self)
        self.act_edit = QAction("✏️ Редактировать", self)
        self.act_delete = QAction("🗑 Удалить", self)

        self.act_add.triggered.connect(self.add_entry)
        self.act_edit.triggered.connect(self.edit_entry)
        self.act_delete.triggered.connect(self.delete_selected_entries)

        toolbar.addAction(self.act_add)
        toolbar.addAction(self.act_edit)
        toolbar.addAction(self.act_delete)

        self.act_delete_all = QAction("🔥 Удалить всё", self)
        self.act_delete_all.triggered.connect(self.delete_all_entries)

        toolbar.addSeparator()
        toolbar.addAction(self.act_delete_all)

        menu = QMenu("📁 Файл", self)

        act_export_csv = QAction("Экспорт CSV", self)
        act_import_csv = QAction("Импорт CSV", self)

        act_export_csv.triggered.connect(self.export_csv)
        act_import_csv.triggered.connect(self.import_csv)

        menu.addAction(act_export_csv)
        menu.addAction(act_import_csv)

        toolbar.addSeparator()
        toolbar.addAction(menu.menuAction())

        self.addToolBar(toolbar)

        self.act_edit.setEnabled(False)
        self.act_delete.setEnabled(False)

    def update_toolbar_state(self):
        has = bool(self.entries_view.selectionModel().selectedRows())
        self.act_edit.setEnabled(has)
        self.act_delete.setEnabled(has)

    # ================= UI =================

    def build_ui(self):
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = self.build_sidebar()
        self.content = self.build_content()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.content, 1)

        self.setCentralWidget(root)

        self.category_list.itemSelectionChanged.connect(
            self.on_category_changed
        )

    # ================= Sidebar =================

    def build_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        title = QLabel("Категории")
        title.setObjectName("SidebarTitle")

        self.category_list = QListWidget()
        self.category_list.setFocusPolicy(Qt.NoFocus)
        self.category_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.category_list.customContextMenuRequested.connect(
            self.open_category_menu
        )

        self.load_categories()

        layout.addWidget(title)
        layout.addWidget(self.category_list)

        return sidebar

    def load_categories(self):
        self.category_list.blockSignals(True)
        self.category_list.clear()

        all_item = QListWidgetItem("Все")
        all_item.setData(Qt.UserRole, "all")
        self.category_list.addItem(all_item)

        for cat in self.vault.get("categories", []):
            name = cat.get("name", "").strip()
            if not name or name.lower() == "все":
                continue

            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, cat["id"])
            self.category_list.addItem(item)

        self.category_list.setCurrentRow(0)
        self.category_list.blockSignals(False)

    def on_category_changed(self):
        item = self.category_list.currentItem()
        if not item:
            return

        self.entries_model.set_category(item.data(Qt.UserRole))
        self.preview.clear()

    # ================= Categories =================

    def create_category(self):
        name, ok = QInputDialog.getText(
            self, "Новая категория", "Название категории:"
        )
        name = name.strip()
        if not ok or not name:
            return

        self.vault.setdefault("categories", []).append({
            "id": os.urandom(8).hex(),
            "name": name,
        })

        save_vault(self.vault, self.session.master_password, self.session.vault_path)
        self.load_categories()

    def rename_category(self, cid):
        cat = next(
            (c for c in self.vault["categories"] if c["id"] == cid),
            None
        )
        if not cat:
            return

        name, ok = QInputDialog.getText(
            self, "Переименовать", "Новое имя:", text=cat["name"]
        )
        if not ok or not name.strip():
            return

        cat["name"] = name.strip()
        save_vault(self.vault, self.session.master_password, self.session.vault_path)
        self.load_categories()

    def delete_category(self, cid):
        if any(e["category_id"] == cid for e in self.vault["entries"]):
            QMessageBox.warning(self, "Ошибка", "В категории есть записи")
            return

        self.vault["categories"] = [
            c for c in self.vault["categories"] if c["id"] != cid
        ]

        save_vault(self.vault, self.session.master_password, self.session.vault_path)
        self.load_categories()

    def open_category_menu(self, pos):
        item = self.category_list.itemAt(pos)
        menu = QMenu(self)

        act_add = QAction("➕ Создать категорию", self)
        act_add.triggered.connect(self.create_category)
        menu.addAction(act_add)

        if item:
            cid = item.data(Qt.UserRole)
            if cid != "all":
                act_rename = QAction("✏️ Переименовать", self)
                act_delete = QAction("🗑 Удалить", self)

                act_rename.triggered.connect(lambda: self.rename_category(cid))
                act_delete.triggered.connect(lambda: self.delete_category(cid))

                menu.addSeparator()
                menu.addAction(act_rename)
                menu.addAction(act_delete)

        menu.exec(self.category_list.mapToGlobal(pos))

    # ================= Content =================

    def build_content(self):
        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(16, 10, 16, 12)
        root.setSpacing(6)

        title = QLabel("Записи")
        title.setObjectName("Title")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по сервису, логину или URL…")

        self.entries_model = EntriesModel(self.vault)

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.entries_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)

        self.search_input.textChanged.connect(
            self.proxy_model.setFilterFixedString
        )

        self.entries_view = QTreeView()
        self.entries_view.setModel(self.proxy_model)
        self.entries_view.setRootIsDecorated(False)
        self.entries_view.setSelectionBehavior(QTreeView.SelectRows)
        self.entries_view.setSelectionMode(QTreeView.ExtendedSelection)
        self.entries_view.setEditTriggers(QTreeView.NoEditTriggers)

        self.entries_view.doubleClicked.connect(self.open_entry)
        self.entries_view.selectionModel().selectionChanged.connect(
            self.on_entry_selected
        )
        self.entries_view.selectionModel().selectionChanged.connect(
            self.update_toolbar_state
        )

        self.preview = PreviewPanel(self)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.entries_view)
        splitter.addWidget(self.preview)
        splitter.setSizes([760, 300])

        root.addWidget(title)
        root.addWidget(self.search_input)
        root.addWidget(splitter, 1)

        return content

    # ================= Delete logic =================

    def delete_selected_entries(self):
        indexes = self.entries_view.selectionModel().selectedRows()
        if not indexes:
            return

        confirm = QMessageBox.warning(
            self,
            "Удалить записи",
            f"Удалить выбранные записи ({len(indexes)})?\n\n"
            "Это действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        rows = sorted(
            (self.proxy_model.mapToSource(i).row() for i in indexes),
            reverse=True
        )

        for row in rows:
            entry = self.entries_model.get_entry(row)
            self.vault["entries"].remove(entry)

        save_vault(self.vault, self.session.master_password, self.session.vault_path)

        self.entries_model.beginResetModel()
        self.entries_model.endResetModel()
        self.preview.clear()

    def delete_all_entries(self):
        if not self.vault["entries"]:
            QMessageBox.information(self, "Нет записей", "Хранилище уже пустое")
            return

        confirm = QMessageBox.warning(
            self,
            "Удалить ВСЕ записи",
            "⚠️ Вы собираетесь удалить ВСЕ записи!\n\n"
            "Это действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        self.vault["entries"].clear()
        save_vault(self.vault, self.session.master_password, self.session.vault_path)

        self.entries_model.beginResetModel()
        self.entries_model.endResetModel()
        self.preview.clear()

    # ================= CSV =================

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт CSV", "", "CSV files (*.csv)"
        )
        if not path:
            return

        export_to_csv(self.vault, path)
        QMessageBox.information(self, "Экспорт", "Экспорт завершён")

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Импорт CSV", "", "CSV files (*.csv)"
        )
        if not path:
            return

        count = import_from_csv(self.vault, path)
        if count:
            save_vault(self.vault, self.session.master_password, self.session.vault_path)
            self.entries_model.beginResetModel()
            self.entries_model.endResetModel()

        QMessageBox.information(self, "Импорт", f"Импортировано записей: {count}")

    # ================= Entry =================

    def on_entry_selected(self):
        entry = self.get_selected_entry()
        if entry:
            self.preview.set_entry(entry)
        else:
            self.preview.clear()

    def get_selected_entry(self):
        indexes = self.entries_view.selectionModel().selectedRows()
        if not indexes:
            return None
        source = self.proxy_model.mapToSource(indexes[0])
        return self.entries_model.get_entry(source.row())

    def add_entry(self):
        entry = {
            "id": os.urandom(8).hex(),
            "service": "",
            "login": "",
            "password": "",
            "url": "",
            "note": "",
            "category_id": "all",
        }

        dialog = EntryDialog(self, entry, self.vault)
        if dialog.exec():
            entry.update(dialog.get_entry_data())
            self.vault["entries"].append(entry)
            save_vault(self.vault, self.session.master_password, self.session.vault_path)
            self.entries_model.beginResetModel()
            self.entries_model.endResetModel()

    def edit_entry(self):
        entry = self.get_selected_entry()
        if not entry:
            return

        dialog = EntryDialog(self, entry, self.vault)
        if dialog.exec():
            entry.update(dialog.get_entry_data())
            save_vault(self.vault, self.session.master_password, self.session.vault_path)
            self.entries_model.beginResetModel()
            self.entries_model.endResetModel()

    def open_entry(self, _):
        self.edit_entry()
