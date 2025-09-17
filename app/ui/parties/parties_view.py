# parties_view.py
from PySide6.QtWidgets import QTableView, QVBoxLayout, QWidget, QHeaderView, QStyledItemDelegate
from PySide6.QtCore import Qt, QAbstractTableModel
from app.utils.rtl import set_rtl_stylesheet
from app.services.parties_service import get_all_parties, update_party

class PartiesModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ['ID', 'Code', 'Name', 'Type', 'Credit Limit', 'Active']

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._data[index.row()][index.column()]
        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            row = self._data[index.row()]
            # بروزرسانی DB
            update_party(row[0], {self.headers[index.column()].lower().replace(' ', '_'): value})
            self._data[index.row()][index.column()] = value
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self.headers)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]

class PartiesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.table = QTableView()
        data = [(p.id, p.code, p.name, p.party_type, p.credit_limit, p.is_active) for p in get_all_parties()]
        model = PartiesModel(data)
        self.table.setModel(model)
        self.table.setItemDelegate(QStyledItemDelegate())  # برای inline edit
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)
        set_rtl_stylesheet(self)  # RTL support