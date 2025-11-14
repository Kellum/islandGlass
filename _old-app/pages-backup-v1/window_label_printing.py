"""
Window Label Printing Page
Print queue and label management for window orders

Features:
- Print queue grouped by PO
- Individual label cards with preview
- Print buttons (single, batch, all)
- Label preview modal
- Print history section
- Printer status indicator
"""

import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, ALL, MATCH, ctx
from dash_iconify import DashIconify
from datetime import datetime
from modules.database import get_authenticated_db
from modules.permissions import get_user_window_permissions
from modules.zpl_generator import ZPLGenerator
from modules.label_printer import LabelPrinter
from modules.fraction_utils import format_fraction
from fractions import Fraction

# Initialize printer in mock mode
label_printer = LabelPrinter(mock_mode=True)
zpl_generator = ZPLGenerator()


def layout(session_data=None):
    """Page layout for label printing"""

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

    if not perms.can_print_labels():
        return html.Div([
            dmc.Alert(
                "You don't have permission to print labels",
                title="Access Denied",
                color="red"
            )
        ])

    # Get printer status
    printer_status = label_printer.get_status()
    printer_color = "green" if printer_status == "online" else "red"

    return dmc.Stack([
        # Store for session data
        dcc.Store(id='wlp-session-store', data=session_data),
        dcc.Store(id='wlp-selected-labels', data=[]),

        # Header with printer status
        dmc.Group([
            dmc.Stack([
                dmc.Title("Label Printing", order=1),
                dmc.Text("Manage and print window labels", c="dimmed", size="sm")
            ], gap=0),
            dmc.Group([
                dmc.Badge(
                    [
                        DashIconify(icon="mdi:printer", width=16, style={"marginRight": "5px"}),
                        f"Printer: {printer_status.title()}"
                    ],
                    color=printer_color,
                    size="lg",
                    variant="light"
                ),
                dmc.Button(
                    "Refresh",
                    id="wlp-refresh-btn",
                    leftSection=DashIconify(icon="mdi:refresh"),
                    variant="light"
                ),
            ], gap="xs"),
        ], justify="space-between"),

        dmc.Space(h=10),

        # Filter/Actions Card
        dmc.Card([
            dmc.Stack([
                dmc.Group([
                    dmc.Text("Print Queue", size="lg", fw=600),
                    dmc.Badge(
                        id="wlp-pending-count",
                        children="0 pending",
                        color="blue",
                        size="lg",
                        variant="light"
                    ),
                ], justify="space-between"),

                # Filters
                dmc.Grid([
                    dmc.GridCol([
                        dmc.Select(
                            id="wlp-filter-status",
                            label="Label Status",
                            placeholder="All labels",
                            data=[
                                {"label": "All", "value": "all"},
                                {"label": "Pending", "value": "pending"},
                                {"label": "Printed", "value": "printed"},
                            ],
                            value="pending",
                            clearable=True
                        )
                    ], span={"base": 12, "sm": 6, "md": 4}),

                    dmc.GridCol([
                        dmc.TextInput(
                            id="wlp-filter-po",
                            label="Filter by PO",
                            placeholder="Search PO number...",
                            leftSection=DashIconify(icon="mdi:magnify")
                        )
                    ], span={"base": 12, "sm": 6, "md": 4}),
                ], gutter="md"),

                # Batch actions
                dmc.Group([
                    dmc.Button(
                        "Print All Pending",
                        id="wlp-print-all-btn",
                        leftSection=DashIconify(icon="mdi:printer-check"),
                        variant="filled",
                        color="blue"
                    ),
                    dmc.Button(
                        "Print Selected",
                        id="wlp-print-selected-btn",
                        leftSection=DashIconify(icon="mdi:printer"),
                        variant="light",
                        color="blue",
                        disabled=True
                    ),
                    dmc.Button(
                        "Test Printer",
                        id="wlp-test-printer-btn",
                        leftSection=DashIconify(icon="mdi:printer-settings"),
                        variant="subtle"
                    ),
                ], gap="xs"),
            ], gap="md")
        ], withBorder=True, padding="lg", radius="md", mb="lg"),

        # Labels container (grouped by PO)
        html.Div(id="wlp-labels-container"),

        # Print history section
        dmc.Accordion(
            id="wlp-history-accordion",
            value=[],
            children=[
                dmc.AccordionItem(
                    [
                        dmc.AccordionControl(
                            "Print History",
                            icon=DashIconify(icon="mdi:history", width=20)
                        ),
                        dmc.AccordionPanel(
                            html.Div(id="wlp-history-content")
                        ),
                    ],
                    value="history"
                )
            ]
        ),

        # Label preview modal
        dmc.Modal(
            id="wlp-preview-modal",
            title="Label Preview",
            size="lg",
            children=[
                html.Div(id="wlp-preview-content")
            ]
        ),

        # Notification container
        html.Div(id="wlp-notifications"),
    ], gap="md", p="md")


