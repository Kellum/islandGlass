"""
Island Glass Leads - Dash CRM Application
Main entry point for the Dash-based CRM system with authentication
"""
import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from modules.database import Database
from modules.auth import AuthManager
from components.auth_check import create_session_stores, create_logout_button, create_user_display
import os

# Import all pages to register their callbacks
from pages import dashboard, contractors, discovery, enrichment, bulk_actions, import_contractors, settings, login, calculator, po_clients, inventory_page

# Initialize database and auth manager
db = Database()
auth = AuthManager()

# Initialize Dash app
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    title="Island Glass Leads CRM"
)

server = app.server  # For deployment

# Create navigation links
def create_nav_link(label, icon, href):
    """Create a navigation link with icon"""
    return dmc.Anchor(
        dmc.Group([
            DashIconify(icon=icon, width=20),
            dmc.Text(label, size="sm")
        ], gap="xs"),
        href=href,
        style={
            "textDecoration": "none",
            "padding": "10px 15px",
            "borderRadius": "5px",
            "display": "block",
            "marginBottom": "5px"
        },
        className="nav-link"
    )

# App layout with authentication
app.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "light",
        "primaryColor": "blue",
        "fontFamily": "Inter, sans-serif",
    },
    children=[
        # Session stores and location
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='session-store', storage_type='session', data={'authenticated': False}),
        dcc.Store(id='redirect-trigger'),

        # Token refresh interval (refreshes every 50 minutes to prevent 60 min expiry)
        dcc.Interval(
            id='token-refresh-interval',
            interval=50*60*1000,  # 50 minutes in milliseconds
            n_intervals=0
        ),

        # Main content container (conditionally shows login or CRM)
        html.Div(id='app-container')
    ]
)

# Main app container callback - decides whether to show login or CRM
@callback(
    Output('app-container', 'children'),
    Input('url', 'pathname'),
    Input('session-store', 'data')
)
def render_app_container(pathname, session_data):
    """Render login page or main CRM based on authentication status"""

    # Check if user is authenticated
    is_authenticated = session_data and session_data.get('authenticated', False)

    # Login page doesn't require auth
    if pathname == '/login' or not is_authenticated:
        return login.layout

    # User is authenticated - show main CRM layout
    user_data = session_data.get('user', {})

    return html.Div([
        # Sidebar
        html.Div([
            dmc.Stack([
                # Logo/Title
                dmc.Text(
                    "Island Glass Leads",
                    size="xl",
                    fw=700,
                    c="blue"
                ),
                dmc.Text(
                    "CRM System",
                    size="sm",
                    c="dimmed"
                ),
                dmc.Divider(),

                # Navigation links
                create_nav_link("Dashboard", "solar:home-2-bold", "/"),
                create_nav_link("Contractors", "solar:users-group-rounded-bold", "/contractors"),
                create_nav_link("Discovery", "solar:magnifer-bold", "/discovery"),
                create_nav_link("Enrichment", "solar:magic-stick-bold", "/enrichment"),
                create_nav_link("Bulk Actions", "solar:download-minimalistic-bold", "/bulk-actions"),
                create_nav_link("Import", "solar:upload-minimalistic-bold", "/import"),

                dmc.Divider(label="GlassPricePro", labelPosition="center"),

                create_nav_link("Glass Calculator", "solar:calculator-bold", "/calculator"),
                create_nav_link("PO Tracker", "solar:document-text-bold", "/po-clients"),
                create_nav_link("Inventory", "solar:box-bold", "/inventory"),

                dmc.Divider(),

                create_nav_link("Settings", "solar:settings-bold", "/settings"),

                dmc.Space(h=20),

                # User display
                create_user_display(user_data),

                dmc.Space(h=10),

                # Logout button
                create_logout_button(),
            ], gap="xs", style={"height": "100%", "display": "flex", "flexDirection": "column"})
        ], style={
            "width": "250px",
            "minHeight": "100vh",
            "backgroundColor": "#f8f9fa",
            "padding": "20px",
            "position": "fixed",
            "left": 0,
            "top": 0
        }),

        # Main content area
        html.Div([
            dmc.Container(
                id='page-content',
                size="xl",
                style={"paddingTop": 20, "paddingBottom": 40}
            )
        ], style={
            "marginLeft": "250px",
            "padding": "20px"
        })
    ])


