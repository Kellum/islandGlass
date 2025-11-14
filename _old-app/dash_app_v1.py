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
from components.auth_check import create_session_stores, create_logout_button, create_user_display, create_session_status_indicator
import os

# Import all pages to register their callbacks
from pages import dashboard, contractors, discovery, enrichment, bulk_actions, import_contractors, settings, login, calculator, po_clients, purchase_orders, inventory_page, window_order_entry, window_order_management, window_label_printing, pricing_settings, jobs, job_detail, test_client

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
        "primaryColor": "violet",
        "fontFamily": "Inter, sans-serif",
        "defaultRadius": "md",
        "shadows": {
            "sm": "0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1)",
            "md": "0 4px 6px rgba(0, 0, 0, 0.05), 0 2px 4px rgba(0, 0, 0, 0.06)",
            "lg": "0 10px 15px rgba(0, 0, 0, 0.05), 0 4px 6px rgba(0, 0, 0, 0.05)",
            "xl": "0 20px 25px rgba(0, 0, 0, 0.05), 0 10px 10px rgba(0, 0, 0, 0.04)"
        },
        "spacing": {
            "xs": "8px",
            "sm": "12px",
            "md": "16px",
            "lg": "24px",
            "xl": "32px"
        },
        "components": {
            "Button": {
                "defaultProps": {
                    "radius": "lg"
                },
                "styles": {
                    "root": {
                        "fontWeight": 500
                    }
                }
            },
            "TextInput": {
                "defaultProps": {
                    "radius": "md"
                },
                "styles": {
                    "input": {
                        "backgroundColor": "#F3F4F6",
                        "border": "1px solid #E5E7EB",
                        "&:focus": {
                            "backgroundColor": "#FFFFFF",
                            "borderColor": "#7C3AED"
                        }
                    }
                }
            },
            "NumberInput": {
                "defaultProps": {
                    "radius": "md"
                },
                "styles": {
                    "input": {
                        "backgroundColor": "#F3F4F6",
                        "border": "1px solid #E5E7EB",
                        "&:focus": {
                            "backgroundColor": "#FFFFFF",
                            "borderColor": "#7C3AED"
                        }
                    }
                }
            },
            "Select": {
                "defaultProps": {
                    "radius": "md"
                },
                "styles": {
                    "input": {
                        "backgroundColor": "#F3F4F6",
                        "border": "1px solid #E5E7EB",
                        "&:focus": {
                            "backgroundColor": "#FFFFFF",
                            "borderColor": "#7C3AED"
                        }
                    }
                }
            },
            "Card": {
                "defaultProps": {
                    "radius": "lg",
                    "shadow": "sm"
                }
            },
            "Paper": {
                "defaultProps": {
                    "radius": "lg"
                }
            }
        }
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

        # Hidden div for user_id (synced from session-store, accessible by page modules)
        # This solves the State("session-store", "data") blocking issue in page callbacks
        html.Div(id='user-id-hidden-div', style={'display': 'none'}),

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
            # Scrollable top section
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

                    # Collapsible Navigation
                    dmc.Accordion([
                        dmc.AccordionItem([
                            dmc.AccordionControl("CRM"),
                            dmc.AccordionPanel([
                                create_nav_link("Dashboard", "solar:home-2-bold", "/"),
                                create_nav_link("Clients", "solar:users-group-rounded-bold", "/clients"),
                                create_nav_link("Purchase Orders", "solar:document-text-bold", "/purchase-orders"),
                            ])
                        ], value="crm"),

                        dmc.AccordionItem([
                            dmc.AccordionControl("Leads & Sales"),
                            dmc.AccordionPanel([
                                create_nav_link("Contractors", "solar:users-group-rounded-bold", "/contractors"),
                                create_nav_link("Discovery", "solar:magnifer-bold", "/discovery"),
                                create_nav_link("Enrichment", "solar:magic-stick-bold", "/enrichment"),
                                create_nav_link("Bulk Actions", "solar:download-minimalistic-bold", "/bulk-actions"),
                                create_nav_link("Import", "solar:upload-minimalistic-bold", "/import"),
                            ])
                        ], value="leads"),

                        dmc.AccordionItem([
                            dmc.AccordionControl("GlassPricePro"),
                            dmc.AccordionPanel([
                                create_nav_link("Glass Calculator", "solar:calculator-bold", "/calculator"),
                                create_nav_link("Inventory", "solar:box-bold", "/inventory"),
                            ])
                        ], value="glass"),

                        dmc.AccordionItem([
                            dmc.AccordionControl("Window Manufacturing"),
                            dmc.AccordionPanel([
                                create_nav_link("Order Entry", "mdi:clipboard-edit", "/window-order-entry"),
                                create_nav_link("Order Management", "mdi:format-list-checks", "/window-order-management"),
                                create_nav_link("Label Printing", "mdi:printer", "/window-label-printing"),
                            ])
                        ], value="windows"),
                    ], multiple=True, variant="separated", chevronPosition="left", value=["crm"]),
                ], gap="xs")
            ], style={
                "overflowY": "auto",
                "flex": "1",
                "paddingBottom": "10px"
            }),

            # Fixed bottom section
            html.Div([
                dmc.Stack([
                    dmc.Divider(),

                    create_nav_link("Settings", "solar:settings-bold", "/settings"),
                    create_nav_link("Pricing Settings", "solar:dollar-bold", "/pricing-settings"),

                    # User display
                    create_user_display(user_data),

                    # Session status indicator
                    create_session_status_indicator(),

                    # Logout button
                    create_logout_button(),
                ], gap="xs")
            ], style={
                "borderTop": "1px solid #dee2e6",
                "paddingTop": "5px",
                "backgroundColor": "#f8f9fa"
            })
        ], style={
            "width": "250px",
            "height": "100vh",
            "backgroundColor": "#f8f9fa",
            "padding": "20px",
            "position": "fixed",
            "left": 0,
            "top": 0,
            "display": "flex",
            "flexDirection": "column"
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
    elif pathname == '/test-client':
        return test_client.layout(session_data)
    elif pathname == '/clients':
        return po_clients.layout
    elif pathname == '/po-clients':  # Legacy route - redirect
        return po_clients.layout
    elif pathname == '/purchase-orders':
        return purchase_orders.layout
    elif pathname == '/inventory':
        return inventory_page.layout
    elif pathname == '/window-order-entry':
        return window_order_entry.layout(session_data)
    elif pathname == '/window-order-management':
        return window_order_management.layout(session_data)
    elif pathname == '/window-label-printing':
        return window_label_printing.layout(session_data)
    elif pathname == '/settings':
        return settings.layout
    elif pathname == '/pricing-settings':
        return pricing_settings.layout()
    elif pathname == '/jobs':
        return jobs.layout(session_data)
    elif pathname and pathname.startswith('/job/'):
        # Extract job_id from path /job/<job_id>
        job_id = pathname.split('/')[-1]
        return job_detail.layout(job_id=job_id, session_data=session_data)
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


# Sync user_id to hidden div (accessible by page modules)
@callback(
    Output('user-id-hidden-div', 'children'),
    Input('session-store', 'data')
)
def sync_user_id_to_hidden_div(session_data):
    """
    Sync user_id from session-store to hidden div

    This allows page modules to access user_id via State('user-id-hidden-div', 'children')
    without needing State('session-store', 'data') which blocks callbacks in page modules.

    See: ARCHITECTURE_RULES.md Rule #2, LESSONS_LEARNED.md Lesson 2
    """
    if not session_data or not session_data.get('authenticated'):
        return None

    # Extract user_id from session
    user_id = session_data.get('session', {}).get('user', {}).get('id')

    print(f"🔄 Syncing user_id to hidden div: {user_id}")

    return user_id


# Session status display callback
@callback(
    Output('session-status-display', 'children'),
    Input('token-refresh-interval', 'n_intervals'),
    State('session-store', 'data')
)
def update_session_status(n_intervals, session_data):
    """
    Update the session status indicator to show time remaining
    """
    if not session_data or not session_data.get('authenticated'):
        return None

    # JWT tokens expire after 60 minutes
    # We refresh every 50 minutes, so calculate time until next refresh
    TOKEN_LIFETIME_MINUTES = 60
    REFRESH_INTERVAL_MINUTES = 50

    # Time since last refresh (or login)
    minutes_since_refresh = (n_intervals * REFRESH_INTERVAL_MINUTES) % TOKEN_LIFETIME_MINUTES
    minutes_remaining = TOKEN_LIFETIME_MINUTES - minutes_since_refresh

    # Determine status
    if minutes_remaining > 15:
        status = 'active'
        color = 'green'
        icon = 'solar:shield-check-bold'
    elif minutes_remaining > 5:
        status = 'warning'
        color = 'orange'
        icon = 'solar:danger-triangle-bold'
    else:
        status = 'refreshing'
        color = 'blue'
        icon = 'solar:refresh-circle-bold'

    return dmc.Paper([
        dmc.Group([
            DashIconify(icon=icon, width=16, color=color),
            dmc.Stack([
                dmc.Text("Session Status", size="xs", c="dimmed"),
                dmc.Text(
                    f"{minutes_remaining} min remaining",
                    size="xs",
                    fw=500,
                    c=color
                )
            ], gap=0)
        ], gap="xs")
    ], p="xs", withBorder=True, radius="sm", style={"backgroundColor": "#f8f9fa"})


# Automatic token refresh (Gmail-style - keeps users logged in)
@callback(
    Output('session-store', 'data', allow_duplicate=True),
    Output('session-notification', 'children', allow_duplicate=True),
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
        return dash.no_update, dash.no_update

    # Check if we have a refresh_token
    session_dict = session_data.get('session', {})
    refresh_token = session_dict.get('refresh_token')

    if not refresh_token:
        print("WARNING: No refresh_token found in session - cannot refresh")
        return dash.no_update, dash.no_update

    print(f"INFO: Auto-refreshing token (interval #{n_intervals})...")

    # Show notification
    notification = dmc.Notification(
        id="refresh-notification",
        title="Session Refreshed",
        message="Your session has been automatically extended",
        color="green",
        icon=DashIconify(icon="solar:check-circle-bold"),
        action="show",
        autoClose=3000
    )

    # Attempt to refresh the session
    from modules.auth import AuthManager
    auth = AuthManager()
    result = auth.refresh_session(refresh_token)

    if result['success']:
        # Update session with new tokens
        session_data['session'] = result['session']
        print("SUCCESS: Token refreshed successfully - user session extended")
        return session_data, notification
    else:
        # Refresh failed - log out user
        print(f"ERROR: Token refresh failed: {result.get('error')}")
        print("INFO: Redirecting user to login page")
        error_notification = dmc.Notification(
            id="refresh-error-notification",
            title="Session Expired",
            message="Please log in again",
            color="red",
            icon=DashIconify(icon="solar:close-circle-bold"),
            action="show",
            autoClose=5000
        )
        return {'authenticated': False, 'session': None}, error_notification

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Island Glass Leads CRM - Dash Application")
    print("="*60)
    print("📊 Running on: http://localhost:8050")
    print("🔄 Debug mode: ON")
    print("="*60 + "\n")
    app.run(debug=True, port=8050)
