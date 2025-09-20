# app/models/journal_line.py
from sqlalchemy import Column, Integer, Numeric, ForeignKey, String
from app.models.base import BaseModel

class JournalLine(BaseModel):
    __tablename__ = 'journal_lines'

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=False, index=True)
    ledger_account_id = Column(Integer, ForeignKey('ledger_accounts.id'), nullable=False)
    debit = Column(Numeric(18, 0), default=0)  # ریال
    credit = Column(Numeric(18, 0), default=0)  # ریال
    party_id = Column(Integer, ForeignKey('parties.id'), nullable=True)  # اختیاری
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<JournalLine JE={self.journal_entry_id} Dr={self.debit} Cr={self.credit}>"