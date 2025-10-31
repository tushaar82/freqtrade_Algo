"""
Order Event Schemas
VELOX Trading Platform
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OrderFill(BaseModel):
    """Schema for order fill details"""
    fill_id: UUID
    quantity: int
    price: Decimal
    timestamp: datetime


class OrderEvent(BaseModel):
    """Schema for order event"""
    order_id: UUID
    strategy_id: UUID
    instrument_id: UUID
    symbol: str
    side: str = Field(..., pattern="^(BUY|SELL)$")
    order_type: str = Field(..., pattern="^(MARKET|LIMIT|STOP_LOSS|STOP_LOSS_MARKET)$")
    quantity: int = Field(..., gt=0)
    filled_quantity: int = Field(..., ge=0)
    average_fill_price: Optional[Decimal] = None
    status: str
    mode: str = Field(..., pattern="^(PAPER|LIVE)$")
    broker_order_id: Optional[str] = None
    fills: list[OrderFill] = Field(default_factory=list)
    timestamp: datetime
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
