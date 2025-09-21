# app/utils/price_calculator.py

def calculate_line_total(item, qty, unit_price, length=None, width=None):
    """محاسبه مبلغ کل خط فاکتور — با در نظر گرفتن نوع کالا — تمام ورودی‌ها به float تبدیل می‌شوند"""
    try:
        qty = float(qty)
        unit_price = float(unit_price)
        
        if item.unit_type == "measure" and length and width:
            area = float(length) * float(width)
            return int(unit_price * area * qty)
        else:
            return int(unit_price * qty)
    except (ValueError, TypeError) as e:
        raise ValueError(f"خطا در محاسبه قیمت: {str(e)}")