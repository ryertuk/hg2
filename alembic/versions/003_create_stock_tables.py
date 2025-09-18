"""create stock_movements and stock_val_periods tables

Revision ID: 003_create_stock_tables
Revises: 002_create_units_items
Create Date: 2025-04-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

revision = '003_create_stock_tables'
down_revision = '002_create_units_items'
branch_labels = None
depends_on = None

def upgrade():
    # stock_movements
    op.create_table('stock_movements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('qty', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=False),
        sa.Column('movement_type', sa.String(length=50), nullable=False),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('cost_per_unit', sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column('total_cost', sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('qty != 0', name='check_qty_nonzero')
    )
    op.create_index(op.f('ix_stock_movements_item_id'), 'stock_movements', ['item_id'], unique=False)

    # stock_val_periods
    op.create_table('stock_val_periods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('avg_cost', sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column('total_qty', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('total_value', sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_val_periods_item_id'), 'stock_val_periods', ['item_id'], unique=False)
    op.create_index(op.f('ix_stock_val_periods_period'), 'stock_val_periods', ['period'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_stock_val_periods_period'), table_name='stock_val_periods')
    op.drop_index(op.f('ix_stock_val_periods_item_id'), table_name='stock_val_periods')
    op.drop_table('stock_val_periods')
    op.drop_index(op.f('ix_stock_movements_item_id'), table_name='stock_movements')
    op.drop_table('stock_movements')