"""
Client Models for FastAPI
Pydantic models for client management
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class ClientContactBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_primary: bool = False

    @field_validator('first_name', 'last_name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure names are not empty or just whitespace"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()


class ClientContactCreate(ClientContactBase):
    pass


class ClientContactResponse(ClientContactBase):
    id: int
    client_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    client_type: str  # 'residential', 'contractor', 'commercial'
    client_name: Optional[str] = None  # Changed from company_name to match database
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None  # Database column is 'zip_code'

    @field_validator('client_type')
    @classmethod
    def valid_client_type(cls, v: str) -> str:
        """Ensure client_type is one of the valid options"""
        valid_types = ['residential', 'contractor', 'commercial']
        if v not in valid_types:
            raise ValueError(f'client_type must be one of: {", ".join(valid_types)}')
        return v

    @field_validator('client_name')
    @classmethod
    def client_name_valid(cls, v: Optional[str]) -> Optional[str]:
        """Ensure client name is at least 2 characters if provided"""
        if v is not None and v.strip() and len(v.strip()) < 2:
            raise ValueError('client_name must be at least 2 characters')
        return v.strip() if v else v


class ClientCreate(ClientBase):
    primary_contact: ClientContactCreate
    additional_contacts: Optional[List[ClientContactCreate]] = []


class ClientUpdate(BaseModel):
    client_type: Optional[str] = None
    client_name: Optional[str] = None  # Changed from company_name to match database
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None  # Database column is 'zip_code'


class ClientResponse(BaseModel):
    # Don't inherit from ClientBase to avoid validation on responses
    id: int
    client_type: str
    client_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    company_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    # Primary contact info for list view
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None

    class Config:
        from_attributes = True


class ClientDetailResponse(ClientResponse):
    """Extended client response with contacts and jobs"""
    contacts: List[ClientContactResponse] = []
    job_count: int = 0
    total_revenue: float = 0.0
