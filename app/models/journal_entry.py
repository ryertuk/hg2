# app/models/journal_entry.py
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from app.models.base import BaseModel

class JournalEntry(BaseModel):
    __tablename__ = 'journal_entries'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    period = Column(String(7), nullable=False, index=True)  # YYYY-MM
    description = Column(String(500), nullable=True)
    source_type = Column(String(50), nullable=False)  # invoice, payment, check, adjustment
    source_id = Column(Integer, nullable=False)
    posted = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<JournalEntry {self.id} {self.period} {self.description}>"