"""
QuickBooks Integration Settings Page
Island Glass CRM - Purchase Order System Phase 1
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import DatabaseConnection
from modules.quickbooks_integration import QuickBooksIntegration
from components.auth_check import require_auth

# Register page
dash.register_page(__name__, path='/quickbooks-settings', name='QuickBooks Settings',
                   title='QuickBooks Settings - Island Glass')

# Initialize database
db = DatabaseConnection()
qb = QuickBooksIntegration(db)

# =====================================================
# LAYOUT
# =====================================================

layout = html.Div([
    require_auth(),

    dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="bi bi-cloud-arrow-up me-3"),
                    "QuickBooks Integration Settings"
                ], className="mb-0"),
            ], width=12),
        ], className="mb-4 mt-4"),

        # Connection Status Card
        dbc.Card([
            dbc.CardHeader([
                html.H5([
                    html.I(className="bi bi-plug me-2"),
                    "Connection Status"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div(id="qb-connection-status"),
                        dcc.Interval(id="qb-status-interval", interval=5000, n_intervals=0),
                    ], width=8),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button(
                                [html.I(className="bi bi-arrow-clockwise me-2"), "Test Connection"],
                                id="qb-test-btn",
                                color="info",
                                outline=True,
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-x-circle me-2"), "Disconnect"],
                                id="qb-disconnect-btn",
                                color="danger",
                                outline=True
                            ),
                        ], className="float-end")
                    ], width=4),
                ]),
            ])
        ], className="mb-4"),

        # Setup Instructions Card
        dbc.Card([
            dbc.CardHeader([
                html.H5([
                    html.I(className="bi bi-info-circle me-2"),
                    "Setup Instructions"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                html.P([
                    "To connect Island Glass CRM to QuickBooks Online, follow these steps:"
                ], className="fw-bold"),

                html.Ol([
                    html.Li([
                        "Create a QuickBooks Online Developer account at ",
                        html.A("developer.intuit.com", href="https://developer.intuit.com",
                              target="_blank", className="fw-bold"),
                    ]),
                    html.Li("Create a new app in the QuickBooks Developer portal"),
                    html.Li("Get your Client ID and Client Secret from the app settings"),
                    html.Li("Add your redirect URI to the app settings (default: http://localhost:8050/qb-callback)"),
                    html.Li("Configure the credentials below"),
                    html.Li("Click 'Connect to QuickBooks' to authorize the integration"),
                ]),

                dbc.Alert([
                    html.I(className="bi bi-shield-check me-2"),
                    html.Strong("Security Note: "),
                    "Your QuickBooks credentials are encrypted and stored securely. "
                    "The CRM only requests the minimum permissions needed for vendor and PO management."
                ], color="info", className="mt-3")
            ])
        ], className="mb-4"),

        # Configuration Card
        dbc.Card([
            dbc.CardHeader([
                html.H5([
                    html.I(className="bi bi-gear me-2"),
                    "Configuration"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Form([
                    # Client ID
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Client ID", className="fw-bold"),
                            dbc.Input(
                                id="qb-client-id-input",
                                placeholder="Enter QuickBooks Client ID",
                                type="text",
                                className="mb-3"
                            ),
                            dbc.FormText("Your QuickBooks app Client ID from the developer portal")
                        ], width=12),
                    ]),

                    # Client Secret
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Client Secret", className="fw-bold"),
                            dbc.Input(
                                id="qb-client-secret-input",
                                placeholder="Enter QuickBooks Client Secret",
                                type="password",
                                className="mb-3"
                            ),
                            dbc.FormText("Your QuickBooks app Client Secret from the developer portal")
                        ], width=12),
                    ]),

                    # Redirect URI
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Redirect URI", className="fw-bold"),
                            dbc.Input(
                                id="qb-redirect-uri-input",
                                placeholder="http://localhost:8050/qb-callback",
                                type="text",
                                value="http://localhost:8050/qb-callback",
                                className="mb-3"
                            ),
                            dbc.FormText("The redirect URI configured in your QuickBooks app")
                        ], width=12),
                    ]),

                    # Save and Connect Buttons
                    dbc.Row([
                        dbc.Col([
                            dbc.ButtonGroup([
                                dbc.Button(
                                    [html.I(className="bi bi-save me-2"), "Save Configuration"],
                                    id="qb-save-config-btn",
                                    color="primary",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    [html.I(className="bi bi-box-arrow-up-right me-2"), "Connect to QuickBooks"],
                                    id="qb-connect-btn",
                                    color="success",
                                    external_link=True
                                ),
                            ])
                        ], width=12),
                    ]),
                ])
            ])
        ], className="mb-4"),

        # Synchronization Settings Card
        dbc.Card([
            dbc.CardHeader([
                html.H5([
                    html.I(className="bi bi-arrow-repeat me-2"),
                    "Synchronization Settings"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Auto-sync Options", className="fw-bold mb-3"),
                        dbc.Checklist(
                            id="qb-auto-sync-options",
                            options=[
                                {"label": "Auto-sync vendors when created or updated", "value": "vendors"},
                                {"label": "Auto-sync purchase orders when created", "value": "pos"},
                                {"label": "Auto-sync payments when recorded", "value": "payments"},
                            ],
                            value=["vendors"],
                            className="mb-3"
                        ),
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Sync Schedule", className="fw-bold mb-3"),
                        dbc.Select(
                            id="qb-sync-schedule",
                            options=[
                                {"label": "Manual only", "value": "manual"},
                                {"label": "Every hour", "value": "hourly"},
                                {"label": "Every 4 hours", "value": "4hours"},
                                {"label": "Daily", "value": "daily"},
                            ],
                            value="manual",
                            className="mb-3"
                        ),
                        dbc.FormText("How often to automatically sync data with QuickBooks")
                    ], width=6),
                ]),

                html.Hr(),

                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="bi bi-arrow-clockwise me-2"), "Sync All Vendors Now"],
                            id="qb-sync-vendors-btn",
                            color="info",
                            outline=True,
                            className="me-2"
                        ),
                        dbc.Button(
                            [html.I(className="bi bi-arrow-clockwise me-2"), "Sync All POs Now"],
                            id="qb-sync-pos-btn",
                            color="info",
                            outline=True,
                        ),
                    ], width=12),
                ]),
            ])
        ], className="mb-4"),

        # Sync Log Card
        dbc.Card([
            dbc.CardHeader([
                html.H5([
                    html.I(className="bi bi-clock-history me-2"),
                    "Recent Sync Activity"
                ], className="mb-0")
            ]),
            dbc.CardBody([
                html.Div(id="qb-sync-log-container"),
                dcc.Interval(id="qb-log-interval", interval=10000, n_intervals=0),
            ])
        ], className="mb-4"),

        # Toast notifications
        html.Div(id="qb-toast-container", style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999}),

    ], fluid=True, className="pb-5")
])


# =====================================================
# CALLBACKS
# =====================================================

@callback(
    Output("qb-connection-status", "children"),
    Input("qb-status-interval", "n_intervals"),
)
def update_connection_status(n):
    """Display QuickBooks connection status"""

    is_connected = qb.is_connected()

    if is_connected:
        success, message = qb.test_connection()

        if success:
            return dbc.Alert([
                html.I(className="bi bi-check-circle me-2"),
                html.Strong("Connected: "),
                message,
                html.Br(),
                html.Small(f"Token expires: {qb.token_expires_at.strftime('%Y-%m-%d %H:%M:%S') if qb.token_expires_at else 'Unknown'}",
                          className="text-muted")
            ], color="success")
        else:
            return dbc.Alert([
                html.I(className="bi bi-exclamation-triangle me-2"),
                html.Strong("Connection Error: "),
                message
            ], color="warning")
    else:
        return dbc.Alert([
            html.I(className="bi bi-x-circle me-2"),
            html.Strong("Not Connected"),
            html.Br(),
            "Configure your credentials and click 'Connect to QuickBooks' to get started."
        ], color="danger")


@callback(
    Output("qb-toast-container", "children", allow_duplicate=True),
    Input("qb-save-config-btn", "n_clicks"),
    State("qb-client-id-input", "value"),
    State("qb-client-secret-input", "value"),
    State("qb-redirect-uri-input", "value"),
    prevent_initial_call=True
)
def save_qb_config(n_clicks, client_id, client_secret, redirect_uri):
    """Save QuickBooks configuration"""

    if not n_clicks:
        return None

    if not client_id or not client_secret:
        return dbc.Toast(
            "Please enter both Client ID and Client Secret",
            header="Validation Error",
            icon="danger",
            duration=4000,
            is_open=True
        )

    try:
        # Save to environment variables (in production, save to secure config)
        os.environ['QB_CLIENT_ID'] = client_id
        os.environ['QB_CLIENT_SECRET'] = client_secret
        os.environ['QB_REDIRECT_URI'] = redirect_uri or 'http://localhost:8050/qb-callback'

        # Reload QB integration
        qb.client_id = client_id
        qb.client_secret = client_secret
        qb.redirect_uri = redirect_uri

        return dbc.Toast(
            "QuickBooks configuration saved successfully!",
            header="Success",
            icon="success",
            duration=4000,
            is_open=True
        )

    except Exception as e:
        return dbc.Toast(
            f"Error saving configuration: {str(e)}",
            header="Error",
            icon="danger",
            duration=4000,
            is_open=True
        )


@callback(
    Output("qb-connect-btn", "href"),
    Input("qb-connect-btn", "n_clicks"),
    prevent_initial_call=True
)
def get_authorization_url(n_clicks):
    """Get QuickBooks authorization URL"""
    if not n_clicks:
        return "#"

    try:
        auth_url = qb.get_authorization_url()
        return auth_url
    except Exception as e:
        print(f"Error getting auth URL: {e}")
        return "#"


@callback(
    Output("qb-toast-container", "children", allow_duplicate=True),
    Input("qb-test-btn", "n_clicks"),
    prevent_initial_call=True
)
def test_qb_connection(n_clicks):
    """Test QuickBooks connection"""

    if not n_clicks:
        return None

    success, message = qb.test_connection()

    return dbc.Toast(
        message,
        header="Connection Test",
        icon="success" if success else "danger",
        duration=4000,
        is_open=True
    )


@callback(
    Output("qb-toast-container", "children", allow_duplicate=True),
    Input("qb-disconnect-btn", "n_clicks"),
    prevent_initial_call=True
)
def disconnect_qb(n_clicks):
    """Disconnect from QuickBooks"""

    if not n_clicks:
        return None

    try:
        qb.disconnect()
        return dbc.Toast(
            "Disconnected from QuickBooks successfully",
            header="Disconnected",
            icon="info",
            duration=4000,
            is_open=True
        )
    except Exception as e:
        return dbc.Toast(
            f"Error disconnecting: {str(e)}",
            header="Error",
            icon="danger",
            duration=4000,
            is_open=True
        )


@callback(
    Output("qb-sync-log-container", "children"),
    Input("qb-log-interval", "n_intervals"),
)
def load_sync_log(n):
    """Load recent sync activity"""

    try:
        logs = db.fetch_all("""
            SELECT
                sync_id, entity_type, entity_id, sync_action, sync_status,
                quickbooks_id, error_message, sync_timestamp
            FROM quickbooks_sync_log
            ORDER BY sync_timestamp DESC
            LIMIT 20
        """)

        if not logs:
            return dbc.Alert(
                [html.I(className="bi bi-info-circle me-2"), "No sync activity yet"],
                color="light"
            )

        # Create table
        table_header = [
            html.Thead(html.Tr([
                html.Th("Timestamp"),
                html.Th("Entity Type"),
                html.Th("Entity ID"),
                html.Th("Action"),
                html.Th("Status"),
                html.Th("QB ID"),
            ]))
        ]

        table_rows = []
        for log in logs:
            status_badge = dbc.Badge(
                log['sync_status'],
                color="success" if log['sync_status'] == 'Success' else "danger",
            )

            table_rows.append(html.Tr([
                html.Td(log['sync_timestamp'].strftime('%Y-%m-%d %H:%M:%S')),
                html.Td(log['entity_type']),
                html.Td(log['entity_id']),
                html.Td(log['sync_action']),
                html.Td(status_badge),
                html.Td(log['quickbooks_id'] or '-'),
            ]))

        table_body = [html.Tbody(table_rows)]

        return dbc.Table(
            table_header + table_body,
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            size="sm"
        )

    except Exception as e:
        return dbc.Alert(f"Error loading sync log: {str(e)}", color="danger")


@callback(
    Output("qb-toast-container", "children", allow_duplicate=True),
    Input("qb-sync-vendors-btn", "n_clicks"),
    prevent_initial_call=True
)
def sync_all_vendors(n_clicks):
    """Sync all vendors to QuickBooks"""

    if not n_clicks:
        return None

    try:
        # Get all active vendors with QB sync enabled
        vendors = db.fetch_all("""
            SELECT vendor_id, vendor_name
            FROM vendors
            WHERE is_active = TRUE AND quickbooks_sync_enabled = TRUE
        """)

        if not vendors:
            return dbc.Toast(
                "No vendors configured for QuickBooks sync",
                header="Info",
                icon="info",
                duration=4000,
                is_open=True
            )

        success_count = 0
        fail_count = 0

        for vendor in vendors:
            success, qb_id = qb.sync_vendor_to_qb(vendor['vendor_id'])
            if success:
                success_count += 1
            else:
                fail_count += 1

        return dbc.Toast(
            f"Synced {success_count} vendor(s) successfully. {fail_count} failed.",
            header="Sync Complete",
            icon="success" if fail_count == 0 else "warning",
            duration=5000,
            is_open=True
        )

    except Exception as e:
        return dbc.Toast(
            f"Error syncing vendors: {str(e)}",
            header="Error",
            icon="danger",
            duration=4000,
            is_open=True
        )
