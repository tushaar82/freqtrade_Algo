"""Position and Trade Models"""
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
from shared.schemas.database.base import BaseModel

class PositionSide(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class PositionStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class Position(BaseModel):
    __tablename__ = "positions"
    
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False, index=True)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey("instruments.id"), nullable=False, index=True)
    side = Column(Enum(PositionSide), nullable=False)
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Numeric(10, 2), nullable=False)
    current_price = Column(Numeric(10, 2), nullable=False)
    stop_loss_price = Column(Numeric(10, 2), nullable=True)
    unrealized_pnl = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(Enum(PositionStatus), nullable=False, default=PositionStatus.OPEN, index=True)
    mode = Column(String(10), nullable=False)
    entry_order_id = Column(UUID(as_uuid=True), nullable=False)
    
    strategy = relationship("Strategy", back_populates="positions")

class Trade(BaseModel):
    __tablename__ = "trades"
    
    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id"), nullable=False, index=True)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False, index=True)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey("instruments.id"), nullable=False, index=True)
    entry_price = Column(Numeric(10, 2), nullable=False)
    exit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    gross_pnl = Column(Numeric(10, 2), nullable=False)
    transaction_costs = Column(Numeric(10, 2), nullable=False, default=0)
    net_pnl = Column(Numeric(10, 2), nullable=False)
    exit_reason = Column(String(100), nullable=False)
    holding_period_seconds = Column(Integer, nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=False)
