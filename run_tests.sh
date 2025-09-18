#!/bin/bash
echo "اجرای تست‌ها..."
python -m pytest tests/ -v --cov=app --cov-report=html
echo "✅ تست‌ها اجرا شدند. گزارش پوشش: htmlcov/index.html"