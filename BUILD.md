#!/bin/bash
echo "ساخت محیط اجرا..."
pip install -r requirements.txt
alembic init alembic
echo "✅ محیط اولیه ساخته شد."