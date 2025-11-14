"""
Admin Pricing Settings Page
Allows admins to edit all calculator pricing formulas and constants
"""

import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, ALL, ctx
from dash_iconify import DashIconify
from modules.database import Database, get_authenticated_db
from typing import Dict, List


def layout():
    """Admin pricing settings page layout"""
    return dmc.Container([
        dmc.Stack([
            # Header
            dmc.Group([
                dmc.Title("Pricing Settings", order=2),
                dmc.Badge("Admin Only", color="red", leftSection=DashIconify(icon="solar:lock-bold"))
            ], justify="apart"),

            dmc.Text(
                "Configure all calculator pricing formulas and system constants. Changes take effect immediately.",
                c="dimmed",
                size="sm"
            ),

            # Tabs for different pricing categories
            dmc.Tabs(
                id="pricing-tabs",
                value="glass",
                children=[
                    dmc.TabsList([
                        dmc.TabsTab("Glass Pricing", value="glass", leftSection=DashIconify(icon="solar:mirror-left-bold")),
                        dmc.TabsTab("Markups", value="markups", leftSection=DashIconify(icon="solar:chart-bold")),
                        dmc.TabsTab("Edge Work", value="edges", leftSection=DashIconify(icon="solar:ruler-bold")),
                        dmc.TabsTab("System Constants", value="constants", leftSection=DashIconify(icon="solar:settings-bold")),
                        dmc.TabsTab("Pricing Formula", value="formula", leftSection=DashIconify(icon="solar:calculator-bold")),
                    ]),

                    # Glass Pricing Tab
                    dmc.TabsPanel(
                        value="glass",
                        children=[
                            html.Div(id="glass-pricing-content", style={"paddingTop": 20})
                        ]
                    ),

                    # Markups Tab
                    dmc.TabsPanel(
                        value="markups",
                        children=[
                            html.Div(id="markups-content", style={"paddingTop": 20})
                        ]
                    ),

                    # Edge Work Tab
                    dmc.TabsPanel(
                        value="edges",
                        children=[
                            html.Div(id="edge-work-content", style={"paddingTop": 20})
                        ]
                    ),

                    # System Constants Tab
                    dmc.TabsPanel(
                        value="constants",
                        children=[
                            html.Div(id="constants-content", style={"paddingTop": 20})
                        ]
                    ),

                    # Pricing Formula Tab
                    dmc.TabsPanel(
                        value="formula",
                        children=[
                            html.Div(id="formula-content", style={"paddingTop": 20})
                        ]
                    ),
                ]
            ),

            # Notification container
            html.Div(id="pricing-notification-container")
        ], gap="md")
    ], size="xl", py=20)


# ========== Glass Pricing Tab ==========

@callback(
    Output("glass-pricing-content", "children"),
    Input("pricing-tabs", "value"),
    State("session-store", "data")
)
def load_glass_pricing(tab_value, session_data):
    """Load glass pricing configuration"""
    if tab_value != "glass":
        return []

    # Check admin access
    if not session_data or not session_data.get('user'):
        return dmc.Alert(
            "Session expired. Please log in again.",
            title="Authentication Required",
            color="red"
        )

    user = session_data['user']
    if user.get('role') not in ['owner', 'ig_admin']:
        return dmc.Alert(
            "You do not have permission to access pricing settings.",
            title="Access Denied",
            color="red",
            icon=DashIconify(icon="solar:lock-bold")
        )

    # Get authenticated database
    db = get_authenticated_db(session_data)
    glass_config_rows = db.get_glass_config()

    if not glass_config_rows:
        return dmc.Alert(
            "No glass pricing configuration found. Please run database migrations.",
            title="Configuration Missing",
            color="yellow"
        )

    # Group by thickness
    thickness_groups = {}
    for row in glass_config_rows:
        thickness = row['thickness']
        if thickness not in thickness_groups:
            thickness_groups[thickness] = []
        thickness_groups[thickness].append(row)

    # Create cards for each thickness
    cards = []
    for thickness, configs in sorted(thickness_groups.items()):
        rows = []
        for config in sorted(configs, key=lambda x: x['type']):
            rows.append(
                dmc.Grid([
                    dmc.GridCol(
                        dmc.Text(config['type'].title(), fw=500),
                        span=3
                    ),
                    dmc.GridCol(
                        dmc.NumberInput(
                            id={"type": "glass-base-price", "index": config['id']},
                            value=float(config['base_price']),
                            label="Base Price ($/sq ft)",
                            decimalScale=2,
                            fixedDecimalScale=True,
                            min=0,
                            step=0.50,
                            prefix="$",
                            size="sm"
                        ),
                        span=4
                    ),
                    dmc.GridCol(
                        dmc.NumberInput(
                            id={"type": "glass-polish-price", "index": config['id']},
                            value=float(config['polish_price']),
                            label="Polish Price ($/inch)",
                            decimalScale=2,
                            fixedDecimalScale=True,
                            min=0,
                            step=0.05,
                            prefix="$",
                            size="sm"
                        ),
                        span=4
                    ),
                    dmc.GridCol(
                        dmc.Button(
                            "Save",
                            id={"type": "save-glass-config", "index": config['id']},
                            size="sm",
                            variant="light",
                            color="green",
                            leftSection=DashIconify(icon="solar:diskette-bold")
                        ),
                        span=1
                    )
                ], gutter="xs", style={"marginBottom": 15})
            )

        cards.append(
            dmc.Card([
                dmc.Text(thickness, fw=700, size="lg", mb="md"),
                dmc.Stack(rows, gap="xs")
            ], withBorder=True, p="md", mb="md")
        )

    return cards


