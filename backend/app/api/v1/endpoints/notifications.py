"""Notifications API endpoints."""

import logging
from datetime import time as time_obj
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.db.models import User, NotificationPreferences, DeliveryLog, Post
from app.schemas.notification import (
    NotificationPreferencesResponse,
    UpdateNotificationSettingsRequest,
    DeliveryLogResponse,
    DeliveryLogListResponse,
    SendPostRequest,
    SendPostResponse
)
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/settings", response_model=NotificationPreferencesResponse)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notification settings for the authenticated user.
    
    Returns:
        NotificationPreferencesResponse: User's notification preferences
    """
    preferences = db.query(NotificationPreferences).filter(
        NotificationPreferences.user_id == current_user.id
    ).first()
    
    if not preferences:
        # Create default preferences if they don't exist
        preferences = NotificationPreferences(
            user_id=current_user.id,
            receive_email_notifications=True,
            receive_telegram_notifications=True,
            daily_reminder_enabled=False,
            daily_reminder_time=time_obj(9, 0, 0)
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    return preferences


@router.put("/settings", response_model=NotificationPreferencesResponse)
async def update_notification_settings(
    settings: UpdateNotificationSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update notification settings for the authenticated user.
    
    Args:
        settings: Updated notification settings
        
    Returns:
        NotificationPreferencesResponse: Updated preferences
    """
    preferences = db.query(NotificationPreferences).filter(
        NotificationPreferences.user_id == current_user.id
    ).first()
    
    if not preferences:
        # Create new preferences
        preferences = NotificationPreferences(user_id=current_user.id)
        db.add(preferences)
    
    # Update fields if provided
    if settings.receive_email_notifications is not None:
        preferences.receive_email_notifications = settings.receive_email_notifications
    
    if settings.receive_telegram_notifications is not None:
        preferences.receive_telegram_notifications = settings.receive_telegram_notifications
    
    if settings.daily_reminder_enabled is not None:
        preferences.daily_reminder_enabled = settings.daily_reminder_enabled
    
    if settings.daily_reminder_time is not None:
        try:
            # Parse time string (HH:MM:SS)
            time_parts = settings.daily_reminder_time.split(':')
            reminder_time = time_obj(
                hour=int(time_parts[0]),
                minute=int(time_parts[1]),
                second=int(time_parts[2]) if len(time_parts) > 2 else 0
            )
            preferences.daily_reminder_time = reminder_time
        except (ValueError, IndexError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid time format. Use HH:MM:SS format. Error: {str(e)}"
            )
    
    # Update telegram_chat_id in user table if provided
    if settings.telegram_chat_id is not None:
        current_user.telegram_chat_id = settings.telegram_chat_id
        db.add(current_user)
    
    db.commit()
    db.refresh(preferences)
    
    logger.info(f"Notification settings updated for user {current_user.id}")
    
    return preferences


@router.get("/logs", response_model=DeliveryLogListResponse)
async def get_delivery_logs(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get delivery logs for the authenticated user with pagination.
    
    Args:
        page: Page number (default: 1)
        limit: Items per page (default: 20)
        
    Returns:
        DeliveryLogListResponse: Paginated delivery logs
    """
    # Calculate offset
    offset = (page - 1) * limit
    
    # Get total count
    total = db.query(DeliveryLog).filter(
        DeliveryLog.user_id == current_user.id
    ).count()
    
    # Get paginated logs
    logs = db.query(DeliveryLog).filter(
        DeliveryLog.user_id == current_user.id
    ).order_by(DeliveryLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return DeliveryLogListResponse(
        logs=[DeliveryLogResponse.from_orm(log) for log in logs],
        total=total,
        page=page,
        limit=limit
    )


@router.post("/posts/{post_id}/send", response_model=SendPostResponse)
async def send_post_notification(
    post_id: int,
    request: SendPostRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a post notification via the specified channel.
    
    Args:
        post_id: ID of the post to send
        request: Channel to send via ('email' or 'telegram')
        background_tasks: FastAPI background tasks
        
    Returns:
        SendPostResponse: Status message
    """
    # Verify post belongs to user
    post = db.query(Post).filter(
        Post.id == post_id,
        Post.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Validate channel
    if request.channel not in ['email', 'telegram']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid channel. Must be 'email' or 'telegram'"
        )
    
    # Add task to background
    async def send_notification_task():
        success, error = await notification_service.send_post_notification(
            db=db,
            user_id=current_user.id,
            post=post,
            channel=request.channel
        )
        if not success:
            logger.warning(f"Failed to send notification: {error}")
    
    background_tasks.add_task(send_notification_task)
    
    return SendPostResponse(
        status="queued",
        message=f"Post delivery has been queued for {request.channel}"
    )


@router.post("/telegram/callback")
async def telegram_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle callbacks from Telegram inline buttons.
    
    This endpoint receives Telegram webhook callbacks when users
    interact with inline buttons (Approve, Regenerate, Delete).
    
    Args:
        request: Raw request from Telegram
        
    Returns:
        Empty response (200 OK)
    """
    try:
        # Parse Telegram Update object
        data = await request.json()
        
        # Extract callback query
        callback_query = data.get('callback_query')
        if not callback_query:
            return {"ok": True}
        
        callback_data = callback_query.get('data', '')
        chat_id = callback_query['from']['id']
        message_id = callback_query['message']['message_id']
        
        # Parse callback data (format: action_postid)
        if '_' not in callback_data:
            return {"ok": True}
        
        action, post_id_str = callback_data.split('_', 1)
        post_id = int(post_id_str)
        
        # Find the user by telegram_chat_id
        user = db.query(User).filter(
            User.telegram_chat_id == str(chat_id)
        ).first()
        
        if not user:
            logger.warning(f"User not found for telegram chat_id: {chat_id}")
            return {"ok": True}
        
        # Find the post
        post = db.query(Post).filter(
            Post.id == post_id,
            Post.user_id == user.id
        ).first()
        
        if not post:
            logger.warning(f"Post {post_id} not found for user {user.id}")
            return {"ok": True}
        
        # Handle actions
        if action == 'approve':
            # Update post status to published
            post.status = 'published'
            db.commit()
            response_text = "✅ Post approved and marked as published!"
            logger.info(f"Post {post_id} approved by user {user.id}")
        
        elif action == 'regenerate':
            # Mark post for regeneration (could trigger a background task)
            response_text = "♻️ Regeneration requested. Please use the app to regenerate."
            logger.info(f"Regeneration requested for post {post_id} by user {user.id}")
        
        elif action == 'delete':
            # Delete the post
            db.delete(post)
            db.commit()
            response_text = "🗑️ Post deleted successfully."
            logger.info(f"Post {post_id} deleted by user {user.id}")
        
        else:
            response_text = "Unknown action."
        
        # Send response back to Telegram (optional)
        # You can use notification_service.telegram_bot.answer_callback_query()
        # and edit_message_text() here if needed
        
        return {"ok": True, "response": response_text}
    
    except Exception as e:
        logger.error(f"Error processing Telegram callback: {e}")
        return {"ok": False, "error": str(e)}
