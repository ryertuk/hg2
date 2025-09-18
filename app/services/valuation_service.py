# app/services/valuation_service.py
from app.database import SessionLocal
from app.models.stock_val_period import StockValPeriod
from app.models.stock_movement import StockMovement
from datetime import datetime

class ValuationService:
    def __init__(self):
        self.db = SessionLocal()

    def calculate_weighted_average(self, item_id: int, year: int, month: int) -> dict:
        """محاسبه میانگین موزون برای یک کالا در یک دوره"""
        period = f"{year}-{month:02d}"
        
        # تمام تحرکات در این دوره
        movements = self.db.query(StockMovement).filter(
            StockMovement.item_id == item_id,
            StockMovement.created_at >= f"{year}-{month:02d}-01",
            StockMovement.created_at < f"{year}-{month+1:02d}-01" if month < 12 else f"{year+1}-01-01"
        ).order_by(StockMovement.created_at).all()

        if not movements:
            return None

        total_qty = 0.0
        total_value = 0

        for m in movements:
            total_qty += m.qty
            total_value += m.total_cost  # cost_per_unit * qty — از قبل محاسبه شده

        avg_cost = int(total_value / total_qty) if total_qty != 0 else 0

        # ذخیره در جدول دوره‌ها
        existing = self.db.query(StockValPeriod).filter(
            StockValPeriod.item_id == item_id,
            StockValPeriod.period == period
        ).first()

        if existing:
            existing.avg_cost = avg_cost
            existing.total_qty = total_qty
            existing.total_value = total_value
        else:
            period_record = StockValPeriod(
                item_id=item_id,
                period=period,
                avg_cost=avg_cost,
                total_qty=total_qty,
                total_value=total_value
            )
            self.db.add(period_record)

        self.db.commit()
        return {"avg_cost": avg_cost, "total_qty": total_qty, "total_value": total_value}