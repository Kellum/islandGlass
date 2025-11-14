"""
Job Schedule Models
Pydantic models for job scheduling
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal


class JobScheduleCreate(BaseModel):
    """Model for creating a new job schedule entry"""
    event_type: str = Field(
        ...,
        description="Event type: Measure, Install, Delivery, Follow-up, Deadline, Custom"
    )
    custom_event_type: Optional[str] = None
    scheduled_date: date = Field(..., description="Scheduled date for the event")
    scheduled_time: Optional[time] = None
    duration_hours: Optional[Decimal] = Field(default=None, ge=0, description="Duration in hours")
    assigned_to: Optional[str] = None  # UUID
    assigned_name: Optional[str] = None
    status: Optional[str] = Field(
        default="Scheduled",
        description="Status: Scheduled, Confirmed, In Progress, Completed, Cancelled, Rescheduled"
    )
    send_reminder: Optional[bool] = Field(default=False)
    reminder_sent: Optional[bool] = Field(default=False)
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "Install",
                "scheduled_date": "2025-01-15",
                "scheduled_time": "09:00:00",
                "duration_hours": 4.0,
                "assigned_name": "John Doe",
                "status": "Scheduled",
                "send_reminder": True,
                "notes": "Customer prefers morning installation"
            }
        }


class JobScheduleUpdate(BaseModel):
    """Model for updating an existing job schedule entry"""
    event_type: Optional[str] = None
    custom_event_type: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    duration_hours: Optional[Decimal] = Field(default=None, ge=0)
    assigned_to: Optional[str] = None  # UUID
    assigned_name: Optional[str] = None
    status: Optional[str] = None
    send_reminder: Optional[bool] = None
    reminder_sent: Optional[bool] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "Completed",
                "notes": "Installation completed successfully"
            }
        }


class JobScheduleResponse(BaseModel):
    """Model for job schedule response"""
    schedule_id: int
    job_id: int
    event_type: str
    custom_event_type: Optional[str] = None
    scheduled_date: date
    scheduled_time: Optional[time] = None
    duration_hours: Optional[Decimal] = None
    assigned_to: Optional[str] = None
    assigned_name: Optional[str] = None
    status: str
    send_reminder: bool
    reminder_sent: bool
    notes: Optional[str] = None
    company_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Optional joined data
    job_po_number: Optional[str] = None
    client_name: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "schedule_id": 1,
                "job_id": 5,
                "event_type": "Install",
                "scheduled_date": "2025-01-15",
                "scheduled_time": "09:00:00",
                "duration_hours": 4.0,
                "assigned_name": "John Doe",
                "status": "Scheduled",
                "send_reminder": True,
                "reminder_sent": False,
                "notes": "Customer prefers morning installation",
                "job_po_number": "01-kellum.ryan-123acme",
                "created_at": "2025-01-10T10:00:00",
                "updated_at": "2025-01-10T10:00:00"
            }
        }
