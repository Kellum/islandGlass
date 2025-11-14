"""
Job Schedule Router
FastAPI endpoints for job scheduling
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional
from models.job_schedule import (
    JobScheduleCreate,
    JobScheduleUpdate,
    JobScheduleResponse
)
from models.user import TokenData
from middleware.auth import get_current_user
from database import Database

router = APIRouter(tags=["job-schedule"])


@router.get("/", response_model=List[JobScheduleResponse])
async def list_job_schedule(
    job_id: int = Path(..., description="Job ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all schedule events for a specific job with optional filters"""
    db = Database()

    try:
        # Get schedule events for specific job
        events = db.get_job_schedule(job_id)

        # Apply event_type filter if provided
        if event_type:
            events = [e for e in events if e.get('event_type') == event_type]

        # Apply status filter if provided
        if status:
            events = [e for e in events if e.get('status') == status]

        # Convert Decimals to float for JSON serialization
        for event in events:
            if 'duration_hours' in event and event['duration_hours'] is not None:
                event['duration_hours'] = float(event['duration_hours'])

        return events
    except Exception as e:
        print(f"Error fetching job schedule: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job schedule")


@router.get("/{schedule_id}", response_model=JobScheduleResponse)
async def get_job_schedule_event(
    job_id: int = Path(..., description="Job ID"),
    schedule_id: int = Path(..., description="Schedule ID"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific job schedule event by ID"""
    db = Database()

    event = db.get_job_schedule_by_id(schedule_id)
    if not event:
        raise HTTPException(status_code=404, detail="Job schedule event not found")

    # Verify the event belongs to the specified job
    if event.get('job_id') != job_id:
        raise HTTPException(status_code=404, detail="Schedule event not found for this job")

    # Convert Decimal to float
    if 'duration_hours' in event and event['duration_hours'] is not None:
        event['duration_hours'] = float(event['duration_hours'])

    return event


@router.post("/", response_model=JobScheduleResponse, status_code=201)
async def create_job_schedule_event(
    job_id: int = Path(..., description="Job ID"),
    schedule_data: JobScheduleCreate = ...,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new job schedule event"""
    db = Database()

    # Verify job exists
    job = db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Convert to dict
    event_dict = schedule_data.model_dump()

    # Add job_id to the event
    event_dict['job_id'] = job_id

    # Convert date objects to strings for Supabase
    if 'scheduled_date' in event_dict and event_dict['scheduled_date']:
        event_dict['scheduled_date'] = str(event_dict['scheduled_date'])

    # Convert time objects to strings for Supabase
    if 'scheduled_time' in event_dict and event_dict['scheduled_time']:
        event_dict['scheduled_time'] = str(event_dict['scheduled_time'])

    # Convert Decimal to float if present
    if 'duration_hours' in event_dict and event_dict['duration_hours'] is not None:
        event_dict['duration_hours'] = float(event_dict['duration_hours'])

    # Insert the event
    created_event = db.insert_schedule_event(event_dict, current_user.user_id)

    if not created_event:
        raise HTTPException(status_code=400, detail="Failed to create job schedule event")

    # Convert Decimal to float in response
    if 'duration_hours' in created_event and created_event['duration_hours'] is not None:
        created_event['duration_hours'] = float(created_event['duration_hours'])

    return created_event


@router.put("/{schedule_id}", response_model=JobScheduleResponse)
async def update_job_schedule_event(
    job_id: int = Path(..., description="Job ID"),
    schedule_id: int = Path(..., description="Schedule ID"),
    schedule_data: JobScheduleUpdate = ...,
    current_user: TokenData = Depends(get_current_user)
):
    """Update a job schedule event"""
    db = Database()

    # Check if event exists
    existing_event = db.get_job_schedule_by_id(schedule_id)
    if not existing_event:
        raise HTTPException(status_code=404, detail="Job schedule event not found")

    # Verify the event belongs to the specified job
    if existing_event.get('job_id') != job_id:
        raise HTTPException(status_code=404, detail="Schedule event not found for this job")

    # Convert to dict and filter out None values
    updates = schedule_data.model_dump(exclude_unset=True)

    # Convert date objects to strings for Supabase
    if 'scheduled_date' in updates and updates['scheduled_date']:
        updates['scheduled_date'] = str(updates['scheduled_date'])

    # Convert time objects to strings for Supabase
    if 'scheduled_time' in updates and updates['scheduled_time']:
        updates['scheduled_time'] = str(updates['scheduled_time'])

    # Convert Decimal to float if present
    if 'duration_hours' in updates and updates['duration_hours'] is not None:
        updates['duration_hours'] = float(updates['duration_hours'])

    # Update the event
    updated_event = db.update_job_schedule(schedule_id, updates)

    if not updated_event:
        raise HTTPException(status_code=400, detail="Failed to update job schedule event")

    # Convert Decimal to float in response
    if 'duration_hours' in updated_event and updated_event['duration_hours'] is not None:
        updated_event['duration_hours'] = float(updated_event['duration_hours'])

    return updated_event


@router.delete("/{schedule_id}", status_code=204)
async def delete_job_schedule_event(
    job_id: int = Path(..., description="Job ID"),
    schedule_id: int = Path(..., description="Schedule ID"),
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a job schedule event"""
    db = Database()

    # Check if event exists
    existing_event = db.get_job_schedule_by_id(schedule_id)
    if not existing_event:
        raise HTTPException(status_code=404, detail="Job schedule event not found")

    # Verify the event belongs to the specified job
    if existing_event.get('job_id') != job_id:
        raise HTTPException(status_code=404, detail="Schedule event not found for this job")

    # Delete the event
    success = db.delete_job_schedule(schedule_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete job schedule event")

    return None
