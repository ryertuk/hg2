# app/services/invoice_service.py
from app.database import SessionLocal
from app.models.invoice import Invoice
from app.models.invoice_line import InvoiceLine
from app.services.date_service import gregorian_to_jalali, jalali_to_gregorian
from app.utils.price_calculator import calculate_line_total
from app.services.stock_service import StockService
from datetime import datetime
from app.models.item import Item  # ✅ اضافه شد
from app.models.stock_movement import StockMovement

class InvoiceService:
    def __init__(self):
        self.db = SessionLocal()
        self.stock_service = StockService()
        
    def get_all_invoices(self):
        return self.db.query(Invoice).order_by(Invoice.id.desc()).all()

    def create_invoice(self, data, lines_data):
        """ایجاد فاکتور + خطوط — با اعتبارسنجی موجودی و محاسبه خودکار + ایجاد تحرک انبار"""
        gregorian_date = jalali_to_gregorian(data['date_jalali'])
        
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
        self.db.flush()
        invoice.date_jalali = gregorian_to_jalali(invoice.date_gregorian)
        
        subtotal = 0
        for line_data in lines_data:
            item_id = line_data['item_id']
            qty = line_data['qty']
            unit_price = line_data['unit_price']
    
            # اعتبارسنجی موجودی — فقط برای فروش
            if data['invoice_type'] in ['sale', 'sale_return']:
                if qty > 0:
                    current_stock = self.stock_service.get_current_stock(item_id)
                    if qty > current_stock:
                        raise ValueError(f"موجودی کافی نیست. کالا: {item_id}, درخواست: {qty}, موجودی: {current_stock}")
    
            # محاسبه line_total
            item = self.db.query(Item).filter(Item.id == item_id).first()
            line_total = calculate_line_total(
                item=item,
                qty=qty,
                unit_price=unit_price,
                length=item.length if item.unit_type == "measure" else None,
                width=item.width if item.unit_type == "measure" else None
            )
    
            line = InvoiceLine(
                invoice_id=invoice.id,
                item_id=item_id,
                qty=qty,
                unit_id=line_data['unit_id'],
                unit_price=unit_price,
                discount=line_data.get('discount', 0),
                tax=line_data.get('tax', 0),
                line_total=line_total,
                notes=line_data.get('notes', '')
            )
            self.db.add(line)
            subtotal += line_total
            
            # ✅ به‌روزرسانی قیمت‌های کالا
            if data['invoice_type'] == "purchase":
                item.last_purchase_price = unit_price
            elif data['invoice_type'] == "sale":
                item.last_sale_price = unit_price
    
            # ✅ ایجاد تحرک انبار
            movement_type = "purchase_in" if data['invoice_type'] == "purchase" else "sale_out"
            if data['invoice_type'] in ['sale_return', 'purchase_return']:
                movement_type = "return_in" if data['invoice_type'] == "sale_return" else "return_out"
    
            # جهت qty — برای فروش منفی است
            movement_qty = qty if data['invoice_type'] in ['purchase', 'sale_return'] else -qty
    
            stock_movement = StockMovement(
                item_id=item_id,
                qty=movement_qty,
                unit_id=line_data['unit_id'],
                movement_type=movement_type,
                reference_type="invoice",
                reference_id=invoice.id,
                cost_per_unit=unit_price,
                total_cost=int(movement_qty * unit_price)
            )
            self.db.add(stock_movement)
    
        invoice.subtotal = subtotal
        invoice.total = subtotal + invoice.tax + invoice.shipping - invoice.discount
    
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
   
    # در کلاس InvoiceService — افزودن این متد
    def update_invoice(self, invoice_id: int, data: dict, lines_data: list):
        """به‌روزرسانی فاکتور + خطوط + به‌روزرسانی تحرکات انبار"""
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise Exception("فاکتور یافت نشد.")
    
        # جبران تحرکات قدیمی — با ایجاد تحرکات معکوس
        old_movements = self.db.query(StockMovement).filter(
            StockMovement.reference_type == "invoice",
            StockMovement.reference_id == invoice_id
        ).all()
        
        for movement in old_movements:
            reverse_movement = StockMovement(
                item_id=movement.item_id,
                qty=-movement.qty,
                unit_id=movement.unit_id,
                movement_type=f"reverse_{movement.movement_type}",
                reference_type="invoice_reverse",
                reference_id=invoice_id,
                cost_per_unit=movement.cost_per_unit,
                total_cost=-movement.total_cost
            )
            self.db.add(reverse_movement)
        
        # حذف خطوط قدیمی
        self.db.query(InvoiceLine).filter(InvoiceLine.invoice_id == invoice_id).delete()
    
        # به‌روزرسانی فیلدهای اصلی
        for key, value in data.items():
            if hasattr(invoice, key):
                setattr(invoice, key, value)
    
        # افزودن خطوط جدید + تحرکات جدید
        subtotal = 0
        for line_data in lines_data:
            item = self.db.query(Item).filter(Item.id == line_data['item_id']).first()
            line_total = calculate_line_total(
                item=item,
                qty=line_data['qty'],
                unit_price=line_data['unit_price'],
                length=item.length if item.unit_type == "measure" else None,
                width=item.width if item.unit_type == "measure" else None
            )
            line = InvoiceLine(
                invoice_id=invoice.id,
                item_id=line_data['item_id'],
                qty=line_data['qty'],
                unit_id=line_data['unit_id'],
                unit_price=line_data['unit_price'],
                discount=line_data.get('discount', 0),
                tax=line_data.get('tax', 0),
                line_total=line_total,
                notes=line_data.get('notes', '')
            )
            self.db.add(line)
            subtotal += line_total
            
             # ✅ به‌روزرسانی قیمت‌های کالا
            if data['invoice_type'] == "purchase":
                item.last_purchase_price = unit_price
            elif data['invoice_type'] == "sale":
                item.last_sale_price = unit_price
       
            # ✅ ایجاد تحرک انبار جدید
            movement_type = "purchase_in" if data['invoice_type'] == "purchase" else "sale_out"
            if data['invoice_type'] in ['sale_return', 'purchase_return']:
                movement_type = "return_in" if data['invoice_type'] == "sale_return" else "return_out"
    
            movement_qty = line_data['qty'] if data['invoice_type'] in ['purchase', 'sale_return'] else -line_data['qty']
    
            stock_movement = StockMovement(
                item_id=line_data['item_id'],
                qty=movement_qty,
                unit_id=line_data['unit_id'],
                movement_type=movement_type,
                reference_type="invoice",
                reference_id=invoice.id,
                cost_per_unit=line_data['unit_price'],
                total_cost=int(movement_qty * line_data['unit_price'])
            )
            self.db.add(stock_movement)
    
        invoice.subtotal = subtotal
        invoice.total = subtotal + invoice.tax + invoice.shipping - invoice.discount
    
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
        
    def delete_invoice(self, invoice_id: int):
        """حذف یک فاکتور + خطوط مرتبط + جبران تحرکات انبار"""
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise Exception("فاکتور یافت نشد.")
        
        # جبران تحرکات انبار — با ایجاد تحرکات معکوس
        movements = self.db.query(StockMovement).filter(
            StockMovement.reference_type == "invoice",
            StockMovement.reference_id == invoice_id
        ).all()
        
        for movement in movements:
            # ایجاد تحرک معکوس — با qty معکوس
            reverse_movement = StockMovement(
                item_id=movement.item_id,
                qty=-movement.qty,  # معکوس کردن جهت
                unit_id=movement.unit_id,
                movement_type=f"reverse_{movement.movement_type}",
                reference_type="invoice_reverse",
                reference_id=invoice_id,
                cost_per_unit=movement.cost_per_unit,
                total_cost=-movement.total_cost
            )
            self.db.add(reverse_movement)
        
        # حذف خطوط فاکتور
        self.db.query(InvoiceLine).filter(InvoiceLine.invoice_id == invoice_id).delete()
        
        # حذف فاکتور
        self.db.delete(invoice)
        self.db.commit()
        
    def get_all_invoices_with_parties(self):
        """دریافت تمام فاکتورها + JOIN با جدول طرف‌حساب‌ها برای نمایش"""
        from app.models.party import Party
        return self.db.query(Invoice, Party.name.label('party_name')).\
            join(Party, Invoice.party_id == Party.id).\
            order_by(Invoice.id.desc()).all()
            