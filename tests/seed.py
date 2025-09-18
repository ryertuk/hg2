import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models.role import Role
from app.models.user import User
from app.models.party import Party


def seed_data():
    db = SessionLocal()

    # Roles
    admin_role = Role(name="admin", permissions={"party.create": True, "party.edit": True})
    user_role = Role(name="user", permissions={"party.view": True})
    db.add_all([admin_role, user_role])
    db.commit()

    # Users
    admin = User(username="admin", full_name="مدیر سیستم", role_id=1)
    admin.set_password("admin123")
    user = User(username="user", full_name="کاربر عادی", role_id=2)
    user.set_password("user123")
    db.add_all([admin, user])
    db.commit()

    # Parties
    parties = [
        Party(code="C001", name="فروشگاه آفتاب", party_type="customer", credit_limit=5000000.00, phone="021-12345678"),
        Party(code="S001", name="شرکت صنایع پلاستیک", party_type="supplier", credit_limit=10000000.00, phone="021-87654321"),
        Party(code="B001", name="فروشگاه همه‌کاره", party_type="both", credit_limit=2000000.00, phone="021-11223344"),
    ]
    db.add_all(parties)
    db.commit()
    print("✅ داده‌های نمونه با موفقیت افزوده شدند.")
# tests/seed.py — بخش جدید در انتهای فایل
def seed_units_and_items(db):
    # Units
    units = [
        Unit(code="UNT-PCS", name="عدد", factor_to_base=1.0),
        Unit(code="UNT-MTR", name="متر", factor_to_base=1.0),
        Unit(code="UNT-M2", name="متر مربع", factor_to_base=1.0),
    ]
    db.add_all(units)
    db.commit()

    # Items
    from app.utils.code_generator import generate_sku
    items = [
        Item(sku=generate_sku(), name="پیچ 4 میلی", unit_type="count", base_unit_id=1, active=True),
        Item(sku=generate_sku(), name="شیلنگ 1 اینچ", unit_type="measure", base_unit_id=2, length=1.0, width=None, active=True),
        Item(sku=generate_sku(), name="کاشی سرامیک", unit_type="measure", base_unit_id=3, length=0.3, width=0.3, active=True),
    ]
    db.add_all(items)
    db.commit()
    print("✅ واحدها و کالاهای نمونه افزوده شدند.")

# در انتهای تابع seed_data() اضافه کنید:
# seed_units_and_items(db)

if __name__ == "__main__":
    init_db()
    seed_data()
    seed_units_and_items(db)

