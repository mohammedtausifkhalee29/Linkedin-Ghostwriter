"""Posts endpoints."""

from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.db.models import Post as PostModel
from app.schemas.post import (
    Post,
    PostGenerateRequest,
    PostAutoGenerateRequest,
    PostSendRequest,
    PostDraftRequest,
    GeneratePostResponse,
    SendPostResponse,
    SaveDraftResponse
)
from app.schemas.user import User
from app.services.post_generator import PostGeneratorService
from app.services.notification_service import NotificationService

router = APIRouter()


@router.post("/generate", response_model=GeneratePostResponse, status_code=status.HTTP_200_OK)
async def generate_post(
    request: PostGenerateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Generate a new LinkedIn post using AI."""
    try:
        # Initialize post generator service
        post_service = PostGeneratorService(db)
        
        # Generate post using AI
        generated_content = await post_service.generate_post(
            post_type=request.post_type,
            message=request.message,
            tone=request.tone,
            reference_text=request.reference_text
        )
        
        # Save generated post to database
        new_post = PostModel(
            user_id=current_user.id,
            content=generated_content,
            generation_mode="manual",
            status="published",
            reference_text=request.reference_text
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        return GeneratePostResponse(
            post={"content": generated_content, "id": new_post.id}
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate post: {str(e)}"
        )


@router.post("/generate-auto", response_model=GeneratePostResponse, status_code=status.HTTP_200_OK)
async def generate_auto_post(
    request: PostAutoGenerateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Generate a LinkedIn post using a predefined template (Auto Post Mode).
    
    This endpoint generates posts based on selected templates with user-provided
    context. The template provides structure and the AI fills it with relevant content.
    """
    try:
        from app.db.models import Template as TemplateModel
        
        # Get the template
        template = db.query(TemplateModel).filter(
            TemplateModel.id == request.template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID {request.template_id} not found"
            )
        
        # Initialize post generator service
        post_service = PostGeneratorService(db)
        
        # Generate post using AI with template
        generated_content = await post_service.generate_template_post(
            template=template,
            message=request.message,
            tone=request.tone,
            reference_text=request.reference_text
        )
        
        # Save generated post to database
        new_post = PostModel(
            user_id=current_user.id,
            content=generated_content,
            template_id=template.id,
            generation_mode="auto",
            status="draft",  # Auto-generated posts start as drafts
            reference_text=request.reference_text
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        return GeneratePostResponse(
            post={
                "id": new_post.id,
                "content": generated_content,
                "template_name": template.name,
                "template_category": template.category,
                "template_structure": template.structure,
                "status": "draft"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate auto post: {str(e)}"
        )


@router.post("/send", response_model=SendPostResponse, status_code=status.HTTP_200_OK)
async def send_post(
    request: PostSendRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Send a generated post via notification channel."""
    try:
        notification_service = NotificationService()
        
        if request.channel == "telegram":
            # Check if user has Telegram configured
            if not current_user.telegram_chat_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Telegram chat ID not configured. Please set up Telegram first."
                )
            
            # Send via Telegram
            success = await notification_service.send_telegram(
                chat_id=current_user.telegram_chat_id,
                message=request.post_content
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send message via Telegram"
                )
                
            return SendPostResponse(
                status="success",
                message="Post sent successfully via Telegram"
            )
            
        elif request.channel == "email":
            # Send via email
            success = notification_service.send_email(
                recipient=current_user.email,
                subject="Your LinkedIn Post",
                body=request.post_content
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send email"
                )
                
            return SendPostResponse(
                status="success",
                message="Post sent successfully via email"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send post: {str(e)}"
        )


@router.post("/draft", response_model=SaveDraftResponse, status_code=status.HTTP_201_CREATED)
async def save_draft(
    request: PostDraftRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Save a generated post as a draft."""
    try:
        # Create draft post
        draft_post = PostModel(
            user_id=current_user.id,
            content=request.content,
            generation_mode="manual",
            status="draft",
            reference_text=request.reference_text
        )
        
        db.add(draft_post)
        db.commit()
        db.refresh(draft_post)
        
        return SaveDraftResponse(
            status="success",
            draft_id=draft_post.id,  # type: ignore
            message="Draft saved successfully"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save draft: {str(e)}"
        )


@router.get("/", response_model=List[Post])
async def get_posts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None
):
    """Get post history for the authenticated user."""
    try:
        query = db.query(PostModel).filter(PostModel.user_id == current_user.id)
        
        # Apply status filter if provided
        if status_filter in ["draft", "published"]:
            query = query.filter(PostModel.status == status_filter)
        
        posts = query.order_by(PostModel.created_at.desc()).offset(skip).limit(limit).all()
        
        return posts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch posts: {str(e)}"
        )


@router.get("/{post_id}", response_model=Post)
async def get_post(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get a specific post by ID."""
    post = db.query(PostModel).filter(
        PostModel.id == post_id,
        PostModel.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Delete a post."""
    post = db.query(PostModel).filter(
        PostModel.id == post_id,
        PostModel.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    db.delete(post)
    db.commit()
    
    return None
