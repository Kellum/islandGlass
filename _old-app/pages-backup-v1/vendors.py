"""
Vendors Management Page
Island Glass CRM - Purchase Order System Phase 1
"""

import dash
from dash import html, dcc, callback, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import Database
from components.auth_check import require_auth

# Register page
dash.register_page(__name__, path='/vendors', name='Vendors', title='Vendors - Island Glass')

# Initialize database
db = Database()

# =====================================================
# VENDOR FORM MODAL
# =====================================================

def create_vendor_form(vendor_id=None, vendor_data=None):
    """Create vendor add/edit form"""

    is_edit = vendor_id is not None

    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Edit Vendor" if is_edit else "Add New Vendor")),
        dbc.ModalBody([
            # Basic Information
            html.H6("Basic Information", className="mb-3 text-primary"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Vendor Name *", className="fw-bold"),
                    dbc.Input(
                        id="vendor-name-input",
                        placeholder="Enter vendor name",
                        value=vendor_data.get('vendor_name', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=8),
                dbc.Col([
                    dbc.Label("Vendor Type *", className="fw-bold"),
                    dbc.Select(
                        id="vendor-type-select",
                        options=[
                            {"label": "Glass", "value": "Glass"},
                            {"label": "Hardware", "value": "Hardware"},
                            {"label": "Materials", "value": "Materials"},
                            {"label": "Services", "value": "Services"},
                            {"label": "Other", "value": "Other"}
                        ],
                        value=vendor_data.get('vendor_type', 'Glass') if vendor_data else 'Glass',
                        className="mb-3"
                    ),
                ], width=4),
            ]),

            # Contact Information
            html.H6("Contact Information", className="mb-3 text-primary"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Contact Person", className="fw-bold"),
                    dbc.Input(
                        id="vendor-contact-input",
                        placeholder="Contact person name",
                        value=vendor_data.get('contact_person', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("Phone", className="fw-bold"),
                    dbc.Input(
                        id="vendor-phone-input",
                        placeholder="(555) 123-4567",
                        value=vendor_data.get('phone', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=6),
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Email", className="fw-bold"),
                    dbc.Input(
                        id="vendor-email-input",
                        type="email",
                        placeholder="vendor@example.com",
                        value=vendor_data.get('email', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=12),
            ]),

            # Address
            html.H6("Address", className="mb-3 text-primary"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Address Line 1", className="fw-bold"),
                    dbc.Input(
                        id="vendor-address1-input",
                        placeholder="Street address",
                        value=vendor_data.get('address_line1', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=12),
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Address Line 2", className="fw-bold"),
                    dbc.Input(
                        id="vendor-address2-input",
                        placeholder="Suite, unit, building, floor, etc.",
                        value=vendor_data.get('address_line2', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=12),
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Label("City", className="fw-bold"),
                    dbc.Input(
                        id="vendor-city-input",
                        placeholder="City",
                        value=vendor_data.get('city', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=4),
                dbc.Col([
                    dbc.Label("State", className="fw-bold"),
                    dbc.Input(
                        id="vendor-state-input",
                        placeholder="State",
                        value=vendor_data.get('state', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=4),
                dbc.Col([
                    dbc.Label("ZIP Code", className="fw-bold"),
                    dbc.Input(
                        id="vendor-zip-input",
                        placeholder="ZIP",
                        value=vendor_data.get('zip_code', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=4),
            ]),

            # Payment & Terms
            html.H6("Payment Terms & Information", className="mb-3 text-primary"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Payment Terms", className="fw-bold"),
                    dbc.Select(
                        id="vendor-payment-terms-select",
                        options=[
                            {"label": "Net 30", "value": "Net 30"},
                            {"label": "Net 60", "value": "Net 60"},
                            {"label": "Due on Receipt", "value": "Due on Receipt"},
                            {"label": "COD", "value": "COD"},
                            {"label": "Prepaid", "value": "Prepaid"},
                        ],
                        value=vendor_data.get('payment_terms', 'Net 30') if vendor_data else 'Net 30',
                        className="mb-3"
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("Account Number", className="fw-bold"),
                    dbc.Input(
                        id="vendor-account-input",
                        placeholder="Your account number with vendor",
                        value=vendor_data.get('account_number', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=6),
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Tax ID", className="fw-bold"),
                    dbc.Input(
                        id="vendor-taxid-input",
                        placeholder="Vendor Tax ID",
                        value=vendor_data.get('tax_id', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=12),
            ]),

            # QuickBooks Integration
            html.H6("QuickBooks Integration", className="mb-3 text-primary"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("QuickBooks Vendor ID", className="fw-bold"),
                    dbc.Input(
                        id="vendor-qb-id-input",
                        placeholder="QuickBooks Vendor ID (optional)",
                        value=vendor_data.get('quickbooks_vendor_id', '') if vendor_data else '',
                        className="mb-3"
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Checklist(
                        id="vendor-qb-sync-check",
                        options=[{"label": " Enable QuickBooks Sync", "value": "enabled"}],
                        value=["enabled"] if (vendor_data and vendor_data.get('quickbooks_sync_enabled')) else [],
                        className="mt-4"
                    ),
                ], width=6),
            ]),

            # Notes
            html.H6("Notes", className="mb-3 text-primary"),
            dbc.Textarea(
                id="vendor-notes-input",
                placeholder="Additional notes about this vendor...",
                value=vendor_data.get('notes', '') if vendor_data else '',
                style={"height": "100px"},
                className="mb-3"
            ),

            # Status
            dbc.Row([
                dbc.Col([
                    dbc.Checklist(
                        id="vendor-active-check",
                        options=[{"label": " Active Vendor", "value": "active"}],
                        value=["active"] if (not vendor_data or vendor_data.get('is_active', True)) else [],
                        className="fw-bold"
                    ),
                ], width=12),
            ]),

            # Store vendor ID for editing
            dcc.Store(id="edit-vendor-id", data=vendor_id),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="vendor-cancel-btn", color="secondary", className="me-2"),
            dbc.Button("Save Vendor", id="vendor-save-btn", color="primary"),
        ]),
    ], id="vendor-modal", size="lg", is_open=False)


# =====================================================
# VENDOR TABLE
# =====================================================

def create_vendor_card(vendor):
    """Create a card for a single vendor"""

    status_badge = dbc.Badge(
        "Active" if vendor['is_active'] else "Inactive",
        color="success" if vendor['is_active'] else "secondary",
        className="me-2"
    )

    qb_badge = dbc.Badge(
        "QB Synced",
        color="info",
        className="me-2"
    ) if vendor['quickbooks_sync_enabled'] else None

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5([
                        vendor['vendor_name'],
                        html.Small(f" ({vendor['vendor_type']})", className="text-muted ms-2")
                    ], className="mb-2"),
                    html.Div([status_badge, qb_badge] if qb_badge else [status_badge]),
                ], width=8),
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Edit", id={"type": "edit-vendor-btn", "index": vendor['vendor_id']},
                                 color="primary", size="sm", outline=True),
                        dbc.Button("Delete", id={"type": "delete-vendor-btn", "index": vendor['vendor_id']},
                                 color="danger", size="sm", outline=True),
                    ], className="float-end")
                ], width=4),
            ]),

            html.Hr(),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="bi bi-person me-2"),
                        html.Strong("Contact: "),
                        vendor['contact_person'] or "N/A"
                    ], className="mb-2") if vendor.get('contact_person') else None,

                    html.Div([
                        html.I(className="bi bi-telephone me-2"),
                        html.Strong("Phone: "),
                        vendor['phone'] or "N/A"
                    ], className="mb-2") if vendor.get('phone') else None,

                    html.Div([
                        html.I(className="bi bi-envelope me-2"),
                        html.Strong("Email: "),
                        html.A(vendor['email'], href=f"mailto:{vendor['email']}")
                    ], className="mb-2") if vendor.get('email') else None,
                ], width=6),

                dbc.Col([
                    html.Div([
                        html.I(className="bi bi-geo-alt me-2"),
                        html.Strong("Address: "),
                        html.Br(),
                        vendor['address_line1'] or "N/A",
                        html.Br() if vendor.get('address_line2') else None,
                        vendor['address_line2'] if vendor.get('address_line2') else None,
                        html.Br() if vendor.get('city') else None,
                        f"{vendor['city']}, {vendor['state']} {vendor['zip_code']}" if vendor.get('city') else None
                    ]) if vendor.get('address_line1') else None,
                ], width=6),
            ]),

            html.Hr() if vendor.get('notes') else None,

            html.Div([
                html.I(className="bi bi-sticky me-2"),
                html.Strong("Notes: "),
                html.Br(),
                vendor['notes']
            ], className="text-muted small") if vendor.get('notes') else None,
        ])
    ], className="mb-3")


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
                    html.I(className="bi bi-building me-3"),
                    "Vendor Management"
                ], className="mb-0"),
            ], width=8),
            dbc.Col([
                dbc.Button(
                    [html.I(className="bi bi-plus-circle me-2"), "Add Vendor"],
                    id="add-vendor-btn",
                    color="primary",
                    className="float-end"
                ),
            ], width=4),
        ], className="mb-4 mt-4"),

        # Filters & Search
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Search", className="fw-bold"),
                        dbc.Input(
                            id="vendor-search-input",
                            placeholder="Search vendors by name, type, or contact...",
                            type="text",
                            debounce=True
                        ),
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Filter by Type", className="fw-bold"),
                        dbc.Select(
                            id="vendor-type-filter",
                            options=[
                                {"label": "All Types", "value": "all"},
                                {"label": "Glass", "value": "Glass"},
                                {"label": "Hardware", "value": "Hardware"},
                                {"label": "Materials", "value": "Materials"},
                                {"label": "Services", "value": "Services"},
                                {"label": "Other", "value": "Other"}
                            ],
                            value="all"
                        ),
                    ], width=3),
                    dbc.Col([
                        dbc.Label("Status", className="fw-bold"),
                        dbc.Select(
                            id="vendor-status-filter",
                            options=[
                                {"label": "All Vendors", "value": "all"},
                                {"label": "Active Only", "value": "active"},
                                {"label": "Inactive Only", "value": "inactive"}
                            ],
                            value="active"
                        ),
                    ], width=3),
                ])
            ])
        ], className="mb-4"),

        # Vendor List
        html.Div(id="vendors-list-container"),

        # Vendor Form Modal
        create_vendor_form(),

        # Delete Confirmation Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
            dbc.ModalBody([
                html.P("Are you sure you want to delete this vendor?"),
                html.P("This action cannot be undone.", className="text-danger fw-bold"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="delete-vendor-cancel-btn", color="secondary", className="me-2"),
                dbc.Button("Delete", id="delete-vendor-confirm-btn", color="danger"),
            ]),
        ], id="delete-vendor-modal", is_open=False),

        # Store for delete vendor ID
        dcc.Store(id="delete-vendor-id", data=None),

        # Toast for notifications
        html.Div(id="vendor-toast-container", style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999}),

    ], fluid=True, className="pb-5")
])


