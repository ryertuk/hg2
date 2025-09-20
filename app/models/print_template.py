# app/models/print_template.py
from sqlalchemy import Column, Integer, String, Text
from app.models.base import BaseModel

class PrintTemplate(BaseModel):
    __tablename__ = 'print_templates'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    template_type = Column(String(50), nullable=False)  # invoice_A4, receipt, thermal
    template_body = Column(Text, nullable=False)        # محتوای Jinja2
    preview_image_path = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<PrintTemplate {self.name}>"