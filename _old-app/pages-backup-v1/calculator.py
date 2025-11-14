"""
Glass Calculator Page
Modern two-column layout with real-time pricing and accordions

Features:
- Two-column layout: Form (left) + Sticky Price Summary (right)
- Accordion sections for advanced options
- Progressive disclosure (dynamic fields)
- Real-time price updates
- Compact, efficient design
"""

import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, ALL
from dash_iconify import DashIconify
from modules.database import get_authenticated_db
from modules.glass_calculator import GlassPriceCalculator
from modules.fraction_utils import parse_measurement, validate_measurement, to_decimal
import traceback

# Glass Calculator Layout
layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Title("Glass Calculator", order=1),
        dmc.Badge("Real-time Quote Generator", color="blue", variant="light")
    ], justify="space-between"),

    dmc.Text("Calculate accurate glass pricing with live updates", c="dimmed", size="sm"),

    dmc.Space(h=10),

    # Two-Column Layout
    dmc.Grid([
        # LEFT COLUMN - Form Inputs (60%)
        dmc.GridCol([
            dmc.Card([
                dmc.Stack([
                    # Basic Info Section
                    dmc.Stack([
                        dmc.Group([
                            dmc.TextInput(
                                id="calc-po-name",
                                label="P.O./Job/Name",
                                placeholder="Enter P.O. or Job Name",
                                style={"flex": 1}
                            ),
                            dmc.Checkbox(
                                id="calc-contractor",
                                label="Contractor (15% off)",
                                mt=25
                            )
                        ]),
                    ], gap="sm"),

                    dmc.Divider(variant="dashed"),

                    # Dimensions
                    dmc.Text("Dimensions", size="md", fw=600),
                    dmc.Grid([
                        dmc.GridCol([
                            dmc.TextInput(
                                id="calc-width",
                                label="Width (inches)",
                                placeholder="24 or 24 1/2",
                                required=True
                            )
                        ], span=4),
                        dmc.GridCol([
                            dmc.TextInput(
                                id="calc-height",
                                label="Height (inches)",
                                placeholder="36 or 36 3/4",
                                required=True
                            )
                        ], span=4),
                        dmc.GridCol([
                            dmc.NumberInput(
                                id="calc-quantity",
                                label="Quantity",
                                min=1,
                                max=999,
                                value=1,
                                step=1
                            )
                        ], span=4),
                    ]),

                    # Minimum warning
                    html.Div(id="calc-min-warning-container"),

                    dmc.Divider(variant="dashed"),

                    # Glass Configuration
                    dmc.Text("Glass Configuration", size="md", fw=600),
                    dmc.Grid([
                        dmc.GridCol([
                            dmc.Select(
                                id="calc-glass-type",
                                label="Glass Type",
                                data=[
                                    {"value": "clear", "label": "Clear Glass"},
                                    {"value": "bronze", "label": "Bronze"},
                                    {"value": "gray", "label": "Gray"},
                                    {"value": "mirror", "label": "Mirror"}
                                ],
                                value="clear",
                                required=True
                            )
                        ], span=6),
                        dmc.GridCol([
                            dmc.Select(
                                id="calc-thickness",
                                label="Thickness",
                                data=[
                                    {"value": '1/8"', "label": '1/8"'},
                                    {"value": '3/16"', "label": '3/16"'},
                                    {"value": '1/4"', "label": '1/4"'},
                                    {"value": '3/8"', "label": '3/8"'},
                                    {"value": '1/2"', "label": '1/2"'}
                                ],
                                value='1/4"',
                                required=True
                            )
                        ], span=6),
                    ]),

                    # Shape Selection (Compact Segmented Control)
                    dmc.Stack([
                        dmc.Text("Shape", size="sm", fw=500),
                        dmc.SegmentedControl(
                            id="calc-shape",
                            value="rectangular",
                            data=[
                                {"value": "rectangular", "label": "Rectangular"},
                                {"value": "circular", "label": "Circular"},
                                {"value": "non-rectangular", "label": "Custom Shape"}
                            ],
                            fullWidth=True
                        ),
                        # Diameter input (always exists, hidden when not circular)
                        dmc.TextInput(
                            id="calc-diameter",
                            label="Diameter (inches)",
                            placeholder="Enter diameter",
                            description="Supports fractions",
                            style={"display": "none"},
                            mt="xs"
                        ),
                    ], gap="xs"),

                    dmc.Divider(variant="dashed"),

                    # Edge Processing Accordion
                    dmc.Accordion([
                        dmc.AccordionItem([
                            dmc.AccordionControl(
                                "Edge Processing",
                                icon=DashIconify(icon="solar:diamond-bold", width=20)
                            ),
                            dmc.AccordionPanel([
                                dmc.Stack([
                                    # Polish and Beveled in one row
                                    dmc.Group([
                                        dmc.Checkbox(
                                            id="calc-polish",
                                            label="Polished Edges"
                                        ),
                                        dmc.Checkbox(
                                            id="calc-beveled",
                                            label="Beveled Edges"
                                        ),
                                    ]),

                                    # Clipped Corners
                                    dmc.Grid([
                                        dmc.GridCol([
                                            dmc.NumberInput(
                                                id="calc-clipped-corners",
                                                label="Clipped Corners",
                                                description="Number of corners",
                                                min=0,
                                                max=4,
                                                value=0,
                                                step=1
                                            )
                                        ], span=6),
                                        dmc.GridCol([
                                            dmc.Select(
                                                id="calc-clip-size",
                                                label="Clip Size",
                                                data=[
                                                    {"value": "under_1", "label": "Under 1 inch"},
                                                    {"value": "over_1", "label": "Over 1 inch"}
                                                ],
                                                value="under_1",
                                                style={"display": "none"}
                                            )
                                        ], span=6),
                                    ])
                                ], gap="sm")
                            ])
                        ], value="edge-processing")
                    ], variant="separated"),

                    # Additional Options Accordion
                    dmc.Accordion([
                        dmc.AccordionItem([
                            dmc.AccordionControl(
                                "Additional Options",
                                icon=DashIconify(icon="solar:settings-bold", width=20)
                            ),
                            dmc.AccordionPanel([
                                dmc.Checkbox(
                                    id="calc-tempered",
                                    label="Tempered Glass (+35% safety glass markup)"
                                )
                            ])
                        ], value="additional-options")
                    ], variant="separated"),

                ], gap="md")
            ], withBorder=True, shadow="sm", p="lg")
        ], span=7),

        # RIGHT COLUMN - Sticky Price Summary (40%)
        dmc.GridCol([
            dmc.Card([
                dmc.Stack([
                    dmc.Group([
                        DashIconify(icon="solar:calculator-bold-duotone", width=24, color="#228BE6"),
                        dmc.Text("Price Summary", size="lg", fw=700)
                    ], gap="xs"),

                    dmc.Divider(),

                    # Live price display
                    html.Div(id="calc-live-price-display"),

                    # Calculate Button
                    dmc.Button(
                        "Calculate Full Quote",
                        id="calc-button",
                        fullWidth=True,
                        size="lg",
                        leftSection=DashIconify(icon="solar:calculator-bold", width=20),
                        mt="md"
                    )
                ], gap="md")
            ], withBorder=True, shadow="md", p="lg", style={"position": "sticky", "top": "20px"})
        ], span=5),
    ], gutter="lg"),

    # Full Results Display (appears below after calculation)
    html.Div(id="calc-results-container")

], gap="md")


