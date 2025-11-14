"""
Purchase Orders Page
Manage and track all purchase orders across clients

Features:
- View all purchase orders in a table/list view
- Filter by client, status, date range
- Search by PO number or project name
- Create new purchase orders
- Edit and update existing POs
- Track PO status and activities
"""

import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, MATCH, ALL, ctx
from dash_iconify import DashIconify
from modules.database import get_authenticated_db

# Purchase Orders Layout
layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Stack([
            dmc.Title("Purchase Orders", order=1),
            dmc.Text("Track and manage all purchase orders", c="dimmed", size="sm")
        ], gap=0),
        dmc.Button(
            "Create Purchase Order",
            id="create-po-button",
            leftSection=DashIconify(icon="solar:add-circle-bold", width=20),
            color="blue"
        )
    ], justify="space-between"),

    dmc.Space(h=10),

    # Filters and Search
    dmc.Card([
        dmc.Grid([
            dmc.GridCol([
                dmc.TextInput(
                    id="po-search-input",
                    placeholder="Search by PO number or project name...",
                    leftSection=DashIconify(icon="solar:magnifer-bold", width=20),
                )
            ], span=4),

            dmc.GridCol([
                dmc.Select(
                    id="po-client-filter",
                    placeholder="Filter by client",
                    data=[],  # Will be populated dynamically
                    clearable=True,
                    searchable=True
                )
            ], span=3),

            dmc.GridCol([
                dmc.Select(
                    id="po-status-filter",
                    placeholder="Filter by status",
                    data=[
                        {"value": "active", "label": "Active"},
                        {"value": "completed", "label": "Completed"},
                        {"value": "cancelled", "label": "Cancelled"},
                        {"value": "on_hold", "label": "On Hold"}
                    ],
                    clearable=True
                )
            ], span=3),

            dmc.GridCol([
                dmc.Button(
                    "Clear Filters",
                    id="clear-po-filters",
                    variant="subtle",
                    color="gray",
                    fullWidth=True
                )
            ], span=2),
        ])
    ], withBorder=True, p="md"),

    # Results Container
    html.Div(id="purchase-orders-container"),

    # Create Purchase Order Modal
    dmc.Modal(
        id="create-po-modal",
        title="Create Purchase Order",
        size="lg",
        children=[
            dmc.Stack([
                dmc.Select(
                    id="create-po-client",
                    label="Client",
                    placeholder="Select client",
                    data=[],  # Will be populated dynamically
                    required=True,
                    searchable=True,
                    description="Choose the client for this purchase order"
                ),
                dmc.TextInput(
                    id="create-po-number",
                    label="PO Number",
                    placeholder="Enter PO number",
                    required=True,
                    description="Must be unique"
                ),
                dmc.TextInput(
                    id="create-po-project-name",
                    label="Project Name",
                    placeholder="Enter project name (optional)"
                ),
                dmc.DateInput(
                    id="create-po-date",
                    label="PO Date",
                    valueFormat="YYYY-MM-DD",
                    clearable=False,
                    description="Purchase order date"
                ),
                dmc.NumberInput(
                    id="create-po-amount",
                    label="Total Amount",
                    placeholder="Enter amount (optional)",
                    prefix="$",
                    decimalScale=2,
                    required=False,
                    min=0,
                    description="Can be added later"
                ),
                dmc.Select(
                    id="create-po-status",
                    label="Status",
                    data=[
                        {"value": "active", "label": "Active"},
                        {"value": "completed", "label": "Completed"},
                        {"value": "cancelled", "label": "Cancelled"},
                        {"value": "on_hold", "label": "On Hold"}
                    ],
                    value="active",
                    required=True
                ),
                dmc.Textarea(
                    id="create-po-notes",
                    label="Notes",
                    placeholder="Enter notes (optional)",
                    minRows=3
                ),
                dmc.Group([
                    dmc.Button(
                        "Cancel",
                        id="cancel-create-po",
                        variant="subtle",
                        color="gray"
                    ),
                    dmc.Button(
                        "Create Purchase Order",
                        id="submit-create-po",
                        color="blue"
                    )
                ], justify="flex-end", mt="md")
            ], gap="sm")
        ]
    ),

    # Edit Purchase Order Modal
    dmc.Modal(
        id="edit-po-modal",
        title="Edit Purchase Order",
        size="lg",
        children=[
            dmc.Stack([
                dmc.TextInput(
                    id="edit-po-number",
                    label="PO Number",
                    placeholder="Enter PO number",
                    required=True,
                    description="Must be unique"
                ),
                dmc.TextInput(
                    id="edit-po-project-name",
                    label="Project Name",
                    placeholder="Enter project name (optional)"
                ),
                dmc.DateInput(
                    id="edit-po-date",
                    label="PO Date",
                    valueFormat="YYYY-MM-DD",
                    clearable=False
                ),
                dmc.NumberInput(
                    id="edit-po-amount",
                    label="Total Amount",
                    placeholder="Enter amount (optional)",
                    prefix="$",
                    decimalScale=2,
                    required=False,
                    min=0,
                    description="Can be added later"
                ),
                dmc.Select(
                    id="edit-po-status",
                    label="Status",
                    data=[
                        {"value": "active", "label": "Active"},
                        {"value": "completed", "label": "Completed"},
                        {"value": "cancelled", "label": "Cancelled"},
                        {"value": "on_hold", "label": "On Hold"}
                    ],
                    required=True
                ),
                dmc.Textarea(
                    id="edit-po-notes",
                    label="Notes",
                    placeholder="Enter notes (optional)",
                    minRows=3
                ),
                dmc.Group([
                    dmc.Button(
                        "Cancel",
                        id="cancel-edit-po",
                        variant="subtle",
                        color="gray"
                    ),
                    dmc.Button(
                        "Save Changes",
                        id="submit-edit-po",
                        color="blue"
                    )
                ], justify="flex-end", mt="md")
            ], gap="sm")
        ]
    ),

    # Delete Confirmation Modal
    dmc.Modal(
        id="delete-po-modal",
        title="Confirm Delete",
        size="sm",
        children=[
            dmc.Stack([
                dmc.Text("Are you sure you want to delete this purchase order?"),
                dmc.Text("This action cannot be undone.", c="dimmed", size="sm"),
                dmc.Group([
                    dmc.Button(
                        "Cancel",
                        id="cancel-delete-po",
                        variant="subtle",
                        color="gray"
                    ),
                    dmc.Button(
                        "Delete",
                        id="confirm-delete-po",
                        color="red"
                    )
                ], justify="flex-end", mt="md")
            ], gap="sm")
        ]
    ),

    # Store for selected PO ID (for edit/delete)
    dcc.Store(id="selected-po-id", data=None),

    # Notification container
    html.Div(id="po-page-notification-container")

], gap="md")


