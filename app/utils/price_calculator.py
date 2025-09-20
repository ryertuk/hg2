# app/utils/price_calculator.py

def calculate_line_total(item, qty, unit_price, length=None, width=None):
    """محاسبه مبلغ کل خط فاکتور — با در نظر گرفتن نوع کالا"""
    if item.unit_type == "measure" and length and width:
        # برای کالاهای اندازه‌ای: قیمت کل = قیمت واحد × طول × عرض × تعداد
        area = length * width
        return int(unit_price * area * qty)
    else:
        # برای کالاهای تعدادی: قیمت کل = قیمت واحد × تعداد
        return int(unit_price * qty)