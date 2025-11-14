"""
Job Detail Page - The One-Stop Hub
Complete project management for a single job/PO

Features:
- Job header with key info and status
- Work items (showers, windows, mirrors, etc.)
- Vendor materials tracking
- Site visits log
- File uploads (photos, PDFs)
- Employee comments/discussion
- Calendar/schedule
- Financial summary
"""

import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, ctx, ALL
from dash_iconify import DashIconify
from modules.database import get_authenticated_db
from datetime import datetime
import json

def layout(job_id=None, session_data=None):
    """Dynamic layout based on job_id"""

    if not job_id:
        return dmc.Alert("No job ID provided", color="red")

    return dmc.Stack([
        # Store job_id
        dcc.Store(id="current-job-id", data=job_id),
        dcc.Store(id="session-store", storage_type="session"),

        # Header Section
        html.Div(id="job-detail-header"),

        # Tabs for different sections
        dmc.Tabs(
            value="overview",
            children=[
                dmc.TabsList([
                    dmc.TabsTab("Overview", value="overview", leftSection=DashIconify(icon="solar:widget-5-bold", width=20)),
                    dmc.TabsTab("Work Items", value="work_items", leftSection=DashIconify(icon="solar:checklist-bold", width=20)),
                    dmc.TabsTab("Materials", value="materials", leftSection=DashIconify(icon="solar:box-bold", width=20)),
                    dmc.TabsTab("Site Visits", value="visits", leftSection=DashIconify(icon="solar:map-point-bold", width=20)),
                    dmc.TabsTab("Files", value="files", leftSection=DashIconify(icon="solar:gallery-bold", width=20)),
                    dmc.TabsTab("Comments", value="comments", leftSection=DashIconify(icon="solar:chat-round-bold", width=20)),
                    dmc.TabsTab("Schedule", value="schedule", leftSection=DashIconify(icon="solar:calendar-bold", width=20)),
                ]),

                dmc.TabsPanel(html.Div(id="overview-tab-content"), value="overview"),
                dmc.TabsPanel(html.Div(id="work-items-tab-content"), value="work_items"),
                dmc.TabsPanel(html.Div(id="materials-tab-content"), value="materials"),
                dmc.TabsPanel(html.Div(id="visits-tab-content"), value="visits"),
                dmc.TabsPanel(html.Div(id="files-tab-content"), value="files"),
                dmc.TabsPanel(html.Div(id="comments-tab-content"), value="comments"),
                dmc.TabsPanel(html.Div(id="schedule-tab-content"), value="schedule"),
            ],
            id="job-detail-tabs"
        ),

        # Modals for adding items
        create_work_item_modal(),
        create_material_modal(),
        create_visit_modal(),
        create_comment_modal(),
        create_schedule_modal(),

    ], gap="md", p="md")


# =====================================================
# HEADER SECTION
# =====================================================

@callback(
    Output("job-detail-header", "children"),
    Input("current-job-id", "data"),
    State("session-store", "data"),
)
def load_job_header(job_id, session_data):
    """Load job header with key information"""

    if not job_id or not session_data:
        return dmc.Alert("Unable to load job", color="red")

    db = get_authenticated_db(session_data)
    job = db.get_job_by_id(int(job_id))

    if not job:
        return dmc.Alert("Job not found", color="red")

    # Status color
    status_colors = {
        'Quote': 'gray', 'Scheduled': 'blue', 'In Progress': 'green',
        'Pending Materials': 'orange', 'Ready for Install': 'cyan',
        'Installed': 'teal', 'Completed': 'teal', 'Cancelled': 'red', 'On Hold': 'yellow'
    }

    status = job.get('status', 'Quote')
    status_color = status_colors.get(status, 'gray')

    # Client info
    client_name = "Unknown Client"
    if job.get('po_clients'):
        client_name = job['po_clients'].get('client_name', 'Unknown Client')

    # Format date
    job_date = job.get('job_date')
    if job_date:
        if isinstance(job_date, str):
            job_date = datetime.fromisoformat(job_date).strftime("%m/%d/%Y")
        else:
            job_date = job_date.strftime("%m/%d/%Y")

    return dmc.Card([
        dmc.Group([
            # Left - Job info
            dmc.Stack([
                dmc.Group([
                    dmc.Button(
                        "← Back to Jobs",
                        variant="subtle",
                        size="sm",
                        id="back-to-jobs-button",
                        leftSection=DashIconify(icon="solar:arrow-left-bold", width=16)
                    ),
                ]),

                dmc.Group([
                    dmc.Title(f"PO# {job.get('po_number', 'N/A')}", order=2),
                    dmc.Badge(status, color=status_color, size="lg", variant="light"),
                ], gap="sm"),

                dmc.Group([
                    DashIconify(icon="solar:user-bold", width=20),
                    dmc.Text(client_name, size="lg", fw=500),
                    dmc.Text("|", c="dimmed"),
                    DashIconify(icon="solar:calendar-bold", width=20),
                    dmc.Text(job_date, size="lg"),
                ], gap="xs"),

                dmc.Text(job.get('job_description', 'No description'), size="sm", c="dimmed"),
            ], gap="xs"),

            # Right - Financial summary
            dmc.Stack([
                dmc.Card([
                    dmc.Stack([
                        dmc.Text("Financial Summary", size="sm", fw=600, c="dimmed"),
                        dmc.Group([
                            dmc.Stack([
                                dmc.Text("Estimate", size="xs", c="dimmed"),
                                dmc.Text(f"${job.get('total_estimate', 0):,.2f}", size="lg", fw=700, c="blue")
                            ], gap=0),

                            dmc.Stack([
                                dmc.Text("Material Cost", size="xs", c="dimmed"),
                                dmc.Text(f"${job.get('material_cost', 0):,.2f}", size="lg", fw=700)
                            ], gap=0),

                            dmc.Stack([
                                dmc.Text("Actual Cost", size="xs", c="dimmed"),
                                dmc.Text(f"${job.get('actual_cost', 0):,.2f}", size="lg", fw=700)
                            ], gap=0),
                        ], gap="xl"),

                        dmc.Progress(
                            value=((job.get('actual_cost', 0) / job.get('total_estimate', 1)) * 100) if job.get('total_estimate', 0) > 0 else 0,
                            color="blue",
                            size="sm"
                        ),
                    ], gap="xs")
                ], withBorder=True, p="md")
            ], align="flex-end")

        ], justify="space-between", align="flex-start")
    ], withBorder=True, p="lg", radius="md", style={"background": "#f8f9fa"})


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("back-to-jobs-button", "n_clicks"),
    prevent_initial_call=True
)
def navigate_back_to_jobs(n_clicks):
    """Navigate back to jobs list"""
    if n_clicks:
        return "/jobs"
    return dash.no_update


# =====================================================
# OVERVIEW TAB
# =====================================================

