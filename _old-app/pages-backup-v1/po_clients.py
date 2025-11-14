"""
PO Clients Page
Customer relationship management for purchase orders

Features:
- Client cards with company info and PO count
- Search by company name or contact
- Filter by city and client type
- Add/edit/delete clients
- Card grid layout
"""

import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, MATCH, ALL, ctx
from dash_iconify import DashIconify
from modules.database import get_authenticated_db

# PO Clients Layout
layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Stack([
            dmc.Title("PO Tracker", order=1),
            dmc.Text("Manage clients and purchase orders", c="dimmed", size="sm")
        ], gap=0),
        dmc.Button(
            "Add New Client",
            id="add-client-button",
            leftSection=DashIconify(icon="solar:add-circle-bold", width=20),
            color="blue"
        )
    ], justify="space-between"),

    dmc.Space(h=10),

    # Search and Filters
    dmc.Card([
        dmc.Grid([
            dmc.GridCol([
                dmc.TextInput(
                    id="po-search-input",
                    placeholder="Search by company or contact name...",
                    leftSection=DashIconify(icon="solar:magnifer-bold", width=20),
                )
            ], span=4),

            dmc.GridCol([
                dmc.Select(
                    id="po-city-filter",
                    placeholder="Filter by city",
                    data=[],  # Will be populated dynamically
                    clearable=True,
                    searchable=True
                )
            ], span=4),

            dmc.GridCol([
                dmc.Select(
                    id="po-type-filter",
                    placeholder="Filter by type",
                    data=[
                        {"value": "contractor", "label": "Contractor"},
                        {"value": "residential", "label": "Residential"},
                        {"value": "commercial", "label": "Commercial"}
                    ],
                    clearable=True
                )
            ], span=4),
        ])
    ], withBorder=True, p="md"),

    # Results Container
    html.Div(id="po-clients-container"),

    # Add Client Modal
    dmc.Modal(
        id="add-client-modal",
        title="Add New Client",
        size="lg",
        children=[
            dmc.Stack([
                # Client Type Selector - Top of Form
                dmc.Select(
                    id="new-client-type",
                    label="Client Type",
                    placeholder="Select client type",
                    data=[
                        {"value": "residential", "label": "Residential"},
                        {"value": "contractor", "label": "Contractor"},
                        {"value": "commercial", "label": "Commercial"}
                    ],
                    required=True,
                    description="Choose the type of client"
                ),

                dmc.Space(h="sm"),

                # Client Name Fields - All exist, shown/hidden dynamically
                html.Div([
                    # Prompt when no type selected
                    dmc.Alert(
                        "Please select a client type first",
                        id="client-type-prompt",
                        color="blue",
                        icon=DashIconify(icon="solar:info-circle-bold")
                    ),

                    # Residential fields
                    html.Div(id="residential-name-fields", style={"display": "none"}, children=[
                        dmc.Text("Client Name", size="sm", fw=500, c="dimmed"),
                        dmc.Grid([
                            dmc.GridCol([
                                dmc.TextInput(
                                    id="new-client-first",
                                    placeholder="First Name"
                                )
                            ], span=6),
                            dmc.GridCol([
                                dmc.TextInput(
                                    id="new-client-last",
                                    placeholder="Last Name"
                                )
                            ], span=6),
                        ])
                    ]),

                    # Company field
                    html.Div(id="company-name-field", style={"display": "none"}, children=[
                        dmc.TextInput(
                            id="new-client-company",
                            label="Company Name",
                            placeholder="Enter company name"
                        )
                    ])
                ]),

                dmc.Space(h="sm"),

                # Primary Contact Section
                dmc.Divider(label="Primary Contact", labelPosition="center"),

                dmc.Grid([
                    dmc.GridCol([
                        dmc.TextInput(
                            id="new-contact-first",
                            label="First Name",
                            placeholder="John",
                            required=True
                        )
                    ], span=6),
                    dmc.GridCol([
                        dmc.TextInput(
                            id="new-contact-last",
                            label="Last Name",
                            placeholder="Doe",
                            required=True
                        )
                    ], span=6),
                ]),

                dmc.Grid([
                    dmc.GridCol([
                        dmc.TextInput(
                            id="new-contact-email",
                            label="Contact Email",
                            placeholder="john@company.com"
                        )
                    ], span=6),
                    dmc.GridCol([
                        dmc.TextInput(
                            id="new-contact-phone",
                            label="Contact Phone",
                            placeholder="(555) 123-4567"
                        )
                    ], span=6),
                ]),

                dmc.TextInput(
                    id="new-contact-jobtitle",
                    label="Job Title / Role",
                    placeholder="Project Manager, Owner, etc."
                ),

                # Additional Contacts Section
                dmc.Divider(label="Additional Contacts (Optional)", labelPosition="center"),

                html.Div(id="additional-contacts-list", children=[]),

                dmc.Button(
                    "Add Another Contact",
                    id="add-contact-button",
                    variant="subtle",
                    leftSection=DashIconify(icon="solar:add-circle-bold"),
                    fullWidth=True
                ),

                # Hidden store for contacts data
                dcc.Store(id="contacts-store", data=[]),

                dmc.Space(h="md"),

                dmc.TextInput(
                    id="new-client-address",
                    label="Address",
                    placeholder="123 Main St"
                ),

                dmc.Grid([
                    dmc.GridCol([
                        dmc.TextInput(
                            id="new-client-city",
                            label="City",
                            placeholder="Jacksonville"
                        )
                    ], span=6),
                    dmc.GridCol([
                        dmc.TextInput(
                            id="new-client-state",
                            label="State",
                            value="FL"
                        )
                    ], span=3),
                    dmc.GridCol([
                        dmc.TextInput(
                            id="new-client-zip",
                            label="ZIP",
                            placeholder="32256"
                        )
                    ], span=3),
                ]),

                dmc.Textarea(
                    id="new-client-notes",
                    label="Notes",
                    placeholder="Additional notes...",
                    minRows=3
                ),

                dmc.Group([
                    dmc.Button(
                        "Cancel",
                        id="cancel-add-client",
                        variant="subtle",
                        color="gray"
                    ),
                    dmc.Button(
                        "Add Client",
                        id="submit-add-client",
                        leftSection=DashIconify(icon="solar:add-circle-bold", width=18)
                    )
                ], justify="flex-end", mt="md")
            ], gap="sm")
        ]
    ),

    # Notification container
    html.Div(id="po-notification-container")

], gap="md")


