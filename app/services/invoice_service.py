# app/services/invoice_service.py
from app.database import SessionLocal
from app.models.invoice import Invoice
from app.models.invoice_line import InvoiceLine
from app.services.date_service import gregorian_to_jalali, jalali_to_gregorian
from app.utils.price_calculator import calculate_line_total
from app.services.stock_service import StockService
from datetime import datetime
from app.models.item import Item
from app.models.stock_movement import StockMovement
from decimal import Decimal
from sqlalchemy import func

class InvoiceService:
    def __init__(self):
        self.db = SessionLocal()
        self.stock_service = StockService()

    def get_current_stock_without_invoice(self, item_id: int, exclude_invoice_id: int) -> float:
        """محاسبه موجودی بدون در نظر گرفتن یک فاکتور خاص"""
        # جمع کل حرکات به جز حرکات مربوط به فاکتور مورد نظر
        result = self.db.query(
            func.coalesce(func.sum(StockMovement.qty), Decimal('0'))
        ).filter(
            StockMovement.item_id == item_id,
            ~(
                (StockMovement.reference_type == "invoice") & 
                (StockMovement.reference_id == exclude_invoice_id)
            )
        ).scalar()
        
        return float(result) if result else 0.0

    # ----- helper (داخل کلاس InvoiceService) -----
    def _get_current_stock_db(self, item_id: int, exclude_invoice_id: int = None) -> Decimal:
        """محاسبه موجودی فعلی از دیتابیس با امکان حذف حرکات مربوط به یک فاکتور خاص"""
        q = self.db.query(func.coalesce(func.sum(StockMovement.qty), Decimal('0'))).filter(
            StockMovement.item_id == item_id
        )
        if exclude_invoice_id is not None:
            # حذف همهٔ حرکاتی که reference_type=='invoice' و reference_id==exclude_invoice_id
            q = q.filter(~((StockMovement.reference_type == "invoice") &
                           (StockMovement.reference_id == exclude_invoice_id)))
        res = q.scalar()
        return Decimal(res or 0)
    
    def create_invoice(self, data: dict, lines_data: list):
        """ایجاد فاکتور + خطوط + تحرکات انبار"""
        try:
            # --- ۱) ایجاد رکورد فاکتور ---
            invoice = Invoice(**data)
            self.db.add(invoice)
            self.db.flush()  # نیاز به id فاکتور داریم
    
            # --- ۲) اعتبارسنجی موجودی ---
            if data['invoice_type'] in ['sale', 'purchase_return']:
                for line_data in lines_data:
                    current_stock = self.stock_service.get_current_stock(line_data['item_id'])
                    if line_data['qty'] > current_stock:
                        raise ValueError(
                            f"موجودی کافی نیست. کالا: {line_data['item_id']}, "
                            f"درخواست: {line_data['qty']}, موجودی: {current_stock}"
                        )
    
            # --- ۳) ثبت خطوط و تحرکات ---
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
    
                # ایجاد خط فاکتور
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
    
                # به‌روزرسانی آخرین قیمت کالا
                if data['invoice_type'] == "purchase":
                    item.last_purchase_price = line_data['unit_price']
                elif data['invoice_type'] == "sale":
                    item.last_sale_price = line_data['unit_price']
    
                # تعیین نوع تحرک انبار
                if data['invoice_type'] == "purchase":
                    movement_type, movement_qty = "purchase_in", line_data['qty']
                elif data['invoice_type'] == "sale":
                    movement_type, movement_qty = "sale_out", -line_data['qty']
                elif data['invoice_type'] == "sale_return":
                    movement_type, movement_qty = "return_in", line_data['qty']
                elif data['invoice_type'] == "purchase_return":
                    movement_type, movement_qty = "return_out", -line_data['qty']
                else:
                    raise ValueError(f"نوع فاکتور نامعتبر: {data['invoice_type']}")
    
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
    
            # --- ۴) محاسبه جمع ---
            invoice.subtotal = subtotal
            invoice.total = subtotal + invoice.tax + invoice.shipping - invoice.discount
    
            # --- ۵) ذخیره ---
            self.db.commit()
            self.db.refresh(invoice)
            return invoice
    
        except Exception as e:
            self.db.rollback()
            # اجازه می‌دهیم UI خطا را نشان دهد و پنجره باز بماند
            raise
    
    
    def update_invoice(self, invoice_id: int, data: dict, lines_data: list):
        """به‌روزرسانی فاکتور + خطوط + تحرکات انبار (حذف و ایجاد مجدد)"""
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise Exception("فاکتور یافت نشد.")
    
        try:
            # --- ۱) حذف خطوط و تحرکات قبلی ---
            self.db.query(StockMovement).filter(
                StockMovement.reference_type == "invoice",
                StockMovement.reference_id == invoice_id
            ).delete()
    
            self.db.query(InvoiceLine).filter(
                InvoiceLine.invoice_id == invoice_id
            ).delete()
    
            # --- ۲) بروزرسانی فیلدهای اصلی ---
            for key, value in data.items():
                if hasattr(invoice, key):
                    setattr(invoice, key, value)
    
            # --- ۳) اعتبارسنجی موجودی ---
            if data['invoice_type'] in ['sale', 'purchase_return']:
                for line_data in lines_data:
                    current_stock = self.stock_service.get_current_stock(line_data['item_id'])
                    if line_data['qty'] > current_stock:
                        raise ValueError(
                            f"موجودی کافی نیست. کالا: {line_data['item_id']}, "
                            f"درخواست: {line_data['qty']}, موجودی: {current_stock}"
                        )
    
            # --- ۴) ثبت خطوط و تحرکات جدید ---
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
    
                if data['invoice_type'] == "purchase":
                    item.last_purchase_price = line_data['unit_price']
                elif data['invoice_type'] == "sale":
                    item.last_sale_price = line_data['unit_price']
    
                if data['invoice_type'] == "purchase":
                    movement_type, movement_qty = "purchase_in", line_data['qty']
                elif data['invoice_type'] == "sale":
                    movement_type, movement_qty = "sale_out", -line_data['qty']
                elif data['invoice_type'] == "sale_return":
                    movement_type, movement_qty = "return_in", line_data['qty']
                elif data['invoice_type'] == "purchase_return":
                    movement_type, movement_qty = "return_out", -line_data['qty']
                else:
                    raise ValueError(f"نوع فاکتور نامعتبر: {data['invoice_type']}")
    
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
    
            # --- ۵) محاسبه جمع ---
            invoice.subtotal = subtotal
            invoice.total = subtotal + invoice.tax + invoice.shipping - invoice.discount
    
            # --- ۶) ذخیره ---
            self.db.commit()
            self.db.refresh(invoice)
            return invoice
    
        except Exception as e:
            self.db.rollback()
            raise
    
    
    def delete_invoice(self, invoice_id: int):
        """حذف فاکتور + خطوط + تحرکات انبار"""
        try:
            invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                raise Exception("فاکتور یافت نشد.")
    
            # --- ۱) حذف تحرکات ---
            self.db.query(StockMovement).filter(
                StockMovement.reference_type == "invoice",
                StockMovement.reference_id == invoice_id
            ).delete()
    
            # --- ۲) حذف خطوط ---
            self.db.query(InvoiceLine).filter(
                InvoiceLine.invoice_id == invoice_id
            ).delete()
    
            # --- ۳) حذف فاکتور ---
            self.db.delete(invoice)
    
            # --- ۴) ذخیره ---
            self.db.commit()
            return True
    
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_all_invoices(self):
        return self.db.query(Invoice).order_by(Invoice.id.desc()).all()

    def get_all_invoices_with_parties(self):
        """دریافت تمام فاکتورها + JOIN با جدول طرف‌حساب‌ها برای نمایش"""
        from app.models.party import Party
        return self.db.query(Invoice, Party.name.label('party_name')).\
            join(Party, Invoice.party_id == Party.id).\
            order_by(Invoice.id.desc()).all()