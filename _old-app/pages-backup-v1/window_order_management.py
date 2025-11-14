"""
Window Order Management Page
View, filter, and manage window orders

Features:
- View all orders in table/card layout
- Filter by date, PO, status, window type
- Expandable details showing window items
- Status update dropdown
- View labels button
"""

import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, ALL, MATCH, ctx
from dash_iconify import DashIconify
from datetime import datetime, timedelta
from modules.database import get_authenticated_db
from modules.permissions import get_user_window_permissions
from modules.fraction_utils import format_fraction
from fractions import Fraction

# Order status options
ORDER_STATUSES = ["pending", "in_production", "completed", "shipped", "cancelled"]

STATUS_COLORS = {
    "pending": "yellow",
    "in_production": "blue",
    "completed": "green",
    "shipped": "teal",
    "cancelled": "red"
}

STATUS_ICONS = {
    "pending": "mdi:clock-outline",
    "in_production": "mdi:hammer-wrench",
    "completed": "mdi:check-circle",
    "shipped": "mdi:truck-delivery",
    "cancelled": "mdi:close-circle"
}

def layout(session_data=None):
    """Page layout for order management"""

    if not session_data:
        return html.Div([
            dmc.Alert(
                "Please log in to access this page",
                title="Authentication Required",
                color="red"
            )
        ])

    user_profile = session_data.get('user_profile', {})
    perms = get_user_window_permissions(user_profile)

    if not perms.can_view_orders():
        return html.Div([
            dmc.Alert(
                "You don't have permission to view orders",
                title="Access Denied",
                color="red"
            )
        ])

    return dmc.Stack([
        # Store for session data
        dcc.Store(id='wom-session-store', data=session_data),

        # Header
        dmc.Group([
            dmc.Stack([
                dmc.Title("Window Order Management", order=1),
                dmc.Text("View and manage all window orders", c="dimmed", size="sm")
            ], gap=0),
            dmc.Group([
                dmc.Button(
                    "Refresh",
                    id="wom-refresh-btn",
                    leftSection=DashIconify(icon="mdi:refresh"),
                    variant="light"
                ),
                dmc.Button(
                    "New Order",
                    id="wom-new-order-btn",
                    leftSection=DashIconify(icon="mdi:plus"),
                    variant="filled",
                    color="blue"
                ) if perms.can_create_orders() else None,
            ], gap="xs"),
        ], justify="space-between"),

        dmc.Space(h=10),

        # Filters Card
        dmc.Card([
            dmc.Stack([
                dmc.Text("Filters", size="lg", fw=600),

                dmc.Grid([
                    # Search PO
                    dmc.GridCol([
                        dmc.TextInput(
                            id="wom-filter-po",
                            label="PO Number",
                            placeholder="Search by PO...",
                            leftSection=DashIconify(icon="mdi:magnify")
                        )
                    ], span={"base": 12, "sm": 6, "md": 3}),

                    # Status filter
                    dmc.GridCol([
                        dmc.Select(
                            id="wom-filter-status",
                            label="Status",
                            placeholder="All statuses",
                            data=[
                                {"label": "All", "value": "all"},
                                {"label": "Pending", "value": "pending"},
                                {"label": "In Production", "value": "in_production"},
                                {"label": "Completed", "value": "completed"},
                                {"label": "Shipped", "value": "shipped"},
                                {"label": "Cancelled", "value": "cancelled"},
                            ],
                            value="all",
                            clearable=True
                        )
                    ], span={"base": 12, "sm": 6, "md": 3}),

                    # Date range
                    dmc.GridCol([
                        dmc.DatePicker(
                            id="wom-filter-date-start",
                            label="Start Date",
                            placeholder="From date",
                            clearable=True,
                            valueFormat="YYYY-MM-DD"
                        )
                    ], span={"base": 12, "sm": 6, "md": 3}),

                    dmc.GridCol([
                        dmc.DatePicker(
                            id="wom-filter-date-end",
                            label="End Date",
                            placeholder="To date",
                            clearable=True,
                            valueFormat="YYYY-MM-DD"
                        )
                    ], span={"base": 12, "sm": 6, "md": 3}),
                ], gutter="md"),

                dmc.Group([
                    dmc.Button(
                        "Clear Filters",
                        id="wom-clear-filters-btn",
                        variant="subtle",
                        size="sm"
                    )
                ], justify="flex-end"),
            ], gap="md")
        ], withBorder=True, padding="lg", radius="md", mb="lg"),

        # Orders container
        html.Div(id="wom-orders-container"),

        # Status update modal
        dmc.Modal(
            id="wom-status-modal",
            title="Update Order Status",
            children=[
                dmc.Stack([
                    html.Div(id="wom-status-modal-content"),
                    dmc.Group([
                        dmc.Button("Cancel", id="wom-status-cancel-btn", variant="subtle"),
                        dmc.Button("Update", id="wom-status-update-btn", color="blue"),
                    ], justify="flex-end")
                ])
            ]
        ),

        # Notification container
        html.Div(id="wom-notifications"),
    ], gap="md", p="md")


