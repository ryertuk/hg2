# tests/test_invoice_model.py
import pytest
from app.database import SessionLocal, init_db
from app.models.party import Party
from app.models.item import Item
from app.models.unit import Unit
from app.services.invoice_service import InvoiceService
from app.utils.code_generator import generate_sku

@pytest.fixture(scope="module")
def db():
    init_db()
    session = SessionLocal()
    yield session
    session.close()

def test_invoice_creation_with_measure_item(db):
    # ایجاد واحد و کالای اندازه‌ای
    unit = Unit(code="UNT-M2", name="متر مربع", factor_to_base=1.0)
    db.add(unit)
    db.commit()

    item = Item(
        sku=generate_sku(),
        name="کاغذ دیواری",
        unit_type="measure",
        base_unit_id=unit.id,
        length=10.0,  # 10 متر طول
        width=1.0,    # 1 متر عرض
        active=True
    )
    db.add(item)
    db.commit()

    # ایجاد فاکتور فروش
    service = InvoiceService()
    invoice_data = {
        "invoice_type": "sale",
        "serial": "INV",
        "number": 1,
        "serial_full": "INV-1404-0001",
        "party_id": 1,  # فرض: مشتری با ID=1 وجود دارد
        "date_jalali": "1404/01/15",
        "created_by": 1,
        "tax": 0,
        "discount": 0,
        "shipping": 0
    }
    lines_data = [
        {
            "item_id": item.id,
            "qty": 5.0,          # 5 رول
            "unit_id": unit.id,
            "unit_price": 20000, # 20 هزار ریال به ازای هر متر مربع
            "discount": 0,
            "tax": 0,
            "notes": "کاغذ دیواری مرغوب"
        }
    ]

    invoice = service.create_invoice(invoice_data, lines_data)
    
    assert invoice.id is not None
    assert len(invoice.lines) == 1
    line = invoice.lines[0]
    # 5 رول × (10m × 1m) × 20,000 ریال = 1,000,000 ریال
    assert line.line_total == 1000000
    assert invoice.total == 1000000