# app/ui/invoices/invoice_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QComboBox, QPushButton, QMessageBox, QTableView, QCompleter)
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QKeyEvent
from .invoice_line_model import InvoiceLineTableModel
from .invoice_line_delegate import InvoiceLineDelegate
from app.services.date_service import gregorian_to_jalali, jalali_to_gregorian
from app.services.party_service import PartyService


class InvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice=None):
        super().__init__(parent)
        self.invoice = invoice
        self.party_service = PartyService()
        self.parties = []
        self.selected_party_id = None  # ✅ این متغیر کلیدی است

        self.setWindowTitle("فاکتور جدید" if not invoice else "ویرایش فاکتور")
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(900, 600)  # ✅ اندازه صفحه بزرگتر
        self.setup_ui()
        self.load_parties()
        # ✅ بارگذاری خطوط فاکتور در حالت ویرایش
        if invoice:
            self.load_invoice_lines(invoice)

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

        # طرف حساب — با جستجوی پیشرفته
        party_layout = QHBoxLayout()
        party_layout.addWidget(QLabel("طرف حساب:"))
        self.party_input = QLineEdit()
        self.party_input.setPlaceholderText("جستجوی طرف‌حساب بر اساس نام یا کد...")
        party_layout.addWidget(self.party_input)
        layout.addLayout(party_layout)

        # مدل برای completer
        self.completer_model = QStringListModel()
        self.completer = QCompleter()
        self.completer.setModel(self.completer_model)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.activated.connect(self.on_party_selected)  # ✅ اتصال سیگنال
        self.party_input.setCompleter(self.completer)

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
        self.table.setSelectionBehavior(QTableView.SelectRows)  # ✅ تغییر مهم: انتخاب کل سطر
        self.table.setSelectionMode(QTableView.SingleSelection)  # ✅ فقط یک سطر قابل انتخاب
        self.table.setItemDelegate(InvoiceLineDelegate(self))
        self.table_model = InvoiceLineTableModel([])
        self.table.setModel(self.table_model)
        
        
        layout.addWidget(self.table)

        # دکمه‌ها
        btn_layout = QHBoxLayout()
        add_line_btn = QPushButton("➕ افزودن خط فاکتور")
        add_line_btn.clicked.connect(self.add_invoice_line)
        btn_layout.addWidget(add_line_btn)

        remove_line_btn = QPushButton("🗑️ حذف خط انتخاب‌شده")
        remove_line_btn.clicked.connect(self.remove_invoice_line)  # ✅ اتصال سیگنال
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
        """✅ اضافه کردن خط فاکتور با زدن دکمه *"""
        if event.text() == '*':
            self.add_invoice_line()
            event.accept()
        else:
            super().keyPressEvent(event)

    def load_parties(self):
        self.parties = self.party_service.get_all_parties()
        display_list = [f"{p.name} ({p.code})" for p in self.parties]
        self.completer_model.setStringList(display_list)

        if self.invoice:
            for i, party in enumerate(self.parties):
                if party.id == self.invoice.party_id:
                    self.party_input.setText(f"{party.name} ({party.code})")
                    self.selected_party_id = party.id  # ✅ تنظیم اولیه
                    break

    def filter_parties(self, text):
        if not text:
            display_list = [f"{p.name} ({p.code})" for p in self.parties]
            self.completer_model.setStringList(display_list)
            return
        filtered = [p for p in self.parties if text.lower() in p.name.lower() or text in p.code]
        display_list = [f"{p.name} ({p.code})" for p in filtered]
        self.completer_model.setStringList(display_list)

    def on_party_selected(self, selected_text):
        """✅ این متد کلیدی است — selected_party_id را تنظیم می‌کند"""
        for party in self.parties:
            if f"{party.name} ({party.code})" == selected_text:
                self.selected_party_id = party.id
                print(f"طرف‌حساب انتخاب شد: {party.name} (ID: {party.id})")  # برای دیباگ
                break

    def add_invoice_line(self):
        self.table_model.add_line()
        self.table.scrollToBottom()

    def remove_invoice_line(self):
        """✅ حذف خط انتخاب‌شده — اصلاح شده"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک خط را انتخاب کنید.")
            return
        
        # ✅ حذف سطر انتخاب شده
        for index in selected:
            row = index.row()
            self.table_model.remove_line(row)

    def cleanup_empty_rows(self):
        """✅ حذف سطرهای خالی قبل از ذخیره"""
        rows_to_remove = []
        for row in range(self.table_model.rowCount()):
            # استفاده از متد data برای دسترسی به مقادیر
            item_code = self.table_model.data(self.table_model.index(row, 0), Qt.DisplayRole)  # ستون کد کالا
            item_name = self.table_model.data(self.table_model.index(row, 1), Qt.DisplayRole)  # ستون نام کالا
            quantity = self.table_model.data(self.table_model.index(row, 4), Qt.DisplayRole)   # ستون تعداد
        
            if not item_code and not item_name and not quantity:
                rows_to_remove.append(row)
    
        # حذف سطرهای خالی از انتها به ابتدا
        for row in sorted(rows_to_remove, reverse=True):
            self.table_model.remove_line(row)
    
        return len(rows_to_remove) > 0

    def load_invoice_lines(self, invoice):
        """بارگذاری خطوط فاکتور در حالت ویرایش"""
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
                'unit_price': int(line.unit_price),
                'discount': int(line.discount),
                'tax': int(line.tax),
                'line_total': int(line.line_total),
                'notes': line.notes or ""
            })
        self.table_model.lines_data = lines_data
        self.table_model.layoutChanged.emit()
 
    def has_valid_data(self):
        """✅ بررسی وجود داده معتبر در جدول"""
        for row in range(self.table_model.rowCount()):
            item_code = self.table_model.data(self.table_model.index(row, 0), Qt.DisplayRole)  # ستون کد کالا
            item_name = self.table_model.data(self.table_model.index(row, 1), Qt.DisplayRole)  # ستون نام کالا
            quantity = self.table_model.data(self.table_model.index(row, 4), Qt.DisplayRole)   # ستون تعداد
            unit_price = self.table_model.data(self.table_model.index(row, 3), Qt.DisplayRole) # ستون قیمت واحد
        
            # اگر حداقل یکی از فیلدهای ضروری پر شده باشد
            if item_code or item_name or (quantity and float(quantity) > 0) or (unit_price and float(unit_price) > 0):
                return True
        return False


    # در متد get_data — جایگزین کامل
    def get_data(self):
        type_reverse = {0: "purchase", 1: "sale", 2: "purchase_return", 3: "sale_return"}
        if self.selected_party_id is None:
            raise ValueError("لطفاً یک طرف‌حساب انتخاب کنید.")
        
        from app.services.date_service import jalali_to_gregorian
        jalali_str = self.date_input.text().strip()
        gregorian_date = jalali_to_gregorian(jalali_str)
        
        # ✅ تولید serial_full منحصربه‌فرد — بر اساس تاریخ و زمان شمسی
        from jdatetime import datetime as jdatetime
        now = jdatetime.now()
        # قالب: INV-14040631-142305
        serial_full = f"INV-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"
        
        return {
            "invoice_type": type_reverse[self.type_combo.currentIndex()],
            "serial": "INV",
            "number": 1,  # در عمل: می‌تواند حذف شود — چون دیگر نیازی به شماره سریالی نیست
            "serial_full": serial_full,  # ✅ منحصربه‌فرد — بدون نیاز به دیتابیس
            "party_id": self.selected_party_id,
            "date_gregorian": gregorian_date,
            "date_jalali": jalali_str,
            "created_by": 1,
        }

    def validate(self):
        if not self.date_input.text().strip():
            QMessageBox.warning(self, "خطا", "تاریخ الزامی است.")
            return False
        
        # ✅ اعتبارسنجی بهبود یافته برای طرف حساب
        if self.selected_party_id is None:
            party_text = self.party_input.text().strip()
            if not party_text:
                QMessageBox.warning(self, "خطا", "لطفاً یک طرف‌حساب انتخاب کنید.")
                return False
            
            # بررسی مجدد برای پیدا کردن طرف حساب بر اساس متن وارد شده
            found = False
            for party in self.parties:
                if f"{party.name} ({party.code})" == party_text:
                    self.selected_party_id = party.id
                    found = True
                    break
            
            if not found:
                QMessageBox.warning(self, "خطا", "طرف‌حساب انتخاب شده معتبر نیست.")
                return False
        
        # ✅ حذف سطرهای خالی قبل از بررسی
        self.cleanup_empty_rows()
        
        # ✅ بررسی وجود داده در جدول
        if not self.has_valid_data():
            QMessageBox.warning(self, "خطا", "جدول فاکتور نمی‌تواند خالی باشد. لطفاً حداقل یک آیتم اضافه کنید.")
            return False
        
        return True

    def accept(self):
        if self.validate():
            super().accept()