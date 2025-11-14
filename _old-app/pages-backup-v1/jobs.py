"""
Jobs/POs List Page
Complete project management hub - where PO = Job

Features:
- List all jobs with filters
- Search by PO#, client, or description
- Filter by status, date range, client
- Quick status updates
- Click to view full job details
"""

import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, ctx
from dash_iconify import DashIconify
from modules.database import get_authenticated_db
from datetime import datetime, timedelta

# Layout
def layout(session_data=None):
    return dmc.Stack([
        # Header
        dmc.Group([
            dmc.Stack([
                dmc.Title("Jobs / Purchase Orders", order=1),
                dmc.Text("Manage all jobs and projects", c="dimmed", size="sm")
            ], gap=0),
            dmc.Button(
                "Create New Job",
                id="create-job-button",
                leftSection=DashIconify(icon="solar:add-circle-bold", width=20),
                color="blue"
            )
        ], justify="space-between"),
    
        dmc.Space(h=10),
    
        # Search and Filters Card
        dmc.Card([
            dmc.Grid([
                # Search
                dmc.GridCol([
                    dmc.TextInput(
                        id="job-search-input",
                        placeholder="Search by PO#, client, or description...",
                        leftSection=DashIconify(icon="solar:magnifer-bold", width=20),
                    )
                ], span=4),
    
                # Status Filter
                dmc.GridCol([
                    dmc.Select(
                        id="job-status-filter",
                        placeholder="Filter by status",
                        data=[
                            {"value": "all", "label": "All Statuses"},
                            {"value": "Quote", "label": "Quote"},
                            {"value": "Scheduled", "label": "Scheduled"},
                            {"value": "In Progress", "label": "In Progress"},
                            {"value": "Pending Materials", "label": "Pending Materials"},
                            {"value": "Ready for Install", "label": "Ready for Install"},
                            {"value": "Installed", "label": "Installed"},
                            {"value": "Completed", "label": "Completed"},
                            {"value": "On Hold", "label": "On Hold"},
                        ],
                        value="all",
                        clearable=True
                    )
                ], span=3),
    
                # Client Filter
                dmc.GridCol([
                    dmc.Select(
                        id="job-client-filter",
                        placeholder="Filter by client",
                        data=[],  # Populated dynamically
                        searchable=True,
                        clearable=True
                    )
                ], span=3),
    
                # Date Range Filter
                dmc.GridCol([
                    dmc.Select(
                        id="job-date-filter",
                        placeholder="Date range",
                        data=[
                            {"value": "all", "label": "All Time"},
                            {"value": "today", "label": "Today"},
                            {"value": "week", "label": "This Week"},
                            {"value": "month", "label": "This Month"},
                            {"value": "quarter", "label": "This Quarter"},
                            {"value": "year", "label": "This Year"},
                        ],
                        value="month",
                    )
                ], span=2),
            ])
        ], withBorder=True, p="md"),
    
        # Stats Cards
        dmc.Grid([
            dmc.GridCol([
                dmc.Card([
                    dmc.Group([
                        DashIconify(icon="solar:document-bold-duotone", width=40, color="blue"),
                        dmc.Stack([
                            dmc.Text("Total Jobs", size="sm", c="dimmed"),
                            dmc.Title(id="stat-total-jobs", order=3, children="0")
                        ], gap=0)
                    ])
                ], withBorder=True, p="md")
            ], span=3),
    
            dmc.GridCol([
                dmc.Card([
                    dmc.Group([
                        DashIconify(icon="solar:widget-5-bold-duotone", width=40, color="green"),
                        dmc.Stack([
                            dmc.Text("In Progress", size="sm", c="dimmed"),
                            dmc.Title(id="stat-in-progress", order=3, children="0")
                        ], gap=0)
                    ])
                ], withBorder=True, p="md")
            ], span=3),
    
            dmc.GridCol([
                dmc.Card([
                    dmc.Group([
                        DashIconify(icon="solar:clock-circle-bold-duotone", width=40, color="orange"),
                        dmc.Stack([
                            dmc.Text("Pending Materials", size="sm", c="dimmed"),
                            dmc.Title(id="stat-pending-materials", order=3, children="0")
                        ], gap=0)
                    ])
                ], withBorder=True, p="md")
            ], span=3),
    
            dmc.GridCol([
                dmc.Card([
                    dmc.Group([
                        DashIconify(icon="solar:check-circle-bold-duotone", width=40, color="teal"),
                        dmc.Stack([
                            dmc.Text("Completed", size="sm", c="dimmed"),
                            dmc.Title(id="stat-completed", order=3, children="0")
                        ], gap=0)
                    ])
                ], withBorder=True, p="md")
            ], span=3),
        ]),
    
        # Jobs List Container
        html.Div(id="jobs-list-container"),
    
        # Create Job Modal
        dmc.Modal(
            id="create-job-modal",
            title="Create New Job/PO",
            size="lg",
            children=[
                dmc.Stack([
                    dmc.TextInput(
                        id="new-job-po-number",
                        label="PO Number",
                        placeholder="e.g., 01-kellum.ryan-123acme",
                        required=True,
                        description="Your internal job/PO reference number"
                    ),
    
                    dmc.Select(
                        id="new-job-client",
                        label="Client",
                        placeholder="Select client",
                        data=[],  # Populated dynamically
                        searchable=True,
                        required=True
                    ),
    
                    dmc.Stack([
                        dmc.Text("Job Date", size="sm", fw=500),
                        dmc.DatePicker(
                            id="new-job-date",
                            value=datetime.now().strftime("%Y-%m-%d")
                        ),
                    ], gap="xs"),
    
                    dmc.Select(
                        id="new-job-status",
                        label="Initial Status",
                        data=[
                            {"value": "Quote", "label": "Quote"},
                            {"value": "Scheduled", "label": "Scheduled"},
                            {"value": "In Progress", "label": "In Progress"},
                        ],
                        value="Quote"
                    ),
    
                    dmc.Textarea(
                        id="new-job-description",
                        label="Job Description",
                        placeholder="Brief description of the work to be done...",
                        minRows=3
                    ),
    
                    dmc.Textarea(
                        id="new-job-site-address",
                        label="Site Address",
                        placeholder="Job site address...",
                        minRows=2
                    ),
    
                    dmc.Group([
                        dmc.Button("Cancel", id="cancel-job-button", variant="subtle", color="gray"),
                        dmc.Button("Create Job", id="save-new-job-button", color="blue"),
                    ], justify="flex-end")
                ], gap="md")
            ]
        ),

        ], gap="md", p="md")


