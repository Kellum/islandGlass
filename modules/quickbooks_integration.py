"""
QuickBooks Integration Module
Island Glass CRM - Purchase Order System
Handles OAuth, API calls, and data synchronization with QuickBooks Online
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from requests.auth import HTTPBasicAuth


class QuickBooksIntegration:
    """
    Manages QuickBooks Online API integration
    Handles authentication, vendor sync, PO creation, and payment tracking
    """

    # QuickBooks API endpoints
    BASE_URL = "https://quickbooks.api.intuit.com/v3/company"
    AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
    TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

    def __init__(self, db_connection):
        """
        Initialize QuickBooks integration

        Args:
            db_connection: DatabaseConnection instance
        """
        self.db = db_connection

        # Load credentials from environment or database
        self.client_id = os.getenv('QB_CLIENT_ID', '')
        self.client_secret = os.getenv('QB_CLIENT_SECRET', '')
        self.redirect_uri = os.getenv('QB_REDIRECT_URI', 'http://localhost:8050/qb-callback')
        self.realm_id = None  # Company ID - loaded from settings
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None

        # Load existing credentials from database
        self._load_credentials()

    # =====================================================
    # CONFIGURATION & CREDENTIALS
    # =====================================================

    def _load_credentials(self):
        """Load QuickBooks credentials from database"""
        try:
            settings = self.db.fetch_one("""
                SELECT setting_value FROM system_settings
                WHERE setting_key = 'quickbooks_config'
            """)

            if settings:
                config = json.loads(settings['setting_value'])
                self.realm_id = config.get('realm_id')
                self.access_token = config.get('access_token')
                self.refresh_token = config.get('refresh_token')

                # Parse token expiration
                expires_str = config.get('token_expires_at')
                if expires_str:
                    self.token_expires_at = datetime.fromisoformat(expires_str)

        except Exception as e:
            print(f"Error loading QB credentials: {e}")

    def save_credentials(self, realm_id: str, access_token: str, refresh_token: str, expires_in: int):
        """
        Save QuickBooks credentials to database

        Args:
            realm_id: QuickBooks company ID
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            expires_in: Token lifetime in seconds
        """
        self.realm_id = realm_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

        config = {
            'realm_id': realm_id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_expires_at': self.token_expires_at.isoformat(),
            'last_updated': datetime.now().isoformat()
        }

        try:
            # Store in database
            self.db.execute_query("""
                INSERT INTO system_settings (setting_key, setting_value, updated_at)
                VALUES ('quickbooks_config', %s, CURRENT_TIMESTAMP)
                ON CONFLICT (setting_key)
                DO UPDATE SET setting_value = EXCLUDED.setting_value, updated_at = CURRENT_TIMESTAMP
            """, (json.dumps(config),))

        except Exception as e:
            print(f"Error saving QB credentials: {e}")
            raise

    def is_connected(self) -> bool:
        """Check if QuickBooks is connected and authenticated"""
        return (
            self.realm_id is not None and
            self.access_token is not None and
            self.refresh_token is not None and
            self.token_expires_at is not None and
            self.token_expires_at > datetime.now()
        )

    def get_authorization_url(self) -> str:
        """
        Get QuickBooks OAuth authorization URL

        Returns:
            Authorization URL for user to visit
        """
        scope = "com.intuit.quickbooks.accounting"
        state = "island_glass_crm"  # CSRF protection

        auth_url = (
            f"{self.AUTH_URL}?"
            f"client_id={self.client_id}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"redirect_uri={self.redirect_uri}&"
            f"state={state}"
        )

        return auth_url

    def exchange_code_for_tokens(self, authorization_code: str, realm_id: str) -> bool:
        """
        Exchange authorization code for access and refresh tokens

        Args:
            authorization_code: Code received from OAuth callback
            realm_id: QuickBooks company ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare token request
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': self.redirect_uri
            }

            # Request tokens
            response = requests.post(self.TOKEN_URL, auth=auth, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()

            # Save credentials
            self.save_credentials(
                realm_id=realm_id,
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                expires_in=token_data['expires_in']
            )

            return True

        except Exception as e:
            print(f"Error exchanging authorization code: {e}")
            return False

    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using refresh token

        Returns:
            True if successful, False otherwise
        """
        if not self.refresh_token:
            return False

        try:
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }

            response = requests.post(self.TOKEN_URL, auth=auth, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()

            # Update credentials
            self.save_credentials(
                realm_id=self.realm_id,
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                expires_in=token_data['expires_in']
            )

            return True

        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False

    def _ensure_valid_token(self):
        """Ensure access token is valid, refresh if necessary"""
        if not self.token_expires_at or datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            if not self.refresh_access_token():
                raise Exception("Failed to refresh QuickBooks access token")

    # =====================================================
    # API REQUEST HELPERS
    # =====================================================

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """
        Make authenticated request to QuickBooks API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., 'vendor')
            data: Request payload

        Returns:
            Response data as dictionary

        Raises:
            Exception on API errors
        """
        self._ensure_valid_token()

        url = f"{self.BASE_URL}/{self.realm_id}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()

        return response.json()

    def _log_sync(self, entity_type: str, entity_id: int, action: str,
                   status: str, qb_id: str = None, error: str = None):
        """
        Log synchronization activity

        Args:
            entity_type: Type of entity (Vendor, PO, Payment, etc.)
            entity_id: Local entity ID
            action: Sync action (Create, Update, Fetch)
            status: Sync status (Success, Failed)
            qb_id: QuickBooks entity ID
            error: Error message if failed
        """
        try:
            self.db.execute_query("""
                INSERT INTO quickbooks_sync_log (
                    entity_type, entity_id, sync_action, sync_status,
                    quickbooks_id, error_message, sync_timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (entity_type, entity_id, action, status, qb_id, error))
        except Exception as e:
            print(f"Error logging sync: {e}")

    # =====================================================
    # VENDOR SYNCHRONIZATION
    # =====================================================

    def sync_vendor_to_qb(self, vendor_id: int) -> Tuple[bool, Optional[str]]:
        """
        Sync vendor from CRM to QuickBooks

        Args:
            vendor_id: Local vendor ID

        Returns:
            Tuple of (success, quickbooks_vendor_id)
        """
        try:
            # Fetch vendor from database
            vendor = self.db.fetch_one("""
                SELECT * FROM vendors WHERE vendor_id = %s
            """, (vendor_id,))

            if not vendor:
                raise Exception(f"Vendor {vendor_id} not found")

            # Check if vendor already exists in QB
            qb_vendor_id = vendor.get('quickbooks_vendor_id')

            # Prepare vendor data for QuickBooks
            vendor_data = {
                "DisplayName": vendor['vendor_name'],
                "CompanyName": vendor['vendor_name'],
                "PrintOnCheckName": vendor['vendor_name'],
                "PrimaryEmailAddr": {"Address": vendor['email']} if vendor.get('email') else None,
                "PrimaryPhone": {"FreeFormNumber": vendor['phone']} if vendor.get('phone') else None,
                "BillAddr": {
                    "Line1": vendor.get('address_line1', ''),
                    "Line2": vendor.get('address_line2', ''),
                    "City": vendor.get('city', ''),
                    "Country": vendor.get('country', 'USA'),
                    "CountrySubDivisionCode": vendor.get('state', ''),
                    "PostalCode": vendor.get('zip_code', '')
                } if vendor.get('address_line1') else None,
                "AcctNum": vendor.get('account_number'),
                "TaxIdentifier": vendor.get('tax_id'),
                "Active": vendor['is_active']
            }

            # Remove None values
            vendor_data = {k: v for k, v in vendor_data.items() if v is not None}

            if qb_vendor_id:
                # Update existing vendor
                # Note: Need to fetch current SyncToken first
                existing = self._make_request('GET', f'vendor/{qb_vendor_id}')
                vendor_data['Id'] = qb_vendor_id
                vendor_data['SyncToken'] = existing['Vendor']['SyncToken']

                response = self._make_request('POST', 'vendor', vendor_data)
            else:
                # Create new vendor
                response = self._make_request('POST', 'vendor', vendor_data)

            qb_vendor_id = response['Vendor']['Id']

            # Update local database
            self.db.execute_query("""
                UPDATE vendors
                SET quickbooks_vendor_id = %s,
                    quickbooks_display_name = %s,
                    quickbooks_last_sync = CURRENT_TIMESTAMP
                WHERE vendor_id = %s
            """, (qb_vendor_id, response['Vendor']['DisplayName'], vendor_id))

            # Log success
            self._log_sync('Vendor', vendor_id, 'Create' if not vendor.get('quickbooks_vendor_id') else 'Update',
                          'Success', qb_vendor_id)

            return True, qb_vendor_id

        except Exception as e:
            error_msg = str(e)
            self._log_sync('Vendor', vendor_id, 'Create', 'Failed', error=error_msg)
            print(f"Error syncing vendor to QB: {error_msg}")
            return False, None

    def fetch_vendors_from_qb(self) -> List[dict]:
        """
        Fetch all vendors from QuickBooks

        Returns:
            List of vendor dictionaries
        """
        try:
            response = self._make_request('GET', 'query?query=SELECT * FROM Vendor')
            return response.get('QueryResponse', {}).get('Vendor', [])
        except Exception as e:
            print(f"Error fetching vendors from QB: {e}")
            return []

    # =====================================================
    # PURCHASE ORDER SYNCHRONIZATION
    # =====================================================

    def sync_po_to_qb(self, po_id: int) -> Tuple[bool, Optional[str]]:
        """
        Sync purchase order from CRM to QuickBooks

        Args:
            po_id: Local PO ID

        Returns:
            Tuple of (success, quickbooks_po_id)
        """
        try:
            # Fetch PO and items from database
            po = self.db.fetch_one("""
                SELECT po.*, v.quickbooks_vendor_id
                FROM purchase_orders po
                JOIN vendors v ON po.vendor_id = v.vendor_id
                WHERE po.po_id = %s
            """, (po_id,))

            if not po:
                raise Exception(f"PO {po_id} not found")

            if not po['quickbooks_vendor_id']:
                raise Exception("Vendor must be synced to QuickBooks first")

            # Fetch PO items
            items = self.db.fetch_all("""
                SELECT * FROM po_items WHERE po_id = %s ORDER BY line_number
            """, (po_id,))

            # Prepare PO data for QuickBooks
            line_items = []
            for item in items:
                line_items.append({
                    "DetailType": "ItemBasedExpenseLineDetail",
                    "Amount": float(item['line_total']),
                    "ItemBasedExpenseLineDetail": {
                        "Qty": float(item['quantity']),
                        "UnitPrice": float(item['unit_price']),
                        # Note: Would need to map items to QB items
                    },
                    "Description": item['description']
                })

            po_data = {
                "VendorRef": {"value": po['quickbooks_vendor_id']},
                "Line": line_items,
                "TxnDate": po['po_date'].isoformat() if po['po_date'] else None,
                "ShipAddr": {"Line1": po['ship_to_address']} if po.get('ship_to_address') else None,
                "Memo": po.get('notes', ''),
                "TotalAmt": float(po['total_amount'])
            }

            # Remove None values
            po_data = {k: v for k, v in po_data.items() if v is not None}

            qb_po_id = po.get('quickbooks_po_id')

            if qb_po_id:
                # Update existing PO
                existing = self._make_request('GET', f'purchaseorder/{qb_po_id}')
                po_data['Id'] = qb_po_id
                po_data['SyncToken'] = existing['PurchaseOrder']['SyncToken']

                response = self._make_request('POST', 'purchaseorder', po_data)
            else:
                # Create new PO
                response = self._make_request('POST', 'purchaseorder', po_data)

            qb_po_id = response['PurchaseOrder']['Id']
            qb_txn_id = response['PurchaseOrder'].get('DocNumber')

            # Update local database
            self.db.execute_query("""
                UPDATE purchase_orders
                SET quickbooks_po_id = %s,
                    quickbooks_txn_id = %s,
                    quickbooks_last_sync = CURRENT_TIMESTAMP
                WHERE po_id = %s
            """, (qb_po_id, qb_txn_id, po_id))

            # Log success
            self._log_sync('PO', po_id, 'Create' if not po.get('quickbooks_po_id') else 'Update',
                          'Success', qb_po_id)

            return True, qb_po_id

        except Exception as e:
            error_msg = str(e)
            self._log_sync('PO', po_id, 'Create', 'Failed', error=error_msg)
            print(f"Error syncing PO to QB: {error_msg}")
            return False, None

    # =====================================================
    # UTILITY METHODS
    # =====================================================

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test QuickBooks connection

        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.is_connected():
                return False, "Not connected to QuickBooks"

            # Try to fetch company info
            response = self._make_request('GET', 'companyinfo/' + self.realm_id)
            company_name = response['CompanyInfo']['CompanyName']

            return True, f"Connected to: {company_name}"

        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def disconnect(self):
        """Disconnect from QuickBooks and clear credentials"""
        try:
            self.db.execute_query("""
                DELETE FROM system_settings WHERE setting_key = 'quickbooks_config'
            """)

            self.realm_id = None
            self.access_token = None
            self.refresh_token = None
            self.token_expires_at = None

        except Exception as e:
            print(f"Error disconnecting from QB: {e}")
            raise
