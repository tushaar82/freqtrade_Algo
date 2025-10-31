"""
Position API Endpoints
VELOX Trading Platform
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth.dependencies import get_current_user, TokenData

router = APIRouter(prefix="/positions", tags=["positions"])


@router.get("/")
async def list_positions(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """List all positions"""
    # TODO: Query positions from database
    return {"positions": []}


@router.get("/{position_id}")
async def get_position(
    position_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get position by ID"""
    # TODO: Query specific position
    return {"position_id": str(position_id)}
