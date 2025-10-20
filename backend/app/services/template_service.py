"""Template service for managing templates and versioning."""

import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.db.models import Template, TemplateVersion, Post
from app.schemas.template import TemplateCreate, TemplateUpdate

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for template CRUD operations and version management."""
    
    @staticmethod
    def create_template(db: Session, template_data: TemplateCreate, created_by: str) -> Template:
        """
        Create a new template and initial version.
        
        Args:
            db: Database session
            template_data: Template creation data
            created_by: Email or ID of the user creating the template
            
        Returns:
            Created template
        """
        # Create template
        template = Template(
            name=template_data.name,
            category=template_data.category,
            tone=template_data.tone,
            structure=template_data.structure,
            example=template_data.example,
            prompt=template_data.prompt
        )
        db.add(template)
        db.flush()  # Flush to get the template ID
        
        # Create initial version
        initial_version = TemplateVersion(
            template_id=template.id,
            version=1,
            prompt=template_data.prompt,
            structure=template_data.structure,
            tone=template_data.tone,
            created_by=created_by,
            change_description="Initial template creation"
        )
        db.add(initial_version)
        db.commit()
        db.refresh(template)
        
        logger.info(f"Created template '{template.name}' (ID: {template.id}) by {created_by}")
        return template
    
    @staticmethod
    def get_template(db: Session, template_id: int) -> Optional[Template]:
        """
        Get a template by ID.
        
        Args:
            db: Database session
            template_id: Template ID
            
        Returns:
            Template or None if not found
        """
        return db.query(Template).filter(Template.id == template_id).first()
    
    @staticmethod
    def get_templates(
        db: Session,
        category: Optional[str] = None,
        tone: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Template], int]:
        """
        Get all templates with optional filtering.
        
        Args:
            db: Database session
            category: Filter by category
            tone: Filter by tone
            search: Search in name, category, or tone
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (templates list, total count)
        """
        query = db.query(Template)
        
        # Apply filters
        if category:
            query = query.filter(Template.category == category)
        if tone:
            query = query.filter(Template.tone == tone)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Template.name.ilike(search_pattern),
                    Template.category.ilike(search_pattern),
                    Template.tone.ilike(search_pattern)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        templates = query.order_by(Template.created_at.desc()).offset(skip).limit(limit).all()
        
        return templates, total
    
    @staticmethod
    def update_template(
        db: Session,
        template_id: int,
        template_data: TemplateUpdate,
        updated_by: str
    ) -> Optional[Template]:
        """
        Update a template and create a new version.
        
        Args:
            db: Database session
            template_id: Template ID to update
            template_data: Update data
            updated_by: Email or ID of the user updating the template
            
        Returns:
            Updated template or None if not found
        """
        template = db.query(Template).filter(Template.id == template_id).first()
        if not template:
            return None
        
        # Track what changed
        changes = []
        version_needed = False
        
        # Update fields
        if template_data.name is not None:
            template.name = template_data.name
            changes.append(f"name: {template_data.name}")
        
        if template_data.category is not None:
            template.category = template_data.category
            changes.append(f"category: {template_data.category}")
        
        if template_data.tone is not None and template_data.tone != template.tone:
            template.tone = template_data.tone
            changes.append(f"tone: {template_data.tone}")
            version_needed = True
        
        if template_data.structure is not None and template_data.structure != template.structure:
            template.structure = template_data.structure
            changes.append(f"structure updated")
            version_needed = True
        
        if template_data.example is not None:
            template.example = template_data.example
            changes.append(f"example updated")
        
        if template_data.prompt is not None and template_data.prompt != template.prompt:
            template.prompt = template_data.prompt
            changes.append(f"prompt updated")
            version_needed = True
        
        # Create new version if significant changes (prompt, structure, or tone)
        if version_needed:
            latest_version = db.query(func.max(TemplateVersion.version)).filter(
                TemplateVersion.template_id == template_id
            ).scalar() or 0
            
            new_version = TemplateVersion(
                template_id=template_id,
                version=latest_version + 1,
                prompt=template.prompt,
                structure=template.structure,
                tone=template.tone,
                created_by=updated_by,
                change_description=template_data.change_description or ", ".join(changes)
            )
            db.add(new_version)
            logger.info(f"Created version {new_version.version} for template {template_id}")
        
        db.commit()
        db.refresh(template)
        
        logger.info(f"Updated template '{template.name}' (ID: {template.id}) by {updated_by}")
        return template
    
    @staticmethod
    def delete_template(db: Session, template_id: int) -> bool:
        """
        Delete a template and all its versions.
        
        Args:
            db: Database session
            template_id: Template ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        template = db.query(Template).filter(Template.id == template_id).first()
        if not template:
            return False
        
        # Check if template is used in posts
        posts_count = db.query(func.count(Post.id)).filter(Post.template_id == template_id).scalar()
        if posts_count > 0:
            logger.warning(f"Template {template_id} is used in {posts_count} posts")
        
        template_name = template.name
        db.delete(template)
        db.commit()
        
        logger.info(f"Deleted template '{template_name}' (ID: {template_id})")
        return True
    
    @staticmethod
    def get_template_versions(db: Session, template_id: int) -> List[TemplateVersion]:
        """
        Get all versions for a template.
        
        Args:
            db: Database session
            template_id: Template ID
            
        Returns:
            List of template versions ordered by version descending
        """
        return db.query(TemplateVersion).filter(
            TemplateVersion.template_id == template_id
        ).order_by(TemplateVersion.version.desc()).all()
    
    @staticmethod
    def get_template_stats(db: Session) -> dict:
        """
        Get statistics about templates.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with statistics
        """
        total_templates = db.query(func.count(Template.id)).scalar()
        
        # Get unique categories
        categories = db.query(Template.category).distinct().all()
        categories = [c[0] for c in categories]
        
        # Get unique tones
        tones = db.query(Template.tone).distinct().all()
        tones = [t[0] for t in tones]
        
        # Get most used template
        most_used = db.query(
            Template.id,
            Template.name,
            func.count(Post.id).label('usage_count')
        ).outerjoin(Post, Template.id == Post.template_id).group_by(
            Template.id
        ).order_by(func.count(Post.id).desc()).first()
        
        return {
            "total_templates": total_templates,
            "categories": sorted(categories),
            "tones": sorted(tones),
            "most_used_template_id": most_used[0] if most_used else None,
            "most_used_template_name": most_used[1] if most_used else None,
            "most_used_count": most_used[2] if most_used else 0
        }


# Create singleton instance
template_service = TemplateService()
