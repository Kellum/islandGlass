"""
Contractors Page
Main page with card grid and detail modal - merges old Directory + Detail pages
"""
print("DEBUG: contractors.py module is being imported!")
import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, ALL, MATCH, ctx, dcc
from dash_iconify import DashIconify
from modules.database import Database, get_authenticated_db
from components.contractor_card import create_contractor_card
from components.contractor_detail_modal import create_detail_modal

db = Database()

# Page layout
layout = html.Div([
    # Store for selected contractor ID
    dcc.Store(id='selected-contractor-store', data=None),

    # Store for outreach generation loading state
    dcc.Store(id='outreach-loading-store', data=False),

    # Store for view mode (card or list)
    dcc.Store(id='view-mode-store', data='card'),

    # Notification container for progress updates
    html.Div(id='outreach-notifications-container'),

    # Header
    dmc.Stack([
        dmc.Group([
            dmc.Title("Contractors", order=1),
            dmc.Group([
                html.Div(id="contractors-count-badge"),
                dmc.SegmentedControl(
                    id="view-mode-toggle",
                    value="card",
                    data=[
                        {"label": dmc.Center(DashIconify(icon="solar:widget-bold", width=18)), "value": "card"},
                        {"label": dmc.Center(DashIconify(icon="solar:list-bold", width=18)), "value": "list"},
                    ],
                    size="sm"
                )
            ], gap="md")
        ], justify="space-between"),

        dmc.Space(h=10),

        # Search and filters
        dmc.Grid([
            dmc.GridCol([
                dmc.TextInput(
                    id="contractor-search",
                    placeholder="Search company name...",
                    leftSection=DashIconify(icon="solar:magnifer-bold", width=18),
                    style={"width": "100%"},
                    value=""  # Initialize with empty string to trigger callback
                )
            ], span=4),

            dmc.GridCol([
                dmc.MultiSelect(
                    id="city-filter",
                    placeholder="Filter by city",
                    data=[],
                    clearable=True,
                    searchable=True,
                    value=[]  # Initialize with empty list
                )
            ], span=3),

            dmc.GridCol([
                dmc.Select(
                    id="status-filter",
                    placeholder="Enrichment status",
                    data=[
                        {"label": "All", "value": "all"},
                        {"label": "Completed", "value": "completed"},
                        {"label": "Pending", "value": "pending"},
                        {"label": "Failed", "value": "failed"},
                    ],
                    value="all",
                    clearable=False
                )
            ], span=2),

            dmc.GridCol([
                dmc.Select(
                    id="sort-by",
                    placeholder="Sort by",
                    data=[
                        {"label": "Company Name", "value": "name"},
                        {"label": "Score (High to Low)", "value": "score_desc"},
                        {"label": "Score (Low to High)", "value": "score_asc"},
                        {"label": "Date Added", "value": "date"},
                    ],
                    value="name",
                    clearable=False
                )
            ], span=3),
        ]),

        dmc.Space(h=20),

        # Contractor cards grid
        html.Div(
            id="contractors-grid",
            children=[dmc.Loader(color="blue", size="lg", type="dots")]  # Initial loading state
        ),

        # Detail modal container
        html.Div(id="detail-modal-container")
    ], gap="md")
])


