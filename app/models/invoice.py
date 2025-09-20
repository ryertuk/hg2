# app/models/invoice.py
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, CheckConstraint
from app.models.base import BaseModel

class Invoice(BaseModel):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, index=True)
    invoice_type = Column(String(20), nullable=False)  # purchase, sale, purchase_return, sale_return
    serial = Column(String(10), nullable=False)        # پیشوند — مثلاً: "INV"
    number = Column(Integer, nullable=False)           # شماره ترتیبی
    serial_full = Column(String(50), unique=True, nullable=False, index=True)  # INV-1404-0001
    party_id = Column(Integer, ForeignKey('parties.id'), nullable=False)
    date_gregorian = Column(Date, nullable=False, index=True)        # تاریخ میلادی — برای محاسبات
    date_jalali = Column(String(10), nullable=False, index=True)     # تاریخ شمسی — برای نمایش
    subtotal = Column(Numeric(18, 0), nullable=False, default=0)     # جمع کل — ریال
    tax = Column(Numeric(18, 0), nullable=False, default=0)
    discount = Column(Numeric(18, 0), nullable=False, default=0)
    shipping = Column(Numeric(18, 0), nullable=False, default=0)
    total = Column(Numeric(18, 0), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="draft")     # draft, posted, cancelled
    posted_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Invoice {self.serial_full} type={self.invoice_type} total={self.total}>"