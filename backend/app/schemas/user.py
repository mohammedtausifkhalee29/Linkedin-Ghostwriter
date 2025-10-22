"""User-related Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema."""
    
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(min_length=6, max_length=72)
    
    @field_validator('password')
    @classmethod
    def validate_password_bytes(cls, v: str) -> str:
        """Ensure password doesn't exceed bcrypt's 72 byte limit."""
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot exceed 72 bytes')
        return v


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
