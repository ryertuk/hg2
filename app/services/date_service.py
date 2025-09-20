# app/services/date_service.py
from datetime import datetime
import jdatetime

def gregorian_to_jalali(gregorian_date) -> str:
    """تبدیل datetime میلادی به رشته تاریخ شمسی — YYYY/MM/DD"""
    if not gregorian_date:
        return ""
    jdate = jdatetime.date.fromgregorian(date=gregorian_date)
    return jdate.strftime("%Y/%m/%d")

def jalali_to_gregorian(jalali_str: str) -> datetime:
    """تبدیل رشته تاریخ شمسی (YYYY/MM/DD) به datetime میلادی"""
    if not jalali_str:
        return None
    j_year, j_month, j_day = map(int, jalali_str.split('/'))
    jdate = jdatetime.date(j_year, j_month, j_day)
    gregorian_date = jdate.togregorian()
    return datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day)