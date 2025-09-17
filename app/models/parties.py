from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Index
from sqlalchemy.orm import validates, relationship
from pydantic import BaseModel, field_validator
from app.models.base import Base, TimestampMixin

class Party(Base, TimestampMixin):
    __tablename__ = 'parties'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    party_type = Column(String)  # 'customer'|'supplier'|'both'
    tax_id = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    credit_limit = Column(Numeric(18, 2), default=0.0)
    is_active = Column(Boolean, default=True)

    # Relationships (برای مراحل بعدی)
    invoices = relationship("Invoice", back_populates="party")
    payments = relationship("Payment", back_populates="party")

    @validates('credit_limit')
    def validate_credit_limit(self, key, value):
        if value < 0:
            raise ValueError("Credit limit must be >= 0")
        return value

    Index('idx_parties_code', 'code')

# Pydantic model برای validation خارجی (e.g., API/UI)
class PartyPydantic(BaseModel):
    code: str
    name: str
    party_type: str
    credit_limit: float

    @field_validator('credit_limit')
    @classmethod
    def credit_limit_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError('Credit limit must be positive')
        return v