# ========== Markups Tab ==========

@callback(
    Output("markups-content", "children"),
    Input("pricing-tabs", "value"),
    State("session-store", "data")
)
def load_markups(tab_value, session_data):
    """Load markup percentages"""
    if tab_value != "markups":
        return []

    # Check admin access
    if not session_data or not session_data.get('user'):
        return dmc.Alert(
            "Session expired. Please log in again.",
            title="Authentication Required",
            color="red"
        )

    user = session_data['user']
    if user.get('role') not in ['owner', 'ig_admin']:
        return dmc.Alert(
            "You do not have permission to access pricing settings.",
            title="Access Denied",
            color="red"
        )

    # Get authenticated database
    db = get_authenticated_db(session_data)
    markups = db.get_markups()

    if not markups:
        return dmc.Alert(
            "No markup configuration found.",
            title="Configuration Missing",
            color="yellow"
        )

    # Get full markup rows for IDs
    markup_rows = db.client.table("markups").select("*").is_("deleted_at", "null").execute().data

    cards = []
    for row in markup_rows:
        name = row['name']
        percentage = row['percentage']

        cards.append(
            dmc.Card([
                dmc.Grid([
                    dmc.GridCol(
                        dmc.Stack([
                            dmc.Text(name.title(), fw=700, size="lg"),
                            dmc.Text(
                                "Percentage added to base price for tempered glass" if name == "tempered"
                                else "Percentage added for non-rectangular shapes",
                                c="dimmed",
                                size="sm"
                            )
                        ], gap=0),
                        span=6
                    ),
                    dmc.GridCol(
                        dmc.NumberInput(
                            id={"type": "markup-percentage", "index": name},
                            value=float(percentage),
                            label="Percentage",
                            decimalScale=1,
                            fixedDecimalScale=True,
                            min=0,
                            max=100,
                            step=1.0,
                            suffix="%",
                            size="lg"
                        ),
                        span=4
                    ),
                    dmc.GridCol(
                        dmc.Button(
                            "Save",
                            id={"type": "save-markup", "index": name},
                            size="lg",
                            variant="light",
                            color="green",
                            leftSection=DashIconify(icon="solar:diskette-bold")
                        ),
                        span=2
                    )
                ])
            ], withBorder=True, p="lg", mb="md")
        )

    return cards


# ========== Edge Work Tab ==========

