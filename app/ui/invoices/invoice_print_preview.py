# app/ui/invoices/invoice_print_preview.py
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton
from app.utils.template_engine import render_invoice_template
from jinja2 import TemplateNotFound

class InvoicePrintPreview(QDialog):
    def __init__(self, parent=None, invoice_data=None):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.setWindowTitle("پیش‌نمایش چاپ فاکتور")
        self.resize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # WebEngine برای نمایش HTML
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # دکمه‌ها
        btn_layout = QVBoxLayout()
        print_btn = QPushButton("🖨️ چاپ")
        print_btn.clicked.connect(self.print_invoice)
        close_btn = QPushButton("بستن")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_preview()

    def load_preview(self):
        try:
            # بارگذاری قالب پیش‌فرض
            with open("templates/invoice_template.html", "r", encoding="utf-8") as f:
                template_body = f.read()
            html_content = render_invoice_template(template_body, self.invoice_data)
            self.web_view.setHtml(html_content)
        except Exception as e:
            self.web_view.setHtml(f"<h2>خطا در بارگذاری پیش‌نمایش: {str(e)}</h2>")

    def print_invoice(self):
        # در عمل: فراخوانی چاپگر
        self.web_view.print()