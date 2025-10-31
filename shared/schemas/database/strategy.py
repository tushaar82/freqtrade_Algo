"""
Strategy Model
VELOX Trading Platform
"""
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class StrategyStatus(str, enum.Enum):
    """Strategy status enumeration"""
    DRAFT = "DRAFT"
    PAPER_TRADING = "PAPER_TRADING"
    LIVE = "LIVE"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"


class TradingMode(str, enum.Enum):
    """Trading mode enumeration"""
    PAPER = "PAPER"
    LIVE = "LIVE"


class Strategy(BaseModel):
    """Strategy model for trading algorithm configuration"""
    
    __tablename__ = "strategies"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    strategy_type = Column(String(100), nullable=False)  # e.g., "MovingAverageCrossover"
    config = Column(JSONB, nullable=False)  # Strategy-specific parameters
    status = Column(Enum(StrategyStatus), nullable=False, default=StrategyStatus.DRAFT, index=True)
    mode = Column(Enum(TradingMode), nullable=False, default=TradingMode.PAPER, index=True)
    risk_params = Column(JSONB, nullable=False)  # Position sizing, loss limits, etc.
    activated_at = Column(DateTime, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="strategies")
    strategy_instruments = relationship("StrategyInstrument", back_populates="strategy", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="strategy", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="strategy", cascade="all, delete-orphan")
    signals = relationship("Signal", back_populates="strategy", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Strategy(name='{self.name}', type='{self.strategy_type}', status='{self.status}')>"