# =====================================================
# CALLBACKS
# =====================================================

@callback(
    Output("create-job-modal", "opened"),
    Output("new-job-po-number", "value"),
    Output("new-job-client", "value"),
    Output("new-job-description", "value"),
    Output("new-job-site-address", "value"),
    Input("create-job-button", "n_clicks"),
    Input("cancel-job-button", "n_clicks"),
    Input("save-new-job-button", "n_clicks"),
    State("new-job-po-number", "value"),
    State("new-job-client", "value"),
    State("new-job-date", "value"),
    State("new-job-status", "value"),
    State("new-job-description", "value"),
    State("new-job-site-address", "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def handle_create_job_modal(create_clicks, cancel_clicks, save_clicks,
                            po_number, client_id, job_date, status,
                            description, site_address, session_data):
    """Handle create job modal open/close and save"""

    triggered = ctx.triggered_id

    if triggered == "create-job-button":
        # Open modal
        return True, "", None, "", ""

    elif triggered == "cancel-job-button":
        # Close modal
        return False, "", None, "", ""

    elif triggered == "save-new-job-button":
        # Validate and save
        if not po_number or not client_id:
            return True, po_number or "", client_id, description or "", site_address or ""

        # Get authenticated database
        db = get_authenticated_db(session_data)
        user_id = session_data.get('session', {}).get('user', {}).get('id') if session_data else None

        if not user_id:
            return False, "", None, "", ""

        # Create job
        job_data = {
            'po_number': po_number,
            'client_id': client_id,
            'job_date': job_date,
            'status': status,
            'job_description': description,
            'site_address': site_address
        }

        result = db.insert_job(job_data, user_id)

        if result:
            # Success - close modal and clear form
            return False, "", None, "", ""
        else:
            # Error - keep modal open
            return True, po_number, client_id, description, site_address

    return False, "", None, "", ""


@callback(
    Output("new-job-client", "data"),
    Output("job-client-filter", "data"),
    Input("create-job-modal", "opened"),
    Input("jobs-list-container", "children"),  # Reload on list changes
    State("session-store", "data"),
)
def load_client_options(modal_opened, list_children, session_data):
    """Load client options for dropdowns"""

    db = get_authenticated_db(session_data)

    # Get all clients
    clients = db.get_all_po_clients()

    client_options = [
        {"value": str(client['id']), "label": client['client_name']}
        for client in clients
    ]

    # Add "All Clients" option for filter
    filter_options = [{"value": "all", "label": "All Clients"}] + client_options

    return client_options, filter_options


@callback(
    Output("jobs-list-container", "children"),
    Output("stat-total-jobs", "children"),
    Output("stat-in-progress", "children"),
    Output("stat-pending-materials", "children"),
    Output("stat-completed", "children"),
    Input("job-search-input", "value"),
    Input("job-status-filter", "value"),
    Input("job-client-filter", "value"),
    Input("job-date-filter", "value"),
    Input("create-job-modal", "opened"),  # Reload after creating job
    State("session-store", "data"),
)
def load_jobs(search_term, status_filter, client_filter, date_filter, modal_opened, session_data):
    """Load and display jobs with filters"""
    print(f"DEBUG: load_jobs called!")
    print(f"DEBUG: session_data={session_data}")

    if not session_data:
        return dmc.Alert("Please log in to view jobs", color="red"), "0", "0", "0", "0"

    db = get_authenticated_db(session_data)

    # Try to get company_id from session, otherwise get from user profile
    company_id = session_data.get('session', {}).get('user', {}).get('company_id')

    if not company_id:
        # Get user's company from database (they should have one associated)
        user_id = session_data.get('session', {}).get('user', {}).get('id')
        if user_id:
            # Query user's company - for now, use a default company UUID
            # TODO: This should be properly set up with company management
            company_id = "00000000-0000-0000-0000-000000000000"  # Default company

    if not company_id:
        return dmc.Alert("No company ID found. Please contact administrator.", color="red"), "0", "0", "0", "0"

    # Get all jobs
    jobs = db.get_all_jobs(company_id)

    # Apply filters
    filtered_jobs = jobs

    # Status filter
    if status_filter and status_filter != "all":
        filtered_jobs = [j for j in filtered_jobs if j.get('status') == status_filter]

    # Client filter
    if client_filter and client_filter != "all":
        filtered_jobs = [j for j in filtered_jobs if str(j.get('client_id')) == client_filter]

    # Date filter
    if date_filter and date_filter != "all":
        today = datetime.now().date()
        if date_filter == "today":
            filtered_jobs = [j for j in filtered_jobs if j.get('job_date') == today]
        elif date_filter == "week":
            week_ago = today - timedelta(days=7)
            filtered_jobs = [j for j in filtered_jobs if j.get('job_date') and j.get('job_date') >= week_ago]
        elif date_filter == "month":
            month_ago = today - timedelta(days=30)
            filtered_jobs = [j for j in filtered_jobs if j.get('job_date') and j.get('job_date') >= month_ago]
        elif date_filter == "quarter":
            quarter_ago = today - timedelta(days=90)
            filtered_jobs = [j for j in filtered_jobs if j.get('job_date') and j.get('job_date') >= quarter_ago]
        elif date_filter == "year":
            year_ago = today - timedelta(days=365)
            filtered_jobs = [j for j in filtered_jobs if j.get('job_date') and j.get('job_date') >= year_ago]

    # Search filter
    if search_term:
        search_lower = search_term.lower()
        filtered_jobs = [
            j for j in filtered_jobs
            if search_lower in j.get('po_number', '').lower()
            or search_lower in j.get('job_description', '').lower()
            or (j.get('po_clients') and search_lower in j['po_clients'].get('client_name', '').lower())
        ]

    # Calculate stats
    total_jobs = len(jobs)
    in_progress = len([j for j in jobs if j.get('status') == 'In Progress'])
    pending_materials = len([j for j in jobs if j.get('status') == 'Pending Materials'])
    completed = len([j for j in jobs if j.get('status') == 'Completed'])

    # Create job cards
    if not filtered_jobs:
        return dmc.Alert(
            "No jobs found. Click 'Create New Job' to get started.",
            color="blue",
            title="No Jobs",
            icon=DashIconify(icon="solar:info-circle-bold")
        ), str(total_jobs), str(in_progress), str(pending_materials), str(completed)

    job_cards = []
    for job in filtered_jobs:
        job_cards.append(create_job_card(job))

    return dmc.Stack(job_cards, gap="md"), str(total_jobs), str(in_progress), str(pending_materials), str(completed)


def create_job_card(job):
    """Create a card for a single job"""

    # Status badge color
    status_colors = {
        'Quote': 'gray',
        'Scheduled': 'blue',
        'In Progress': 'green',
        'Pending Materials': 'orange',
        'Ready for Install': 'cyan',
        'Installed': 'teal',
        'Completed': 'teal',
        'Cancelled': 'red',
        'On Hold': 'yellow'
    }

    status = job.get('status', 'Quote')
    status_color = status_colors.get(status, 'gray')

    # Client name
    client_name = "Unknown Client"
    if job.get('po_clients'):
        client_name = job['po_clients'].get('client_name', 'Unknown Client')

    # Job date
    job_date = job.get('job_date')
    if job_date:
        if isinstance(job_date, str):
            job_date = datetime.fromisoformat(job_date).strftime("%m/%d/%Y")
        else:
            job_date = job_date.strftime("%m/%d/%Y")
    else:
        job_date = "No date"

    return dmc.Card([
        dmc.Group([
            # Left side - Job info
            dmc.Stack([
                dmc.Group([
                    dmc.Text(job.get('po_number', 'No PO#'), size="lg", fw=700),
                    dmc.Badge(status, color=status_color, variant="light"),
                ], gap="sm"),

                dmc.Text(client_name, size="sm", c="dimmed"),

                html.Div([
                    DashIconify(icon="solar:calendar-bold", width=16, style={"display": "inline", "margin-right": "5px"}),
                    dmc.Text(job_date, size="sm", c="dimmed", style={"display": "inline"})
                ]),

                dmc.Text(
                    job.get('job_description', 'No description')[:100] + ("..." if job.get('job_description', '') and len(job.get('job_description', '')) > 100 else ""),
                    size="sm",
                    lineClamp=2
                ),
            ], gap="xs", style={"flex": 1}),

            # Right side - Costs and actions
            dmc.Stack([
                dmc.Group([
                    dmc.Stack([
                        dmc.Text("Estimate", size="xs", c="dimmed"),
                        dmc.Text(f"${job.get('total_estimate', 0):,.2f}", size="sm", fw=600)
                    ], gap=0),

                    dmc.Stack([
                        dmc.Text("Actual", size="xs", c="dimmed"),
                        dmc.Text(f"${job.get('actual_cost', 0):,.2f}", size="sm", fw=600)
                    ], gap=0),
                ], gap="xl"),

                dmc.Button(
                    "View Details",
                    variant="light",
                    color="blue",
                    size="sm",
                    leftSection=DashIconify(icon="solar:eye-bold", width=16),
                    id={"type": "view-job-button", "index": job['job_id']},
                    style={"marginTop": "10px"}
                )
            ], align="flex-end", gap="xs")

        ], justify="space-between", align="flex-start"),
    ], withBorder=True, p="md", radius="md", style={"cursor": "pointer"})


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input({"type": "view-job-button", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def navigate_to_job_detail(n_clicks):
    """Navigate to job detail page"""
    if not any(n_clicks):
        return dash.no_update

    triggered = ctx.triggered_id
    if triggered and isinstance(triggered, dict):
        job_id = triggered['index']
        return f"/job/{job_id}"

    return dash.no_update
