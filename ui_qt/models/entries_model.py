from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QIcon

from utils.icons import get_favicon


class EntriesModel(QAbstractTableModel):
    HEADERS = ["Service", "Login", "URL"]

    def __init__(self, vault):
        super().__init__()
        self.vault = vault
        self.category_id = "all"

    def set_category(self, cid):
        self.category_id = cid
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._entries())

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]
        return None

    def data(self, index, role):
        if not index.isValid():
            return None

        entry = self._entries()[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return entry.get("service", "")
            if col == 1:
                return entry.get("login", "")
            if col == 2:
                return entry.get("url", "")

        if role == Qt.DecorationRole and col == 0:
            icon = get_favicon(entry.get("url", ""))
            if icon:
                return icon

        return None

    def get_entry(self, row: int) -> dict:
        return self._entries()[row]

    def _entries(self):
        if self.category_id == "all":
            return self.vault["entries"]
        return [
            e for e in self.vault["entries"]
            if e.get("category_id") == self.category_id
        ]
