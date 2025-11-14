"""
Job Files Router
FastAPI endpoints for job file attachments
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional
from models.job_file import (
    JobFileCreate,
    JobFileUpdate,
    JobFileResponse
)
from models.user import TokenData
from middleware.auth import get_current_user
from database import Database

router = APIRouter(tags=["job-files"])


@router.get("/", response_model=List[JobFileResponse])
async def list_job_files(
    job_id: int = Path(..., description="Job ID"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all files for a specific job with optional filters"""
    db = Database()

    try:
        # Get files for specific job with optional file_type filter
        files = db.get_job_files(job_id, file_type)

        return files
    except Exception as e:
        print(f"Error fetching job files: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job files")


@router.get("/{file_id}", response_model=JobFileResponse)
async def get_job_file(
    job_id: int = Path(..., description="Job ID"),
    file_id: int = Path(..., description="File ID"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific job file by ID"""
    db = Database()

    file_data = db.get_job_file_by_id(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="Job file not found")

    # Verify the file belongs to the specified job
    if file_data.get('job_id') != job_id:
        raise HTTPException(status_code=404, detail="File not found for this job")

    return file_data


@router.post("/", response_model=JobFileResponse, status_code=201)
async def create_job_file(
    job_id: int = Path(..., description="Job ID"),
    file_data: JobFileCreate = ...,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new job file entry"""
    db = Database()

    # Verify job exists
    job = db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Convert to dict
    file_dict = file_data.model_dump()

    # Add job_id to the file entry
    file_dict['job_id'] = job_id

    # Insert the file entry
    created_file = db.insert_job_file(file_dict, current_user.user_id)

    if not created_file:
        raise HTTPException(status_code=400, detail="Failed to create job file entry")

    return created_file


@router.put("/{file_id}", response_model=JobFileResponse)
async def update_job_file(
    job_id: int = Path(..., description="Job ID"),
    file_id: int = Path(..., description="File ID"),
    file_data: JobFileUpdate = ...,
    current_user: TokenData = Depends(get_current_user)
):
    """Update a job file entry"""
    db = Database()

    # Check if file exists
    existing_file = db.get_job_file_by_id(file_id)
    if not existing_file:
        raise HTTPException(status_code=404, detail="Job file not found")

    # Verify the file belongs to the specified job
    if existing_file.get('job_id') != job_id:
        raise HTTPException(status_code=404, detail="File not found for this job")

    # Convert to dict and filter out None values
    updates = file_data.model_dump(exclude_unset=True)

    # Update the file entry
    updated_file = db.update_job_file(file_id, updates)

    if not updated_file:
        raise HTTPException(status_code=400, detail="Failed to update job file entry")

    return updated_file


@router.delete("/{file_id}", status_code=204)
async def delete_job_file(
    job_id: int = Path(..., description="Job ID"),
    file_id: int = Path(..., description="File ID"),
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a job file entry"""
    db = Database()

    # Check if file exists
    existing_file = db.get_job_file_by_id(file_id)
    if not existing_file:
        raise HTTPException(status_code=404, detail="Job file not found")

    # Verify the file belongs to the specified job
    if existing_file.get('job_id') != job_id:
        raise HTTPException(status_code=404, detail="File not found for this job")

    # Delete the file entry
    success = db.delete_job_file(file_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete job file entry")

    return None