# Callback to load and display purchase orders
@callback(
    Output("purchase-orders-container", "children"),
    Output("po-client-filter", "data"),
    Input("po-search-input", "value"),
    Input("po-client-filter", "value"),
    Input("po-status-filter", "value"),
    Input("clear-po-filters", "n_clicks"),
    State("session-store", "data"),
    prevent_initial_call=False
)
def load_purchase_orders(search_term, client_filter, status_filter, clear_clicks, session_data):
    """Load and filter purchase orders"""

    # Check if clear button was clicked
    if ctx.triggered_id == "clear-po-filters":
        search_term = None
        client_filter = None
        status_filter = None

    # Get authenticated database
    db = get_authenticated_db(session_data)

    # Get all purchase orders
    if client_filter:
        purchase_orders = db.get_purchase_orders_by_client(client_filter)
    else:
        # Get all POs (we'll need to add this method to database.py)
        purchase_orders = []
        clients = db.get_all_po_clients()
        for client in clients:
            pos = db.get_purchase_orders_by_client(client['id'])
            purchase_orders.extend(pos)

    # Apply filters
    if search_term:
        search_lower = search_term.lower()
        purchase_orders = [
            po for po in purchase_orders
            if search_lower in po.get('po_number', '').lower() or
               search_lower in po.get('project_name', '').lower()
        ]

    if status_filter:
        purchase_orders = [po for po in purchase_orders if po.get('status') == status_filter]

    # Get unique clients for filter dropdown
    clients = db.get_all_po_clients()
    client_options = [{"value": str(c['id']), "label": c.get('client_name', 'Unknown')} for c in clients]

    return render_purchase_orders_table(purchase_orders, db), client_options


