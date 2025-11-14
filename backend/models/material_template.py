"""
Material Template Models - Master list of materials for quick job entry

Templates are reusable material definitions that can be:
- Quickly added to jobs
- Associated with preferred vendors
- Categorized by type (Glass, Hardware, Frame, Misc, Custom)
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MaterialTemplateBase(BaseModel):
    """Base fields for material templates"""
    template_name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, pattern="^(Glass|Hardware|Frame|Misc|Custom)$")
    description: Optional[str] = None
    typical_vendor_id: Optional[int] = None
    is_active: bool = True
    sort_order: int = 0


class MaterialTemplateCreate(MaterialTemplateBase):
    """Fields required to create a material template"""
    pass


class MaterialTemplateUpdate(BaseModel):
    """Fields that can be updated on a material template"""
    template_name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, pattern="^(Glass|Hardware|Frame|Misc|Custom)$")
    description: Optional[str] = None
    typical_vendor_id: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class MaterialTemplate(MaterialTemplateBase):
    """Complete material template with all fields"""
    template_id: int
    company_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
