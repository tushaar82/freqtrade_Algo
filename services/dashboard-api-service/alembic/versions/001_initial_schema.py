"""Initial schema - User, Instrument, Strategy tables

Revision ID: 001
Revises: 
Create Date: 2025-10-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'INVESTOR', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create instruments table
    op.create_table(
        'instruments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('exchange', sa.Enum('NSE', 'BSE', 'MCX', 'NFO', name='exchange'), nullable=False),
        sa.Column('instrument_type', sa.Enum('EQUITY', 'FUTURE', 'CALL_OPTION', 'PUT_OPTION', name='instrumenttype'), nullable=False),
        sa.Column('lot_size', sa.Integer(), nullable=False, default=1),
        sa.Column('tick_size', sa.Numeric(10, 4), nullable=False, default=0.05),
        sa.Column('circuit_limit_upper', sa.Numeric(10, 2), nullable=True),
        sa.Column('circuit_limit_lower', sa.Numeric(10, 2), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('strike_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('symbol', 'exchange', name='uix_symbol_exchange'),
    )
    op.create_index('ix_instruments_symbol', 'instruments', ['symbol'])
    op.create_index('ix_instruments_exchange', 'instruments', ['exchange'])
    op.create_index('ix_instruments_type', 'instruments', ['instrument_type'])
    op.create_index('ix_instruments_active', 'instruments', ['is_active'])
    
    # Create strategies table
    op.create_table(
        'strategies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('strategy_type', sa.String(100), nullable=False),
        sa.Column('config', postgresql.JSONB(), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'PAPER_TRADING', 'LIVE', 'PAUSED', 'STOPPED', name='strategystatus'), nullable=False),
        sa.Column('mode', sa.Enum('PAPER', 'LIVE', name='tradingmode'), nullable=False),
        sa.Column('risk_params', postgresql.JSONB(), nullable=False),
        sa.Column('activated_at', sa.DateTime(), nullable=True),
        sa.Column('deactivated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_strategies_owner', 'strategies', ['owner_id'])
    op.create_index('ix_strategies_status', 'strategies', ['status'])
    op.create_index('ix_strategies_mode', 'strategies', ['mode'])


def downgrade() -> None:
    op.drop_table('strategies')
    op.drop_table('instruments')
    op.drop_table('users')
    
    op.execute('DROP TYPE IF EXISTS strategystatus')
    op.execute('DROP TYPE IF EXISTS tradingmode')
    op.execute('DROP TYPE IF EXISTS instrumenttype')
    op.execute('DROP TYPE IF EXISTS exchange')
    op.execute('DROP TYPE IF EXISTS userrole')