def render_purchase_orders_table(purchase_orders, db):
    """Render purchase orders in a table format"""

    if not purchase_orders:
        return dmc.Card([
            dmc.Center([
                dmc.Stack([
                    DashIconify(icon="solar:document-text-bold", width=64, color="#868e96"),
                    dmc.Text("No purchase orders found", size="lg", c="dimmed"),
                    dmc.Text("Create a purchase order to get started", size="sm", c="dimmed")
                ], align="center", gap="xs")
            ], style={"padding": "60px 0"})
        ], withBorder=True)

    # Status colors
    status_colors = {
        'active': 'blue',
        'completed': 'green',
        'cancelled': 'red',
        'on_hold': 'orange'
    }

    # Create table rows
    rows = []
    for po in purchase_orders:
        po_id = po.get('id')
        po_number = po.get('po_number', 'N/A')
        project_name = po.get('project_name', 'N/A')
        client_id = po.get('client_id')

        # Get client name
        client = db.get_po_client_by_id(client_id) if client_id else None
        client_name = client.get('client_name', 'Unknown') if client else 'Unknown'

        po_date = po.get('po_date', 'N/A')
        total_amount = po.get('total_amount', 0)
        status = po.get('status', 'active')
        status_color = status_colors.get(status, 'gray')

        rows.append(
            html.Tr([
                html.Td(
                    dmc.Group([
                        DashIconify(icon="solar:document-text-bold", width=18, color="#228be6"),
                        dmc.Text(po_number, fw=600, size="sm")
                    ], gap=8)
                ),
                html.Td(dmc.Text(project_name, size="sm")),
                html.Td(dmc.Text(client_name, size="sm")),
                html.Td(dmc.Text(po_date, size="sm")),
                html.Td(dmc.Text(f"${total_amount:,.2f}" if total_amount else "$0.00", size="sm")),
                html.Td(
                    dmc.Badge(
                        status.replace('_', ' ').title(),
                        color=status_color,
                        variant="light"
                    )
                ),
                html.Td(
                    dmc.Group([
                        dmc.ActionIcon(
                            DashIconify(icon="solar:eye-bold", width=18),
                            id={'type': 'view-po-btn', 'index': po_id},
                            variant="light",
                            color="blue",
                            size="lg"
                        ),
                        dmc.ActionIcon(
                            DashIconify(icon="solar:pen-bold", width=18),
                            id={'type': 'edit-po-btn', 'index': po_id},
                            variant="light",
                            color="blue",
                            size="lg"
                        ),
                        dmc.ActionIcon(
                            DashIconify(icon="solar:trash-bin-trash-bold", width=18),
                            id={'type': 'delete-po-btn', 'index': po_id},
                            variant="light",
                            color="red",
                            size="lg"
                        )
                    ], gap=5)
                )
            ])
        )

    return dmc.Stack([
        dmc.Text(f"Showing {len(purchase_orders)} purchase order(s)", size="sm", c="dimmed"),

        dmc.Card([
            dmc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("PO Number"),
                        html.Th("Project Name"),
                        html.Th("Client"),
                        html.Th("Date"),
                        html.Th("Amount"),
                        html.Th("Status"),
                        html.Th("Actions")
                    ])
                ]),
                html.Tbody(rows)
            ], striped=True, highlightOnHover=True, withTableBorder=True, withColumnBorders=True)
        ], withBorder=True, p="md")
    ], gap="sm")


