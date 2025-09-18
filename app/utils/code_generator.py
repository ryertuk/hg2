# app/utils/code_generator.py
import uuid
from datetime import datetime

def generate_sku():
    """تولید کد کالا منحصربه‌فرد — مثلاً: SKU-20250405-AB3F"""
    prefix = "SKU"
    date_part = datetime.now().strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:4].upper()
    return f"{prefix}-{date_part}-{unique_part}"

def generate_unit_code():
    """تولید کد واحد — مثلاً: UNT-7X9K"""
    prefix = "UNT"
    unique_part = uuid.uuid4().hex[:4].upper()
    return f"{prefix}-{unique_part}"

def generate_serial(prefix="INV"):
    """تولید سریال — مثلاً: INV-2025-0001"""
    year = datetime.now().year
    # در عمل: آخرین شماره از دیتابیس گرفته می‌شود — اینجا ساده‌سازی شده
    last_num = 1  # در عمل: SELECT MAX(number) FROM invoices WHERE serial LIKE 'INV-2025%'
    return f"{prefix}-{year}-{last_num:04d}"