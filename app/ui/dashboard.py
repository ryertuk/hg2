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

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سامانه حسابداری و انبار - داشبورد")
        self.setGeometry(100, 100, 1000, 700)
        self.setLayoutDirection(Qt.RightToLeft)

        self.tabs = QTabWidget()

        # Tab 1: Placeholder
        placeholder_widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("مرحله 4: مدیریت فاکتورها — آماده استفاده")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
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