# Callback to open/close create PO modal and populate client dropdown
@callback(
    Output("create-po-modal", "opened"),
    Output("create-po-client", "data"),
    Input("create-po-button", "n_clicks"),
    Input("cancel-create-po", "n_clicks"),
    State("create-po-modal", "opened"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def toggle_create_po_modal(open_clicks, cancel_clicks, is_opened, session_data):
    """Toggle create purchase order modal and populate client list"""
    triggered_id = ctx.triggered_id

    if triggered_id == "create-po-button":
        # Get client list for dropdown
        db = get_authenticated_db(session_data)
        clients = db.get_all_po_clients()
        client_options = [{"value": str(c['id']), "label": c.get('client_name', 'Unknown')} for c in clients]
        return True, client_options
    elif triggered_id == "cancel-create-po":
        return False, dash.no_update

    return is_opened, dash.no_update


# Callback to set default date for new PO
@callback(
    Output("create-po-date", "value"),
    Input("create-po-modal", "opened"),
    prevent_initial_call=True
)
def set_default_create_po_date(opened):
    """Set today's date as default when modal opens"""
    if opened:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    return dash.no_update


# Callback to submit new purchase order from PO page
@callback(
    [
        Output("create-po-modal", "opened", allow_duplicate=True),
        Output("purchase-orders-container", "children", allow_duplicate=True),
        Output("po-page-notification-container", "children"),
        Output("create-po-client", "value"),
        Output("create-po-number", "value"),
        Output("create-po-project-name", "value"),
        Output("create-po-amount", "value"),
        Output("create-po-notes", "value"),
    ],
    Input("submit-create-po", "n_clicks"),
    [
        State("create-po-client", "value"),
        State("create-po-number", "value"),
        State("create-po-project-name", "value"),
        State("create-po-date", "value"),
        State("create-po-amount", "value"),
        State("create-po-status", "value"),
        State("create-po-notes", "value"),
        State("session-store", "data")
    ],
    prevent_initial_call=True
)
def submit_create_purchase_order(n_clicks, client_id, po_number, project_name, po_date,
                                  amount, status, notes, session_data):
    """Submit new purchase order from the PO page"""
    print(f"DEBUG submit_create_purchase_order called: n_clicks={n_clicks}, client_id={client_id}, po_number={po_number}")

    if not n_clicks:
        print("DEBUG: No clicks, returning no_update")
        return dash.no_update

    # Validate required fields
    if not po_number or not client_id:
        print(f"DEBUG: Validation failed - po_number={po_number}, client_id={client_id}")
        notification = dmc.Notification(
            title="Error",
            message="Client and PO Number are required",
            color="red",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="solar:close-circle-bold")
        )
        return dash.no_update, dash.no_update, notification, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    try:
        # Get authenticated database connection
        db = get_authenticated_db(session_data)
        user_id = session_data.get('session', {}).get('user', {}).get('id') if session_data else None

        if not user_id:
            notification = dmc.Notification(
                title="Error",
                message="User session expired. Please log in again.",
                color="red",
                action="show",
                autoClose=5000,
                icon=DashIconify(icon="solar:close-circle-bold")
            )
            return dash.no_update, dash.no_update, notification, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        # Create PO data
        po_data = {
            'client_id': int(client_id),
            'po_number': po_number,
            'project_name': project_name,
            'po_date': po_date,
            'total_amount': amount,
            'status': status,
            'notes': notes
        }

        # Insert purchase order
        result = db.insert_purchase_order(po_data, user_id)

        if result:
            # Success - close modal and refresh PO list
            notification = dmc.Notification(
                title="Success",
                message=f"Purchase Order {po_number} created successfully",
                color="green",
                action="show",
                autoClose=3000,
                icon=DashIconify(icon="solar:check-circle-bold")
            )

            # Refresh purchase orders list
            purchase_orders = []
            clients = db.get_all_po_clients()
            for client in clients:
                pos = db.get_purchase_orders_by_client(client['id'])
                purchase_orders.extend(pos)

            updated_content = render_purchase_orders_table(purchase_orders, db)

            # Clear form and close modal
            return False, updated_content, notification, None, "", "", None, ""
        else:
            notification = dmc.Notification(
                title="Error",
                message="Failed to create purchase order. PO number might already exist.",
                color="red",
                action="show",
                autoClose=5000,
                icon=DashIconify(icon="solar:close-circle-bold")
            )
            return dash.no_update, dash.no_update, notification, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    except Exception as e:
        print(f"Error creating purchase order: {e}")
        notification = dmc.Notification(
            title="Error",
            message=f"An error occurred: {str(e)}",
            color="red",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="solar:close-circle-bold")
        )
        return dash.no_update, dash.no_update, notification, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


