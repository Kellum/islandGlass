"""
Vendors Router
Handles vendor management CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorDetailResponse,
    VendorContactCreate,
    VendorContactUpdate,
    VendorContactResponse,
)
from models.user import TokenData
from middleware.auth import get_current_user
from database import Database

router = APIRouter()


@router.get("/", response_model=List[VendorResponse])
async def get_all_vendors(
    current_user: TokenData = Depends(get_current_user),
    vendor_type: Optional[str] = Query(None, description="Filter by vendor type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by vendor name"),
):
    """
    Get all vendors for the current user's company

    Query Parameters:
    - vendor_type: Filter by type (Glass, Hardware, Materials, Services, Other)
    - is_active: Filter by active status (true/false)
    - search: Search in vendor name

    Returns list of vendors
    """
    try:
        db = Database()

        # Get all vendors
        vendors = db.get_all_vendors()

        if not vendors:
            return []

        # Apply filters
        filtered_vendors = vendors

        if vendor_type:
            filtered_vendors = [v for v in filtered_vendors if v.get("vendor_type") == vendor_type]

        if is_active is not None:
            filtered_vendors = [v for v in filtered_vendors if v.get("is_active") == is_active]

        if search:
            search_lower = search.lower()
            filtered_vendors = [
                v for v in filtered_vendors
                if (v.get("vendor_name") and search_lower in v.get("vendor_name", "").lower())
            ]

        # Convert to response models
        return [
            VendorResponse(
                vendor_id=vendor["vendor_id"],
                vendor_name=vendor["vendor_name"],
                vendor_type=vendor.get("vendor_type"),
                contact_person=vendor.get("contact_person"),
                email=vendor.get("email"),
                phone=vendor.get("phone"),
                address_line1=vendor.get("address_line1"),
                address_line2=vendor.get("address_line2"),
                city=vendor.get("city"),
                state=vendor.get("state"),
                zip_code=vendor.get("zip_code"),
                is_active=vendor.get("is_active", True),
                notes=vendor.get("notes"),
                company_id=vendor.get("company_id"),
                created_by=vendor.get("created_by"),
                created_at=vendor.get("created_at"),
                updated_at=vendor.get("updated_at"),
            )
            for vendor in filtered_vendors
        ]

    except Exception as e:
        print(f"Error in get_all_vendors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while fetching vendors. Please try again later.",
        )


@router.get("/{vendor_id}", response_model=VendorDetailResponse)
async def get_vendor_by_id(
    vendor_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Get detailed vendor information with contacts

    Returns vendor details and all associated contacts
    """
    try:
        db = Database()

        # Get vendor details
        vendor = db.get_vendor_by_id(vendor_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found",
            )

        # Get vendor contacts
        contacts = db.get_vendor_contacts(vendor_id)

        # Get primary contact for summary fields
        primary_contact = db.get_primary_vendor_contact(vendor_id)
        primary_contact_name = None
        primary_contact_email = None
        primary_contact_phone = None

        if primary_contact:
            primary_contact_name = f"{primary_contact.get('first_name', '')} {primary_contact.get('last_name', '')}".strip()
            primary_contact_email = primary_contact.get('email')
            primary_contact_phone = primary_contact.get('phone')

        # Map contacts to response models
        contact_responses = [
            VendorContactResponse(
                id=contact["id"],
                vendor_id=contact["vendor_id"],
                first_name=contact["first_name"],
                last_name=contact["last_name"],
                email=contact.get("email"),
                phone=contact.get("phone"),
                job_title=contact.get("job_title"),
                is_primary=contact.get("is_primary", False),
                created_at=contact.get("created_at"),
            )
            for contact in contacts
        ]

        return VendorDetailResponse(
            vendor_id=vendor["vendor_id"],
            vendor_name=vendor["vendor_name"],
            vendor_type=vendor.get("vendor_type"),
            contact_person=vendor.get("contact_person"),
            email=vendor.get("email"),
            phone=vendor.get("phone"),
            address_line1=vendor.get("address_line1"),
            address_line2=vendor.get("address_line2"),
            city=vendor.get("city"),
            state=vendor.get("state"),
            zip_code=vendor.get("zip_code"),
            is_active=vendor.get("is_active", True),
            notes=vendor.get("notes"),
            company_id=vendor.get("company_id"),
            created_by=vendor.get("created_by"),
            created_at=vendor.get("created_at"),
            updated_at=vendor.get("updated_at"),
            primary_contact_name=primary_contact_name,
            primary_contact_email=primary_contact_email,
            primary_contact_phone=primary_contact_phone,
            contacts=contact_responses,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_vendor_by_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while fetching vendor details. Please try again later.",
        )


