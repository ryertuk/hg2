from app.utils.db import SessionLocal
from app.models.items import Item

def get_all_items():
    with SessionLocal() as session:
        return session.query(Item).all()

def create_item(data: dict):
    with SessionLocal.begin() as session:
        item = Item(**data)
        session.add(item)

def update_item(id: int, data: dict):
    with SessionLocal.begin() as session:
        item = session.query(Item).filter(Item.id == id).first()
        for k, v in data.items():
            setattr(item, k, v)

# تابع نمونه برای تبدیل واحدها (برای استفاده در مراحل بعدی انبار)
def convert_qty_to_base(item_id: int, qty: float, unit_id: int) -> float:
    with SessionLocal() as session:
        item = session.query(Item).filter(Item.id == item_id).first()
        unit = session.query(Unit).filter(Unit.id == unit_id).first()
        if item.base_unit_id != unit.id:  # اگر واحد متفاوت، تبدیل کن
            # فرض: همه واحدها به base تبدیل می‌شن
            return qty * unit.factor_to_base
        return qty