# =====================================================
# CALLBACKS
# =====================================================

@callback(
    Output("vendors-list-container", "children"),
    Input("vendor-search-input", "value"),
    Input("vendor-type-filter", "value"),
    Input("vendor-status-filter", "value"),
    Input("vendor-modal", "is_open"),  # Reload after modal closes
    Input("delete-vendor-modal", "is_open"),  # Reload after delete
)
def load_vendors(search_term, vendor_type, status_filter, modal_open, delete_modal_open):
    """Load and filter vendors"""

    try:
        # Build query
        query = """
            SELECT
                vendor_id, vendor_name, vendor_type, contact_person, email, phone,
                address_line1, address_line2, city, state, zip_code,
                payment_terms, account_number, tax_id,
                quickbooks_vendor_id, quickbooks_sync_enabled,
                is_active, notes, created_at
            FROM vendors
            WHERE 1=1
        """
        params = []

        # Status filter
        if status_filter == "active":
            query += " AND is_active = TRUE"
        elif status_filter == "inactive":
            query += " AND is_active = FALSE"

        # Type filter
        if vendor_type != "all":
            query += " AND vendor_type = %s"
            params.append(vendor_type)

        # Search filter
        if search_term:
            query += """ AND (
                LOWER(vendor_name) LIKE LOWER(%s) OR
                LOWER(vendor_type) LIKE LOWER(%s) OR
                LOWER(contact_person) LIKE LOWER(%s) OR
                LOWER(email) LIKE LOWER(%s)
            )"""
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern] * 4)

        query += " ORDER BY vendor_name ASC"

        vendors = db.fetch_all(query, tuple(params))

        if not vendors:
            return dbc.Alert(
                [
                    html.I(className="bi bi-info-circle me-2"),
                    "No vendors found. Click 'Add Vendor' to create your first vendor."
                ],
                color="info",
                className="mt-4"
            )

        # Create vendor cards
        vendor_cards = [create_vendor_card(vendor) for vendor in vendors]

        return html.Div([
            dbc.Alert(
                f"Showing {len(vendors)} vendor{'s' if len(vendors) != 1 else ''}",
                color="light",
                className="mb-3"
            ),
            html.Div(vendor_cards)
        ])

    except Exception as e:
        return dbc.Alert(f"Error loading vendors: {str(e)}", color="danger")


