# app/ui/parties/party_list.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableView, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from app.services.party_service import PartyService
from app.ui.parties.party_dialog import PartyDialog

class PartyTableModel(QAbstractTableModel):
    def __init__(self, parties):
        super().__init__()
        self.parties = parties
        self.headers = ["کد", "نام", "نوع", "تلفن", "اعتبار", "فعال"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.parties)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        party = self.parties[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return party.code
            elif col == 1: return party.name
            elif col == 2:
                type_map = {"customer": "مشتری", "supplier": "تأمین‌کننده", "both": "هر دو"}
                return type_map.get(party.party_type, party.party_type)
            elif col == 3: return party.phone or "-"
            elif col == 4:
                return f"{party.credit_limit:,.2f}" if party.credit_limit else "-"
            elif col == 5: return "✅" if party.is_active else "❌"
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class PartyListView(QWidget):
    def __init__(self):
        super().__init__()
        self.service = PartyService()
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
        self.add_btn.clicked.connect(self.add_party)
        self.edit_btn = QPushButton("✏️ ویرایش")
        self.edit_btn.clicked.connect(self.edit_party)
        self.delete_btn = QPushButton("🗑️ حذف")
        self.delete_btn.clicked.connect(self.delete_party)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        self.parties = self.service.get_all_parties()
        self.model = PartyTableModel(self.parties)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

    def filter_data(self):
        text = self.search_input.text().lower()
        filtered = [p for p in self.parties if
                    text in p.code.lower() or
                    text in p.name.lower() or
                    (p.phone and text in p.phone.lower())]
        self.model.parties = filtered
        self.model.layoutChanged.emit()

    def add_party(self):
        dialog = PartyDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.service.create_party(data)
                QMessageBox.information(self, "موفق", "طرف‌حساب با موفقیت افزوده شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در افزودن: {str(e)}")

    def edit_party(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک رکورد را انتخاب کنید.")
            return
        row = selected[0].row()
        party = self.model.parties[row]
        dialog = PartyDialog(self, party)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.service.update_party(party.id, data)
                QMessageBox.information(self, "موفق", "طرف‌حساب با موفقیت ویرایش شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ویرایش: {str(e)}")

    def delete_party(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک رکورد را انتخاب کنید.")
            return
        row = selected[0].row()
        party = self.model.parties[row]
        if QMessageBox.question(self, "تأیید حذف",
                                f"آیا از حذف طرف‌حساب «{party.name}» اطمینان دارید؟",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.service.delete_party(party.id)
                QMessageBox.information(self, "موفق", "طرف‌حساب حذف شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")