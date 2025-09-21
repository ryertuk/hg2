# app/ui/checks/check_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QComboBox, QDateEdit, QDoubleSpinBox, QPushButton,
                               QMessageBox, QCompleter)
from PySide6.QtCore import Qt, QStringListModel
from app.services.party_service import PartyService
from app.services.bank_account_service import BankAccountService
from app.services.date_service import jalali_to_gregorian
import datetime

class CheckDialog(QDialog):
    def __init__(self, parent=None, check=None):
        super().__init__(parent)
        self.check = check
        self.party_service = PartyService()
        self.bank_service = BankAccountService()
        self.parties = []
        self.bank_accounts = []
        self.selected_payer_id = None
        self.selected_payee_id = None
        self.selected_bank_account_id = None

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

        # حساب بانکی — با QComboBox
        bank_account_layout = QHBoxLayout()
        bank_account_layout.addWidget(QLabel("حساب بانکی:"))
        self.bank_account_combo = QComboBox()
        bank_account_layout.addWidget(self.bank_account_combo)
        layout.addLayout(bank_account_layout)

        # بانک — فقط نمایش (readonly)
        bank_layout = QHBoxLayout()
        bank_layout.addWidget(QLabel("نام بانک:"))
        self.bank_display = QLineEdit()
        self.bank_display.setReadOnly(True)
        bank_layout.addWidget(self.bank_display)
        layout.addLayout(bank_layout)

        # شماره حساب — فقط نمایش (readonly)
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("شماره حساب:"))
        self.account_display = QLineEdit()
        self.account_display.setReadOnly(True)
        account_layout.addWidget(self.account_display)
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

        # تاریخ صدور و سررسید — شمسی
        dates_layout = QHBoxLayout()
        dates_layout.addWidget(QLabel("تاریخ صدور (شمسی):"))
        self.issue_date_input = QLineEdit()
        if self.check:
            from jdatetime import date as jdate
            j_issue = jdate.fromgregorian(date=self.check.issue_date)
            self.issue_date_input.setText(j_issue.strftime("%Y/%m/%d"))
        else:
            from jdatetime import date as jdate
            today = jdate.today().strftime("%Y/%m/%d")
            self.issue_date_input.setText(today)
        dates_layout.addWidget(self.issue_date_input)

        dates_layout.addWidget(QLabel("سررسید (شمسی):"))
        self.due_date_input = QLineEdit()
        if self.check:
            j_due = jdate.fromgregorian(date=self.check.due_date)
            self.due_date_input.setText(j_due.strftime("%Y/%m/%d"))
        else:
            today = jdate.today().strftime("%Y/%m/%d")
            self.due_date_input.setText(today)
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
        self.bank_account_combo.currentIndexChanged.connect(self.on_bank_account_changed)

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

    def load_bank_accounts(self):
        self.bank_accounts = self.bank_service.get_all_bank_accounts()
        if not self.bank_accounts:
            # ایجاد حساب بانکی پیش‌فرض — فقط برای محیط توسعه
            default_account = self.bank_service.create_bank_account({
                "name": "حساب پیش‌فرض",
                "bank_name": "بانک ملی",
                "account_number": "1234567890",
                "ledger_account_id": 1,
                "currency": "IRR"
            })
            self.bank_accounts = [default_account]

        self.bank_account_combo.clear()
        for acc in self.bank_accounts:
            self.bank_account_combo.addItem(f"{acc.bank_name} - {acc.account_number}", acc.id)

        if self.check:
            for i, acc in enumerate(self.bank_accounts):
                if acc.id == self.check.bank_account_id:
                    self.bank_account_combo.setCurrentIndex(i)
                    self.on_bank_account_changed(i)
                    break
        else:
            if self.bank_accounts:
                self.on_bank_account_changed(0)

    def on_bank_account_changed(self, index):
        if index >= 0 and index < len(self.bank_accounts):
            acc = self.bank_accounts[index]
            self.bank_display.setText(acc.bank_name)
            self.account_display.setText(acc.account_number)
            self.selected_bank_account_id = acc.id

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

        # تبدیل تاریخ شمسی به میلادی
        issue_date = jalali_to_gregorian(self.issue_date_input.text().strip())
        due_date = jalali_to_gregorian(self.due_date_input.text().strip())

        return {
            "check_number": self.check_num_input.text().strip(),
            "bank_name": self.bank_display.text().strip(),
            "account_number": self.account_display.text().strip(),
            "direction": direction,
            "amount": int(self.amount_input.value()),
            "issue_date": issue_date,
            "due_date": due_date,
            "payer_party_id": self.selected_payer_id,
            "payee_party_id": self.selected_payee_id,
            "created_by": 1,  # در عمل: از session کاربر جاری
            "bank_account_id": self.selected_bank_account_id,
        }

    def validate(self):
        if not self.check_num_input.text().strip():
            QMessageBox.warning(self, "خطا", "شماره چک الزامی است.")
            return False
        if not self.issue_date_input.text().strip():
            QMessageBox.warning(self, "خطا", "تاریخ صدور الزامی است.")
            return False
        if not self.due_date_input.text().strip():
            QMessageBox.warning(self, "خطا", "تاریخ سررسید الزامی است.")
            return False
        if not self.selected_bank_account_id:
            QMessageBox.warning(self, "خطا", "لطفاً یک حساب بانکی انتخاب کنید.")
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()