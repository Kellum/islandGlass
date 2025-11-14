"""
Window Order Entry Page
Create window orders with multiple window specifications

Features:
- PO number with autocomplete
- Customer selection/search
- Dynamic multi-window form
- Fraction input support
- Order review and submit
"""

import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, ALL, MATCH, ctx
from dash_iconify import DashIconify
from modules.database import get_authenticated_db
from modules.permissions import get_user_window_permissions
from modules.fraction_utils import to_decimal, validate_measurement, format_fraction
from fractions import Fraction

# Window types
WINDOW_TYPES = [
    "Rectangle", "Arch", "Half Moon", "Triangle", "Circle",
    "Oval", "Pentagon", "Hexagon", "Octagon", "Trapezoid", "Custom Shape"
]

# Page layout
layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Stack([
            dmc.Title("Window Order Entry", order=1),
            dmc.Text("Create a new window order with multiple windows", c="dimmed", size="sm")
        ], gap=0),
    ], justify="space-between"),

    dmc.Space(h=10),

    # Order Info Card
    dmc.Card([
        dmc.Stack([
            dmc.Text("Order Information", size="lg", fw=600),

            dmc.Grid([
                dmc.GridCol([
                    dmc.TextInput(
                        id="window-po-number",
                        label="PO Number",
                        placeholder="Enter PO number",
                        required=True,
                        leftSection=DashIconify(icon="solar:document-bold"),
                        description="Start typing to see existing POs"
                    ),
                    # Autocomplete dropdown
                    html.Div(id="po-autocomplete-list")
                ], span=6),

                dmc.GridCol([
                    dmc.TextInput(
                        id="window-customer-name",
                        label="Customer Name",
                        placeholder="Enter customer name",
                        required=True,
                        leftSection=DashIconify(icon="solar:user-bold")
                    )
                ], span=6),
            ]),

            dmc.Textarea(
                id="window-order-notes",
                label="Order Notes (Optional)",
                placeholder="Additional notes about this order",
                minRows=2
            )
        ], gap="md")
    ], withBorder=True, p="md"),

    # Windows Section
    dmc.Card([
        dmc.Stack([
            dmc.Group([
                dmc.Text("Windows", size="lg", fw=600),
                dmc.Badge(
                    id="window-count-badge",
                    children="0 windows",
                    color="blue",
                    variant="filled",
                    size="lg"
                )
            ], justify="space-between"),

            # Window items list
            html.Div(id="window-items-list"),

            # Add window button
            dmc.Button(
                "Add Window",
                id="add-window-button",
                leftSection=DashIconify(icon="solar:add-circle-bold"),
                variant="light",
                fullWidth=True,
                size="lg"
            ),

            # Hidden store for windows data
            dcc.Store(id="windows-store", data=[])
        ], gap="md")
    ], withBorder=True, p="md"),

    # Action buttons
    dmc.Group([
        dmc.Button(
            "Cancel",
            id="cancel-order-button",
            variant="subtle",
            color="gray",
            size="lg"
        ),
        dmc.Button(
            "Submit Order",
            id="submit-order-button",
            leftSection=DashIconify(icon="solar:check-circle-bold"),
            color="green",
            size="lg"
        )
    ], justify="flex-end"),

    # Notification container
    html.Div(id="window-order-notification")

], gap="md")


# Callback for PO autocomplete
@callback(
    Output("po-autocomplete-list", "children"),
    Input("window-po-number", "value"),
    State("session-store", "data")
)
def po_autocomplete(po_search, session_data):
    """Show autocomplete suggestions for PO numbers"""
    if not po_search or len(po_search) < 2:
        return None

    db = get_authenticated_db(session_data)
    company_id = session_data.get('user_profile', {}).get('company_id')

    if not company_id:
        return None

    # Search for matching PO numbers
    po_numbers = db.search_po_numbers(po_search, company_id, limit=5)

    if not po_numbers:
        return None

    # Create dropdown list
    suggestions = dmc.Paper([
        dmc.Stack([
            dmc.Button(
                po,
                id={'type': 'po-suggestion', 'po': po},
                variant="subtle",
                fullWidth=True,
                justify="flex-start",
                size="sm"
            )
            for po in po_numbers
        ], gap="xs")
    ], shadow="sm", p="xs", style={"position": "absolute", "zIndex": 1000, "width": "100%"})

    return suggestions