@callback(
    Output("edge-work-content", "children"),
    Input("pricing-tabs", "value"),
    State("session-store", "data")
)
def load_edge_work(tab_value, session_data):
    """Load edge work pricing (beveled & clipped corners)"""
    if tab_value != "edges":
        return []

    # Check admin access
    if not session_data or not session_data.get('user'):
        return dmc.Alert(
            "Session expired. Please log in again.",
            title="Authentication Required",
            color="red"
        )

    user = session_data['user']
    if user.get('role') not in ['owner', 'ig_admin']:
        return dmc.Alert(
            "You do not have permission to access pricing settings.",
            title="Access Denied",
            color="red"
        )

    # Get authenticated database
    db = get_authenticated_db(session_data)
    beveled_rows = db.client.table("beveled_pricing").select("*").is_("deleted_at", "null").execute().data
    clipped_rows = db.client.table("clipped_corners_pricing").select("*").is_("deleted_at", "null").execute().data

    content = []

    # Beveled Pricing Section
    content.append(dmc.Title("Beveled Edge Pricing", order=4, mb="md"))
    content.append(dmc.Text("Price per inch of perimeter", c="dimmed", size="sm", mb="md"))

    beveled_cards = []
    for row in sorted(beveled_rows, key=lambda x: x['glass_thickness']):
        beveled_cards.append(
            dmc.Grid([
                dmc.GridCol(
                    dmc.Text(row['glass_thickness'], fw=500, size="lg"),
                    span=3
                ),
                dmc.GridCol(
                    dmc.NumberInput(
                        id={"type": "beveled-price", "index": row['id']},
                        value=float(row['price_per_inch']),
                        label="Price per Inch",
                        decimalScale=2,
                        fixedDecimalScale=True,
                        min=0,
                        step=0.10,
                        prefix="$",
                        size="sm"
                    ),
                    span=6
                ),
                dmc.GridCol(
                    dmc.Button(
                        "Save",
                        id={"type": "save-beveled", "index": row['id']},
                        size="sm",
                        variant="light",
                        color="green",
                        leftSection=DashIconify(icon="solar:diskette-bold")
                    ),
                    span=3
                )
            ], gutter="sm", style={"marginBottom": 10})
        )

    content.append(dmc.Card(beveled_cards, withBorder=True, p="md", mb="xl"))

    # Clipped Corners Pricing Section
    content.append(dmc.Title("Clipped Corners Pricing", order=4, mb="md"))
    content.append(dmc.Text("Price per corner", c="dimmed", size="sm", mb="md"))

    clipped_cards = []
    for row in sorted(clipped_rows, key=lambda x: (x['glass_thickness'], x['clip_size'])):
        label = f"{row['glass_thickness']} - {row['clip_size'].replace('_', ' ').title()}"
        clipped_cards.append(
            dmc.Grid([
                dmc.GridCol(
                    dmc.Text(label, fw=500),
                    span=3
                ),
                dmc.GridCol(
                    dmc.NumberInput(
                        id={"type": "clipped-price", "index": row['id']},
                        value=float(row['price_per_corner']),
                        label="Price per Corner",
                        decimalScale=2,
                        fixedDecimalScale=True,
                        min=0,
                        step=0.50,
                        prefix="$",
                        size="sm"
                    ),
                    span=6
                ),
                dmc.GridCol(
                    dmc.Button(
                        "Save",
                        id={"type": "save-clipped", "index": row['id']},
                        size="sm",
                        variant="light",
                        color="green",
                        leftSection=DashIconify(icon="solar:diskette-bold")
                    ),
                    span=3
                )
            ], gutter="sm", style={"marginBottom": 10})
        )

    content.append(dmc.Card(clipped_cards, withBorder=True, p="md"))

    return content


# ========== System Constants Tab ==========

@callback(
    Output("constants-content", "children"),
    Input("pricing-tabs", "value"),
    State("session-store", "data")
)
def load_constants(tab_value, session_data):
    """Load system constants"""
    if tab_value != "constants":
        return []

    # Check admin access
    if not session_data or not session_data.get('user'):
        return dmc.Alert(
            "Session expired. Please log in again.",
            title="Authentication Required",
            color="red"
        )

    user = session_data['user']
    if user.get('role') not in ['owner', 'ig_admin']:
        return dmc.Alert(
            "You do not have permission to access pricing settings.",
            title="Access Denied",
            color="red"
        )

    # Get authenticated database
    db = get_authenticated_db(session_data)
    settings = db.get_calculator_settings()

    constants_config = [
        {
            "key": "minimum_sq_ft",
            "title": "Minimum Square Footage",
            "description": "Minimum billable square footage for all glass orders (typically 3.0)",
            "value": settings.get('minimum_sq_ft', 3.0),
            "step": 0.5,
            "suffix": "sq ft"
        },
        {
            "key": "markup_divisor",
            "title": "Markup Divisor",
            "description": "Final quote price = Total ÷ this value (typically 0.28 for ~257% markup)",
            "value": settings.get('markup_divisor', 0.28),
            "step": 0.01,
            "suffix": ""
        },
        {
            "key": "contractor_discount_rate",
            "title": "Contractor Discount Rate",
            "description": "Discount percentage for contractor pricing (0.15 = 15%)",
            "value": settings.get('contractor_discount_rate', 0.15),
            "step": 0.01,
            "suffix": ""
        },
        {
            "key": "flat_polish_rate",
            "title": "Flat Polish Rate (Mirrors)",
            "description": "Price per inch for flat polish on mirror glass",
            "value": settings.get('flat_polish_rate', 0.27),
            "step": 0.01,
            "suffix": "$/inch"
        }
    ]

    cards = []
    for const in constants_config:
        cards.append(
            dmc.Card([
                dmc.Grid([
                    dmc.GridCol(
                        dmc.Stack([
                            dmc.Text(const['title'], fw=700, size="lg"),
                            dmc.Text(const['description'], c="dimmed", size="sm")
                        ], gap=5),
                        span=6
                    ),
                    dmc.GridCol(
                        dmc.NumberInput(
                            id={"type": "constant-value", "index": const['key']},
                            value=const['value'],
                            label="Value",
                            decimalScale=4,
                            min=0,
                            step=const['step'],
                            **({'suffix': const['suffix']} if const['suffix'] else {}),
                            size="lg"
                        ),
                        span=4
                    ),
                    dmc.GridCol(
                        dmc.Button(
                            "Save",
                            id={"type": "save-constant", "index": const['key']},
                            size="lg",
                            variant="light",
                            color="green",
                            leftSection=DashIconify(icon="solar:diskette-bold")
                        ),
                        span=2
                    )
                ])
            ], withBorder=True, p="lg", mb="md")
        )

    return dmc.Stack([
        dmc.Alert(
            "These constants affect all calculator pricing globally. Changes take effect immediately.",
            title="Warning",
            color="orange",
            icon=DashIconify(icon="solar:danger-bold")
        ),
        *cards
    ], gap="md")


