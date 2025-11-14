"""
Vendor Models for FastAPI
Pydantic models for vendor management
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class VendorBase(BaseModel):
    """Base model for Vendor - matches database schema"""
    vendor_name: str
    vendor_type: Optional[str] = None

    # Contact Information
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    # Address
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

    # Status & Notes
    is_active: bool = True
    notes: Optional[str] = None

    @field_validator('vendor_type')
    @classmethod
    def valid_vendor_type(cls, v: Optional[str]) -> Optional[str]:
        """Ensure vendor_type matches database constraints if provided"""
        if v is None:
            return v
        valid_types = ['Glass', 'Hardware', 'Materials', 'Services', 'Other']
        if v not in valid_types:
            raise ValueError(f'vendor_type must be one of: {", ".join(valid_types)}')
        return v

    @field_validator('vendor_name')
    @classmethod
    def vendor_name_not_empty(cls, v: str) -> str:
        """Ensure vendor name is not empty"""
        if not v or not v.strip():
            raise ValueError('vendor_name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('vendor_name must be at least 2 characters')
        return v.strip()


class VendorCreate(VendorBase):
    """Create a new vendor"""
    pass


class VendorUpdate(BaseModel):
    """Update an existing vendor - all fields optional"""
    vendor_name: Optional[str] = None
    vendor_type: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

    @field_validator('vendor_type')
    @classmethod
    def valid_vendor_type(cls, v: Optional[str]) -> Optional[str]:
        """Ensure vendor_type matches database constraints if provided"""
        if v is None:
            return v
        valid_types = ['Glass', 'Hardware', 'Materials', 'Services', 'Other']
        if v not in valid_types:
            raise ValueError(f'vendor_type must be one of: {", ".join(valid_types)}')
        return v

    @field_validator('vendor_name')
    @classmethod
    def vendor_name_valid(cls, v: Optional[str]) -> Optional[str]:
        """Ensure vendor name is at least 2 characters if provided"""
        if v is not None and v.strip() and len(v.strip()) < 2:
            raise ValueError('vendor_name must be at least 2 characters')
        return v.strip() if v else v


class VendorResponse(VendorBase):
    """Vendor response with database fields"""
    vendor_id: int
    company_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
