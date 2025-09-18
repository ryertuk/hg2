# app/models/party.py
from sqlalchemy import Column, Integer, String, Boolean, Numeric, CheckConstraint
from app.models.base import BaseModel

class Party(BaseModel):
    __tablename__ = 'parties'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    party_type = Column(String(20), nullable=False)  # 'customer', 'supplier', 'both'
    tax_id = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    credit_limit = Column(Numeric(18, 2), nullable=True)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint('credit_limit >= 0', name='check_credit_limit_positive'),
    )

    def __repr__(self):
        return f"<Party {self.name} ({self.party_type})>"