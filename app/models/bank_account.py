# app/models/bank_account.py
from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.base import BaseModel

class BankAccount(BaseModel):
    __tablename__ = 'bank_accounts'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # نام حساب — مثلاً: "حساب جاری ملی"
    bank_name = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=False)
    ledger_account_id = Column(Integer, ForeignKey('ledger_accounts.id'), nullable=False)  # برای مرحله 6
    currency = Column(String(3), default="IRR")

    def __repr__(self):
        return f"<BankAccount {self.name} - {self.bank_name}>"