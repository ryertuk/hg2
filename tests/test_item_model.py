# tests/test_item_model.py
import pytest
from app.database import SessionLocal, init_db
from app.models.unit import Unit
from app.models.item import Item
from app.utils.code_generator import generate_sku

@pytest.fixture(scope="module")
def db():
    init_db()
    session = SessionLocal()
    yield session
    session.close()

def test_item_creation(db):
    # ابتدا یک واحد ایجاد کنید
    unit = Unit(code="UNT-TEST", name="تست", factor_to_base=1.0)
    db.add(unit)
    db.commit()

    item = Item(
        sku=generate_sku(),
        name="کالای تستی",
        unit_type="count",
        base_unit_id=unit.id,
        active=True
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    assert item.id is not None
    assert item.name == "کالای تستی"
    assert item.base_unit_id == unit.id