import pytest
from app.models.parties import Party, PartyPydantic
from app.utils.db import SessionLocal, engine
from app.services.parties_service import create_party, get_all_parties

@pytest.fixture
def test_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

def test_create_party(test_session):
    data = {'code': 'C001', 'name': 'Customer1', 'party_type': 'customer', 'credit_limit': 1000.0}
    create_party(data)
    parties = get_all_parties()
    assert len(parties) == 1
    assert parties[0].code == 'C001'

def test_validation_credit_limit():
    with pytest.raises(ValueError):
        PartyPydantic(code='C001', name='Test', party_type='customer', credit_limit=-1)

def test_db_validation(test_session):
    party = Party(code='C001', name='Test', party_type='customer', credit_limit=-1)
    with pytest.raises(ValueError):
        test_session.add(party)
        test_session.commit()