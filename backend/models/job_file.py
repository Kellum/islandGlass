"""
Job File Models
Pydantic models for job file attachments
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class JobFileCreate(BaseModel):
    """Model for creating a new job file entry"""
    file_name: str = Field(..., min_length=1, description="Name of the file")
    file_type: str = Field(
        ...,
        description="File type: Photo, PDF, Drawing, Document, Video, Other"
    )
    file_size: Optional[int] = Field(default=None, ge=0, description="File size in bytes")
    file_path: str = Field(..., min_length=1, description="Supabase storage URL or path")
    thumbnail_path: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None, description="Tags for categorization")
    visit_id: Optional[int] = Field(default=None, description="Related site visit ID")
    work_item_id: Optional[int] = Field(default=None, description="Related work item ID")

    class Config:
        json_schema_extra = {
            "example": {
                "file_name": "shower_door_measurement.jpg",
                "file_type": "Photo",
                "file_size": 2048576,
                "file_path": "/storage/jobs/5/photos/shower_door_measurement.jpg",
                "thumbnail_path": "/storage/jobs/5/photos/thumbs/shower_door_measurement_thumb.jpg",
                "description": "Measurements for custom shower door",
                "tags": ["measurement", "shower", "photo"],
                "visit_id": 1
            }
        }


class JobFileUpdate(BaseModel):
    """Model for updating an existing job file entry"""
    file_name: Optional[str] = Field(default=None, min_length=1)
    file_type: Optional[str] = None
    file_size: Optional[int] = Field(default=None, ge=0)
    file_path: Optional[str] = Field(default=None, min_length=1)
    thumbnail_path: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    visit_id: Optional[int] = None
    work_item_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated measurement photo with annotations",
                "tags": ["measurement", "shower", "photo", "annotated"]
            }
        }


class JobFileResponse(BaseModel):
    """Model for job file response"""
    file_id: int
    job_id: int
    file_name: str
    file_type: str
    file_size: Optional[int] = None
    file_path: str
    thumbnail_path: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    visit_id: Optional[int] = None
    work_item_id: Optional[int] = None
    company_id: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: Optional[datetime] = None

    # Optional joined data
    job_po_number: Optional[str] = None
    client_name: Optional[str] = None
    visit_type: Optional[str] = None
    work_item_description: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "file_id": 1,
                "job_id": 5,
                "file_name": "shower_door_measurement.jpg",
                "file_type": "Photo",
                "file_size": 2048576,
                "file_path": "/storage/jobs/5/photos/shower_door_measurement.jpg",
                "thumbnail_path": "/storage/jobs/5/photos/thumbs/shower_door_measurement_thumb.jpg",
                "description": "Measurements for custom shower door",
                "tags": ["measurement", "shower", "photo"],
                "visit_id": 1,
                "job_po_number": "01-kellum.ryan-123acme",
                "client_name": "ACME Corporation",
                "visit_type": "Measure",
                "uploaded_at": "2025-01-10T10:00:00"
            }
        }
