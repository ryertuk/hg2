# app/ui/invoices/invoice_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QComboBox, QPushButton, QMessageBox, QTableView, QCompleter)
from PySide6.QtCore import Qt, QStringListModel
from app.services.date_service import gregorian_to_jalali, jalali_to_gregorian
from app.services.party_service import PartyService

class InvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice=None):
        super().__init__(parent)
        self.invoice = invoice
        self.party_service = PartyService()
        self.parties = []  # لیست کامل طرف‌حساب‌ها
        self.selected_party_id = None  # ID طرف‌حساب انتخاب‌شده

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
        self.completer.activated.connect(self.on_party_selected)
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
        layout.addWidget(self.table)

        # دکمه‌ها
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("ذخیره")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # اتصال سیگنال تغییر متن برای فیلتر
        self.party_input.textChanged.connect(self.filter_parties)

    def load_parties(self):
        """بارگذاری لیست کامل طرف‌حساب‌ها"""
        self.parties = self.party_service.get_all_parties()
        # ایجاد لیست نمایشی
        display_list = [f"{p.name} ({p.code})" for p in self.parties]
        self.completer_model.setStringList(display_list)

        # اگر فاکتور ویرایشی است — مقدار قبلی را تنظیم کن
        if self.invoice:
            for i, party in enumerate(self.parties):
                if party.id == self.invoice.party_id:
                    self.party_input.setText(f"{party.name} ({party.code})")
                    self.selected_party_id = party.id
                    break

    def filter_parties(self, text):
        """فیلتر کردن لیست بر اساس متن وارد شده"""
        if not text:
            display_list = [f"{p.name} ({p.code})" for p in self.parties]
            self.completer_model.setStringList(display_list)
            return

        filtered = [
            p for p in self.parties
            if text.lower() in p.name.lower() or text in p.code
        ]
        display_list = [f"{p.name} ({p.code})" for p in filtered]
        self.completer_model.setStringList(display_list)

    def on_party_selected(self, selected_text):
        """هنگام انتخاب یک مورد از completer"""
        # استخراج ID از متن انتخاب‌شده
        for party in self.parties:
            if f"{party.name} ({party.code})" == selected_text:
                self.selected_party_id = party.id
                break

    def get_data(self):
        type_reverse = {0: "purchase", 1: "sale", 2: "purchase_return", 3: "sale_return"}

        if self.selected_party_id is None:
            raise ValueError("لطفاً یک طرف‌حساب انتخاب کنید.")

        return {
            "invoice_type": type_reverse[self.type_combo.currentIndex()],
            "serial": "INV",
            "number": 1,
            "serial_full": "INV-1404-0001",
            "party_id": self.selected_party_id,
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