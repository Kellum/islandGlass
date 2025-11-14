"""
Site Visits Router
FastAPI endpoints for job site visits
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from models.site_visit import SiteVisitCreate, SiteVisitUpdate, SiteVisitResponse
from models.user import TokenData
from middleware.auth import get_current_user
from database import Database

router = APIRouter(tags=["site-visits"])


@router.get("/", response_model=List[SiteVisitResponse])
async def list_site_visits(
    job_id: Optional[int] = Query(None, description="Filter by job ID"),
    visit_type: Optional[str] = Query(None, description="Filter by visit type"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all site visits with optional filters"""
    db = Database()

    try:
        if job_id:
            # Get visits for specific job
            visits = db.get_job_site_visits(job_id)
        else:
            # Get all visits (would need to implement this in database.py if needed)
            raise HTTPException(status_code=400, detail="job_id parameter is required")

        # Apply additional filters
        if visit_type:
            visits = [v for v in visits if v.get('visit_type') == visit_type]

        if completed is not None:
            visits = [v for v in visits if v.get('completed') == completed]

        # Convert Decimals to float for JSON serialization
        for visit in visits:
            if 'duration_hours' in visit and visit['duration_hours'] is not None:
                visit['duration_hours'] = float(visit['duration_hours'])

        return visits
    except Exception as e:
        print(f"Error fetching site visits: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch site visits")


@router.get("/{visit_id}", response_model=SiteVisitResponse)
async def get_site_visit(
    visit_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific site visit by ID"""
    db = Database()

    visit = db.get_site_visit_by_id(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Site visit not found")

    # Convert Decimals to float
    if 'duration_hours' in visit and visit['duration_hours'] is not None:
        visit['duration_hours'] = float(visit['duration_hours'])

    return visit


@router.post("/", response_model=SiteVisitResponse, status_code=201)
async def create_site_visit(
    visit_data: SiteVisitCreate,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new site visit"""
    db = Database()

    # Convert to dict
    visit_dict = visit_data.model_dump()

    # Convert Decimal to float for database
    if 'duration_hours' in visit_dict and visit_dict['duration_hours'] is not None:
        visit_dict['duration_hours'] = float(visit_dict['duration_hours'])

    # Convert datetime objects to strings
    if 'visit_date' in visit_dict and visit_dict['visit_date']:
        visit_dict['visit_date'] = str(visit_dict['visit_date'])
    if 'visit_time' in visit_dict and visit_dict['visit_time']:
        visit_dict['visit_time'] = str(visit_dict['visit_time'])

    # Insert the visit
    created_visit = db.insert_site_visit(visit_dict, current_user.user_id)

    if not created_visit:
        raise HTTPException(status_code=400, detail="Failed to create site visit")

    # Convert Decimals to float in response
    if 'duration_hours' in created_visit and created_visit['duration_hours'] is not None:
        created_visit['duration_hours'] = float(created_visit['duration_hours'])

    return created_visit


@router.put("/{visit_id}", response_model=SiteVisitResponse)
async def update_site_visit(
    visit_id: int,
    visit_data: SiteVisitUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update a site visit"""
    db = Database()

    # Check if visit exists
    existing_visit = db.get_site_visit_by_id(visit_id)
    if not existing_visit:
        raise HTTPException(status_code=404, detail="Site visit not found")

    # Convert to dict, excluding unset fields
    updates = visit_data.model_dump(exclude_unset=True)

    # Convert Decimal to float for database
    if 'duration_hours' in updates and updates['duration_hours'] is not None:
        updates['duration_hours'] = float(updates['duration_hours'])

    # Convert datetime objects to strings
    if 'visit_date' in updates and updates['visit_date']:
        updates['visit_date'] = str(updates['visit_date'])
    if 'visit_time' in updates and updates['visit_time']:
        updates['visit_time'] = str(updates['visit_time'])

    # Update the visit
    updated_visit = db.update_site_visit(visit_id, updates, current_user.user_id)

    if not updated_visit:
        raise HTTPException(status_code=400, detail="Failed to update site visit")

    # Convert Decimals to float in response
    if 'duration_hours' in updated_visit and updated_visit['duration_hours'] is not None:
        updated_visit['duration_hours'] = float(updated_visit['duration_hours'])

    return updated_visit


@router.delete("/{visit_id}", status_code=204)
async def delete_site_visit(
    visit_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a site visit"""
    db = Database()

    # Check if visit exists
    existing_visit = db.get_site_visit_by_id(visit_id)
    if not existing_visit:
        raise HTTPException(status_code=404, detail="Site visit not found")

    # Delete the visit
    success = db.delete_site_visit(visit_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete site visit")

    return None
