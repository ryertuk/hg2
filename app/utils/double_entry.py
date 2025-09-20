# app/utils/double_entry.py
from sqlalchemy.orm import Session
from app.models.journal_entry import JournalEntry
from app.models.journal_line import JournalLine

def validate_double_entry(session: Session, journal_entry: JournalEntry):
    """اعتبارسنجی: جمع debit == جمع credit"""
    lines = session.query(JournalLine).filter(JournalLine.journal_entry_id == journal_entry.id).all()
    total_debit = sum(line.debit for line in lines)
    total_credit = sum(line.credit for line in lines)
    if total_debit != total_credit:
        raise ValueError(f"ثبت دوبل نامعتبر: Debit={total_debit} != Credit={total_credit}")
    return True