# Callback to open edit modal and load PO data
@callback(
    Output("edit-po-modal", "opened"),
    Output("selected-po-id", "data"),
    Output("edit-po-number", "value"),
    Output("edit-po-project-name", "value"),
    Output("edit-po-date", "value"),
    Output("edit-po-amount", "value"),
    Output("edit-po-status", "value"),
    Output("edit-po-notes", "value"),
    Input({'type': 'edit-po-btn', 'index': ALL}, "n_clicks"),
    Input("cancel-edit-po", "n_clicks"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def toggle_edit_po_modal(edit_clicks, cancel_click, session_data):
    """Open edit modal and load PO data"""
    triggered_id = ctx.triggered_id

    # Cancel button clicked
    if triggered_id == "cancel-edit-po":
        return False, None, "", "", None, None, "active", ""

    # Edit button clicked
    if triggered_id and isinstance(triggered_id, dict) and triggered_id.get('type') == 'edit-po-btn':
        po_id = triggered_id.get('index')

        # Get PO data
        db = get_authenticated_db(session_data)
        po = db.get_purchase_order_by_id(po_id)

        if po:
            return (
                True,
                po_id,
                po.get('po_number', ''),
                po.get('project_name', ''),
                po.get('po_date', ''),
                po.get('total_amount', 0),
                po.get('status', 'active'),
                po.get('notes', '')
            )

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


# Callback to submit edited PO
@callback(
    [
        Output("edit-po-modal", "opened", allow_duplicate=True),
        Output("purchase-orders-container", "children", allow_duplicate=True),
        Output("po-page-notification-container", "children", allow_duplicate=True),
    ],
    Input("submit-edit-po", "n_clicks"),
    [
        State("selected-po-id", "data"),
        State("edit-po-number", "value"),
        State("edit-po-project-name", "value"),
        State("edit-po-date", "value"),
        State("edit-po-amount", "value"),
        State("edit-po-status", "value"),
        State("edit-po-notes", "value"),
        State("session-store", "data")
    ],
    prevent_initial_call=True
)
def submit_edit_purchase_order(n_clicks, po_id, po_number, project_name, po_date,
                                amount, status, notes, session_data):
    """Submit edited purchase order"""
    if not n_clicks or not po_id:
        return dash.no_update

    # Validate required fields
    if not po_number:
        notification = dmc.Notification(
            title="Error",
            message="PO Number is required",
            color="red",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="solar:close-circle-bold")
        )
        return dash.no_update, dash.no_update, notification

    try:
        # Get authenticated database connection
        db = get_authenticated_db(session_data)
        user_id = session_data.get('session', {}).get('user', {}).get('id') if session_data else None

        if not user_id:
            notification = dmc.Notification(
                title="Error",
                message="User session expired. Please log in again.",
                color="red",
                action="show",
                autoClose=5000,
                icon=DashIconify(icon="solar:close-circle-bold")
            )
            return dash.no_update, dash.no_update, notification

        # Update PO data
        po_data = {
            'po_number': po_number,
            'project_name': project_name,
            'po_date': po_date,
            'total_amount': amount,
            'status': status,
            'notes': notes
        }

        # Update purchase order
        success = db.update_purchase_order(po_id, po_data, user_id)

        if success:
            # Success - close modal and refresh PO list
            notification = dmc.Notification(
                title="Success",
                message=f"Purchase Order {po_number} updated successfully",
                color="green",
                action="show",
                autoClose=3000,
                icon=DashIconify(icon="solar:check-circle-bold")
            )

            # Refresh purchase orders list
            purchase_orders = []
            clients = db.get_all_po_clients()
            for client in clients:
                pos = db.get_purchase_orders_by_client(client['id'])
                purchase_orders.extend(pos)

            updated_content = render_purchase_orders_table(purchase_orders, db)

            return False, updated_content, notification
        else:
            notification = dmc.Notification(
                title="Error",
                message="Failed to update purchase order",
                color="red",
                action="show",
                autoClose=5000,
                icon=DashIconify(icon="solar:close-circle-bold")
            )
            return dash.no_update, dash.no_update, notification

    except Exception as e:
        print(f"Error updating purchase order: {e}")
        notification = dmc.Notification(
            title="Error",
            message=f"An error occurred: {str(e)}",
            color="red",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="solar:close-circle-bold")
        )
        return dash.no_update, dash.no_update, notification


