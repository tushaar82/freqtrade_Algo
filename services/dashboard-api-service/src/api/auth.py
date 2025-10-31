"""
Authentication API Endpoints
VELOX Trading Platform
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from shared.schemas.api.user import TokenResponse, UserResponse
from shared.schemas.database.user import User
from ..database import get_db
from ..auth.password import verify_password
from ..auth.dependencies import jwt_manager

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    """Login with email and password"""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Generate tokens
    access_token = jwt_manager.create_access_token(user.id, user.email, user.role.value)
    refresh_token = jwt_manager.create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Annotated[Session, Depends(get_db)]
):
    """Refresh access token"""
    token_data = jwt_manager.verify_token(refresh_token, token_type="refresh")
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    access_token = jwt_manager.create_access_token(user.id, user.email, user.role.value)
    new_refresh_token = jwt_manager.create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.from_orm(user)
    )