# Callback: Load and filter contractors
@callback(
    Output("contractors-grid", "children"),
    Output("city-filter", "data"),
    Output("contractors-count-badge", "children"),
    Input("contractor-search", "value"),
    Input("city-filter", "value"),
    Input("status-filter", "value"),
    Input("sort-by", "value"),
    Input("view-mode-toggle", "value"),
    State("session-store", "data"),
)
def update_contractors_grid(search, cities, status, sort_by, view_mode, session_data):
    """Filter and display contractor cards"""
    print(f"DEBUG contractors: session_data={session_data}")

    # Get authenticated database instance
    auth_db = get_authenticated_db(session_data)

    # Get all contractors
    try:
        all_contractors = auth_db.get_all_contractors()
        print(f"DEBUG: Fetched {len(all_contractors)} contractors from database")
        print(f"DEBUG: Search={search}, Cities={cities}, Status={status}, Sort={sort_by}")
    except Exception as e:
        print(f"ERROR fetching contractors: {e}")
        import traceback
        traceback.print_exc()
        all_contractors = []

    if not all_contractors:
        return (
            dmc.Alert(
                "No contractors found in database. Use Discovery to add contractors.",
                title="No Data",
                color="yellow",
                icon=DashIconify(icon="solar:info-circle-bold")
            ),
            [],
            dmc.Badge("0 Total", size="lg", color="gray")
        )

    # Apply filters
    filtered = all_contractors.copy()

    if search:
        search_lower = search.lower()
        filtered = [c for c in filtered if search_lower in c.get('company_name', '').lower()]

    if cities and len(cities) > 0:
        filtered = [c for c in filtered if c.get('city') in cities]

    if status and status != "all":
        filtered = [c for c in filtered if c.get('enrichment_status') == status]

    # Apply sorting
    if sort_by == "name":
        filtered.sort(key=lambda x: x.get('company_name', '').lower())
    elif sort_by == "score_desc":
        filtered.sort(key=lambda x: x.get('lead_score') or 0, reverse=True)
    elif sort_by == "score_asc":
        filtered.sort(key=lambda x: x.get('lead_score') or 0)
    elif sort_by == "date":
        filtered.sort(key=lambda x: x.get('date_added', ''), reverse=True)

    # Get unique cities for filter dropdown
    cities_list = sorted(list(set([c.get('city') for c in all_contractors if c.get('city')])))
    city_options = [{"label": city, "value": city} for city in cities_list]

    # Create count badge
    count_badge = dmc.Badge(
        f"{len(filtered)} of {len(all_contractors)}",
        size="lg",
        color="blue"
    )

    # Create view based on mode
    if not filtered:
        view = dmc.Alert(
            "No contractors match your filters. Try adjusting your search criteria.",
            title="No Results",
            color="gray",
            icon=DashIconify(icon="solar:magnifer-bold")
        )
    else:
        if view_mode == "list":
            # List view - table format
            rows = []
            for contractor in filtered:
                rows.append(
                    dmc.TableTr([
                        dmc.TableTd(contractor.get('company_name', 'N/A')),
                        dmc.TableTd(f"{contractor.get('city', 'N/A')}, {contractor.get('state', 'FL')}"),
                        dmc.TableTd(contractor.get('contact_person') or 'N/A'),
                        dmc.TableTd(contractor.get('phone') or 'N/A'),
                        dmc.TableTd(
                            dmc.Badge(
                                f"{contractor.get('lead_score', 'N/A')}/10" if contractor.get('lead_score') else "Not Scored",
                                color="green" if contractor.get('lead_score') and contractor.get('lead_score') >= 8 else "blue",
                                variant="filled"
                            )
                        ),
                        dmc.TableTd(
                            dmc.Badge(
                                (contractor.get('enrichment_status') or 'pending').title(),
                                color={'completed': 'green', 'pending': 'yellow', 'failed': 'red'}.get(
                                    contractor.get('enrichment_status'), 'gray'
                                ),
                                variant="light"
                            )
                        ),
                        dmc.TableTd(
                            dmc.ActionIcon(
                                DashIconify(icon="solar:eye-bold", width=18),
                                variant="filled",
                                color="blue",
                                size="sm",
                                id={'type': 'view-detail-btn', 'index': contractor.get('id')}
                            )
                        ),
                    ])
                )

            view = dmc.Table([
                dmc.TableThead([
                    dmc.TableTr([
                        dmc.TableTh("Company"),
                        dmc.TableTh("Location"),
                        dmc.TableTh("Contact"),
                        dmc.TableTh("Phone"),
                        dmc.TableTh("Score"),
                        dmc.TableTh("Status"),
                        dmc.TableTh("Actions"),
                    ])
                ]),
                dmc.TableTbody(rows)
            ], striped=True, highlightOnHover=True, withTableBorder=True, withColumnBorders=True)
        else:
            # Card view - grid format
            cards = [
                dmc.GridCol(
                    create_contractor_card(contractor),
                    span={"base": 12, "sm": 6, "lg": 4}  # Responsive: 1 col mobile, 2 tablet, 3 desktop
                )
                for contractor in filtered
            ]
            view = dmc.Grid(cards, gutter="lg")

    return view, city_options, count_badge


