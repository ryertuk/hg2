from app.utils.db import SessionLocal
from app.models.parties import Party, PartyPydantic

def get_all_parties():
    with SessionLocal() as session:
        return session.query(Party).all()

def create_party(data: dict):
    with SessionLocal.begin() as session:
        party = Party(**data)
        session.add(party)

def update_party(id: int, data: dict):
    with SessionLocal.begin() as session:
        party = session.query(Party).filter(Party.id == id).first()
        for k, v in data.items():
            setattr(party, k, v)