# Callback to open/cancel add client modal
@callback(
    Output("add-client-modal", "opened"),
    Input("add-client-button", "n_clicks"),
    Input("cancel-add-client", "n_clicks"),
    State("add-client-modal", "opened"),
    prevent_initial_call=True
)
def toggle_add_modal(open_clicks, cancel_clicks, is_opened):
    """Toggle add client modal (submit is handled by add_new_client callback)"""
    triggered_id = ctx.triggered_id

    if triggered_id == "add-client-button":
        return True
    elif triggered_id == "cancel-add-client":
        return False

    return is_opened


# Callback to show/hide client name fields based on client type
@callback(
    Output("residential-name-fields", "style"),
    Output("company-name-field", "style"),
    Output("client-type-prompt", "style"),
    Input("new-client-type", "value")
)
def update_client_name_fields(client_type):
    """Show/hide input fields based on client type (components always exist, just hidden)"""
    if not client_type:
        # Show prompt, hide all fields
        return {"display": "none"}, {"display": "none"}, {}
    elif client_type == "residential":
        # Show residential fields, hide company field and prompt
        return {}, {"display": "none"}, {"display": "none"}
    else:
        # Show company field, hide residential fields and prompt
        return {"display": "none"}, {}, {"display": "none"}


# Callback to manage additional contacts
@callback(
    Output("additional-contacts-list", "children"),
    Output("contacts-store", "data"),
    Input("add-contact-button", "n_clicks"),
    Input({'type': 'remove-contact', 'index': ALL}, 'n_clicks'),
    State("contacts-store", "data"),
    prevent_initial_call=True
)
def manage_additional_contacts(add_clicks, remove_clicks, contacts):
    """Add or remove additional contact cards"""
    if not contacts:
        contacts = []

    triggered = ctx.triggered_id

    # Check if add button was clicked
    if triggered == "add-contact-button":
        contact_id = len(contacts)
        contacts.append({'id': contact_id})

    # Check if remove button was clicked
    elif triggered and isinstance(triggered, dict) and triggered.get('type') == 'remove-contact':
        remove_index = triggered['index']
        contacts = [c for c in contacts if c['id'] != remove_index]

    # Generate contact cards
    cards = []
    for i, contact in enumerate(contacts):
        cards.append(
            dmc.Card([
                dmc.Stack([
                    dmc.Group([
                        dmc.Text(f"Contact #{i+1}", fw=500, size="sm"),
                        dmc.ActionIcon(
                            DashIconify(icon="solar:trash-bin-bold"),
                            id={'type': 'remove-contact', 'index': contact['id']},
                            color="red",
                            variant="subtle",
                            size="sm"
                        )
                    ], justify="space-between"),

                    dmc.Grid([
                        dmc.GridCol([
                            dmc.TextInput(
                                id={'type': 'additional-contact-first', 'index': contact['id']},
                                placeholder="First Name",
                                size="sm"
                            )
                        ], span=6),
                        dmc.GridCol([
                            dmc.TextInput(
                                id={'type': 'additional-contact-last', 'index': contact['id']},
                                placeholder="Last Name",
                                size="sm"
                            )
                        ], span=6),
                    ]),

                    dmc.Grid([
                        dmc.GridCol([
                            dmc.TextInput(
                                id={'type': 'additional-contact-email', 'index': contact['id']},
                                placeholder="Email",
                                size="sm"
                            )
                        ], span=6),
                        dmc.GridCol([
                            dmc.TextInput(
                                id={'type': 'additional-contact-phone', 'index': contact['id']},
                                placeholder="Phone",
                                size="sm"
                            )
                        ], span=6),
                    ]),

                    dmc.TextInput(
                        id={'type': 'additional-contact-jobtitle', 'index': contact['id']},
                        placeholder="Job Title",
                        size="sm"
                    ),
                ], gap="xs")
            ], withBorder=True, p="sm", mb="sm")
        )

    return cards, contacts