@callback(
    Output("overview-tab-content", "children"),
    Input("job-detail-tabs", "value"),
    State("current-job-id", "data"),
    State("session-store", "data"),
)
def load_overview_tab(active_tab, job_id, session_data):
    """Load overview tab content"""

    if active_tab != "overview" or not job_id:
        return html.Div()

    db = get_authenticated_db(session_data)
    job = db.get_job_by_id(int(job_id))

    if not job:
        return dmc.Alert("Job not found", color="red")

    return dmc.Stack([
        dmc.Grid([
            # Job Details
            dmc.GridCol([
                dmc.Card([
                    dmc.Stack([
                        dmc.Text("Job Details", size="lg", fw=600),

                        dmc.TextInput(
                            label="PO Number",
                            value=job.get('po_number', ''),
                            readOnly=True
                        ),

                        dmc.Textarea(
                            label="Job Description",
                            value=job.get('job_description', ''),
                            minRows=3,
                            id="edit-job-description"
                        ),

                        dmc.Textarea(
                            label="Site Address",
                            value=job.get('site_address', ''),
                            minRows=2,
                            id="edit-site-address"
                        ),

                        dmc.Group([
                            dmc.TextInput(
                                label="Site Contact Name",
                                value=job.get('site_contact_name', ''),
                                style={"flex": 1},
                                id="edit-site-contact-name"
                            ),
                            dmc.TextInput(
                                label="Site Contact Phone",
                                value=job.get('site_contact_phone', ''),
                                style={"flex": 1},
                                id="edit-site-contact-phone"
                            ),
                        ]),

                        dmc.Textarea(
                            label="Internal Notes",
                            value=job.get('internal_notes', ''),
                            minRows=3,
                            id="edit-internal-notes"
                        ),

                        dmc.Button(
                            "Save Changes",
                            id="save-job-details-button",
                            color="blue",
                            leftSection=DashIconify(icon="solar:diskette-bold", width=16)
                        ),
                    ], gap="md")
                ], withBorder=True, p="md")
            ], span=8),

            # Quick Stats
            dmc.GridCol([
                dmc.Stack([
                    dmc.Card([
                        dmc.Stack([
                            dmc.Text("Quick Stats", size="lg", fw=600),

                            dmc.Group([
                                DashIconify(icon="solar:checklist-bold-duotone", width=40, color="blue"),
                                dmc.Stack([
                                    dmc.Text("Work Items", size="xs", c="dimmed"),
                                    dmc.Text(id="stat-work-items-count", children="0", size="xl", fw=700)
                                ], gap=0)
                            ]),

                            dmc.Divider(),

                            dmc.Group([
                                DashIconify(icon="solar:box-bold-duotone", width=40, color="green"),
                                dmc.Stack([
                                    dmc.Text("Materials", size="xs", c="dimmed"),
                                    dmc.Text(id="stat-materials-count", children="0", size="xl", fw=700)
                                ], gap=0)
                            ]),

                            dmc.Divider(),

                            dmc.Group([
                                DashIconify(icon="solar:map-point-bold-duotone", width=40, color="orange"),
                                dmc.Stack([
                                    dmc.Text("Site Visits", size="xs", c="dimmed"),
                                    dmc.Text(id="stat-visits-count", children="0", size="xl", fw=700)
                                ], gap=0)
                            ]),

                            dmc.Divider(),

                            dmc.Group([
                                DashIconify(icon="solar:gallery-bold-duotone", width=40, color="purple"),
                                dmc.Stack([
                                    dmc.Text("Files", size="xs", c="dimmed"),
                                    dmc.Text(id="stat-files-count", children="0", size="xl", fw=700)
                                ], gap=0)
                            ]),

                        ], gap="md")
                    ], withBorder=True, p="md"),
                ], gap="md")
            ], span=4),
        ]),
    ], gap="md")


