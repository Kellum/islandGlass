"""
Inventory Management Page
Track IGU manufacturing supplies with low stock alerts

Features:
- Inventory table with category, quantity, unit, cost
- Low stock warnings (red badge if qty < threshold)
- Category filtering
- Add/edit/delete items
- Cost per unit tracking
"""

import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, MATCH, ALL, ctx
from dash_iconify import DashIconify
from modules.database import get_authenticated_db

# Inventory Layout
layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Stack([
            dmc.Title("Inventory Management", order=1),
            dmc.Text("Track IGU manufacturing supplies", c="dimmed", size="sm")
        ], gap=0),
        dmc.Button(
            "Add Item",
            id="add-inventory-button",
            leftSection=DashIconify(icon="solar:add-circle-bold", width=20),
            color="blue"
        )
    ], justify="space-between"),

    dmc.Space(h=10),

    # Filters and Stats
    dmc.Grid([
        dmc.GridCol([
            dmc.Select(
                id="inventory-category-filter",
                placeholder="All Categories",
                data=[],  # Will be populated dynamically
                clearable=True
            )
        ], span=6),

        dmc.GridCol([
            dmc.Group([
                dmc.Badge(
                    id="low-stock-count",
                    color="red",
                    variant="filled",
                    size="lg"
                ),
                dmc.Text("Low Stock Items", size="sm", c="dimmed")
            ], gap="xs")
        ], span=6),
    ]),

    # Inventory Table
    html.Div(id="inventory-table-container"),

    # Add/Edit Item Modal
    dmc.Modal(
        id="inventory-modal",
        title="Add Inventory Item",
        size="lg",
        children=[
            dmc.Stack([
                dmc.TextInput(
                    id="inventory-name",
                    label="Item Name",
                    placeholder="e.g., Aluminum Spacer 1/2\"",
                    required=True
                ),

                dmc.Grid([
                    dmc.GridCol([
                        dmc.Select(
                            id="inventory-category",
                            label="Category",
                            placeholder="Select category",
                            data=[],  # Populated dynamically
                            searchable=True
                        )
                    ], span=6),

                    dmc.GridCol([
                        dmc.Select(
                            id="inventory-unit",
                            label="Unit",
                            placeholder="Select unit",
                            data=[],  # Populated dynamically
                            searchable=True
                        )
                    ], span=6),
                ]),

                dmc.Grid([
                    dmc.GridCol([
                        dmc.NumberInput(
                            id="inventory-quantity",
                            label="Quantity",
                            placeholder="0",
                            min=0,
                            step=1,
                            decimalScale=2
                        )
                    ], span=4),

                    dmc.GridCol([
                        dmc.NumberInput(
                            id="inventory-cost",
                            label="Cost Per Unit ($)",
                            placeholder="0.00",
                            min=0,
                            step=0.01,
                            decimalScale=2
                        )
                    ], span=4),

                    dmc.GridCol([
                        dmc.NumberInput(
                            id="inventory-threshold",
                            label="Low Stock Threshold",
                            placeholder="10",
                            min=0,
                            step=1,
                            value=10
                        )
                    ], span=4),
                ]),

                dmc.Group([
                    dmc.Button(
                        "Cancel",
                        id="cancel-inventory",
                        variant="subtle",
                        color="gray"
                    ),
                    dmc.Button(
                        "Save Item",
                        id="submit-inventory",
                        leftSection=DashIconify(icon="solar:check-circle-bold", width=18)
                    )
                ], justify="flex-end", mt="md")
            ], gap="sm")
        ]
    ),

    # Notification container
    html.Div(id="inventory-notification-container")

], gap="md")


# Callback to toggle add/edit modal
@callback(
    Output("inventory-modal", "opened"),
    Input("add-inventory-button", "n_clicks"),
    Input("cancel-inventory", "n_clicks"),
    Input("submit-inventory", "n_clicks"),
    State("inventory-modal", "opened"),
    prevent_initial_call=True
)
def toggle_inventory_modal(open_clicks, cancel_clicks, submit_clicks, is_opened):
    """Toggle inventory modal"""
    triggered_id = ctx.triggered_id

    if triggered_id == "add-inventory-button":
        return True
    elif triggered_id in ["cancel-inventory", "submit-inventory"]:
        return False

    return is_opened


