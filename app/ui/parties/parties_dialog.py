# parties_dialog.py
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox, QPushButton, QMessageBox
from app.services.parties_service import create_party

class PartiesDialog(QDialog):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.code = QLineEdit()
        self.name = QLineEdit()
        self.party_type = QComboBox()
        self.party_type.addItems(['customer', 'supplier', 'both'])
        self.credit_limit = QSpinBox()
        self.credit_limit.setMaximum(999999999)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addRow("Code", self.code)
        layout.addRow("Name", self.name)
        layout.addRow("Type", self.party_type)
        layout.addRow("Credit Limit", self.credit_limit)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save(self):
        try:
            data = PartyPydantic(code=self.code.text(), name=self.name.text(), party_type=self.party_type.currentText(), credit_limit=self.credit_limit.value())
            create_party(data.dict())
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))