@callback(
    Output("job-detail-header", "children", allow_duplicate=True),
    Input("save-job-details-button", "n_clicks"),
    State("edit-job-description", "value"),
    State("edit-site-address", "value"),
    State("edit-site-contact-name", "value"),
    State("edit-site-contact-phone", "value"),
    State("edit-internal-notes", "value"),
    State("current-job-id", "data"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def save_job_details(n_clicks, description, site_address, site_contact_name, site_contact_phone, internal_notes, job_id, session_data):
    """Save job detail updates"""

    if not n_clicks or not job_id:
        return dash.no_update

    db = get_authenticated_db(session_data)
    user_id = session_data.get('session', {}).get('user', {}).get('id')

    updates = {
        'job_description': description,
        'site_address': site_address,
        'site_contact_name': site_contact_name,
        'site_contact_phone': site_contact_phone,
        'internal_notes': internal_notes
    }

    db.update_job(int(job_id), updates, user_id)

    # Reload header
    return load_job_header(job_id, session_data)


# =====================================================
# WORK ITEMS TAB
# =====================================================

def create_work_item_modal():
    """Create modal for adding work items"""
    return dmc.Modal(
        id="add-work-item-modal",
        title="Add Work Item",
        size="lg",
        children=[
            dmc.Stack([
                dmc.Select(
                    id="new-work-item-type",
                    label="Work Type",
                    data=[
                        {"value": "Shower", "label": "Shower"},
                        {"value": "Window/IG", "label": "Window/IG"},
                        {"value": "Mirror", "label": "Mirror"},
                        {"value": "Tabletop", "label": "Tabletop"},
                        {"value": "Mirror Frame", "label": "Mirror Frame"},
                        {"value": "Custom", "label": "Custom"},
                    ],
                    required=True
                ),

                dmc.NumberInput(
                    id="new-work-item-quantity",
                    label="Quantity",
                    value=1,
                    min=1,
                    required=True
                ),

                dmc.Textarea(
                    id="new-work-item-description",
                    label="Description / Specifications",
                    placeholder="Details about this work item...",
                    minRows=3
                ),

                dmc.NumberInput(
                    id="new-work-item-estimated-cost",
                    label="Estimated Cost",
                    value=0,
                    min=0,
                    precision=2,
                    leftSection="$"
                ),

                dmc.Group([
                    dmc.Button("Cancel", id="cancel-work-item-button", variant="subtle", color="gray"),
                    dmc.Button("Add Work Item", id="save-work-item-button", color="blue"),
                ], justify="flex-end")
            ], gap="md")
        ]
    )


@callback(
    Output("work-items-tab-content", "children"),
    Input("job-detail-tabs", "value"),
    Input("add-work-item-modal", "opened"),  # Reload when modal closes
    State("current-job-id", "data"),
    State("session-store", "data"),
)
def load_work_items_tab(active_tab, modal_opened, job_id, session_data):
    """Load work items tab content"""

    if active_tab != "work_items" or not job_id:
        return html.Div()

    db = get_authenticated_db(session_data)
    work_items = db.get_job_work_items(int(job_id))

    work_item_cards = []
    for item in work_items:
        work_item_cards.append(create_work_item_card(item))

    return dmc.Stack([
        dmc.Group([
            dmc.Text("Work Items", size="xl", fw=600),
            dmc.Button(
                "Add Work Item",
                id="add-work-item-button",
                leftSection=DashIconify(icon="solar:add-circle-bold", width=16),
                color="blue"
            )
        ], justify="space-between"),

        dmc.Stack(work_item_cards, gap="md") if work_item_cards else dmc.Alert(
            "No work items yet. Click 'Add Work Item' to get started.",
            color="blue",
            icon=DashIconify(icon="solar:info-circle-bold")
        )
    ], gap="md")


def create_work_item_card(item):
    """Create a card for a work item"""

    work_type_icons = {
        'Shower': 'solar:bath-bold-duotone',
        'Window/IG': 'solar:window-frame-bold-duotone',
        'Mirror': 'solar:mirror-left-bold-duotone',
        'Tabletop': 'solar:case-minimalistic-bold-duotone',
        'Mirror Frame': 'solar:frame-bold-duotone',
        'Custom': 'solar:widget-3-bold-duotone'
    }

    icon = work_type_icons.get(item.get('work_type'), 'solar:widget-3-bold-duotone')

    return dmc.Card([
        dmc.Group([
            DashIconify(icon=icon, width=40, color="blue"),

            dmc.Stack([
                dmc.Group([
                    dmc.Text(item.get('work_type', 'Unknown'), size="lg", fw=600),
                    dmc.Badge(f"Qty: {item.get('quantity', 1)}", color="blue", variant="light"),
                ]),

                dmc.Text(item.get('description', 'No description'), size="sm", c="dimmed"),

                dmc.Group([
                    dmc.Text(f"Est. Cost: ${item.get('estimated_cost', 0):,.2f}", size="sm", fw=500),
                    dmc.Text(f"Actual: ${item.get('actual_cost', 0):,.2f}", size="sm", fw=500, c="green"),
                ], gap="xl"),
            ], gap="xs", style={"flex": 1}),
        ])
    ], withBorder=True, p="md")


@callback(
    Output("add-work-item-modal", "opened"),
    Output("new-work-item-type", "value"),
    Output("new-work-item-quantity", "value"),
    Output("new-work-item-description", "value"),
    Output("new-work-item-estimated-cost", "value"),
    Input("add-work-item-button", "n_clicks"),
    Input("cancel-work-item-button", "n_clicks"),
    Input("save-work-item-button", "n_clicks"),
    State("new-work-item-type", "value"),
    State("new-work-item-quantity", "value"),
    State("new-work-item-description", "value"),
    State("new-work-item-estimated-cost", "value"),
    State("current-job-id", "data"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_work_item_modal(add_clicks, cancel_clicks, save_clicks,
                           work_type, quantity, description, estimated_cost,
                           job_id, session_data):
    """Handle work item modal"""

    triggered = ctx.triggered_id

    if triggered == "add-work-item-button":
        return True, None, 1, "", 0

    elif triggered == "cancel-work-item-button":
        return False, None, 1, "", 0

    elif triggered == "save-work-item-button":
        if not work_type or not quantity:
            return True, work_type, quantity, description, estimated_cost

        db = get_authenticated_db(session_data)
        user_id = session_data.get('session', {}).get('user', {}).get('id')

        item_data = {
            'job_id': int(job_id),
            'work_type': work_type,
            'quantity': quantity,
            'description': description,
            'estimated_cost': estimated_cost or 0
        }

        db.insert_work_item(item_data, user_id)

        return False, None, 1, "", 0

    return False, None, 1, "", 0


# =====================================================
# MATERIALS TAB
# =====================================================

def create_material_modal():
    """Create modal for adding vendor materials"""
    return dmc.Modal(
        id="add-material-modal",
        title="Add Vendor Material",
        size="lg",
        children=[
            dmc.Stack([
                dmc.Select(
                    id="new-material-vendor",
                    label="Vendor",
                    data=[],  # Populated dynamically
                    searchable=True,
                    required=True,
                    description="Select vendor supplying this material"
                ),

                dmc.Textarea(
                    id="new-material-description",
                    label="Material Description",
                    placeholder="e.g., shower door, crystalline bypass",
                    minRows=2,
                    required=True,
                    description="Describe what you're ordering (free text)"
                ),

                dmc.Select(
                    id="new-material-template",
                    label="Or Choose from Template (Optional)",
                    data=[],  # Populated dynamically
                    searchable=True,
                    clearable=True,
                    description="Quick-add common materials"
                ),

                dmc.NumberInput(
                    id="new-material-cost",
                    label="Cost",
                    value=0,
                    min=0,
                    precision=2,
                    leftSection="$",
                    description="Expected material cost"
                ),

                dmc.Group([
                    dmc.DatePicker(
                        id="new-material-ordered-date",
                        label="Ordered Date",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        style={"flex": 1}
                    ),
                    dmc.DatePicker(
                        id="new-material-expected-date",
                        label="Expected Delivery",
                        style={"flex": 1}
                    ),
                ]),

                dmc.Select(
                    id="new-material-status",
                    label="Status",
                    data=[
                        {"value": "Not Ordered", "label": "Not Ordered"},
                        {"value": "Ordered", "label": "Ordered"},
                        {"value": "In Transit", "label": "In Transit"},
                        {"value": "Delivered", "label": "Delivered"},
                    ],
                    value="Ordered"
                ),

                dmc.Textarea(
                    id="new-material-notes",
                    label="Notes",
                    placeholder="Additional notes...",
                    minRows=2
                ),

                dmc.Group([
                    dmc.Button("Cancel", id="cancel-material-button", variant="subtle", color="gray"),
                    dmc.Button("Add Material", id="save-material-button", color="blue"),
                ], justify="flex-end")
            ], gap="md")
        ]
    )


@callback(
    Output("materials-tab-content", "children"),
    Input("job-detail-tabs", "value"),
    Input("add-material-modal", "opened"),  # Reload when modal closes
    State("current-job-id", "data"),
    State("session-store", "data"),
)
def load_materials_tab(active_tab, modal_opened, job_id, session_data):
    """Load vendor materials tab content"""

    if active_tab != "materials" or not job_id:
        return html.Div()

    db = get_authenticated_db(session_data)
    materials = db.get_job_vendor_materials(int(job_id))

    material_cards = []
    for material in materials:
        material_cards.append(create_material_card(material))

    return dmc.Stack([
        dmc.Group([
            dmc.Text("Vendor Materials", size="xl", fw=600),
            dmc.Button(
                "Add Material",
                id="add-material-button",
                leftSection=DashIconify(icon="solar:add-circle-bold", width=16),
                color="blue"
            )
        ], justify="space-between"),

        dmc.Stack(material_cards, gap="md") if material_cards else dmc.Alert(
            "No materials ordered yet. Click 'Add Material' to track vendor deliveries.",
            color="blue",
            icon=DashIconify(icon="solar:info-circle-bold")
        )
    ], gap="md")


def create_material_card(material):
    """Create a card for a vendor material"""

    status_colors = {
        'Not Ordered': 'gray',
        'Ordered': 'blue',
        'In Transit': 'orange',
        'Delivered': 'green',
        'Installed': 'teal',
        'Cancelled': 'red'
    }

    status = material.get('status', 'Not Ordered')
    status_color = status_colors.get(status, 'gray')

    # Vendor name
    vendor_name = "Unknown Vendor"
    if material.get('vendors'):
        vendor_name = material['vendors'].get('vendor_name', 'Unknown Vendor')

    # Dates
    ordered_date = material.get('ordered_date')
    if ordered_date:
        if isinstance(ordered_date, str):
            ordered_date = datetime.fromisoformat(ordered_date).strftime("%m/%d/%Y")
        else:
            ordered_date = ordered_date.strftime("%m/%d/%Y")

    expected_date = material.get('expected_delivery_date')
    if expected_date:
        if isinstance(expected_date, str):
            expected_date = datetime.fromisoformat(expected_date).strftime("%m/%d/%Y")
        else:
            expected_date = expected_date.strftime("%m/%d/%Y")

    actual_date = material.get('actual_delivery_date')
    if actual_date:
        if isinstance(actual_date, str):
            actual_date = datetime.fromisoformat(actual_date).strftime("%m/%d/%Y")
        else:
            actual_date = actual_date.strftime("%m/%d/%Y")

    return dmc.Card([
        dmc.Group([
            DashIconify(icon="solar:box-bold-duotone", width=40, color="blue"),

            dmc.Stack([
                dmc.Group([
                    dmc.Text(vendor_name, size="lg", fw=600),
                    dmc.Badge(status, color=status_color, variant="light"),
                ]),

                dmc.Text(material.get('description', 'No description'), size="md"),

                dmc.Group([
                    dmc.Stack([
                        dmc.Text("Cost:", size="xs", c="dimmed"),
                        dmc.Text(f"${material.get('cost', 0):,.2f}", size="sm", fw=500, c="blue")
                    ], gap=0),

                    dmc.Stack([
                        dmc.Text("Ordered:", size="xs", c="dimmed"),
                        dmc.Text(ordered_date or "Not set", size="sm")
                    ], gap=0),

                    dmc.Stack([
                        dmc.Text("Expected:", size="xs", c="dimmed"),
                        dmc.Text(expected_date or "TBD", size="sm", fw=500 if not actual_date else 400)
                    ], gap=0),

                    dmc.Stack([
                        dmc.Text("Delivered:", size="xs", c="dimmed"),
                        dmc.Text(actual_date or "-", size="sm", fw=500 if actual_date else 400, c="green" if actual_date else "gray")
                    ], gap=0) if status == 'Delivered' else None,
                ], gap="xl"),

                dmc.Text(material.get('notes', ''), size="sm", c="dimmed", lineClamp=2) if material.get('notes') else None,

            ], gap="xs", style={"flex": 1}),
        ])
    ], withBorder=True, p="md")


@callback(
    Output("add-material-modal", "opened"),
    Output("new-material-vendor", "value"),
    Output("new-material-description", "value"),
    Output("new-material-template", "value"),
    Output("new-material-cost", "value"),
    Output("new-material-status", "value"),
    Output("new-material-notes", "value"),
    Input("add-material-button", "n_clicks"),
    Input("cancel-material-button", "n_clicks"),
    Input("save-material-button", "n_clicks"),
    State("new-material-vendor", "value"),
    State("new-material-description", "value"),
    State("new-material-template", "value"),
    State("new-material-cost", "value"),
    State("new-material-ordered-date", "value"),
    State("new-material-expected-date", "value"),
    State("new-material-status", "value"),
    State("new-material-notes", "value"),
    State("current-job-id", "data"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_material_modal(add_clicks, cancel_clicks, save_clicks,
                         vendor_id, description, template_id, cost, ordered_date, expected_date,
                         status, notes, job_id, session_data):
    """Handle material modal"""

    triggered = ctx.triggered_id

    if triggered == "add-material-button":
        return True, None, "", None, 0, "Ordered", ""

    elif triggered == "cancel-material-button":
        return False, None, "", None, 0, "Ordered", ""

    elif triggered == "save-material-button":
        if not vendor_id or not description:
            return True, vendor_id, description, template_id, cost, status, notes

        db = get_authenticated_db(session_data)
        user_id = session_data.get('session', {}).get('user', {}).get('id')

        material_data = {
            'job_id': int(job_id),
            'vendor_id': int(vendor_id) if vendor_id else None,
            'description': description,
            'template_id': int(template_id) if template_id else None,
            'cost': cost or 0,
            'ordered_date': ordered_date,
            'expected_delivery_date': expected_date,
            'status': status,
            'notes': notes
        }

        db.insert_vendor_material(material_data, user_id)

        return False, None, "", None, 0, "Ordered", ""

    return False, None, "", None, 0, "Ordered", ""


@callback(
    Output("new-material-vendor", "data"),
    Output("new-material-template", "data"),
    Input("add-material-modal", "opened"),
    State("session-store", "data"),
)
def load_material_options(modal_opened, session_data):
    """Load vendor and template options for material form"""

    if not modal_opened:
        return [], []

    db = get_authenticated_db(session_data)

    # Get vendors
    vendors = db.get_all_vendors()
    vendor_options = [
        {"value": str(v['vendor_id']), "label": v['vendor_name']}
        for v in vendors if v.get('is_active', True)
    ]

    # Get material templates
    templates = db.get_all_material_templates()
    template_options = [
        {"value": str(t['template_id']), "label": t['template_name']}
        for t in templates
    ]

    return vendor_options, template_options


@callback(
    Output("new-material-description", "value", allow_duplicate=True),
    Input("new-material-template", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def apply_material_template(template_id, session_data):
    """Fill description from selected template"""

    if not template_id:
        return dash.no_update

    db = get_authenticated_db(session_data)
    templates = db.get_all_material_templates()

    for template in templates:
        if str(template['template_id']) == template_id:
            return template['template_name']

    return dash.no_update


# =====================================================
# SITE VISITS TAB
# =====================================================

def create_visit_modal():
    """Create modal for adding site visits"""
    return dmc.Modal(
        id="add-visit-modal",
        title="Log Site Visit",
        size="lg",
        children=[
            dmc.Stack([
                dmc.Select(
                    id="new-visit-type",
                    label="Visit Type",
                    data=[
                        {"value": "Measure/Estimate", "label": "Measure/Estimate"},
                        {"value": "Remeasure", "label": "Remeasure"},
                        {"value": "Install", "label": "Install"},
                        {"value": "Finals/Walkthrough", "label": "Finals/Walkthrough"},
                        {"value": "Adjustment/Fix", "label": "Adjustment/Fix"},
                        {"value": "Delivery", "label": "Delivery"},
                        {"value": "Other", "label": "Other"},
                    ],
                    required=True,
                    description="What type of visit was this?"
                ),

                dmc.DatePicker(
                    id="new-visit-date",
                    label="Visit Date",
                    value=datetime.now().strftime("%Y-%m-%d"),
                    required=True
                ),

                dmc.TextInput(
                    id="new-visit-employee",
                    label="Employee(s) Who Went",
                    placeholder="e.g., John Smith, Jane Doe",
                    required=True,
                    description="Names of employees on this visit"
                ),

                dmc.Group([
                    dmc.TimeInput(
                        id="new-visit-start-time",
                        label="Start Time",
                        style={"flex": 1}
                    ),
                    dmc.TimeInput(
                        id="new-visit-end-time",
                        label="End Time",
                        style={"flex": 1}
                    ),
                ]),

                dmc.Textarea(
                    id="new-visit-notes",
                    label="Visit Notes",
                    placeholder="What happened during this visit? Any issues or findings?",
                    minRows=4,
                    description="Details about the visit, measurements taken, issues found, etc."
                ),

                dmc.Textarea(
                    id="new-visit-outcome",
                    label="Outcome / Next Steps",
                    placeholder="What needs to happen next?",
                    minRows=2,
                    description="Follow-up actions or next scheduled visit"
                ),

                dmc.Group([
                    dmc.Button("Cancel", id="cancel-visit-button", variant="subtle", color="gray"),
                    dmc.Button("Log Visit", id="save-visit-button", color="blue"),
                ], justify="flex-end")
            ], gap="md")
        ]
    )


@callback(
    Output("visits-tab-content", "children"),
    Input("job-detail-tabs", "value"),
    Input("add-visit-modal", "opened"),  # Reload when modal closes
    State("current-job-id", "data"),
    State("session-store", "data"),
)
def load_visits_tab(active_tab, modal_opened, job_id, session_data):
    """Load site visits tab content"""

    if active_tab != "visits" or not job_id:
        return html.Div()

    db = get_authenticated_db(session_data)
    visits = db.get_job_site_visits(int(job_id))

    visit_cards = []
    for visit in visits:
        visit_cards.append(create_visit_card(visit))

    return dmc.Stack([
        dmc.Group([
            dmc.Text("Site Visits", size="xl", fw=600),
            dmc.Button(
                "Log Visit",
                id="add-visit-button",
                leftSection=DashIconify(icon="solar:add-circle-bold", width=16),
                color="blue"
            )
        ], justify="space-between"),

        dmc.Stack(visit_cards, gap="md") if visit_cards else dmc.Alert(
            "No site visits logged yet. Click 'Log Visit' to track your first visit.",
            color="blue",
            icon=DashIconify(icon="solar:info-circle-bold")
        )
    ], gap="md")


def create_visit_card(visit):
    """Create a card for a site visit"""

    visit_type_icons = {
        'Measure/Estimate': 'solar:ruler-angular-bold-duotone',
        'Remeasure': 'solar:ruler-cross-pen-bold-duotone',
        'Install': 'solar:tools-bold-duotone',
        'Finals/Walkthrough': 'solar:checklist-minimalistic-bold-duotone',
        'Adjustment/Fix': 'solar:wrench-bold-duotone',
        'Delivery': 'solar:delivery-bold-duotone',
        'Other': 'solar:map-point-bold-duotone'
    }

    visit_type_colors = {
        'Measure/Estimate': 'blue',
        'Remeasure': 'orange',
        'Install': 'green',
        'Finals/Walkthrough': 'teal',
        'Adjustment/Fix': 'yellow',
        'Delivery': 'cyan',
        'Other': 'gray'
    }

    visit_type = visit.get('visit_type', 'Other')
    icon = visit_type_icons.get(visit_type, 'solar:map-point-bold-duotone')
    color = visit_type_colors.get(visit_type, 'gray')

    # Format visit date
    visit_date = visit.get('visit_date')
    if visit_date:
        if isinstance(visit_date, str):
            visit_date = datetime.fromisoformat(visit_date).strftime("%m/%d/%Y")
        else:
            visit_date = visit_date.strftime("%m/%d/%Y")

    # Calculate duration if times available
    duration_text = ""
    start_time = visit.get('start_time')
    end_time = visit.get('end_time')
    if start_time and end_time:
        duration_text = f"{start_time} - {end_time}"
    elif visit.get('duration_hours'):
        duration_text = f"{visit.get('duration_hours')} hours"

    return dmc.Card([
        dmc.Group([
            DashIconify(icon=icon, width=40, color=color),

            dmc.Stack([
                dmc.Group([
                    dmc.Badge(visit_type, color=color, variant="light", size="lg"),
                    dmc.Text(visit_date, size="sm", fw=500),
                ]),

                dmc.Group([
                    DashIconify(icon="solar:user-bold", width=16),
                    dmc.Text(visit.get('employee_name', 'Unknown'), size="sm", fw=500),
                    dmc.Text("|", c="dimmed") if duration_text else None,
                    DashIconify(icon="solar:clock-circle-bold", width=16) if duration_text else None,
                    dmc.Text(duration_text, size="sm") if duration_text else None,
                ], gap="xs"),

                dmc.Text(visit.get('visit_notes', ''), size="sm", c="dimmed", lineClamp=2) if visit.get('visit_notes') else None,

                dmc.Card([
                    dmc.Stack([
                        dmc.Text("Outcome / Next Steps:", size="xs", fw=600, c="dimmed"),
                        dmc.Text(visit.get('outcome', 'No outcome recorded'), size="sm"),
                    ], gap="xs")
                ], withBorder=True, p="sm", style={"backgroundColor": "#f8f9fa"}) if visit.get('outcome') else None,

            ], gap="xs", style={"flex": 1}),
        ])
    ], withBorder=True, p="md")


@callback(
    Output("add-visit-modal", "opened"),
    Output("new-visit-type", "value"),
    Output("new-visit-date", "value"),
    Output("new-visit-employee", "value"),
    Output("new-visit-start-time", "value"),
    Output("new-visit-end-time", "value"),
    Output("new-visit-notes", "value"),
    Output("new-visit-outcome", "value"),
    Input("add-visit-button", "n_clicks"),
    Input("cancel-visit-button", "n_clicks"),
    Input("save-visit-button", "n_clicks"),
    State("new-visit-type", "value"),
    State("new-visit-date", "value"),
    State("new-visit-employee", "value"),
    State("new-visit-start-time", "value"),
    State("new-visit-end-time", "value"),
    State("new-visit-notes", "value"),
    State("new-visit-outcome", "value"),
    State("current-job-id", "data"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_visit_modal(add_clicks, cancel_clicks, save_clicks,
                       visit_type, visit_date, employee, start_time, end_time,
                       notes, outcome, job_id, session_data):
    """Handle site visit modal"""

    triggered = ctx.triggered_id
    today = datetime.now().strftime("%Y-%m-%d")

    if triggered == "add-visit-button":
        return True, None, today, "", None, None, "", ""

    elif triggered == "cancel-visit-button":
        return False, None, today, "", None, None, "", ""

    elif triggered == "save-visit-button":
        if not visit_type or not visit_date or not employee:
            return True, visit_type, visit_date, employee, start_time, end_time, notes, outcome

        db = get_authenticated_db(session_data)
        user_id = session_data.get('session', {}).get('user', {}).get('id')

        # Calculate duration if both times provided
        duration_hours = None
        if start_time and end_time:
            try:
                start_dt = datetime.strptime(start_time, "%H:%M")
                end_dt = datetime.strptime(end_time, "%H:%M")
                duration = (end_dt - start_dt).total_seconds() / 3600
                duration_hours = round(duration, 2)
            except:
                pass

        visit_data = {
            'job_id': int(job_id),
            'visit_type': visit_type,
            'visit_date': visit_date,
            'employee_name': employee,
            'start_time': start_time,
            'end_time': end_time,
            'duration_hours': duration_hours,
            'visit_notes': notes,
            'outcome': outcome
        }

        db.insert_site_visit(visit_data, user_id)

        return False, None, today, "", None, None, "", ""

    return False, None, today, "", None, None, "", ""


# =====================================================
# FILES TAB
# =====================================================

@callback(
    Output("files-tab-content", "children"),
    Input("job-detail-tabs", "value"),
    Input("upload-file-button", "n_clicks"),  # Reload after upload
    State("current-job-id", "data"),
    State("session-store", "data"),
)
def load_files_tab(active_tab, upload_clicks, job_id, session_data):
    """Load files tab content"""

    if active_tab != "files" or not job_id:
        return html.Div()

    db = get_authenticated_db(session_data)
    files = db.get_job_files(int(job_id))

    file_cards = []
    for file in files:
        file_cards.append(create_file_card(file))

    return dmc.Stack([
        dmc.Group([
            dmc.Text("Files & Photos", size="xl", fw=600),
            dmc.Button(
                "Upload File",
                id="open-upload-modal-button",
                leftSection=DashIconify(icon="solar:upload-bold", width=16),
                color="blue"
            )
        ], justify="space-between"),

        dmc.Alert(
            "File uploads require Supabase Storage configuration. You can still track file references manually.",
            color="blue",
            icon=DashIconify(icon="solar:info-circle-bold"),
            style={"marginBottom": "1rem"}
        ),

        # Upload form (simplified without actual upload for now)
        dmc.Card([
            dmc.Stack([
                dmc.Text("Add File Reference", size="md", fw=600),
                dmc.TextInput(
                    id="new-file-name",
                    label="File Name",
                    placeholder="e.g., measurement-drawing.pdf",
                    required=True
                ),
                dmc.Select(
                    id="new-file-category",
                    label="Category",
                    data=[
                        {"value": "Photo", "label": "Photo"},
                        {"value": "Drawing", "label": "Drawing"},
                        {"value": "Document", "label": "Document"},
                        {"value": "Quote", "label": "Quote"},
                        {"value": "Invoice", "label": "Invoice"},
                        {"value": "Other", "label": "Other"},
                    ],
                    value="Photo"
                ),
                dmc.TextInput(
                    id="new-file-url",
                    label="File URL or Path",
                    placeholder="https://... or local path",
                    description="Link to where this file is stored"
                ),
                dmc.Textarea(
                    id="new-file-description",
                    label="Description",
                    placeholder="What does this file show?",
                    minRows=2
                ),
                dmc.TextInput(
                    id="new-file-tags",
                    label="Tags",
                    placeholder="e.g., measure, shower, before",
                    description="Comma-separated tags for organization"
                ),
                dmc.Button(
                    "Add File Reference",
                    id="upload-file-button",
                    color="blue",
                    leftSection=DashIconify(icon="solar:add-circle-bold", width=16)
                ),
            ], gap="sm")
        ], withBorder=True, p="md", style={"marginBottom": "1rem"}),

        dmc.Text(f"Files ({len(files)})", size="sm", fw=600, c="dimmed") if files else None,

        dmc.Stack(file_cards, gap="md") if file_cards else dmc.Alert(
            "No files uploaded yet. Add file references above to track photos, drawings, and documents.",
            color="gray",
            icon=DashIconify(icon="solar:gallery-bold")
        )
    ], gap="md")


def create_file_card(file):
    """Create a card for a file"""

    category_icons = {
        'Photo': 'solar:camera-bold-duotone',
        'Drawing': 'solar:ruler-pen-bold-duotone',
        'Document': 'solar:document-bold-duotone',
        'Quote': 'solar:bill-list-bold-duotone',
        'Invoice': 'solar:bill-check-bold-duotone',
        'Other': 'solar:file-bold-duotone'
    }

    category_colors = {
        'Photo': 'blue',
        'Drawing': 'orange',
        'Document': 'gray',
        'Quote': 'cyan',
        'Invoice': 'green',
        'Other': 'purple'
    }

    category = file.get('file_category', 'Other')
    icon = category_icons.get(category, 'solar:file-bold-duotone')
    color = category_colors.get(category, 'gray')

    # Format upload date
    uploaded_at = file.get('created_at')
    if uploaded_at:
        if isinstance(uploaded_at, str):
            uploaded_at = datetime.fromisoformat(uploaded_at).strftime("%m/%d/%Y %I:%M %p")
        else:
            uploaded_at = uploaded_at.strftime("%m/%d/%Y %I:%M %p")

    # Parse tags
    tags = []
    if file.get('tags'):
        tags = [tag.strip() for tag in file.get('tags', '').split(',')]

    return dmc.Card([
        dmc.Group([
            DashIconify(icon=icon, width=40, color=color),

            dmc.Stack([
                dmc.Group([
                    dmc.Text(file.get('file_name', 'Untitled'), size="lg", fw=600),
                    dmc.Badge(category, color=color, variant="light"),
                ]),

                dmc.Text(file.get('file_description', ''), size="sm", c="dimmed") if file.get('file_description') else None,

                dmc.Group([
                    DashIconify(icon="solar:calendar-bold", width=16, color="gray"),
                    dmc.Text(uploaded_at, size="xs", c="dimmed"),
                    dmc.Text("|", c="dimmed") if file.get('file_size') else None,
                    dmc.Text(f"{file.get('file_size', 0)} KB", size="xs", c="dimmed") if file.get('file_size') else None,
                ], gap="xs"),

                dmc.Group([
                    dmc.Badge(tag, color="gray", variant="outline", size="sm") for tag in tags
                ], gap="xs") if tags else None,

                dmc.Button(
                    "View File",
                    size="xs",
                    variant="subtle",
                    leftSection=DashIconify(icon="solar:eye-bold", width=14),
                    style={"width": "fit-content"}
                ) if file.get('file_url') else None,

            ], gap="xs", style={"flex": 1}),
        ], align="flex-start")
    ], withBorder=True, p="md")


@callback(
    Output("files-tab-content", "children", allow_duplicate=True),
    Input("upload-file-button", "n_clicks"),
    State("new-file-name", "value"),
    State("new-file-category", "value"),
    State("new-file-url", "value"),
    State("new-file-description", "value"),
    State("new-file-tags", "value"),
    State("current-job-id", "data"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_file_upload(n_clicks, file_name, category, file_url, description, tags, job_id, session_data):
    """Handle file upload/reference addition"""

    if not n_clicks or not file_name:
        return dash.no_update

    db = get_authenticated_db(session_data)
    user_id = session_data.get('session', {}).get('user', {}).get('id')

    file_data = {
        'job_id': int(job_id),
        'file_name': file_name,
        'file_category': category or 'Other',
        'file_url': file_url,
        'file_description': description,
        'tags': tags
    }

    db.insert_job_file(file_data, user_id)

    # Reload the tab
    return load_files_tab("files", n_clicks, job_id, session_data)


# =====================================================
# COMMENTS TAB
# =====================================================

def create_comment_modal():
    """Create modal for adding comments"""
    return dmc.Modal(
        id="add-comment-modal",
        title="Add Comment",
        size="lg",
        children=[
            dmc.Stack([
                dmc.Select(
                    id="new-comment-type",
                    label="Comment Type",
                    data=[
                        {"value": "Note", "label": "Note"},
                        {"value": "Update", "label": "Update"},
                        {"value": "Issue", "label": "Issue"},
                        {"value": "Resolution", "label": "Resolution"},
                        {"value": "Question", "label": "Question"},
                    ],
                    value="Note",
                    description="What kind of comment is this?"
                ),

                dmc.Textarea(
                    id="new-comment-text",
                    label="Comment",
                    placeholder="Add your comment here...",
                    minRows=5,
                    required=True,
                    description="Share updates, ask questions, or note issues"
                ),

                dmc.Group([
                    dmc.Button("Cancel", id="cancel-comment-button", variant="subtle", color="gray"),
                    dmc.Button("Post Comment", id="save-comment-button", color="blue"),
                ], justify="flex-end")
            ], gap="md")
        ]
    )


@callback(
    Output("comments-tab-content", "children"),
    Input("job-detail-tabs", "value"),
    Input("add-comment-modal", "opened"),  # Reload when modal closes
    State("current-job-id", "data"),
    State("session-store", "data"),
)
def load_comments_tab(active_tab, modal_opened, job_id, session_data):
    """Load comments tab content"""

    if active_tab != "comments" or not job_id:
        return html.Div()

    db = get_authenticated_db(session_data)
    comments = db.get_job_comments(int(job_id))

    # Sort comments by date, newest first
    comments.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    comment_cards = []
    for comment in comments:
        comment_cards.append(create_comment_card(comment))

    return dmc.Stack([
        dmc.Group([
            dmc.Text("Discussion & Comments", size="xl", fw=600),
            dmc.Button(
                "Add Comment",
                id="add-comment-button",
                leftSection=DashIconify(icon="solar:add-circle-bold", width=16),
                color="blue"
            )
        ], justify="space-between"),

        dmc.Alert(
            "Use comments to communicate with your team about this job. Document issues, share updates, and ask questions.",
            color="blue",
            icon=DashIconify(icon="solar:info-circle-bold")
        ),

        dmc.Stack(comment_cards, gap="md") if comment_cards else dmc.Alert(
            "No comments yet. Click 'Add Comment' to start the discussion.",
            color="gray",
            icon=DashIconify(icon="solar:chat-round-bold")
        )
    ], gap="md")


def create_comment_card(comment):
    """Create a card for a comment"""

    comment_type_icons = {
        'Note': 'solar:notes-bold-duotone',
        'Update': 'solar:refresh-circle-bold-duotone',
        'Issue': 'solar:danger-triangle-bold-duotone',
        'Resolution': 'solar:check-circle-bold-duotone',
        'Question': 'solar:question-circle-bold-duotone',
    }

    comment_type_colors = {
        'Note': 'gray',
        'Update': 'blue',
        'Issue': 'red',
        'Resolution': 'green',
        'Question': 'orange',
    }

    comment_type = comment.get('comment_type', 'Note')
    icon = comment_type_icons.get(comment_type, 'solar:notes-bold-duotone')
    color = comment_type_colors.get(comment_type, 'gray')

    # Format comment date
    created_at = comment.get('created_at')
    if created_at:
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at).strftime("%m/%d/%Y %I:%M %p")
        else:
            created_at = created_at.strftime("%m/%d/%Y %I:%M %p")

    # Check if edited
    updated_at = comment.get('updated_at')
    is_edited = False
    if updated_at and updated_at != comment.get('created_at'):
        is_edited = True

    # Get user info (from created_by or user_profiles if joined)
    user_name = "Unknown User"
    if comment.get('user_profiles'):
        user_name = comment['user_profiles'].get('full_name') or comment['user_profiles'].get('email', 'Unknown')

    return dmc.Card([
        dmc.Stack([
            # Header
            dmc.Group([
                DashIconify(icon=icon, width=24, color=color),
                dmc.Badge(comment_type, color=color, variant="light"),
                dmc.Text(user_name, size="sm", fw=600),
                dmc.Text("•", size="sm", c="dimmed"),
                dmc.Text(created_at, size="sm", c="dimmed"),
                dmc.Badge("Edited", color="gray", variant="outline", size="xs") if is_edited else None,
            ], gap="xs"),

            # Comment text
            dmc.Text(
                comment.get('comment_text', ''),
                size="md",
                style={"whiteSpace": "pre-wrap"}
            ),

        ], gap="sm")
    ], withBorder=True, p="md", style={"backgroundColor": "#f8f9fa"})


@callback(
    Output("add-comment-modal", "opened"),
    Output("new-comment-type", "value"),
    Output("new-comment-text", "value"),
    Input("add-comment-button", "n_clicks"),
    Input("cancel-comment-button", "n_clicks"),
    Input("save-comment-button", "n_clicks"),
    State("new-comment-type", "value"),
    State("new-comment-text", "value"),
    State("current-job-id", "data"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_comment_modal(add_clicks, cancel_clicks, save_clicks,
                         comment_type, comment_text, job_id, session_data):
    """Handle comment modal"""

    triggered = ctx.triggered_id

    if triggered == "add-comment-button":
        return True, "Note", ""

    elif triggered == "cancel-comment-button":
        return False, "Note", ""

    elif triggered == "save-comment-button":
        if not comment_text:
            return True, comment_type, comment_text

        db = get_authenticated_db(session_data)
        user_id = session_data.get('session', {}).get('user', {}).get('id')

        comment_data = {
            'job_id': int(job_id),
            'comment_type': comment_type or 'Note',
            'comment_text': comment_text
        }

        db.insert_comment(comment_data, user_id)

        return False, "Note", ""

    return False, "Note", ""


# =====================================================
# SCHEDULE TAB
# =====================================================

def create_schedule_modal():
    """Create modal for adding scheduled events"""
    return dmc.Modal(
        id="add-schedule-modal",
        title="Add Scheduled Event",
        size="lg",
        children=[
            dmc.Stack([
                dmc.Select(
                    id="new-schedule-event-type",
                    label="Event Type",
                    data=[
                        {"value": "Measure", "label": "Measure"},
                        {"value": "Remeasure", "label": "Remeasure"},
                        {"value": "Install", "label": "Install"},
                        {"value": "Delivery", "label": "Delivery"},
                        {"value": "Follow-up", "label": "Follow-up"},
                        {"value": "Finals", "label": "Finals"},
                        {"value": "Meeting", "label": "Meeting"},
                        {"value": "Other", "label": "Other"},
                    ],
                    required=True,
                    description="What type of event are you scheduling?"
                ),

                dmc.Group([
                    dmc.DatePicker(
                        id="new-schedule-date",
                        label="Date",
                        required=True,
                        style={"flex": 1}
                    ),
                    dmc.TimeInput(
                        id="new-schedule-time",
                        label="Time",
                        style={"flex": 1}
                    ),
                ]),

                dmc.TextInput(
                    id="new-schedule-assigned-to",
                    label="Assigned To",
                    placeholder="e.g., John Smith, Jane Doe",
                    description="Who is responsible for this event?"
                ),

                dmc.Textarea(
                    id="new-schedule-notes",
                    label="Notes",
                    placeholder="Details about this scheduled event...",
                    minRows=3
                ),

                dmc.Select(
                    id="new-schedule-status",
                    label="Status",
                    data=[
                        {"value": "Scheduled", "label": "Scheduled"},
                        {"value": "Confirmed", "label": "Confirmed"},
                        {"value": "In Progress", "label": "In Progress"},
                        {"value": "Completed", "label": "Completed"},
                        {"value": "Cancelled", "label": "Cancelled"},
                        {"value": "Rescheduled", "label": "Rescheduled"},
                    ],
                    value="Scheduled"
                ),

                dmc.Group([
                    dmc.Button("Cancel", id="cancel-schedule-button", variant="subtle", color="gray"),
                    dmc.Button("Add Event", id="save-schedule-button", color="blue"),
                ], justify="flex-end")
            ], gap="md")
        ]
    )


@callback(
    Output("schedule-tab-content", "children"),
    Input("job-detail-tabs", "value"),
    Input("add-schedule-modal", "opened"),  # Reload when modal closes
    State("current-job-id", "data"),
    State("session-store", "data"),
)
def load_schedule_tab(active_tab, modal_opened, job_id, session_data):
    """Load schedule tab content"""

    if active_tab != "schedule" or not job_id:
        return html.Div()

    db = get_authenticated_db(session_data)
    events = db.get_job_schedule(int(job_id))

    # Sort by scheduled date
    events.sort(key=lambda x: x.get('scheduled_date', ''))

    # Separate upcoming and past events
    today = datetime.now().date()
    upcoming_events = []
    past_events = []

    for event in events:
        event_date = event.get('scheduled_date')
        if event_date:
            if isinstance(event_date, str):
                event_date = datetime.fromisoformat(event_date).date()

            if event_date >= today and event.get('status') not in ['Completed', 'Cancelled']:
                upcoming_events.append(event)
            else:
                past_events.append(event)

    upcoming_cards = [create_schedule_card(event) for event in upcoming_events]
    past_cards = [create_schedule_card(event, is_past=True) for event in past_events]

    return dmc.Stack([
        dmc.Group([
            dmc.Text("Schedule", size="xl", fw=600),
            dmc.Button(
                "Add Event",
                id="add-schedule-button",
                leftSection=DashIconify(icon="solar:add-circle-bold", width=16),
                color="blue"
            )
        ], justify="space-between"),

        # Upcoming events
        dmc.Stack([
            dmc.Group([
                DashIconify(icon="solar:calendar-mark-bold", width=24, color="blue"),
                dmc.Text("Upcoming Events", size="lg", fw=600),
                dmc.Badge(f"{len(upcoming_events)}", color="blue") if upcoming_events else None,
            ], gap="xs"),

            dmc.Stack(upcoming_cards, gap="md") if upcoming_cards else dmc.Alert(
                "No upcoming events. Click 'Add Event' to schedule something.",
                color="gray",
                icon=DashIconify(icon="solar:calendar-bold")
            )
        ], gap="md"),

        # Past events (if any)
        dmc.Stack([
            dmc.Group([
                DashIconify(icon="solar:history-bold", width=24, color="gray"),
                dmc.Text("Past Events", size="lg", fw=600),
                dmc.Badge(f"{len(past_events)}", color="gray") if past_events else None,
            ], gap="xs"),

            dmc.Stack(past_cards, gap="md") if past_cards else None,
        ], gap="md") if past_events else None,

    ], gap="xl")


def create_schedule_card(event, is_past=False):
    """Create a card for a scheduled event"""

    event_type_icons = {
        'Measure': 'solar:ruler-angular-bold-duotone',
        'Remeasure': 'solar:ruler-cross-pen-bold-duotone',
        'Install': 'solar:tools-bold-duotone',
        'Delivery': 'solar:delivery-bold-duotone',
        'Follow-up': 'solar:phone-calling-bold-duotone',
        'Finals': 'solar:checklist-minimalistic-bold-duotone',
        'Meeting': 'solar:users-group-two-rounded-bold-duotone',
        'Other': 'solar:calendar-bold-duotone'
    }

    status_colors = {
        'Scheduled': 'blue',
        'Confirmed': 'green',
        'In Progress': 'orange',
        'Completed': 'teal',
        'Cancelled': 'red',
        'Rescheduled': 'yellow'
    }

    event_type = event.get('event_type', 'Other')
    icon = event_type_icons.get(event_type, 'solar:calendar-bold-duotone')

    status = event.get('status', 'Scheduled')
    status_color = status_colors.get(status, 'blue')

    # Format scheduled date
    scheduled_date = event.get('scheduled_date')
    date_display = "No date"
    if scheduled_date:
        if isinstance(scheduled_date, str):
            dt = datetime.fromisoformat(scheduled_date)
            date_display = dt.strftime("%A, %B %d, %Y")
        else:
            date_display = scheduled_date.strftime("%A, %B %d, %Y")

    # Time
    scheduled_time = event.get('scheduled_time')
    if scheduled_time:
        date_display += f" at {scheduled_time}"

    return dmc.Card([
        dmc.Group([
            DashIconify(icon=icon, width=40, color="gray" if is_past else "blue"),

            dmc.Stack([
                dmc.Group([
                    dmc.Text(event_type, size="lg", fw=600),
                    dmc.Badge(status, color=status_color, variant="light"),
                ]),

                dmc.Group([
                    DashIconify(icon="solar:calendar-bold", width=16),
                    dmc.Text(date_display, size="sm", fw=500),
                ], gap="xs"),

                dmc.Group([
                    DashIconify(icon="solar:user-bold", width=16),
                    dmc.Text(event.get('assigned_to', 'Unassigned'), size="sm"),
                ], gap="xs") if event.get('assigned_to') else None,

                dmc.Text(event.get('event_notes', ''), size="sm", c="dimmed", lineClamp=2) if event.get('event_notes') else None,

            ], gap="xs", style={"flex": 1}),
        ], align="flex-start")
    ], withBorder=True, p="md", style={"opacity": 0.7 if is_past else 1})


@callback(
    Output("add-schedule-modal", "opened"),
    Output("new-schedule-event-type", "value"),
    Output("new-schedule-date", "value"),
    Output("new-schedule-time", "value"),
    Output("new-schedule-assigned-to", "value"),
    Output("new-schedule-notes", "value"),
    Output("new-schedule-status", "value"),
    Input("add-schedule-button", "n_clicks"),
    Input("cancel-schedule-button", "n_clicks"),
    Input("save-schedule-button", "n_clicks"),
    State("new-schedule-event-type", "value"),
    State("new-schedule-date", "value"),
    State("new-schedule-time", "value"),
    State("new-schedule-assigned-to", "value"),
    State("new-schedule-notes", "value"),
    State("new-schedule-status", "value"),
    State("current-job-id", "data"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_schedule_modal(add_clicks, cancel_clicks, save_clicks,
                          event_type, scheduled_date, scheduled_time, assigned_to,
                          notes, status, job_id, session_data):
    """Handle schedule modal"""

    triggered = ctx.triggered_id

    if triggered == "add-schedule-button":
        return True, None, None, None, "", "", "Scheduled"

    elif triggered == "cancel-schedule-button":
        return False, None, None, None, "", "", "Scheduled"

    elif triggered == "save-schedule-button":
        if not event_type or not scheduled_date:
            return True, event_type, scheduled_date, scheduled_time, assigned_to, notes, status

        db = get_authenticated_db(session_data)
        user_id = session_data.get('session', {}).get('user', {}).get('id')

        schedule_data = {
            'job_id': int(job_id),
            'event_type': event_type,
            'scheduled_date': scheduled_date,
            'scheduled_time': scheduled_time,
            'assigned_to': assigned_to,
            'event_notes': notes,
            'status': status or 'Scheduled'
        }

        db.insert_schedule_event(schedule_data, user_id)

        return False, None, None, None, "", "", "Scheduled"

    return False, None, None, None, "", "", "Scheduled"