# Callback to show/hide diameter input
@callback(
    Output("calc-diameter", "style"),
    Input("calc-shape", "value")
)
def toggle_diameter(shape):
    """Show diameter input only for circular shape"""
    if shape == "circular":
        return {"display": "block"}
    return {"display": "none"}


# Callback to show/hide clip size selector
@callback(
    Output("calc-clip-size", "style"),
    Input("calc-clipped-corners", "value")
)
def toggle_clip_size(num_corners):
    """Show clip size only when corners > 0"""
    if num_corners and num_corners > 0:
        return {"display": "block"}
    return {"display": "none"}


# Callback to disable/enable controls based on glass config and selections
@callback(
    [
        Output("calc-tempered", "disabled"),
        Output("calc-polish", "disabled"),
        Output("calc-beveled", "disabled"),
        Output("calc-clipped-corners", "disabled"),
    ],
    [
        Input("calc-thickness", "value"),
        Input("calc-glass-type", "value"),
        Input("calc-shape", "value"),
    ],
    State("session-store", "data"),
    prevent_initial_call=False
)
def update_control_availability(thickness, glass_type, shape, session_data):
    """
    Disable controls based on glass configuration rules:
    - 1/8" glass: Cannot be tempered, beveled
    - Mirrors: Cannot be tempered, cannot have clipped corners
    - Circular: Cannot have clipped corners
    """
    # Default: all enabled
    tempered_disabled = False
    polish_disabled = False
    beveled_disabled = False
    clipped_disabled = False

    # Rule 1: 1/8" glass cannot have ANY edge work (no polish, no bevel, no tempered)
    if thickness == '1/8"':
        tempered_disabled = True
        polish_disabled = True
        beveled_disabled = True

    # Rule 2: Mirrors cannot be tempered
    if glass_type == 'mirror':
        tempered_disabled = True

    # Rule 3: Circular glass cannot have clipped corners
    if shape == 'circular':
        clipped_disabled = True

    # Rule 4: Mirrors cannot have clipped corners (glass type only feature)
    if glass_type == 'mirror':
        clipped_disabled = True

    return tempered_disabled, polish_disabled, beveled_disabled, clipped_disabled


