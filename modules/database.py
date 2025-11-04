"""
Database module for Supabase connection and operations
"""
import os
from supabase import create_client, Client
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    """Handle all Supabase database operations"""

    def __init__(self, access_token: Optional[str] = None):
        """Initialize Supabase client

        Args:
            access_token: Optional JWT access token for authenticated requests (enables RLS)
        """
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "Missing Supabase credentials. "
                "Please set SUPABASE_URL and SUPABASE_KEY in .env file"
            )

        self.client: Client = create_client(self.url, self.key)

        # If access token provided, set it for RLS-enabled queries
        if access_token:
            self.client.postgrest.auth(access_token)

    def get_user_company_id(self, user_id: str) -> Optional[str]:
        """Get the company_id for a given user_id

        Args:
            user_id: The auth.users UUID

        Returns:
            company_id UUID or None if not found
        """
        try:
            response = self.client.table("user_profiles").select("company_id").eq("user_id", user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]['company_id']
            return None
        except Exception as e:
            print(f"Error fetching company_id for user {user_id}: {e}")
            return None

    def get_all_contractors(self) -> List[Dict]:
        """Get all contractors from database"""
        try:
            response = self.client.table("contractors").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching contractors: {e}")
            return []

    def get_contractor_by_id(self, contractor_id: int) -> Optional[Dict]:
        """Get a single contractor by ID"""
        try:
            response = self.client.table("contractors").select("*").eq("id", contractor_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching contractor {contractor_id}: {e}")
            return None

    def search_contractors(
        self,
        search_term: str = None,
        city: str = None,
        min_score: int = None,
        max_score: int = None,
        company_type: str = None
    ) -> List[Dict]:
        """Search contractors with filters"""
        try:
            query = self.client.table("contractors").select("*")

            if search_term:
                query = query.ilike("company_name", f"%{search_term}%")

            if city:
                query = query.eq("city", city)

            if min_score is not None:
                query = query.gte("lead_score", min_score)

            if max_score is not None:
                query = query.lte("lead_score", max_score)

            if company_type:
                query = query.eq("company_type", company_type)

            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error searching contractors: {e}")
            return []

    def insert_contractor(self, contractor_data: Dict, user_id: str = None) -> Optional[Dict]:
        """Insert a new contractor with optional audit trail"""
        try:
            # Add audit fields if user_id provided
            if user_id:
                contractor_data['created_by'] = user_id
                contractor_data['user_id'] = user_id

            response = self.client.table("contractors").insert(contractor_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error inserting contractor: {e}")
            return None

    def update_contractor(self, contractor_id: int, updates: Dict, user_id: str = None) -> bool:
        """Update contractor information with optional audit trail"""
        try:
            # Add audit field if user_id provided
            if user_id:
                updates['updated_by'] = user_id

            self.client.table("contractors").update(updates).eq("id", contractor_id).execute()
            return True
        except Exception as e:
            print(f"Error updating contractor {contractor_id}: {e}")
            return False

    def log_interaction(
        self,
        contractor_id: int,
        status: str,
        notes: str = None,
        user_name: str = None,
        user_id: str = None
    ) -> bool:
        """Log an interaction with a contractor (with optional user_id for audit trail)"""
        try:
            interaction_data = {
                "contractor_id": contractor_id,
                "status": status,
                "notes": notes,
                "user_name": user_name
            }

            # Add user_id for audit trail if provided
            if user_id:
                interaction_data['user_id'] = user_id

            self.client.table("interaction_log").insert(interaction_data).execute()
            return True
        except Exception as e:
            print(f"Error logging interaction: {e}")
            return False

    def get_interaction_history(self, contractor_id: int) -> List[Dict]:
        """Get interaction history for a contractor"""
        try:
            response = (
                self.client.table("interaction_log")
                .select("*")
                .eq("contractor_id", contractor_id)
                .order("timestamp", desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching interaction history: {e}")
            return []

    def get_outreach_materials(self, contractor_id: int) -> List[Dict]:
        """Get all outreach materials for a contractor"""
        try:
            response = (
                self.client.table("outreach_materials")
                .select("*")
                .eq("contractor_id", contractor_id)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching outreach materials: {e}")
            return []

    def save_outreach_material(
        self,
        contractor_id: int,
        material_type: str,
        content: str,
        subject_line: str = None
    ) -> bool:
        """Save or update outreach material"""
        try:
            material_data = {
                "contractor_id": contractor_id,
                "material_type": material_type,
                "content": content,
                "subject_line": subject_line
            }
            self.client.table("outreach_materials").insert(material_data).execute()
            return True
        except Exception as e:
            print(f"Error saving outreach material: {e}")
            return False

    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        try:
            # Total contractors
            total_response = self.client.table("contractors").select("id", count="exact").execute()
            total_count = total_response.count if hasattr(total_response, 'count') else len(total_response.data)

            # High priority leads (score 8+)
            high_priority = self.client.table("contractors").select("*").gte("lead_score", 8).execute()

            return {
                "total_contractors": total_count,
                "high_priority_leads": len(high_priority.data) if high_priority.data else 0
            }
        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
            return {"total_contractors": 0, "high_priority_leads": 0}

    # API Usage Tracking Methods
    def log_api_usage(
        self,
        action_type: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float,
        contractor_id: int = None,
        success: bool = True
    ) -> bool:
        """Log Claude API token usage"""
        try:
            usage_data = {
                "contractor_id": contractor_id,
                "action_type": action_type,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "estimated_cost": estimated_cost,
                "success": success
            }
            self.client.table("api_usage").insert(usage_data).execute()
            return True
        except Exception as e:
            print(f"Error logging API usage: {e}")
            return False

    def get_total_api_usage(self) -> Dict:
        """Get total API usage statistics"""
        try:
            response = self.client.table("api_usage").select("*").execute()

            if not response.data:
                return {
                    "total_calls": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "by_action": {}
                }

            total_calls = len(response.data)
            total_tokens = sum([record['total_tokens'] for record in response.data])
            total_cost = sum([float(record['estimated_cost']) for record in response.data])

            # Break down by action type
            by_action = {}
            for record in response.data:
                action = record['action_type']
                if action not in by_action:
                    by_action[action] = {
                        "calls": 0,
                        "tokens": 0,
                        "cost": 0.0
                    }
                by_action[action]["calls"] += 1
                by_action[action]["tokens"] += record['total_tokens']
                by_action[action]["cost"] += float(record['estimated_cost'])

            return {
                "total_calls": total_calls,
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "by_action": by_action
            }
        except Exception as e:
            print(f"Error fetching total API usage: {e}")
            return {
                "total_calls": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "by_action": {}
            }

    def get_api_usage_this_month(self) -> Dict:
        """Get API usage for current month"""
        try:
            from datetime import datetime

            # Get first day of current month
            today = datetime.now()
            first_day = datetime(today.year, today.month, 1).isoformat()

            response = self.client.table("api_usage")\
                .select("*")\
                .gte("timestamp", first_day)\
                .execute()

            if not response.data:
                return {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0
                }

            return {
                "calls": len(response.data),
                "tokens": sum([record['total_tokens'] for record in response.data]),
                "cost": sum([float(record['estimated_cost']) for record in response.data])
            }
        except Exception as e:
            print(f"Error fetching monthly API usage: {e}")
            return {"calls": 0, "tokens": 0, "cost": 0.0}

    def get_contractor_api_usage(self, contractor_id: int) -> Dict:
        """Get API usage for a specific contractor"""
        try:
            response = self.client.table("api_usage")\
                .select("*")\
                .eq("contractor_id", contractor_id)\
                .execute()

            if not response.data:
                return {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0
                }

            return {
                "calls": len(response.data),
                "tokens": sum([record['total_tokens'] for record in response.data]),
                "cost": sum([float(record['estimated_cost']) for record in response.data])
            }
        except Exception as e:
            print(f"Error fetching contractor API usage: {e}")
            return {"calls": 0, "tokens": 0, "cost": 0.0}

    def get_top_contractors_by_usage(self, limit: int = 10) -> list:
        """Get contractors with highest API usage"""
        try:
            # Get all usage records
            response = self.client.table("api_usage").select("*").execute()

            if not response.data:
                return []

            # Group by contractor_id
            contractor_usage = {}
            for record in response.data:
                cid = record.get('contractor_id')
                if cid:
                    if cid not in contractor_usage:
                        contractor_usage[cid] = {
                            "contractor_id": cid,
                            "calls": 0,
                            "tokens": 0,
                            "cost": 0.0
                        }
                    contractor_usage[cid]["calls"] += 1
                    contractor_usage[cid]["tokens"] += record['total_tokens']
                    contractor_usage[cid]["cost"] += float(record['estimated_cost'])

            # Sort by cost and get top N
            sorted_contractors = sorted(
                contractor_usage.values(),
                key=lambda x: x["cost"],
                reverse=True
            )[:limit]

            # Add contractor names
            for item in sorted_contractors:
                contractor = self.get_contractor_by_id(item["contractor_id"])
                if contractor:
                    item["company_name"] = contractor.get("company_name", "Unknown")

            return sorted_contractors

        except Exception as e:
            print(f"Error fetching top contractors by usage: {e}")
            return []

    # ========== User Management Methods ==========

    def get_all_users(self) -> List[Dict]:
        """Get all users from database"""
        from modules import auth
        return auth.get_all_users()

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get a single user by ID"""
        from modules import auth
        return auth.get_current_user(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get a user by email address"""
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None

    # ========== Glass Calculator Methods ==========

    def get_glass_config(self) -> List[Dict]:
        """Get all glass configuration (pricing matrix)"""
        try:
            response = self.client.table("glass_config").select("*").is_("deleted_at", "null").execute()
            print(f"DEBUG: Fetched {len(response.data)} glass configs")
            return response.data
        except Exception as e:
            print(f"ERROR fetching glass config: {e}")
            print(f"ERROR type: {type(e)}")
            import traceback
            traceback.print_exc()
            return []

    def get_markups(self) -> Dict:
        """Get markup percentages as a dict"""
        try:
            response = self.client.table("markups").select("*").is_("deleted_at", "null").execute()
            return {row['name']: float(row['percentage']) for row in response.data}
        except Exception as e:
            print(f"Error fetching markups: {e}")
            return {}

    def get_beveled_pricing(self) -> Dict:
        """Get beveled pricing as a dict (thickness -> price)"""
        try:
            response = self.client.table("beveled_pricing").select("*").is_("deleted_at", "null").execute()
            return {row['glass_thickness']: float(row['price_per_inch']) for row in response.data}
        except Exception as e:
            print(f"Error fetching beveled pricing: {e}")
            return {}

    def get_clipped_corners_pricing(self) -> Dict:
        """Get clipped corners pricing as a dict"""
        try:
            response = self.client.table("clipped_corners_pricing").select("*").is_("deleted_at", "null").execute()
            result = {}
            for row in response.data:
                key = f"{row['glass_thickness']}_{row['clip_size']}"
                result[key] = float(row['price_per_corner'])
            return result
        except Exception as e:
            print(f"Error fetching clipped corners pricing: {e}")
            return {}

    def get_calculator_config(self) -> Dict:
        """Get complete calculator configuration for pricing"""
        try:
            # Get all config data
            glass_config_rows = self.get_glass_config()
            markups = self.get_markups()
            beveled = self.get_beveled_pricing()
            clipped = self.get_clipped_corners_pricing()

            # Transform glass_config to dict
            glass_config = {}
            for row in glass_config_rows:
                key = f"{row['thickness']}_{row['type']}"
                glass_config[key] = {
                    'base_price': float(row['base_price']),
                    'polish_price': float(row['polish_price']),
                    'only_tempered': row.get('only_tempered', False),
                    'no_polish': row.get('no_polish', False),
                    'never_tempered': row.get('never_tempered', False)
                }

            return {
                'glass_config': glass_config,
                'markups': markups,
                'beveled_pricing': beveled,
                'clipped_corners_pricing': clipped
            }
        except Exception as e:
            print(f"Error fetching calculator config: {e}")
            return {
                'glass_config': {},
                'markups': {},
                'beveled_pricing': {},
                'clipped_corners_pricing': {}
            }

    # ========== PO Tracker Methods ==========

    def get_all_po_clients(self) -> List[Dict]:
        """Get all PO clients (excludes soft-deleted)"""
        try:
            response = self.client.table("po_clients").select("*").is_("deleted_at", "null").order("client_name").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching PO clients: {e}")
            return []

    def get_po_client_by_id(self, client_id: int) -> Optional[Dict]:
        """Get a single PO client by ID"""
        try:
            response = self.client.table("po_clients").select("*").eq("id", client_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching PO client {client_id}: {e}")
            return None

    def search_po_clients(
        self,
        search_term: str = None,
        city: str = None,
        client_type: str = None,
        tags: List[str] = None
    ) -> List[Dict]:
        """Search PO clients with filters"""
        try:
            query = self.client.table("po_clients").select("*").is_("deleted_at", "null")

            if search_term:
                query = query.ilike("client_name", f"%{search_term}%")

            if city:
                query = query.eq("city", city)

            if client_type:
                query = query.eq("client_type", client_type)

            if tags and len(tags) > 0:
                # PostgreSQL array contains
                query = query.contains("tags", tags)

            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error searching PO clients: {e}")
            return []

    def insert_po_client(self, client_data: Dict, user_id: str) -> Optional[Dict]:
        """Insert a new PO client with company scoping and audit trail

        Args:
            client_data: Client information dictionary
            user_id: UUID of the user creating the client

        Returns:
            Created client record or None on error
        """
        try:
            # Get user's company_id
            company_id = self.get_user_company_id(user_id)
            if not company_id:
                print(f"Error: Could not find company_id for user {user_id}")
                return None

            # Add company scoping and audit trail
            client_data['company_id'] = company_id
            client_data['created_by'] = user_id

            response = self.client.table("po_clients").insert(client_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error inserting PO client: {e}")
            return None

    def update_po_client(self, client_id: int, updates: Dict, user_id: str) -> bool:
        """Update PO client information with audit trail

        Args:
            client_id: ID of the client to update
            updates: Dictionary of fields to update
            user_id: UUID of the user making the update

        Returns:
            True if successful, False otherwise
        """
        try:
            # Add audit trail
            updates['updated_by'] = user_id
            updates['updated_at'] = 'NOW()'
            self.client.table("po_clients").update(updates).eq("id", client_id).execute()
            return True
        except Exception as e:
            print(f"Error updating PO client {client_id}: {e}")
            return False

    def delete_po_client(self, client_id: int, user_id: str) -> bool:
        """Soft delete a PO client (marks as deleted, doesn't remove)

        Args:
            client_id: ID of the client to delete
            user_id: UUID of the user deleting the client

        Returns:
            True if successful, False otherwise
        """
        try:
            # Soft delete: set deleted_by and deleted_at
            updates = {
                'deleted_by': user_id,
                'deleted_at': 'NOW()'
            }
            self.client.table("po_clients").update(updates).eq("id", client_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting PO client {client_id}: {e}")
            return False

    def get_po_client_with_po_count(self) -> List[Dict]:
        """Get all clients with their PO count and primary contact"""
        try:
            clients = self.get_all_po_clients()

            for client in clients:
                # Get PO count
                po_count = self.client.table("po_purchase_orders")\
                    .select("*", count="exact")\
                    .eq("client_id", client['id'])\
                    .execute()
                client['po_count'] = po_count.count if hasattr(po_count, 'count') else len(po_count.data)

                # Get primary contact
                client['primary_contact'] = self.get_primary_contact(client['id'])

            return clients
        except Exception as e:
            print(f"Error getting clients with PO count: {e}")
            return []

    def get_purchase_orders_by_client(self, client_id: int) -> List[Dict]:
        """Get all purchase orders for a client"""
        try:
            response = self.client.table("po_purchase_orders")\
                .select("*")\
                .eq("client_id", client_id)\
                .order("created_at", desc=True)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching POs for client {client_id}: {e}")
            return []

    def insert_purchase_order(self, po_data: Dict) -> Optional[Dict]:
        """Insert a new purchase order"""
        try:
            response = self.client.table("po_purchase_orders").insert(po_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error inserting purchase order: {e}")
            return None

    def get_po_activities(self, client_id: int = None, po_id: int = None) -> List[Dict]:
        """Get activity log for client or PO"""
        try:
            query = self.client.table("po_activities").select("*")

            if client_id:
                query = query.eq("client_id", client_id)

            if po_id:
                query = query.eq("po_id", po_id)

            response = query.order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching PO activities: {e}")
            return []

    def log_po_activity(self, activity_data: Dict) -> bool:
        """Log a PO activity"""
        try:
            self.client.table("po_activities").insert(activity_data).execute()
            return True
        except Exception as e:
            print(f"Error logging PO activity: {e}")
            return False

    # ========== Client Contacts Methods ==========

    def get_client_contacts(self, client_id: int) -> List[Dict]:
        """Get all contacts for a client (excludes soft-deleted)"""
        try:
            response = self.client.table("po_client_contacts")\
                .select("*")\
                .eq("client_id", client_id)\
                .is_("deleted_at", "null")\
                .order("is_primary", desc=True)\
                .order("first_name")\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching contacts for client {client_id}: {e}")
            return []

    def get_primary_contact(self, client_id: int) -> Optional[Dict]:
        """Get the primary contact for a client"""
        try:
            response = self.client.table("po_client_contacts")\
                .select("*")\
                .eq("client_id", client_id)\
                .eq("is_primary", True)\
                .is_("deleted_at", "null")\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching primary contact for client {client_id}: {e}")
            return None

    def insert_client_contact(self, contact_data: Dict, user_id: str) -> Optional[Dict]:
        """Insert a new client contact with company scoping and audit trail

        Args:
            contact_data: Contact information dictionary
            user_id: UUID of the user creating the contact

        Returns:
            Created contact record or None on error
        """
        try:
            # Get user's company_id
            company_id = self.get_user_company_id(user_id)
            if not company_id:
                print(f"Error: Could not find company_id for user {user_id}")
                return None

            # Add company scoping and audit trail
            contact_data['company_id'] = company_id
            contact_data['created_by'] = user_id

            response = self.client.table("po_client_contacts").insert(contact_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error inserting client contact: {e}")
            return None

    def update_client_contact(self, contact_id: int, updates: Dict, user_id: str) -> bool:
        """Update client contact information with audit trail

        Args:
            contact_id: ID of the contact to update
            updates: Dictionary of fields to update
            user_id: UUID of the user making the update

        Returns:
            True if successful, False otherwise
        """
        try:
            # Add audit trail
            updates['updated_by'] = user_id
            updates['updated_at'] = 'NOW()'
            self.client.table("po_client_contacts").update(updates).eq("id", contact_id).execute()
            return True
        except Exception as e:
            print(f"Error updating client contact {contact_id}: {e}")
            return False

    def delete_client_contact(self, contact_id: int, user_id: str) -> bool:
        """Soft delete a client contact

        Args:
            contact_id: ID of the contact to delete
            user_id: UUID of the user deleting the contact

        Returns:
            True if successful, False otherwise
        """
        try:
            # Soft delete: set deleted_by and deleted_at
            updates = {
                'deleted_by': user_id,
                'deleted_at': 'NOW()'
            }
            self.client.table("po_client_contacts").update(updates).eq("id", contact_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting client contact {contact_id}: {e}")
            return False

    def set_primary_contact(self, client_id: int, contact_id: int, user_id: str) -> bool:
        """Set a contact as the primary contact for a client

        This unsets any existing primary contact and sets the new one.

        Args:
            client_id: ID of the client
            contact_id: ID of the contact to set as primary
            user_id: UUID of the user making the change

        Returns:
            True if successful, False otherwise
        """
        try:
            # First, unset all primary contacts for this client
            self.client.table("po_client_contacts")\
                .update({
                    'is_primary': False,
                    'updated_by': user_id,
                    'updated_at': 'NOW()'
                })\
                .eq("client_id", client_id)\
                .execute()

            # Then set the new primary contact
            self.client.table("po_client_contacts")\
                .update({
                    'is_primary': True,
                    'updated_by': user_id,
                    'updated_at': 'NOW()'
                })\
                .eq("id", contact_id)\
                .execute()

            return True
        except Exception as e:
            print(f"Error setting primary contact: {e}")
            return False

    # ========== Inventory Methods ==========

    def get_all_inventory_items(self) -> List[Dict]:
        """Get all inventory items with category and unit names"""
        try:
            response = self.client.table("inventory_items")\
                .select("*, inventory_categories(name), inventory_units(name), suppliers(name)")\
                .order("sort_order")\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching inventory items: {e}")
            return []

    def get_inventory_categories(self) -> List[Dict]:
        """Get all inventory categories"""
        try:
            response = self.client.table("inventory_categories").select("*").order("name").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching inventory categories: {e}")
            return []

    def get_inventory_units(self) -> List[Dict]:
        """Get all inventory units"""
        try:
            response = self.client.table("inventory_units").select("*").order("name").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching inventory units: {e}")
            return []

    def get_suppliers(self) -> List[Dict]:
        """Get all suppliers"""
        try:
            response = self.client.table("suppliers").select("*").order("name").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching suppliers: {e}")
            return []

    def insert_inventory_item(self, item_data: Dict, user_id: str) -> Optional[Dict]:
        """Insert a new inventory item with company scoping and audit trail"""
        try:
            # Get user's company_id
            company_id = self.get_user_company_id(user_id)
            if not company_id:
                print(f"Error: Could not find company_id for user {user_id}")
                return None

            # Add company scoping and audit trail
            item_data['company_id'] = company_id
            item_data['created_by'] = user_id

            response = self.client.table("inventory_items").insert(item_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error inserting inventory item: {e}")
            return None

    def update_inventory_item(self, item_id: int, updates: Dict, user_id: str) -> bool:
        """Update inventory item with audit trail"""
        try:
            # Add audit trail
            updates['updated_by'] = user_id
            updates['updated_at'] = 'NOW()'

            self.client.table("inventory_items").update(updates).eq("id", item_id).execute()
            return True
        except Exception as e:
            print(f"Error updating inventory item {item_id}: {e}")
            return False

    def delete_inventory_item(self, item_id: int, user_id: str) -> bool:
        """Soft delete an inventory item"""
        try:
            # Soft delete: set deleted_by and deleted_at
            updates = {
                'deleted_by': user_id,
                'deleted_at': 'NOW()'
            }
            self.client.table("inventory_items").update(updates).eq("id", item_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting inventory item {item_id}: {e}")
            return False

    def get_low_stock_items(self) -> List[Dict]:
        """Get items with quantity below threshold"""
        try:
            # This requires a custom query since we need quantity < low_stock_threshold
            all_items = self.get_all_inventory_items()
            return [
                item for item in all_items
                if float(item.get('quantity', 0)) < float(item.get('low_stock_threshold', 0))
            ]
        except Exception as e:
            print(f"Error fetching low stock items: {e}")
            return []

    def insert_inventory_category(self, category_data: Dict, user_id: str) -> Optional[Dict]:
        """Insert a new inventory category with company scoping"""
        try:
            company_id = self.get_user_company_id(user_id)
            if not company_id:
                return None

            category_data['company_id'] = company_id
            category_data['created_by'] = user_id

            response = self.client.table("inventory_categories").insert(category_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error inserting inventory category: {e}")
            return None

    def insert_inventory_unit(self, unit_data: Dict, user_id: str) -> Optional[Dict]:
        """Insert a new inventory unit with company scoping"""
        try:
            company_id = self.get_user_company_id(user_id)
            if not company_id:
                return None

            unit_data['company_id'] = company_id
            unit_data['created_by'] = user_id

            response = self.client.table("inventory_units").insert(unit_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error inserting inventory unit: {e}")
            return None

    def insert_supplier(self, supplier_data: Dict, user_id: str) -> Optional[Dict]:
        """Insert a new supplier with company scoping"""
        try:
            company_id = self.get_user_company_id(user_id)
            if not company_id:
                return None

            supplier_data['company_id'] = company_id
            supplier_data['created_by'] = user_id

            response = self.client.table("suppliers").insert(supplier_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error inserting supplier: {e}")
            return None

    # ========== Window Manufacturing Methods ==========

    def create_window_order(self, order_data: Dict, user_id: str, company_id: str) -> Optional[Dict]:
        """Create a new window order

        Args:
            order_data: Dict with po_number, customer_name, customer_id (optional), notes
            user_id: UUID of user creating the order
            company_id: UUID of company

        Returns:
            Created order dict or None if failed
        """
        try:
            order_data['company_id'] = company_id
            order_data['created_by'] = user_id
            order_data['status'] = order_data.get('status', 'pending')

            response = self.client.table("window_orders").insert(order_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating window order: {e}")
            return None

    def get_window_orders(self, company_id: str, status: Optional[str] = None) -> List[Dict]:
        """Get all window orders for a company

        Args:
            company_id: UUID of company
            status: Optional status filter

        Returns:
            List of window order dicts
        """
        try:
            query = self.client.table("window_orders")\
                .select("*")\
                .eq("company_id", company_id)\
                .is_("deleted_at", "null")\
                .order("order_date", desc=True)

            if status:
                query = query.eq("status", status)

            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error fetching window orders: {e}")
            return []

    def get_window_order_by_id(self, order_id: int) -> Optional[Dict]:
        """Get a single window order by ID

        Args:
            order_id: Order ID

        Returns:
            Order dict or None
        """
        try:
            response = self.client.table("window_orders")\
                .select("*")\
                .eq("id", order_id)\
                .is_("deleted_at", "null")\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching window order {order_id}: {e}")
            return None

    def update_window_order_status(self, order_id: int, status: str, user_id: str) -> bool:
        """Update window order status

        Args:
            order_id: Order ID
            status: New status (pending, in_production, printed, completed)
            user_id: UUID of user making the update

        Returns:
            True if successful
        """
        try:
            self.client.table("window_orders")\
                .update({
                    'status': status,
                    'updated_by': user_id,
                    'updated_at': 'NOW()'
                })\
                .eq("id", order_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error updating window order status: {e}")
            return False

    def add_window_order_item(self, item_data: Dict, user_id: str, company_id: str) -> Optional[Dict]:
        """Add a window item to an order

        Args:
            item_data: Dict with order_id, window_type, thickness, width, height, quantity, shape_notes
            user_id: UUID of user adding the item
            company_id: UUID of company

        Returns:
            Created item dict or None if failed
        """
        try:
            item_data['company_id'] = company_id
            item_data['created_by'] = user_id

            response = self.client.table("window_order_items").insert(item_data).execute()

            if response.data:
                # Generate labels for this item
                item_id = response.data[0]['id']
                quantity = item_data.get('quantity', 1)
                self.generate_labels_for_item(item_id, quantity, user_id, company_id)

            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error adding window order item: {e}")
            return None

    def get_window_order_items(self, order_id: int) -> List[Dict]:
        """Get all items for a window order

        Args:
            order_id: Order ID

        Returns:
            List of window order item dicts
        """
        try:
            response = self.client.table("window_order_items")\
                .select("*")\
                .eq("order_id", order_id)\
                .is_("deleted_at", "null")\
                .order("created_at")\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching window order items: {e}")
            return []

    def generate_labels_for_item(self, item_id: int, quantity: int, user_id: str, company_id: str) -> int:
        """Generate labels for a window order item

        Args:
            item_id: Window order item ID
            quantity: Number of labels to generate
            user_id: UUID of user generating labels
            company_id: UUID of company

        Returns:
            Number of labels created
        """
        try:
            labels = []
            for i in range(1, quantity + 1):
                labels.append({
                    'order_item_id': item_id,
                    'label_number': i,
                    'company_id': company_id,
                    'created_by': user_id,
                    'print_status': 'pending'
                })

            response = self.client.table("window_labels").insert(labels).execute()
            return len(response.data) if response.data else 0
        except Exception as e:
            print(f"Error generating labels: {e}")
            return 0

    def get_labels_for_order(self, order_id: int) -> List[Dict]:
        """Get all labels for a window order (with item details)

        Args:
            order_id: Order ID

        Returns:
            List of label dicts with window item data
        """
        try:
            # Get all items for this order
            items = self.get_window_order_items(order_id)

            all_labels = []
            for item in items:
                # Get labels for this item
                response = self.client.table("window_labels")\
                    .select("*")\
                    .eq("order_item_id", item['id'])\
                    .order("label_number")\
                    .execute()

                # Attach item data to each label
                for label in response.data:
                    label['window_item'] = item
                    all_labels.append(label)

            return all_labels
        except Exception as e:
            print(f"Error fetching labels for order: {e}")
            return []

    def get_pending_labels(self, company_id: str) -> List[Dict]:
        """Get all pending labels for a company

        Args:
            company_id: UUID of company

        Returns:
            List of pending label dicts with item and order details
        """
        try:
            response = self.client.table("window_labels")\
                .select("*, window_order_items(*)")\
                .eq("company_id", company_id)\
                .eq("print_status", "pending")\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching pending labels: {e}")
            return []

    def update_label_print_status(self, label_id: int, status: str, user_id: str, zpl_code: Optional[str] = None) -> bool:
        """Update label print status

        Args:
            label_id: Label ID
            status: New status (printed, reprinted)
            user_id: UUID of user printing the label
            zpl_code: Optional ZPL code to store

        Returns:
            True if successful
        """
        try:
            update_data = {
                'print_status': status,
                'printed_by': user_id,
                'printed_at': 'NOW()'
            }

            if zpl_code:
                update_data['zpl_code'] = zpl_code

            self.client.table("window_labels")\
                .update(update_data)\
                .eq("id", label_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error updating label print status: {e}")
            return False

    def get_label_by_id(self, label_id: int) -> Optional[Dict]:
        """Get a single label with item and order details

        Args:
            label_id: Label ID

        Returns:
            Label dict with related data or None
        """
        try:
            response = self.client.table("window_labels")\
                .select("*, window_order_items(*, window_orders(*))")\
                .eq("id", label_id)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching label {label_id}: {e}")
            return None

    def get_printer_config(self, company_id: str) -> Optional[Dict]:
        """Get default printer config for a company

        Args:
            company_id: UUID of company

        Returns:
            Printer config dict or None
        """
        try:
            response = self.client.table("label_printer_config")\
                .select("*")\
                .eq("company_id", company_id)\
                .eq("is_default", True)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching printer config: {e}")
            return None

    def search_po_numbers(self, search_term: str, company_id: str, limit: int = 10) -> List[str]:
        """Search for PO numbers (for autocomplete)

        Args:
            search_term: Search term
            company_id: UUID of company
            limit: Max results

        Returns:
            List of matching PO numbers
        """
        try:
            response = self.client.table("window_orders")\
                .select("po_number")\
                .eq("company_id", company_id)\
                .ilike("po_number", f"%{search_term}%")\
                .is_("deleted_at", "null")\
                .limit(limit)\
                .execute()

            return [row['po_number'] for row in response.data]
        except Exception as e:
            print(f"Error searching PO numbers: {e}")
            return []


# ========== Helper Functions ==========

def get_authenticated_db(session_data: dict) -> 'Database':
    """Get a Database instance authenticated with user's access token

    Args:
        session_data: Session data dict containing 'session' with 'access_token'

    Returns:
        Database instance with RLS-enabled authentication
    """
    if session_data and session_data.get('session'):
        access_token = session_data['session'].get('access_token')
        if access_token:
            print(f"DEBUG: Creating authenticated DB with token (length: {len(access_token)})")
            return Database(access_token=access_token)
        else:
            print("WARNING: session exists but no access_token found")
    else:
        print("WARNING: No session_data or session not in session_data")

    # Fallback to unauthenticated client (will fail with RLS)
    print("ERROR: Falling back to unauthenticated Database - RLS will block queries!")
    return Database()
