"""Pydantic schemas for notification-related models."""

from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field


class NotificationPreferencesBase(BaseModel):
    """Base schema for notification preferences."""
    
    receive_email_notifications: bool = True
    receive_telegram_notifications: bool = True
    daily_reminder_enabled: bool = False
    daily_reminder_time: time = time(9, 0, 0)


class UpdateNotificationSettingsRequest(BaseModel):
    """Request schema for updating notification settings."""
    
    receive_email_notifications: Optional[bool] = None
    receive_telegram_notifications: Optional[bool] = None
    daily_reminder_enabled: Optional[bool] = None
    daily_reminder_time: Optional[str] = Field(
        None, 
        description="Time in HH:MM:SS format",
        pattern=r"^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$"
    )
    telegram_chat_id: Optional[str] = None


class NotificationPreferencesResponse(NotificationPreferencesBase):
    """Response schema for notification preferences."""
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeliveryLogBase(BaseModel):
    """Base schema for delivery logs."""
    
    user_id: int
    post_id: Optional[int] = None
    channel: str = Field(..., description="'email' or 'telegram'")
    status: str = Field(..., description="'delivered', 'failed', or 'retried'")
    error_message: Optional[str] = None


class DeliveryLogResponse(DeliveryLogBase):
    """Response schema for delivery logs."""
    
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DeliveryLogListResponse(BaseModel):
    """Response schema for paginated delivery logs."""
    
    logs: list[DeliveryLogResponse]
    total: int
    page: int
    limit: int


class SendPostRequest(BaseModel):
    """Request schema for sending a post notification."""
    
    channel: str = Field(..., description="'email' or 'telegram'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "channel": "telegram"
            }
        }


class SendPostResponse(BaseModel):
    """Response schema for send post request."""
    
    status: str
    message: str
