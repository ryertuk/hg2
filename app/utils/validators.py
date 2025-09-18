# app/utils/validators.py

def validate_stock_availability(item_id: int, requested_qty: float):
    """اعتبارسنجی موجودی قبل از ثبت خروجی"""
    # ✅ واردات داخلی — فقط زمانی که تابع فراخوانی می‌شود
    from app.services.stock_service import StockService
    
    service = StockService()
    current_stock = service.get_current_stock(item_id)
    if requested_qty > current_stock:
        raise ValueError(f"موجودی کافی نیست. درخواست: {requested_qty}، موجودی: {current_stock}")
    return True