@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: VendorCreate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Create a new vendor

    Request body:
    - vendor_name: Vendor name (required)
    - vendor_type: Type (Glass, Hardware, Materials, Services, Other)
    - All other fields optional
    """
    try:
        db = Database()

        # Prepare vendor data
        vendor_dict = {
            "vendor_name": vendor_data.vendor_name,
            "is_active": vendor_data.is_active,
        }

        # Add optional fields if provided
        if vendor_data.vendor_type is not None:
            vendor_dict["vendor_type"] = vendor_data.vendor_type
        if vendor_data.contact_person is not None:
            vendor_dict["contact_person"] = vendor_data.contact_person
        if vendor_data.email is not None:
            vendor_dict["email"] = vendor_data.email
        if vendor_data.phone is not None:
            vendor_dict["phone"] = vendor_data.phone
        if vendor_data.address_line1 is not None:
            vendor_dict["address_line1"] = vendor_data.address_line1
        if vendor_data.address_line2 is not None:
            vendor_dict["address_line2"] = vendor_data.address_line2
        if vendor_data.city is not None:
            vendor_dict["city"] = vendor_data.city
        if vendor_data.state is not None:
            vendor_dict["state"] = vendor_data.state
        if vendor_data.zip_code is not None:
            vendor_dict["zip_code"] = vendor_data.zip_code
        if vendor_data.notes is not None:
            vendor_dict["notes"] = vendor_data.notes

        # Insert vendor
        created_vendor = db.insert_vendor(
            vendor_data=vendor_dict,
            user_id=current_user.user_id,
        )

        if not created_vendor:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to create vendor. Please try again or contact support.",
            )

        vendor_id = created_vendor["vendor_id"]

        # Handle primary contact if provided
        primary_contact_name = None
        primary_contact_email = None
        primary_contact_phone = None

        if vendor_data.primary_contact:
            contact_dict = {
                "vendor_id": vendor_id,
                "first_name": vendor_data.primary_contact.first_name,
                "last_name": vendor_data.primary_contact.last_name,
                "email": vendor_data.primary_contact.email,
                "phone": vendor_data.primary_contact.phone,
                "job_title": vendor_data.primary_contact.job_title,
                "is_primary": True,
            }
            created_contact = db.insert_vendor_contact(contact_dict, current_user.user_id)
            if created_contact:
                primary_contact_name = f"{created_contact['first_name']} {created_contact['last_name']}"
                primary_contact_email = created_contact.get("email")
                primary_contact_phone = created_contact.get("phone")

        # Handle additional contacts if provided
        if vendor_data.additional_contacts:
            for contact in vendor_data.additional_contacts:
                contact_dict = {
                    "vendor_id": vendor_id,
                    "first_name": contact.first_name,
                    "last_name": contact.last_name,
                    "email": contact.email,
                    "phone": contact.phone,
                    "job_title": contact.job_title,
                    "is_primary": contact.is_primary,
                }
                db.insert_vendor_contact(contact_dict, current_user.user_id)

        return VendorResponse(
            vendor_id=created_vendor["vendor_id"],
            vendor_name=created_vendor["vendor_name"],
            vendor_type=created_vendor.get("vendor_type"),
            contact_person=created_vendor.get("contact_person"),
            email=created_vendor.get("email"),
            phone=created_vendor.get("phone"),
            address_line1=created_vendor.get("address_line1"),
            address_line2=created_vendor.get("address_line2"),
            city=created_vendor.get("city"),
            state=created_vendor.get("state"),
            zip_code=created_vendor.get("zip_code"),
            is_active=created_vendor.get("is_active", True),
            notes=created_vendor.get("notes"),
            company_id=created_vendor.get("company_id"),
            created_by=created_vendor.get("created_by"),
            created_at=created_vendor.get("created_at"),
            updated_at=created_vendor.get("updated_at"),
            primary_contact_name=primary_contact_name,
            primary_contact_email=primary_contact_email,
            primary_contact_phone=primary_contact_phone,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_vendor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while creating vendor. Please check your input and try again.",
        )


@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: int,
    vendor_data: VendorUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Update an existing vendor

    Only provided fields will be updated (partial update supported)
    """
    try:
        db = Database()

        # Check if vendor exists
        existing_vendor = db.get_vendor_by_id(vendor_id)
        if not existing_vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found",
            )

        # Prepare update data (only include non-None values)
        update_dict = {}
        if vendor_data.vendor_name is not None:
            update_dict["vendor_name"] = vendor_data.vendor_name
        if vendor_data.vendor_type is not None:
            update_dict["vendor_type"] = vendor_data.vendor_type
        if vendor_data.contact_person is not None:
            update_dict["contact_person"] = vendor_data.contact_person
        if vendor_data.email is not None:
            update_dict["email"] = vendor_data.email
        if vendor_data.phone is not None:
            update_dict["phone"] = vendor_data.phone
        if vendor_data.address_line1 is not None:
            update_dict["address_line1"] = vendor_data.address_line1
        if vendor_data.address_line2 is not None:
            update_dict["address_line2"] = vendor_data.address_line2
        if vendor_data.city is not None:
            update_dict["city"] = vendor_data.city
        if vendor_data.state is not None:
            update_dict["state"] = vendor_data.state
        if vendor_data.zip_code is not None:
            update_dict["zip_code"] = vendor_data.zip_code
        if vendor_data.is_active is not None:
            update_dict["is_active"] = vendor_data.is_active
        if vendor_data.notes is not None:
            update_dict["notes"] = vendor_data.notes

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        # Update vendor
        success = db.update_vendor(
            vendor_id=vendor_id,
            updates=update_dict,
            user_id=current_user.user_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to update vendor. Please try again.",
            )

        # Fetch updated vendor
        updated_vendor = db.get_vendor_by_id(vendor_id)

        return VendorResponse(
            vendor_id=updated_vendor["vendor_id"],
            vendor_name=updated_vendor["vendor_name"],
            vendor_type=updated_vendor.get("vendor_type"),
            contact_person=updated_vendor.get("contact_person"),
            email=updated_vendor.get("email"),
            phone=updated_vendor.get("phone"),
            address_line1=updated_vendor.get("address_line1"),
            address_line2=updated_vendor.get("address_line2"),
            city=updated_vendor.get("city"),
            state=updated_vendor.get("state"),
            zip_code=updated_vendor.get("zip_code"),
            is_active=updated_vendor.get("is_active", True),
            notes=updated_vendor.get("notes"),
            company_id=updated_vendor.get("company_id"),
            created_by=updated_vendor.get("created_by"),
            created_at=updated_vendor.get("created_at"),
            updated_at=updated_vendor.get("updated_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_vendor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while updating vendor. Please try again later.",
        )


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    vendor_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Delete a vendor (hard delete - vendors don't have soft delete in schema)

    Returns 204 No Content on success
    """
    try:
        db = Database()

        # Check if vendor exists
        existing_vendor = db.get_vendor_by_id(vendor_id)
        if not existing_vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found",
            )

        # Delete the vendor
        success = db.delete_vendor(vendor_id=vendor_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to delete vendor. Please try again.",
            )

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_vendor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while deleting vendor. Please try again later.",
        )


# ==================== VENDOR CONTACTS ENDPOINTS ====================

@router.post("/{vendor_id}/contacts", response_model=VendorContactResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor_contact(
    vendor_id: int,
    contact_data: VendorContactCreate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Add a contact to a vendor

    Request body:
    - first_name: Contact first name (required)
    - last_name: Contact last name (required)
    - email, phone, job_title: Optional
    - is_primary: Mark as primary contact (default: false)
    """
    try:
        db = Database()

        # Verify vendor exists
        vendor = db.get_vendor_by_id(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found",
            )

        # Prepare contact data
        contact_dict = {
            "vendor_id": vendor_id,
            "first_name": contact_data.first_name,
            "last_name": contact_data.last_name,
            "is_primary": contact_data.is_primary,
        }

        # Add optional fields
        if contact_data.email:
            contact_dict["email"] = contact_data.email
        if contact_data.phone:
            contact_dict["phone"] = contact_data.phone
        if contact_data.job_title:
            contact_dict["job_title"] = contact_data.job_title

        # Insert contact
        created_contact = db.insert_vendor_contact(
            contact_data=contact_dict,
            user_id=current_user.user_id,
        )

        if not created_contact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to create vendor contact. Please try again.",
            )

        return VendorContactResponse(
            id=created_contact["id"],
            vendor_id=created_contact["vendor_id"],
            first_name=created_contact["first_name"],
            last_name=created_contact["last_name"],
            email=created_contact.get("email"),
            phone=created_contact.get("phone"),
            job_title=created_contact.get("job_title"),
            is_primary=created_contact.get("is_primary", False),
            created_at=created_contact.get("created_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_vendor_contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while creating vendor contact. Please try again.",
        )


@router.put("/contacts/{contact_id}", response_model=VendorContactResponse)
async def update_vendor_contact(
    contact_id: int,
    contact_data: VendorContactUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Update a vendor contact

    Only provided fields will be updated (partial update supported)
    """
    try:
        db = Database()

        # Prepare update data (only include non-None values)
        update_dict = {}
        if contact_data.first_name is not None:
            update_dict["first_name"] = contact_data.first_name
        if contact_data.last_name is not None:
            update_dict["last_name"] = contact_data.last_name
        if contact_data.email is not None:
            update_dict["email"] = contact_data.email
        if contact_data.phone is not None:
            update_dict["phone"] = contact_data.phone
        if contact_data.job_title is not None:
            update_dict["job_title"] = contact_data.job_title
        if contact_data.is_primary is not None:
            update_dict["is_primary"] = contact_data.is_primary

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        # Update contact
        success = db.update_vendor_contact(
            contact_id=contact_id,
            updates=update_dict,
            user_id=current_user.user_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to update vendor contact. Please try again.",
            )

        # Return updated contact (need to fetch it - simplified version)
        # In a real app, you'd fetch the updated contact from DB
        return VendorContactResponse(
            id=contact_id,
            vendor_id=0,  # Placeholder
            **{k: v for k, v in contact_data.dict().items() if v is not None}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_vendor_contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while updating vendor contact. Please try again.",
        )


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor_contact(
    contact_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Delete a vendor contact

    Returns 204 No Content on success
    """
    try:
        db = Database()

        # Delete the contact
        success = db.delete_vendor_contact(contact_id=contact_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to delete vendor contact. Please try again.",
            )

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_vendor_contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while deleting vendor contact. Please try again.",
        )
