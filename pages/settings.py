"""
Settings Page
API usage tracking, cost monitoring, system configuration, and user management
"""
import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, ctx
from dash_iconify import DashIconify
from modules.database import Database, get_authenticated_db
from modules import auth
from datetime import datetime, timedelta
import os

db = Database()

layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Title("Settings & Usage", order=1),
        dmc.Badge("Configuration", color="gray", variant="light", leftSection=DashIconify(icon="solar:settings-bold"))
    ], justify="space-between"),

    dmc.Text("Monitor API usage, costs, and system configuration", c="dimmed", size="sm"),

    dmc.Space(h=10),

    # Auto-refresh interval (every 60 seconds)
    dcc.Interval(id="settings-refresh-interval", interval=60000, n_intervals=0),

    # API Keys Status
    html.Div(id="settings-api-status"),

    dmc.Space(h=10),

    # Database Statistics
    html.Div(id="settings-database-stats"),

    dmc.Space(h=10),

    # API Usage Tracking
    html.Div(id="settings-api-usage"),

    dmc.Space(h=10),

    # Cost Breakdown
    html.Div(id="settings-cost-breakdown"),

    dmc.Space(h=10),

    # User Management (Owner Only)
    html.Div(id="settings-user-management"),

    # Hidden stores for user management state
    dcc.Store(id="user-management-refresh", data=0),

    # Add User Modal (must be in static layout for callbacks to work)
    dmc.Modal(
        id="add-user-modal",
        title=dmc.Group([
            DashIconify(icon="solar:user-plus-bold", width=24),
            dmc.Text("Add New User", fw=600)
        ]),
        children=[
            dmc.Stack([
                dmc.TextInput(
                    label="Email",
                    placeholder="user@example.com",
                    id="new-user-email",
                    required=True,
                    leftSection=DashIconify(icon="solar:letter-bold")
                ),
                dmc.PasswordInput(
                    label="Password",
                    placeholder="Secure password",
                    id="new-user-password",
                    required=True,
                    leftSection=DashIconify(icon="solar:lock-password-bold")
                ),
                dmc.TextInput(
                    label="Full Name",
                    placeholder="John Doe",
                    id="new-user-name",
                    required=True,
                    leftSection=DashIconify(icon="solar:user-bold")
                ),
                dmc.Select(
                    label="Role",
                    placeholder="Select role",
                    id="new-user-role",
                    data=[
                        {'label': 'Owner', 'value': 'owner'},
                        {'label': 'Admin', 'value': 'admin'},
                        {'label': 'Team Member', 'value': 'team_member'}
                    ],
                    value='team_member',
                    required=True
                ),
                html.Div(id="add-user-error"),
                dmc.Group([
                    dmc.Button("Cancel", id="cancel-add-user", variant="subtle", color="gray"),
                    dmc.Button("Create User", id="submit-add-user", variant="filled", color="blue",
                              leftSection=DashIconify(icon="solar:user-plus-bold"))
                ], justify="flex-end")
            ], gap="md")
        ],
        size="md",
        opened=False
    ),

], gap="md")


