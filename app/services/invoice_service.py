# app/services/invoice_service.py
from app.database import SessionLocal
from app.models.invoice import Invoice
from app.models.invoice_line import InvoiceLine
from app.services.date_service import gregorian_to_jalali, jalali_to_gregorian
from app.utils.price_calculator import calculate_line_total
from app.services.stock_service import StockService
from datetime import datetime

class InvoiceService:
    def __init__(self):
        self.db = SessionLocal()
        self.stock_service = StockService()
        
    def get_all_invoices(self):
        return self.db.query(Invoice).order_by(Invoice.id.desc()).all()

    def create_invoice(self, data, lines_data):
        """ایجاد فاکتور + خطوط — با اعتبارسنجی موجودی و محاسبه خودکار"""
        # تبدیل تاریخ شمسی به میلادی
        gregorian_date = jalali_to_gregorian(data['date_jalali'])
        
        # ایجاد فاکتور (موقتاً subtotal=0 — بعداً به‌روزرسانی می‌شود)
        invoice = Invoice(
            invoice_type=data['invoice_type'],
            serial=data['serial'],
            number=data['number'],
            serial_full=data['serial_full'],
            party_id=data['party_id'],
            date_gregorian=gregorian_date,
            date_jalali=data['date_jalali'],
            subtotal=0,
            tax=data.get('tax', 0),
            discount=data.get('discount', 0),
            shipping=data.get('shipping', 0),
            total=0,
            status="draft",
            created_by=data['created_by']
        )
        self.db.add(invoice)
        self.db.flush()  # برای دریافت id

        # ایجاد خطوط فاکتور
        subtotal = 0
        for line_data in lines_data:
            item_id = line_data['item_id']
            qty = line_data['qty']

            # اعتبارسنجی موجودی — فقط برای فروش
            if data['invoice_type'] in ['sale', 'sale_return']:
                if qty > 0:  # فروش — باید موجودی کافی باشد
                    self.stock_service.get_current_stock(item_id)  # فقط برای اعتبارسنجی — در add_movement واقعی انجام می‌شود

            # محاسبه line_total
            from app.models.item import Item
            item = self.db.query(Item).filter(Item.id == item_id).first()
            line_total = calculate_line_total(
                item=item,
                qty=qty,
                unit_price=line_data['unit_price'],
                length=item.length if item.unit_type == "measure" else None,
                width=item.width if item.unit_type == "measure" else None
            )

            line = InvoiceLine(
                invoice_id=invoice.id,
                item_id=item_id,
                qty=qty,
                unit_id=line_data['unit_id'],
                unit_price=line_data['unit_price'],
                discount=line_data.get('discount', 0),
                tax=line_data.get('tax', 0),
                line_total=line_total,
                notes=line_data.get('notes', '')
            )
            self.db.add(line)
            subtotal += line_total

        # به‌روزرسانی جمع فاکتور
        invoice.subtotal = subtotal
        invoice.total = subtotal + invoice.tax + invoice.shipping - invoice.discount

        self.db.commit()
        self.db.refresh(invoice)
        return invoice