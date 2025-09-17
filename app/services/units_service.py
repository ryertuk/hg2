from app.utils.db import SessionLocal
from app.models.units import Unit

def get_all_units():
    with SessionLocal() as session:
        return session.query(Unit).all()

def create_unit(data: dict):
    with SessionLocal.begin() as session:
        unit = Unit(**data)
        session.add(unit)

def update_unit(id: int, data: dict):
    with SessionLocal.begin() as session:
        unit = session.query(Unit).filter(Unit.id == id).first()
        for k, v in data.items():
            setattr(unit, k, v)