# Callback: Load labels
@callback(
    Output("wlp-labels-container", "children"),
    Output("wlp-pending-count", "children"),
    Input("wlp-refresh-btn", "n_clicks"),
    Input("wlp-filter-status", "value"),
    Input("wlp-filter-po", "value"),
    State("wlp-session-store", "data"),
    prevent_initial_call=False
)
def load_labels(n_clicks, status_filter, po_filter, session_data):
    """Load and display labels grouped by PO"""

    if not session_data:
        return dmc.Alert("Session expired", color="red"), "0 pending"

    try:
        db = get_authenticated_db(session_data)
        company_id = session_data.get('user_profile', {}).get('company_id')

        if not company_id:
            return dmc.Alert("Company ID not found", color="red"), "0 pending"

        # Get labels based on filter
        if not status_filter or status_filter == "all":
            labels = db.get_pending_labels(company_id)
            # Also get printed labels
            printed = db.get_window_labels(company_id, status="printed")
            labels.extend(printed if printed else [])
        elif status_filter == "pending":
            labels = db.get_pending_labels(company_id)
        elif status_filter == "printed":
            labels = db.get_window_labels(company_id, status="printed")
        else:
            labels = []

        # Filter by PO if specified
        if po_filter:
            labels = [l for l in labels if po_filter.lower() in l.get('po_number', '').lower()]

        # Count pending
        pending_count = len([l for l in labels if l.get('print_status') == 'pending'])
        pending_badge = f"{pending_count} pending"

        if not labels:
            return dmc.Center([
                dmc.Stack([
                    DashIconify(icon="mdi:label-off-outline", width=64, color="gray"),
                    dmc.Text("No labels found", size="lg", c="dimmed"),
                    dmc.Text("Labels will appear here once orders are created", size="sm", c="dimmed"),
                ], align="center")
            ], style={"minHeight": "300px"}), pending_badge

        # Group labels by PO number
        labels_by_po = {}
        for label in labels:
            po = label.get('po_number', 'Unknown')
            if po not in labels_by_po:
                labels_by_po[po] = []
            labels_by_po[po].append(label)

        # Create accordion items for each PO
        accordion_items = []
        for po_number, po_labels in labels_by_po.items():
            pending_in_po = len([l for l in po_labels if l.get('print_status') == 'pending'])
            total_in_po = len(po_labels)

            accordion_items.append(
                dmc.AccordionItem([
                    dmc.AccordionControl(
                        dmc.Group([
                            dmc.Text(f"PO: {po_number}", fw=600),
                            dmc.Badge(
                                f"{pending_in_po}/{total_in_po} pending",
                                color="blue" if pending_in_po > 0 else "gray",
                                variant="light"
                            ),
                        ], justify="space-between")
                    ),
                    dmc.AccordionPanel(
                        create_label_cards(po_labels)
                    ),
                ], value=po_number)
            )

        return dmc.Accordion(
            accordion_items,
            multiple=True,
            variant="separated",
            value=[list(labels_by_po.keys())[0]] if labels_by_po else []  # Open first PO
        ), pending_badge

    except Exception as e:
        return dmc.Alert(f"Error loading labels: {str(e)}", color="red"), "0 pending"


