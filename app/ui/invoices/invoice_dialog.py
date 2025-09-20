# app/ui/invoices/invoice_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QComboBox, QDateEdit, QDoubleSpinBox, QPushButton, QMessageBox, QTableView)
from PySide6.QtCore import Qt, QDate
from app.services.date_service import gregorian_to_jalali, jalali_to_gregorian
from app.services.party_service import PartyService
from app.services.item_service import ItemService
from app.services.unit_service import UnitService

class InvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice=None):
        super().__init__(parent)
        self.invoice = invoice
        self.party_service = PartyService()
        self.item_service = ItemService()
        self.unit_service = UnitService()
        self.setWindowTitle("فاکتور جدید" if not invoice else "ویرایش فاکتور")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()

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

        # طرف حساب
        party_layout = QHBoxLayout()
        party_layout.addWidget(QLabel("طرف حساب:"))
        self.party_combo = QComboBox()
        parties = self.party_service.get_all_parties()
        self.party_combo.addItems([f"{p.name} ({p.code})" for p in parties])
        if self.invoice:
            party_map = {p.id: i for i, p in enumerate(parties)}
            self.party_combo.setCurrentIndex(party_map.get(self.invoice.party_id, 0))
        party_layout.addWidget(self.party_combo)
        layout.addLayout(party_layout)

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
        # TODO: در مرحله بعد — افزودن delegate برای ویرایش inline
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

    def get_data(self):
        type_reverse = {0: "purchase", 1: "sale", 2: "purchase_return", 3: "sale_return"}
        parties = self.party_service.get_all_parties()
        party_id = parties[self.party_combo.currentIndex()].id

        return {
            "invoice_type": type_reverse[self.type_combo.currentIndex()],
            "serial": "INV",
            "number": 1,  # در عمل: شماره سریالی خودکار
            "serial_full": "INV-1404-0001",  # در عمل: خودکار
            "party_id": party_id,
            "date_jalali": self.date_input.text().strip(),
            "created_by": 1,  # در عمل: از session کاربر جاری
        }

    def validate(self):
        if not self.date_input.text().strip():
            QMessageBox.warning(self, "خطا", "تاریخ الزامی است.")
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()