# Callback to auto-uncheck disabled controls and show helper text
@callback(
    [
        Output("calc-tempered", "checked"),
        Output("calc-polish", "checked"),
        Output("calc-beveled", "checked"),
        Output("calc-clipped-corners", "value"),
        Output("calc-glass-type", "data"),  # Update available glass types based on thickness
    ],
    [
        Input("calc-tempered", "disabled"),
        Input("calc-polish", "disabled"),
        Input("calc-beveled", "disabled"),
        Input("calc-clipped-corners", "disabled"),
        Input("calc-thickness", "value"),
    ],
    [
        State("calc-tempered", "checked"),
        State("calc-polish", "checked"),
        State("calc-beveled", "checked"),
        State("calc-clipped-corners", "value"),
    ],
    prevent_initial_call=False
)
def auto_uncheck_disabled_controls(
    tempered_disabled, polish_disabled, beveled_disabled, clipped_disabled, thickness,
    tempered_checked, polish_checked, beveled_checked, clipped_value
):
    """
    Auto-uncheck controls when they become disabled
    Also update available glass types based on thickness (1/8" cannot be mirror)
    """
    # Uncheck if disabled
    if tempered_disabled and tempered_checked:
        tempered_checked = False

    if polish_disabled and polish_checked:
        polish_checked = False

    if beveled_disabled and beveled_checked:
        beveled_checked = False

    if clipped_disabled and clipped_value and clipped_value > 0:
        clipped_value = 0

    # Update glass type options based on thickness
    # 1/8" glass should not allow mirror
    if thickness == '1/8"':
        glass_types = [
            {"value": "clear", "label": "Clear Glass"},
            {"value": "bronze", "label": "Bronze"},
            {"value": "gray", "label": "Gray"}
        ]
    else:
        glass_types = [
            {"value": "clear", "label": "Clear Glass"},
            {"value": "bronze", "label": "Bronze"},
            {"value": "gray", "label": "Gray"},
            {"value": "mirror", "label": "Mirror"}
        ]

    return tempered_checked, polish_checked, beveled_checked, clipped_value, glass_types


