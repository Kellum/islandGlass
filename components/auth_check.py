"""
Authentication Check Component
Wraps protected content and manages session state
"""
import dash_mantine_components as dmc
from dash import html, dcc
from dash_iconify import DashIconify


def create_session_stores():
    """
    Create dcc.Store components for session management
    These should be added to the app layout
    """
    return [
        # Store for user session data
        dcc.Store(
            id='session-store',
            storage_type='session',  # Persists until browser tab is closed
            data={'authenticated': False, 'user': None}
        ),

        # Store for triggering redirects
        dcc.Store(
            id='redirect-store',
            storage_type='memory'  # Clears on page refresh
        ),

        # Location component for handling redirects
        dcc.Location(id='url', refresh=False)
    ]


def create_logout_button():
    """
    Create logout button for navigation
    """
    return dmc.Button(
        "Logout",
        id="logout-button",
        variant="subtle",
        color="red",
        leftSection=DashIconify(icon="solar:logout-2-bold"),
        size="sm",
        style={"marginTop": "auto"}  # Push to bottom of sidebar
    )


def create_user_display(user_data):
    """
    Create user info display for navigation

    Args:
        user_data: Dict with user info (name, email, role)

    Returns:
        DMC component showing user info
    """
    if not user_data:
        return None

    role_colors = {
        'owner': 'red',
        'admin': 'blue',
        'team_member': 'green'
    }

    role_labels = {
        'owner': 'Owner',
        'admin': 'Admin',
        'team_member': 'Team Member'
    }

    role = user_data.get('role', 'team_member')

    return dmc.Paper([
        dmc.Stack([
            dmc.Group([
                DashIconify(icon="solar:user-circle-bold", width=20, color="gray"),
                dmc.Stack([
                    dmc.Text(
                        user_data.get('full_name', user_data.get('email', 'User')),
                        size="sm",
                        fw=500
                    ),
                    dmc.Badge(
                        role_labels.get(role, role),
                        size="sm",
                        color=role_colors.get(role, 'gray'),
                        variant="light"
                    )
                ], gap=0)
            ], gap="xs")
        ], gap="xs")
    ], p="sm", withBorder=True, radius="md", style={"marginTop": "10px"})


def create_unauthenticated_message():
    """
    Create message shown when user is not authenticated
    """
    return dmc.Center(
        style={"minHeight": "100vh"},
        children=dmc.Stack([
            dmc.Alert(
                "Please log in to access the CRM",
                title="Authentication Required",
                color="blue",
                icon=DashIconify(icon="solar:lock-password-bold")
            ),
            dmc.Button(
                "Go to Login",
                href="/login",
                leftSection=DashIconify(icon="solar:login-3-bold")
            )
        ], align="center", gap="md")
    )


def require_auth(layout_function):
    """
    Decorator to protect pages that require authentication

    Usage:
        @require_auth
        def create_protected_layout(user):
            return dmc.Stack([...])

    Args:
        layout_function: Function that takes user data and returns layout

    Returns:
        Wrapped function that checks auth before rendering
    """
    def wrapper(session_data=None):
        if not session_data or not session_data.get('authenticated'):
            return create_unauthenticated_message()

        user = session_data.get('user')
        return layout_function(user)

    return wrapper


def require_owner(layout_function):
    """
    Decorator to protect pages that require owner role

    Usage:
        @require_owner
        def create_owner_only_layout(user):
            return dmc.Stack([...])

    Args:
        layout_function: Function that takes user data and returns layout

    Returns:
        Wrapped function that checks owner role before rendering
    """
    def wrapper(session_data=None):
        if not session_data or not session_data.get('authenticated'):
            return create_unauthenticated_message()

        user = session_data.get('user')
        if user.get('role') != 'owner':
            return dmc.Center(
                style={"minHeight": "80vh"},
                children=dmc.Alert(
                    "This feature is only available to account owners",
                    title="Access Denied",
                    color="red",
                    icon=DashIconify(icon="solar:shield-cross-bold")
                )
            )

        return layout_function(user)

    return wrapper


# Session validation helper
def is_authenticated(session_data):
    """
    Check if session data indicates authenticated user

    Args:
        session_data: Data from session-store

    Returns:
        bool: True if authenticated
    """
    if not session_data:
        return False
    return session_data.get('authenticated', False)


def get_user_from_session(session_data):
    """
    Extract user data from session

    Args:
        session_data: Data from session-store

    Returns:
        dict or None: User data if authenticated
    """
    if not is_authenticated(session_data):
        return None
    return session_data.get('user')


def is_owner(session_data):
    """
    Check if session user is an owner

    Args:
        session_data: Data from session-store

    Returns:
        bool: True if user is owner
    """
    user = get_user_from_session(session_data)
    if not user:
        return False
    return user.get('role') == 'owner'