# Callback to select PO from autocomplete
@callback(
    Output("window-po-number", "value"),
    Input({'type': 'po-suggestion', 'po': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def select_po_suggestion(n_clicks):
    """Fill PO number from autocomplete selection"""
    if not any(n_clicks):
        return dash.no_update

    triggered = ctx.triggered_id
    if triggered and isinstance(triggered, dict):
        return triggered['po']

    return dash.no_update


# Callback to manage windows
@callback(
    Output("window-items-list", "children"),
    Output("windows-store", "data"),
    Output("window-count-badge", "children"),
    Input("add-window-button", "n_clicks"),
    Input({'type': 'remove-window', 'index': ALL}, 'n_clicks'),
    State("windows-store", "data"),
    prevent_initial_call=True
)
def manage_windows(add_clicks, remove_clicks, windows):
    """Add or remove window specification cards"""
    if not windows:
        windows = []

    triggered = ctx.triggered_id

    # Add window
    if triggered == "add-window-button":
        window_id = len(windows)
        windows.append({'id': window_id})

    # Remove window
    elif triggered and isinstance(triggered, dict) and triggered.get('type') == 'remove-window':
        remove_index = triggered['index']
        windows = [w for w in windows if w['id'] != remove_index]

    # Generate window cards
    cards = []
    for i, window in enumerate(windows):
        cards.append(create_window_card(i + 1, window['id']))

    count_text = f"{len(windows)} window{'s' if len(windows) != 1 else ''}"

    return cards, windows, count_text


def create_window_card(window_number, window_id):
    """Create a single window specification card"""
    return dmc.Card([
        dmc.Stack([
            # Header
            dmc.Group([
                dmc.Text(f"Window #{window_number}", fw=600, size="md"),
                dmc.ActionIcon(
                    DashIconify(icon="solar:trash-bin-bold"),
                    id={'type': 'remove-window', 'index': window_id},
                    color="red",
                    variant="subtle"
                )
            ], justify="space-between"),

            # Window type
            dmc.Select(
                id={'type': 'window-type', 'index': window_id},
                label="Window Type",
                placeholder="Select window type",
                data=[{"value": wt, "label": wt} for wt in WINDOW_TYPES],
                required=True
            ),

            # Dimensions
            dmc.Text("Dimensions (in inches)", size="sm", fw=500, c="dimmed"),
            dmc.Grid([
                dmc.GridCol([
                    dmc.TextInput(
                        id={'type': 'window-thickness', 'index': window_id},
                        label="Thickness",
                        placeholder='e.g., 1 1/2"',
                        required=True,
                        description="Use fractions: 1 1/2, 3/4"
                    )
                ], span=4),
                dmc.GridCol([
                    dmc.TextInput(
                        id={'type': 'window-width', 'index': window_id},
                        label="Width",
                        placeholder='e.g., 36"',
                        required=True
                    )
                ], span=4),
                dmc.GridCol([
                    dmc.TextInput(
                        id={'type': 'window-height', 'index': window_id},
                        label="Height",
                        placeholder='e.g., 48"',
                        required=True
                    )
                ], span=4),
            ]),

            # Quantity
            dmc.NumberInput(
                id={'type': 'window-quantity', 'index': window_id},
                label="Quantity",
                description="How many identical windows",
                min=1,
                value=1,
                required=True
            ),

            # Shape notes (for custom shapes)
            dmc.Textarea(
                id={'type': 'window-notes', 'index': window_id},
                label="Shape Notes (Optional)",
                placeholder="Additional details for custom shapes",
                minRows=2
            )
        ], gap="sm")
    ], withBorder=True, p="md", mb="md")


# Callback to submit order
@callback(
    Output("window-order-notification", "children"),
    Output("window-po-number", "value", allow_duplicate=True),
    Output("window-customer-name", "value"),
    Output("window-order-notes", "value"),
    Output("windows-store", "data", allow_duplicate=True),
    Input("submit-order-button", "n_clicks"),
    State("window-po-number", "value"),
    State("window-customer-name", "value"),
    State("window-order-notes", "value"),
    State({'type': 'window-type', 'index': ALL}, 'value'),
    State({'type': 'window-thickness', 'index': ALL}, 'value'),
    State({'type': 'window-width', 'index': ALL}, 'value'),
    State({'type': 'window-height', 'index': ALL}, 'value'),
    State({'type': 'window-quantity', 'index': ALL}, 'value'),
    State({'type': 'window-notes', 'index': ALL}, 'value'),
    State("session-store", "data"),
    prevent_initial_call=True
)
def submit_order(
    n_clicks, po_number, customer_name, order_notes,
    window_types, thicknesses, widths, heights, quantities, window_notes,
    session_data
):
    """Submit window order to database"""

    # Validate basic info
    if not po_number or not customer_name:
        return dmc.Notification(
            title="Validation Error",
            message="PO number and customer name are required",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        ), dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Validate windows
    if not window_types or len(window_types) == 0:
        return dmc.Notification(
            title="Validation Error",
            message="Please add at least one window",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        ), dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Get database and user info
    db = get_authenticated_db(session_data)
    user_id = session_data.get('user', {}).get('id')
    company_id = session_data.get('user_profile', {}).get('company_id')

    if not user_id or not company_id:
        return dmc.Notification(
            title="Authentication Error",
            message="User not authenticated",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        ), dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Validate and convert measurements
    validated_windows = []
    for i in range(len(window_types)):
        if not window_types[i] or not thicknesses[i] or not widths[i] or not heights[i]:
            return dmc.Notification(
                title="Validation Error",
                message=f"Window #{i+1}: All dimensions are required",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold"),
                action="show"
            ), dash.no_update, dash.no_update, dash.no_update, dash.no_update

        # Validate measurements
        try:
            thickness_decimal = to_decimal(thicknesses[i])
            width_decimal = to_decimal(widths[i])
            height_decimal = to_decimal(heights[i])
        except:
            return dmc.Notification(
                title="Validation Error",
                message=f"Window #{i+1}: Invalid measurement format. Use fractions like 1 1/2 or decimals",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold"),
                action="show"
            ), dash.no_update, dash.no_update, dash.no_update, dash.no_update

        validated_windows.append({
            'window_type': window_types[i],
            'thickness': thickness_decimal,
            'width': width_decimal,
            'height': height_decimal,
            'quantity': quantities[i] or 1,
            'shape_notes': window_notes[i] if i < len(window_notes) else None
        })

    # Create order
    order_data = {
        'po_number': po_number,
        'customer_name': customer_name,
        'notes': order_notes
    }

    order = db.create_window_order(order_data, user_id, company_id)

    if not order:
        return dmc.Notification(
            title="Error",
            message="Failed to create order",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        ), dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Add window items
    total_windows = 0
    for window_data in validated_windows:
        window_data['order_id'] = order['id']
        item = db.add_window_order_item(window_data, user_id, company_id)
        if item:
            total_windows += window_data['quantity']

    # Success!
    return dmc.Notification(
        title="Order Created!",
        message=f"PO {po_number}: {total_windows} windows ordered",
        color="green",
        icon=DashIconify(icon="solar:check-circle-bold"),
        action="show"
    ), "", "", "", []  # Clear form
