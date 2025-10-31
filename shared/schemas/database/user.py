"""
User Model
VELOX Trading Platform
"""
from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "ADMIN"
    INVESTOR = "INVESTOR"


class User(BaseModel):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.INVESTOR)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    strategies = relationship("Strategy", back_populates="owner", cascade="all, delete-orphan")
    broker_accounts = relationship("BrokerAccount", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(email='{self.email}', role='{self.role}')>"