@callback(
    Output("settings-api-status", "children"),
    Output("settings-database-stats", "children"),
    Output("settings-api-usage", "children"),
    Output("settings-cost-breakdown", "children"),
    Output("settings-user-management", "children"),
    Input("settings-refresh-interval", "n_intervals"),
    Input("user-management-refresh", "data"),
    State("session-store", "data"),
)
def update_settings(_, refresh_trigger, session_data):
    """Load and display settings and usage data"""

    # ===== API Keys Status =====
    api_keys_status = []

    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_PLACES_API_KEY")

    api_keys = [
        {
            "name": "Supabase URL",
            "env_var": "SUPABASE_URL",
            "configured": bool(supabase_url),
            "icon": "solar:database-bold",
            "color": "blue"
        },
        {
            "name": "Supabase Key",
            "env_var": "SUPABASE_KEY",
            "configured": bool(supabase_key),
            "icon": "solar:key-bold",
            "color": "blue"
        },
        {
            "name": "Anthropic API",
            "env_var": "ANTHROPIC_API_KEY",
            "configured": bool(anthropic_key),
            "icon": "solar:magic-stick-bold",
            "color": "purple"
        },
        {
            "name": "Google Places API",
            "env_var": "GOOGLE_PLACES_API_KEY",
            "configured": bool(google_key),
            "icon": "solar:map-bold",
            "color": "orange"
        },
    ]

    api_status_section = dmc.Paper([
        dmc.Stack([
            dmc.Group([
                DashIconify(icon="solar:shield-check-bold", width=24, color="green"),
                dmc.Text("API Configuration Status", size="lg", fw=600)
            ], gap="sm"),

            dmc.SimpleGrid([
                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon=key["icon"], width=20, color=key["color"]),
                            dmc.Text(key["name"], size="sm", fw=500)
                        ], gap="xs"),
                        dmc.Group([
                            dmc.Badge(
                                "Configured" if key["configured"] else "Missing",
                                color="green" if key["configured"] else "red",
                                size="sm",
                                leftSection=DashIconify(
                                    icon="solar:check-circle-bold" if key["configured"] else "solar:close-circle-bold",
                                    width=12
                                )
                            ),
                            dmc.Text(key["env_var"], size="xs", c="dimmed")
                        ], justify="space-between")
                    ], gap="xs")
                ], p="md", withBorder=True)
                for key in api_keys
            ], cols=2, spacing="md")
        ], gap="md")
    ], p="md", withBorder=True)

    # ===== Database Statistics =====
    # Get authenticated database instance
    auth_db = get_authenticated_db(session_data)

    try:
        # Get all contractors
        all_contractors = auth_db.client.table("contractors").select("*").execute()
        contractors = all_contractors.data if all_contractors.data else []
        total_contractors = len(contractors)

        # Count by status
        enriched = len([c for c in contractors if c.get('enrichment_status') == 'completed'])
        pending = len([c for c in contractors if c.get('enrichment_status') == 'pending'])
        failed = len([c for c in contractors if c.get('enrichment_status') == 'failed'])

        # Count by source
        google_places = len([c for c in contractors if c.get('source') == 'google_places'])
        manual = len([c for c in contractors if c.get('source') == 'manual_entry'])
        csv_import = len([c for c in contractors if c.get('source') == 'csv_import'])

        # Count with outreach
        outreach_result = auth_db.client.table("outreach_materials").select("contractor_id", count="exact").execute()
        contractors_with_outreach = len(set([m['contractor_id'] for m in outreach_result.data])) if outreach_result.data else 0

        # Count interactions
        interactions_result = auth_db.client.table("interaction_log").select("*", count="exact").execute()
        total_interactions = interactions_result.count if hasattr(interactions_result, 'count') else len(interactions_result.data) if interactions_result.data else 0

    except Exception as e:
        total_contractors = "Error"
        enriched = pending = failed = 0
        google_places = manual = csv_import = 0
        contractors_with_outreach = 0
        total_interactions = 0

    database_stats_section = dmc.Paper([
        dmc.Stack([
            dmc.Group([
                DashIconify(icon="solar:database-bold", width=24, color="blue"),
                dmc.Text("Database Statistics", size="lg", fw=600)
            ], gap="sm"),

            # Main metrics
            dmc.SimpleGrid([
                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:buildings-2-bold", width=20, color="blue"),
                            dmc.Text("Total Contractors", size="sm", fw=500)
                        ], gap="xs"),
                        dmc.Text(str(total_contractors), size="xl", fw=700, c="blue")
                    ], gap="xs", align="center")
                ], p="md", withBorder=True),

                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:check-circle-bold", width=20, color="green"),
                            dmc.Text("Enriched", size="sm", fw=500)
                        ], gap="xs"),
                        dmc.Text(str(enriched), size="xl", fw=700, c="green")
                    ], gap="xs", align="center")
                ], p="md", withBorder=True),

                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:letter-bold", width=20, color="purple"),
                            dmc.Text("With Outreach", size="sm", fw=500)
                        ], gap="xs"),
                        dmc.Text(str(contractors_with_outreach), size="xl", fw=700, c="purple")
                    ], gap="xs", align="center")
                ], p="md", withBorder=True),

                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:chat-round-bold", width=20, color="orange"),
                            dmc.Text("Total Interactions", size="sm", fw=500)
                        ], gap="xs"),
                        dmc.Text(str(total_interactions), size="xl", fw=700, c="orange")
                    ], gap="xs", align="center")
                ], p="md", withBorder=True),
            ], cols=4, spacing="md"),

            # Breakdown by status
            dmc.Text("Contractor Status Breakdown", size="sm", fw=600, mt="md"),
            dmc.SimpleGrid([
                dmc.Stack([
                    dmc.Progress(
                        value=(enriched / total_contractors * 100) if total_contractors else 0,
                        color="green",
                        size="lg"
                    ),
                    dmc.Group([
                        dmc.Text("Enriched", size="sm"),
                        dmc.Text(f"{enriched} ({enriched / total_contractors * 100:.1f}%)" if total_contractors else "0", size="sm", c="dimmed")
                    ], justify="space-between")
                ], gap="xs"),

                dmc.Stack([
                    dmc.Progress(
                        value=(pending / total_contractors * 100) if total_contractors else 0,
                        color="orange",
                        size="lg"
                    ),
                    dmc.Group([
                        dmc.Text("Pending", size="sm"),
                        dmc.Text(f"{pending} ({pending / total_contractors * 100:.1f}%)" if total_contractors else "0", size="sm", c="dimmed")
                    ], justify="space-between")
                ], gap="xs"),

                dmc.Stack([
                    dmc.Progress(
                        value=(failed / total_contractors * 100) if total_contractors else 0,
                        color="red",
                        size="lg"
                    ),
                    dmc.Group([
                        dmc.Text("Failed", size="sm"),
                        dmc.Text(f"{failed} ({failed / total_contractors * 100:.1f}%)" if total_contractors else "0", size="sm", c="dimmed")
                    ], justify="space-between")
                ], gap="xs"),
            ], cols=1, spacing="md"),

            # Source breakdown
            dmc.Text("Contractor Sources", size="sm", fw=600, mt="md"),
            dmc.SimpleGrid([
                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:map-bold", width=16, color="orange"),
                            dmc.Text("Google Places", size="xs")
                        ], gap="xs"),
                        dmc.Text(str(google_places), size="lg", fw=700)
                    ], gap=0, align="center")
                ], p="sm", withBorder=True),

                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:pen-bold", width=16, color="teal"),
                            dmc.Text("Manual Entry", size="xs")
                        ], gap="xs"),
                        dmc.Text(str(manual), size="lg", fw=700)
                    ], gap=0, align="center")
                ], p="sm", withBorder=True),

                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:upload-minimalistic-bold", width=16, color="blue"),
                            dmc.Text("CSV Import", size="xs")
                        ], gap="xs"),
                        dmc.Text(str(csv_import), size="lg", fw=700)
                    ], gap=0, align="center")
                ], p="sm", withBorder=True),
            ], cols=3, spacing="md")
        ], gap="md")
    ], p="md", withBorder=True)

    # ===== API Usage Tracking =====
    try:
        # Get token tracking from app_settings
        settings = auth_db.client.table("app_settings").select("*").eq("key", "token_tracking").execute()

        if settings.data and settings.data[0].get('value'):
            token_data = settings.data[0]['value']
            total_input = token_data.get('total_input_tokens', 0)
            total_output = token_data.get('total_output_tokens', 0)
            total_cost = token_data.get('total_cost_usd', 0)
            enrichment_count = token_data.get('enrichment_count', 0)
            outreach_count = token_data.get('outreach_count', 0)
        else:
            total_input = total_output = total_cost = enrichment_count = outreach_count = 0

    except Exception as e:
        total_input = total_output = total_cost = enrichment_count = outreach_count = 0

    api_usage_section = dmc.Paper([
        dmc.Stack([
            dmc.Group([
                DashIconify(icon="solar:chart-bold", width=24, color="purple"),
                dmc.Text("Claude AI Usage Tracking", size="lg", fw=600)
            ], gap="sm"),

            dmc.Alert(
                "Usage data is tracked in the app_settings table. Costs are estimates based on Claude Haiku pricing.",
                color="blue",
                variant="light",
                icon=DashIconify(icon="solar:info-circle-bold")
            ),

            dmc.SimpleGrid([
                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:magic-stick-bold", width=20, color="purple"),
                            dmc.Text("Enrichments", size="sm", fw=500)
                        ], gap="xs"),
                        dmc.Text(str(enrichment_count), size="xl", fw=700),
                        dmc.Text(f"~${enrichment_count * 0.03:.2f} estimated", size="xs", c="dimmed")
                    ], gap="xs", align="center")
                ], p="md", withBorder=True),

                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:letter-bold", width=20, color="blue"),
                            dmc.Text("Outreach Generated", size="sm", fw=500)
                        ], gap="xs"),
                        dmc.Text(str(outreach_count), size="xl", fw=700),
                        dmc.Text(f"~${outreach_count * 0.03:.2f} estimated", size="xs", c="dimmed")
                    ], gap="xs", align="center")
                ], p="md", withBorder=True),

                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:chat-round-line-bold", width=20, color="green"),
                            dmc.Text("Input Tokens", size="sm", fw=500)
                        ], gap="xs"),
                        dmc.Text(f"{total_input:,}", size="xl", fw=700),
                        dmc.Text("Sent to Claude", size="xs", c="dimmed")
                    ], gap="xs", align="center")
                ], p="md", withBorder=True),

                dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:chat-round-bold", width=20, color="orange"),
                            dmc.Text("Output Tokens", size="sm", fw=500)
                        ], gap="xs"),
                        dmc.Text(f"{total_output:,}", size="xl", fw=700),
                        dmc.Text("Received from Claude", size="xs", c="dimmed")
                    ], gap="xs", align="center")
                ], p="md", withBorder=True),
            ], cols=4, spacing="md"),

            dmc.Paper([
                dmc.Stack([
                    dmc.Group([
                        DashIconify(icon="solar:dollar-bold", width=20, color="green"),
                        dmc.Text("Total Tracked Cost", size="sm", fw=600)
                    ], gap="xs"),
                    dmc.Text(f"${total_cost:.2f}", size="xl", fw=700, c="green"),
                    dmc.Text("Based on Claude Haiku pricing", size="xs", c="dimmed")
                ], gap="xs", align="center")
            ], p="md", withBorder=True, style={"backgroundColor": "rgba(0, 255, 0, 0.05)"})
        ], gap="md")
    ], p="md", withBorder=True)

    # ===== Cost Breakdown =====
    cost_breakdown_section = dmc.Paper([
        dmc.Stack([
            dmc.Group([
                DashIconify(icon="solar:dollar-bold", width=24, color="green"),
                dmc.Text("Cost Breakdown & Estimates", size="lg", fw=600)
            ], gap="sm"),

            dmc.Accordion([
                # Enrichment costs
                dmc.AccordionItem([
                    dmc.AccordionControl(
                        dmc.Group([
                            DashIconify(icon="solar:magic-stick-bold", width=20, color="purple"),
                            dmc.Stack([
                                dmc.Text("Website Enrichment", fw=500),
                                dmc.Text("Claude Haiku API", size="xs", c="dimmed")
                            ], gap=0),
                            dmc.Badge(f"${enrichment_count * 0.03:.2f}", color="purple", variant="light")
                        ], justify="space-between")
                    ),
                    dmc.AccordionPanel([
                        dmc.Stack([
                            dmc.Text("Pricing Details:", fw=600, size="sm"),
                            dmc.List([
                                dmc.ListItem(f"Enrichments performed: {enrichment_count}"),
                                dmc.ListItem("Average cost: $0.03 per contractor"),
                                dmc.ListItem("Includes: Website scraping, AI analysis, lead scoring"),
                                dmc.ListItem("Model: Claude 3 Haiku")
                            ], size="sm"),
                            dmc.Alert(
                                "Enrichment cost varies based on website content length. Average is ~$0.03 per contractor.",
                                color="purple",
                                variant="light"
                            )
                        ], gap="xs")
                    ])
                ], value="enrichment"),

                # Outreach costs
                dmc.AccordionItem([
                    dmc.AccordionControl(
                        dmc.Group([
                            DashIconify(icon="solar:letter-bold", width=20, color="blue"),
                            dmc.Stack([
                                dmc.Text("Outreach Generation", fw=500),
                                dmc.Text("3 emails + 2 call scripts", size="xs", c="dimmed")
                            ], gap=0),
                            dmc.Badge(f"${outreach_count * 0.03:.2f}", color="blue", variant="light")
                        ], justify="space-between")
                    ),
                    dmc.AccordionPanel([
                        dmc.Stack([
                            dmc.Text("Pricing Details:", fw=600, size="sm"),
                            dmc.List([
                                dmc.ListItem(f"Outreach generated: {outreach_count} contractors"),
                                dmc.ListItem("Average cost: $0.03 per contractor"),
                                dmc.ListItem("Includes: 3 email variants + 2 call scripts"),
                                dmc.ListItem("Personalized based on enrichment data")
                            ], size="sm"),
                            dmc.Alert(
                                "Each outreach generation creates 5 personalized materials (3 emails, 2 scripts).",
                                color="blue",
                                variant="light"
                            )
                        ], gap="xs")
                    ])
                ], value="outreach"),

                # Google Places costs
                dmc.AccordionItem([
                    dmc.AccordionControl(
                        dmc.Group([
                            DashIconify(icon="solar:map-bold", width=20, color="orange"),
                            dmc.Stack([
                                dmc.Text("Google Places Discovery", fw=500),
                                dmc.Text("Contractor search", size="xs", c="dimmed")
                            ], gap=0),
                            dmc.Badge(f"~${google_places * 0.003:.2f}", color="orange", variant="light")
                        ], justify="space-between")
                    ),
                    dmc.AccordionPanel([
                        dmc.Stack([
                            dmc.Text("Pricing Details:", fw=600, size="sm"),
                            dmc.List([
                                dmc.ListItem(f"Contractors discovered: {google_places}"),
                                dmc.ListItem("Cost: ~$0.003 per contractor found"),
                                dmc.ListItem("Includes: Name, phone, address, rating, reviews"),
                                dmc.ListItem("Pagination: Up to 60 results per search")
                            ], size="sm"),
                            dmc.Alert(
                                "Google Places API charges per search. Each search can return up to 60 results.",
                                color="orange",
                                variant="light"
                            )
                        ], gap="xs")
                    ])
                ], value="google"),

                # Total summary
                dmc.AccordionItem([
                    dmc.AccordionControl(
                        dmc.Group([
                            DashIconify(icon="solar:calculator-bold", width=20, color="green"),
                            dmc.Stack([
                                dmc.Text("Total Cost Summary", fw=500),
                                dmc.Text("All operations", size="xs", c="dimmed")
                            ], gap=0),
                            dmc.Badge(
                                f"${(enrichment_count * 0.03) + (outreach_count * 0.03) + (google_places * 0.003):.2f}",
                                color="green",
                                variant="filled",
                                size="lg"
                            )
                        ], justify="space-between")
                    ),
                    dmc.AccordionPanel([
                        dmc.Stack([
                            dmc.SimpleGrid([
                                dmc.Stack([
                                    dmc.Text("Per Contractor Breakdown:", fw=600, size="sm"),
                                    dmc.List([
                                        dmc.ListItem("Discovery: $0.003"),
                                        dmc.ListItem("Enrichment: $0.03"),
                                        dmc.ListItem("Outreach: $0.03"),
                                        dmc.ListItem(dmc.Text([
                                            "Total: ",
                                            dmc.Text("$0.063", fw=700, span=True)
                                        ]))
                                    ], size="sm")
                                ], gap="xs"),

                                dmc.Stack([
                                    dmc.Text("Optimization Tips:", fw=600, size="sm"),
                                    dmc.List([
                                        dmc.ListItem("Only enrich high-value contractors"),
                                        dmc.ListItem("Generate outreach in batches"),
                                        dmc.ListItem("Use broad Google searches"),
                                        dmc.ListItem("Filter results before enrichment")
                                    ], size="sm")
                                ], gap="xs"),
                            ], cols=2, spacing="md"),

                            dmc.Alert(
                                [
                                    dmc.Text("Budget-Friendly Approach:", fw=600, size="sm"),
                                    dmc.Text(
                                        "Discover contractors ($0.003) → Review manually → Enrich only promising leads ($0.03) → Generate outreach for hot leads ($0.03)",
                                        size="sm"
                                    )
                                ],
                                color="green",
                                variant="light",
                                icon=DashIconify(icon="solar:lightbulb-bold")
                            )
                        ], gap="md")
                    ])
                ], value="total"),
            ], value="total")
        ], gap="md")
    ], p="md", withBorder=True)

    # ===== User Management (Owner Only) =====
    user_management_section = None

    # Check if user is authenticated and is owner
    if session_data and session_data.get('user'):
        current_user = session_data['user']
        user_role = current_user.get('role')

        if user_role == 'owner':
            # Fetch all users
            try:
                users = auth.get_all_users()

                # User stats
                total_users = len(users)
                active_users = len([u for u in users if u.get('is_active')])
                owners = len([u for u in users if u.get('role') == 'owner'])
                admins = len([u for u in users if u.get('role') == 'admin'])
                team_members = len([u for u in users if u.get('role') == 'team_member'])

                # Create user list table
                user_rows = []
                for user in users:
                    last_login = user.get('last_login')
                    # Fix timestamps with too many decimal places
                    if last_login:
                        try:
                            # Remove 'Z' and truncate microseconds to 6 digits
                            last_login_clean = last_login.replace('Z', '+00:00')
                            # Handle microseconds with more than 6 digits
                            if '.' in last_login_clean:
                                parts = last_login_clean.split('.')
                                if len(parts) == 2:
                                    # Truncate microseconds to 6 digits
                                    microseconds = parts[1].split('+')[0].split('-')[0]
                                    if len(microseconds) > 6:
                                        microseconds = microseconds[:6]
                                    # Reconstruct with truncated microseconds
                                    timezone = '+00:00' if '+' in parts[1] or '-' in parts[1] else ''
                                    last_login_clean = f"{parts[0]}.{microseconds}{timezone}"
                            last_login_str = datetime.fromisoformat(last_login_clean).strftime('%b %d, %Y %I:%M %p')
                        except Exception as e:
                            print(f"ERROR parsing timestamp {last_login}: {e}")
                            last_login_str = 'Invalid date'
                    else:
                        last_login_str = 'Never'

                    user_rows.append(
                        html.Tr([
                            html.Td(user.get('email', 'N/A')),
                            html.Td(user.get('full_name', 'N/A')),
                            html.Td(
                                dmc.Badge(
                                    user.get('role', 'N/A').replace('_', ' ').title(),
                                    color='red' if user.get('role') == 'owner' else 'blue' if user.get('role') == 'admin' else 'green',
                                    variant='light'
                                )
                            ),
                            html.Td(last_login_str),
                            html.Td(
                                dmc.Badge(
                                    "Active" if user.get('is_active') else "Inactive",
                                    color='green' if user.get('is_active') else 'red',
                                    variant='light'
                                )
                            ),
                            html.Td(
                                dmc.Group([
                                    dmc.Select(
                                        id={'type': 'user-role-select', 'user_id': user.get('id')},
                                        value=user.get('role'),
                                        data=[
                                            {'label': 'Owner', 'value': 'owner'},
                                            {'label': 'Admin', 'value': 'admin'},
                                            {'label': 'Team Member', 'value': 'team_member'}
                                        ],
                                        size='xs',
                                        style={'width': '140px'}
                                    ),
                                    dmc.ActionIcon(
                                        DashIconify(
                                            icon='solar:eye-closed-bold' if user.get('is_active') else 'solar:eye-bold',
                                            width=16
                                        ),
                                        id={'type': 'toggle-user-status', 'user_id': user.get('id')},
                                        variant='subtle',
                                        color='red' if user.get('is_active') else 'green',
                                        size='sm',
                                        disabled=(user.get('id') == current_user.get('id'))  # Can't deactivate self
                                    )
                                ], gap='xs')
                            )
                        ])
                    )

                user_management_section = dmc.Paper([
                    dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:users-group-rounded-bold", width=24, color="red"),
                            dmc.Text("User Management", size="lg", fw=600),
                            dmc.Badge("Owner Only", color="red", variant="filled")
                        ], gap="sm", justify="space-between"),

                        # User stats
                        dmc.SimpleGrid([
                            dmc.Paper([
                                dmc.Stack([
                                    dmc.Group([
                                        DashIconify(icon="solar:users-group-rounded-bold", width=20, color="blue"),
                                        dmc.Text("Total Users", size="sm", fw=500)
                                    ], gap="xs"),
                                    dmc.Text(str(total_users), size="xl", fw=700, c="blue")
                                ], gap="xs", align="center")
                            ], p="md", withBorder=True),

                            dmc.Paper([
                                dmc.Stack([
                                    dmc.Group([
                                        DashIconify(icon="solar:check-circle-bold", width=20, color="green"),
                                        dmc.Text("Active", size="sm", fw=500)
                                    ], gap="xs"),
                                    dmc.Text(str(active_users), size="xl", fw=700, c="green")
                                ], gap="xs", align="center")
                            ], p="md", withBorder=True),

                            dmc.Paper([
                                dmc.Stack([
                                    dmc.Text("By Role", size="sm", fw=500),
                                    dmc.Group([
                                        dmc.Badge(f"{owners} Owner", color="red", size="sm"),
                                        dmc.Badge(f"{admins} Admin", color="blue", size="sm"),
                                        dmc.Badge(f"{team_members} Team", color="green", size="sm")
                                    ], gap="xs")
                                ], gap="xs", align="center")
                            ], p="md", withBorder=True)
                        ], cols=3, spacing="md"),

                        # Add user button
                        dmc.Button(
                            "Add User",
                            id="open-add-user-modal",
                            leftSection=DashIconify(icon="solar:user-plus-bold"),
                            variant="filled",
                            color="blue",
                            size="sm"
                        ),

                        # User list table
                        dmc.Table([
                            html.Thead(
                                html.Tr([
                                    html.Th("Email"),
                                    html.Th("Full Name"),
                                    html.Th("Role"),
                                    html.Th("Last Login"),
                                    html.Th("Status"),
                                    html.Th("Actions")
                                ])
                            ),
                            html.Tbody(user_rows)
                        ], striped=True, highlightOnHover=True, withTableBorder=True, withColumnBorders=True)
                    ], gap="md")
                ], p="md", withBorder=True)

            except Exception as e:
                user_management_section = dmc.Paper([
                    dmc.Alert(
                        f"Error loading user management: {str(e)}",
                        color="red",
                        icon=DashIconify(icon="solar:danger-bold")
                    )
                ], p="md", withBorder=True)
        else:
            # Non-owner users see access denied
            user_management_section = dmc.Paper([
                dmc.Stack([
                    dmc.Group([
                        DashIconify(icon="solar:shield-warning-bold", width=24, color="orange"),
                        dmc.Text("User Management", size="lg", fw=600)
                    ], gap="sm"),
                    dmc.Alert(
                        "User management is only available to owners. Contact your system administrator if you need to manage users.",
                        color="orange",
                        icon=DashIconify(icon="solar:lock-bold"),
                        title="Access Denied"
                    )
                ], gap="md")
            ], p="md", withBorder=True)
    else:
        # Not authenticated - show nothing
        user_management_section = html.Div()

    return api_status_section, database_stats_section, api_usage_section, cost_breakdown_section, user_management_section


