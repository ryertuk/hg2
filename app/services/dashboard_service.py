# app/services/dashboard_service.py
from app.database import SessionLocal
from app.models.item import Item
from app.models.party import Party
from app.models.invoice import Invoice
from app.models.check import Check
from app.models.stock_val_period import StockValPeriod
from datetime import date
from sqlalchemy import func

class DashboardService:
    def __init__(self):
        self.db = SessionLocal()

    def get_item_count(self):
        return self.db.query(Item).count()

    def get_party_count(self):
        return self.db.query(Party).count()

    def get_total_inventory_value(self):
        total = self.db.query(StockValPeriod).with_entities(
            func.sum(StockValPeriod.total_value)
        ).scalar()
        return total or 0

    def get_today_invoices_count(self):
        today = date.today()
        return self.db.query(Invoice).filter(Invoice.date_gregorian == today).count()

    def get_active_checks_count(self):
        return self.db.query(Check).filter(Check.status.in_(['in_hand', 'deposited'])).count()

    def get_total_receivable_payable(self):
        # ساده‌سازی — در عمل باید از جدول حسابداری محاسبه شود
        return 0