# app/ui/invoices/invoice_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QComboBox, QPushButton, QMessageBox, QTableView, QCompleter)
from PySide6.QtCore import Qt, QStringListModel
from .invoice_line_model import InvoiceLineTableModel
from .invoice_line_delegate import InvoiceLineDelegate
from app.services.date_service import gregorian_to_jalali, jalali_to_gregorian
from app.services.party_service import PartyService

class InvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice=None):
        super().__init__(parent)
        self.invoice = invoice
        self.party_service = PartyService()
        self.parties = []
        self.selected_party_id = None  # ✅ این متغیر کلیدی است

        self.setWindowTitle("فاکتور جدید" if not invoice else "ویرایش فاکتور")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        self.load_parties()

    def setup_ui(self):
        layout = QVBoxLayout()

        # نوع فاکتور
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("نوع فاکتور:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["خرید", "فروش", "مرجوعی خرید", "مرجوعی فروش"])
        type_map = {"purchase": 0, "sale": 1, "purchase_return": 2, "sale_return": 3}
        if self.invoice:
            self.type_combo.setCurrentIndex(type_map.get(self.invoice.invoice_type, 1))
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # طرف حساب — با جستجوی پیشرفته
        party_layout = QHBoxLayout()
        party_layout.addWidget(QLabel("طرف حساب:"))
        self.party_input = QLineEdit()
        self.party_input.setPlaceholderText("جستجوی طرف‌حساب بر اساس نام یا کد...")
        party_layout.addWidget(self.party_input)
        layout.addLayout(party_layout)

        # مدل برای completer
        self.completer_model = QStringListModel()
        self.completer = QCompleter()
        self.completer.setModel(self.completer_model)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.activated.connect(self.on_party_selected)  # ✅ اتصال سیگنال
        self.party_input.setCompleter(self.completer)

        # تاریخ — شمسی
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("تاریخ (شمسی):"))
        self.date_input = QLineEdit()
        if self.invoice:
            self.date_input.setText(self.invoice.date_jalali)
        else:
            from jdatetime import date as jdate
            today = jdate.today().strftime("%Y/%m/%d")
            self.date_input.setText(today)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # خطوط فاکتور — جدول
        self.table = QTableView()
        self.table.setItemDelegate(InvoiceLineDelegate(self))
        self.table_model = InvoiceLineTableModel([])
        self.table.setModel(self.table_model)
        layout.addWidget(self.table)

        # دکمه‌ها
        btn_layout = QHBoxLayout()
        add_line_btn = QPushButton("➕ افزودن خط فاکتور")
        add_line_btn.clicked.connect(self.add_invoice_line)
        btn_layout.addWidget(add_line_btn)

        remove_line_btn = QPushButton("🗑️ حذف خط انتخاب‌شده")
        remove_line_btn.clicked.connect(self.remove_invoice_line)  # ✅ اتصال سیگنال
        btn_layout.addWidget(remove_line_btn)

        save_btn = QPushButton("ذخیره")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.party_input.textChanged.connect(self.filter_parties)

    def load_parties(self):
        self.parties = self.party_service.get_all_parties()
        display_list = [f"{p.name} ({p.code})" for p in self.parties]
        self.completer_model.setStringList(display_list)

        if self.invoice:
            for i, party in enumerate(self.parties):
                if party.id == self.invoice.party_id:
                    self.party_input.setText(f"{party.name} ({party.code})")
                    self.selected_party_id = party.id  # ✅ تنظیم اولیه
                    break

    def filter_parties(self, text):
        if not text:
            display_list = [f"{p.name} ({p.code})" for p in self.parties]
            self.completer_model.setStringList(display_list)
            return
        filtered = [p for p in self.parties if text.lower() in p.name.lower() or text in p.code]
        display_list = [f"{p.name} ({p.code})" for p in filtered]
        self.completer_model.setStringList(display_list)

    def on_party_selected(self, selected_text):
        """✅ این متد کلیدی است — selected_party_id را تنظیم می‌کند"""
        for party in self.parties:
            if f"{party.name} ({party.code})" == selected_text:
                self.selected_party_id = party.id
                print(f"طرف‌حساب انتخاب شد: {party.name} (ID: {party.id})")  # برای دیباگ
                break

    def add_invoice_line(self):
        self.table_model.add_line()
        self.table.scrollToBottom()

    def remove_invoice_line(self):
        """✅ حذف خط انتخاب‌شده — اصلاح شده"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک خط را انتخاب کنید.")
            return
        row = selected[0].row()
        self.table_model.remove_line(row)  # ✅ فراخوانی صحیح

    def get_data(self):
        type_reverse = {0: "purchase", 1: "sale", 2: "purchase_return", 3: "sale_return"}

        # ✅ اعتبارسنجی انتخاب طرف‌حساب
        if self.selected_party_id is None:
            raise ValueError("لطفاً یک طرف‌حساب انتخاب کنید.")

        return {
            "invoice_type": type_reverse[self.type_combo.currentIndex()],
            "serial": "INV",
            "number": 1,
            "serial_full": "INV-1404-0001",
            "party_id": self.selected_party_id,  # ✅ از selected_party_id استفاده می‌شود
            "date_jalali": self.date_input.text().strip(),
            "created_by": 1,
        }

    def validate(self):
        if not self.date_input.text().strip():
            QMessageBox.warning(self, "خطا", "تاریخ الزامی است.")
            return False
        if self.selected_party_id is None:
            QMessageBox.warning(self, "خطا", "لطفاً یک طرف‌حساب انتخاب کنید.")
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()