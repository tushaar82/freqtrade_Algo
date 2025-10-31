"""
FastAPI Authentication Dependencies
VELOX Trading Platform
"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .jwt import JWTManager, TokenData
from ..database import get_db

# Security scheme
security = HTTPBearer()

# JWT manager (will be initialized in main.py)
jwt_manager: JWTManager = None


def init_jwt_manager(secret_key: str, algorithm: str = "HS256") -> None:
    """Initialize JWT manager with configuration"""
    global jwt_manager
    jwt_manager = JWTManager(secret_key=secret_key, algorithm=algorithm)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)]
) -> TokenData:
    """
    Dependency to get current authenticated user from JWT token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = jwt_manager.verify_token(token, token_type="access")
    
    if token_data is None:
        raise credentials_exception
    
    # Verify user exists in database
    from shared.schemas.database.user import User
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None or not user.is_active:
        raise credentials_exception
    
    return token_data


async def require_admin(
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> TokenData:
    """
    Dependency to require admin role
    
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_investor_or_admin(
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> TokenData:
    """
    Dependency to require investor or admin role
    
    Raises:
        HTTPException: If user role is invalid
    """
    if current_user.role not in ["ADMIN", "INVESTOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Investor or Admin access required"
        )
    return current_user
