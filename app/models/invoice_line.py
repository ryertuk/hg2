# app/models/invoice_line.py
from sqlalchemy import Column, Integer, Numeric, Text, ForeignKey
from app.models.base import BaseModel

class InvoiceLine(BaseModel):
    __tablename__ = 'invoice_lines'

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    qty = Column(Numeric(18, 4), nullable=False)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=False)
    unit_price = Column(Numeric(18, 0), nullable=False)  # قیمت واحد — ریال
    discount = Column(Numeric(18, 0), nullable=False, default=0)
    tax = Column(Numeric(18, 0), nullable=False, default=0)
    line_total = Column(Numeric(18, 0), nullable=False)  # محاسبه شده — ریال
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<InvoiceLine item={self.item_id} qty={self.qty} total={self.line_total}>"