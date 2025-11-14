"""
Work Item Models - Track work being done per job

Work items represent individual pieces of work on a job (PO):
- Shower installations
- Window/IG units
- Mirrors
- Tabletops
- Mirror frames
- Custom work
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class WorkItemBase(BaseModel):
    """Base fields for work items"""
    job_id: int
    work_type: str = Field(..., pattern="^(Shower|Window/IG|Mirror|Tabletop|Mirror Frame|Custom)$")
    quantity: int = Field(default=1, ge=1)
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None  # JSONB - flexible specs
    estimated_cost: Decimal = Field(default=Decimal("0.00"), ge=0)
    actual_cost: Decimal = Field(default=Decimal("0.00"), ge=0)
    status: str = Field(default="Pending")
    sort_order: int = Field(default=0)
    notes: Optional[str] = None


class WorkItemCreate(WorkItemBase):
    """Fields required to create a work item"""
    pass


class WorkItemUpdate(BaseModel):
    """Fields that can be updated on a work item"""
    job_id: Optional[int] = None
    work_type: Optional[str] = Field(None, pattern="^(Shower|Window/IG|Mirror|Tabletop|Mirror Frame|Custom)$")
    quantity: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    actual_cost: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = None
    sort_order: Optional[int] = None
    notes: Optional[str] = None


class WorkItem(WorkItemBase):
    """Complete work item with all fields"""
    item_id: int
    company_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
