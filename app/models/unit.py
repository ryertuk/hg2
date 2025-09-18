# app/models/unit.py
from sqlalchemy import Column, Integer, String, Numeric
from app.models.base import BaseModel

class Unit(BaseModel):
    __tablename__ = 'units'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)  # مثلاً: UNT-7X9K
    name = Column(String(50), nullable=False)  # مثلاً: متر مربع
    factor_to_base = Column(Numeric(18, 4), default=1.0)  # ضریب تبدیل به واحد پایه

    def __repr__(self):
        return f"<Unit {self.name} ({self.code})>"