print("DEBUG: About to register add_new_client callback...")

# Callback to submit new client
@callback(
    Output("po-clients-container", "children", allow_duplicate=True),
    Output("po-notification-container", "children"),
    Output("add-client-modal", "opened", allow_duplicate=True),
    Input("submit-add-client", "n_clicks"),
    State("new-client-type", "value"),
    State("new-client-first", "value"),  # For residential
    State("new-client-last", "value"),   # For residential
    State("new-client-company", "value"), # For contractor/commercial
    State("new-contact-first", "value"),
    State("new-contact-last", "value"),
    State("new-contact-email", "value"),
    State("new-contact-phone", "value"),
    State("new-contact-jobtitle", "value"),
    State("new-client-address", "value"),
    State("new-client-city", "value"),
    State("new-client-state", "value"),
    State("new-client-zip", "value"),
    State("new-client-notes", "value"),
    # Additional contacts (pattern-matching)
    State({'type': 'additional-contact-first', 'index': ALL}, 'value'),
    State({'type': 'additional-contact-last', 'index': ALL}, 'value'),
    State({'type': 'additional-contact-email', 'index': ALL}, 'value'),
    State({'type': 'additional-contact-phone', 'index': ALL}, 'value'),
    State({'type': 'additional-contact-jobtitle', 'index': ALL}, 'value'),
    # REMOVED: State("session-store", "data") - See TROUBLESHOOTING_LOG.md Issue #1
    prevent_initial_call=True
)
def add_new_client(
    n_clicks, client_type,
    client_first, client_last, company_name,
    contact_first, contact_last, contact_email, contact_phone, contact_jobtitle,
    address, city, state, zip_code, notes,
    additional_first, additional_last, additional_email, additional_phone, additional_jobtitle
):
    """Add new client to database"""
    print(f"🔥🔥🔥 ADD CLIENT CALLBACK FIRED! n_clicks={n_clicks}, client_type={client_type}")

    # Determine client_name based on client_type
    client_name = None
    if client_type == "residential":
        if not client_first or not client_last:
            return dash.no_update, dmc.Notification(
                title="Validation Error",
                message="First and last name are required for residential clients",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold"),
                action="show"
            ), dash.no_update
        client_name = f"{client_first} {client_last}"
    else:
        # Contractor or commercial
        if not company_name:
            return dash.no_update, dmc.Notification(
                title="Validation Error",
                message="Company name is required for contractor/commercial clients",
                color="red",
                icon=DashIconify(icon="solar:danger-circle-bold"),
                action="show"
            ), dash.no_update
        client_name = company_name

    # Validate contact info
    if not contact_first or not contact_last:
        return dash.no_update, dmc.Notification(
            title="Validation Error",
            message="Primary contact first and last name are required",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        ), dash.no_update

    # Get database connection without session auth
    # NOTE: user_id will be None - see TROUBLESHOOTING_LOG.md Issue #1
    from modules.database import Database
    db = Database()
    user_id = None

    print(f"DEBUG add_new_client: user_id={user_id} (None - no session), client_name={client_name}")

    # Prepare client data
    client_data = {
        "client_name": client_name,
        "client_type": client_type or "contractor",
        "address": address,
        "city": city,
        "state": state or "FL",
        "zip": zip_code,
        "notes": notes
    }

    # Insert client with user_id for audit trail
    client = db.insert_po_client(client_data, user_id)

    if not client:
        return dash.no_update, dmc.Notification(
            title="Error",
            message="Failed to create client",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        ), dash.no_update

    # Create primary contact
    contact_data = {
        'client_id': client['id'],
        'first_name': contact_first,
        'last_name': contact_last,
        'email': contact_email,
        'phone': contact_phone,
        'job_title': contact_jobtitle,
        'is_primary': True
    }

    contact = db.insert_client_contact(contact_data, user_id)

    if not contact:
        # Rollback: delete the client
        db.delete_po_client(client['id'], user_id)
        return dash.no_update, dmc.Notification(
            title="Error",
            message="Failed to create contact",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        ), dash.no_update

    # Create additional contacts
    additional_contacts_count = 0
    if additional_first and len(additional_first) > 0:
        for i in range(len(additional_first)):
            # Skip if first or last name is empty
            if not additional_first[i] or not additional_last[i]:
                continue

            additional_contact_data = {
                'client_id': client['id'],
                'first_name': additional_first[i],
                'last_name': additional_last[i],
                'email': additional_email[i] if i < len(additional_email) else None,
                'phone': additional_phone[i] if i < len(additional_phone) else None,
                'job_title': additional_jobtitle[i] if i < len(additional_jobtitle) else None,
                'is_primary': False
            }

            additional_contact = db.insert_client_contact(additional_contact_data, user_id)
            if additional_contact:
                additional_contacts_count += 1

    # Reload clients
    clients = db.get_po_client_with_po_count()

    # Build success message
    success_message = f"Client '{client_name}' added successfully"
    if additional_contacts_count > 0:
        success_message += f" with {additional_contacts_count + 1} contact(s)"

    notification = dmc.Notification(
        title="Success",
        message=success_message,
        color="green",
        icon=DashIconify(icon="solar:check-circle-bold"),
        action="show"
    )

    print(f"DEBUG: Client added successfully, returning {len(clients)} clients")

    return render_client_cards(clients), notification, False  # Close modal

