# app/ui/invoices/invoice_line_delegate.py
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox, QDoubleSpinBox, QLineEdit
from PySide6.QtCore import Qt
from app.services.item_service import ItemService
from app.services.unit_service import UnitService

class InvoiceLineDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_service = ItemService()
        self.unit_service = UnitService()
        self.items = self.item_service.get_all_items()
        self.units = self.unit_service.get_all_units()

    def createEditor(self, parent, option, index):
        col = index.column()
        if col == 0:  # item_id
            editor = QComboBox(parent)
            editor.addItems([f"{item.name} ({item.sku})" for item in self.items])
            return editor
        elif col == 1:  # qty
            editor = QDoubleSpinBox(parent)
            editor.setDecimals(4)
            editor.setMaximum(999999.9999)
            return editor
        elif col == 2:  # unit_id
            editor = QComboBox(parent)
            editor.addItems([unit.name for unit in self.units])
            return editor
        elif col == 3:  # unit_price
            editor = QDoubleSpinBox(parent)
            editor.setDecimals(0)
            editor.setMaximum(999999999999)
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        col = index.column()
        value = index.model().data(index, Qt.EditRole)
        if isinstance(editor, QComboBox):
            if col == 0:  # item_id
                item_id = int(value) if value else 1
                item_map = {item.id: i for i, item in enumerate(self.items)}
                editor.setCurrentIndex(item_map.get(item_id, 0))
            elif col == 2:  # unit_id
                unit_id = int(value) if value else 1
                unit_map = {unit.id: i for i, unit in enumerate(self.units)}
                editor.setCurrentIndex(unit_map.get(unit_id, 0))
        elif isinstance(editor, QDoubleSpinBox):
            editor.setValue(float(value) if value else 0.0)

    def setModelData(self, editor, model, index):
        col = index.column()
        if isinstance(editor, QComboBox):
            if col == 0:  # item_id
                item_id = self.items[editor.currentIndex()].id
                model.setData(index, item_id, Qt.EditRole)
            elif col == 2:  # unit_id
                unit_id = self.units[editor.currentIndex()].id
                model.setData(index, unit_id, Qt.EditRole)
        elif isinstance(editor, QDoubleSpinBox):
            model.setData(index, editor.value(), Qt.EditRole)