# ========== Pricing Formula Tab ==========

@callback(
    Output("formula-content", "children"),
    Input("pricing-tabs", "value"),
    State("session-store", "data")
)
def load_pricing_formula(tab_value, session_data):
    """Load pricing formula configuration"""
    if tab_value != "formula":
        return []

    # Check admin access
    if not session_data or not session_data.get('user'):
        return dmc.Alert(
            "Session expired. Please log in again.",
            title="Authentication Required",
            color="red"
        )

    user = session_data['user']
    if user.get('role') not in ['owner', 'ig_admin']:
        return dmc.Alert(
            "You do not have permission to access pricing settings.",
            title="Access Denied",
            color="red"
        )

    # Get authenticated database
    db = get_authenticated_db(session_data)
    formula_config = db.get_pricing_formula_config()

    return dmc.Stack([
        # Warning Alert
        dmc.Alert(
            "Changes to the pricing formula affect ALL calculator pricing globally and take effect immediately. "
            "All changes are logged for audit purposes.",
            title="Critical Warning",
            color="red",
            icon=DashIconify(icon="solar:danger-triangle-bold")
        ),

        # Formula Mode Selection
        dmc.Card([
            dmc.Title("Formula Mode", order=4, mb="md"),
            dmc.Text(
                "Choose how the final quote price is calculated from the combined cost",
                c="dimmed",
                size="sm",
                mb="md"
            ),

            dmc.RadioGroup(
                id="formula-mode-radio",
                value=formula_config.get('formula_mode', 'divisor'),
                children=[
                    dmc.Radio(
                        label=dmc.Group([
                            dmc.Text("Divisor Mode", fw=500),
                            dmc.Text("(Quote Price = Total ÷ Divisor)", c="dimmed", size="sm")
                        ], gap="xs"),
                        value="divisor"
                    ),
                    dmc.Radio(
                        label=dmc.Group([
                            dmc.Text("Multiplier Mode", fw=500),
                            dmc.Text("(Quote Price = Total × Multiplier)", c="dimmed", size="sm")
                        ], gap="xs"),
                        value="multiplier"
                    ),
                    dmc.Radio(
                        label=dmc.Group([
                            dmc.Text("Custom Expression", fw=500),
                            dmc.Text("(Advanced: Write your own formula)", c="dimmed", size="sm")
                        ], gap="xs"),
                        value="custom"
                    ),
                ],
                mb="lg"
            ),

            # Divisor Input (shown when divisor mode)
            html.Div(
                id="divisor-input-container",
                children=[
                    dmc.NumberInput(
                        id="formula-divisor-value",
                        label="Divisor Value",
                        description="Typically 0.28 for ~257% markup",
                        value=formula_config.get('divisor_value', 0.28),
                        decimalScale=4,
                        min=0.01,
                        max=1.0,
                        step=0.01,
                        size="lg",
                        style={"maxWidth": 300}
                    )
                ],
                style={"display": "block" if formula_config.get('formula_mode') == 'divisor' else "none"}
            ),

            # Multiplier Input (shown when multiplier mode)
            html.Div(
                id="multiplier-input-container",
                children=[
                    dmc.NumberInput(
                        id="formula-multiplier-value",
                        label="Multiplier Value",
                        description="Typically 3.5714 (equivalent to ÷ 0.28)",
                        value=formula_config.get('multiplier_value', 3.5714),
                        decimalScale=4,
                        min=1.0,
                        max=10.0,
                        step=0.1,
                        size="lg",
                        style={"maxWidth": 300}
                    )
                ],
                style={"display": "block" if formula_config.get('formula_mode') == 'multiplier' else "none"}
            ),

            # Custom Expression Input (shown when custom mode)
            html.Div(
                id="custom-expression-container",
                children=[
                    dmc.Textarea(
                        id="formula-custom-expression",
                        label="Custom Formula Expression",
                        description="Use 'total' as the variable. Example: total * 3.5 + 10",
                        value=formula_config.get('custom_expression', ''),
                        placeholder="total * 3.5 + 10",
                        autosize=True,
                        minRows=3,
                        size="lg"
                    ),
                    dmc.Text(
                        "Allowed: +, -, *, /, (), total, abs(), min(), max(), round()",
                        c="dimmed",
                        size="xs",
                        mt="xs"
                    ),
                    html.Div(id="formula-validation-message", style={"marginTop": 10})
                ],
                style={"display": "block" if formula_config.get('formula_mode') == 'custom' else "none"}
            ),
        ], withBorder=True, p="lg", mb="md"),

        # Formula Components Toggles
        dmc.Card([
            dmc.Title("Formula Components", order=4, mb="md"),
            dmc.Text(
                "Enable or disable specific components of the pricing calculation",
                c="dimmed",
                size="sm",
                mb="md"
            ),

            dmc.Grid([
                dmc.GridCol(
                    dmc.Switch(
                        id="enable-base-price",
                        label="Base Price (sq ft × rate)",
                        checked=formula_config.get('enable_base_price', True),
                        size="md"
                    ),
                    span=6
                ),
                dmc.GridCol(
                    dmc.Switch(
                        id="enable-polish",
                        label="Polish Edges",
                        checked=formula_config.get('enable_polish', True),
                        size="md"
                    ),
                    span=6
                ),
                dmc.GridCol(
                    dmc.Switch(
                        id="enable-beveled",
                        label="Beveled Edges",
                        checked=formula_config.get('enable_beveled', True),
                        size="md"
                    ),
                    span=6
                ),
                dmc.GridCol(
                    dmc.Switch(
                        id="enable-clipped-corners",
                        label="Clipped Corners",
                        checked=formula_config.get('enable_clipped_corners', True),
                        size="md"
                    ),
                    span=6
                ),
                dmc.GridCol(
                    dmc.Switch(
                        id="enable-tempered-markup",
                        label="Tempered Markup",
                        checked=formula_config.get('enable_tempered_markup', True),
                        size="md"
                    ),
                    span=6
                ),
                dmc.GridCol(
                    dmc.Switch(
                        id="enable-shape-markup",
                        label="Shape Markup",
                        checked=formula_config.get('enable_shape_markup', True),
                        size="md"
                    ),
                    span=6
                ),
                dmc.GridCol(
                    dmc.Switch(
                        id="enable-contractor-discount",
                        label="Contractor Discount",
                        checked=formula_config.get('enable_contractor_discount', True),
                        size="md"
                    ),
                    span=6
                ),
            ], gutter="md")
        ], withBorder=True, p="lg", mb="md"),

        # Example Calculation Preview
        dmc.Card([
            dmc.Title("Formula Preview", order=4, mb="md"),
            html.Div(id="formula-preview-content")
        ], withBorder=True, p="lg", mb="md"),

        # Save Button
        dmc.Button(
            "Save Formula Configuration",
            id="save-formula-config-btn",
            size="lg",
            color="green",
            leftSection=DashIconify(icon="solar:diskette-bold"),
            fullWidth=True
        ),
    ], gap="md")


