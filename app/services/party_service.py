# app/services/party_service.py
from app.database import SessionLocal
from app.models.party import Party

class PartyService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_parties(self):
        return self.db.query(Party).all()

    def create_party(self, data):
        party = Party(**data)
        self.db.add(party)
        self.db.commit()
        self.db.refresh(party)
        return party

    def update_party(self, party_id, data):
        party = self.db.query(Party).filter(Party.id == party_id).first()
        if not party:
            raise Exception("طرف‌حساب یافت نشد.")
        for key, value in data.items():
            setattr(party, key, value)
        self.db.commit()
        self.db.refresh(party)
        return party

    def delete_party(self, party_id):
        party = self.db.query(Party).filter(Party.id == party_id).first()
        if not party:
            raise Exception("طرف‌حساب یافت نشد.")
        self.db.delete(party)
        self.db.commit()
        
    # در کلاس PartyService — افزودن این متد
    def get_party_by_id(self, party_id: int):
        return self.db.query(Party).filter(Party.id == party_id).first()