# app/ui/units/unit_list.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableView, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from app.services.unit_service import UnitService
from app.ui.units.unit_dialog import UnitDialog

class UnitTableModel(QAbstractTableModel):
    def __init__(self, units):
        super().__init__()
        self.units = units
        self.headers = ["کد", "نام", "ضریب تبدیل"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.units)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        unit = self.units[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return unit.code
            elif col == 1: return unit.name
            elif col == 2: return f"{unit.factor_to_base:.4f}"
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class UnitListView(QWidget):
    def __init__(self):
        super().__init__()
        self.service = UnitService()
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
        self.add_btn.clicked.connect(self.add_unit)
        self.edit_btn = QPushButton("✏️ ویرایش")
        self.edit_btn.clicked.connect(self.edit_unit)
        self.delete_btn = QPushButton("🗑️ حذف")
        self.delete_btn.clicked.connect(self.delete_unit)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        self.units = self.service.get_all_units()
        self.model = UnitTableModel(self.units)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

    def filter_data(self):
        text = self.search_input.text().lower()
        filtered = [u for u in self.units if text in u.code.lower() or text in u.name.lower()]
        self.model.units = filtered
        self.model.layoutChanged.emit()

    def add_unit(self):
        dialog = UnitDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.service.create_unit(data)
                QMessageBox.information(self, "موفق", "واحد با موفقیت افزوده شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در افزودن: {str(e)}")

    def edit_unit(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک رکورد را انتخاب کنید.")
            return
        row = selected[0].row()
        unit = self.model.units[row]
        dialog = UnitDialog(self, unit)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.service.update_unit(unit.id, data)
                QMessageBox.information(self, "موفق", "واحد با موفقیت ویرایش شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ویرایش: {str(e)}")

    def delete_unit(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک رکورد را انتخاب کنید.")
            return
        row = selected[0].row()
        unit = self.model.units[row]
        if QMessageBox.question(self, "تأیید حذف",
                                f"آیا از حذف واحد «{unit.name}» اطمینان دارید؟",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.service.delete_unit(unit.id)
                QMessageBox.information(self, "موفق", "واحد حذف شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")