# Callback to auto-switch glass type from mirror when 1/8" is selected
@callback(
    Output("calc-glass-type", "value"),
    Input("calc-thickness", "value"),
    State("calc-glass-type", "value"),
    prevent_initial_call=False
)
def reset_glass_type_for_1_8(thickness, current_glass_type):
    """
    If user selects 1/8" thickness while mirror is selected,
    automatically switch to clear glass since 1/8" mirror is not valid
    """
    if thickness == '1/8"' and current_glass_type == 'mirror':
        return "clear"
    return current_glass_type


# Callback to show minimum sq ft warning
@callback(
    Output("calc-min-warning-container", "children"),
    Input("calc-width", "value"),
    Input("calc-height", "value"),
    Input("calc-shape", "value"),
    Input("calc-diameter", "value"),
    prevent_initial_call=False
)
def show_minimum_warning(width_str, height_str, shape, diameter_str):
    """Show warning when dimensions are below 3 sq ft minimum"""
    import math

    try:
        current_sq_ft = 0

        if shape == "circular" and diameter_str:
            diameter = to_decimal(diameter_str)
            if diameter > 0:
                radius = diameter / 2
                current_sq_ft = (math.pi * radius * radius) / 144
        elif width_str and height_str:
            width = to_decimal(width_str)
            height = to_decimal(height_str)
            if width > 0 and height > 0:
                current_sq_ft = (width * height) / 144

        # Show warning if below minimum
        if current_sq_ft > 0 and current_sq_ft < 3.0:
            return dmc.Alert(
                f"Current: {current_sq_ft:.2f} sq ft - Minimum charge of 3 sq ft applies",
                color="orange",
                icon=DashIconify(icon="solar:info-circle-bold"),
                mt="sm"
            )
    except:
        pass  # Invalid input, don't show warning

    return None