# ========== User Management Callbacks ==========

@callback(
    Output("add-user-modal", "opened"),
    Input("open-add-user-modal", "n_clicks"),
    Input("cancel-add-user", "n_clicks"),
    Input("user-management-refresh", "data"),
    State("add-user-modal", "opened"),
    prevent_initial_call=True
)
def toggle_add_user_modal(open_clicks, cancel_clicks, refresh_count, is_opened):
    """Open/close the add user modal - closes when user is created (refresh triggered) or cancelled"""
    triggered_id = ctx.triggered_id

    if triggered_id == "open-add-user-modal":
        return True
    elif triggered_id == "cancel-add-user":
        return False
    elif triggered_id == "user-management-refresh":
        # Close modal after successful user creation
        return False

    return is_opened


print("DEBUG: Registering create_new_user callback...")

@callback(
    Output("add-user-error", "children"),
    Output("user-management-refresh", "data"),
    Output("new-user-email", "value"),
    Output("new-user-password", "value"),
    Output("new-user-name", "value"),
    Output("new-user-role", "value"),
    Input("submit-add-user", "n_clicks"),
    State("new-user-email", "value"),
    State("new-user-password", "value"),
    State("new-user-name", "value"),
    State("new-user-role", "value"),
    State("session-store", "data"),
    State("user-management-refresh", "data"),
    prevent_initial_call=True
)
def create_new_user(n_clicks, email, password, full_name, role, session_data, refresh_count):
    """Create a new user"""
    print(f"DEBUG create_new_user CALLED: n_clicks={n_clicks}, email={email}, role={role}")
    print(f"DEBUG session_data: {session_data}")

    if not n_clicks:
        print("DEBUG: No clicks, returning no_update")
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Validate inputs
    if not email or not password or not full_name or not role:
        print(f"DEBUG: Validation failed - email={email}, password={'***' if password else None}, full_name={full_name}, role={role}")
        return dmc.Alert(
            "All fields are required",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        ), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Check if user is owner
    if not session_data or not session_data.get('user'):
        print(f"DEBUG: No session or user in session_data")
        return dmc.Alert(
            "You must be logged in",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        ), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    current_user = session_data['user']
    print(f"DEBUG current_user: {current_user}")
    print(f"DEBUG current_user role: {current_user.get('role')}")

    if current_user.get('role') != 'owner':
        print(f"DEBUG: User role is '{current_user.get('role')}', not 'owner'")
        return dmc.Alert(
            "Only owners can create users",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        ), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Create user
    try:
        print(f"DEBUG: Calling auth.create_user for {email}")
        result = auth.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            created_by_id=current_user.get('id')
        )
        print(f"DEBUG: auth.create_user result: {result}")

        if result.get('success'):
            # Clear form and refresh user list
            return dmc.Alert(
                f"User {email} created successfully",
                color="green",
                icon=DashIconify(icon="solar:check-circle-bold")
            ), refresh_count + 1, "", "", "", "team_member"
        else:
            return dmc.Alert(
                result.get('error', 'Failed to create user'),
                color="red",
                icon=DashIconify(icon="solar:danger-bold")
            ), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    except Exception as e:
        return dmc.Alert(
            f"Error: {str(e)}",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        ), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@callback(
    Output("user-management-refresh", "data", allow_duplicate=True),
    Input({"type": "user-role-select", "user_id": dash.ALL}, "value"),
    State({"type": "user-role-select", "user_id": dash.ALL}, "id"),
    State("session-store", "data"),
    State("user-management-refresh", "data"),
    prevent_initial_call=True
)
def update_user_role(values, ids, session_data, refresh_count):
    """Update user role when changed in dropdown"""
    if not ctx.triggered_id:
        return dash.no_update

    # Check if user is owner
    if not session_data or not session_data.get('user'):
        return dash.no_update

    current_user = session_data['user']
    if current_user.get('role') != 'owner':
        return dash.no_update

    # Get the user_id and new role
    triggered_id = ctx.triggered_id
    user_id = triggered_id['user_id']

    # Find the index of the triggered dropdown
    idx = [i for i, id_dict in enumerate(ids) if id_dict['user_id'] == user_id][0]
    new_role = values[idx]

    try:
        result = auth.update_user_role(
            user_id=user_id,
            new_role=new_role,
            updated_by_id=current_user.get('id')
        )

        if result.get('success'):
            return refresh_count + 1
        else:
            return dash.no_update

    except Exception as e:
        print(f"Error updating role: {e}")
        return dash.no_update