def create_label_cards(labels):
    """Create label cards for a PO"""

    cards = []
    for label in labels:
        card = create_single_label_card(label)
        cards.append(card)

    return dmc.Stack(cards, gap="sm")


def create_single_label_card(label):
    """Create a single label card"""

    label_id = label.get('id')
    item_data = label.get('item_data', {})
    print_status = label.get('print_status', 'pending')
    printed_at = label.get('printed_at')
    label_number = label.get('label_number', 1)
    total_labels = label.get('total_labels', 1)

    # Extract window details
    window_type = item_data.get('window_type', 'Unknown')
    width = item_data.get('width')
    height = item_data.get('height')
    thickness = item_data.get('thickness')

    # Format measurements
    try:
        width_str = format_fraction(Fraction(width).limit_denominator(16)) if width else 'N/A'
        height_str = format_fraction(Fraction(height).limit_denominator(16)) if height else 'N/A'
        thickness_str = format_fraction(Fraction(thickness).limit_denominator(16)) if thickness else 'N/A'
    except:
        width_str = str(width) if width else 'N/A'
        height_str = str(height) if height else 'N/A'
        thickness_str = str(thickness) if thickness else 'N/A'

    # Status badge
    status_badge = dmc.Badge(
        print_status.title(),
        color="green" if print_status == "printed" else "yellow",
        size="sm",
        variant="light"
    )

    # Print time
    print_time = ""
    if printed_at:
        try:
            dt = datetime.fromisoformat(printed_at.replace('Z', '+00:00'))
            print_time = dt.strftime('%b %d, %I:%M %p')
        except:
            print_time = printed_at

    return dmc.Card([
        dmc.Group([
            # Label info
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="mdi:label", width=20, color="blue"),
                    dmc.Text(f"Label {label_number}/{total_labels}", size="sm", fw=600),
                    status_badge,
                ], gap=5),
                dmc.Text(f"{window_type}: {width_str}\" × {height_str}\" × {thickness_str}\"", size="sm"),
                dmc.Text(f"Printed: {print_time}", size="xs", c="dimmed") if printed_at else None,
            ], gap=3),

            # Actions
            dmc.Group([
                dmc.Checkbox(
                    id={"type": "wlp-label-checkbox", "index": label_id},
                    checked=False,
                    size="sm"
                ) if print_status == "pending" else None,
                dmc.ActionIcon(
                    DashIconify(icon="mdi:eye", width=18),
                    id={"type": "wlp-preview-label-btn", "index": label_id},
                    variant="subtle",
                    size="sm",
                    color="blue"
                ),
                dmc.Button(
                    "Print",
                    id={"type": "wlp-print-single-btn", "index": label_id},
                    leftSection=DashIconify(icon="mdi:printer", width=16),
                    variant="light" if print_status == "pending" else "subtle",
                    size="xs",
                    color="blue",
                    disabled=(print_status == "printed")
                ),
            ], gap=5),
        ], justify="space-between", align="flex-start"),
    ], withBorder=True, padding="sm", radius="md")


