from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox, QPushButton, QMessageBox
from app.services.items_service import create_item
from app.models.items import ItemPydantic
from app.services.units_service import get_all_units  # برای انتخاب base_unit

class ItemsDialog(QDialog):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.sku = QLineEdit()
        self.name = QLineEdit()
        self.unit_type = QComboBox()
        self.unit_type.addItems(['count', 'measure'])
        self.base_unit_id = QComboBox()
        units = get_all_units()
        self.base_unit_id.addItems([f"{u.id}: {u.code}" for u in units])
        self.length = QDoubleSpinBox()
        self.width = QDoubleSpinBox()
        self.active = QCheckBox(checked=True)
        self.barcode = QLineEdit()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addRow("SKU", self.sku)
        layout.addRow("Name", self.name)
        layout.addRow("Unit Type", self.unit_type)
        layout.addRow("Base Unit", self.base_unit_id)
        layout.addRow("Length", self.length)
        layout.addRow("Width", self.width)
        layout.addRow("Active", self.active)
        layout.addRow("Barcode", self.barcode)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save(self):
        try:
            base_unit_id = int(self.base_unit_id.currentText().split(':')[0])
            data = ItemPydantic(sku=self.sku.text(), name=self.name.text(), unit_type=self.unit_type.currentText(),
                                base_unit_id=base_unit_id, length=self.length.value(), width=self.width.value(),
                                active=self.active.isChecked(), barcode=self.barcode.text())
            create_item(data.dict())
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))