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

if __name__ == "__main__":
    init_db()
    seed_data()