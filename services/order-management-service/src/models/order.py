"""
Order Model
VELOX Trading Platform
"""
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
from shared.schemas.database.base import BaseModel


class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Order(BaseModel):
    __tablename__ = "orders"
    
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False, index=True)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey("instruments.id"), nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    quantity = Column(Integer, nullable=False)
    filled_quantity = Column(Integer, nullable=False, default=0)
    price = Column(Numeric(10, 2), nullable=True)  # For limit orders
    stop_price = Column(Numeric(10, 2), nullable=True)  # For stop orders
    average_fill_price = Column(Numeric(10, 2), nullable=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING, index=True)
    mode = Column(String(10), nullable=False, index=True)  # PAPER or LIVE
    broker_order_id = Column(String(100), nullable=True)
    fills = Column(JSONB, nullable=False, default=list)  # List of fill details
    rejection_reason = Column(String(500), nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    filled_at = Column(DateTime, nullable=True)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, side={self.side}, status={self.status})>"
