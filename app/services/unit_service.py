# app/services/unit_service.py
from app.database import SessionLocal
from app.models.unit import Unit

class UnitService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_units(self):
        return self.db.query(Unit).all()

    def create_unit(self, data):
        unit = Unit(**data)
        self.db.add(unit)
        self.db.commit()
        self.db.refresh(unit)
        return unit

    def update_unit(self, unit_id, data):
        unit = self.db.query(Unit).filter(Unit.id == unit_id).first()
        if not unit:
            raise Exception("واحد یافت نشد.")
        for key, value in data.items():
            setattr(unit, key, value)
        self.db.commit()
        self.db.refresh(unit)
        return unit

    def delete_unit(self, unit_id):
        unit = self.db.query(Unit).filter(Unit.id == unit_id).first()
        if not unit:
            raise Exception("واحد یافت نشد.")
        self.db.delete(unit)
        self.db.commit()

    # ✅ متد جدید — افزوده شد
    def get_unit_by_id(self, unit_id: int):
        return self.db.query(Unit).filter(Unit.id == unit_id).first()