# app/services/stock_service.py
from app.database import SessionLocal
from app.models.stock_movement import StockMovement
from app.models.item import Item
from app.utils.validators import validate_stock_availability

class StockService:
    def __init__(self):
        self.db = SessionLocal()

    def get_current_stock(self, item_id: int) -> float:
        """محاسبه موجودی فعلی کالا"""
        movements = self.db.query(StockMovement).filter(StockMovement.item_id == item_id).all()
        return sum(m.qty for m in movements)

    def add_movement(self, data: dict):
        """افزودن تحرک انبار — با اعتبارسنجی برای خروجی‌ها"""
        item_id = data['item_id']
        qty = data['qty']

        # اگر خروجی است — اعتبارسنجی موجودی
        if qty < 0:
            current_stock = self.get_current_stock(item_id)
            if abs(qty) > current_stock:
                raise ValueError(f"موجودی کافی نیست. موجودی فعلی: {current_stock}")

        movement = StockMovement(**data)
        movement.total_cost = int(movement.qty * movement.cost_per_unit)  # محاسبه خودکار
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return movement

    def get_movements_by_item(self, item_id: int):
        return self.db.query(StockMovement).filter(StockMovement.item_id == item_id).order_by(StockMovement.created_at).all()