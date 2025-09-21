# app/backup/restore_service.py
import zipfile
import os
import shutil
from app.utils.crypto import decrypt_file

class RestoreService:
    @staticmethod
    def restore_backup(backup_file, encrypt=False, key=None):
        """بازیابی بک‌آپ — جایگزینی دیتابیس و پیوست‌ها"""
        if encrypt and key:
            backup_file = decrypt_file(backup_file, key)

        with zipfile.ZipFile(backup_file, 'r') as zipf:
            for member in zipf.namelist():
                # بازیابی دیتابیس
                if member.endswith(".db"):
                    zipf.extract(member, ".")
                # بازیابی پیوست‌ها
                elif member.startswith("storage/attachments/"):
                    zipf.extract(member, ".")

        return True