# Callback: Open detail modal when card is clicked
@callback(
    Output("detail-modal-container", "children"),
    Output("selected-contractor-store", "data"),
    Input({"type": "view-detail-btn", "index": ALL}, "n_clicks"),
    State("selected-contractor-store", "data"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def open_detail_modal(n_clicks, current_contractor_id, session_data):
    """Open modal when View Details button is clicked"""
    if not any(n_clicks):
        return None, current_contractor_id

    # Get which button was clicked
    triggered_id = ctx.triggered_id
    if not triggered_id:
        return None, current_contractor_id

    contractor_id = triggered_id['index']

    # Get authenticated database instance
    auth_db = get_authenticated_db(session_data)

    # Fetch contractor details
    contractor = auth_db.get_contractor_by_id(contractor_id)

    if not contractor:
        return (
            dmc.Alert(
                "Contractor not found",
                title="Error",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold")
            ),
            None
        )

    # Fetch outreach materials
    outreach_data = auth_db.get_outreach_materials(contractor_id)
    # Transform database format to component format
    outreach_materials = None
    if outreach_data:
        outreach_materials = {
            'emails': [
                {
                    'id': item.get('id'),
                    'subject_line': item.get('subject_line'),
                    'content': item.get('content')
                }
                for item in outreach_data if item.get('material_type', '').startswith('email')
            ],
            'scripts': [
                {
                    'id': item.get('id'),
                    'content': item.get('content')
                }
                for item in outreach_data if item.get('material_type', '').startswith('script')
            ]
        }

    # Fetch interactions
    interactions = auth_db.get_interaction_history(contractor_id)

    return create_detail_modal(contractor, outreach_materials, interactions, is_open=True), contractor_id


# Callback: Close modal
@callback(
    Output("detail-modal-container", "children", allow_duplicate=True),
    Input("contractor-detail-modal", "opened"),
    prevent_initial_call=True
)
def close_modal(is_open):
    """Clear modal when closed"""
    if not is_open:
        return None
    return dash.no_update


# Callback: Show loading overlay when generate button is clicked
@callback(
    Output({'type': 'outreach-loading-overlay', 'index': MATCH}, 'visible'),
    Input({'type': 'generate-outreach-btn', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
)
def show_loading(n_clicks):
    """Show loading overlay when button is clicked"""
    if n_clicks:
        return True
    return dash.no_update


# Callback: Show progress notification when generate button is clicked
@callback(
    Output('outreach-notifications-container', 'children'),
    Input({"type": "generate-outreach-btn", "index": ALL}, "n_clicks"),
    State({"type": "email-quantity", "index": ALL}, "value"),
    State({"type": "script-quantity", "index": ALL}, "value"),
    prevent_initial_call=True
)
def show_progress_notification(n_clicks, email_quantities, script_quantities):
    """Show progress notification when button is clicked"""
    if not any(n_clicks):
        return dash.no_update

    triggered_id = ctx.triggered_id
    if not triggered_id or not triggered_id.get('index'):
        return dash.no_update

    # Extract quantities
    idx = 0  # Default to first item
    num_emails = int(email_quantities[idx]) if email_quantities else 3
    num_scripts = int(script_quantities[idx]) if script_quantities else 2

    progress_notification = dmc.Paper([
        dmc.Stack([
            dmc.Group([
                dmc.Loader(size="sm", color="blue", type="dots"),
                dmc.Text("Generating Outreach Materials", fw=600, size="lg")
            ], gap="sm"),
            dmc.Text("This will take 10-20 seconds...", size="sm", c="dimmed"),
            dmc.Space(h=10),
            dmc.Stepper(
                active=0,
                size="sm",
                children=[
                    dmc.StepperStep(label="Emails", description=f"Creating {num_emails} email template{'s' if num_emails > 1 else ''}"),
                    dmc.StepperStep(label="Scripts", description=f"Creating {num_scripts} call script{'s' if num_scripts > 1 else ''}"),
                    dmc.StepperStep(label="Save", description="Saving to database"),
                ]
            )
        ], gap="xs")
    ], p="lg", withBorder=True, shadow="lg", style={"position": "fixed", "bottom": "20px", "left": "50%", "transform": "translateX(-50%)", "zIndex": 10000, "minWidth": "400px", "backgroundColor": "white"})
    return progress_notification


# Callback: Generate outreach materials
@callback(
    Output("detail-modal-container", "children", allow_duplicate=True),
    Output('outreach-notifications-container', 'children', allow_duplicate=True),
    Input({"type": "generate-outreach-btn", "index": ALL}, "n_clicks"),
    State("selected-contractor-store", "data"),
    State({"type": "email-quantity", "index": ALL}, "value"),
    State({"type": "script-quantity", "index": ALL}, "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def generate_outreach(n_clicks, contractor_id, email_quantities, script_quantities, session_data):
    """Generate outreach materials using Claude AI"""
    print(f"DEBUG: Generate outreach called - n_clicks={n_clicks}, contractor_id={contractor_id}")

    if not any(n_clicks) or not contractor_id:
        print("DEBUG: Returning no_update - no clicks or no contractor_id")
        return dash.no_update, dash.no_update

    # Check if button was actually clicked (not just initialized)
    triggered_id = ctx.triggered_id
    print(f"DEBUG: triggered_id={triggered_id}")
    if not triggered_id or not triggered_id.get('index'):
        print("DEBUG: Returning no_update - no triggered_id")
        return dash.no_update, dash.no_update

    print(f"DEBUG: Starting outreach generation for contractor {contractor_id}")

    # Get authenticated database instance
    auth_db = get_authenticated_db(session_data)

    # Extract quantities from the lists (using triggered_id to find the right index)
    triggered_index = triggered_id.get('index')
    # Find the index in the ALL list that matches our triggered contractor_id
    idx = 0  # Default to first item if we can't find it
    num_emails = int(email_quantities[idx]) if email_quantities else 3
    num_scripts = int(script_quantities[idx]) if script_quantities else 2

    print(f"DEBUG: Generating {num_emails} emails and {num_scripts} scripts")

    # Import here to avoid circular imports
    from modules.outreach import OutreachGenerator

    try:
        # Generate outreach materials with authenticated database
        outreach_gen = OutreachGenerator(db=auth_db)

        # Get contractor
        contractor = auth_db.get_contractor_by_id(contractor_id)

        # Generate emails (with quantity)
        emails = outreach_gen.generate_email_templates(contractor, contractor_id, num_emails=num_emails)

        if not emails:
            error_notification = dmc.Alert(
                "Failed to generate email templates",
                title="Generation Failed",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold"),
                withCloseButton=True
            )
            return (
                create_detail_modal(contractor, None, None, is_open=True, active_tab="outreach"),
                error_notification
            )

        # Generate scripts (with quantity)
        scripts = outreach_gen.generate_call_scripts(contractor, contractor_id, num_scripts=num_scripts)

        if not scripts:
            error_notification = dmc.Alert(
                "Failed to generate call scripts",
                title="Generation Failed",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold"),
                withCloseButton=True
            )
            return (
                create_detail_modal(contractor, None, None, is_open=True, active_tab="outreach"),
                error_notification
            )

        # Save to database
        saved_count = 0
        for i in range(1, num_emails + 1):
            email_key = f"email_{i}"
            if email_key in emails:
                email_data = emails[email_key]
                if auth_db.save_outreach_material(
                    contractor_id=contractor_id,
                    material_type=email_key,
                    content=email_data.get('body', ''),
                    subject_line=email_data.get('subject', '')
                ):
                    saved_count += 1

        for i in range(1, num_scripts + 1):
            script_key = f"script_{i}"
            if script_key in scripts:
                if auth_db.save_outreach_material(
                    contractor_id=contractor_id,
                    material_type=script_key,
                    content=scripts[script_key],
                    subject_line=None
                ):
                    saved_count += 1

        # Refresh modal with new outreach materials
        outreach_data = auth_db.get_outreach_materials(contractor_id)
        outreach_materials = None
        if outreach_data:
            outreach_materials = {
                'emails': [
                    {
                        'subject_line': item.get('subject_line'),
                        'content': item.get('content')
                    }
                    for item in outreach_data if item.get('material_type', '').startswith('email')
                ],
                'scripts': [
                    {
                        'content': item.get('content')
                    }
                    for item in outreach_data if item.get('material_type', '').startswith('script')
                ]
            }

        interactions = auth_db.get_interaction_history(contractor_id)

        # Success notification
        success_notification = dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:check-circle-bold", width=24, color="green"),
                    dmc.Text("Success!", fw=600, size="lg", c="green")
                ], gap="sm"),
                dmc.Text(f"Generated {saved_count} outreach materials for {contractor.get('company_name')}", size="sm"),
            ], gap="xs")
        ], p="md", withBorder=True, shadow="lg", style={"position": "fixed", "bottom": "20px", "left": "50%", "transform": "translateX(-50%)", "zIndex": 10000, "minWidth": "350px", "backgroundColor": "#d4edda", "borderColor": "#28a745"})

        return (
            create_detail_modal(contractor, outreach_materials, interactions, is_open=True, active_tab="outreach"),
            success_notification
        )

    except Exception as e:
        contractor = auth_db.get_contractor_by_id(contractor_id)
        error_notification = dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:danger-circle-bold", width=24, color="red"),
                    dmc.Text("Error", fw=600, size="lg", c="red")
                ], gap="sm"),
                dmc.Text(f"Error generating outreach: {str(e)}", size="sm"),
            ], gap="xs")
        ], p="md", withBorder=True, shadow="lg", style={"position": "fixed", "bottom": "20px", "left": "50%", "transform": "translateX(-50%)", "zIndex": 10000, "minWidth": "350px", "backgroundColor": "#f8d7da", "borderColor": "#dc3545"})
        return (
            create_detail_modal(contractor, None, None, is_open=True, active_tab="outreach"),
            error_notification
        )


