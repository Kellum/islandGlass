"""
Window Manufacturing Access Control Module

Provides role-based permission checking for window manufacturing features.

Role Hierarchy:
- owner: Full access to everything
- ig_manufacturing_admin: Full window manufacturing access
- ig_admin: Everything except window manufacturing
- ig_employee: Window order entry only
- sales: Contractor dashboard and PO tracking only
"""

from typing import Dict, Optional


class WindowPermissions:
    """Handle window manufacturing permissions"""

    # Role definitions
    ROLE_OWNER = 'owner'
    ROLE_IG_MANUFACTURING_ADMIN = 'ig_manufacturing_admin'
    ROLE_IG_ADMIN = 'ig_admin'
    ROLE_IG_EMPLOYEE = 'ig_employee'
    ROLE_SALES = 'sales'

    # Department definitions
    DEPT_MANUFACTURING = 'manufacturing'
    DEPT_SALES = 'sales'
    DEPT_ADMIN = 'admin'
    DEPT_GENERAL = 'general'

    def __init__(self, user_profile: Optional[Dict] = None):
        """
        Initialize permissions for a user

        Args:
            user_profile: Dict with 'role' and 'department' keys
        """
        self.role = user_profile.get('role') if user_profile else None
        self.department = user_profile.get('department') if user_profile else None

    def can_access_window_system(self) -> bool:
        """
        Check if user can access ANY window manufacturing features

        Returns:
            bool: True if user has any window access
        """
        if not self.role:
            return False

        # Owners can access everything
        if self.role == self.ROLE_OWNER:
            return True

        # Manufacturing admins have full access
        if self.role == self.ROLE_IG_MANUFACTURING_ADMIN:
            return True

        # IG Employees can access if in manufacturing department
        if self.role == self.ROLE_IG_EMPLOYEE:
            return True  # All employees can at least submit orders

        return False

    def can_enter_orders(self) -> bool:
        """
        Check if user can enter new window orders

        Returns:
            bool: True if user can submit orders
        """
        if not self.role:
            return False

        # Owners, manufacturing admins, and all IG employees can enter orders
        return self.role in [
            self.ROLE_OWNER,
            self.ROLE_IG_MANUFACTURING_ADMIN,
            self.ROLE_IG_EMPLOYEE
        ]

    def can_manage_orders(self) -> bool:
        """
        Check if user can view/edit all orders and change statuses

        Returns:
            bool: True if user can manage orders
        """
        if not self.role:
            return False

        # Only owners and manufacturing admins can manage
        return self.role in [
            self.ROLE_OWNER,
            self.ROLE_IG_MANUFACTURING_ADMIN
        ]

    def can_print_labels(self) -> bool:
        """
        Check if user can access label printing system

        Returns:
            bool: True if user can print labels
        """
        # Same as can_manage_orders - printing is an admin function
        return self.can_manage_orders()

    def can_configure_printers(self) -> bool:
        """
        Check if user can configure printer settings

        Returns:
            bool: True if user can configure printers
        """
        if not self.role:
            return False

        # Only owners and manufacturing admins can configure printers
        return self.role in [
            self.ROLE_OWNER,
            self.ROLE_IG_MANUFACTURING_ADMIN
        ]

    def get_accessible_features(self) -> Dict[str, bool]:
        """
        Get dictionary of all window features and their access status

        Returns:
            Dict with feature names as keys and bool access as values
        """
        return {
            'window_system': self.can_access_window_system(),
            'order_entry': self.can_enter_orders(),
            'order_management': self.can_manage_orders(),
            'label_printing': self.can_print_labels(),
            'printer_config': self.can_configure_printers()
        }

    def get_navigation_items(self) -> list:
        """
        Get list of navigation items user should see

        Returns:
            List of dicts with navigation item details
        """
        items = []

        if not self.can_access_window_system():
            return items

        # Order Entry - all window users can see
        if self.can_enter_orders():
            items.append({
                'label': 'Window Order Entry',
                'href': '/window-order-entry',
                'icon': 'solar:clipboard-add-bold'
            })

        # Order Management - admins only
        if self.can_manage_orders():
            items.append({
                'label': 'Order Management',
                'href': '/window-order-management',
                'icon': 'solar:clipboard-list-bold'
            })

        # Label Printing - admins only
        if self.can_print_labels():
            items.append({
                'label': 'Label Printing',
                'href': '/window-label-printing',
                'icon': 'solar:printer-bold'
            })

        return items


def check_window_access(user_profile: Optional[Dict]) -> bool:
    """
    Helper function to quickly check if user has any window access

    Args:
        user_profile: Dict with user role and department

    Returns:
        bool: True if user can access window features
    """
    perms = WindowPermissions(user_profile)
    return perms.can_access_window_system()


def get_user_window_permissions(user_profile: Optional[Dict]) -> WindowPermissions:
    """
    Get WindowPermissions object for a user

    Args:
        user_profile: Dict with user role and department

    Returns:
        WindowPermissions instance
    """
    return WindowPermissions(user_profile)


# Example usage:
"""
from modules.permissions import get_user_window_permissions

# Get user profile from session
user_profile = session_data.get('user_profile', {})

# Check permissions
perms = get_user_window_permissions(user_profile)

if perms.can_enter_orders():
    # Show order entry form
    pass

if perms.can_manage_orders():
    # Show order management dashboard
    pass

# Get all accessible features
features = perms.get_accessible_features()
# {'window_system': True, 'order_entry': True, 'order_management': False, ...}

# Get navigation items
nav_items = perms.get_navigation_items()
# [{'label': 'Window Order Entry', 'href': '/window-order-entry', ...}, ...]
"""
