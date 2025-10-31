"""Add Order, Position, Trade tables

Revision ID: 002
Revises: 001
Create Date: 2025-10-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('strategy_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('strategies.id'), nullable=False),
        sa.Column('instrument_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('instruments.id'), nullable=False),
        sa.Column('side', sa.Enum('BUY', 'SELL', name='orderside'), nullable=False),
        sa.Column('order_type', sa.Enum('MARKET', 'LIMIT', 'STOP_LOSS', 'STOP_LOSS_MARKET', name='ordertype'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('filled_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('price', sa.Numeric(10, 2), nullable=True),
        sa.Column('stop_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('average_fill_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'SUBMITTED', 'ACKNOWLEDGED', 'FILLED', 'PARTIALLY_FILLED', 'REJECTED', 'CANCELLED', name='orderstatus'), nullable=False),
        sa.Column('mode', sa.String(10), nullable=False),
        sa.Column('broker_order_id', sa.String(100), nullable=True),
        sa.Column('fills', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('rejection_reason', sa.String(500), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('filled_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_orders_strategy', 'orders', ['strategy_id'])
    op.create_index('ix_orders_instrument', 'orders', ['instrument_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_orders_mode', 'orders', ['mode'])
    
    # Create positions table
    op.create_table(
        'positions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('strategy_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('strategies.id'), nullable=False),
        sa.Column('instrument_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('instruments.id'), nullable=False),
        sa.Column('side', sa.Enum('LONG', 'SHORT', name='positionside'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('entry_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('current_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('stop_loss_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('unrealized_pnl', sa.Numeric(10, 2), nullable=False, default=0),
        sa.Column('status', sa.Enum('OPEN', 'CLOSED', name='positionstatus'), nullable=False),
        sa.Column('mode', sa.String(10), nullable=False),
        sa.Column('entry_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_positions_strategy', 'positions', ['strategy_id'])
    op.create_index('ix_positions_instrument', 'positions', ['instrument_id'])
    op.create_index('ix_positions_status', 'positions', ['status'])
    
    # Create trades table
    op.create_table(
        'trades',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('position_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('positions.id'), nullable=False),
        sa.Column('strategy_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('strategies.id'), nullable=False),
        sa.Column('instrument_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('instruments.id'), nullable=False),
        sa.Column('entry_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('exit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('gross_pnl', sa.Numeric(10, 2), nullable=False),
        sa.Column('transaction_costs', sa.Numeric(10, 2), nullable=False, default=0),
        sa.Column('net_pnl', sa.Numeric(10, 2), nullable=False),
        sa.Column('exit_reason', sa.String(100), nullable=False),
        sa.Column('holding_period_seconds', sa.Integer(), nullable=False),
        sa.Column('entry_time', sa.DateTime(), nullable=False),
        sa.Column('exit_time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_trades_position', 'trades', ['position_id'])
    op.create_index('ix_trades_strategy', 'trades', ['strategy_id'])


def downgrade() -> None:
    op.drop_table('trades')
    op.drop_table('positions')
    op.drop_table('orders')
    
    op.execute('DROP TYPE IF EXISTS positionstatus')
    op.execute('DROP TYPE IF EXISTS positionside')
    op.execute('DROP TYPE IF EXISTS orderstatus')
    op.execute('DROP TYPE IF EXISTS ordertype')
    op.execute('DROP TYPE IF EXISTS orderside')