print("DEBUG: add_new_client callback has been registered!")

# Callback to load and display clients
@callback(
    Output("po-clients-container", "children"),
    Output("po-city-filter", "data"),
    Input("po-search-input", "value"),
    Input("po-city-filter", "value"),
    Input("po-type-filter", "value"),
    State("session-store", "data")
)
def load_clients(search_term, city_filter, type_filter, session_data):
    """Load and filter PO clients"""

    # Get authenticated database
    db = get_authenticated_db(session_data)

    # Get all clients with PO count
    clients = db.get_po_client_with_po_count()

    # Apply filters
    if search_term:
        search_lower = search_term.lower()
        clients = [
            c for c in clients
            if search_lower in c.get('client_name', '').lower()
        ]

    if city_filter:
        clients = [c for c in clients if c.get('city') == city_filter]

    if type_filter:
        clients = [c for c in clients if c.get('client_type') == type_filter]

    # Get unique cities for filter dropdown
    all_clients = db.get_all_po_clients()
    cities = sorted(list(set([c.get('city') for c in all_clients if c.get('city')])))
    city_options = [{"value": city, "label": city} for city in cities]

    return render_client_cards(clients), city_options


def render_client_cards(clients):
    """Render client cards in grid"""

    if not clients:
        return dmc.Card([
            dmc.Center([
                dmc.Stack([
                    DashIconify(icon="solar:users-group-rounded-bold", width=64, color="#868e96"),
                    dmc.Text("No clients found", size="lg", c="dimmed"),
                    dmc.Text("Add a new client to get started", size="sm", c="dimmed")
                ], align="center", gap="xs")
            ], style={"padding": "60px 0"})
        ], withBorder=True)

    return dmc.Stack([
        dmc.Text(f"Showing {len(clients)} client(s)", size="sm", c="dimmed"),

        dmc.Grid([
            dmc.GridCol(
                create_client_card(client),
                span={"base": 12, "sm": 6, "lg": 4}
            )
            for client in clients
        ], gutter="lg")
    ], gap="sm")


