from PySide6.QtWidgets import QWidget
import arabic_reshaper
from bidi.algorithm import get_display

def set_rtl_stylesheet(widget: QWidget):
    widget.setStyleSheet("QWidget { direction: rtl; }")
    # برای متن‌ها: get_display(arabic_reshaper.reshape(text))