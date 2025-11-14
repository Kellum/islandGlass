"""
Job Models for FastAPI
Pydantic models for job/PO management
"""
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class JobBase(BaseModel):
    """Base model for Job - matches database schema"""
    po_number: str
    client_id: int

    # PO Auto-Generation Fields
    location_code: Optional[str] = None  # '01', '02', or '03'
    is_remake: bool = False
    is_warranty: bool = False

    # Dates
    job_date: Optional[date] = None
    estimated_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None

    # Status - matches database CHECK constraint
    status: str = "Quote"

    # Financials
    total_estimate: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    material_cost: Optional[Decimal] = None
    labor_cost: Optional[Decimal] = None
    profit_margin: Optional[Decimal] = None

    # Details
    job_description: Optional[str] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None

    # Site Information
    site_address: Optional[str] = None
    site_contact_name: Optional[str] = None
    site_contact_phone: Optional[str] = None

    @field_validator('status')
    @classmethod
    def valid_status(cls, v: str) -> str:
        """Ensure status matches database constraints"""
        valid_statuses = [
            'Quote', 'Scheduled', 'In Progress', 'Pending Materials',
            'Ready for Install', 'Installed', 'Completed', 'Cancelled', 'On Hold'
        ]
        if v not in valid_statuses:
            raise ValueError(f'status must be one of: {", ".join(valid_statuses)}')
        return v

    @field_validator('po_number')
    @classmethod
    def po_number_not_empty(cls, v: str) -> str:
        """Ensure PO number is not empty"""
        if not v or not v.strip():
            raise ValueError('po_number cannot be empty')
        if len(v.strip()) < 3:
            raise ValueError('po_number must be at least 3 characters')
        return v.strip()

    @field_validator('location_code')
    @classmethod
    def valid_location_code(cls, v: Optional[str]) -> Optional[str]:
        """Ensure location_code is valid if provided"""
        if v is None:
            return v
        valid_codes = ['01', '02', '03']
        if v not in valid_codes:
            raise ValueError(f'location_code must be one of: {", ".join(valid_codes)}')
        return v

    @classmethod
    def model_validate(cls, *args, **kwargs):
        """Additional validation for remake/warranty constraint"""
        instance = super().model_validate(*args, **kwargs)
        if instance.is_remake and instance.is_warranty:
            raise ValueError('A job cannot be both a remake and a warranty job')
        return instance


class JobCreate(JobBase):
    """Create a new job"""
    pass


class JobUpdate(BaseModel):
    """Update an existing job - all fields optional"""
    client_id: Optional[int] = None
    location_code: Optional[str] = None
    is_remake: Optional[bool] = None
    is_warranty: Optional[bool] = None
    job_date: Optional[date] = None
    estimated_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    status: Optional[str] = None
    total_estimate: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    material_cost: Optional[Decimal] = None
    labor_cost: Optional[Decimal] = None
    profit_margin: Optional[Decimal] = None
    job_description: Optional[str] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None
    site_address: Optional[str] = None
    site_contact_name: Optional[str] = None
    site_contact_phone: Optional[str] = None

    @field_validator('status')
    @classmethod
    def valid_status(cls, v: Optional[str]) -> Optional[str]:
        """Ensure status matches database constraints if provided"""
        if v is None:
            return v
        valid_statuses = [
            'Quote', 'Scheduled', 'In Progress', 'Pending Materials',
            'Ready for Install', 'Installed', 'Completed', 'Cancelled', 'On Hold'
        ]
        if v not in valid_statuses:
            raise ValueError(f'status must be one of: {", ".join(valid_statuses)}')
        return v


class JobResponse(JobBase):
    """Job response with database fields"""
    job_id: int  # Database uses job_id, not id
    company_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    client_name: Optional[str] = None  # Client name for display

    class Config:
        from_attributes = True


class WorkItemBase(BaseModel):
    item_type: str  # 'Shower', 'Window', 'Mirror', 'Tabletop', 'Other'
    description: str
    quantity: int = 1
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    specifications: Optional[dict] = None


class WorkItemCreate(WorkItemBase):
    job_id: str


class WorkItemResponse(WorkItemBase):
    id: str
    job_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VendorMaterialBase(BaseModel):
    vendor_id: str
    material_description: str
    quantity: int = 1
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    ordered_date: Optional[date] = None
    expected_delivery: Optional[date] = None
    actual_delivery: Optional[date] = None
    status: str = "Ordered"  # Ordered, In Transit, Delivered, Installed


class VendorMaterialCreate(VendorMaterialBase):
    job_id: str


class VendorMaterialResponse(VendorMaterialBase):
    id: str
    job_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SiteVisitBase(BaseModel):
    visit_type: str  # Measure/Estimate, Remeasure, Install, etc.
    visit_date: date
    employee: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    visit_notes: Optional[str] = None
    outcome: Optional[str] = None


class SiteVisitCreate(SiteVisitBase):
    job_id: str


class SiteVisitResponse(SiteVisitBase):
    id: str
    job_id: str
    duration_minutes: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    """Extended job response with client name and summary data"""
    client_name: Optional[str] = None
    work_item_count: int = 0
    material_count: int = 0
    visit_count: int = 0
