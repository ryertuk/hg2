# tests/test_stock_model.py
import pytest
from app.database import SessionLocal, init_db
from app.models.unit import Unit
from app.models.item import Item
from app.models.stock_movement import StockMovement
from app.services.stock_service import StockService
from app.utils.code_generator import generate_sku

@pytest.fixture(scope="module")
def db():
    init_db()
    session = SessionLocal()
    yield session
    session.close()

def test_stock_movement_creation(db):
    # ایجاد واحد و کالا
    unit = Unit(code="UNT-PCS", name="عدد", factor_to_base=1.0)
    db.add(unit)
    db.commit()

    item = Item(sku=generate_sku(), name="پیچ تست", unit_type="count", base_unit_id=unit.id, active=True)
    db.add(item)
    db.commit()

    # افزودن تحرک ورودی
    movement = StockMovement(
        item_id=item.id,
        qty=100.0,
        unit_id=unit.id,
        movement_type="purchase_in",
        cost_per_unit=5000,  # 5 هزار ریال
        total_cost=500000
    )
    db.add(movement)
    db.commit()

    assert movement.id is not None
    assert movement.total_cost == 500000

def test_stock_availability_validation(db):
    service = StockService()
    
    # فرض کنید کالایی با ID=1 وجود دارد و 100 واحد موجودی دارد
    # ابتدا 100 واحد وارد می‌کنیم
    service.add_movement({
        "item_id": 1,
        "qty": 100.0,
        "unit_id": 1,
        "movement_type": "purchase_in",
        "cost_per_unit": 10000,
        "reference_type": "manual",
        "reference_id": None
    })

    # سپس 50 واحد خارج می‌کنیم — باید موفقیت‌آمیز باشد
    service.add_movement({
        "item_id": 1,
        "qty": -50.0,
        "unit_id": 1,
        "movement_type": "sale_out",
        "cost_per_unit": 15000,
        "reference_type": "manual",
        "reference_id": None
    })

    # سپس 60 واحد خارج می‌کنیم — باید خطا بدهد
    with pytest.raises(ValueError, match="موجودی کافی نیست"):
        service.add_movement({
            "item_id": 1,
            "qty": -60.0,
            "unit_id": 1,
            "movement_type": "sale_out",
            "cost_per_unit": 15000,
            "reference_type": "manual",
            "reference_id": None
        })