# app/models/stock_movement.py
from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, CheckConstraint
from app.models.base import BaseModel
from sqlalchemy.sql import func  # ✅ این خط اضافه شود

class StockMovement(BaseModel):
    __tablename__ = 'stock_movements'

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False, index=True)
    qty = Column(Numeric(18, 4), nullable=False)  # + برای ورودی، - برای خروجی
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=False)
    movement_type = Column(String(50), nullable=False)  # purchase_in, sale_out, adjustment, return_in, return_out
    reference_type = Column(String(50), nullable=True)  # 'invoice', 'adjustment', etc.
    reference_id = Column(Integer, nullable=True)      # ID مرجع (فاکتور، تعدیل و ...)
    cost_per_unit = Column(Numeric(18, 0), nullable=False)  # قیمت به ریال — بدون اعشار
    total_cost = Column(Numeric(18, 0), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint('qty != 0', name='check_qty_nonzero'),
    )

    def __repr__(self):
        sign = "+" if self.qty > 0 else ""
        return f"<StockMovement item={self.item_id} {sign}{self.qty} type={self.movement_type}>"