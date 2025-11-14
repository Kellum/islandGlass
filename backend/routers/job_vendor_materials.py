"""
Job Vendor Materials Router
FastAPI endpoints for job vendor materials tracking
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional
from models.job_vendor_material import (
    JobVendorMaterialCreate,
    JobVendorMaterialUpdate,
    JobVendorMaterialResponse
)
from models.user import TokenData
from middleware.auth import get_current_user
from database import Database

router = APIRouter(tags=["job-vendor-materials"])


@router.get("/", response_model=List[JobVendorMaterialResponse])
async def list_job_vendor_materials(
    job_id: int = Path(..., description="Job ID"),
    vendor_id: Optional[int] = Query(None, description="Filter by vendor ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all vendor materials for a specific job with optional filters"""
    db = Database()

    try:
        # Get materials for specific job
        materials = db.get_job_vendor_materials(job_id)

        # Apply vendor_id filter if provided
        if vendor_id is not None:
            materials = [m for m in materials if m.get('vendor_id') == vendor_id]

        # Apply status filter if provided
        if status:
            materials = [m for m in materials if m.get('status') == status]

        # Convert Decimals to float for JSON serialization
        for material in materials:
            if 'cost' in material and material['cost'] is not None:
                material['cost'] = float(material['cost'])

        return materials
    except Exception as e:
        print(f"Error fetching job vendor materials: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job vendor materials")


@router.get("/{material_id}", response_model=JobVendorMaterialResponse)
async def get_job_vendor_material(
    job_id: int = Path(..., description="Job ID"),
    material_id: int = Path(..., description="Material ID"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific job vendor material by ID"""
    db = Database()

    material = db.get_job_vendor_material_by_id(material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Job vendor material not found")

    # Verify the material belongs to the specified job
    if material.get('job_id') != job_id:
        raise HTTPException(status_code=404, detail="Material not found for this job")

    # Convert Decimal to float
    if 'cost' in material and material['cost'] is not None:
        material['cost'] = float(material['cost'])

    return material


@router.post("/", response_model=JobVendorMaterialResponse, status_code=201)
async def create_job_vendor_material(
    job_id: int = Path(..., description="Job ID"),
    material_data: JobVendorMaterialCreate = ...,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new job vendor material"""
    db = Database()

    # Verify job exists
    job = db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Convert to dict
    material_dict = material_data.model_dump()

    # Add job_id to the material
    material_dict['job_id'] = job_id

    # Convert date objects to strings for Supabase
    if 'ordered_date' in material_dict and material_dict['ordered_date']:
        material_dict['ordered_date'] = str(material_dict['ordered_date'])
    if 'expected_delivery_date' in material_dict and material_dict['expected_delivery_date']:
        material_dict['expected_delivery_date'] = str(material_dict['expected_delivery_date'])
    if 'actual_delivery_date' in material_dict and material_dict['actual_delivery_date']:
        material_dict['actual_delivery_date'] = str(material_dict['actual_delivery_date'])

    # Convert Decimal to float if present
    if 'cost' in material_dict and material_dict['cost'] is not None:
        material_dict['cost'] = float(material_dict['cost'])

    # Insert the material
    created_material = db.insert_job_vendor_material(material_dict, current_user.user_id)

    if not created_material:
        raise HTTPException(status_code=400, detail="Failed to create job vendor material")

    # Convert Decimal to float in response
    if 'cost' in created_material and created_material['cost'] is not None:
        created_material['cost'] = float(created_material['cost'])

    return created_material


@router.put("/{material_id}", response_model=JobVendorMaterialResponse)
async def update_job_vendor_material(
    job_id: int = Path(..., description="Job ID"),
    material_id: int = Path(..., description="Material ID"),
    material_data: JobVendorMaterialUpdate = ...,
    current_user: TokenData = Depends(get_current_user)
):
    """Update a job vendor material"""
    db = Database()

    # Check if material exists
    existing_material = db.get_job_vendor_material_by_id(material_id)
    if not existing_material:
        raise HTTPException(status_code=404, detail="Job vendor material not found")

    # Verify the material belongs to the specified job
    if existing_material.get('job_id') != job_id:
        raise HTTPException(status_code=404, detail="Material not found for this job")

    # Convert to dict and filter out None values
    updates = material_data.model_dump(exclude_unset=True)

    # Convert date objects to strings for Supabase
    if 'ordered_date' in updates and updates['ordered_date']:
        updates['ordered_date'] = str(updates['ordered_date'])
    if 'expected_delivery_date' in updates and updates['expected_delivery_date']:
        updates['expected_delivery_date'] = str(updates['expected_delivery_date'])
    if 'actual_delivery_date' in updates and updates['actual_delivery_date']:
        updates['actual_delivery_date'] = str(updates['actual_delivery_date'])

    # Convert Decimal to float if present
    if 'cost' in updates and updates['cost'] is not None:
        updates['cost'] = float(updates['cost'])

    # Update the material
    updated_material = db.update_job_vendor_material(material_id, updates)

    if not updated_material:
        raise HTTPException(status_code=400, detail="Failed to update job vendor material")

    # Convert Decimal to float in response
    if 'cost' in updated_material and updated_material['cost'] is not None:
        updated_material['cost'] = float(updated_material['cost'])

    return updated_material


@router.delete("/{material_id}", status_code=204)
async def delete_job_vendor_material(
    job_id: int = Path(..., description="Job ID"),
    material_id: int = Path(..., description="Material ID"),
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a job vendor material"""
    db = Database()

    # Check if material exists
    existing_material = db.get_job_vendor_material_by_id(material_id)
    if not existing_material:
        raise HTTPException(status_code=404, detail="Job vendor material not found")

    # Verify the material belongs to the specified job
    if existing_material.get('job_id') != job_id:
        raise HTTPException(status_code=404, detail="Material not found for this job")

    # Delete the material
    success = db.delete_job_vendor_material(material_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete job vendor material")

    return None
