# app/ui/parties/party_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QComboBox, QDoubleSpinBox, QCheckBox, QPushButton, QMessageBox)
from PySide6.QtCore import Qt

class PartyDialog(QDialog):
    def __init__(self, parent=None, party=None):
        super().__init__(parent)
        self.party = party
        self.setWindowTitle("افزودن/ویرایش طرف‌حساب" if not party else "ویرایش طرف‌حساب")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Code
        code_layout = QHBoxLayout()
        code_layout.addWidget(QLabel("کد:"))
        self.code_input = QLineEdit()
        if self.party:
            self.code_input.setText(self.party.code)
        code_layout.addWidget(self.code_input)
        layout.addLayout(code_layout)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("نام:"))
        self.name_input = QLineEdit()
        if self.party:
            self.name_input.setText(self.party.name)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("نوع:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["مشتری", "تأمین‌کننده", "هر دو"])
        type_map = {"customer": 0, "supplier": 1, "both": 2}
        if self.party:
            self.type_combo.setCurrentIndex(type_map.get(self.party.party_type, 0))
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Tax ID
        tax_layout = QHBoxLayout()
        tax_layout.addWidget(QLabel("شناسه مالیاتی:"))
        self.tax_input = QLineEdit()
        if self.party and self.party.tax_id:
            self.tax_input.setText(self.party.tax_id)
        tax_layout.addWidget(self.tax_input)
        layout.addLayout(tax_layout)

        # Phone
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("تلفن:"))
        self.phone_input = QLineEdit()
        if self.party and self.party.phone:
            self.phone_input.setText(self.party.phone)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)

        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("ایمیل:"))
        self.email_input = QLineEdit()
        if self.party and self.party.email:
            self.email_input.setText(self.party.email)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)

        # Address
        address_layout = QHBoxLayout()
        address_layout.addWidget(QLabel("آدرس:"))
        self.address_input = QLineEdit()
        if self.party and self.party.address:
            self.address_input.setText(self.party.address)
        address_layout.addWidget(self.address_input)
        layout.addLayout(address_layout)

        # Credit Limit
        credit_layout = QHBoxLayout()
        credit_layout.addWidget(QLabel("سقف اعتبار (ریال):"))
        self.credit_input = QDoubleSpinBox()
        self.credit_input.setMaximum(999999999999.99)
        self.credit_input.setDecimals(2)
        if self.party and self.party.credit_limit:
            self.credit_input.setValue(float(self.party.credit_limit))
        credit_layout.addWidget(self.credit_input)
        layout.addLayout(credit_layout)

        # Active
        active_layout = QHBoxLayout()
        active_layout.addWidget(QLabel("فعال:"))
        self.active_check = QCheckBox()
        self.active_check.setChecked(self.party.is_active if self.party else True)
        active_layout.addWidget(self.active_check)
        layout.addLayout(active_layout)

        # Buttons
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
        type_reverse = {0: "customer", 1: "supplier", 2: "both"}
        return {
            "code": self.code_input.text().strip(),
            "name": self.name_input.text().strip(),
            "party_type": type_reverse[self.type_combo.currentIndex()],
            "tax_id": self.tax_input.text().strip() or None,
            "phone": self.phone_input.text().strip() or None,
            "email": self.email_input.text().strip() or None,
            "address": self.address_input.text().strip() or None,
            "credit_limit": self.credit_input.value() or None,
            "is_active": self.active_check.isChecked(),
        }

    def validate(self):
        if not self.code_input.text().strip():
            QMessageBox.warning(self, "خطا", "کد طرف‌حساب الزامی است.")
            return False
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "خطا", "نام طرف‌حساب الزامی است.")
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()