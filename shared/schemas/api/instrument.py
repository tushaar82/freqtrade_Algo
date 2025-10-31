"""
Instrument API Schemas
VELOX Trading Platform
"""
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InstrumentResponse(BaseModel):
    """Schema for instrument response"""
    id: UUID
    symbol: str
    exchange: str
    instrument_type: str
    lot_size: int
    tick_size: Decimal
    circuit_limit_upper: Optional[Decimal] = None
    circuit_limit_lower: Optional[Decimal] = None
    expiry_date: Optional[date] = None
    strike_price: Optional[Decimal] = None
    is_active: bool
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }
