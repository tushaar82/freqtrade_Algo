"""
Market Data Event Schemas
VELOX Trading Platform
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MarketTickEvent(BaseModel):
    """Schema for market data tick event"""
    instrument_id: UUID
    symbol: str
    exchange: str
    timestamp: datetime
    price: Decimal = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    bid_price: Optional[Decimal] = None
    ask_price: Optional[Decimal] = None
    bid_quantity: Optional[int] = None
    ask_quantity: Optional[int] = None
    open_interest: Optional[int] = None
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
