"""
Authentication module for Supabase Auth integration
Handles login, logout, session management, and user operations
"""
import os
from supabase import create_client, Client
from typing import Optional, Dict, List
from dotenv import load_dotenv
from datetime import datetime
import secrets

# Load environment variables
load_dotenv()


class AuthManager:
    """Handle all authentication and user management operations"""

    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "Missing Supabase credentials. "
                "Please set SUPABASE_URL and SUPABASE_KEY in .env file"
            )

        # Regular client for auth operations
        self.client: Client = create_client(self.url, self.key)

        # Admin client for user management (bypasses RLS if service role key available)
        if self.service_role_key:
            self.admin_client: Client = create_client(self.url, self.service_role_key)
        else:
            # Fallback to regular client (will respect RLS)
            self.admin_client = self.client

    def login(self, email: str, password: str) -> Dict:
        """
        Authenticate user with email and password

        Args:
            email: User email
            password: User password

        Returns:
            dict: {
                'success': bool,
                'user': dict or None,
                'session': dict or None,
                'error': str or None
            }
        """
        try:
            # Authenticate with Supabase Auth
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                # Get user profile from users table
                user_profile = self.admin_client.table("users").select("*").eq(
                    "id", response.user.id
                ).execute()

                if not user_profile.data:
                    return {
                        'success': False,
                        'user': None,
                        'session': None,
                        'error': 'User profile not found. Please contact administrator.'
                    }

                profile = user_profile.data[0]

                # Check if user is active
                if not profile.get('is_active', False):
                    return {
                        'success': False,
                        'user': None,
                        'session': None,
                        'error': 'Your account has been deactivated. Please contact administrator.'
                    }

                # Update last login timestamp
                self.admin_client.table("users").update({
                    "last_login": datetime.now().isoformat()
                }).eq("id", response.user.id).execute()

                return {
                    'success': True,
                    'user': {
                        'id': profile['id'],
                        'email': profile['email'],
                        'full_name': profile.get('full_name'),
                        'role': profile['role']
                    },
                    'session': {
                        'access_token': response.session.access_token,
                        'refresh_token': response.session.refresh_token,
                        'expires_at': response.session.expires_at
                    },
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'user': None,
                    'session': None,
                    'error': 'Authentication failed. Please check your credentials.'
                }

        except Exception as e:
            error_msg = str(e)
            if 'Invalid login credentials' in error_msg:
                error_msg = 'Invalid email or password'
            return {
                'success': False,
                'user': None,
                'session': None,
                'error': error_msg
            }

    def logout(self) -> bool:
        """
        Sign out current user

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.auth.sign_out()
            return True
        except Exception as e:
            print(f"Error during logout: {e}")
            return False

    def refresh_session(self, refresh_token: str) -> Dict:
        """
        Refresh an expired session using refresh_token

        Args:
            refresh_token: The refresh token from the current session

        Returns:
            dict: {
                'success': bool,
                'session': dict or None (with new access_token, refresh_token, expires_at),
                'error': str or None
            }
        """
        try:
            print(f"DEBUG: Attempting to refresh session...")
            response = self.client.auth.refresh_session(refresh_token)

            if response and response.session:
                print(f"DEBUG: Session refreshed successfully")
                return {
                    'success': True,
                    'session': {
                        'access_token': response.session.access_token,
                        'refresh_token': response.session.refresh_token,
                        'expires_at': response.session.expires_at
                    },
                    'error': None
                }
            else:
                print("WARNING: Refresh response had no session")
                return {
                    'success': False,
                    'session': None,
                    'error': 'No session in refresh response'
                }
        except Exception as e:
            print(f"ERROR: Token refresh failed: {e}")
            return {
                'success': False,
                'session': None,
                'error': str(e)
            }

    def get_session(self) -> Optional[Dict]:
        """
        Get current session

        Returns:
            dict or None: Session data if active, None otherwise
        """
        try:
            session = self.client.auth.get_session()
            if session:
                return {
                    'access_token': session.access_token,
                    'refresh_token': session.refresh_token,
                    'expires_at': session.expires_at,
                    'user': session.user
                }
            return None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None

    def get_current_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user profile by ID

        Args:
            user_id: User UUID

        Returns:
            dict or None: User profile if found
        """
        try:
            response = self.admin_client.table("users").select("*").eq("id", user_id).execute()
            if response.data:
                user = response.data[0]
                return {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user.get('full_name'),
                    'role': user['role'],
                    'is_active': user.get('is_active', True),
                    'created_at': user.get('created_at'),
                    'last_login': user.get('last_login')
                }
            return None
        except Exception as e:
            print(f"Error getting current user: {e}")
            return None

    def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str,
        created_by_id: str
    ) -> Dict:
        """
        Create a new user (owner only)

        Args:
            email: User email
            password: User password
            full_name: User full name
            role: User role (owner, admin, team_member)
            created_by_id: UUID of user creating this account

        Returns:
            dict: {
                'success': bool,
                'user': dict or None,
                'error': str or None
            }
        """
        try:
            # Verify creator is an owner
            creator = self.get_current_user(created_by_id)
            if not creator or creator['role'] != 'owner':
                return {
                    'success': False,
                    'user': None,
                    'error': 'Only owners can create users'
                }

            # Validate role
            if role not in ['owner', 'admin', 'team_member']:
                return {
                    'success': False,
                    'user': None,
                    'error': 'Invalid role. Must be owner, admin, or team_member'
                }

            # Create user in Supabase Auth (requires service role key)
            auth_response = self.admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True  # Auto-confirm email
            })

            if auth_response.user:
                # Create user profile in users table
                profile_data = {
                    'id': auth_response.user.id,
                    'email': email,
                    'full_name': full_name,
                    'role': role,
                    'created_by': created_by_id,
                    'is_active': True
                }

                profile_response = self.admin_client.table("users").insert(profile_data).execute()

                if profile_response.data:
                    return {
                        'success': True,
                        'user': profile_response.data[0],
                        'error': None
                    }
                else:
                    # Rollback: delete auth user if profile creation failed
                    try:
                        self.admin_client.auth.admin.delete_user(auth_response.user.id)
                    except:
                        pass
                    return {
                        'success': False,
                        'user': None,
                        'error': 'Failed to create user profile'
                    }
            else:
                return {
                    'success': False,
                    'user': None,
                    'error': 'Failed to create user in authentication system'
                }

        except Exception as e:
            error_msg = str(e)
            if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                error_msg = 'A user with this email already exists'
            return {
                'success': False,
                'user': None,
                'error': error_msg
            }

    def get_all_users(self) -> List[Dict]:
        """
        Get all users (requires authentication)

        Returns:
            list: List of user dictionaries
        """
        try:
            response = self.admin_client.table("users").select("*").order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []

    def update_user_role(self, user_id: str, new_role: str, updated_by_id: str) -> Dict:
        """
        Update user role (owner only)

        Args:
            user_id: UUID of user to update
            new_role: New role to assign
            updated_by_id: UUID of user making the change

        Returns:
            dict: {'success': bool, 'error': str or None}
        """
        try:
            # Verify updater is an owner
            updater = self.get_current_user(updated_by_id)
            if not updater or updater['role'] != 'owner':
                return {
                    'success': False,
                    'error': 'Only owners can update user roles'
                }

            # Validate role
            if new_role not in ['owner', 'admin', 'team_member']:
                return {
                    'success': False,
                    'error': 'Invalid role. Must be owner, admin, or team_member'
                }

            # Update role
            self.admin_client.table("users").update({
                "role": new_role
            }).eq("id", user_id).execute()

            return {'success': True, 'error': None}

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to update user role: {str(e)}"
            }

    def deactivate_user(self, user_id: str, deactivated_by_id: str) -> Dict:
        """
        Deactivate a user (owner only)

        Args:
            user_id: UUID of user to deactivate
            deactivated_by_id: UUID of user performing the action

        Returns:
            dict: {'success': bool, 'error': str or None}
        """
        try:
            # Verify deactivator is an owner
            deactivator = self.get_current_user(deactivated_by_id)
            if not deactivator or deactivator['role'] != 'owner':
                return {
                    'success': False,
                    'error': 'Only owners can deactivate users'
                }

            # Prevent deactivating yourself
            if user_id == deactivated_by_id:
                return {
                    'success': False,
                    'error': 'You cannot deactivate your own account'
                }

            # Deactivate user
            self.admin_client.table("users").update({
                "is_active": False
            }).eq("id", user_id).execute()

            return {'success': True, 'error': None}

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to deactivate user: {str(e)}"
            }

    def activate_user(self, user_id: str, activated_by_id: str) -> Dict:
        """
        Activate a user (owner only)

        Args:
            user_id: UUID of user to activate
            activated_by_id: UUID of user performing the action

        Returns:
            dict: {'success': bool, 'error': str or None}
        """
        try:
            # Verify activator is an owner
            activator = self.get_current_user(activated_by_id)
            if not activator or activator['role'] != 'owner':
                return {
                    'success': False,
                    'error': 'Only owners can activate users'
                }

            # Activate user
            self.admin_client.table("users").update({
                "is_active": True
            }).eq("id", user_id).execute()

            return {'success': True, 'error': None}

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to activate user: {str(e)}"
            }

    def reset_password_request(self, email: str) -> Dict:
        """
        Send password reset email

        Args:
            email: User email

        Returns:
            dict: {'success': bool, 'error': str or None}
        """
        try:
            self.client.auth.reset_password_email(email)
            return {
                'success': True,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to send reset email: {str(e)}"
            }

    def check_permission(self, user: Dict, permission: str) -> bool:
        """
        Check if user has permission (for future granular permissions)

        Args:
            user: User dictionary with role
            permission: Permission to check (e.g., 'manage_users', 'delete_contractors')

        Returns:
            bool: True if user has permission
        """
        # Current implementation: owners can manage users, everyone else can do everything in CRM
        if permission == 'manage_users':
            return user.get('role') == 'owner'

        # All other permissions are granted to all authenticated users
        return True

    def is_owner(self, user: Dict) -> bool:
        """Check if user is an owner"""
        return user.get('role') == 'owner'

    def is_admin(self, user: Dict) -> bool:
        """Check if user is an admin"""
        return user.get('role') == 'admin'

    def is_team_member(self, user: Dict) -> bool:
        """Check if user is a team member"""
        return user.get('role') == 'team_member'


