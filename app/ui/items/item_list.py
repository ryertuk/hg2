# app/ui/items/item_list.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableView, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from app.services.item_service import ItemService
from app.ui.items.item_dialog import ItemDialog

class ItemTableModel(QAbstractTableModel):
    def __init__(self, items):
        super().__init__()
        self.items = items
        self.headers = ["کد کالا", "نام", "نوع", "واحد", "فعال"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        item = self.items[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return item.sku
            elif col == 1: return item.name
            elif col == 2: return "تعدادی" if item.unit_type == "count" else "اندازه‌ای"
            elif col == 3:
                if hasattr(item, 'unit') and item.unit:
                    return item.unit.name
                else:
                    # بارگذاری واحد از دیتابیس
                    from app.services.unit_service import UnitService
                    unit_service = UnitService()
                    unit = unit_service.get_unit_by_id(item.base_unit_id)
                    if unit:
                        item.unit = unit  # ذخیره برای نمایش بعدی
                        return unit.name
                    return "نامشخص"
            elif col == 4: return "✅" if item.active else "❌"
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class ItemListView(QWidget):
    def __init__(self):
        super().__init__()
        self.service = ItemService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("جستجو:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_data)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ افزودن")
        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn = QPushButton("✏️ ویرایش")
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn = QPushButton("🗑️ حذف")
        self.delete_btn.clicked.connect(self.delete_item)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        self.items = self.service.get_all_items()
        self.model = ItemTableModel(self.items)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

    def filter_data(self):
        text = self.search_input.text().lower()
        filtered = [i for i in self.items if
                    text in i.sku.lower() or
                    text in i.name.lower() or
                    (i.barcode and text in i.barcode.lower())]
        self.model.items = filtered
        self.model.layoutChanged.emit()

    def add_item(self):
        dialog = ItemDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.service.create_item(data)
                QMessageBox.information(self, "موفق", "کالا با موفقیت افزوده شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در افزودن: {str(e)}")

    def edit_item(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک رکورد را انتخاب کنید.")
            return
        row = selected[0].row()
        item = self.model.items[row]
        dialog = ItemDialog(self, item)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.service.update_item(item.id, data)
                QMessageBox.information(self, "موفق", "کالا با موفقیت ویرایش شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ویرایش: {str(e)}")

    def delete_item(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک رکورد را انتخاب کنید.")
            return
        row = selected[0].row()
        item = self.model.items[row]
        if QMessageBox.question(self, "تأیید حذف",
                                f"آیا از حذف کالا «{item.name}» اطمینان دارید؟",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.service.delete_item(item.id)
                QMessageBox.information(self, "موفق", "کالا حذف شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")