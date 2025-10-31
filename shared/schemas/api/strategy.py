"""
Strategy API Schemas
VELOX Trading Platform
"""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class StrategyCreate(BaseModel):
    """Schema for creating a new strategy"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    strategy_type: str = Field(..., min_length=1)
    config: dict[str, Any]
    risk_params: dict[str, Any]
    instruments: list[UUID] = Field(default_factory=list)


class StrategyUpdate(BaseModel):
    """Schema for updating a strategy"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    risk_params: Optional[dict[str, Any]] = None


class StrategyResponse(BaseModel):
    """Schema for strategy response"""
    id: UUID
    name: str
    description: Optional[str]
    strategy_type: str
    status: str
    mode: str
    created_at: datetime
    activated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StrategyDetail(StrategyResponse):
    """Schema for detailed strategy response"""
    config: dict[str, Any]
    risk_params: dict[str, Any]
    active_positions: int = 0
    total_pnl: float = 0.0
