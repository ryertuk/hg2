from PySide6.QtWidgets import QTableView, QVBoxLayout, QWidget, QHeaderView, QStyledItemDelegate
from PySide6.QtCore import Qt, QAbstractTableModel
from app.utils.rtl import set_rtl_stylesheet
from app.services.items_service import get_all_items, update_item

class ItemsModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ['ID', 'SKU', 'Name', 'Unit Type', 'Base Unit ID', 'Length', 'Width', 'Active', 'Barcode']

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._data[index.row()][index.column()]
        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            row = self._data[index.row()]
            update_item(row[0], {self.headers[index.column()].lower().replace(' ', '_'): value})
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

class ItemsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.table = QTableView()
        data = [(i.id, i.sku, i.name, i.unit_type, i.base_unit_id, i.length, i.width, i.active, i.barcode) for i in get_all_items()]
        model = ItemsModel(data)
        self.table.setModel(model)
        self.table.setItemDelegate(QStyledItemDelegate())
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)
        set_rtl_stylesheet(self)