# Callback: Print single label
@callback(
    Output("wlp-notifications", "children", allow_duplicate=True),
    Output("wlp-refresh-btn", "n_clicks", allow_duplicate=True),
    Input({"type": "wlp-print-single-btn", "index": ALL}, "n_clicks"),
    State({"type": "wlp-print-single-btn", "index": ALL}, "id"),
    State("wlp-session-store", "data"),
    State("wlp-refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def print_single_label(n_clicks_list, btn_ids, session_data, refresh_clicks):
    """Print a single label"""

    if not any(n_clicks_list):
        return dash.no_update, dash.no_update

    triggered_id = ctx.triggered_id
    if not triggered_id:
        return dash.no_update, dash.no_update

    label_id = triggered_id['index']

    try:
        db = get_authenticated_db(session_data)
        user_id = session_data.get('user', {}).get('id')

        # Get label data
        label = db.get_label_by_id(label_id)
        if not label:
            raise Exception("Label not found")

        # Generate ZPL
        zpl_code = generate_zpl_for_label(label)

        # Print (mock mode)
        success, message = label_printer.print_label(zpl_code, filename=f"label_{label_id}")

        if success:
            # Update print status
            db.update_label_print_status(label_id, "printed", user_id, zpl_code)

            notification = dmc.Notification(
                title="Success",
                message=f"Label printed successfully. {message}",
                color="green",
                action="show",
                autoClose=3000,
                icon=DashIconify(icon="mdi:check")
            )
            return notification, (refresh_clicks or 0) + 1
        else:
            raise Exception(message)

    except Exception as e:
        notification = dmc.Notification(
            title="Print Failed",
            message=str(e),
            color="red",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="mdi:alert")
        )
        return notification, dash.no_update


# Callback: Print all pending
@callback(
    Output("wlp-notifications", "children", allow_duplicate=True),
    Output("wlp-refresh-btn", "n_clicks", allow_duplicate=True),
    Input("wlp-print-all-btn", "n_clicks"),
    State("wlp-session-store", "data"),
    State("wlp-refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def print_all_pending(n_clicks, session_data, refresh_clicks):
    """Print all pending labels"""

    if not n_clicks:
        return dash.no_update, dash.no_update

    try:
        db = get_authenticated_db(session_data)
        user_id = session_data.get('user', {}).get('id')
        company_id = session_data.get('user_profile', {}).get('company_id')

        # Get all pending labels
        labels = db.get_pending_labels(company_id)

        if not labels:
            notification = dmc.Notification(
                title="No Pending Labels",
                message="There are no pending labels to print",
                color="yellow",
                action="show",
                autoClose=3000,
                icon=DashIconify(icon="mdi:information")
            )
            return notification, dash.no_update

        # Print each label
        success_count = 0
        for label in labels:
            try:
                zpl_code = generate_zpl_for_label(label)
                success, message = label_printer.print_label(
                    zpl_code,
                    filename=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_label{label['id']}"
                )
                if success:
                    db.update_label_print_status(label['id'], "printed", user_id, zpl_code)
                    success_count += 1
            except Exception as e:
                print(f"Error printing label {label['id']}: {e}")
                continue

        notification = dmc.Notification(
            title="Batch Print Complete",
            message=f"Successfully printed {success_count} of {len(labels)} labels",
            color="green" if success_count == len(labels) else "yellow",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="mdi:check-all")
        )
        return notification, (refresh_clicks or 0) + 1

    except Exception as e:
        notification = dmc.Notification(
            title="Batch Print Failed",
            message=str(e),
            color="red",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="mdi:alert")
        )
        return notification, dash.no_update


# Callback: Test printer
@callback(
    Output("wlp-notifications", "children", allow_duplicate=True),
    Input("wlp-test-printer-btn", "n_clicks"),
    prevent_initial_call=True
)
def test_printer(n_clicks):
    """Test printer connection"""

    if not n_clicks:
        return dash.no_update

    try:
        success, message = label_printer.test_connection()

        notification = dmc.Notification(
            title="Printer Test",
            message=message,
            color="green" if success else "red",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="mdi:printer-check" if success else "mdi:printer-alert")
        )
        return notification

    except Exception as e:
        notification = dmc.Notification(
            title="Test Failed",
            message=str(e),
            color="red",
            action="show",
            autoClose=5000,
            icon=DashIconify(icon="mdi:alert")
        )
        return notification


