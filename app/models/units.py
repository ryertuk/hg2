from sqlalchemy import Column, Integer, String, Numeric, Index
from sqlalchemy.orm import validates, relationship
from pydantic import BaseModel, field_validator
from app.models.base import Base, TimestampMixin

class Unit(Base, TimestampMixin):
    __tablename__ = 'units'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True)  # e.g., 'pcs', 'm', 'm2'
    name = Column(String, nullable=False)
    factor_to_base = Column(Numeric(18, 4), default=1.0)  # ضریب تبدیل به واحد پایه

    # Relationships
    items = relationship("Item", back_populates="base_unit")

    @validates('factor_to_base')
    def validate_factor(self, key, value):
        if value <= 0:
            raise ValueError("Factor to base must be > 0")
        return value

Index('idx_units_code', 'code')

class UnitPydantic(BaseModel):
    code: str
    name: str
    factor_to_base: float

    @field_validator('factor_to_base')
    @classmethod
    def factor_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Factor to base must be positive')
        return v