# Callback: Navigate to new order page
@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("wom-new-order-btn", "n_clicks"),
    prevent_initial_call=True
)
def navigate_to_new_order(n_clicks):
    """Navigate to order entry page"""
    if n_clicks:
        return "/window-order-entry"
    return dash.no_update


# Callback: Load orders
@callback(
    Output("wom-orders-container", "children"),
    Input("wom-refresh-btn", "n_clicks"),
    Input("wom-filter-status", "value"),
    Input("wom-filter-po", "value"),
    Input("wom-filter-date-start", "value"),
    Input("wom-filter-date-end", "value"),
    State("wom-session-store", "data"),
    prevent_initial_call=False
)
def load_orders(n_clicks, status_filter, po_filter, date_start, date_end, session_data):
    """Load and display orders based on filters"""

    if not session_data:
        return dmc.Alert("Session expired. Please log in.", color="red")

    try:
        db = get_authenticated_db(session_data)
        company_id = session_data.get('user_profile', {}).get('company_id')

        if not company_id:
            return dmc.Alert("Company ID not found", color="red")

        # Get orders with filters
        filters = {}
        if status_filter and status_filter != "all":
            filters['status'] = status_filter

        orders = db.get_window_orders(company_id, filters.get('status'))

        if not orders:
            return dmc.Center([
                dmc.Stack([
                    DashIconify(icon="mdi:inbox-outline", width=64, color="gray"),
                    dmc.Text("No orders found", size="lg", c="dimmed"),
                    dmc.Text("Create your first window order to get started", size="sm", c="dimmed"),
                ], align="center")
            ], style={"minHeight": "300px"})

        # Filter by PO number (client-side)
        if po_filter:
            orders = [o for o in orders if po_filter.lower() in o.get('po_number', '').lower()]

        # Filter by date range
        if date_start:
            orders = [o for o in orders if o.get('created_at', '') >= date_start]
        if date_end:
            orders = [o for o in orders if o.get('created_at', '') <= date_end]

        # Build order cards
        order_cards = []
        for order in orders:
            order_card = create_order_card(order, session_data)
            order_cards.append(order_card)

        return dmc.Stack(order_cards, gap="md")

    except Exception as e:
        return dmc.Alert(
            f"Error loading orders: {str(e)}",
            title="Error",
            color="red"
        )