# ========== Save Callbacks ==========

@callback(
    Output("pricing-notification-container", "children", allow_duplicate=True),
    Input({"type": "save-glass-config", "index": ALL}, "n_clicks"),
    State({"type": "glass-base-price", "index": ALL}, "value"),
    State({"type": "glass-polish-price", "index": ALL}, "value"),
    State({"type": "glass-base-price", "index": ALL}, "id"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def save_glass_config(n_clicks, base_prices, polish_prices, ids, session_data):
    """Save glass configuration changes"""
    if not ctx.triggered_id or not any(n_clicks):
        return None

    if not session_data or not session_data.get('user'):
        return dmc.Notification(
            title="Error",
            message="Session expired",
            color="red",
            action="show"
        )

    user = session_data['user']

    # Find which button was clicked
    clicked_id = ctx.triggered_id['index']
    clicked_index = next((i for i, id_dict in enumerate(ids) if id_dict['index'] == clicked_id), None)

    if clicked_index is None:
        return None

    base_price = base_prices[clicked_index]
    polish_price = polish_prices[clicked_index]

    # Get authenticated database
    db = get_authenticated_db(session_data)
    success = db.update_glass_config(
        id=clicked_id,
        base_price=base_price,
        polish_price=polish_price,
        user_id=user['id']
    )

    if success:
        return dmc.Notification(
            title="Success",
            message="Glass pricing updated",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold"),
            action="show"
        )
    else:
        return dmc.Notification(
            title="Error",
            message="Failed to update pricing",
            color="red",
            action="show"
        )


@callback(
    Output("pricing-notification-container", "children", allow_duplicate=True),
    Input({"type": "save-markup", "index": ALL}, "n_clicks"),
    State({"type": "markup-percentage", "index": ALL}, "value"),
    State({"type": "markup-percentage", "index": ALL}, "id"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def save_markup(n_clicks, percentages, ids, session_data):
    """Save markup percentage changes"""
    if not ctx.triggered_id or not any(n_clicks):
        return None

    if not session_data or not session_data.get('user'):
        return dmc.Notification(
            title="Error",
            message="Session expired",
            color="red",
            action="show"
        )

    user = session_data['user']
    markup_name = ctx.triggered_id['index']
    clicked_index = next((i for i, id_dict in enumerate(ids) if id_dict['index'] == markup_name), None)

    if clicked_index is None:
        return None

    percentage = percentages[clicked_index]

    # Get authenticated database
    db = get_authenticated_db(session_data)
    success = db.update_markup(
        name=markup_name,
        percentage=percentage,
        user_id=user['id']
    )

    if success:
        return dmc.Notification(
            title="Success",
            message=f"{markup_name.title()} markup updated to {percentage}%",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold"),
            action="show"
        )
    else:
        return dmc.Notification(
            title="Error",
            message="Failed to update markup",
            color="red",
            action="show"
        )


@callback(
    Output("pricing-notification-container", "children", allow_duplicate=True),
    Input({"type": "save-beveled", "index": ALL}, "n_clicks"),
    State({"type": "beveled-price", "index": ALL}, "value"),
    State({"type": "beveled-price", "index": ALL}, "id"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def save_beveled_pricing(n_clicks, prices, ids, session_data):
    """Save beveled pricing changes"""
    if not ctx.triggered_id or not any(n_clicks):
        return None

    if not session_data or not session_data.get('user'):
        return dmc.Notification(
            title="Error",
            message="Session expired",
            color="red",
            action="show"
        )

    user = session_data['user']
    clicked_id = ctx.triggered_id['index']
    clicked_index = next((i for i, id_dict in enumerate(ids) if id_dict['index'] == clicked_id), None)

    if clicked_index is None:
        return None

    price = prices[clicked_index]

    # Get authenticated database
    db = get_authenticated_db(session_data)
    success = db.update_beveled_pricing(
        id=clicked_id,
        price_per_inch=price,
        user_id=user['id']
    )

    if success:
        return dmc.Notification(
            title="Success",
            message="Beveled pricing updated",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold"),
            action="show"
        )
    else:
        return dmc.Notification(
            title="Error",
            message="Failed to update pricing",
            color="red",
            action="show"
        )


@callback(
    Output("pricing-notification-container", "children", allow_duplicate=True),
    Input({"type": "save-clipped", "index": ALL}, "n_clicks"),
    State({"type": "clipped-price", "index": ALL}, "value"),
    State({"type": "clipped-price", "index": ALL}, "id"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def save_clipped_pricing(n_clicks, prices, ids, session_data):
    """Save clipped corners pricing changes"""
    if not ctx.triggered_id or not any(n_clicks):
        return None

    if not session_data or not session_data.get('user'):
        return dmc.Notification(
            title="Error",
            message="Session expired",
            color="red",
            action="show"
        )

    user = session_data['user']
    clicked_id = ctx.triggered_id['index']
    clicked_index = next((i for i, id_dict in enumerate(ids) if id_dict['index'] == clicked_id), None)

    if clicked_index is None:
        return None

    price = prices[clicked_index]

    # Get authenticated database
    db = get_authenticated_db(session_data)
    success = db.update_clipped_corners_pricing(
        id=clicked_id,
        price_per_corner=price,
        user_id=user['id']
    )

    if success:
        return dmc.Notification(
            title="Success",
            message="Clipped corners pricing updated",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold"),
            action="show"
        )
    else:
        return dmc.Notification(
            title="Error",
            message="Failed to update pricing",
            color="red",
            action="show"
        )


@callback(
    Output("pricing-notification-container", "children", allow_duplicate=True),
    Input({"type": "save-constant", "index": ALL}, "n_clicks"),
    State({"type": "constant-value", "index": ALL}, "value"),
    State({"type": "constant-value", "index": ALL}, "id"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def save_constant(n_clicks, values, ids, session_data):
    """Save system constant changes"""
    if not ctx.triggered_id or not any(n_clicks):
        return None

    if not session_data or not session_data.get('user'):
        return dmc.Notification(
            title="Error",
            message="Session expired",
            color="red",
            action="show"
        )

    user = session_data['user']
    setting_key = ctx.triggered_id['index']
    clicked_index = next((i for i, id_dict in enumerate(ids) if id_dict['index'] == setting_key), None)

    if clicked_index is None:
        return None

    value = values[clicked_index]

    # Get authenticated database
    db = get_authenticated_db(session_data)
    success = db.update_calculator_setting(
        setting_key=setting_key,
        setting_value=value,
        user_id=user['id']
    )

    if success:
        return dmc.Notification(
            title="Success",
            message=f"{setting_key.replace('_', ' ').title()} updated to {value}",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold"),
            action="show"
        )
    else:
        return dmc.Notification(
            title="Error",
            message="Failed to update setting",
            color="red",
            action="show"
        )


# ========== Formula Tab Callbacks ==========

@callback(
    [
        Output("divisor-input-container", "style"),
        Output("multiplier-input-container", "style"),
        Output("custom-expression-container", "style"),
    ],
    Input("formula-mode-radio", "value")
)
def toggle_formula_inputs(mode):
    """Show/hide formula inputs based on selected mode"""
    return (
        {"display": "block"} if mode == "divisor" else {"display": "none"},
        {"display": "block"} if mode == "multiplier" else {"display": "none"},
        {"display": "block"} if mode == "custom" else {"display": "none"}
    )


@callback(
    Output("formula-validation-message", "children"),
    Input("formula-custom-expression", "value"),
    prevent_initial_call=True
)
def validate_custom_expression(expression):
    """Validate custom formula expression in real-time"""
    if not expression or not expression.strip():
        return None

    # Import calculator to use validation method
    from modules.glass_calculator import GlassPriceCalculator

    # Create a dummy calculator just for validation
    calc = GlassPriceCalculator({'glass_config': {}, 'markups': {}, 'beveled_pricing': {}, 'clipped_corners_pricing': {}})
    is_valid, error_msg = calc.validate_custom_formula(expression)

    if is_valid:
        return dmc.Alert(
            "Formula is valid!",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold")
        )
    else:
        return dmc.Alert(
            error_msg,
            title="Invalid Formula",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        )


@callback(
    Output("formula-preview-content", "children"),
    [
        Input("formula-mode-radio", "value"),
        Input("formula-divisor-value", "value"),
        Input("formula-multiplier-value", "value"),
        Input("formula-custom-expression", "value"),
    ]
)
def update_formula_preview(mode, divisor, multiplier, custom_expr):
    """Show example calculation with current formula settings"""
    # Example: $100 combined cost
    example_total = 100.0

    try:
        if mode == "divisor":
            if divisor and divisor > 0:
                result = example_total / divisor
                formula_text = f"${example_total:.2f} ÷ {divisor} = ${result:.2f}"
            else:
                result = 0
                formula_text = "Invalid divisor (must be > 0)"
        elif mode == "multiplier":
            if multiplier:
                result = example_total * multiplier
                formula_text = f"${example_total:.2f} × {multiplier} = ${result:.2f}"
            else:
                result = 0
                formula_text = "Invalid multiplier"
        elif mode == "custom":
            if custom_expr:
                # Import calculator to use validation
                from modules.glass_calculator import GlassPriceCalculator
                calc = GlassPriceCalculator({'glass_config': {}, 'markups': {}, 'beveled_pricing': {}, 'clipped_corners_pricing': {}})
                is_valid, error = calc.validate_custom_formula(custom_expr)

                if is_valid:
                    safe_namespace = {
                        'total': example_total,
                        'abs': abs,
                        'min': min,
                        'max': max,
                        'round': round,
                        '__builtins__': {}
                    }
                    result = eval(custom_expr, safe_namespace)
                    formula_text = f"Expression: {custom_expr}\n${example_total:.2f} → ${result:.2f}"
                else:
                    result = 0
                    formula_text = f"Invalid expression: {error}"
            else:
                result = 0
                formula_text = "No expression provided"
        else:
            result = 0
            formula_text = "Unknown mode"

        return dmc.Stack([
            dmc.Text("Example with $100 combined cost:", fw=500, size="sm", c="dimmed"),
            dmc.Code(formula_text, block=True, style={"fontSize": 16, "padding": 15}),
            dmc.Text(f"Quote Price: ${result:.2f}", size="xl", fw=700, c="green")
        ], gap="sm")

    except Exception as e:
        return dmc.Alert(
            f"Error calculating preview: {str(e)}",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        )


@callback(
    Output("pricing-notification-container", "children", allow_duplicate=True),
    Input("save-formula-config-btn", "n_clicks"),
    [
        State("formula-mode-radio", "value"),
        State("formula-divisor-value", "value"),
        State("formula-multiplier-value", "value"),
        State("formula-custom-expression", "value"),
        State("enable-base-price", "checked"),
        State("enable-polish", "checked"),
        State("enable-beveled", "checked"),
        State("enable-clipped-corners", "checked"),
        State("enable-tempered-markup", "checked"),
        State("enable-shape-markup", "checked"),
        State("enable-contractor-discount", "checked"),
        State("session-store", "data"),
    ],
    prevent_initial_call=True
)
def save_formula_config(
    n_clicks,
    formula_mode,
    divisor_value,
    multiplier_value,
    custom_expression,
    enable_base,
    enable_polish,
    enable_beveled,
    enable_clipped,
    enable_tempered,
    enable_shape,
    enable_contractor,
    session_data
):
    """Save pricing formula configuration"""
    if not n_clicks:
        return None

    if not session_data or not session_data.get('user'):
        return dmc.Notification(
            title="Error",
            message="Session expired",
            color="red",
            action="show"
        )

    user = session_data['user']

    # Validate formula mode specific values
    if formula_mode == "divisor" and (not divisor_value or divisor_value <= 0):
        return dmc.Notification(
            title="Validation Error",
            message="Divisor value must be greater than 0",
            color="red",
            action="show"
        )

    if formula_mode == "multiplier" and (not multiplier_value or multiplier_value <= 0):
        return dmc.Notification(
            title="Validation Error",
            message="Multiplier value must be greater than 0",
            color="red",
            action="show"
        )

    if formula_mode == "custom":
        if not custom_expression or not custom_expression.strip():
            return dmc.Notification(
                title="Validation Error",
                message="Custom expression cannot be empty",
                color="red",
                action="show"
            )

        # Validate custom expression
        from modules.glass_calculator import GlassPriceCalculator
        calc = GlassPriceCalculator({'glass_config': {}, 'markups': {}, 'beveled_pricing': {}, 'clipped_corners_pricing': {}})
        is_valid, error = calc.validate_custom_formula(custom_expression)

        if not is_valid:
            return dmc.Notification(
                title="Invalid Formula",
                message=error,
                color="red",
                action="show"
            )

    # Get authenticated database
    db = get_authenticated_db(session_data)
    success = db.update_pricing_formula_config(
        formula_mode=formula_mode,
        divisor_value=divisor_value or 0.28,
        multiplier_value=multiplier_value or 3.5714,
        custom_expression=custom_expression if formula_mode == "custom" else None,
        enable_base_price=enable_base,
        enable_polish=enable_polish,
        enable_beveled=enable_beveled,
        enable_clipped_corners=enable_clipped,
        enable_tempered_markup=enable_tempered,
        enable_shape_markup=enable_shape,
        enable_contractor_discount=enable_contractor,
        user_id=user['id']
    )

    if success:
        return dmc.Notification(
            title="Success",
            message="Pricing formula configuration updated successfully. Changes are now active.",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold"),
            action="show",
            autoClose=5000
        )
    else:
        return dmc.Notification(
            title="Error",
            message="Failed to update formula configuration",
            color="red",
            action="show"
        )
