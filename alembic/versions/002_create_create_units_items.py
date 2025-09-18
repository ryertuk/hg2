"""create units and items tables

Revision ID: 002_create_units_items
Revises: 1_create_users_roles_parties
Create Date: 2025-04-05 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '002_create_units_items'
down_revision = '1_create_users_roles_parties'
branch_labels = None
depends_on = None

def upgrade():
    # units
    op.create_table('units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('factor_to_base', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_units_code'), 'units', ['code'], unique=False)

    # items
    op.create_table('items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('unit_type', sa.String(length=20), nullable=False),
        sa.Column('base_unit_id', sa.Integer(), nullable=False),
        sa.Column('length', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('width', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('barcode', sa.String(length=100), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['base_unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku'),
        sa.UniqueConstraint('barcode')
    )
    op.create_index(op.f('ix_items_name'), 'items', ['name'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_items_name'), table_name='items')
    op.drop_table('items')
    op.drop_index(op.f('ix_units_code'), table_name='units')
    op.drop_table('units')