# app/ui/dashboard.py
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QTabWidget
from PySide6.QtCore import Qt
from app.ui.parties.party_list import PartyListView
from app.ui.units.unit_list import UnitListView
from app.ui.items.item_list import ItemListView
from app.ui.stock.stock_view import StockView
from app.ui.invoices.invoice_list import InvoiceListView
from app.ui.checks.check_list import CheckListView
from app.ui.accounting.journal_view import JournalView 
from app.ui.backup.backup_view import BackupView
from PySide6.QtWidgets import QGridLayout, QFrame
from app.services.dashboard_service import DashboardService  # جدید — باید ایجاد شود

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سامانه حسابداری و انبار - داشبورد")
        self.setGeometry(100, 100, 1000, 700)
        self.setLayoutDirection(Qt.RightToLeft)

        self.tabs = QTabWidget()
        
        # Tab 1: Placeholder
        # جایگزین کردن تب placeholder
        placeholder_widget = QWidget()
        layout = QGridLayout()
        # عنوان
        title_label = QLabel("📊 خلاصه عملکرد سیستم")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label, 0, 0, 1, 3)

        # کارت‌های آمار
        service = DashboardService()

        # کارت ۱: تعداد کالاها
        card1 = self.create_stat_card("📦 تعداد کالاها", f"{service.get_item_count():,}")
        layout.addWidget(card1, 1, 0)

        # کارت ۲: تعداد طرف‌حساب‌ها
        card2 = self.create_stat_card("👥 تعداد طرف‌حساب‌ها", f"{service.get_party_count():,}")
        layout.addWidget(card2, 1, 1)

        # کارت ۳: موجودی کل انبار (ریال)
        card3 = self.create_stat_card("💰 ارزش کل انبار", f"{service.get_total_inventory_value():,} ریال")
        layout.addWidget(card3, 1, 2)

        # کارت ۴: فاکتورهای امروز
        card4 = self.create_stat_card("📄 فاکتورهای امروز", f"{service.get_today_invoices_count()}")
        layout.addWidget(card4, 2, 0)

        # کارت ۵: چک‌های در جریان
        card5 = self.create_stat_card("💳 چک‌های در جریان", f"{service.get_active_checks_count()}")
        layout.addWidget(card5, 2, 1)

        # کارت ۶: بدهی/طلب کل
        card6 = self.create_stat_card("📊 بدهی/طلب کل", f"{service.get_total_receivable_payable():,} ریال")
        layout.addWidget(card6, 2, 2)

        placeholder_widget.setLayout(layout)
        self.tabs.insertTab(0, placeholder_widget, "📊 داشبورد")
        #

        
        
        placeholder_widget.setLayout(layout)
        self.tabs.addTab(placeholder_widget, "داشبورد")

        # Tab 2: Parties
        self.party_view = PartyListView()
        self.tabs.addTab(self.party_view, "طرف‌حساب‌ها")

        # Tab 3: Units
        self.unit_view = UnitListView()
        self.tabs.addTab(self.unit_view, "واحدها")

        # Tab 4: Items
        self.item_view = ItemListView()
        self.tabs.addTab(self.item_view, "کالاها")

        # Tab 5: Stock
        self.stock_view = StockView()
        self.tabs.addTab(self.stock_view, "📦 انبار")

        # Tab 6: Invoices ✅ اضافه شد
        self.invoice_view = InvoiceListView()
        self.tabs.addTab(self.invoice_view, "📄 فاکتورها")
        
        # Tab 7: checks
        self.check_view = CheckListView()
        self.tabs.addTab(self.check_view, "💳 چک‌ها")
        
        # Tab 8: Journal ✅ اضافه شد
        self.journal_view = JournalView()
        self.tabs.addTab(self.journal_view, "📚 دفتر روزنامه")
        
        self.backup_view = BackupView()
        self.tabs.addTab(self.backup_view, "💾 بک‌آپ و بازیابی")

        self.setCentralWidget(self.tabs)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                font-family: 'Tahoma', 'Yekan', sans-serif;
                font-size: 14px;
            }
            QLabel {
                padding: 20px;
            }
            QPushButton {
                padding: 8px 15px;
                margin: 5px;
            }
        """)
        
    def create_stat_card(self, title, value):
        """ایجاد یک کارت آماری"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setStyleSheet("border: 2px solid #ccc; border-radius: 10px; padding: 15px;")
    
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666; font-weight: bold;")
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        value_label.setAlignment(Qt.AlignCenter)
    
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        frame.setLayout(layout)
        return frame        