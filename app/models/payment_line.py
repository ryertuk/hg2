# app/models/payment_line.py
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.models.base import BaseModel

class PaymentLine(BaseModel):
    __tablename__ = 'payment_lines'

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=True)
    check_id = Column(Integer, ForeignKey('checks.id'), nullable=True)
    amount = Column(Numeric(18, 0), nullable=False)  # ریال
    account_id = Column(Integer, ForeignKey('ledger_accounts.id'), nullable=False)  # برای مرحله 6
    notes = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<PaymentLine payment={self.payment_id} amount={self.amount:,.0f}>"