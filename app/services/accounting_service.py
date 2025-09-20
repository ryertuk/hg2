# app/services/accounting_service.py
from app.database import SessionLocal
from app.models.journal_entry import JournalEntry
from app.models.journal_line import JournalLine
from app.utils.double_entry import validate_double_entry

class AccountingService:
    def __init__(self):
        self.db = SessionLocal()

    def create_journal_entry(self, data, lines_data):
        """ایجاد ثبت روزنامه + خطوط — با اعتبارسنجی دوبل"""
        journal_entry = JournalEntry(**data)
        self.db.add(journal_entry)
        self.db.flush()

        for line_data in lines_data:
            line = JournalLine(journal_entry_id=journal_entry.id, **line_data)
            self.db.add(line)

        self.db.flush()
        validate_double_entry(self.db, journal_entry)
        self.db.commit()
        self.db.refresh(journal_entry)
        return journal_entry

    def get_journal_entries_by_period(self, period: str):
        return self.db.query(JournalEntry).filter(JournalEntry.period == period).order_by(JournalEntry.date).all()