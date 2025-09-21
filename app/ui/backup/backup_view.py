# app/ui/backup/backup_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableView, QLabel, QMessageBox, QFileDialog,
                               QCheckBox, QLineEdit)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import QInputDialog
import os
from app.backup.backup_service import BackupService
from app.backup.restore_service import RestoreService

class BackupTableModel(QAbstractTableModel):
    def __init__(self, backup_files):
        super().__init__()
        self.backups = backup_files
        self.headers = ["نام فایل", "تاریخ", "اندازه (KB)"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.backups)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        backup = self.backups[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return os.path.basename(backup)
            elif col == 1:
                timestamp = backup.split('_')[-2] + '_' + backup.split('_')[-1].replace('.zip', '').replace('.enc', '')
                return timestamp
            elif col == 2:
                size_kb = os.path.getsize(backup) // 1024
                return f"{size_kb} KB"
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class BackupView(QWidget):
    def __init__(self):
        super().__init__()
        self.backup_path = "backups"
        os.makedirs(self.backup_path, exist_ok=True)
        self.setup_ui()
        self.load_backup_list()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("💾 مدیریت بک‌آپ و بازیابی")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Buttons
        btn_layout = QHBoxLayout()
        
        self.backup_btn = QPushButton("📦 ایجاد بک‌آپ جدید")
        self.backup_btn.clicked.connect(self.create_backup)
        btn_layout.addWidget(self.backup_btn)

        self.restore_btn = QPushButton("🔄 بازیابی از فایل")
        self.restore_btn.clicked.connect(self.restore_backup)
        btn_layout.addWidget(self.restore_btn)

        layout.addLayout(btn_layout)

        # Encryption Option
        encrypt_layout = QHBoxLayout()
        self.encrypt_check = QCheckBox("🔐 رمزنگاری بک‌آپ (با کلید)")
        encrypt_layout.addWidget(self.encrypt_check)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("کلید رمزنگاری (32 کاراکتر)")
        self.key_input.setEnabled(False)
        encrypt_layout.addWidget(self.key_input)

        self.encrypt_check.stateChanged.connect(lambda: self.key_input.setEnabled(self.encrypt_check.isChecked()))
        layout.addLayout(encrypt_layout)

        # Backup List
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        layout.addWidget(self.table)

        # Refresh Button
        refresh_btn = QPushButton("🔄 تازه‌سازی لیست")
        refresh_btn.clicked.connect(self.load_backup_list)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)

    def load_backup_list(self):
        backup_files = [
            os.path.join(self.backup_path, f)
            for f in os.listdir(self.backup_path)
            if f.endswith(('.zip', '.enc'))
        ]
        backup_files.sort(key=os.path.getmtime, reverse=True)
        self.model = BackupTableModel(backup_files)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

    def create_backup(self):
        encrypt = self.encrypt_check.isChecked()
        key = self.key_input.text().strip().encode() if encrypt else None

        if encrypt and len(key) != 32:
            QMessageBox.warning(self, "خطا", "کلید رمزنگاری باید 32 کاراکتر باشد.")
            return

        try:
            backup_file = BackupService.create_backup(
                backup_path=self.backup_path,
                encrypt=encrypt,
                key=key if encrypt else None
            )
            QMessageBox.information(self, "موفق", f"بک‌آپ با موفقیت ایجاد شد:\n{backup_file}")
            self.load_backup_list()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد بک‌آپ: {str(e)}")

    def restore_backup(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک فایل بک‌آپ را انتخاب کنید.")
            return

        row = selected[0].row()
        backup_file = self.model.backups[row]

        encrypt = backup_file.endswith('.enc')
        key = None
        if encrypt:
            key, ok = QInputDialog.getText(self, "کلید رمزنگاری", "کلید را وارد کنید:")
            if not ok or len(key.encode()) != 32:
                QMessageBox.warning(self, "خطا", "کلید باید 32 کاراکتر باشد.")
                return
            key = key.encode()

        reply = QMessageBox.question(
            self,
            "تأیید بازیابی",
            f"آیا از بازیابی از فایل زیر اطمینان دارید؟\n{os.path.basename(backup_file)}\n\n⚠️ تمام داده‌های فعلی جایگزین خواهند شد!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                RestoreService.restore_backup(backup_file, encrypt=encrypt, key=key if encrypt else None)
                QMessageBox.information(self, "موفق", "بازیابی با موفقیت انجام شد.\nبرنامه را مجدداً راه‌اندازی کنید.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در بازیابی: {str(e)}")