# Callback to populate category and unit dropdowns in modal
@callback(
    Output("inventory-category", "data"),
    Output("inventory-unit", "data"),
    Input("inventory-modal", "opened"),
    State("session-store", "data")
)
def populate_modal_dropdowns(is_opened, session_data):
    """Load categories and units for dropdowns"""

    if not is_opened:
        return [], []

    db = get_authenticated_db(session_data)

    categories = db.get_inventory_categories()
    category_options = [{"value": str(cat['id']), "label": cat['name']} for cat in categories]

    units = db.get_inventory_units()
    unit_options = [{"value": str(unit['id']), "label": unit['name']} for unit in units]

    return category_options, unit_options


# Callback to submit new inventory item
@callback(
    Output("inventory-table-container", "children", allow_duplicate=True),
    Output("inventory-notification-container", "children"),
    Input("submit-inventory", "n_clicks"),
    State("inventory-name", "value"),
    State("inventory-category", "value"),
    State("inventory-unit", "value"),
    State("inventory-quantity", "value"),
    State("inventory-cost", "value"),
    State("inventory-threshold", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def add_inventory_item(
    n_clicks, name, category_id, unit_id, quantity, cost, threshold, session_data
):
    """Add new inventory item"""

    if not name:
        return dash.no_update, dmc.Notification(
            title="Error",
            message="Item name is required",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )

    db = get_authenticated_db(session_data)

    # Get user_id from session
    user_id = session_data.get('user', {}).get('id') if session_data else None
    if not user_id:
        return dash.no_update, dmc.Notification(
            title="Error",
            message="User authentication required",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )

    # Prepare item data
    item_data = {
        "name": name,
        "category_id": int(category_id) if category_id else None,
        "unit_id": int(unit_id) if unit_id else None,
        "quantity": quantity or 0,
        "cost_per_unit": cost or 0,
        "low_stock_threshold": threshold or 10
    }

    # Insert item with user_id for audit trail
    result = db.insert_inventory_item(item_data, user_id)

    if result:
        # Reload inventory
        items = db.get_all_inventory_items()

        notification = dmc.Notification(
            title="Success",
            message=f"Added {name} to inventory",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold"),
            action="show"
        )

        return render_inventory_table(items), notification
    else:
        return dash.no_update, dmc.Notification(
            title="Error",
            message="Failed to add item",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )


# Callback to load inventory items
@callback(
    Output("inventory-table-container", "children"),
    Output("inventory-category-filter", "data"),
    Output("low-stock-count", "children"),
    Input("inventory-category-filter", "value"),
    State("session-store", "data")
)
def load_inventory(category_filter, session_data):
    """Load and filter inventory items"""

    db = get_authenticated_db(session_data)

    # Get all items
    items = db.get_all_inventory_items()

    # Get low stock items
    low_stock_items = db.get_low_stock_items()
    low_stock_count = len(low_stock_items)

    # Apply category filter
    if category_filter:
        items = [item for item in items if item.get('category_id') == int(category_filter)]

    # Get unique categories for filter
    categories = db.get_inventory_categories()
    category_options = [{"value": str(cat['id']), "label": cat['name']} for cat in categories]

    return (
        render_inventory_table(items),
        category_options,
        f"{low_stock_count} Low Stock" if low_stock_count > 0 else "All Good"
    )


def render_inventory_table(items):
    """Render inventory items as table"""

    if not items:
        return dmc.Card([
            dmc.Center([
                dmc.Stack([
                    DashIconify(icon="solar:box-bold", width=64, color="#868e96"),
                    dmc.Text("No inventory items", size="lg", c="dimmed"),
                    dmc.Text("Add items to track your supplies", size="sm", c="dimmed")
                ], align="center", gap="xs")
            ], style={"padding": "60px 0"})
        ], withBorder=True)

    # Build table rows
    rows = []
    for item in items:
        item_id = item.get('id')
        name = item.get('name', 'Unknown')
        quantity = float(item.get('quantity', 0))
        threshold = float(item.get('low_stock_threshold', 0))
        cost = float(item.get('cost_per_unit', 0))

        # Get category and unit names from joined data
        category_name = "N/A"
        if item.get('inventory_categories'):
            if isinstance(item['inventory_categories'], dict):
                category_name = item['inventory_categories'].get('name', 'N/A')
            elif isinstance(item['inventory_categories'], list) and len(item['inventory_categories']) > 0:
                category_name = item['inventory_categories'][0].get('name', 'N/A')

        unit_name = "units"
        if item.get('inventory_units'):
            if isinstance(item['inventory_units'], dict):
                unit_name = item['inventory_units'].get('name', 'units')
            elif isinstance(item['inventory_units'], list) and len(item['inventory_units']) > 0:
                unit_name = item['inventory_units'][0].get('name', 'units')

        # Check if low stock
        is_low_stock = quantity < threshold

        rows.append(
            html.Tr([
                # Name
                html.Td(dmc.Text(name, fw=600)),

                # Category
                html.Td(dmc.Badge(category_name, variant="light", color="blue")),

                # Quantity with low stock indicator
                html.Td(
                    dmc.Group([
                        dmc.Text(f"{quantity:.1f}"),
                        dmc.Badge("Low", color="red", size="xs") if is_low_stock else None
                    ], gap="xs")
                ),

                # Unit
                html.Td(dmc.Text(unit_name, size="sm", c="dimmed")),

                # Cost per unit
                html.Td(dmc.Text(f"${cost:.2f}", size="sm")),

                # Total value
                html.Td(dmc.Text(f"${(quantity * cost):.2f}", fw=600, c="blue")),

                # Actions
                html.Td(
                    dmc.Group([
                        dmc.ActionIcon(
                            DashIconify(icon="solar:pen-bold", width=18),
                            id={'type': 'edit-inventory-btn', 'index': item_id},
                            variant="light",
                            color="blue"
                        ),
                        dmc.ActionIcon(
                            DashIconify(icon="solar:trash-bin-trash-bold", width=18),
                            id={'type': 'delete-inventory-btn', 'index': item_id},
                            variant="light",
                            color="red"
                        )
                    ], gap="xs")
                )
            ])
        )

    return dmc.Card([
        dmc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Item Name"),
                    html.Th("Category"),
                    html.Th("Quantity"),
                    html.Th("Unit"),
                    html.Th("Cost/Unit"),
                    html.Th("Total Value"),
                    html.Th("Actions")
                ])
            ]),
            html.Tbody(rows)
        ], striped=True, highlightOnHover=True, withTableBorder=True, withColumnBorders=True),

        dmc.Space(h="sm"),
        dmc.Text(f"Showing {len(items)} item(s)", size="xs", c="dimmed", ta="right")
    ], withBorder=True, p="md")


