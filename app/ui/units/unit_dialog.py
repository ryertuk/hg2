# app/ui/units/unit_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QDoubleSpinBox, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
from app.utils.code_generator import generate_unit_code

class UnitDialog(QDialog):
    def __init__(self, parent=None, unit=None):
        super().__init__(parent)
        self.unit = unit
        self.setWindowTitle("افزودن واحد" if not unit else "ویرایش واحد")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Code (خودکار برای جدید — فقط نمایش برای ویرایش)
        code_layout = QHBoxLayout()
        code_layout.addWidget(QLabel("کد:"))
        self.code_input = QLineEdit()
        if self.unit:
            self.code_input.setText(self.unit.code)
            self.code_input.setReadOnly(True)
        else:
            self.code_input.setText(generate_unit_code())
            self.code_input.setReadOnly(True)
        code_layout.addWidget(self.code_input)
        layout.addLayout(code_layout)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("نام:"))
        self.name_input = QLineEdit()
        if self.unit:
            self.name_input.setText(self.unit.name)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Factor
        factor_layout = QHBoxLayout()
        factor_layout.addWidget(QLabel("ضریب تبدیل به واحد پایه:"))
        self.factor_input = QDoubleSpinBox()
        self.factor_input.setDecimals(4)
        self.factor_input.setMaximum(999999.9999)
        self.factor_input.setMinimum(0.0001)
        if self.unit and self.unit.factor_to_base:
            self.factor_input.setValue(float(self.unit.factor_to_base))
        else:
            self.factor_input.setValue(1.0)
        factor_layout.addWidget(self.factor_input)
        layout.addLayout(factor_layout)

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
        return {
            "code": self.code_input.text().strip(),
            "name": self.name_input.text().strip(),
            "factor_to_base": self.factor_input.value(),
        }

    def validate(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "خطا", "نام واحد الزامی است.")
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()