"""Post-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class PostGenerateRequest(BaseModel):
    """Schema for post generation request."""
    
    post_type: str = Field(..., description="Type of post (e.g., Motivational, Case Study, How-To)")
    message: str = Field(..., min_length=1, max_length=2000, description="Main message for the post")
    tone: str = Field(..., description="Desired tone of the post")
    reference_text: Optional[str] = Field(None, description="Reference text from uploads")


class PostSendRequest(BaseModel):
    """Schema for sending a post."""
    
    post_content: str = Field(..., description="Content of the post to send")
    channel: Literal["telegram", "email"] = Field(..., description="Delivery channel")


class PostDraftRequest(BaseModel):
    """Schema for saving a post draft."""
    
    content: str = Field(..., description="Post content")
    reference_text: Optional[str] = Field(None, description="Reference text used")


class PostBase(BaseModel):
    """Base post schema."""
    
    content: str
    generation_mode: str
    status: str = "published"


class PostCreate(PostBase):
    """Schema for post creation."""
    
    user_id: int
    template_id: Optional[int] = None
    reference_text: Optional[str] = None


class Post(PostBase):
    """Schema for post response."""
    
    id: int
    user_id: int
    template_id: Optional[int] = None
    reference_text: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class GeneratePostResponse(BaseModel):
    """Schema for post generation response."""
    
    post: dict = Field(..., description="Generated post object")


class SendPostResponse(BaseModel):
    """Schema for send post response."""
    
    status: Literal["success", "error"]
    message: str


class SaveDraftResponse(BaseModel):
    """Schema for save draft response."""
    
    status: Literal["success", "error"]
    draft_id: Optional[int] = None
    message: str
