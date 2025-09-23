"""add last_purchase_price and last_sale_price to items table

Revision ID: 008_add_price_fields_to_items
Revises: 007_create_print_templates
Create Date: 2025-04-11 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '008_add_price_fields_to_items'
down_revision = '007_create_print_templates'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('items', sa.Column('last_purchase_price', sa.Numeric(precision=18, scale=0), nullable=True, server_default='0'))
    op.add_column('items', sa.Column('last_sale_price', sa.Numeric(precision=18, scale=0), nullable=True, server_default='0'))

def downgrade():
    op.drop_column('items', 'last_sale_price')
    op.drop_column('items', 'last_purchase_price')