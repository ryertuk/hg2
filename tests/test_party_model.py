# tests/test_party_model.py
import pytest
from app.database import SessionLocal, init_db
from app.models.party import Party

@pytest.fixture(scope="module")
def db():
    init_db()
    session = SessionLocal()
    yield session
    session.close()

def test_party_creation(db):
    party = Party(
        code="CUST001",
        name="مشتری نمونه",
        party_type="customer",
        credit_limit=1000000.00
    )
    db.add(party)
    db.commit()
    db.refresh(party)
    assert party.id is not None
    assert party.code == "CUST001"
    assert party.name == "مشتری نمونه"

def test_credit_limit_constraint(db):
    party = Party(
        code="CUST002",
        name="مشتری با اعتبار منفی",
        party_type="customer",
        credit_limit=-100.00
    )
    db.add(party)
    with pytest.raises(Exception):
        db.commit()