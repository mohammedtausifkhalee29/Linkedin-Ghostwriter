"""Template management API endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.db.models import User
from app.schemas.template import (
    Template,
    TemplateCreate,
    TemplateUpdate,
    TemplateListResponse,
    TemplateVersionListResponse,
    TemplateStats
)
from app.services.template_service import template_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=TemplateListResponse)
async def get_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    tone: Optional[str] = Query(None, description="Filter by tone"),
    search: Optional[str] = Query(None, description="Search in name, category, or tone"),
    skip: int = Query(0, ge=0, description="Number of templates to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of templates to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all templates with optional filtering.
    
    - **category**: Filter by template category
    - **tone**: Filter by writing tone
    - **search**: Search in name, category, or tone
    - **skip**: Pagination offset
    - **limit**: Maximum results per page
    """
    templates, total = template_service.get_templates(
        db=db,
        category=category,
        tone=tone,
        search=search,
        skip=skip,
        limit=limit
    )
    
    return TemplateListResponse(templates=templates, total=total)


@router.get("/stats", response_model=TemplateStats)
async def get_template_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get template statistics.
    
    Returns:
    - Total number of templates
    - Available categories
    - Available tones
    - Most used template
    """
    stats = template_service.get_template_stats(db)
    return TemplateStats(**stats)


@router.get("/{template_id}", response_model=Template)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific template by ID.
    
    - **template_id**: Template ID to retrieve
    """
    template = template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
    return template


@router.post("/", response_model=Template, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new template (Admin only).
    
    Automatically creates an initial version (v1) for the template.
    
    - **name**: Template name
    - **category**: Template category (e.g., "Case Study", "Build in Public")
    - **tone**: Writing tone (e.g., "Professional", "Casual")
    - **structure**: Post structure (e.g., "Hook → Problem → Solution")
    - **example**: Optional example post
    - **prompt**: LLM prompt for generating posts
    """
    # TODO: Add admin role check when roles are implemented
    # For now, any authenticated user can create templates
    
    template = template_service.create_template(
        db=db,
        template_data=template_data,
        created_by=current_user.email
    )
    
    return template


@router.put("/{template_id}", response_model=Template)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing template (Admin only).
    
    Automatically creates a new version if prompt, structure, or tone changes.
    
    - **template_id**: Template ID to update
    - **name**: New template name (optional)
    - **category**: New category (optional)
    - **tone**: New tone (optional)
    - **structure**: New structure (optional)
    - **example**: New example (optional)
    - **prompt**: New prompt (optional)
    - **change_description**: Description of changes (optional)
    """
    # TODO: Add admin role check when roles are implemented
    
    template = template_service.update_template(
        db=db,
        template_id=template_id,
        template_data=template_data,
        updated_by=current_user.email
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
    
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a template (Admin only).
    
    Deletes the template and all its versions.
    Note: Posts created from this template will not be affected.
    
    - **template_id**: Template ID to delete
    """
    # TODO: Add admin role check when roles are implemented
    
    deleted = template_service.delete_template(db, template_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
    
    return None


@router.get("/{template_id}/versions", response_model=TemplateVersionListResponse)
async def get_template_versions(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get version history for a template (Admin only).
    
    Returns all versions ordered by version number (newest first).
    
    - **template_id**: Template ID to get versions for
    """
    # TODO: Add admin role check when roles are implemented
    
    # Verify template exists
    template = template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
    
    versions = template_service.get_template_versions(db, template_id)
    
    return TemplateVersionListResponse(
        versions=versions,
        total=len(versions),
        template_id=template_id,
        template_name=template.name
    )

