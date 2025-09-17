"""Create units and items tables

Revision ID: 0002
Revises: 0001
Create Date: 2025-09-17

"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('factor_to_base', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_units_code'), 'units', ['code'], unique=False)

    op.create_table('items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('unit_type', sa.String(), nullable=True),
        sa.Column('base_unit_id', sa.Integer(), nullable=True),
        sa.Column('length', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('width', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('barcode', sa.String(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['base_unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('barcode'),
        sa.UniqueConstraint('sku')
    )
    op.create_index(op.f('ix_items_name'), 'items', ['name'], unique=False)
    op.create_index(op.f('ix_items_sku'), 'items', ['sku'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_items_sku'), table_name='items')
    op.drop_index(op.f('ix_items_name'), table_name='items')
    op.drop_table('items')
    op.drop_index(op.f('ix_units_code'), table_name='units')
    op.drop_table('units')