# app/models/item.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from app.models.base import BaseModel

class Item(BaseModel):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)  # کد کالا — خودکار
    name = Column(String(200), nullable=False, index=True)
    unit_type = Column(String(20), nullable=False)  # 'count' | 'measure'
    base_unit_id = Column(Integer, ForeignKey('units.id'), nullable=False)  # واحد پایه
    length = Column(Numeric(18, 4), nullable=True)  # برای کالاهای اندازه‌دار
    width = Column(Numeric(18, 4), nullable=True)
    active = Column(Boolean, default=True)
    barcode = Column(String(100), nullable=True, unique=True)
    category_id = Column(Integer, nullable=True)  # FK → categories.id (در آینده)
    # ✅ فیلدهای جدید — قیمت آخرین خرید و فروش
    last_purchase_price = Column(Numeric(18, 0), default=0)  # ریال
    last_sale_price = Column(Numeric(18, 0), default=0)      # ریال
    
    def __repr__(self):
        return f"<Item {self.name} ({self.sku})>"