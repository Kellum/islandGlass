"""
Material Templates API Routes - Master list for quick job entry

This module provides CRUD operations for material templates.
Templates are reusable material definitions with categories and optional vendor links.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from models.material_template import MaterialTemplate, MaterialTemplateCreate, MaterialTemplateUpdate
from models.user import TokenData
from database import Database
from middleware.auth import get_current_user

router = APIRouter(tags=["material-templates"])


@router.get("/", response_model=List[MaterialTemplate])
async def get_material_templates(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all material templates with optional filters

    Filters:
    - category: Glass, Hardware, Frame, Misc, Custom
    - is_active: true/false

    Returns templates sorted by sort_order
    """
    try:
        db = Database()
        templates = db.get_all_material_templates()

        # Apply filters
        if category:
            templates = [t for t in templates if t.get('category') == category]

        if is_active is not None:
            templates = [t for t in templates if t.get('is_active') == is_active]

        return templates
    except Exception as e:
        print(f"Error in get_material_templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}", response_model=MaterialTemplate)
async def get_material_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific material template by ID"""
    try:
        db = Database()
        template = db.get_material_template_by_id(template_id)

        if not template:
            raise HTTPException(status_code=404, detail="Material template not found")

        return template
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_material_template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=MaterialTemplate, status_code=201)
async def create_material_template(
    template_data: MaterialTemplateCreate,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new material template"""
    try:
        db = Database()
        user_id = current_user.user_id

        # Convert Pydantic model to dict
        template_dict = template_data.model_dump()

        # Create the template
        new_template = db.insert_material_template(template_dict, user_id)

        if not new_template:
            raise HTTPException(status_code=400, detail="Failed to create material template")

        return new_template
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_material_template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{template_id}", response_model=MaterialTemplate)
async def update_material_template(
    template_id: int,
    template_data: MaterialTemplateUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update an existing material template"""
    try:
        db = Database()
        user_id = current_user.user_id

        # Check if template exists
        existing_template = db.get_material_template_by_id(template_id)
        if not existing_template:
            raise HTTPException(status_code=404, detail="Material template not found")

        # Convert to dict, excluding unset fields
        updates = template_data.model_dump(exclude_unset=True)

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Update the template
        updated_template = db.update_material_template(template_id, updates, user_id)

        if not updated_template:
            raise HTTPException(status_code=400, detail="Failed to update material template")

        return updated_template
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_material_template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}", status_code=204)
async def delete_material_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a material template (hard delete)"""
    try:
        db = Database()

        # Check if template exists
        existing_template = db.get_material_template_by_id(template_id)
        if not existing_template:
            raise HTTPException(status_code=404, detail="Material template not found")

        # Delete the template
        success = db.delete_material_template(template_id)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete material template")

        return None
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_material_template: {e}")
        raise HTTPException(status_code=500, detail=str(e))