# Live Price Preview Callback
@callback(
    Output("calc-live-price-display", "children"),
    Input("calc-width", "value"),
    Input("calc-height", "value"),
    Input("calc-glass-type", "value"),
    Input("calc-thickness", "value"),
    Input("calc-shape", "value"),
    Input("calc-diameter", "value"),
    Input("calc-polish", "checked"),
    Input("calc-beveled", "checked"),
    Input("calc-clipped-corners", "value"),
    Input("calc-clip-size", "value"),
    Input("calc-tempered", "checked"),
    Input("calc-contractor", "checked"),
    Input("calc-quantity", "value"),
    State("session-store", "data"),
    prevent_initial_call=False
)
def update_live_price(
    width_str, height_str, glass_type, thickness, shape, diameter_str,
    is_polished, is_beveled, num_clipped, clip_size, is_tempered, is_contractor, quantity,
    session_data
):
    """Update live price preview as user types"""

    try:
        # Need valid dimensions at minimum
        if not width_str or not height_str:
            return dmc.Stack([
                dmc.Text("Enter dimensions to see pricing", c="dimmed", size="sm", ta="center", mt="xl")
            ])

        # Parse measurements
        try:
            width = to_decimal(width_str)
            height = to_decimal(height_str)
        except:
            return dmc.Text("Invalid dimensions", c="red", size="sm", ta="center")

        # Parse diameter for circular
        diameter = None
        if shape == "circular":
            if not diameter_str:
                return dmc.Text("Enter diameter", c="dimmed", size="sm", ta="center")
            try:
                diameter = to_decimal(diameter_str)
            except:
                return dmc.Text("Invalid diameter", c="red", size="sm", ta="center")

        # Get database and config
        db = get_authenticated_db(session_data)
        if not db:
            return dmc.Text("Session expired", c="orange", size="sm", ta="center")

        config = db.get_calculator_config()
        if not config['glass_config']:
            return dmc.Text("Config error", c="orange", size="sm", ta="center")

        # Calculate
        calculator = GlassPriceCalculator(config)
        is_circular = (shape == "circular")
        is_non_rectangular = (shape == "non-rectangular")

        result = calculator.calculate_quote(
            width=width,
            height=height,
            thickness=thickness,
            glass_type=glass_type,
            quantity=quantity or 1,
            is_polished=is_polished or False,
            is_beveled=is_beveled or False,
            num_clipped_corners=num_clipped or 0,
            clip_size=clip_size or "under_1",
            is_tempered=is_tempered or False,
            is_non_rectangular=is_non_rectangular,
            is_circular=is_circular,
            diameter=diameter,
            is_contractor=is_contractor or False
        )

        # Check for validation errors
        if 'error' in result and result['error']:
            return dmc.Alert(
                result['error'],
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold"),
                title="Invalid Configuration"
            )

        # Build compact live preview
        return dmc.Stack([
            # Square footage
            dmc.Group([
                dmc.Text("Area:", size="xs", c="dimmed"),
                dmc.Badge(f"{result['billable_sq_ft']} sq ft", color="gray", size="sm")
            ], justify="space-between"),

            dmc.Divider(variant="dashed"),

            # Base price
            dmc.Group([
                dmc.Text("Base:", size="sm"),
                dmc.Text(f"${result['base_price']:.2f}", size="sm", fw=500)
            ], justify="space-between"),

            # Edge work (if any)
            *([dmc.Group([
                dmc.Text("Edges:", size="sm"),
                dmc.Text(
                    f"${(result['polish_price'] or 0) + (result['beveled_price'] or 0) + (result['clipped_corners_price'] or 0):.2f}",
                    size="sm",
                    fw=500
                )
            ], justify="space-between")] if (result['polish_price'] or result['beveled_price'] or result['clipped_corners_price']) else []),

            # Markups (if any)
            *([dmc.Group([
                dmc.Text("Markups:", size="sm"),
                dmc.Text(
                    f"${(result['tempered_price'] or 0) + (result['shape_price'] or 0):.2f}",
                    size="sm",
                    fw=500
                )
            ], justify="space-between")] if (result['tempered_price'] or result['shape_price']) else []),

            # Discount (if applicable)
            *([dmc.Group([
                dmc.Text("Discount:", size="sm", c="green"),
                dmc.Text(f"-${result['contractor_discount']:.2f}", size="sm", fw=500, c="green")
            ], justify="space-between")] if result['contractor_discount'] else []),

            dmc.Divider(),

            # Final Quote Price
            dmc.Stack([
                dmc.Text("Estimated Quote", size="xs", c="dimmed", ta="center"),
                dmc.Text(
                    f"${result['quote_price']:.2f}",
                    size="2rem",
                    fw=700,
                    c="blue",
                    ta="center"
                ),
                *([dmc.Text(f"×{quantity} pieces", size="xs", c="dimmed", ta="center")] if quantity and quantity > 1 else [])
            ], gap=2)
        ], gap="xs")

    except Exception as e:
        print(f"Live preview error: {e}")
        traceback.print_exc()
        return dmc.Text("Calculation error", c="red", size="sm", ta="center")


