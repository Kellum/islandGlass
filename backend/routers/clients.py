"""
Clients Router
Handles client management CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientDetailResponse,
    ClientContactResponse,
)
from models.user import TokenData
from middleware.auth import get_current_user
from database import Database

router = APIRouter()


@router.get("/", response_model=List[ClientResponse])
async def get_all_clients(
    current_user: TokenData = Depends(get_current_user),
    client_type: Optional[str] = Query(None, description="Filter by client type: residential, contractor, commercial"),
    city: Optional[str] = Query(None, description="Filter by city"),
    search: Optional[str] = Query(None, description="Search by name or company"),
):
    """
    Get all clients for the current user's company

    Query Parameters:
    - client_type: Filter by type (residential, contractor, commercial)
    - city: Filter by city
    - search: Search in company name or contact names

    Returns list of clients with basic info
    """
    try:
        db = Database()

        # Get user's company_id for scoping
        company_id = db.get_user_company_id(current_user.user_id)
        if not company_id:
            # Fallback to default company for testing
            company_id = "720d425e-bb02-4612-9b35-70bded465dca"
            print(f"Using default company_id for user {current_user.user_id}")

        # Query clients with company scoping
        response = db.client.table("po_clients").select("*").eq("company_id", company_id).is_("deleted_at", "null").order("created_at", desc=True).execute()
        clients = response.data if response.data else []

        if not clients:
            return []

        # Apply filters
        filtered_clients = clients

        if client_type:
            filtered_clients = [c for c in filtered_clients if c.get("client_type") == client_type]

        if city:
            filtered_clients = [c for c in filtered_clients if c.get("city", "").lower() == city.lower()]

        if search:
            search_lower = search.lower()
            filtered_clients = [
                c for c in filtered_clients
                if (c.get("client_name") and search_lower in c.get("client_name", "").lower())
                or (c.get("primary_contact_name") and search_lower in c.get("primary_contact_name", "").lower())
            ]

        # For each client, fetch primary contact info
        client_responses = []
        for client in filtered_clients:
            # Get primary contact for this client
            primary_contact = None
            try:
                contacts = db.get_client_contacts(client["id"])
                primary_contact = next((c for c in contacts if c.get("is_primary")), contacts[0] if contacts else None)
            except:
                pass

            client_responses.append(
                ClientResponse(
                    id=client["id"],
                    client_type=client["client_type"],
                    client_name=client.get("client_name"),
                    address=client.get("address"),
                    city=client.get("city"),
                    state=client.get("state"),
                    zip_code=client.get("zip_code"),
                    company_id=client.get("company_id"),
                    created_at=client.get("created_at"),
                    updated_at=client.get("updated_at"),
                    created_by=client.get("created_by"),
                    updated_by=client.get("updated_by"),
                    primary_contact_email=primary_contact.get("email") if primary_contact else None,
                    primary_contact_phone=primary_contact.get("phone") if primary_contact else None,
                )
            )

        return client_responses

    except Exception as e:
        print(f"Error in get_all_clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while fetching clients. Please try again later.",
        )


@router.get("/{client_id}", response_model=ClientDetailResponse)
async def get_client_by_id(
    client_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Get detailed client information including contacts and job statistics

    Returns:
    - Client details
    - All contacts for this client
    - Number of jobs
    - Total revenue from jobs
    """
    try:
        db = Database()

        # Get client details
        client = db.get_po_client_by_id(client_id)

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found",
            )

        # Get contacts for this client
        contacts = db.get_client_contacts(client_id)
        contact_responses = [
            ClientContactResponse(
                id=contact["id"],
                client_id=contact["client_id"],
                first_name=contact["first_name"],
                last_name=contact["last_name"],
                email=contact.get("email"),
                phone=contact.get("phone"),
                is_primary=contact.get("is_primary", False),
                created_at=contact.get("created_at"),
            )
            for contact in contacts
        ]

        # Get job statistics (if jobs system is available)
        job_count = 0
        total_revenue = 0.0
        try:
            jobs = db.get_jobs_by_client(client_id)
            job_count = len(jobs)
            # Sum up actual costs from completed jobs
            total_revenue = sum(
                float(job.get("actual_cost", 0) or 0)
                for job in jobs
                if job.get("status") == "Completed" and job.get("actual_cost")
            )
        except:
            # Jobs table might not exist yet, that's okay
            pass

        return ClientDetailResponse(
            id=client["id"],
            client_type=client["client_type"],
            client_name=client.get("client_name"),
            address=client.get("address"),
            city=client.get("city"),
            state=client.get("state"),
            zipcode=client.get("zipcode"),
            company_id=client.get("company_id"),
            created_at=client.get("created_at"),
            updated_at=client.get("updated_at"),
            created_by=client.get("created_by"),
            updated_by=client.get("updated_by"),
            contacts=contact_responses,
            job_count=job_count,
            total_revenue=total_revenue,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_client_by_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while fetching client details. Please try again later.",
        )


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Create a new client with primary contact

    Request body:
    - client_type: residential, contractor, or commercial
    - client_name: Client or company name
    - address, city, state, zipcode: Address info
    - primary_contact: First name, last name, email, phone
    - additional_contacts: Optional list of additional contacts
    """
    try:
        db = Database()

        # Prepare client data (only include non-None values)
        client_dict = {
            "client_type": client_data.client_type,
        }

        # For residential clients without a client_name, use the contact name
        # For contractor/commercial, client_name is required
        if client_data.client_name is not None:
            client_dict["client_name"] = client_data.client_name
        elif client_data.client_type == "residential":
            # Auto-generate client_name from primary contact
            client_dict["client_name"] = f"{client_data.primary_contact.first_name} {client_data.primary_contact.last_name}"

        if client_data.address is not None:
            client_dict["address"] = client_data.address
        if client_data.city is not None:
            client_dict["city"] = client_data.city
        if client_data.state is not None:
            client_dict["state"] = client_data.state
        # TODO: Fix zip_code - database column name mismatch
        # if client_data.zip_code is not None:
        #     client_dict["zip_code"] = client_data.zip_code

        # Insert client first
        # Pass user_id from JWT token for audit trail
        created_client = db.insert_po_client(
            client_data=client_dict,
            user_id=current_user.user_id,  # Use authenticated user ID
        )

        if not created_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to create client. Please try again or contact support.",
            )

        client_id = created_client["id"]

        # Now insert primary contact
        primary_contact = {
            "client_id": client_id,
            "first_name": client_data.primary_contact.first_name,
            "last_name": client_data.primary_contact.last_name,
            "email": client_data.primary_contact.email,
            "phone": client_data.primary_contact.phone,
            "is_primary": True,
        }

        contact_result = db.insert_client_contact(
            contact_data=primary_contact,
            user_id=current_user.user_id,
        )

        if not contact_result:
            # Contact creation failed - log warning but don't fail the whole request
            # Client was already created successfully
            print(f"Warning: Failed to create primary contact for client {client_id}")

        # Add additional contacts if provided
        if client_data.additional_contacts:
            for contact in client_data.additional_contacts:
                contact_dict = {
                    "client_id": client_id,
                    "first_name": contact.first_name,
                    "last_name": contact.last_name,
                    "email": contact.email,
                    "phone": contact.phone,
                    "is_primary": False,
                }
                result = db.insert_client_contact(
                    contact_dict,
                    user_id=current_user.user_id,
                )
                if not result:
                    print(f"Warning: Failed to create additional contact for client {client_id}")

        # Fetch the created client to return (already have it from insert)
        # But refetch to ensure we have the latest data
        created_client = db.get_po_client_by_id(client_id)

        return ClientResponse(
            id=created_client["id"],
            client_type=created_client["client_type"],
            client_name=created_client.get("client_name"),
            address=created_client.get("address"),
            city=created_client.get("city"),
            state=created_client.get("state"),
            zipcode=created_client.get("zipcode"),
            company_id=created_client.get("company_id"),
            created_at=created_client.get("created_at"),
            updated_at=created_client.get("updated_at"),
            created_by=created_client.get("created_by"),
            updated_by=created_client.get("updated_by"),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while creating client. Please check your input and try again.",
        )


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Update an existing client

    Only provided fields will be updated (partial update supported)
    """
    try:
        db = Database()

        # Check if client exists
        existing_client = db.get_po_client_by_id(client_id)
        if not existing_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found",
            )

        # Prepare update data (only include non-None values)
        update_dict = {}
        if client_data.client_type is not None:
            update_dict["client_type"] = client_data.client_type
        if client_data.client_name is not None:
            update_dict["client_name"] = client_data.client_name
        if client_data.address is not None:
            update_dict["address"] = client_data.address
        if client_data.city is not None:
            update_dict["city"] = client_data.city
        if client_data.state is not None:
            update_dict["state"] = client_data.state
        # TODO: Fix zip_code - database column name mismatch
        # if client_data.zip_code is not None:
        #     update_dict["zip_code"] = client_data.zip_code

        if not update_dict:
            # No fields to update
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        # Update client (returns bool)
        success = db.update_po_client(
            client_id=client_id,
            updates=update_dict,
            user_id=current_user.user_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to update client. Please try again.",
            )

        # Fetch updated client
        updated_client = db.get_po_client_by_id(client_id)

        return ClientResponse(
            id=updated_client["id"],
            client_type=updated_client["client_type"],
            client_name=updated_client.get("client_name"),
            address=updated_client.get("address"),
            city=updated_client.get("city"),
            state=updated_client.get("state"),
            zipcode=updated_client.get("zipcode"),
            company_id=updated_client.get("company_id"),
            created_at=updated_client.get("created_at"),
            updated_at=updated_client.get("updated_at"),
            created_by=updated_client.get("created_by"),
            updated_by=updated_client.get("updated_by"),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while updating client. Please try again later.",
        )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Soft delete a client (sets deleted_at timestamp)

    Returns 204 No Content on success
    """
    try:
        db = Database()

        # Check if client exists
        existing_client = db.get_po_client_by_id(client_id)
        if not existing_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found",
            )

        # Soft delete the client (returns bool)
        success = db.delete_po_client(
            client_id=client_id,
            user_id=current_user.user_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Unable to delete client. Please try again.",
            )

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while deleting client. Please try again later.",
        )
