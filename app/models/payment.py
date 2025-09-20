# app/models/payment.py
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from app.models.base import BaseModel

class Payment(BaseModel):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, index=True)
    payment_type = Column(String(20), nullable=False)  # 'receipt' | 'payment'
    party_id = Column(Integer, ForeignKey('parties.id'), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 0), nullable=False)  # ریال
    method = Column(String(50), nullable=False)  # 'cash'|'bank_transfer'|'check'|'mixed'
    status = Column(String(20), nullable=False, default="pending")  # pending, completed, cancelled
    reference = Column(String(100), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    notes = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<Payment {self.payment_type} - {self.amount:,.0f}>"