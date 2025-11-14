"""
PO Number Auto-Generation Utility
Island Glass CRM

Generates PO numbers based on location, client name, and address
Format: PO-{location}-{name}.{street_number}[-{sequence}]

Examples:
  - Regular: PO-01-Ryan.Kellum.3432
  - Company: PO-02-AcmeGlass.4567
  - Remake: PO-01-RMK.Kellum.3432
  - Warranty: PO-03-WAR.Kellum.3432
  - Duplicate: PO-01-Ryan.Kellum.3432-2
"""

import re
from typing import Optional, Dict, Any
from supabase import Client


class POGenerationError(Exception):
    """Custom exception for PO generation errors"""
    pass


def extract_street_number(address: Optional[str]) -> Optional[str]:
    """
    Extract first numeric value from address string

    Args:
        address: Full address string (e.g., "123 Main St Apt 4B")

    Returns:
        First number found in address (e.g., "123")
        None if no number found

    Examples:
        >>> extract_street_number("123 Main St")
        "123"
        >>> extract_street_number("PO Box 456")
        "456"
        >>> extract_street_number("No Number Lane")
        None
    """
    if not address:
        return None

    # Match first sequence of digits
    match = re.search(r'\d+', address)
    if match:
        return match.group()

    return None


def format_name_for_po(
    client_name: Optional[str],
    contact_name: Optional[str],
    is_remake: bool = False,
    is_warranty: bool = False
) -> str:
    """
    Format client/contact name for PO number

    Args:
        client_name: Company name (from po_clients.company_name)
        contact_name: Contact name (from client_contacts, usually first_name + last_name)
        is_remake: Whether this is a remake job
        is_warranty: Whether this is a warranty job

    Returns:
        Formatted name string for PO

    Logic:
        - Remake: "RMK.LastName"
        - Warranty: "WAR.LastName"
        - Company: "CompanyName" (no spaces)
        - Individual: "FirstName.LastName"

    Examples:
        >>> format_name_for_po("Acme Glass", None)
        "AcmeGlass"
        >>> format_name_for_po(None, "Ryan Kellum")
        "Ryan.Kellum"
        >>> format_name_for_po(None, "Ryan Kellum", is_remake=True)
        "RMK.Kellum"
    """
    # Handle remakes
    if is_remake:
        if contact_name:
            # Extract last name from contact_name
            parts = contact_name.strip().split()
            last_name = parts[-1] if parts else 'UNKNOWN'
            return f"RMK.{last_name.replace(' ', '')}"
        elif client_name:
            return f"RMK.{client_name.strip().replace(' ', '')}"
        else:
            return "RMK.UNKNOWN"

    # Handle warranties
    if is_warranty:
        if contact_name:
            # Extract last name from contact_name
            parts = contact_name.strip().split()
            last_name = parts[-1] if parts else 'UNKNOWN'
            return f"WAR.{last_name.replace(' ', '')}"
        elif client_name:
            return f"WAR.{client_name.strip().replace(' ', '')}"
        else:
            return "WAR.UNKNOWN"

    # Regular jobs: Prefer company name, fall back to contact name
    if client_name and client_name.strip():
        # Use company name, remove spaces
        return client_name.strip().replace(' ', '')
    elif contact_name and contact_name.strip():
        # Format as FirstName.LastName
        parts = contact_name.strip().split()
        if len(parts) >= 2:
            first_name = parts[0]
            last_name = parts[-1]
            return f"{first_name}.{last_name}"
        else:
            # Only one name provided
            return contact_name.strip().replace(' ', '')
    else:
        return "UNKNOWN"


async def count_duplicate_pos(
    supabase: Client,
    client_id: int,
    location_code: str,
    name_part: str,
    street_number: str
) -> int:
    """
    Count existing POs matching the base pattern for this client/location

    Args:
        supabase: Supabase client instance
        client_id: Client ID
        location_code: Location code (01, 02, 03)
        name_part: Formatted name portion of PO
        street_number: Street number from address

    Returns:
        Count of existing matching POs

    Used for determining sequence number for duplicates
    """
    base_po = f"PO-{location_code}-{name_part}.{street_number}"

    # Query for POs that match base pattern (exact match or with suffix)
    # Using ilike for case-insensitive matching
    result = supabase.table('jobs').select('po_number').match({
        'client_id': client_id,
        'location_code': location_code
    }).is_('deleted_at', 'null').execute()

    # Count POs that match our pattern
    count = 0
    if result.data:
        for job in result.data:
            po = job.get('po_number', '')
            # Check if PO matches our base pattern (with or without sequence)
            if po == base_po or po.startswith(f"{base_po}-"):
                count += 1

    return count