def create_client_card(client):
    """Create a single client card"""

    client_id = client.get('id')
    client_name = client.get('client_name', 'Unknown')
    city = client.get('city', 'Unknown')
    state = client.get('state', 'FL')
    client_type = client.get('client_type', 'N/A')
    po_count = client.get('po_count', 0)

    # Type badge color
    type_colors = {
        'contractor': 'blue',
        'residential': 'green',
        'commercial': 'orange'
    }
    type_color = type_colors.get(client_type, 'gray')

    # Get primary contact info
    primary_contact = client.get('primary_contact', {})
    contact_name = 'No contact'
    contact_email = 'No email'
    contact_phone = 'No phone'

    if primary_contact:
        first = primary_contact.get('first_name', '')
        last = primary_contact.get('last_name', '')
        if first or last:
            contact_name = f"{first} {last}".strip()
        contact_email = primary_contact.get('email') or 'No email'
        contact_phone = primary_contact.get('phone') or 'No phone'
        job_title = primary_contact.get('job_title')
        if job_title:
            contact_name = f"{contact_name} ({job_title})"

    return dmc.Card([
        dmc.Stack([
            # Header with client name and type
            dmc.Group([
                dmc.Text(client_name, size="lg", fw=700, style={"flex": 1}),
                dmc.Badge(
                    client_type.title() if client_type != 'N/A' else 'N/A',
                    color=type_color,
                    variant="light"
                )
            ], justify="space-between", wrap="nowrap"),

            # Location
            dmc.Group([
                DashIconify(icon="solar:map-point-bold", width=16, color="#868e96"),
                dmc.Text(f"{city}, {state}", size="sm", c="dimmed")
            ], gap=5),

            dmc.Divider(),

            # Contact info
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:user-bold", width=16, color="#868e96"),
                    dmc.Text(contact_name, size="sm")
                ], gap=5),

                dmc.Group([
                    DashIconify(icon="solar:phone-bold", width=16, color="#868e96"),
                    dmc.Text(contact_phone, size="sm")
                ], gap=5),

                dmc.Group([
                    DashIconify(icon="solar:letter-bold", width=16, color="#868e96"),
                    dmc.Text(
                        contact_email if len(contact_email) <= 25 else contact_email[:22] + "...",
                        size="sm"
                    )
                ], gap=5),
            ], gap="xs"),

            dmc.Divider(),

            # PO Count
            dmc.Group([
                dmc.Text("Purchase Orders:", size="sm", c="dimmed"),
                dmc.Badge(str(po_count), color="blue", variant="filled")
            ], justify="space-between"),

            # Action buttons
            dmc.Group([
                dmc.Button(
                    "View Details",
                    id={'type': 'view-client-btn', 'index': client_id},
                    variant="light",
                    fullWidth=True,
                    leftSection=DashIconify(icon="solar:eye-bold", width=18),
                    size="sm"
                ),
                dmc.ActionIcon(
                    DashIconify(icon="solar:trash-bin-trash-bold", width=18),
                    id={'type': 'delete-client-btn', 'index': client_id},
                    variant="light",
                    color="red",
                    size="lg"
                )
            ], gap="xs")
        ], gap="sm")
    ], withBorder=True, shadow="sm", p="md", style={"height": "100%"})


# Callback to handle delete client
@callback(
    Output("po-clients-container", "children", allow_duplicate=True),
    Output("po-notification-container", "children", allow_duplicate=True),
    Input({'type': 'delete-client-btn', 'index': ALL}, 'n_clicks'),
    State("session-store", "data"),
    prevent_initial_call=True
)
def delete_client(n_clicks_list, session_data):
    """Delete a client"""

    if not any(n_clicks_list):
        return dash.no_update, dash.no_update

    # Get which button was clicked
    triggered = ctx.triggered_id
    if not triggered:
        return dash.no_update, dash.no_update

    client_id = triggered['index']

    # Get authenticated database
    db = get_authenticated_db(session_data)

    # Get user_id from session - FIXED: correct path is session_data['session']['user']['id']
    user_id = None
    if session_data and 'session' in session_data:
        user_id = session_data['session'].get('user', {}).get('id')
    if not user_id:
        return dash.no_update, dmc.Notification(
            title="Error",
            message="User authentication required",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )

    # Soft delete client with user_id for audit trail
    success = db.delete_po_client(client_id, user_id)

    if success:
        # Reload clients
        clients = db.get_po_client_with_po_count()

        notification = dmc.Notification(
            title="Deleted",
            message="Client deleted successfully",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold"),
            action="show"
        )

        return render_client_cards(clients), notification
    else:
        return dash.no_update, dmc.Notification(
            title="Error",
            message="Failed to delete client",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )
