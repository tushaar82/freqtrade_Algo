"""
Signal Event Schemas
VELOX Trading Platform
"""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SignalEvent(BaseModel):
    """Schema for trading signal event"""
    signal_id: UUID
    strategy_id: UUID
    strategy_name: str
    instrument_id: UUID
    symbol: str
    signal_type: str = Field(..., pattern="^(ENTRY_LONG|ENTRY_SHORT|EXIT_LONG|EXIT_SHORT)$")
    strength: float = Field(..., ge=0.0, le=1.0)
    indicators: dict[str, Any]
    reasoning: str
    recommended_quantity: int = Field(..., gt=0)
    recommended_price: float = Field(..., gt=0)
    generated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