# Main calculation callback (full detailed breakdown)
@callback(
    Output("calc-results-container", "children"),
    Input("calc-button", "n_clicks"),
    State("calc-width", "value"),
    State("calc-height", "value"),
    State("calc-glass-type", "value"),
    State("calc-thickness", "value"),
    State("calc-shape", "value"),
    State("calc-diameter", "value"),
    State("calc-polish", "checked"),
    State("calc-beveled", "checked"),
    State("calc-clipped-corners", "value"),
    State("calc-clip-size", "value"),
    State("calc-tempered", "checked"),
    State("calc-contractor", "checked"),
    State("calc-quantity", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def calculate_full_quote(
    n_clicks, width_str, height_str, glass_type, thickness, shape, diameter_str,
    is_polished, is_beveled, num_clipped, clip_size, is_tempered, is_contractor, quantity,
    session_data
):
    """Calculate full quote with detailed breakdown"""

    try:
        # Validate inputs
        if not width_str or not height_str:
            return dmc.Alert(
                "Please enter width and height",
                title="Missing Dimensions",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold")
            )

        # Parse measurements
        try:
            width = to_decimal(width_str)
            height = to_decimal(height_str)
        except Exception as e:
            return dmc.Alert(
                f"Invalid dimension format. Use numbers, decimals, or fractions like '24 1/2'",
                title="Invalid Input",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold")
            )

        # Parse diameter for circular
        diameter = None
        if shape == "circular":
            if not diameter_str:
                return dmc.Alert(
                    "Please enter diameter for circular glass",
                    title="Missing Diameter",
                    color="red",
                    icon=DashIconify(icon="solar:danger-circle-bold")
                )
            try:
                diameter = to_decimal(diameter_str)
            except Exception as e:
                return dmc.Alert(
                    f"Invalid diameter format",
                    title="Invalid Input",
                    color="red",
                    icon=DashIconify(icon="solar:danger-circle-bold")
                )

        # Get database instance
        db = get_authenticated_db(session_data)

        if not db:
            return dmc.Alert(
                "Session expired. Please refresh the page and log in again.",
                title="Authentication Required",
                color="orange",
                icon=DashIconify(icon="solar:shield-warning-bold")
            )

        # Get pricing configuration
        config = db.get_calculator_config()

        if not config['glass_config']:
            return dmc.Alert(
                "Glass pricing configuration not found. Please contact administrator.",
                title="Configuration Error",
                color="orange",
                icon=DashIconify(icon="solar:danger-triangle-bold")
            )

        # Create calculator
        calculator = GlassPriceCalculator(config)

        # Determine shape flags
        is_circular = (shape == "circular")
        is_non_rectangular = (shape == "non-rectangular")

        # Calculate quote
        result = calculator.calculate_quote(
            width=width,
            height=height,
            thickness=thickness,
            glass_type=glass_type,
            quantity=quantity or 1,
            is_polished=is_polished or False,
            is_beveled=is_beveled or False,
            num_clipped_corners=num_clipped or 0,
            clip_size=clip_size or "under_1",
            is_tempered=is_tempered or False,
            is_non_rectangular=is_non_rectangular,
            is_circular=is_circular,
            diameter=diameter,
            is_contractor=is_contractor or False
        )

        # Check for validation errors
        if 'error' in result and result['error']:
            return dmc.Alert(
                result['error'],
                title="Invalid Configuration",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold")
            )

        # Build detailed results display
        # Determine sq ft display text
        sq_ft_text = f"{result['billable_sq_ft']} sq ft"
        if result['actual_sq_ft'] < 3.0:
            sq_ft_text = f"{result['actual_sq_ft']} sq ft (billed as {result['billable_sq_ft']} sq ft)"

        return dmc.Card([
            dmc.Stack([
                dmc.Group([
                    dmc.Text("Detailed Quote Breakdown", size="xl", fw=700),
                    dmc.Badge(sq_ft_text, color="blue", size="lg")
                ], justify="space-between"),

                dmc.Divider(),

                # Price Breakdown
                dmc.Stack([
                    # Base Price
                    dmc.Group([
                        dmc.Text("Base Price:", size="sm", c="dimmed"),
                        dmc.Text(f"${result['base_price']:.2f}", size="sm", fw=600)
                    ], justify="space-between"),

                    # Polish (if applicable)
                    *([dmc.Group([
                        dmc.Text(f"Polish ({result['perimeter']:.2f}\" perimeter):", size="sm", c="dimmed"),
                        dmc.Text(f"${result['polish_price']:.2f}", size="sm", fw=600)
                    ], justify="space-between")] if result['polish_price'] else []),

                    # Beveled (if applicable)
                    *([dmc.Group([
                        dmc.Text("Beveled Edges:", size="sm", c="dimmed"),
                        dmc.Text(f"${result['beveled_price']:.2f}", size="sm", fw=600)
                    ], justify="space-between")] if result['beveled_price'] else []),

                    # Clipped Corners (if applicable)
                    *([dmc.Group([
                        dmc.Text(f"Clipped Corners ({num_clipped}):", size="sm", c="dimmed"),
                        dmc.Text(f"${result['clipped_corners_price']:.2f}", size="sm", fw=600)
                    ], justify="space-between")] if result['clipped_corners_price'] else []),

                    dmc.Divider(variant="dashed"),

                    # Before Markups
                    dmc.Group([
                        dmc.Text("Before Markups:", size="sm", fw=600),
                        dmc.Text(f"${result['before_markups']:.2f}", size="sm", fw=600)
                    ], justify="space-between"),

                    # Tempered Markup (if applicable)
                    *([dmc.Group([
                        dmc.Text("Tempered Markup (35%):", size="sm", c="dimmed"),
                        dmc.Text(f"${result['tempered_price']:.2f}", size="sm", fw=600)
                    ], justify="space-between")] if result['tempered_price'] else []),

                    # Shape Markup (if applicable)
                    *([dmc.Group([
                        dmc.Text("Shape Markup (25%):", size="sm", c="dimmed"),
                        dmc.Text(f"${result['shape_price']:.2f}", size="sm", fw=600)
                    ], justify="space-between")] if result['shape_price'] else []),

                    dmc.Divider(),

                    # Subtotal
                    dmc.Group([
                        dmc.Text("Subtotal:", size="md", fw=600),
                        dmc.Text(f"${result['subtotal']:.2f}", size="md", fw=600)
                    ], justify="space-between"),

                    # Contractor Discount (if applicable)
                    *([dmc.Group([
                        dmc.Text("Contractor Discount (15%):", size="sm", c="green"),
                        dmc.Text(f"-${result['contractor_discount']:.2f}", size="sm", c="green", fw=600)
                    ], justify="space-between")] if result['contractor_discount'] else []),

                    # Discounted Subtotal (if discount applied)
                    *([dmc.Group([
                        dmc.Text("After Discount:", size="md", fw=600),
                        dmc.Text(f"${result['discounted_subtotal']:.2f}", size="md", fw=600)
                    ], justify="space-between")] if result['discounted_subtotal'] else []),

                    # Quantity
                    *([dmc.Group([
                        dmc.Text(f"Quantity (×{quantity}):", size="sm", c="dimmed"),
                        dmc.Text(f"${result['total']:.2f}", size="sm", fw=600)
                    ], justify="space-between")] if quantity > 1 else []),

                    dmc.Divider(size="md"),

                    # FINAL QUOTE PRICE (ULTIMATE FORMULA)
                    dmc.Card([
                        dmc.Stack([
                            dmc.Text("Final Quote Price", size="sm", c="dimmed", ta="center"),
                            dmc.Text(
                                f"${result['quote_price']:.2f}",
                                size="2.5rem",
                                fw=700,
                                c="blue",
                                ta="center"
                            ),
                            dmc.Text(
                                "Total ÷ 0.28 (Ultimate Formula)",
                                size="xs",
                                c="dimmed",
                                ta="center",
                                fs="italic"
                            )
                        ], gap="xs")
                    ], withBorder=True, p="md", style={"backgroundColor": "#f0f7ff"}),

                ], gap="xs")
            ], gap="md")
        ], withBorder=True, shadow="md", p="lg", style={"backgroundColor": "white"}, mt="lg")

    except Exception as e:
        print(f"Calculator error: {e}")
        print(traceback.format_exc())
        return dmc.Alert(
            f"Error calculating price: {str(e)}",
            title="Calculation Error",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold")
        )
