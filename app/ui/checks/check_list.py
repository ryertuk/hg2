# app/ui/checks/check_list.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableView, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from app.services.check_service import CheckService

class CheckTableModel(QAbstractTableModel):
    def __init__(self, checks):
        super().__init__()
        self.checks = checks
        self.headers = ["شماره چک", "بانک", "مبلغ", "تاریخ صدور", "سررسید", "پرداخت‌کننده", "دریافت‌کننده", "وضعیت", "جهت"]
        
        # ✅ بارگذاری یک‌باره تمام طرف‌حساب‌ها — برای جلوگیری از فراخوانی مکرر دیتابیس
        from app.services.party_service import PartyService
        self.party_service = PartyService()
        self.parties = {p.id: p for p in self.party_service.get_all_parties()}  # کش به صورت dict

    def rowCount(self, parent=QModelIndex()):
        """تعداد ردیف‌های داده را برمی‌گرداند"""
        return len(self.checks)

    def columnCount(self, parent=QModelIndex()):
        """تعداد ستون‌ها را برمی‌گرداند"""
        return len(self.headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """هدرهای ستون‌ها را برمی‌گرداند"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        check = self.checks[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return check.check_number
            elif col == 1: return check.bank_name
            elif col == 2: return f"{check.amount:,.0f}"
            elif col == 3:  # تاریخ صدور — شمسی
                return check.date_jalali if hasattr(check, 'date_jalali') else self.gregorian_to_jalali(check.issue_date)
            elif col == 4:  # سررسید — شمسی
                return self.gregorian_to_jalali(check.due_date)
            elif col == 5:  # پرداخت‌کننده
                if check.payer_party_id:
                    from app.services.party_service import PartyService
                    party = PartyService().get_party_by_id(check.payer_party_id)
                    return party.name if party else "-"
                return "-"
            elif col == 6:  # دریافت‌کننده
                if check.payee_party_id:
                    from app.services.party_service import PartyService
                    party = PartyService().get_party_by_id(check.payee_party_id)
                    return party.name if party else "-"
                return "-"
            elif col == 7: return check.status
            elif col == 8: return "دریافتی" if check.direction == "received" else "پرداختی"
        return None

    def gregorian_to_jalali(self, gregorian_date):
        """تبدیل تاریخ میلادی به شمسی — برای نمایش در جدول"""
        if not gregorian_date:
            return ""
        from jdatetime import date as jdate
        j = jdate.fromgregorian(date=gregorian_date)
        return j.strftime("%Y/%m/%d")

class CheckListView(QWidget):
    def __init__(self):
        super().__init__()
        self.service = CheckService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("💳 لیست چک‌ها")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

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
        self.add_btn = QPushButton("➕ ایجاد چک جدید")
        self.add_btn.clicked.connect(self.add_check)
        self.edit_btn = QPushButton("✏️ ویرایش")
        self.edit_btn.clicked.connect(self.edit_check)
        self.delete_btn = QPushButton("🗑️ حذف")
        self.delete_btn.clicked.connect(self.delete_check)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        self.checks = self.service.get_all_checks()
        self.model = CheckTableModel(self.checks)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

    def filter_data(self):
        text = self.search_input.text().lower()
        filtered = [chk for chk in self.checks if text in chk.check_number.lower() or text in chk.bank_name.lower()]
        self.model.checks = filtered
        self.model.layoutChanged.emit()

    def add_check(self):
        from app.ui.checks.check_dialog import CheckDialog
        dialog = CheckDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.service.create_check(data)
                QMessageBox.information(self, "موفق", "چک با موفقیت ایجاد شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ایجاد: {str(e)}")

    def edit_check(self):
        from app.ui.checks.check_dialog import CheckDialog
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک چک را انتخاب کنید.")
            return
        row = selected[0].row()
        check = self.model.checks[row]
        dialog = CheckDialog(self, check)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.service.update_check(check.id, data)
                QMessageBox.information(self, "موفق", "چک با موفقیت ویرایش شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ویرایش: {str(e)}")

    def delete_check(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک چک را انتخاب کنید.")
            return
        row = selected[0].row()
        check = self.model.checks[row]
        if QMessageBox.question(self, "تأیید حذف", f"آیا از حذف چک «{check.check_number}» اطمینان دارید؟", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.service.delete_check(check.id)
                QMessageBox.information(self, "موفق", "چک حذف شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")