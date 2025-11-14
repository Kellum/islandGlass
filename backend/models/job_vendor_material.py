"""
Job Vendor Material Models
Pydantic models for job vendor materials
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class JobVendorMaterialCreate(BaseModel):
    """Model for creating a new job vendor material"""
    vendor_id: Optional[int] = None
    description: str = Field(..., description="Material description")
    template_id: Optional[int] = None
    ordered_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    cost: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0)
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    status: Optional[str] = Field(
        default="Not Ordered",
        description="Material status: Not Ordered, Ordered, In Transit, Delivered, Installed, Cancelled"
    )
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "vendor_id": 1,
                "description": "Shower door crystalline bypass",
                "ordered_date": "2025-01-10",
                "expected_delivery_date": "2025-01-20",
                "cost": 1250.00,
                "status": "Ordered",
                "tracking_number": "1Z999AA10123456784",
                "carrier": "UPS",
                "notes": "Need to confirm measurements before ordering"
            }
        }


class JobVendorMaterialUpdate(BaseModel):
    """Model for updating an existing job vendor material"""
    vendor_id: Optional[int] = None
    description: Optional[str] = None
    template_id: Optional[int] = None
    ordered_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    cost: Optional[Decimal] = Field(default=None, ge=0)
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "actual_delivery_date": "2025-01-18",
                "status": "Delivered",
                "notes": "Delivered 2 days early. Quality looks good."
            }
        }


class JobVendorMaterialResponse(BaseModel):
    """Model for job vendor material response"""
    material_id: int
    job_id: int
    vendor_id: Optional[int] = None
    description: str
    template_id: Optional[int] = None
    ordered_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    cost: Decimal
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    status: str
    notes: Optional[str] = None
    company_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Optional joined data
    vendor_name: Optional[str] = None
    template_name: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "material_id": 1,
                "job_id": 5,
                "vendor_id": 2,
                "description": "Shower door crystalline bypass",
                "ordered_date": "2025-01-10",
                "expected_delivery_date": "2025-01-20",
                "actual_delivery_date": "2025-01-18",
                "cost": 1250.00,
                "status": "Delivered",
                "tracking_number": "1Z999AA10123456784",
                "carrier": "UPS",
                "notes": "Delivered 2 days early. Quality looks good.",
                "vendor_name": "Glass Suppliers Inc",
                "created_at": "2025-01-10T10:00:00",
                "updated_at": "2025-01-18T14:30:00"
            }
        }
