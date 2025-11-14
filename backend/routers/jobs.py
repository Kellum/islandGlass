"""
Jobs Router
Handles job/PO management CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobDetailResponse,
)
from models.user import TokenData
from middleware.auth import get_current_user
from database import Database
from utils.po_generator import generate_po_number, validate_po_format, POGenerationError

router = APIRouter()


# Request/Response models for PO generation
class POGenerateRequest(BaseModel):
    client_id: int
    location_code: str
    is_remake: bool = False
    is_warranty: bool = False
    site_address: Optional[str] = None


class POGenerateResponse(BaseModel):
    po_number: str
    is_duplicate: bool
    warning: Optional[str] = None
    location_code: str
    street_number: str
    name_part: str


@router.get("/", response_model=List[JobResponse])
async def get_all_jobs(
    current_user: TokenData = Depends(get_current_user),
    status_filter: Optional[str] = Query(None, description="Filter by job status"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    search: Optional[str] = Query(None, description="Search by PO number or description"),
):
    """
    Get all jobs for the current user's company

    Query Parameters:
    - status_filter: Filter by status (Quote, Scheduled, In Progress, etc.)
    - client_id: Filter by client ID
    - search: Search in PO number or job description

    Returns list of jobs with basic info
    """
    try:
        db = Database()

        # Get all jobs (database methods handle company scoping)
        jobs = db.get_all_jobs()

        if not jobs:
            return []

        # Apply filters
        filtered_jobs = jobs

        if status_filter:
            filtered_jobs = [j for j in filtered_jobs if j.get("status") == status_filter]

        if client_id:
            filtered_jobs = [j for j in filtered_jobs if j.get("client_id") == client_id]

        if search:
            search_lower = search.lower()
            filtered_jobs = [
                j for j in filtered_jobs
                if (j.get("po_number") and search_lower in j.get("po_number", "").lower())
                or (j.get("job_description") and search_lower in j.get("job_description", "").lower())
            ]

        # Enrich jobs with client names
        for job in filtered_jobs:
            try:
                client = db.get_po_client_by_id(job["client_id"])
                if client:
                    job["client_name"] = client.get("client_name")
            except:
                job["client_name"] = None

        # Convert to response models
        return [
            JobResponse(
                job_id=job["job_id"],
                po_number=job["po_number"],
                client_id=job["client_id"],
                location_code=job.get("location_code"),
                is_remake=job.get("is_remake", False),
                is_warranty=job.get("is_warranty", False),
                client_name=job.get("client_name"),
                job_date=job.get("job_date"),
                estimated_completion_date=job.get("estimated_completion_date"),
                actual_completion_date=job.get("actual_completion_date"),
                status=job.get("status", "Quote"),
                total_estimate=job.get("total_estimate"),
                actual_cost=job.get("actual_cost"),
                material_cost=job.get("material_cost"),
                labor_cost=job.get("labor_cost"),
                profit_margin=job.get("profit_margin"),
                job_description=job.get("job_description"),
                internal_notes=job.get("internal_notes"),
                customer_notes=job.get("customer_notes"),
                site_address=job.get("site_address"),
                site_contact_name=job.get("site_contact_name"),
                site_contact_phone=job.get("site_contact_phone"),
                company_id=job.get("company_id"),
                created_at=job.get("created_at"),
                updated_at=job.get("updated_at"),
                created_by=job.get("created_by"),
                updated_by=job.get("updated_by"),
            )
            for job in filtered_jobs
        ]

    except Exception as e:
        print(f"Error in get_all_jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while fetching jobs. Please try again later.",
        )


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job_by_id(
    job_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Get detailed job information including client name and related counts

    Returns:
    - Job details
    - Client name
    - Count of work items, materials, visits
    """
    try:
        db = Database()

        # Get job details
        job = db.get_job_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )

        # Get client name
        client_name = None
        try:
            client = db.get_po_client_by_id(job["client_id"])
            if client:
                client_name = client.get("client_name")
        except:
            pass

        # Get related counts
        work_item_count = 0
        material_count = 0
        visit_count = 0
        try:
            work_items = db.get_job_work_items(job_id)
            work_item_count = len(work_items) if work_items else 0
        except:
            pass

        try:
            materials = db.get_job_materials(job_id)
            material_count = len(materials) if materials else 0
        except:
            pass

        try:
            visits = db.get_job_site_visits(job_id)
            visit_count = len(visits) if visits else 0
        except:
            pass

        return JobDetailResponse(
            job_id=job["job_id"],
            po_number=job["po_number"],
            client_id=job["client_id"],
            location_code=job.get("location_code"),
            is_remake=job.get("is_remake", False),
            is_warranty=job.get("is_warranty", False),
            job_date=job.get("job_date"),
            estimated_completion_date=job.get("estimated_completion_date"),
            actual_completion_date=job.get("actual_completion_date"),
            status=job.get("status", "Quote"),
            total_estimate=job.get("total_estimate"),
            actual_cost=job.get("actual_cost"),
            material_cost=job.get("material_cost"),
            labor_cost=job.get("labor_cost"),
            profit_margin=job.get("profit_margin"),
            job_description=job.get("job_description"),
            internal_notes=job.get("internal_notes"),
            customer_notes=job.get("customer_notes"),
            site_address=job.get("site_address"),
            site_contact_name=job.get("site_contact_name"),
            site_contact_phone=job.get("site_contact_phone"),
            company_id=job.get("company_id"),
            created_at=job.get("created_at"),
            updated_at=job.get("updated_at"),
            created_by=job.get("created_by"),
            updated_by=job.get("updated_by"),
            client_name=client_name,
            work_item_count=work_item_count,
            material_count=material_count,
            visit_count=visit_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_job_by_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while fetching job details. Please try again later.",
        )


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Create a new job/PO

    Request body:
    - po_number: Unique PO number (required)
    - client_id: Client ID (required)
    - status: Job status (default: Quote)
    - All other fields optional
    """
    try:
        db = Database()

        # Verify client exists
        client = db.get_po_client_by_id(job_data.client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {job_data.client_id} not found",
            )

        # Prepare job data
        job_dict = {
            "po_number": job_data.po_number,
            "client_id": job_data.client_id,
            "status": job_data.status,
        }

        # Add PO generation fields
        if job_data.location_code is not None:
            job_dict["location_code"] = job_data.location_code
        if job_data.is_remake is not None:
            job_dict["is_remake"] = job_data.is_remake
        if job_data.is_warranty is not None:
            job_dict["is_warranty"] = job_data.is_warranty

        # Add optional fields if provided
        if job_data.job_date is not None:
            job_dict["job_date"] = str(job_data.job_date)
        if job_data.estimated_completion_date is not None:
            job_dict["estimated_completion_date"] = str(job_data.estimated_completion_date)
        if job_data.actual_completion_date is not None:
            job_dict["actual_completion_date"] = str(job_data.actual_completion_date)
        if job_data.total_estimate is not None:
            job_dict["total_estimate"] = float(job_data.total_estimate)
        if job_data.actual_cost is not None:
            job_dict["actual_cost"] = float(job_data.actual_cost)
        if job_data.material_cost is not None:
            job_dict["material_cost"] = float(job_data.material_cost)
        if job_data.labor_cost is not None:
            job_dict["labor_cost"] = float(job_data.labor_cost)
        if job_data.profit_margin is not None:
            job_dict["profit_margin"] = float(job_data.profit_margin)
        if job_data.job_description is not None:
            job_dict["job_description"] = job_data.job_description
        if job_data.internal_notes is not None:
            job_dict["internal_notes"] = job_data.internal_notes
        if job_data.customer_notes is not None:
            job_dict["customer_notes"] = job_data.customer_notes
        if job_data.site_address is not None:
            job_dict["site_address"] = job_data.site_address
        if job_data.site_contact_name is not None:
            job_dict["site_contact_name"] = job_data.site_contact_name
        if job_data.site_contact_phone is not None:
            job_dict["site_contact_phone"] = job_data.site_contact_phone

        # Insert job
        created_job = db.insert_job(
            job_data=job_dict,
            user_id=current_user.user_id,
        )

        if not created_job:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to create job. Please try again or contact support.",
            )

        return JobResponse(
            job_id=created_job["job_id"],
            po_number=created_job["po_number"],
            client_id=created_job["client_id"],
            location_code=created_job.get("location_code"),
            is_remake=created_job.get("is_remake", False),
            is_warranty=created_job.get("is_warranty", False),
            job_date=created_job.get("job_date"),
            estimated_completion_date=created_job.get("estimated_completion_date"),
            actual_completion_date=created_job.get("actual_completion_date"),
            status=created_job.get("status", "Quote"),
            total_estimate=created_job.get("total_estimate"),
            actual_cost=created_job.get("actual_cost"),
            material_cost=created_job.get("material_cost"),
            labor_cost=created_job.get("labor_cost"),
            profit_margin=created_job.get("profit_margin"),
            job_description=created_job.get("job_description"),
            internal_notes=created_job.get("internal_notes"),
            customer_notes=created_job.get("customer_notes"),
            site_address=created_job.get("site_address"),
            site_contact_name=created_job.get("site_contact_name"),
            site_contact_phone=created_job.get("site_contact_phone"),
            company_id=created_job.get("company_id"),
            created_at=created_job.get("created_at"),
            updated_at=created_job.get("updated_at"),
            created_by=created_job.get("created_by"),
            updated_by=created_job.get("updated_by"),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while creating job. Please check your input and try again.",
        )


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Update an existing job

    Only provided fields will be updated (partial update supported)
    """
    try:
        db = Database()

        # Check if job exists
        existing_job = db.get_job_by_id(job_id)
        if not existing_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )

        # Prepare update data (only include non-None values)
        update_dict = {}
        if job_data.client_id is not None:
            # Verify client exists
            client = db.get_po_client_by_id(job_data.client_id)
            if not client:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Client with ID {job_data.client_id} not found",
                )
            update_dict["client_id"] = job_data.client_id
        if job_data.job_date is not None:
            update_dict["job_date"] = str(job_data.job_date)
        if job_data.estimated_completion_date is not None:
            update_dict["estimated_completion_date"] = str(job_data.estimated_completion_date)
        if job_data.actual_completion_date is not None:
            update_dict["actual_completion_date"] = str(job_data.actual_completion_date)
        if job_data.status is not None:
            update_dict["status"] = job_data.status
        if job_data.total_estimate is not None:
            update_dict["total_estimate"] = float(job_data.total_estimate)
        if job_data.actual_cost is not None:
            update_dict["actual_cost"] = float(job_data.actual_cost)
        if job_data.material_cost is not None:
            update_dict["material_cost"] = float(job_data.material_cost)
        if job_data.labor_cost is not None:
            update_dict["labor_cost"] = float(job_data.labor_cost)
        if job_data.profit_margin is not None:
            update_dict["profit_margin"] = float(job_data.profit_margin)
        if job_data.job_description is not None:
            update_dict["job_description"] = job_data.job_description
        if job_data.internal_notes is not None:
            update_dict["internal_notes"] = job_data.internal_notes
        if job_data.customer_notes is not None:
            update_dict["customer_notes"] = job_data.customer_notes
        if job_data.site_address is not None:
            update_dict["site_address"] = job_data.site_address
        if job_data.site_contact_name is not None:
            update_dict["site_contact_name"] = job_data.site_contact_name
        if job_data.site_contact_phone is not None:
            update_dict["site_contact_phone"] = job_data.site_contact_phone

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        # Update job
        success = db.update_job(
            job_id=job_id,
            updates=update_dict,
            user_id=current_user.user_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to update job. Please try again.",
            )

        # Fetch updated job
        updated_job = db.get_job_by_id(job_id)

        return JobResponse(
            job_id=updated_job["job_id"],
            po_number=updated_job["po_number"],
            client_id=updated_job["client_id"],
            job_date=updated_job.get("job_date"),
            estimated_completion_date=updated_job.get("estimated_completion_date"),
            actual_completion_date=updated_job.get("actual_completion_date"),
            status=updated_job.get("status", "Quote"),
            total_estimate=updated_job.get("total_estimate"),
            actual_cost=updated_job.get("actual_cost"),
            material_cost=updated_job.get("material_cost"),
            labor_cost=updated_job.get("labor_cost"),
            profit_margin=updated_job.get("profit_margin"),
            job_description=updated_job.get("job_description"),
            internal_notes=updated_job.get("internal_notes"),
            customer_notes=updated_job.get("customer_notes"),
            site_address=updated_job.get("site_address"),
            site_contact_name=updated_job.get("site_contact_name"),
            site_contact_phone=updated_job.get("site_contact_phone"),
            company_id=updated_job.get("company_id"),
            created_at=updated_job.get("created_at"),
            updated_at=updated_job.get("updated_at"),
            created_by=updated_job.get("created_by"),
            updated_by=updated_job.get("updated_by"),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while updating job. Please try again later.",
        )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Soft delete a job (sets deleted_at timestamp)

    Returns 204 No Content on success
    """
    try:
        db = Database()

        # Check if job exists
        existing_job = db.get_job_by_id(job_id)
        if not existing_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )

        # Soft delete the job
        success = db.delete_job(
            job_id=job_id,
            user_id=current_user.user_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to delete job. Please try again.",
            )

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while deleting job. Please try again later.",
        )


@router.post("/generate-po", response_model=POGenerateResponse)
async def generate_po_preview(
    request: POGenerateRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Generate a PO number preview based on client data and location

    This endpoint generates a PO number without creating a job.
    Use it to preview PO numbers in the UI before form submission.

    Request body:
    - client_id: ID of the client
    - location_code: Location code (01, 02, or 03)
    - is_remake: Whether this is a remake job (default: false)
    - is_warranty: Whether this is a warranty job (default: false)
    - site_address: Optional site address override

    Returns:
    - po_number: Generated PO number
    - is_duplicate: Whether this is a duplicate PO
    - warning: Optional warning message
    - Additional metadata (location_code, street_number, name_part)
    """
    try:
        db = Database()

        # Generate PO number using the utility
        result = await generate_po_number(
            supabase=db.client,
            client_id=request.client_id,
            location_code=request.location_code,
            is_remake=request.is_remake,
            is_warranty=request.is_warranty,
            site_address=request.site_address,
        )

        return POGenerateResponse(**result)

    except POGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        print(f"Error in generate_po_preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while generating PO number. Please try again later.",
        )
