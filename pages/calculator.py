"""
Glass Calculator Page
Main glass pricing calculator with real-time quote generation

Features:
- Dimension inputs with fraction support ("24 1/2")
- Glass type and thickness selection
- Edge processing options (polish, beveled, clipped corners)
- Tempered glass option
- Contractor discount
- Real-time price calculation
- ULTIMATE FORMULA: Quote Price = Total ÷ 0.28
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
        dmc.Badge("Quote Generator", color="blue", variant="light")
    ], justify="space-between"),

    dmc.Text("Calculate accurate glass pricing with fraction support", c="dimmed", size="sm"),

    dmc.Space(h=10),

    # Calculator Form
    dmc.Card([
        dmc.Stack([
            # Dimensions Section
            dmc.Text("Dimensions", size="lg", fw=600),

            dmc.Grid([
                dmc.GridCol([
                    dmc.TextInput(
                        id="calc-width",
                        label="Width (inches)",
                        placeholder="24 or 24 1/2",
                        description="Supports fractions: 24, 24.5, 24 1/2, or 3/4",
                        required=True
                    )
                ], span=6),

                dmc.GridCol([
                    dmc.TextInput(
                        id="calc-height",
                        label="Height (inches)",
                        placeholder="36 or 36 3/4",
                        description="Supports fractions: 36, 36.75, 36 3/4",
                        required=True
                    )
                ], span=6),
            ]),

            # Glass Type & Thickness
            dmc.Text("Glass Configuration", size="lg", fw=600, mt="md"),

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

            # Shape Options
            dmc.Text("Shape", size="lg", fw=600, mt="md"),

            dmc.RadioGroup(
                id="calc-shape",
                value="rectangular",
                children=[
                    dmc.Radio(label="Rectangular", value="rectangular"),
                    dmc.Radio(label="Circular", value="circular"),
                    dmc.Radio(label="Non-Rectangular (Custom)", value="non-rectangular"),
                ],
                mb="sm"
            ),

            # Diameter input (shown for circular)
            html.Div(id="diameter-container"),

            # Edge Processing
            dmc.Text("Edge Processing", size="lg", fw=600, mt="md"),

            dmc.Stack([
                dmc.Checkbox(
                    id="calc-polish",
                    label="Polished Edges",
                    description="Clean, smooth edges"
                ),
                dmc.Checkbox(
                    id="calc-beveled",
                    label="Beveled Edges",
                    description="Angled decorative edges (not available for 1/8\")"
                ),
                dmc.Group([
                    dmc.NumberInput(
                        id="calc-clipped-corners",
                        label="Clipped Corners",
                        description="Number of corners to clip",
                        min=0,
                        max=4,
                        value=0,
                        step=1,
                        style={"width": "200px"}
                    ),
                    dmc.Select(
                        id="calc-clip-size",
                        label="Clip Size",
                        data=[
                            {"value": "under_1", "label": "Under 1 inch"},
                            {"value": "over_1", "label": "Over 1 inch"}
                        ],
                        value="under_1",
                        style={"width": "200px"}
                    )
                ], mt="xs")
            ], gap="xs"),

            # Additional Options
            dmc.Text("Additional Options", size="lg", fw=600, mt="md"),

            dmc.Stack([
                dmc.Checkbox(
                    id="calc-tempered",
                    label="Tempered Glass",
                    description="Safety glass - adds 35% markup (not available for mirrors)"
                ),
                dmc.Checkbox(
                    id="calc-contractor",
                    label="Contractor Discount",
                    description="Apply 15% contractor discount"
                ),
            ], gap="xs"),

            # Quantity
            dmc.NumberInput(
                id="calc-quantity",
                label="Quantity",
                description="Number of pieces",
                min=1,
                max=999,
                value=1,
                step=1,
                mt="md"
            ),

            # Calculate Button
            dmc.Button(
                "Calculate Price",
                id="calc-button",
                fullWidth=True,
                size="lg",
                leftSection=DashIconify(icon="solar:calculator-bold", width=20),
                mt="lg"
            )
        ], gap="md")
    ], withBorder=True, shadow="sm", p="lg"),

    # Results Display
    html.Div(id="calc-results-container")

], gap="md")


# Callback to show/hide diameter input
@callback(
    Output("diameter-container", "children"),
    Input("calc-shape", "value")
)
def toggle_diameter(shape):
    """Show diameter input only for circular shape"""
    if shape == "circular":
        return dmc.TextInput(
            id="calc-diameter",
            label="Diameter (inches)",
            placeholder="Enter diameter",
            description="Supports fractions",
            required=True,
            mt="sm"
        )
    return html.Div(id="calc-diameter", style={"display": "none"})


# Main calculation callback
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
def calculate_price(
    n_clicks, width_str, height_str, glass_type, thickness, shape, diameter_str,
    is_polished, is_beveled, num_clipped, clip_size, is_tempered, is_contractor, quantity,
    session_data
):
    """Calculate glass price and display results"""

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
            clip_size=clip_size,
            is_tempered=is_tempered or False,
            is_non_rectangular=is_non_rectangular,
            is_circular=is_circular,
            diameter=diameter,
            is_contractor=is_contractor or False
        )

        # Build results display
        return dmc.Card([
            dmc.Stack([
                dmc.Group([
                    dmc.Text("Quote Results", size="xl", fw=700),
                    dmc.Badge(f"{result['sq_ft']} sq ft", color="blue", size="lg")
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
        ], withBorder=True, shadow="md", p="lg", style={"backgroundColor": "white"})

    except Exception as e:
        print(f"Calculator error: {e}")
        print(traceback.format_exc())
        return dmc.Alert(
            f"Error calculating price: {str(e)}",
            title="Calculation Error",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold")
        )