def create_order_card(order, session_data):
    """Create a card for displaying an order"""

    user_profile = session_data.get('user_profile', {})
    perms = get_user_window_permissions(user_profile)

    order_id = order.get('id')
    po_number = order.get('po_number', 'N/A')
    status = order.get('status', 'pending')
    created_at = order.get('created_at', '')
    customer_name = order.get('customer_name', 'Unknown')
    notes = order.get('notes', '')

    # Format date
    try:
        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        formatted_date = created_date.strftime('%b %d, %Y %I:%M %p')
    except:
        formatted_date = created_at

    return dmc.Card([
        dmc.Stack([
            # Header row
            dmc.Group([
                dmc.Group([
                    DashIconify(
                        icon=STATUS_ICONS.get(status, "mdi:file"),
                        width=24,
                        color=STATUS_COLORS.get(status, "gray")
                    ),
                    dmc.Stack([
                        dmc.Text(f"PO: {po_number}", size="lg", fw=600),
                        dmc.Text(customer_name, size="sm", c="dimmed"),
                    ], gap=0),
                ]),
                dmc.Group([
                    dmc.Badge(
                        status.replace('_', ' ').title(),
                        color=STATUS_COLORS.get(status, "gray"),
                        size="lg",
                        variant="light"
                    ),
                    dmc.ActionIcon(
                        DashIconify(icon="mdi:chevron-down", width=20),
                        id={"type": "wom-expand-btn", "index": order_id},
                        variant="subtle",
                        size="lg"
                    ),
                ], gap="xs"),
            ], justify="space-between"),

            # Metadata
            dmc.Group([
                dmc.Group([
                    DashIconify(icon="mdi:calendar", width=16),
                    dmc.Text(formatted_date, size="sm", c="dimmed"),
                ], gap=5),
            ]),

            # Expandable details
            dmc.Collapse(
                id={"type": "wom-order-details", "index": order_id},
                children=[
                    dmc.Divider(my="sm"),
                    html.Div(id={"type": "wom-order-items", "index": order_id}),

                    # Notes
                    dmc.Stack([
                        dmc.Text("Notes:", size="sm", fw=600) if notes else None,
                        dmc.Text(notes, size="sm", c="dimmed") if notes else None,
                    ], gap=5) if notes else None,

                    # Actions
                    dmc.Group([
                        dmc.Button(
                            "View Labels",
                            id={"type": "wom-view-labels-btn", "index": order_id},
                            leftSection=DashIconify(icon="mdi:barcode"),
                            variant="light",
                            size="sm"
                        ),
                        dmc.Button(
                            "Update Status",
                            id={"type": "wom-update-status-btn", "index": order_id},
                            leftSection=DashIconify(icon="mdi:pencil"),
                            variant="light",
                            size="sm",
                            color="blue"
                        ) if perms.can_manage_orders() else None,
                    ], gap="xs", mt="md"),
                ],
                opened=False
            ),
        ], gap="sm")
    ], withBorder=True, padding="lg", radius="md")


# Callback: Toggle order details
@callback(
    Output({"type": "wom-order-details", "index": MATCH}, "opened"),
    Output({"type": "wom-order-items", "index": MATCH}, "children"),
    Input({"type": "wom-expand-btn", "index": MATCH}, "n_clicks"),
    State({"type": "wom-order-details", "index": MATCH}, "opened"),
    State({"type": "wom-expand-btn", "index": MATCH}, "id"),
    State("wom-session-store", "data"),
    prevent_initial_call=True
)
def toggle_order_details(n_clicks, is_opened, btn_id, session_data):
    """Toggle order details and load items if needed"""

    if not n_clicks:
        return dash.no_update, dash.no_update

    order_id = btn_id['index']

    # If closing, just toggle
    if is_opened:
        return False, dash.no_update

    # If opening, load order items
    try:
        db = get_authenticated_db(session_data)
        items = db.get_window_order_items(order_id)

        if not items:
            items_content = dmc.Text("No items found", size="sm", c="dimmed")
        else:
            items_content = create_order_items_table(items)

        return True, items_content

    except Exception as e:
        return True, dmc.Alert(f"Error loading items: {str(e)}", color="red", size="sm")


def create_order_items_table(items):
    """Create a table of window order items"""

    rows = []
    for item in items:
        window_type = item.get('window_type', 'Unknown')
        width = item.get('width')
        height = item.get('height')
        thickness = item.get('thickness')
        quantity = item.get('quantity', 1)

        # Format measurements as fractions
        try:
            width_frac = format_fraction(Fraction(width).limit_denominator(16)) if width else 'N/A'
            height_frac = format_fraction(Fraction(height).limit_denominator(16)) if height else 'N/A'
            thickness_frac = format_fraction(Fraction(thickness).limit_denominator(16)) if thickness else 'N/A'
        except:
            width_frac = str(width) if width else 'N/A'
            height_frac = str(height) if height else 'N/A'
            thickness_frac = str(thickness) if thickness else 'N/A'

        rows.append(
            html.Tr([
                html.Td(window_type),
                html.Td(f'{width_frac}"'),
                html.Td(f'{height_frac}"'),
                html.Td(f'{thickness_frac}"'),
                html.Td(str(quantity)),
            ])
        )

    return dmc.Table([
        html.Thead([
            html.Tr([
                html.Th("Type"),
                html.Th("Width"),
                html.Th("Height"),
                html.Th("Thickness"),
                html.Th("Qty"),
            ])
        ]),
        html.Tbody(rows)
    ], striped=True, highlightOnHover=True, withTableBorder=True, withColumnBorders=True)


