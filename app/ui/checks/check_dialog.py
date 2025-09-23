# app/ui/checks/check_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QComboBox, QDateEdit, QDoubleSpinBox, QPushButton,
                               QMessageBox, QCompleter, QToolButton)
from PySide6.QtCore import Qt, QStringListModel, QEvent  # QEvent را import کنید
from app.services.party_service import PartyService
from app.services.date_service import jalali_to_gregorian, gregorian_to_jalali
import datetime

class CheckDialog(QDialog):
    def __init__(self, parent=None, check=None):
        super().__init__(parent)
        self.check = check
        self.party_service = PartyService()
        self.parties = []
        self.selected_payer_id = None
        self.selected_payee_id = None

        self.setWindowTitle("چک جدید" if not check else "ویرایش چک")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        self.load_parties()

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

        # نام بانک — با QComboBox + لیست ثابت
        bank_layout = QHBoxLayout()
        bank_layout.addWidget(QLabel("نام بانک:"))
        self.bank_combo = QComboBox()
        bank_list = [
            "آینده", "اقتصاد نوین", "ایران زمین", "انصار", "پارسیان", "پاسارگاد",
            "توسعه تعاون", "توسعه صادرات", "تجارت", "حکمت ایرانیان", "خاورمیانه",
            "دی", "رسالت", "سپه", "سینا", "سرمایه", "سامان", "شهر","صادرات", "صنعت و معدن",
            "کشاورزی", "کارآفرین", "قوامین", "گردشگری", "ملی","ملت", "مسکن", "مهر اقتصاد", "مهر ایران", "سایر"
        ]
        self.bank_combo.addItems(bank_list)
        if self.check:
            # تنظیم مقدار فعلی — اگر در لیست وجود داشت
            try:
                index = bank_list.index(self.check.bank_name)
                self.bank_combo.setCurrentIndex(index)
            except ValueError:
                self.bank_combo.addItem(self.check.bank_name)
                self.bank_combo.setCurrentIndex(len(bank_list))
        bank_layout.addWidget(self.bank_combo)
        layout.addLayout(bank_layout)

        # شماره حساب — قابل ویرایش
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("شماره حساب:"))
        self.account_input = QLineEdit()
        if self.check:
            self.account_input.setText(self.check.account_number)
        account_layout.addWidget(self.account_input)
        layout.addLayout(account_layout)

        # مبلغ — بدون دکمه +
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("مبلغ (ریال):"))
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(999999999999999)
        self.amount_input.setDecimals(0)
        if self.check:
            self.amount_input.setValue(float(self.check.amount))
        
        # تنظیم shortcut برای کلید +
        self.amount_input.installEventFilter(self)
        
        amount_layout.addWidget(self.amount_input)
        layout.addLayout(amount_layout)

        # تاریخ صدور و سررسید — شمسی با فرمت 14--/--/--
        dates_layout = QHBoxLayout()
        dates_layout.addWidget(QLabel("تاریخ صدور (شمسی):"))
        self.issue_date_input = QLineEdit()
        self.issue_date_input.setInputMask("1499/99/99")
        self.issue_date_input.setText("14  /  /  ")
        self.issue_date_input.setCursorPosition(2)  # قرار دادن курсور در ابتدای قسمت سال
        dates_layout.addWidget(self.issue_date_input)
        
        dates_layout.addWidget(QLabel("سررسید (شمسی):"))
        self.due_date_input = QLineEdit()
        self.due_date_input.setInputMask("1499/99/99")
        self.due_date_input.setText("14  /  /  ")
        self.due_date_input.setCursorPosition(2)  # قرار دادن курсور در ابتدای قسمت سال
        dates_layout.addWidget(self.due_date_input)
        layout.addLayout(dates_layout)
        
        # اگر در حال ویرایش هستیم، تاریخ‌ها را از دیتابیس پر کنیم
        if self.check:
            # تاریخ صدور
            if hasattr(self.check, 'date_jalali') and self.check.date_jalali:
                jalali_date = self.convert_to_two_digit_year(self.check.date_jalali)
                self.issue_date_input.setText(jalali_date)
            elif self.check.issue_date:
                j_issue = gregorian_to_jalali(self.check.issue_date)
                j_issue = self.convert_to_two_digit_year(j_issue)
                self.issue_date_input.setText(j_issue)
            
            # تاریخ سررسید
            if self.check.due_date:
                j_due = gregorian_to_jalali(self.check.due_date)
                j_due = self.convert_to_two_digit_year(j_due)
                self.due_date_input.setText(j_due)
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
    def convert_to_two_digit_year(self, jalali_date):
        """تبدیل تاریخ شمسی به فرمت دو رقمی (۱۴۰۳ -> ۱۴۰۳)"""
        if not jalali_date:
            return "14  /  /  "
        
        try:
            # جدا کردن قسمت‌های تاریخ
            parts = jalali_date.split('/')
            if len(parts) == 3:
                year = parts[0]
                if len(year) == 4:
                    # گرفتن دو رقم آخر سال
                    two_digit_year = year[2:]
                    return f"14{two_digit_year}/{parts[1]}/{parts[2]}"
                else:
                    return f"14{year}/{parts[1]}/{parts[2]}"
        except:
            pass
        return "14  /  /  "
    def eventFilter(self, obj, event):
        """مدیریت رویدادهای کیبورد برای فیلد مبلغ"""
        if obj == self.amount_input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key_Plus:
                self.add_zeros_to_amount()
                return True  # رویداد پردازش شده است
        return super().eventFilter(obj, event)

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

    def add_zeros_to_amount(self):
        """افزودن سه صفر به مبلغ — ضرب در 1000"""
        current_value = self.amount_input.value()
        new_value = current_value * 1000
        self.amount_input.setValue(new_value)
      
        
    def get_data(self):
        direction = "received" if self.direction_combo.currentIndex() == 0 else "issued"
    
        # پردازش تاریخ‌ها - گرفتن مقدار از فیلدها
        issue_date_text = self.issue_date_input.text().replace(" ", "0")
        due_date_text = self.due_date_input.text().replace(" ", "0")
        
        # اطمینان از کامل بودن تاریخ‌ها
        if len(issue_date_text.replace("/", "")) < 6:
            QMessageBox.warning(self, "خطا", "تاریخ صدور باید کامل پر شود.")
            return None
            
        if len(due_date_text.replace("/", "")) < 6:
            QMessageBox.warning(self, "خطا", "تاریخ سررسید باید کامل پر شود.")
            return None
        
        # تبدیل به فرمت کامل شمسی (۱۴۰x/xx/xx)
        # از آنجایی که InputMask داریم، فرمت 14xx/xx/xx است
        # باید به 140x/xx/xx تبدیل شود
        try:
            # تاریخ صدور
            if issue_date_text.startswith("14"):
                # استخراج دو رقم آخر سال از 14xx
                year_suffix = issue_date_text[2:4]  # دو رقم بعد از 14
                full_year = "140" + year_suffix[0]  # 140 + اولین رقم
                issue_date_text = f"{full_year}/{issue_date_text[5:7]}/{issue_date_text[8:10]}"
            
            # تاریخ سررسید
            if due_date_text.startswith("14"):
                year_suffix = due_date_text[2:4]  # دو رقم بعد از 14
                full_year = "140" + year_suffix[0]  # 140 + اولین رقم
                due_date_text = f"{full_year}/{due_date_text[5:7]}/{due_date_text[8:10]}"
            
            # تبدیل به میلادی
            issue_date = jalali_to_gregorian(issue_date_text)
            due_date = jalali_to_gregorian(due_date_text)
            
        except ValueError as e:
            QMessageBox.warning(self, "خطا در تاریخ", f"تاریخ وارد شده معتبر نیست: {str(e)}")
            return None
        except Exception as e:
            QMessageBox.warning(self, "خطا در تاریخ", f"خطا در پردازش تاریخ: {str(e)}")
            return None
    
        return {
            "check_number": self.check_num_input.text().strip(),
            "bank_name": self.bank_combo.currentText().strip(),
            "account_number": self.account_input.text().strip(),
            "direction": direction,
            "amount": int(self.amount_input.value()),
            "issue_date": issue_date,
            "due_date": due_date,
            "payer_party_id": self.selected_payer_id,
            "payee_party_id": self.selected_payee_id,
            "created_by": 1,
            "bank_account_id": 1,
        }
        
    def validate(self):
        if not self.check_num_input.text().strip():
            QMessageBox.warning(self, "خطا", "شماره چک الزامی است.")
            return False
        
        # بررسی تاریخ‌ها - باید کامل پر شده باشند
        issue_date_text = self.issue_date_input.text()
        due_date_text = self.due_date_input.text()
        
        if " " in issue_date_text or len(issue_date_text.replace("/", "")) < 8:
            QMessageBox.warning(self, "خطا", "تاریخ صدور باید کامل پر شود.")
            return False
            
        if " " in due_date_text or len(due_date_text.replace("/", "")) < 8:
            QMessageBox.warning(self, "خطا", "تاریخ سررسید باید کامل پر شود.")
            return False
            
        if not self.bank_combo.currentText().strip():
            QMessageBox.warning(self, "خطا", "نام بانک الزامی است.")
            return False
        if not self.account_input.text().strip():
            QMessageBox.warning(self, "خطا", "شماره حساب الزامی است.")
            return False
        return True

    def validate_and_set_parties(self):
        """اعتبارسنجی و تنظیم طرف‌حساب‌ها بر اساس متن وارد شده — حتی اگر از لیست انتخاب نشده باشد"""
        payer_text = self.payer_input.text().strip()
        payee_text = self.payee_input.text().strip()

        # پرداخت‌کننده
        if payer_text:
            self.selected_payer_id = self.find_party_by_text(payer_text)
            if self.selected_payer_id is None:
                raise ValueError(f"طرف‌حساب پرداخت‌کننده «{payer_text}» یافت نشد.")

        # دریافت‌کننده
        if payee_text:
            self.selected_payee_id = self.find_party_by_text(payee_text)
            if self.selected_payee_id is None:
                raise ValueError(f"طرف‌حساب دریافت‌کننده «{payee_text}» یافت نشد.")
    
    def find_party_by_text(self, text):
        """پیدا کردن طرف‌حساب بر اساس نام یا کد — حتی اگر دقیقاً مطابقت نداشته باشد"""
        if not text:
            return None
        for party in self.parties:
            if text == party.name or text == party.code or text in f"{party.name} ({party.code})":
                return party.id
        return None
        
    def accept(self):
        if self.validate():
            try:
                # ✅ تنظیم طرف‌حساب‌ها بر اساس متن وارد شده
                self.validate_and_set_parties()
                super().accept()
            except ValueError as e:
                QMessageBox.warning(self, "خطا", str(e))
                
            data = self.get_data()
            if data is not None:  # فقط اگر داده‌ها معتبر باشند
                super().accept()
                
       
        