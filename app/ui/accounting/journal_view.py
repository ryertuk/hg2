# app/ui/accounting/journal_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableView, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from app.services.accounting_service import AccountingService

class JournalTableModel(QAbstractTableModel):
    def __init__(self, entries):
        super().__init__()
        self.entries = entries
        self.headers = ["تاریخ", "شرح", "منبع", "وضعیت"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        entry = self.entries[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return entry.date.strftime("%Y-%m-%d")
            elif col == 1: return entry.description or "-"
            elif col == 2: return f"{entry.source_type} #{entry.source_id}"
            elif col == 3: return "ثبت شده" if entry.posted else "پیش‌نویس"
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class JournalView(QWidget):
    def __init__(self):
        super().__init__()
        self.service = AccountingService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("📚 دفتر روزنامه")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Period Filter
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("دوره مالی (YYYY-MM):"))
        self.period_input = QLineEdit()
        from jdatetime import date as jdate
        today = jdate.today()
        self.period_input.setText(f"{today.year}-{today.month:02d}")
        period_layout.addWidget(self.period_input)
        self.filter_btn = QPushButton("فیلتر")
        self.filter_btn.clicked.connect(self.load_data)
        period_layout.addWidget(self.filter_btn)
        layout.addLayout(period_layout)

        # Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.close_period_btn = QPushButton("🔒 بستن دوره مالی")
        self.close_period_btn.clicked.connect(self.close_period)
        btn_layout.addWidget(self.close_period_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        period = self.period_input.text().strip()
        if not period:
            QMessageBox.warning(self, "خطا", "لطفاً دوره مالی را وارد کنید.")
            return
        self.entries = self.service.get_journal_entries_by_period(period)
        self.model = JournalTableModel(self.entries)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

    def close_period(self):
        QMessageBox.information(self, "به زودی", "بستن دوره مالی در نسخه بعدی فعال خواهد شد.")