# Callback: Navigate to labels page
@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input({"type": "wom-view-labels-btn", "index": ALL}, "n_clicks"),
    State({"type": "wom-view-labels-btn", "index": ALL}, "id"),
    prevent_initial_call=True
)
def navigate_to_labels(n_clicks_list, btn_ids):
    """Navigate to label printing page with order filter"""

    if not any(n_clicks_list):
        return dash.no_update

    # Find which button was clicked
    triggered_id = ctx.triggered_id
    if triggered_id:
        order_id = triggered_id['index']
        return f"/window-label-printing?order_id={order_id}"

    return dash.no_update


# Callback: Clear filters
@callback(
    Output("wom-filter-po", "value"),
    Output("wom-filter-status", "value"),
    Output("wom-filter-date-start", "value"),
    Output("wom-filter-date-end", "value"),
    Input("wom-clear-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_filters(n_clicks):
    """Clear all filters"""
    if n_clicks:
        return "", "all", None, None
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


# Callback: Open status update modal
@callback(
    Output("wom-status-modal", "opened"),
    Output("wom-status-modal-content", "children"),
    Input({"type": "wom-update-status-btn", "index": ALL}, "n_clicks"),
    State({"type": "wom-update-status-btn", "index": ALL}, "id"),
    State("wom-status-modal", "opened"),
    prevent_initial_call=True
)
def open_status_modal(n_clicks_list, btn_ids, is_opened):
    """Open modal for updating order status"""

    if not any(n_clicks_list):
        return dash.no_update, dash.no_update

    triggered_id = ctx.triggered_id
    if not triggered_id:
        return dash.no_update, dash.no_update

    order_id = triggered_id['index']

    modal_content = dmc.Stack([
        dmc.Text(f"Order ID: {order_id}", size="sm", c="dimmed"),
        dmc.Select(
            id="wom-new-status-select",
            label="New Status",
            data=[
                {"label": "Pending", "value": "pending"},
                {"label": "In Production", "value": "in_production"},
                {"label": "Completed", "value": "completed"},
                {"label": "Shipped", "value": "shipped"},
                {"label": "Cancelled", "value": "cancelled"},
            ],
            required=True
        ),
        dcc.Store(id="wom-updating-order-id", data=order_id),
    ])

    return True, modal_content


# Callback: Update order status
@callback(
    Output("wom-notifications", "children", allow_duplicate=True),
    Output("wom-status-modal", "opened", allow_duplicate=True),
    Output("wom-refresh-btn", "n_clicks", allow_duplicate=True),
    Input("wom-status-update-btn", "n_clicks"),
    State("wom-new-status-select", "value"),
    State("wom-updating-order-id", "data"),
    State("wom-session-store", "data"),
    State("wom-refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def update_order_status(n_clicks, new_status, order_id, session_data, current_refresh_clicks):
    """Update the status of an order"""

    if not n_clicks or not new_status or not order_id:
        return dash.no_update, dash.no_update, dash.no_update

    try:
        db = get_authenticated_db(session_data)
        user_id = session_data.get('user', {}).get('id')

        # Update status
        db.update_window_order_status(order_id, new_status, user_id)

        notification = dmc.Notification(
            title="Success",
            message=f"Order status updated to {new_status.replace('_', ' ').title()}",
            color="green",
            action="show",
            autoClose=3000,
            icon=DashIconify(icon="mdi:check")
        )

        # Close modal and trigger refresh
        return notification, False, (current_refresh_clicks or 0) + 1

    except Exception as e:
        notification = dmc.Notification(
            title="Error",
            message=f"Failed to update status: {str(e)}",
            color="red",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="mdi:alert")
        )
        return notification, True, dash.no_update


# Callback: Cancel status update
@callback(
    Output("wom-status-modal", "opened", allow_duplicate=True),
    Input("wom-status-cancel-btn", "n_clicks"),
    prevent_initial_call=True
)
def cancel_status_update(n_clicks):
    """Close status update modal"""
    if n_clicks:
        return False
    return dash.no_update
