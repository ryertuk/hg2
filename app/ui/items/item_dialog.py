# app/ui/items/item_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QComboBox, QDoubleSpinBox, QCheckBox, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
from app.utils.code_generator import generate_sku
from app.services.unit_service import UnitService

class ItemDialog(QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.item = item
        self.unit_service = UnitService()
        self.units = self.unit_service.get_all_units()
        self.setWindowTitle("افزودن کالا" if not item else "ویرایش کالا")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # SKU (خودکار برای جدید)
        sku_layout = QHBoxLayout()
        sku_layout.addWidget(QLabel("کد کالا (SKU):"))
        self.sku_input = QLineEdit()
        if self.item:
            self.sku_input.setText(self.item.sku)
            self.sku_input.setReadOnly(True)
        else:
            self.sku_input.setText(generate_sku())
            self.sku_input.setReadOnly(True)
        sku_layout.addWidget(self.sku_input)
        layout.addLayout(sku_layout)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("نام کالا:"))
        self.name_input = QLineEdit()
        if self.item:
            self.name_input.setText(self.item.name)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Unit Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("نوع واحد:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["تعدادی (count)", "اندازه‌ای (measure)"])
        if self.item:
            self.type_combo.setCurrentIndex(0 if self.item.unit_type == "count" else 1)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Base Unit
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("واحد پایه:"))
        self.unit_combo = QComboBox()
        self.unit_combo.addItems([f"{u.name} ({u.code})" for u in self.units])
        if self.item:
            unit_map = {u.id: i for i, u in enumerate(self.units)}
            self.unit_combo.setCurrentIndex(unit_map.get(self.item.base_unit_id, 0))
        unit_layout.addWidget(self.unit_combo)
        layout.addLayout(unit_layout)

        # Dimensions (if measure)
        dim_layout = QHBoxLayout()
        dim_layout.addWidget(QLabel("طول (متر):"))
        self.length_input = QDoubleSpinBox()
        self.length_input.setDecimals(4)
        self.length_input.setMaximum(999999.9999)
        if self.item and self.item.length:
            self.length_input.setValue(float(self.item.length))
        dim_layout.addWidget(self.length_input)

        dim_layout.addWidget(QLabel("عرض (متر):"))
        self.width_input = QDoubleSpinBox()
        self.width_input.setDecimals(4)
        self.width_input.setMaximum(999999.9999)
        if self.item and self.item.width:
            self.width_input.setValue(float(self.item.width))
        dim_layout.addWidget(self.width_input)
        layout.addLayout(dim_layout)

        # Barcode
        barcode_layout = QHBoxLayout()
        barcode_layout.addWidget(QLabel("بارکد:"))
        self.barcode_input = QLineEdit()
        if self.item and self.item.barcode:
            self.barcode_input.setText(self.item.barcode)
        barcode_layout.addWidget(self.barcode_input)
        layout.addLayout(barcode_layout)

        # Active
        active_layout = QHBoxLayout()
        active_layout.addWidget(QLabel("فعال:"))
        self.active_check = QCheckBox()
        self.active_check.setChecked(self.item.active if self.item else True)
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
        unit_id = self.units[self.unit_combo.currentIndex()].id
        unit_type = "count" if self.type_combo.currentIndex() == 0 else "measure"
        return {
            "sku": self.sku_input.text().strip(),
            "name": self.name_input.text().strip(),
            "unit_type": unit_type,
            "base_unit_id": unit_id,
            "length": self.length_input.value() if unit_type == "measure" else None,
            "width": self.width_input.value() if unit_type == "measure" else None,
            "barcode": self.barcode_input.text().strip() or None,
            "active": self.active_check.isChecked(),
        }

    def validate(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "خطا", "نام کالا الزامی است.")
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()