"""User-related Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str


class UserUpdate(BaseModel):
    """Schema for user updates."""
    
    telegram_chat_id: Optional[str] = None


class UserInDB(UserBase):
    """Schema for user in database."""
    
    id: int
    hashed_password: str
    telegram_chat_id: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class User(UserBase):
    """Schema for user response."""
    
    id: int
    telegram_chat_id: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token."""
    
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token data."""
    
    email: Optional[str] = None
