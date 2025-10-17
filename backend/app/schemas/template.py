"""Template-related Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel


class TemplateBase(BaseModel):
    """Base template schema."""
    
    name: str
    category: str
    structure: str
    prompt: str


class TemplateCreate(TemplateBase):
    """Schema for template creation."""
    
    pass


class TemplateUpdate(BaseModel):
    """Schema for template updates."""
    
    name: str | None = None
    category: str | None = None
    structure: str | None = None
    prompt: str | None = None


class Template(TemplateBase):
    """Schema for template response."""
    
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}