# Callback: Preview label
@callback(
    Output("wlp-preview-modal", "opened"),
    Output("wlp-preview-content", "children"),
    Input({"type": "wlp-preview-label-btn", "index": ALL}, "n_clicks"),
    State({"type": "wlp-preview-label-btn", "index": ALL}, "id"),
    State("wlp-session-store", "data"),
    prevent_initial_call=True
)
def preview_label(n_clicks_list, btn_ids, session_data):
    """Show label preview"""

    if not any(n_clicks_list):
        return dash.no_update, dash.no_update

    triggered_id = ctx.triggered_id
    if not triggered_id:
        return dash.no_update, dash.no_update

    label_id = triggered_id['index']

    try:
        db = get_authenticated_db(session_data)
        label = db.get_label_by_id(label_id)

        if not label:
            return False, dmc.Alert("Label not found", color="red")

        # Generate ZPL
        zpl_code = generate_zpl_for_label(label)

        # Create preview content
        item_data = label.get('item_data', {})
        po_number = label.get('po_number', 'N/A')

        preview_content = dmc.Stack([
            dmc.Text(f"PO Number: {po_number}", fw=600),
            dmc.Text(f"Label {label.get('label_number')}/{label.get('total_labels')}", size="sm", c="dimmed"),
            dmc.Divider(),
            dmc.Text("Window Details:", size="sm", fw=600, mt="md"),
            dmc.List([
                dmc.ListItem(f"Type: {item_data.get('window_type', 'N/A')}"),
                dmc.ListItem(f"Width: {item_data.get('width', 'N/A')}\""),
                dmc.ListItem(f"Height: {item_data.get('height', 'N/A')}\""),
                dmc.ListItem(f"Thickness: {item_data.get('thickness', 'N/A')}\""),
            ], size="sm"),
            dmc.Divider(),
            dmc.Text("ZPL Code:", size="sm", fw=600, mt="md"),
            dmc.Code(
                zpl_code,
                block=True,
                style={"maxHeight": "200px", "overflow": "auto"}
            ),
            dmc.Text(
                "View at: labelary.com/viewer.html",
                size="xs",
                c="dimmed",
                mt="xs"
            ),
        ])

        return True, preview_content

    except Exception as e:
        return True, dmc.Alert(f"Error: {str(e)}", color="red")


# Callback: Load print history
@callback(
    Output("wlp-history-content", "children"),
    Input("wlp-refresh-btn", "n_clicks"),
    State("wlp-session-store", "data"),
    prevent_initial_call=False
)
def load_print_history(n_clicks, session_data):
    """Load and display print history"""

    if not session_data:
        return dmc.Text("No history available", size="sm", c="dimmed")

    try:
        db = get_authenticated_db(session_data)
        company_id = session_data.get('user_profile', {}).get('company_id')

        # Get printed labels
        printed_labels = db.get_window_labels(company_id, status="printed")

        if not printed_labels:
            return dmc.Text("No print history yet", size="sm", c="dimmed")

        # Sort by printed_at descending
        printed_labels.sort(key=lambda x: x.get('printed_at', ''), reverse=True)

        # Take last 20
        recent_labels = printed_labels[:20]

        # Create history table
        rows = []
        for label in recent_labels:
            po_number = label.get('po_number', 'N/A')
            item_data = label.get('item_data', {})
            window_type = item_data.get('window_type', 'Unknown')
            printed_at = label.get('printed_at', '')

            try:
                dt = datetime.fromisoformat(printed_at.replace('Z', '+00:00'))
                time_str = dt.strftime('%b %d, %Y %I:%M %p')
            except:
                time_str = printed_at

            rows.append(
                html.Tr([
                    html.Td(po_number),
                    html.Td(window_type),
                    html.Td(f"{label.get('label_number')}/{label.get('total_labels')}"),
                    html.Td(time_str),
                ])
            )

        return dmc.Table([
            html.Thead([
                html.Tr([
                    html.Th("PO Number"),
                    html.Th("Window Type"),
                    html.Th("Label"),
                    html.Th("Printed At"),
                ])
            ]),
            html.Tbody(rows)
        ], striped=True, highlightOnHover=True, withTableBorder=True)

    except Exception as e:
        return dmc.Alert(f"Error loading history: {str(e)}", color="red", size="sm")


def generate_zpl_for_label(label):
    """Generate ZPL code for a label"""

    po_number = label.get('po_number', 'UNKNOWN')
    item_data = label.get('item_data', {})
    label_number = label.get('label_number', 1)
    total_labels = label.get('total_labels', 1)

    # Use ZPL generator
    zpl = zpl_generator.generate_window_label(
        po_number=po_number,
        window_data=item_data,
        label_number=label_number,
        total_labels=total_labels
    )

    return zpl