# ========== Module-level convenience functions ==========

# Create a module-level instance for convenience
_auth_manager = AuthManager()

# Export methods as module-level functions
def login(email: str, password: str) -> Dict:
    """Login with email and password"""
    return _auth_manager.login(email, password)

def logout() -> Dict:
    """Logout current user"""
    return _auth_manager.logout()

def get_current_user(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    return _auth_manager.get_current_user(user_id)

def create_user(email: str, password: str, full_name: str, role: str, created_by_id: str) -> Dict:
    """Create a new user"""
    return _auth_manager.create_user(email, password, full_name, role, created_by_id)

def get_all_users() -> List[Dict]:
    """Get all users"""
    return _auth_manager.get_all_users()

def update_user_role(user_id: str, new_role: str, updated_by_id: str) -> Dict:
    """Update user role"""
    return _auth_manager.update_user_role(user_id, new_role, updated_by_id)

def activate_user(user_id: str, activated_by_id: str) -> Dict:
    """Activate a user"""
    return _auth_manager.activate_user(user_id, activated_by_id)

def deactivate_user(user_id: str, deactivated_by_id: str) -> Dict:
    """Deactivate a user"""
    return _auth_manager.deactivate_user(user_id, deactivated_by_id)

def reset_password_request(email: str) -> Dict:
    """Send password reset email"""
    return _auth_manager.reset_password_request(email)

def check_permission(user: Dict, permission: str) -> bool:
    """Check if user has permission"""
    return _auth_manager.check_permission(user, permission)

def is_owner(user: Dict) -> bool:
    """Check if user is owner"""
    return _auth_manager.is_owner(user)

def is_admin(user: Dict) -> bool:
    """Check if user is admin"""
    return _auth_manager.is_admin(user)

def is_team_member(user: Dict) -> bool:
    """Check if user is team member"""
    return _auth_manager.is_team_member(user)
