"""create print_templates table

Revision ID: 007_create_print_templates
Revises: 006_create_accounting_tables
Create Date: 2025-04-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '007_create_print_templates'
down_revision = '006_create_accounting_tables'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('print_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('template_type', sa.String(length=50), nullable=False),
        sa.Column('template_body', sa.Text(), nullable=False),
        sa.Column('preview_image_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('print_templates')