@callback(
    Output("user-management-refresh", "data", allow_duplicate=True),
    Input({"type": "toggle-user-status", "user_id": dash.ALL}, "n_clicks"),
    State({"type": "toggle-user-status", "user_id": dash.ALL}, "id"),
    State("session-store", "data"),
    State("user-management-refresh", "data"),
    prevent_initial_call=True
)
def toggle_user_status(n_clicks, ids, session_data, refresh_count):
    """Toggle user active status"""
    if not ctx.triggered_id:
        return dash.no_update

    # Check if user is owner
    if not session_data or not session_data.get('user'):
        return dash.no_update

    current_user = session_data['user']
    if current_user.get('role') != 'owner':
        return dash.no_update

    # Get the user_id
    triggered_id = ctx.triggered_id
    user_id = triggered_id['user_id']

    # Get current user status
    try:
        users = auth.get_all_users()
        target_user = next((u for u in users if u.get('id') == user_id), None)

        if not target_user:
            return dash.no_update

        # Toggle status
        if target_user.get('is_active'):
            result = auth.deactivate_user(user_id, current_user.get('id'))
        else:
            result = auth.activate_user(user_id, current_user.get('id'))

        if result.get('success'):
            return refresh_count + 1
        else:
            return dash.no_update

    except Exception as e:
        print(f"Error toggling user status: {e}")
        return dash.no_update
