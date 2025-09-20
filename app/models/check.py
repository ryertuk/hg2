# app/models/check.py
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, CheckConstraint
from app.models.base import BaseModel

class Check(BaseModel):
    __tablename__ = 'checks'

    id = Column(Integer, primary_key=True, index=True)
    check_number = Column(String(50), nullable=False, index=True)  # منحصربه‌فرد در هر حساب بانکی
    bank_name = Column(String(100), nullable=False)
    bank_branch = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=False)
    direction = Column(String(20), nullable=False)  # 'received' | 'issued'
    amount = Column(Numeric(18, 0), nullable=False)  # ریال — بدون اعشار
    currency = Column(String(3), default="IRR")
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False, default="registered")  # registered, issued, in_hand, deposited, cleared, bounced, endorsed, reconciled, cancelled
    issuer_name = Column(String(200), nullable=True)
    payer_party_id = Column(Integer, ForeignKey('parties.id'), nullable=True)  # طرف پرداخت‌کننده
    payee_party_id = Column(Integer, ForeignKey('parties.id'), nullable=True)  # طرف دریافت‌کننده
    related_invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=True)
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False)
    image_path = Column(String(500), nullable=True)
    bounce_reason = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    __table_args__ = (
        CheckConstraint("direction IN ('received', 'issued')", name="check_direction_valid"),
        CheckConstraint("status IN ('registered', 'issued', 'in_hand', 'deposited', 'cleared', 'bounced', 'endorsed', 'reconciled', 'cancelled')", name="check_status_valid"),
    )

    def __repr__(self):
        return f"<Check {self.check_number} - {self.amount:,.0f} {self.status}>"