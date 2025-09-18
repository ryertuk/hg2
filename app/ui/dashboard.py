# app/ui/dashboard.py — به‌روزرسانی
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QTabWidget
from PySide6.QtCore import Qt
from app.ui.parties.party_list import PartyListView
from app.ui.units.unit_list import UnitListView      # ✅ جدید
from app.ui.items.item_list import ItemListView      # ✅ جدید

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
        label = QLabel("مرحله 2: مدیریت کالاها و واحدها — آماده استفاده")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        placeholder_widget.setLayout(layout)
        self.tabs.addTab(placeholder_widget, "داشبورد")

        # Tab 2: Parties
        self.party_view = PartyListView()
        self.tabs.addTab(self.party_view, "طرف‌حساب‌ها")

        # Tab 3: Units ✅
        self.unit_view = UnitListView()
        self.tabs.addTab(self.unit_view, "واحدها")

        # Tab 4: Items ✅
        self.item_view = ItemListView()
        self.tabs.addTab(self.item_view, "کالاها")

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