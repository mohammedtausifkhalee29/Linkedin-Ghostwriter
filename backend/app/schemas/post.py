"""Post-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel


class PostGenerateRequest(BaseModel):
    """Schema for post generation request."""
    
    mode: Literal["manual", "auto"]
    message: str
    template_id: Optional[int] = None
    post_type: Optional[str] = None  # For manual mode
    tone: Optional[str] = None
    references: Optional[str] = None
    additional_context: Optional[str] = None


class PostBase(BaseModel):
    """Base post schema."""
    
    content: str
    generation_mode: str


class PostCreate(PostBase):
    """Schema for post creation."""
    
    user_id: int
    template_id: Optional[int] = None


class Post(PostBase):
    """Schema for post response."""
    
    id: int
    user_id: int
    template_id: Optional[int] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class PostSendRequest(BaseModel):
    """Schema for sending a post."""
    
    channel: Literal["telegram", "email"]
