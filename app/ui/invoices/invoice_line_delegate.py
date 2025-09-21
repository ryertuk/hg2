# app/ui/invoices/invoice_line_delegate.py
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox, QDoubleSpinBox, QLineEdit, QCompleter
from PySide6.QtCore import Qt, QStringListModel

class InvoiceLineDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_service = None
        self.unit_service = None
        self.items = []
        self.units = []
        self._load_data()

    def _load_data(self):
        from app.services.item_service import ItemService
        from app.services.unit_service import UnitService
        self.item_service = ItemService()
        self.unit_service = UnitService()
        self.items = self.item_service.get_all_items()
        self.units = self.unit_service.get_all_units()

    def createEditor(self, parent, option, index):
        col = index.column()
        if col == 0:  # item_id — با جستجو
            editor = QLineEdit(parent)
            editor.setPlaceholderText("جستجوی کالا...")
            display_list = [f"{item.name} ({item.sku})" for item in self.items]
            model = QStringListModel(display_list)
            completer = QCompleter()
            completer.setModel(model)
            completer.setFilterMode(Qt.MatchContains)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            editor.setCompleter(completer)
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
            editor.setGroupSeparatorShown(True)
            return editor
        elif col == 5:  # discount
            editor = QDoubleSpinBox(parent)
            editor.setDecimals(0)
            editor.setMaximum(999999999999)
            editor.setGroupSeparatorShown(True)
            return editor
        elif col == 6:  # tax
            editor = QDoubleSpinBox(parent)
            editor.setDecimals(0)
            editor.setMaximum(999999999999)
            editor.setGroupSeparatorShown(True)
            return editor
        elif col == 7:  # notes
            editor = QLineEdit(parent)
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        col = index.column()
        value = index.model().data(index, Qt.EditRole)
        
        if isinstance(editor, QLineEdit):
            if col == 0:  # item_id
                if value:
                    item = next((i for i in self.items if i.id == value), None)
                    if item:
                        editor.setText(f"{item.name} ({item.sku})")
                    else:
                        editor.setText("")
                else:
                    editor.setText("")
            elif col == 7:  # notes
                editor.setText(str(value) if value else "")
        elif isinstance(editor, QComboBox):
            if col == 2:  # unit_id
                if value:
                    unit = next((u for u in self.units if u.id == value), None)
                    if unit:
                        unit_names = [u.name for u in self.units]
                        if unit.name in unit_names:
                            editor.setCurrentIndex(unit_names.index(unit.name))
        elif isinstance(editor, QDoubleSpinBox):
            editor.setValue(float(value) if value else 0.0)

    def setModelData(self, editor, model, index):
        col = index.column()
        if isinstance(editor, QLineEdit):
            if col == 0:  # item_id
                text = editor.text()
                model.setData(index, text, Qt.EditRole)  # ✅ ارسال متن — مدل خودش item_id را استخراج می‌کند
            elif col == 7:  # notes
                model.setData(index, editor.text(), Qt.EditRole)
        elif isinstance(editor, QComboBox):
            if col == 2:  # unit_id
                unit_name = editor.currentText()
                unit = next((u for u in self.units if u.name == unit_name), None)
                if unit:
                    model.setData(index, unit.id, Qt.EditRole)
        elif isinstance(editor, QDoubleSpinBox):
            model.setData(index, editor.value(), Qt.EditRole)