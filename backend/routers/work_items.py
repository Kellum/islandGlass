"""
Work Items API Routes - Track work being done per job

This module provides CRUD operations for work items (line items on jobs).
Work items represent individual pieces of work: Showers, Windows, Mirrors, etc.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from models.work_item import WorkItem, WorkItemCreate, WorkItemUpdate
from models.user import TokenData
from database import Database
from middleware.auth import get_current_user

router = APIRouter(tags=["work-items"])


@router.get("/", response_model=List[WorkItem])
async def get_work_items(
    job_id: Optional[int] = None,
    work_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all work items with optional filters

    Filters:
    - job_id: Filter by specific job
    - work_type: Shower, Window/IG, Mirror, Tabletop, Mirror Frame, Custom
    - status: Pending, In Progress, Complete, etc.

    Returns items sorted by sort_order
    """
    try:
        db = Database()

        if job_id:
            # Get items for specific job
            items = db.get_job_work_items(job_id)
        else:
            # Would need a get_all_work_items method - for now return empty
            # TODO: Add get_all_work_items to database.py if needed
            items = []

        # Apply additional filters
        if work_type:
            items = [i for i in items if i.get('work_type') == work_type]

        if status:
            items = [i for i in items if i.get('status') == status]

        # Convert Decimal to float for JSON
        for item in items:
            if 'estimated_cost' in item and item['estimated_cost'] is not None:
                item['estimated_cost'] = float(item['estimated_cost'])
            if 'actual_cost' in item and item['actual_cost'] is not None:
                item['actual_cost'] = float(item['actual_cost'])

        return items
    except Exception as e:
        print(f"Error in get_work_items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{item_id}", response_model=WorkItem)
async def get_work_item(
    item_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific work item by ID"""
    try:
        db = Database()
        item = db.get_work_item_by_id(item_id)

        if not item:
            raise HTTPException(status_code=404, detail="Work item not found")

        # Convert Decimal to float for JSON
        if 'estimated_cost' in item and item['estimated_cost'] is not None:
            item['estimated_cost'] = float(item['estimated_cost'])
        if 'actual_cost' in item and item['actual_cost'] is not None:
            item['actual_cost'] = float(item['actual_cost'])

        return item
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_work_item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=WorkItem, status_code=201)
async def create_work_item(
    item_data: WorkItemCreate,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new work item"""
    try:
        db = Database()
        user_id = current_user.user_id

        # Convert Pydantic model to dict
        item_dict = item_data.model_dump()

        # Convert Decimals to float for database
        if 'estimated_cost' in item_dict and item_dict['estimated_cost'] is not None:
            item_dict['estimated_cost'] = float(item_dict['estimated_cost'])
        if 'actual_cost' in item_dict and item_dict['actual_cost'] is not None:
            item_dict['actual_cost'] = float(item_dict['actual_cost'])

        # Create the work item
        new_item = db.insert_work_item(item_dict, user_id)

        if not new_item:
            raise HTTPException(status_code=400, detail="Failed to create work item")

        # Convert Decimal to float for response
        if 'estimated_cost' in new_item and new_item['estimated_cost'] is not None:
            new_item['estimated_cost'] = float(new_item['estimated_cost'])
        if 'actual_cost' in new_item and new_item['actual_cost'] is not None:
            new_item['actual_cost'] = float(new_item['actual_cost'])

        return new_item
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_work_item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{item_id}", response_model=WorkItem)
async def update_work_item(
    item_id: int,
    item_data: WorkItemUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update an existing work item"""
    try:
        db = Database()
        user_id = current_user.user_id

        # Check if item exists
        existing_item = db.get_work_item_by_id(item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Work item not found")

        # Convert to dict, excluding unset fields
        updates = item_data.model_dump(exclude_unset=True)

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Convert Decimals to float for database
        if 'estimated_cost' in updates and updates['estimated_cost'] is not None:
            updates['estimated_cost'] = float(updates['estimated_cost'])
        if 'actual_cost' in updates and updates['actual_cost'] is not None:
            updates['actual_cost'] = float(updates['actual_cost'])

        # Update the work item
        updated_item = db.update_work_item(item_id, updates, user_id)

        if not updated_item:
            raise HTTPException(status_code=400, detail="Failed to update work item")

        # Convert Decimal to float for response
        if 'estimated_cost' in updated_item and updated_item['estimated_cost'] is not None:
            updated_item['estimated_cost'] = float(updated_item['estimated_cost'])
        if 'actual_cost' in updated_item and updated_item['actual_cost'] is not None:
            updated_item['actual_cost'] = float(updated_item['actual_cost'])

        return updated_item
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_work_item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}", status_code=204)
async def delete_work_item(
    item_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a work item (hard delete)"""
    try:
        db = Database()

        # Check if item exists
        existing_item = db.get_work_item_by_id(item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Work item not found")

        # Delete the work item
        success = db.delete_work_item(item_id)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete work item")

        return None
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_work_item: {e}")
        raise HTTPException(status_code=500, detail=str(e))