# Callback to delete inventory item
@callback(
    Output("inventory-table-container", "children", allow_duplicate=True),
    Output("inventory-notification-container", "children", allow_duplicate=True),
    Input({'type': 'delete-inventory-btn', 'index': ALL}, 'n_clicks'),
    State("session-store", "data"),
    prevent_initial_call=True
)
def delete_inventory_item(n_clicks_list, session_data):
    """Delete an inventory item"""

    if not any(n_clicks_list):
        return dash.no_update, dash.no_update

    triggered = ctx.triggered_id
    if not triggered:
        return dash.no_update, dash.no_update

    item_id = triggered['index']

    db = get_authenticated_db(session_data)

    # Get user_id from session
    user_id = session_data.get('user', {}).get('id') if session_data else None
    if not user_id:
        return dash.no_update, dmc.Notification(
            title="Error",
            message="User authentication required",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )

    # Soft delete item with user_id for audit trail
    success = db.delete_inventory_item(item_id, user_id)

    if success:
        # Reload inventory
        items = db.get_all_inventory_items()

        notification = dmc.Notification(
            title="Deleted",
            message="Item deleted successfully",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold"),
            action="show"
        )

        return render_inventory_table(items), notification
    else:
        return dash.no_update, dmc.Notification(
            title="Error",
            message="Failed to delete item",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )
