"""create ledger_accounts, journal_entries, journal_lines tables

Revision ID: 006_create_accounting_tables
Revises: 005_create_checks_payments_tables
Create Date: 2025-04-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '006_create_accounting_tables'
down_revision = '005_create_checks_payments_tables'
branch_labels = None
depends_on = None

def upgrade():
    # ledger_accounts
    op.create_table('ledger_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('account_type', sa.String(length=50), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('is_reconcilable', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['ledger_accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # journal_entries
    op.create_table('journal_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('posted', sa.Boolean(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_journal_entries_date'), 'journal_entries', ['date'], unique=False)
    op.create_index(op.f('ix_journal_entries_period'), 'journal_entries', ['period'], unique=False)

    # journal_lines
    op.create_table('journal_lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('journal_entry_id', sa.Integer(), nullable=False),
        sa.Column('ledger_account_id', sa.Integer(), nullable=False),
        sa.Column('debit', sa.Numeric(precision=18, scale=0), nullable=True),
        sa.Column('credit', sa.Numeric(precision=18, scale=0), nullable=True),
        sa.Column('party_id', sa.Integer(), nullable=True),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], ),
        sa.ForeignKeyConstraint(['ledger_account_id'], ['ledger_accounts.id'], ),
        sa.ForeignKeyConstraint(['party_id'], ['parties.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_journal_lines_journal_entry_id'), 'journal_lines', ['journal_entry_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_journal_lines_journal_entry_id'), table_name='journal_lines')
    op.drop_table('journal_lines')
    op.drop_index(op.f('ix_journal_entries_period'), table_name='journal_entries')
    op.drop_index(op.f('ix_journal_entries_date'), table_name='journal_entries')
    op.drop_table('journal_entries')
    op.drop_table('ledger_accounts')