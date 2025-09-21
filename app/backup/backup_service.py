# app/backup/backup_service.py
import shutil
import zipfile
import os
import datetime
from app.database import DATABASE_URL
from app.utils.crypto import encrypt_file

class BackupService:
    @staticmethod
    def create_backup(backup_path="backups", encrypt=False, key=None):
        """ایجاد بک‌آپ از دیتابیس و پوشه پیوست‌ها"""
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_path, f"backup_{timestamp}.zip")

        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # بک‌آپ دیتابیس
            db_path = DATABASE_URL.replace("sqlite:///", "")
            if os.path.exists(db_path):
                zipf.write(db_path, os.path.basename(db_path))

            # بک‌آپ پیوست‌ها (اگر وجود دارد)
            attachments_path = "storage/attachments"
            if os.path.exists(attachments_path):
                for root, dirs, files in os.walk(attachments_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=".")
                        zipf.write(file_path, arcname)

        # رمزنگاری اختیاری
        if encrypt and key:
            encrypted_file = encrypt_file(backup_file, key)
            os.remove(backup_file)  # حذف فایل اصلی
            backup_file = encrypted_file

        return backup_file