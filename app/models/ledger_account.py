# app/models/ledger_account.py
from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.base import BaseModel

class LedgerAccount(BaseModel):
    __tablename__ = 'ledger_accounts'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # مثلاً: 1.1.1
    name = Column(String(200), nullable=False)
    account_type = Column(String(50), nullable=False)  # asset, liability, equity, income, expense
    parent_id = Column(Integer, ForeignKey('ledger_accounts.id'), nullable=True)
    is_reconcilable = Column(Boolean, default=False)

    def __repr__(self):
        return f"<LedgerAccount {self.code} - {self.name}>"