async def generate_po_number(
    supabase: Client,
    client_id: int,
    location_code: str,
    is_remake: bool = False,
    is_warranty: bool = False,
    site_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a PO number based on client data and location

    Args:
        supabase: Supabase client instance
        client_id: ID of the client
        location_code: Location code (01, 02, or 03)
        is_remake: Whether this is a remake job
        is_warranty: Whether this is a warranty job
        site_address: Optional site address override (if different from client address)

    Returns:
        Dictionary with:
            - po_number: Generated PO number string
            - is_duplicate: Boolean indicating if this is a duplicate
            - warning: Optional warning message

    Raises:
        POGenerationError: If unable to generate PO number

    Examples:
        >>> await generate_po_number(supabase, 123, "01", False, False)
        {"po_number": "PO-01-Ryan.Kellum.3432", "is_duplicate": False}
        >>> await generate_po_number(supabase, 123, "01", True, False)
        {"po_number": "PO-01-RMK.Kellum.3432", "is_duplicate": False}
    """
    # Validate location code
    valid_locations = ['01', '02', '03']
    if location_code not in valid_locations:
        raise POGenerationError(
            f"Invalid location code '{location_code}'. Must be one of: {', '.join(valid_locations)}"
        )

    # Validate remake/warranty combination
    if is_remake and is_warranty:
        raise POGenerationError("A job cannot be both a remake and a warranty job")

    # Fetch client data
    client_result = supabase.table('po_clients').select(
        'id, client_name, address'
    ).eq('id', client_id).single().execute()

    if not client_result.data:
        raise POGenerationError(f"Client with ID {client_id} not found")

    client_data = client_result.data

    # Use client_name from po_clients as the contact name
    # This is simpler than the client_contacts approach
    contact_name = client_data.get('client_name')

    # Determine which address to use
    address = site_address if site_address else client_data.get('address')

    # Extract street number
    street_number = extract_street_number(address)
    if not street_number:
        raise POGenerationError(
            f"Unable to extract street number from address: '{address}'. "
            "Please ensure the address contains a number or manually enter the PO number."
        )

    # Format name for PO
    # Use client_name for both individual and company names
    # The format_name_for_po function will handle the formatting
    name_part = format_name_for_po(
        client_name=None,  # Don't use company_name
        contact_name=contact_name,  # Use client_name as contact_name
        is_remake=is_remake,
        is_warranty=is_warranty
    )

    # Check for duplicates
    duplicate_count = await count_duplicate_pos(
        supabase, client_id, location_code, name_part, street_number
    )

    # Build PO number
    base_po = f"PO-{location_code}-{name_part}.{street_number}"

    if duplicate_count > 0:
        # This is a duplicate, add sequence number
        sequence = duplicate_count + 1
        po_number = f"{base_po}-{sequence}"
        is_duplicate = True
        warning = f"This is duplicate #{sequence} for this client/location/address"
    else:
        # First PO with this pattern
        po_number = base_po
        is_duplicate = False
        warning = None

    return {
        "po_number": po_number,
        "is_duplicate": is_duplicate,
        "warning": warning,
        "location_code": location_code,
        "street_number": street_number,
        "name_part": name_part
    }


async def validate_po_format(po_number: str) -> Dict[str, Any]:
    """
    Validate if a PO number follows the expected format

    Args:
        po_number: PO number string to validate

    Returns:
        Dictionary with:
            - is_valid: Boolean indicating if format is correct
            - warning: Optional warning message if format doesn't match

    Used for showing warnings when users manually edit PO numbers
    """
    # Expected format: PO-{location}-{name}.{number}[-{sequence}]
    pattern = r'^PO-\d{2}-[A-Za-z0-9.]+\.\d+(-\d+)?$'

    is_valid = bool(re.match(pattern, po_number))

    if not is_valid:
        return {
            "is_valid": False,
            "warning": (
                "PO number doesn't follow standard format. "
                "Expected: PO-{location}-{name}.{number} (e.g., PO-01-Ryan.Kellum.3432)"
            )
        }

    return {
        "is_valid": True,
        "warning": None
    }