# Callback: Log interaction
@callback(
    Output({"type": "interaction-history", "index": MATCH}, "children"),
    Input({"type": "log-interaction-submit-btn", "index": MATCH}, "n_clicks"),
    State({"type": "interaction-status", "index": MATCH}, "value"),
    State({"type": "interaction-user", "index": MATCH}, "value"),
    State({"type": "interaction-notes", "index": MATCH}, "value"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def log_interaction(n_clicks, status, user_name, notes, session_data):
    """Log a new interaction"""
    if not n_clicks:
        return dash.no_update

    # Get contractor ID from MATCH pattern
    contractor_id = ctx.triggered_id['index']

    # Get authenticated database instance
    auth_db = get_authenticated_db(session_data)

    # Validate inputs
    if not status:
        return dmc.Alert("Please select a status", color="red", icon=DashIconify(icon="solar:danger-circle-bold"))

    if not user_name:
        return dmc.Alert("Please enter your name", color="red", icon=DashIconify(icon="solar:danger-circle-bold"))

    try:
        # Log the interaction
        auth_db.log_interaction(
            contractor_id=contractor_id,
            user_name=user_name,
            status=status,
            notes=notes or ""
        )

        # Fetch updated interactions
        interactions = auth_db.get_interaction_history(contractor_id)

        # Display success notification and updated history
        return dmc.Stack([
            dmc.Alert(
                "Interaction logged successfully!",
                title="Success",
                color="green",
                icon=DashIconify(icon="solar:check-circle-bold")
            ),
            dmc.Space(h=10),
            dmc.Stack([
                dmc.Card([
                    dmc.Group([
                        dmc.Badge(interaction.get('status', 'N/A').replace('_', ' ').title(), color="blue", variant="light"),
                        dmc.Text(interaction.get('date_logged', 'N/A'), size="sm", c="dimmed")
                    ], justify="space-between"),
                    dmc.Space(h=5),
                    dmc.Text(interaction.get('notes', 'No notes'), size="sm"),
                    dmc.Space(h=5),
                    dmc.Text(f"By: {interaction.get('user_name', 'Unknown')}", size="xs", c="dimmed")
                ], withBorder=True, padding="md")
                for interaction in (interactions or [])
            ], gap="sm") if interactions else dmc.Text("No interactions logged yet", c="dimmed", size="sm", style={"fontStyle": "italic"})
        ], gap="md")

    except Exception as e:
        return dmc.Alert(
            f"Error logging interaction: {str(e)}",
            title="Error",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold")
        )


# Callback: Delete outreach material
@callback(
    Output("detail-modal-container", "children", allow_duplicate=True),
    Input({"type": "delete-outreach-btn", "index": ALL}, "n_clicks"),
    State("selected-contractor-store", "data"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def delete_outreach_material(n_clicks, contractor_id, session_data):
    """Delete an outreach material (email or script)"""
    if not any(n_clicks) or not contractor_id:
        return dash.no_update

    # Get which delete button was clicked
    triggered_id = ctx.triggered_id
    if not triggered_id or not triggered_id.get('index'):
        return dash.no_update

    material_id = triggered_id.get('index')

    # Get authenticated database instance
    auth_db = get_authenticated_db(session_data)

    try:
        # Delete the outreach material
        auth_db.client.table("outreach_materials").delete().eq("id", material_id).execute()

        # Reload the modal with updated data
        contractor = auth_db.get_contractor_by_id(contractor_id)

        # Get updated outreach materials
        outreach_data = auth_db.get_outreach_materials(contractor_id)
        outreach_materials = {
            'emails': [
                {
                    'id': item.get('id'),
                    'subject_line': item.get('subject_line'),
                    'content': item.get('content')
                }
                for item in outreach_data if item.get('material_type', '').startswith('email')
            ],
            'scripts': [
                {
                    'id': item.get('id'),
                    'content': item.get('content')
                }
                for item in outreach_data if item.get('material_type', '').startswith('script')
            ]
        }

        interactions = auth_db.get_interaction_history(contractor_id)

        return create_detail_modal(contractor, outreach_materials, interactions, is_open=True, active_tab="outreach")

    except Exception as e:
        print(f"Error deleting outreach material: {e}")
        return dash.no_update
