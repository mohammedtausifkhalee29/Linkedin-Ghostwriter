"""Posts endpoints."""

from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.schemas.post import Post, PostGenerateRequest, PostSendRequest
from app.schemas.user import User
from app.services.post_generator import PostGeneratorService
from app.services.notification_service import NotificationService

router = APIRouter()


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def generate_post(
    request: PostGenerateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Generate a new LinkedIn post."""
    # TODO: Implement post generation
    # - Use PostGeneratorService
    # - Save to database
    # - Return generated post
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Post generation not yet implemented"
    )


@router.get("/", response_model=List[Post])
async def get_posts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get post history for the authenticated user."""
    # TODO: Implement fetching user's posts
    # - Query posts from database for current user
    # - Return paginated results
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get posts not yet implemented"
    )


@router.post("/{post_id}/send", status_code=status.HTTP_200_OK)
async def send_post(
    post_id: int,
    request: PostSendRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Send a generated post via notification channel."""
    # TODO: Implement post sending
    # - Fetch post from database
    # - Verify ownership
    # - Send via NotificationService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Send post not yet implemented"
    )
