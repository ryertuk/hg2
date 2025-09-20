# app/ui/checks/check_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QComboBox, QDateEdit, QDoubleSpinBox, QPushButton, 
                               QMessageBox, QCompleter)
from PySide6.QtCore import Qt, QStringListModel
from app.services.party_service import PartyService
from app.services.bank_account_service import BankAccountService  # فرض — در ادامه ایجاد می‌شود

class CheckDialog(QDialog):
    def __init__(self, parent=None, check=None):
        super().__init__(parent)
        self.check = check
        self.party_service = PartyService()
        self.bank_service = BankAccountService()
        self.parties = []
        self.selected_payer_id = None
        self.selected_payee_id = None

        self.setWindowTitle("چک جدید" if not check else "ویرایش چک")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        self.load_parties()
        self.load_bank_accounts()

    def setup_ui(self):
        layout = QVBoxLayout()

        # جهت چک
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(QLabel("جهت چک:"))
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["دریافتی", "پرداختی"])
        if self.check:
            self.direction_combo.setCurrentIndex(0 if self.check.direction == "received" else 1)
        direction_layout.addWidget(self.direction_combo)
        layout.addLayout(direction_layout)

        # شماره چک
        check_num_layout = QHBoxLayout()
        check_num_layout.addWidget(QLabel("شماره چک:"))
        self.check_num_input = QLineEdit()
        if self.check:
            self.check_num_input.setText(self.check.check_number)
        check_num_layout.addWidget(self.check_num_input)
        layout.addLayout(check_num_layout)

        # بانک
        bank_layout = QHBoxLayout()
        bank_layout.addWidget(QLabel("نام بانک:"))
        self.bank_input = QLineEdit()
        if self.check:
            self.bank_input.setText(self.check.bank_name)
        bank_layout.addWidget(self.bank_input)
        layout.addLayout(bank_layout)

        # شماره حساب
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("شماره حساب:"))
        self.account_input = QLineEdit()
        if self.check:
            self.account_input.setText(self.check.account_number)
        account_layout.addWidget(self.account_input)
        layout.addLayout(account_layout)

        # مبلغ
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("مبلغ (ریال):"))
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(999999999999)
        self.amount_input.setDecimals(0)
        if self.check:
            self.amount_input.setValue(float(self.check.amount))
        amount_layout.addWidget(self.amount_input)
        layout.addLayout(amount_layout)

        # تاریخ صدور و سررسید
        dates_layout = QHBoxLayout()
        dates_layout.addWidget(QLabel("تاریخ صدور (شمسی):"))
        self.issue_date_input = QLineEdit()
        dates_layout.addWidget(self.issue_date_input)
        dates_layout.addWidget(QLabel("سررسید (شمسی):"))
        self.due_date_input = QLineEdit()
        dates_layout.addWidget(self.due_date_input)
        layout.addLayout(dates_layout)

        # طرف پرداخت‌کننده (payer)
        payer_layout = QHBoxLayout()
        payer_layout.addWidget(QLabel("پرداخت‌کننده:"))
        self.payer_input = QLineEdit()
        self.payer_input.setPlaceholderText("جستجو...")
        payer_layout.addWidget(self.payer_input)
        layout.addLayout(payer_layout)

        # طرف دریافت‌کننده (payee)
        payee_layout = QHBoxLayout()
        payee_layout.addWidget(QLabel("دریافت‌کننده:"))
        self.payee_input = QLineEdit()
        self.payee_input.setPlaceholderText("جستجو...")
        payee_layout.addWidget(self.payee_input)
        layout.addLayout(payee_layout)

        # completer برای payer
        self.payer_completer_model = QStringListModel()
        self.payer_completer = QCompleter()
        self.payer_completer.setModel(self.payer_completer_model)
        self.payer_completer.setFilterMode(Qt.MatchContains)
        self.payer_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.payer_completer.activated.connect(self.on_payer_selected)
        self.payer_input.setCompleter(self.payer_completer)

        # completer برای payee
        self.payee_completer_model = QStringListModel()
        self.payee_completer = QCompleter()
        self.payee_completer.setModel(self.payee_completer_model)
        self.payee_completer.setFilterMode(Qt.MatchContains)
        self.payee_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.payee_completer.activated.connect(self.on_payee_selected)
        self.payee_input.setCompleter(self.payee_completer)

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

        # اتصال سیگنال‌ها
        self.payer_input.textChanged.connect(self.filter_parties_payer)
        self.payee_input.textChanged.connect(self.filter_parties_payee)

    def load_parties(self):
        self.parties = self.party_service.get_all_parties()
        display_list = [f"{p.name} ({p.code})" for p in self.parties]
        self.payer_completer_model.setStringList(display_list)
        self.payee_completer_model.setStringList(display_list)

        if self.check:
            if self.check.payer_party_id:
                for p in self.parties:
                    if p.id == self.check.payer_party_id:
                        self.payer_input.setText(f"{p.name} ({p.code})")
                        self.selected_payer_id = p.id
                        break
            if self.check.payee_party_id:
                for p in self.parties:
                    if p.id == self.check.payee_party_id:
                        self.payee_input.setText(f"{p.name} ({p.code})")
                        self.selected_payee_id = p.id
                        break

    def filter_parties_payer(self, text):
        if not text:
            display_list = [f"{p.name} ({p.code})" for p in self.parties]
            self.payer_completer_model.setStringList(display_list)
            return
        filtered = [p for p in self.parties if text.lower() in p.name.lower() or text in p.code]
        display_list = [f"{p.name} ({p.code})" for p in filtered]
        self.payer_completer_model.setStringList(display_list)

    def filter_parties_payee(self, text):
        if not text:
            display_list = [f"{p.name} ({p.code})" for p in self.parties]
            self.payee_completer_model.setStringList(display_list)
            return
        filtered = [p for p in self.parties if text.lower() in p.name.lower() or text in p.code]
        display_list = [f"{p.name} ({p.code})" for p in filtered]
        self.payee_completer_model.setStringList(display_list)

    def on_payer_selected(self, selected_text):
        for party in self.parties:
            if f"{party.name} ({party.code})" == selected_text:
                self.selected_payer_id = party.id
                break

    def on_payee_selected(self, selected_text):
        for party in self.parties:
            if f"{party.name} ({party.code})" == selected_text:
                self.selected_payee_id = party.id
                break

    def get_data(self):
        direction = "received" if self.direction_combo.currentIndex() == 0 else "issued"
        return {
            "check_number": self.check_num_input.text().strip(),
            "bank_name": self.bank_input.text().strip(),
            "account_number": self.account_input.text().strip(),
            "direction": direction,
            "amount": int(self.amount_input.value()),
            "issue_date": ... , # تبدیل شمسی به میلادی — در عمل
            "due_date": ... ,   # تبدیل شمسی به میلادی — در عمل
            "payer_party_id": self.selected_payer_id,
            "payee_party_id": self.selected_payee_id,
            "created_by": 1,
            "bank_account_id": 1,  # در عمل: از کاربر انتخاب می‌شود
        }

    def validate(self):
        if not self.check_num_input.text().strip():
            QMessageBox.warning(self, "خطا", "شماره چک الزامی است.")
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()