# Callback to open delete confirmation modal
@callback(
    Output("delete-po-modal", "opened"),
    Output("selected-po-id", "data", allow_duplicate=True),
    Input({'type': 'delete-po-btn', 'index': ALL}, "n_clicks"),
    Input("cancel-delete-po", "n_clicks"),
    prevent_initial_call=True
)
def toggle_delete_po_modal(delete_clicks, cancel_click):
    """Toggle delete confirmation modal"""
    triggered_id = ctx.triggered_id

    # Cancel button clicked
    if triggered_id == "cancel-delete-po":
        return False, None

    # Delete button clicked
    if triggered_id and isinstance(triggered_id, dict) and triggered_id.get('type') == 'delete-po-btn':
        # Check if any button was actually clicked (n_clicks > 0)
        # This prevents the modal from opening on initial page load
        if delete_clicks and any(clicks for clicks in delete_clicks if clicks):
            po_id = triggered_id.get('index')
            return True, po_id

    return dash.no_update, dash.no_update


# Callback to confirm delete PO
@callback(
    [
        Output("delete-po-modal", "opened", allow_duplicate=True),
        Output("purchase-orders-container", "children", allow_duplicate=True),
        Output("po-page-notification-container", "children", allow_duplicate=True),
    ],
    Input("confirm-delete-po", "n_clicks"),
    [
        State("selected-po-id", "data"),
        State("session-store", "data")
    ],
    prevent_initial_call=True
)
def confirm_delete_purchase_order(n_clicks, po_id, session_data):
    """Confirm and delete purchase order"""
    if not n_clicks or not po_id:
        return dash.no_update

    try:
        # Get authenticated database connection
        db = get_authenticated_db(session_data)
        user_id = session_data.get('session', {}).get('user', {}).get('id') if session_data else None

        if not user_id:
            notification = dmc.Notification(
                title="Error",
                message="User session expired. Please log in again.",
                color="red",
                action="show",
                autoClose=5000,
                icon=DashIconify(icon="solar:close-circle-bold")
            )
            return dash.no_update, dash.no_update, notification

        # Get PO number for notification
        po = db.get_purchase_order_by_id(po_id)
        po_number = po.get('po_number', 'Unknown') if po else 'Unknown'

        # Delete purchase order
        success = db.delete_purchase_order(po_id, user_id)

        if success:
            # Success - close modal and refresh PO list
            notification = dmc.Notification(
                title="Success",
                message=f"Purchase Order {po_number} deleted successfully",
                color="green",
                action="show",
                autoClose=3000,
                icon=DashIconify(icon="solar:check-circle-bold")
            )

            # Refresh purchase orders list
            purchase_orders = []
            clients = db.get_all_po_clients()
            for client in clients:
                pos = db.get_purchase_orders_by_client(client['id'])
                purchase_orders.extend(pos)

            updated_content = render_purchase_orders_table(purchase_orders, db)

            return False, updated_content, notification
        else:
            notification = dmc.Notification(
                title="Error",
                message="Failed to delete purchase order",
                color="red",
                action="show",
                autoClose=5000,
                icon=DashIconify(icon="solar:close-circle-bold")
            )
            return dash.no_update, dash.no_update, notification

    except Exception as e:
        print(f"Error deleting purchase order: {e}")
        notification = dmc.Notification(
            title="Error",
            message=f"An error occurred: {str(e)}",
            color="red",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="solar:close-circle-bold")
        )
        return dash.no_update, dash.no_update, notification
