# app/ui/invoices/invoice_list.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableView, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from app.services.invoice_service import InvoiceService

# جایگزین کلاس InvoiceTableModel
class InvoiceTableModel(QAbstractTableModel):
    def __init__(self, invoices_with_party):
        super().__init__()
        self.invoices = invoices_with_party  # لیست tupleهای (Invoice, party_name)
        self.headers = ["سریال", "نوع", "طرف حساب", "تاریخ", "جمع کل", "وضعیت"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.invoices)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        invoice, party_name = self.invoices[index.row()]  # ✅ تغییر اینجا
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return invoice.serial_full
            elif col == 1:
                type_map = {"purchase": "خرید", "sale": "فروش", "purchase_return": "مرجوعی خرید", "sale_return": "مرجوعی فروش"}
                return type_map.get(invoice.invoice_type, invoice.invoice_type)
            elif col == 2: return party_name or "-"  # ✅ نمایش نام طرف‌حساب
            elif col == 3: return invoice.date_jalali or "—"  # ✅ تاریخ شمسی
            elif col == 4: return f"{invoice.total:,.0f}"
            elif col == 5: return invoice.status
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class InvoiceListView(QWidget):
    def __init__(self):
        super().__init__()
        self.service = InvoiceService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("📄 لیست فاکتورها")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("جستجو:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_data)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ ایجاد فاکتور جدید")
        self.add_btn.clicked.connect(self.add_invoice)
        self.edit_btn = QPushButton("✏️ ویرایش")
        self.edit_btn.clicked.connect(self.edit_invoice)
        self.delete_btn = QPushButton("🗑️ حذف")
        self.delete_btn.clicked.connect(self.delete_invoice)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        self.invoices = self.service.get_all_invoices_with_parties()  # ✅ اصلاح شد
        self.model = InvoiceTableModel(self.invoices)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

    def filter_data(self):
        text = self.search_input.text().lower()
        filtered = [inv for inv in self.invoices if text in inv.serial_full.lower()]
        self.model.invoices = filtered
        self.model.layoutChanged.emit()

    def add_invoice(self):
        from app.ui.invoices.invoice_dialog import InvoiceDialog
        dialog = InvoiceDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                # ✅ دریافت خطوط فاکتور از مدل جدول
                lines_data = dialog.table_model.lines_data
                # ✅ ارسال خطوط فاکتور به سرویس
                self.service.create_invoice(data, lines_data)
                QMessageBox.information(self, "موفق", "فاکتور با موفقیت ایجاد شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ایجاد: {str(e)}")
    def edit_invoice(self):
        from app.ui.invoices.invoice_dialog import InvoiceDialog  # ✅ اضافه شد
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک فاکتور را انتخاب کنید.")
            return
        row = selected[0].row()
        invoice, party_name = self.model.invoices[row]  # ✅ invoice[0] نیست — چون در مدل tuple است
        dialog = InvoiceDialog(self, invoice)
        if dialog.exec():
            data = dialog.get_data()
            lines_data = dialog.table_model.lines_data
            try:
                # فرض — باید update_invoice در سرویس اضافه شود
                self.service.update_invoice(invoice.id, data, lines_data)
                QMessageBox.information(self, "موفق", "فاکتور با موفقیت ویرایش شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ویرایش: {str(e)}")
    
    def delete_invoice(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک فاکتور را انتخاب کنید.")
            return
        row = selected[0].row()
        invoice, party_name = self.model.invoices[row]  # ✅ tuple است
        if QMessageBox.question(self, "تأیید حذف", f"آیا از حذف فاکتور «{invoice.serial_full}» اطمینان دارید؟", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.service.delete_invoice(invoice.id)
                QMessageBox.information(self, "موفق", "فاکتور حذف شد.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")