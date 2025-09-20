"""create checks, payments, payment_lines, bank_accounts tables

Revision ID: 005_create_checks_payments_tables
Revises: 004_create_invoices_tables
Create Date: 2025-04-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '005_create_checks_payments_tables'
down_revision = '004_create_invoices_tables'
branch_labels = None
depends_on = None

def upgrade():
    # bank_accounts
    op.create_table('bank_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('bank_name', sa.String(length=100), nullable=False),
        sa.Column('account_number', sa.String(length=50), nullable=False),
        sa.Column('ledger_account_id', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ledger_account_id'], ['ledger_accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # checks
    op.create_table('checks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('check_number', sa.String(length=50), nullable=False),
        sa.Column('bank_name', sa.String(length=100), nullable=False),
        sa.Column('bank_branch', sa.String(length=100), nullable=True),
        sa.Column('account_number', sa.String(length=50), nullable=False),
        sa.Column('direction', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('issuer_name', sa.String(length=200), nullable=True),
        sa.Column('payer_party_id', sa.Integer(), nullable=True),
        sa.Column('payee_party_id', sa.Integer(), nullable=True),
        sa.Column('related_invoice_id', sa.Integer(), nullable=True),
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        sa.Column('image_path', sa.String(length=500), nullable=True),
        sa.Column('bounce_reason', sa.String(length=500), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint("direction IN ('received', 'issued')", name='check_direction_valid'),
        sa.CheckConstraint("status IN ('registered', 'issued', 'in_hand', 'deposited', 'cleared', 'bounced', 'endorsed', 'reconciled', 'cancelled')", name='check_status_valid'),
        sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['payee_party_id'], ['parties.id'], ),
        sa.ForeignKeyConstraint(['payer_party_id'], ['parties.id'], ),
        sa.ForeignKeyConstraint(['related_invoice_id'], ['invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_checks_check_number'), 'checks', ['check_number'], unique=False)

    # payments
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('payment_type', sa.String(length=20), nullable=False),
        sa.Column('party_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column('method', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['party_id'], ['parties.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # payment_lines
    op.create_table('payment_lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('payment_id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=True),
        sa.Column('check_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['ledger_accounts.id'], ),
        sa.ForeignKeyConstraint(['check_id'], ['checks.id'], ),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_lines_payment_id'), 'payment_lines', ['payment_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_payment_lines_payment_id'), table_name='payment_lines')
    op.drop_table('payment_lines')
    op.drop_table('payments')
    op.drop_table('checks')
    op.drop_table('bank_accounts')