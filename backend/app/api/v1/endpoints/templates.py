"""Templates endpoints."""

from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.schemas.template import Template, TemplateCreate, TemplateUpdate
from app.schemas.user import User

router = APIRouter()


@router.get("/", response_model=List[Template])
async def get_templates(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    category: str | None = None
):
    """Get all available post templates.
    
    Args:
        current_user: Authenticated user
        db: Database session
        category: Optional filter by category
        
    Returns:
        List of templates
    """
    from app.db.models import Template as TemplateModel
    
    query = db.query(TemplateModel)
    
    # Filter by category if provided
    if category:
        query = query.filter(TemplateModel.category == category)
    
    # Order by category and name
    templates = query.order_by(TemplateModel.category, TemplateModel.name).all()
    
    return templates


@router.post("/", response_model=Template, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: TemplateCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Create a new template (Admin only)."""
    # TODO: Implement template creation
    # - Add admin check
    # - Create template in database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Create template not yet implemented"
    )


@router.put("/{template_id}", response_model=Template)
async def update_template(
    template_id: int,
    template: TemplateUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update an existing template (Admin only)."""
    # TODO: Implement template update
    # - Add admin check
    # - Update template in database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update template not yet implemented"
    )
