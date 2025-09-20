"""create invoices and invoice_lines tables

Revision ID: 004_create_invoices_tables
Revises: 003_create_stock_tables
Create Date: 2025-04-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '004_create_invoices_tables'
down_revision = '003_create_stock_tables'
branch_labels = None
depends_on = None

def upgrade():
    # invoices
    op.create_table('invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_type', sa.String(length=20), nullable=False),
        sa.Column('serial', sa.String(length=10), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('serial_full', sa.String(length=50), nullable=False),
        sa.Column('party_id', sa.Integer(), nullable=False),
        sa.Column('date_gregorian', sa.Date(), nullable=False),
        sa.Column('date_jalali', sa.String(length=10), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=18, scale=0), nullable=True),
        sa.Column('tax', sa.Numeric(precision=18, scale=0), nullable=True),
        sa.Column('discount', sa.Numeric(precision=18, scale=0), nullable=True),
        sa.Column('shipping', sa.Numeric(precision=18, scale=0), nullable=True),
        sa.Column('total', sa.Numeric(precision=18, scale=0), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['party_id'], ['parties.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('serial_full')
    )
    op.create_index(op.f('ix_invoices_date_gregorian'), 'invoices', ['date_gregorian'], unique=False)
    op.create_index(op.f('ix_invoices_date_jalali'), 'invoices', ['date_jalali'], unique=False)
    op.create_index(op.f('ix_invoices_serial_full'), 'invoices', ['serial_full'], unique=False)

    # invoice_lines
    op.create_table('invoice_lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('qty', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column('discount', sa.Numeric(precision=18, scale=0), nullable=True),
        sa.Column('tax', sa.Numeric(precision=18, scale=0), nullable=True),
        sa.Column('line_total', sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_lines_invoice_id'), 'invoice_lines', ['invoice_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_invoice_lines_invoice_id'), table_name='invoice_lines')
    op.drop_table('invoice_lines')
    op.drop_index(op.f('ix_invoices_serial_full'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_date_jalali'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_date_gregorian'), table_name='invoices')
    op.drop_table('invoices')