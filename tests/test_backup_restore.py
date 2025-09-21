# tests/test_backup_restore.py
import pytest
import os
from app.backup.backup_service import BackupService
from app.backup.restore_service import RestoreService

def test_backup_creation():
    backup_file = BackupService.create_backup(backup_path="test_backups")
    assert os.path.exists(backup_file)
    assert backup_file.endswith(".zip")
    # پاک‌سازی
    os.remove(backup_file)
    os.rmdir("test_backups")

def test_backup_with_encryption():
    from app.utils.crypto import generate_key
    key = generate_key()
    backup_file = BackupService.create_backup(backup_path="test_backups", encrypt=True, key=key)
    assert os.path.exists(backup_file)
    assert backup_file.endswith(".enc")
    # بازیابی و بررسی
    restored = RestoreService.restore_backup(backup_file, encrypt=True, key=key)
    assert restored is True
    # پاک‌سازی
    os.remove(backup_file.replace('.enc', '.zip'))
    os.remove(backup_file)
    os.rmdir("test_backups")