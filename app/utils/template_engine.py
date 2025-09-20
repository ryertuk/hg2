# app/utils/template_engine.py
import jinja2
import arabic_reshaper
from bidi.algorithm import get_display
from jdatetime import date as jdate

def render_invoice_template(template_body: str, context: dict) -> str:
    """رندر کردن قالب فاکتور با داده‌های فاکتور — با پشتیبانی RTL"""
    # افزودن توابع کمکی به context
    context['to_jalali'] = lambda greg_date: jdate.fromgregorian(date=greg_date).strftime("%Y/%m/%d") if greg_date else ""
    context['format_price'] = lambda price: f"{int(price):,}" if price else "0"

    # رندر اولیه
    template = jinja2.Template(template_body)
    rendered = template.render(**context)

    # اعمال RTL — reshaper + bidi
    reshaped_text = arabic_reshaper.reshape(rendered)
    bidi_text = get_display(reshaped_text)
    return bidi_text