"""
Instrument Model
VELOX Trading Platform
"""
from datetime import date
from decimal import Decimal
from sqlalchemy import Boolean, Column, Date, Enum, Integer, Numeric, String, UniqueConstraint
import enum

from .base import BaseModel


class Exchange(str, enum.Enum):
    """Exchange enumeration"""
    NSE = "NSE"
    BSE = "BSE"
    MCX = "MCX"
    NFO = "NFO"


class InstrumentType(str, enum.Enum):
    """Instrument type enumeration"""
    EQUITY = "EQUITY"
    FUTURE = "FUTURE"
    CALL_OPTION = "CALL_OPTION"
    PUT_OPTION = "PUT_OPTION"


class Instrument(BaseModel):
    """Instrument model for stocks and options"""
    
    __tablename__ = "instruments"
    __table_args__ = (
        UniqueConstraint('symbol', 'exchange', name='uix_symbol_exchange'),
    )
    
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(Enum(Exchange), nullable=False, index=True)
    instrument_type = Column(Enum(InstrumentType), nullable=False, index=True)
    lot_size = Column(Integer, nullable=False, default=1)
    tick_size = Column(Numeric(10, 4), nullable=False, default=Decimal("0.05"))
    circuit_limit_upper = Column(Numeric(10, 2), nullable=True)
    circuit_limit_lower = Column(Numeric(10, 2), nullable=True)
    expiry_date = Column(Date, nullable=True)  # For F&O
    strike_price = Column(Numeric(10, 2), nullable=True)  # For options
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<Instrument(symbol='{self.symbol}', exchange='{self.exchange}', type='{self.instrument_type}')>"
