"""
Site Visit Models
Pydantic models for job site visits API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time, datetime
from decimal import Decimal


class SiteVisitBase(BaseModel):
    """Base site visit model with common fields"""
    job_id: int
    visit_date: date
    visit_time: Optional[time] = None
    duration_hours: Optional[Decimal] = None
    visit_type: str  # 'Measure/Estimate', 'Install', 'Remeasure', 'Finals', 'Adjustment', 'Delivery', 'Inspection', 'Service Call', 'Custom'
    custom_visit_type: Optional[str] = None
    employee_name: Optional[str] = None
    employee_id: Optional[str] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    issues_found: Optional[str] = None
    photos: Optional[List[str]] = None
    completed: bool = False


class SiteVisitCreate(SiteVisitBase):
    """Model for creating a new site visit"""
    pass


class SiteVisitUpdate(BaseModel):
    """Model for updating a site visit - all fields optional"""
    job_id: Optional[int] = None
    visit_date: Optional[date] = None
    visit_time: Optional[time] = None
    duration_hours: Optional[Decimal] = None
    visit_type: Optional[str] = None
    custom_visit_type: Optional[str] = None
    employee_name: Optional[str] = None
    employee_id: Optional[str] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    issues_found: Optional[str] = None
    photos: Optional[List[str]] = None
    completed: Optional[bool] = None


class SiteVisitResponse(SiteVisitBase):
    """Model for site visit responses"""
    visit_id: int
    company_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
