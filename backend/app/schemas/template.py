"""Pydantic schemas for template management."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TemplateBase(BaseModel):
    """Base template schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Template name")
    category: str = Field(..., min_length=1, max_length=100, description="Template category")
    tone: str = Field(..., min_length=1, max_length=100, description="Writing tone")
    structure: str = Field(..., min_length=1, description="Post structure (e.g., 'Hook → Problem → Solution')")
    example: Optional[str] = Field(None, description="Example post using this template")
    prompt: str = Field(..., min_length=1, description="LLM prompt for generating posts")


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating an existing template."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    tone: Optional[str] = Field(None, min_length=1, max_length=100)
    structure: Optional[str] = Field(None, min_length=1)
    example: Optional[str] = None
    prompt: Optional[str] = Field(None, min_length=1)
    change_description: Optional[str] = Field(None, description="Description of changes made")


class Template(TemplateBase):
    """Schema for template response."""
    
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TemplateListResponse(BaseModel):
    """Schema for listing templates."""
    
    templates: List[Template]
    total: int


class TemplateVersionBase(BaseModel):
    """Base schema for template versions."""
    
    version: int
    prompt: str
    structure: str
    tone: str
    created_at: datetime
    created_by: str
    change_description: Optional[str] = None


class TemplateVersion(TemplateVersionBase):
    """Schema for template version responses."""
    
    id: int
    template_id: int
    
    model_config = ConfigDict(from_attributes=True)


class TemplateVersionListResponse(BaseModel):
    """Schema for listing template versions."""
    
    versions: List[TemplateVersion]
    total: int
    template_id: int
    template_name: str


class TemplateWithVersions(Template):
    """Schema for template with version count."""
    
    version_count: int = Field(default=0, description="Number of versions for this template")


class TemplateStats(BaseModel):
    """Schema for template statistics."""
    
    total_templates: int
    categories: List[str]
    tones: List[str]
    most_used_template_id: Optional[int] = None
    most_used_template_name: Optional[str] = None

