# app/models/stock_val_period.py
from sqlalchemy import Column, Integer, Numeric, String, ForeignKey
from app.models.base import BaseModel

class StockValPeriod(BaseModel):
    __tablename__ = 'stock_val_periods'

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False, index=True)
    period = Column(String(7), nullable=False, index=True)  # YYYY-MM
    avg_cost = Column(Numeric(18, 0), nullable=False)      # میانگین موزون — ریال
    total_qty = Column(Numeric(18, 4), nullable=False)
    total_value = Column(Numeric(18, 0), nullable=False)    # ریال

    def __repr__(self):
        return f"<StockValPeriod {self.item_id} {self.period} avg={self.avg_cost}>"