# tests/seed.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models.role import Role
from app.models.user import User
from app.models.party import Party
from app.models.unit import Unit
from app.models.item import Item
from app.utils.code_generator import generate_sku



def seed_data():
    db = SessionLocal()

    # ============================
    # Seed Roles — با بررسی وجود قبلی
    # ============================
    def get_or_create_role(name, permissions):
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            role = Role(name=name, permissions=permissions)
            db.add(role)
            db.flush()  # برای دریافت id قبل از commit
        return role

    admin_role = get_or_create_role("admin", {"party.create": True, "party.edit": True})
    user_role = get_or_create_role("user", {"party.view": True})

    # ============================
    # Seed Users — با بررسی وجود قبلی
    # ============================
    def get_or_create_user(username, full_name, role_id, password):
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(username=username, full_name=full_name, role_id=role_id)
            user.set_password(password)
            db.add(user)
            db.flush()
        return user

    admin = get_or_create_user("admin", "مدیر سیستم", admin_role.id, "admin123")
    user = get_or_create_user("user", "کاربر عادی", user_role.id, "user123")

    # ============================
    # Seed Parties — با بررسی وجود قبلی
    # ============================
    def get_or_create_party(code, **kwargs):
        party = db.query(Party).filter(Party.code == code).first()
        if not party:
            party = Party(code=code, **kwargs)
            db.add(party)
            db.flush()
        return party

    parties = [
        get_or_create_party("C001", name="فروشگاه آفتاب", party_type="customer", credit_limit=5000000.00, phone="021-12345678"),
        get_or_create_party("S001", name="شرکت صنایع پلاستیک", party_type="supplier", credit_limit=10000000.00, phone="021-87654321"),
        get_or_create_party("B001", name="فروشگاه همه‌کاره", party_type="both", credit_limit=2000000.00, phone="021-11223344"),
    ]

    # ============================
    # Seed Units — با بررسی وجود قبلی
    # ============================
    def get_or_create_unit(code, **kwargs):
        unit = db.query(Unit).filter(Unit.code == code).first()
        if not unit:
            unit = Unit(code=code, **kwargs)
            db.add(unit)
            db.flush()
        return unit

    units = [
        get_or_create_unit("UNT-PCS", name="عدد", factor_to_base=1.0),
        get_or_create_unit("UNT-MTR", name="متر", factor_to_base=1.0),
        get_or_create_unit("UNT-M2", name="متر مربع", factor_to_base=1.0),
    ]

    # ============================
    # Seed Items — با بررسی وجود قبلی
    # ============================
    def get_or_create_item(sku, **kwargs):
        item = db.query(Item).filter(Item.sku == sku).first()
        if not item:
            item = Item(sku=sku, **kwargs)
            db.add(item)
            db.flush()
        return item

    from app.utils.code_generator import generate_sku
    # برای جلوگیری از تکرار SKU در تست‌های متوالی، از کدهای ثابت استفاده می‌کنیم
    # یا اگر می‌خواهید هر بار جدید باشد — قبل از seed دیتابیس را پاک کنید
    skus = ["SKU-FIXED-001", "SKU-FIXED-002", "SKU-FIXED-003"]
    items = [
        get_or_create_item(skus[0], name="پیچ 4 میلی", unit_type="count", base_unit_id=units[0].id, active=True),
        get_or_create_item(skus[1], name="شیلنگ 1 اینچ", unit_type="measure", base_unit_id=units[1].id, length=1.0, width=None, active=True),
        get_or_create_item(skus[2], name="کاشی سرامیک", unit_type="measure", base_unit_id=units[2].id, length=0.3, width=0.3, active=True),
    ]

    db.commit()
    print("✅ داده‌های نمونه با موفقیت افزوده یا به‌روزرسانی شدند.")

    from app.models.stock_movement import StockMovement
    # فرض: 3 کالا وجود دارد — با IDهای 1,2,3
    movements = [
        StockMovement(item_id=1, qty=100.0, unit_id=1, movement_type="purchase_in", cost_per_unit=10000, reference_type="seed", reference_id=None),
        StockMovement(item_id=1, qty=-20.0, unit_id=1, movement_type="sale_out", cost_per_unit=15000, reference_type="seed", reference_id=None),
        StockMovement(item_id=2, qty=50.0, unit_id=2, movement_type="purchase_in", cost_per_unit=50000, reference_type="seed", reference_id=None),
        StockMovement(item_id=3, qty=200.0, unit_id=3, movement_type="purchase_in", cost_per_unit=20000, reference_type="seed", reference_id=None),
    ]

    db.commit()
    print("✅ تحرکات انبار نمونه افزوده شدند.")

if __name__ == "__main__":
    init_db()
    seed_data()