@callback(
    Output("vendor-modal", "is_open"),
    Output("vendor-name-input", "value"),
    Output("vendor-type-select", "value"),
    Output("vendor-contact-input", "value"),
    Output("vendor-phone-input", "value"),
    Output("vendor-email-input", "value"),
    Output("vendor-address1-input", "value"),
    Output("vendor-address2-input", "value"),
    Output("vendor-city-input", "value"),
    Output("vendor-state-input", "value"),
    Output("vendor-zip-input", "value"),
    Output("vendor-payment-terms-select", "value"),
    Output("vendor-account-input", "value"),
    Output("vendor-taxid-input", "value"),
    Output("vendor-qb-id-input", "value"),
    Output("vendor-qb-sync-check", "value"),
    Output("vendor-notes-input", "value"),
    Output("vendor-active-check", "value"),
    Output("edit-vendor-id", "data"),
    Input("add-vendor-btn", "n_clicks"),
    Input({"type": "edit-vendor-btn", "index": ALL}, "n_clicks"),
    Input("vendor-cancel-btn", "n_clicks"),
    State("vendor-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_vendor_modal(add_clicks, edit_clicks, cancel_clicks, is_open):
    """Open/close vendor modal and populate for editing"""

    triggered_id = ctx.triggered_id

    # Cancel button closes modal
    if triggered_id == "vendor-cancel-btn":
        return [False] + [""] * 16 + [None]

    # Add button opens empty modal
    if triggered_id == "add-vendor-btn":
        return [True, "", "Glass", "", "", "", "", "", "", "", "", "Net 30", "", "", "", [], "", ["active"], None]

    # Edit button opens populated modal
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "edit-vendor-btn":
        vendor_id = triggered_id["index"]

        # Fetch vendor data
        vendor = db.fetch_one(
            "SELECT * FROM vendors WHERE vendor_id = %s",
            (vendor_id,)
        )

        if vendor:
            return [
                True,
                vendor['vendor_name'],
                vendor['vendor_type'],
                vendor['contact_person'] or "",
                vendor['phone'] or "",
                vendor['email'] or "",
                vendor['address_line1'] or "",
                vendor['address_line2'] or "",
                vendor['city'] or "",
                vendor['state'] or "",
                vendor['zip_code'] or "",
                vendor['payment_terms'] or "Net 30",
                vendor['account_number'] or "",
                vendor['tax_id'] or "",
                vendor['quickbooks_vendor_id'] or "",
                ["enabled"] if vendor['quickbooks_sync_enabled'] else [],
                vendor['notes'] or "",
                ["active"] if vendor['is_active'] else [],
                vendor_id
            ]

    return [is_open] + [""] * 16 + [None]


@callback(
    Output("vendor-toast-container", "children"),
    Input("vendor-save-btn", "n_clicks"),
    State("vendor-name-input", "value"),
    State("vendor-type-select", "value"),
    State("vendor-contact-input", "value"),
    State("vendor-phone-input", "value"),
    State("vendor-email-input", "value"),
    State("vendor-address1-input", "value"),
    State("vendor-address2-input", "value"),
    State("vendor-city-input", "value"),
    State("vendor-state-input", "value"),
    State("vendor-zip-input", "value"),
    State("vendor-payment-terms-select", "value"),
    State("vendor-account-input", "value"),
    State("vendor-taxid-input", "value"),
    State("vendor-qb-id-input", "value"),
    State("vendor-qb-sync-check", "value"),
    State("vendor-notes-input", "value"),
    State("vendor-active-check", "value"),
    State("edit-vendor-id", "data"),
    prevent_initial_call=True
)
def save_vendor(n_clicks, name, vendor_type, contact, phone, email, addr1, addr2,
                city, state, zip_code, payment_terms, account_num, tax_id, qb_id,
                qb_sync, notes, is_active, vendor_id):
    """Save or update vendor"""

    if not n_clicks:
        return None

    # Validation
    if not name or not vendor_type:
        return dbc.Toast(
            "Please fill in all required fields (Vendor Name and Type)",
            header="Validation Error",
            icon="danger",
            duration=4000,
            is_open=True
        )

    try:
        if vendor_id:
            # Update existing vendor
            db.execute_query("""
                UPDATE vendors SET
                    vendor_name = %s,
                    vendor_type = %s,
                    contact_person = %s,
                    phone = %s,
                    email = %s,
                    address_line1 = %s,
                    address_line2 = %s,
                    city = %s,
                    state = %s,
                    zip_code = %s,
                    payment_terms = %s,
                    account_number = %s,
                    tax_id = %s,
                    quickbooks_vendor_id = %s,
                    quickbooks_sync_enabled = %s,
                    notes = %s,
                    is_active = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE vendor_id = %s
            """, (name, vendor_type, contact, phone, email, addr1, addr2, city, state, zip_code,
                  payment_terms, account_num, tax_id, qb_id or None, "enabled" in qb_sync, notes,
                  "active" in is_active, vendor_id))

            message = f"Vendor '{name}' updated successfully!"
        else:
            # Insert new vendor
            db.execute_query("""
                INSERT INTO vendors (
                    vendor_name, vendor_type, contact_person, phone, email,
                    address_line1, address_line2, city, state, zip_code,
                    payment_terms, account_number, tax_id,
                    quickbooks_vendor_id, quickbooks_sync_enabled,
                    notes, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, vendor_type, contact, phone, email, addr1, addr2, city, state, zip_code,
                  payment_terms, account_num, tax_id, qb_id or None, "enabled" in qb_sync,
                  notes, "active" in is_active))

            message = f"Vendor '{name}' added successfully!"

        return dbc.Toast(
            message,
            header="Success",
            icon="success",
            duration=4000,
            is_open=True
        )

    except Exception as e:
        return dbc.Toast(
            f"Error saving vendor: {str(e)}",
            header="Error",
            icon="danger",
            duration=4000,
            is_open=True
        )


@callback(
    Output("delete-vendor-modal", "is_open"),
    Output("delete-vendor-id", "data"),
    Input({"type": "delete-vendor-btn", "index": ALL}, "n_clicks"),
    Input("delete-vendor-cancel-btn", "n_clicks"),
    Input("delete-vendor-confirm-btn", "n_clicks"),
    State("delete-vendor-id", "data"),
    prevent_initial_call=True
)
def handle_vendor_delete(delete_clicks, cancel_clicks, confirm_clicks, stored_vendor_id):
    """Handle vendor deletion"""

    triggered_id = ctx.triggered_id

    # Open delete confirmation modal
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "delete-vendor-btn":
        vendor_id = triggered_id["index"]
        return True, vendor_id

    # Cancel deletion
    if triggered_id == "delete-vendor-cancel-btn":
        return False, None

    # Confirm deletion
    if triggered_id == "delete-vendor-confirm-btn" and stored_vendor_id:
        try:
            db.execute_query(
                "DELETE FROM vendors WHERE vendor_id = %s",
                (stored_vendor_id,)
            )
            return False, None
        except Exception as e:
            print(f"Error deleting vendor: {e}")
            return False, None

    return False, None