# Page routing callback (only fires when authenticated)
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('session-store', 'data')
)
def display_page(pathname, session_data):
    """Route to appropriate page based on URL pathname"""

    # If not authenticated, this callback shouldn't fire
    # (app-container will show login page instead)
    if not session_data or not session_data.get('authenticated'):
        return dmc.Alert(
            "Please log in to access this page",
            title="Authentication Required",
            color="blue"
        )

    # Route to appropriate page
    if pathname == '/' or pathname is None:
        return dashboard.layout
    elif pathname == '/contractors':
        return contractors.layout
    elif pathname == '/discovery':
        return discovery.layout
    elif pathname == '/enrichment':
        return enrichment.layout
    elif pathname == '/bulk-actions':
        return bulk_actions.layout
    elif pathname == '/import':
        return import_contractors.layout
    elif pathname == '/calculator':
        return calculator.layout
    elif pathname == '/po-clients':
        return po_clients.layout
    elif pathname == '/inventory':
        return inventory_page.layout
    elif pathname == '/settings':
        return settings.layout
    elif pathname == '/login':
        return None  # Login is handled by app-container
    else:
        return dmc.Alert(
            "404 - Page not found",
            title="Error",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold")
        )


# Logout callback
@callback(
    Output('session-store', 'data', allow_duplicate=True),
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """Handle logout button click"""
    if n_clicks:
        auth.logout()
        return {'authenticated': False, 'user': None}, '/login'
    return dash.no_update, dash.no_update


# Redirect after login callback
@callback(
    Output('url', 'pathname'),
    Input('login-redirect-trigger', 'data'),
    State('login-session-store', 'data'),
    prevent_initial_call=True
)
def redirect_after_login(trigger, login_session):
    """Redirect to dashboard after successful login"""
    if trigger and trigger.get('redirect') and login_session:
        # Update main session store will happen via another callback
        return '/'
    return dash.no_update


# Sync login session to main session
@callback(
    Output('session-store', 'data'),
    Input('login-session-store', 'data'),
    prevent_initial_call=True
)
def sync_login_session(login_session):
    """Sync login page session to main session store"""
    if login_session and login_session.get('authenticated'):
        return login_session
    return dash.no_update

# Automatic token refresh (Gmail-style - keeps users logged in)
@callback(
    Output('session-store', 'data', allow_duplicate=True),
    Input('token-refresh-interval', 'n_intervals'),
    State('session-store', 'data'),
    prevent_initial_call=True
)
def refresh_token_automatically(n_intervals, session_data):
    """
    Automatically refresh JWT token every 50 minutes to prevent expiration.
    This allows users to work for extended periods without being logged out.
    """
    # Only refresh if user is authenticated
    if not session_data or not session_data.get('authenticated'):
        return dash.no_update

    # Check if we have a refresh_token
    session_dict = session_data.get('session', {})
    refresh_token = session_dict.get('refresh_token')

    if not refresh_token:
        print("WARNING: No refresh_token found in session - cannot refresh")
        return dash.no_update

    print(f"INFO: Auto-refreshing token (interval #{n_intervals})...")

    # Attempt to refresh the session
    from modules.auth import AuthManager
    auth = AuthManager()
    result = auth.refresh_session(refresh_token)

    if result['success']:
        # Update session with new tokens
        session_data['session'] = result['session']
        print("SUCCESS: Token refreshed successfully - user session extended")
        return session_data
    else:
        # Refresh failed - log out user
        print(f"ERROR: Token refresh failed: {result.get('error')}")
        print("INFO: Redirecting user to login page")
        return {'authenticated': False, 'session': None}

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Island Glass Leads CRM - Dash Application")
    print("="*60)
    print("📊 Running on: http://localhost:8050")
    print("🔄 Debug mode: ON")
    print("="*60 + "\n")
    app.run(debug=True, port=8050)
