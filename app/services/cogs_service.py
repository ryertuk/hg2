# app/services/cogs_service.py
from app.database import SessionLocal
from app.models.stock_val_period import StockValPeriod
from app.models.invoice_line import InvoiceLine

class COGSService:
    def __init__(self):
        self.db = SessionLocal()

    def calculate_cogs_for_invoice_line(self, invoice_line_id: int) -> int:
        """محاسبه بهای تمام‌شده برای یک خط فاکتور — با آخرین avg_cost"""
        line = self.db.query(InvoiceLine).filter(InvoiceLine.id == invoice_line_id).first()
        if not line:
            raise Exception("خط فاکتور یافت نشد.")

        # آخرین دوره مالی برای این کالا
        last_valuation = self.db.query(StockValPeriod).filter(
            StockValPeriod.item_id == line.item_id
        ).order_by(StockValPeriod.period.desc()).first()

        if not last_valuation:
            return 0

        # COGS = میانگین موزون × تعداد فروخته شده
        cogs = int(last_valuation.avg_cost * line.qty)
        return cogs