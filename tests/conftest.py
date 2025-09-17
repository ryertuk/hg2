import pytest
from app.utils.db import engine, SessionLocal
from app.models.base import Base  # import جدید

@pytest.fixture(scope="function")
def test_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    Base.metadata.create_all(bind=engine)  # ایجاد جدول‌ها برای تست
    yield session
    session.close()
    transaction.rollback()
    connection.close()