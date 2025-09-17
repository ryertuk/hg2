from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from pydantic import BaseModel, field_validator
from app.models.base import Base, TimestampMixin

class Item(Base, TimestampMixin):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String, nullable=False, index=True)
    unit_type = Column(String)  # 'count'|'measure'
    base_unit_id = Column(Integer, ForeignKey('units.id'))
    length = Column(Numeric(18, 4), nullable=True)  # برای متراژی
    width = Column(Numeric(18, 4), nullable=True)
    active = Column(Boolean, default=True)
    barcode = Column(String, unique=True)
    category_id = Column(Integer, nullable=True)  # FK به categories در مراحل بعدی

    # Relationships
    base_unit = relationship("Unit", back_populates="items")

    @validates('unit_type')
    def validate_unit_type(self, key, value):
        if value not in ['count', 'measure']:
            raise ValueError("Unit type must be 'count' or 'measure'")
        return value

Index('idx_items_sku', 'sku')
Index('idx_items_name', 'name')

class ItemPydantic(BaseModel):
    sku: str
    name: str
    unit_type: str
    base_unit_id: int
    length: float | None = None
    width: float | None = None
    active: bool = True
    barcode: str | None = None

    @field_validator('unit_type')
    @classmethod
    def unit_type_valid(cls, v: str) -> str:
        if v not in ['count', 'measure']:
            raise ValueError("Unit type must be 'count' or 'measure'")
        return v