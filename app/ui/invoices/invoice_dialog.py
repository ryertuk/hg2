# app/ui/invoices/invoice_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QTableView, QCompleter
)
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QKeyEvent
from .invoice_line_model import InvoiceLineTableModel
from .invoice_line_delegate import InvoiceLineDelegate
from app.services.date_service import gregorian_to_jalali, jalali_to_gregorian
from app.services.party_service import PartyService
#from app.services.invoice_service import InvoiceService

class InvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice=None):
        super().__init__(parent)
        self.invoice = invoice
        self.party_service = PartyService()
#        self.invoice_service = InvoiceService()
        self.parties = []
        self.selected_party_id = None

        self.setWindowTitle("فاکتور جدید" if not invoice else "ویرایش فاکتور")
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(900, 600)
        self.setup_ui()
        self.load_parties()
        if invoice:
            self.load_invoice_lines(invoice)


    def setup_ui(self):
        layout = QVBoxLayout()
        
        # --- نوع فاکتور ---
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("نوع فاکتور:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["خرید", "فروش", "مرجوعی خرید", "مرجوعی فروش"])
        type_map = {"purchase": 0, "sale": 1, "purchase_return": 2, "sale_return": 3}
        if self.invoice:
            self.type_combo.setCurrentIndex(type_map.get(self.invoice.invoice_type, 1))
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # --- طرف حساب ---
        party_layout = QHBoxLayout()
        party_layout.addWidget(QLabel("طرف حساب:"))
        self.party_input = QLineEdit()
        self.party_input.setPlaceholderText("جستجوی طرف‌حساب بر اساس نام یا کد...")
        party_layout.addWidget(self.party_input)
        layout.addLayout(party_layout)

        self.completer_model = QStringListModel()
        self.completer = QCompleter()
        self.completer.setModel(self.completer_model)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.activated.connect(self.on_party_selected)
        self.party_input.setCompleter(self.completer)

        # --- تاریخ ---
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("تاریخ (شمسی):"))
        self.date_input = QLineEdit()
        if self.invoice:
            self.date_input.setText(self.invoice.date_jalali)
        else:
            from jdatetime import date as jdate
            self.date_input.setText(jdate.today().strftime("%Y/%m/%d"))
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)


        # --- جدول خطوط ---
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setItemDelegate(InvoiceLineDelegate(self))
        self.table_model = InvoiceLineTableModel([])
        self.table.setModel(self.table_model)
        layout.addWidget(self.table)

        # --- دکمه‌ها ---
        btn_layout = QHBoxLayout()
        add_line_btn = QPushButton("➕ افزودن خط فاکتور")
        add_line_btn.clicked.connect(self.add_invoice_line)
        btn_layout.addWidget(add_line_btn)

        remove_line_btn = QPushButton("🗑️ حذف خط انتخاب‌شده")
        remove_line_btn.clicked.connect(self.remove_invoice_line)
        btn_layout.addWidget(remove_line_btn)

        save_btn = QPushButton("ذخیره")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.party_input.textChanged.connect(self.filter_parties)

    def keyPressEvent(self, event: QKeyEvent):
        # کلیدهای قابل قبول برای اجرای عملیات
        trigger_keys = {
            Qt.Key.Key_Return, 
            Qt.Key.Key_Enter,
            # اگر می‌خواهید کلیدهای دیگری هم اضافه کنید
            # Qt.Key.Key_Space,  # کلید Space
        }
        
        if event.key() in trigger_keys:
            self.add_invoice_line()
            event.accept()
        else:
            super().keyPressEvent(event)

    # ---------------- متدهای کمکی ----------------
    def load_parties(self):
        self.parties = self.party_service.get_all_parties()
        display_list = [f"{p.name} ({p.code})" for p in self.parties]
        self.completer_model.setStringList(display_list)
        if self.invoice:
            for party in self.parties:
                if party.id == self.invoice.party_id:
                    self.party_input.setText(f"{party.name} ({party.code})")
                    self.selected_party_id = party.id
                    break

    def filter_parties(self, text):
        if not text:
            display_list = [f"{p.name} ({p.code})" for p in self.parties]
        else:
            filtered = [p for p in self.parties if text.lower() in p.name.lower() or text in p.code]
            display_list = [f"{p.name} ({p.code})" for p in filtered]
        self.completer_model.setStringList(display_list)

    def on_party_selected(self, selected_text):
        for party in self.parties:
            if f"{party.name} ({party.code})" == selected_text:
                self.selected_party_id = party.id
                break

    def add_invoice_line(self):
        self.table_model.add_line()
        
        # رفتن به سطر آخر
        last_row = self.table_model.rowCount() - 1
        
        # انتخاب سلول اول از سطر آخر
        index = self.table_model.index(last_row, 0)
        self.table.setCurrentIndex(index)
        
        # فعال کردن حالت edit برای سلول انتخاب شده
        self.table.edit(index)
        
        self.table.scrollToBottom()

    def remove_invoice_line(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک خط را انتخاب کنید.", QMessageBox.Ok)
            return
        for index in selected:
        
            self.table_model.remove_line(index.row())

    def cleanup_empty_rows(self):
        rows_to_remove = []
        for row in range(self.table_model.rowCount()):
            item_code = self.table_model.data(self.table_model.index(row, 0), Qt.DisplayRole)
            item_name = self.table_model.data(self.table_model.index(row, 1), Qt.DisplayRole)
            quantity = self.table_model.data(self.table_model.index(row, 4), Qt.DisplayRole)
            if not item_code and not item_name and not quantity:
                rows_to_remove.append(row)
        for row in sorted(rows_to_remove, reverse=True):
            self.table_model.remove_line(row)
        return len(rows_to_remove) > 0

    def has_valid_data(self):
        for row in range(self.table_model.rowCount()):
            item_code = self.table_model.data(self.table_model.index(row, 0), Qt.DisplayRole)
            item_name = self.table_model.data(self.table_model.index(row, 1), Qt.DisplayRole)
            quantity = self.table_model.data(self.table_model.index(row, 4), Qt.DisplayRole)
            unit_price = self.table_model.data(self.table_model.index(row, 3), Qt.DisplayRole)
            if item_code or item_name or (quantity and float(quantity) > 0) or (unit_price and float(unit_price) > 0):
                return True
        return False

    def load_invoice_lines(self, invoice):
        from app.services.invoice_service import InvoiceService
        from app.models.invoice_line import InvoiceLine
        service = InvoiceService()
        lines = service.db.query(InvoiceLine).filter(InvoiceLine.invoice_id == invoice.id).all()
        lines_data = []
        for line in lines:
            lines_data.append({
                'item_id': line.item_id,
                'qty': float(line.qty),
                'unit_id': line.unit_id,
                'unit_price': float(line.unit_price),
                'discount': float(line.discount),
                'tax': float(line.tax),
                'line_total': float(line.line_total),
                'notes': line.notes or ""
            })
        self.table_model.lines_data = lines_data
        self.table_model.layoutChanged.emit()
    

    def get_data(self):
        type_reverse = {0: "purchase", 1: "sale", 2: "purchase_return", 3: "sale_return"}
        if self.selected_party_id is None:
            raise ValueError("لطفاً یک طرف‌حساب انتخاب کنید.")
            
        from app.services.date_service import jalali_to_gregorian
        jalali_str = self.date_input.text().strip()
        gregorian_date = jalali_to_gregorian(jalali_str)
        
        # ✅ اگر در حالت ویرایش هستیم — serial_full قبلی را حفظ کن
        if self.invoice:
            serial_full = self.invoice.serial_full
        else:
            # ✅ فقط در حالت ایجاد جدید — serial_full جدید تولید شود
            from jdatetime import datetime as jdatetime
            now = jdatetime.now()
            serial_full = f"INV-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"
        
        return {
            "invoice_type": type_reverse[self.type_combo.currentIndex()],
            "serial": "INV",
            "number": 1,
            "serial_full": serial_full,  # ✅ اصلاح شد
            "party_id": self.selected_party_id,
            "date_gregorian": gregorian_date,
            "date_jalali": jalali_str,
            "created_by": 1,
        }

    def validate(self):
        if not self.date_input.text().strip():
            QMessageBox.warning(self, "خطا", "تاریخ الزامی است.", QMessageBox.Ok)
            return False
        if self.selected_party_id is None:
            party_text = self.party_input.text().strip()
            if not party_text:
                QMessageBox.warning(self, "خطا", "لطفاً یک طرف‌حساب انتخاب کنید.", QMessageBox.Ok)
                return False
            found = False
            for party in self.parties:
                if f"{party.name} ({party.code})" == party_text:
                    self.selected_party_id = party.id
                    found = True
                    break
            if not found:
                QMessageBox.warning(self, "خطا", "طرف‌حساب انتخاب شده معتبر نیست.", QMessageBox.Ok)
                return False
        self.cleanup_empty_rows()
        if not self.has_valid_data():
            QMessageBox.warning(self, "خطا", "جدول فاکتور نمی‌تواند خالی باشد.", QMessageBox.Ok)
            return False
        return True

    def accept(self):
        if not self.validate():
            return  # فرم باز می‌ماند
        try:
            if self.validate():
                super().accept()
        except ValueError as ve:
            # خطاهای مشخص مثل موجودی کافی نیست
            QMessageBox.warning(self, "خطا در موجودی", str(ve), QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "خطا در ذخیره فاکتور", str(e), QMessageBox.Ok)

