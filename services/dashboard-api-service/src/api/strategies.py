"""
Strategy API Endpoints
VELOX Trading Platform
"""
import sys
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from shared.schemas.api.strategy import StrategyCreate, StrategyUpdate, StrategyResponse
from shared.schemas.database.strategy import Strategy, StrategyStatus
from ..database import get_db
from ..auth.dependencies import get_current_user, TokenData

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.get("/", response_model=list[StrategyResponse])
async def list_strategies(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """List all strategies for current user"""
    strategies = db.query(Strategy).filter(Strategy.owner_id == current_user.user_id).all()
    return strategies


@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Create new strategy"""
    strategy = Strategy(
        name=strategy_data.name,
        description=strategy_data.description,
        owner_id=current_user.user_id,
        strategy_type=strategy_data.strategy_type,
        config=strategy_data.config,
        risk_params=strategy_data.risk_params,
        status=StrategyStatus.DRAFT
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get strategy by ID"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.owner_id == current_user.user_id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return strategy


@router.patch("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: UUID,
    strategy_data: StrategyUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Update strategy"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.owner_id == current_user.user_id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy_data.name:
        strategy.name = strategy_data.name
    if strategy_data.description:
        strategy.description = strategy_data.description
    if strategy_data.config:
        strategy.config = strategy_data.config
    if strategy_data.risk_params:
        strategy.risk_params = strategy_data.risk_params
    
    db.commit()
    db.refresh(strategy)
    return strategy


@router.post("/{strategy_id}/activate")
async def activate_strategy(
    strategy_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Activate strategy"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.owner_id == current_user.user_id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    strategy.status = StrategyStatus.PAPER_TRADING
    db.commit()
    
    return {"message": "Strategy activated", "strategy_id": str(strategy_id)}


@router.post("/{strategy_id}/pause")
async def pause_strategy(
    strategy_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Pause strategy"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.owner_id == current_user.user_id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    strategy.status = StrategyStatus.PAUSED
    db.commit()
    
    return {"message": "Strategy paused", "strategy_id": str(strategy_id)}


@router.post("/{strategy_id}/stop")
async def stop_strategy(
    strategy_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Stop strategy"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.owner_id == current_user.user_id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    strategy.status = StrategyStatus.STOPPED
    db.commit()
    
    return {"message": "Strategy stopped", "strategy_id": str(strategy_id)}
