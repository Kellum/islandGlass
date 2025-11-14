"""
Dashboard Page
Main overview with metrics, statistics, and recent activity
"""
import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc
from dash_iconify import DashIconify
from modules.database import Database, get_authenticated_db
from datetime import datetime

db = Database()

layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Title("Dashboard", order=1),
        dmc.Badge("Overview", color="blue", variant="light")
    ], justify="space-between"),

    dmc.Text("Manage your business operations", c="dimmed", size="sm"),

    dmc.Space(h=10),

    # Auto-refresh interval (every 30 seconds)
    dcc.Interval(id="dashboard-refresh-interval", interval=30000, n_intervals=0),

    # Tabbed View
    dmc.Tabs(
        value="clients",
        children=[
            dmc.TabsList([
                dmc.TabsTab("Clients & POs", value="clients", leftSection=DashIconify(icon="solar:users-group-rounded-bold", width=18)),
                dmc.TabsTab("Leads & Sales", value="leads", leftSection=DashIconify(icon="solar:chart-2-bold", width=18)),
            ]),

            # Leads & Sales Tab
            dmc.TabsPanel(
                value="leads",
                children=dmc.Stack([
                    # Main metrics container
                    html.Div(id="dashboard-metrics-container"),
                    dmc.Space(h=10),
                    # Charts and activity container
                    html.Div(id="dashboard-content-container"),
                ], gap="md")
            ),

            # Clients & POs Tab
            dmc.TabsPanel(
                value="clients",
                children=html.Div(id="dashboard-clients-container")
            ),
        ],
        id="dashboard-tabs"
    ),

], gap="md")


@callback(
    Output("dashboard-metrics-container", "children"),
    Output("dashboard-content-container", "children"),
    Input("dashboard-refresh-interval", "n_intervals"),
    State("session-store", "data"),
)
def update_dashboard(_, session_data):
    """Load and display dashboard metrics"""

    # Get authenticated database instance
    auth_db = get_authenticated_db(session_data)

    # Get all contractors
    try:
        all_contractors = auth_db.get_all_contractors()
        contractors = all_contractors if all_contractors else []
    except Exception as e:
        print(f"ERROR loading contractors on dashboard: {e}")
        contractors = []

    # Calculate metrics
    total_contractors = len(contractors)

    enriched_contractors = [c for c in contractors if c.get('enrichment_status') == 'completed']
    enriched_count = len(enriched_contractors)

    pending_contractors = [c for c in contractors if c.get('enrichment_status') == 'pending' or not c.get('enrichment_status')]
    pending_count = len(pending_contractors)

    failed_contractors = [c for c in contractors if c.get('enrichment_status') == 'failed']
    failed_count = len(failed_contractors)

    high_priority = [c for c in enriched_contractors if c.get('lead_score', 0) >= 8]
    high_priority_count = len(high_priority)

    medium_priority = [c for c in enriched_contractors if 5 <= c.get('lead_score', 0) < 8]
    medium_priority_count = len(medium_priority)

    low_priority = [c for c in enriched_contractors if c.get('lead_score', 0) < 5]
    low_priority_count = len(low_priority)

    # Get contractors with outreach materials
    try:
        outreach = db.client.table("outreach_materials").select("contractor_id").execute()
        contractors_with_outreach = len(set([o['contractor_id'] for o in outreach.data])) if outreach.data else 0
    except:
        contractors_with_outreach = 0

    # Get interaction count
    try:
        interactions = db.client.table("interaction_log").select("*", count="exact").execute()
        interaction_count = interactions.count if hasattr(interactions, 'count') else len(interactions.data) if interactions.data else 0
    except:
        interaction_count = 0

    # Calculate enrichment rate
    enrichment_rate = round((enriched_count / total_contractors * 100) if total_contractors > 0 else 0, 1)

    # Top Metrics Cards
    metrics = dmc.SimpleGrid([
        # Total Contractors
        dmc.Tooltip(
            label="Total number of contractors in your database",
            children=dmc.Paper([
                dmc.Stack([
                    dmc.Group([
                        DashIconify(icon="solar:users-group-rounded-bold", width=32, color="blue"),
                        dmc.Stack([
                            dmc.Text("Total Contractors", size="xs", c="dimmed", fw=500),
                            dmc.Text(str(total_contractors), size="xl", fw=700, c="blue"),
                        ], gap=0)
                    ], justify="space-between"),
                    dmc.Progress(value=100, color="blue", size="xs"),
                    dmc.Text("All contractors", size="xs", c="dimmed")
                ], gap="xs")
            ], p="md", withBorder=True, radius="md", style={"cursor": "help"})
        ),

        # Enriched
        dmc.Tooltip(
            label=f"Contractors successfully analyzed with Claude AI ({enrichment_rate}% of total)",
            children=dmc.Paper([
                dmc.Stack([
                    dmc.Group([
                        DashIconify(icon="solar:magic-stick-bold", width=32, color="green"),
                        dmc.Stack([
                            dmc.Text("Enriched", size="xs", c="dimmed", fw=500),
                            dmc.Text(str(enriched_count), size="xl", fw=700, c="green"),
                        ], gap=0)
                    ], justify="space-between"),
                    dmc.Progress(value=enrichment_rate, color="green", size="xs"),
                    dmc.Text(f"{enrichment_rate}% enriched", size="xs", c="dimmed")
                ], gap="xs")
            ], p="md", withBorder=True, radius="md", style={"cursor": "help"})
        ),

        # High Priority
        dmc.Tooltip(
            label="High-quality leads with scores 8+ (hot prospects)",
            children=dmc.Paper([
                dmc.Stack([
                    dmc.Group([
                        DashIconify(icon="solar:fire-bold", width=32, color="orange"),
                        dmc.Stack([
                            dmc.Text("High Priority", size="xs", c="dimmed", fw=500),
                            dmc.Text(str(high_priority_count), size="xl", fw=700, c="orange"),
                        ], gap=0)
                    ], justify="space-between"),
                    dmc.Progress(
                        value=(high_priority_count / enriched_count * 100) if enriched_count > 0 else 0,
                        color="orange",
                        size="xs"
                    ),
                    dmc.Text("Lead score 8-10", size="xs", c="dimmed")
                ], gap="xs")
            ], p="md", withBorder=True, radius="md", style={"cursor": "help"})
        ),

        # Pending
        dmc.Tooltip(
            label="Contractors awaiting enrichment (need Claude AI analysis)",
            children=dmc.Paper([
                dmc.Stack([
                    dmc.Group([
                        DashIconify(icon="solar:clock-circle-bold", width=32, color="gray"),
                        dmc.Stack([
                            dmc.Text("Pending", size="xs", c="dimmed", fw=500),
                            dmc.Text(str(pending_count), size="xl", fw=700, c="gray"),
                        ], gap=0)
                    ], justify="space-between"),
                    dmc.Progress(
                        value=(pending_count / total_contractors * 100) if total_contractors > 0 else 0,
                        color="gray",
                        size="xs"
                    ),
                    dmc.Text("Awaiting enrichment", size="xs", c="dimmed")
                ], gap="xs")
            ], p="md", withBorder=True, radius="md", style={"cursor": "help"})
        ),
    ], cols=4, spacing="md")

    # Secondary metrics and charts
    content = dmc.Stack([
        # Lead Score Distribution
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    dmc.Text("Lead Score Distribution", size="lg", fw=600),
                    dmc.Badge(f"{enriched_count} enriched", color="purple", variant="light")
                ], justify="space-between"),

                dmc.SimpleGrid([
                    dmc.Stack([
                        dmc.Group([
                            dmc.ThemeIcon(
                                DashIconify(icon="solar:fire-bold", width=20),
                                size="lg",
                                radius="md",
                                color="red",
                                variant="light"
                            ),
                            dmc.Stack([
                                dmc.Text("Hot Leads", size="sm", fw=500),
                                dmc.Text("Score 8-10", size="xs", c="dimmed")
                            ], gap=0)
                        ], gap="sm"),
                        dmc.Group([
                            dmc.Text(str(high_priority_count), size="xl", fw=700),
                            dmc.Text(
                                f"{round(high_priority_count / enriched_count * 100, 1)}%" if enriched_count > 0 else "0%",
                                size="sm",
                                c="dimmed"
                            )
                        ], gap="xs"),
                        dmc.Progress(
                            value=(high_priority_count / enriched_count * 100) if enriched_count > 0 else 0,
                            color="red",
                            size="md"
                        )
                    ], gap="xs"),

                    dmc.Stack([
                        dmc.Group([
                            dmc.ThemeIcon(
                                DashIconify(icon="solar:star-bold", width=20),
                                size="lg",
                                radius="md",
                                color="yellow",
                                variant="light"
                            ),
                            dmc.Stack([
                                dmc.Text("Warm Leads", size="sm", fw=500),
                                dmc.Text("Score 5-7", size="xs", c="dimmed")
                            ], gap=0)
                        ], gap="sm"),
                        dmc.Group([
                            dmc.Text(str(medium_priority_count), size="xl", fw=700),
                            dmc.Text(
                                f"{round(medium_priority_count / enriched_count * 100, 1)}%" if enriched_count > 0 else "0%",
                                size="sm",
                                c="dimmed"
                            )
                        ], gap="xs"),
                        dmc.Progress(
                            value=(medium_priority_count / enriched_count * 100) if enriched_count > 0 else 0,
                            color="yellow",
                            size="md"
                        )
                    ], gap="xs"),

                    dmc.Stack([
                        dmc.Group([
                            dmc.ThemeIcon(
                                DashIconify(icon="solar:check-circle-bold", width=20),
                                size="lg",
                                radius="md",
                                color="blue",
                                variant="light"
                            ),
                            dmc.Stack([
                                dmc.Text("Cold Leads", size="sm", fw=500),
                                dmc.Text("Score 1-4", size="xs", c="dimmed")
                            ], gap=0)
                        ], gap="sm"),
                        dmc.Group([
                            dmc.Text(str(low_priority_count), size="xl", fw=700),
                            dmc.Text(
                                f"{round(low_priority_count / enriched_count * 100, 1)}%" if enriched_count > 0 else "0%",
                                size="sm",
                                c="dimmed"
                            )
                        ], gap="xs"),
                        dmc.Progress(
                            value=(low_priority_count / enriched_count * 100) if enriched_count > 0 else 0,
                            color="blue",
                            size="md"
                        )
                    ], gap="xs"),
                ], cols=3, spacing="lg")
            ], gap="md")
        ], p="lg", withBorder=True, radius="md"),

        # Activity & Status
        dmc.SimpleGrid([
            # Enrichment Status
            dmc.Paper([
                dmc.Stack([
                    dmc.Group([
                        DashIconify(icon="solar:chart-bold", width=24, color="purple"),
                        dmc.Text("Enrichment Status", size="md", fw=600)
                    ], gap="sm"),

                    dmc.Stack([
                        dmc.Group([
                            dmc.Badge("Completed", color="green", size="lg", variant="light"),
                            dmc.Text(str(enriched_count), size="lg", fw=700, c="green")
                        ], justify="space-between"),

                        dmc.Group([
                            dmc.Badge("Pending", color="orange", size="lg", variant="light"),
                            dmc.Text(str(pending_count), size="lg", fw=700, c="orange")
                        ], justify="space-between"),

                        dmc.Group([
                            dmc.Badge("Failed", color="red", size="lg", variant="light"),
                            dmc.Text(str(failed_count), size="lg", fw=700, c="red")
                        ], justify="space-between"),
                    ], gap="md")
                ], gap="md")
            ], p="md", withBorder=True, radius="md"),

            # Outreach Activity
            dmc.Paper([
                dmc.Stack([
                    dmc.Group([
                        DashIconify(icon="solar:letter-bold", width=24, color="blue"),
                        dmc.Text("Outreach Activity", size="md", fw=600)
                    ], gap="sm"),

                    dmc.Stack([
                        dmc.Group([
                            dmc.Stack([
                                dmc.Text("With Outreach", size="xs", c="dimmed"),
                                dmc.Text(str(contractors_with_outreach), size="xl", fw=700, c="blue")
                            ], gap=0),
                            dmc.Stack([
                                dmc.Text("Interactions", size="xs", c="dimmed"),
                                dmc.Text(str(interaction_count), size="xl", fw=700, c="green")
                            ], gap=0)
                        ], grow=True),

                        dmc.Stack([
                            dmc.Progress(
                                value=(contractors_with_outreach / enriched_count * 100) if enriched_count > 0 else 0,
                                color="blue",
                                size="sm"
                            ),
                            dmc.Text(
                                f"{round(contractors_with_outreach / enriched_count * 100, 1)}% have outreach" if enriched_count > 0 else "0%",
                                size="xs",
                                c="dimmed",
                                ta="center"
                            )
                        ], gap=4)
                    ], gap="md")
                ], gap="md")
            ], p="md", withBorder=True, radius="md"),
        ], cols=2, spacing="md"),

        # Top Contractors
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    dmc.Group([
                        DashIconify(icon="solar:star-bold", width=24, color="orange"),
                        dmc.Text("Top Priority Contractors", size="md", fw=600)
                    ], gap="sm"),
                    dmc.Badge(f"Top {min(10, high_priority_count)}", color="orange", variant="light")
                ], justify="space-between"),

                dmc.Stack([
                    dmc.Group([
                        dmc.Stack([
                            dmc.Text(contractor['company_name'], fw=500, size="sm"),
                            dmc.Text(
                                f"{contractor.get('city', 'N/A')} • {contractor.get('specializations', 'N/A')[:50]}...",
                                size="xs",
                                c="dimmed"
                            ) if contractor.get('specializations') and len(contractor.get('specializations', '')) > 50
                            else dmc.Text(
                                f"{contractor.get('city', 'N/A')} • {contractor.get('specializations', 'N/A')}",
                                size="xs",
                                c="dimmed"
                            )
                        ], gap=0),
                        dmc.Badge(
                            f"🔥 {contractor.get('lead_score', 'N/A')}/10",
                            color="red" if contractor.get('lead_score', 0) >= 9 else "orange",
                            size="lg",
                            variant="filled"
                        )
                    ], justify="space-between", align="center")
                    for contractor in sorted(high_priority, key=lambda x: x.get('lead_score', 0), reverse=True)[:10]
                ], gap="sm") if high_priority else dmc.Alert(
                    "No high-priority contractors yet. Enrich contractors to see top leads here.",
                    color="blue",
                    variant="light",
                    icon=DashIconify(icon="solar:info-circle-bold")
                )
            ], gap="md")
        ], p="lg", withBorder=True, radius="md"),

        # Quick Actions
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:lightning-bold", width=24, color="blue"),
                    dmc.Text("Quick Actions", size="md", fw=600)
                ], gap="sm"),

                dmc.SimpleGrid([
                    dmc.Button(
                        "Discover Contractors",
                        leftSection=DashIconify(icon="solar:magnifer-bold"),
                        variant="light",
                        color="blue",
                        size="md",
                        fullWidth=True,
                        id={"type": "nav-btn", "page": "/discovery"}
                    ),
                    dmc.Button(
                        f"Enrich {pending_count} Pending",
                        leftSection=DashIconify(icon="solar:magic-stick-bold"),
                        variant="light",
                        color="purple",
                        size="md",
                        fullWidth=True,
                        id={"type": "nav-btn", "page": "/enrichment"}
                    ),
                    dmc.Button(
                        "View All Contractors",
                        leftSection=DashIconify(icon="solar:users-group-rounded-bold"),
                        variant="light",
                        color="green",
                        size="md",
                        fullWidth=True,
                        id={"type": "nav-btn", "page": "/contractors"}
                    ),
                ], cols=3, spacing="md")
            ], gap="md")
        ], p="md", withBorder=True, radius="md", style={"background": "linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%)"})
    ], gap="md")

    return metrics, content


@callback(
    Output("dashboard-clients-container", "children"),
    Input("dashboard-refresh-interval", "n_intervals"),
    State("session-store", "data"),
)
def update_clients_dashboard(_, session_data):
    """Load and display clients & POs dashboard"""

    # Get authenticated database instance
    auth_db = get_authenticated_db(session_data)

    try:
        # Get all clients and POs
        clients = auth_db.get_all_po_clients()

        # Count totals
        total_clients = len(clients)

        # Get all POs
        all_pos = []
        for client in clients:
            pos = auth_db.get_purchase_orders_by_client(client['id'])
            all_pos.extend(pos)

        total_pos = len(all_pos)

        # PO status breakdown
        active_pos = len([po for po in all_pos if po.get('status') == 'active'])
        completed_pos = len([po for po in all_pos if po.get('status') == 'completed'])

        # Total PO value
        total_po_value = sum([float(po.get('total_amount', 0) or 0) for po in all_pos])

        # Client type breakdown
        residential = len([c for c in clients if c.get('client_type') == 'residential'])
        contractor = len([c for c in clients if c.get('client_type') == 'contractor'])
        commercial = len([c for c in clients if c.get('client_type') == 'commercial'])

    except Exception as e:
        print(f"ERROR loading clients dashboard: {e}")
        return dmc.Alert(
            "Failed to load client data",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold")
        )

    # Top Metrics Cards
    metrics = dmc.SimpleGrid([
        # Total Clients
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:users-group-rounded-bold", width=32, color="blue"),
                    dmc.Stack([
                        dmc.Text("Total Clients", size="xs", c="dimmed", fw=500),
                        dmc.Text(str(total_clients), size="xl", fw=700, c="blue"),
                    ], gap=0)
                ], justify="space-between"),
                dmc.Text("Active clients", size="xs", c="dimmed")
            ], gap="xs")
        ], p="md", withBorder=True, radius="md"),

        # Total POs
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:document-text-bold", width=32, color="green"),
                    dmc.Stack([
                        dmc.Text("Purchase Orders", size="xs", c="dimmed", fw=500),
                        dmc.Text(str(total_pos), size="xl", fw=700, c="green"),
                    ], gap=0)
                ], justify="space-between"),
                dmc.Group([
                    dmc.Badge(f"{active_pos} Active", color="blue", variant="light", size="sm"),
                    dmc.Badge(f"{completed_pos} Done", color="green", variant="light", size="sm"),
                ], gap="xs")
            ], gap="xs")
        ], p="md", withBorder=True, radius="md"),

        # Total Value
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:dollar-bold", width=32, color="orange"),
                    dmc.Stack([
                        dmc.Text("Total PO Value", size="xs", c="dimmed", fw=500),
                        dmc.Text(f"${total_po_value:,.0f}", size="xl", fw=700, c="orange"),
                    ], gap=0)
                ], justify="space-between"),
                dmc.Text("All purchase orders", size="xs", c="dimmed")
            ], gap="xs")
        ], p="md", withBorder=True, radius="md"),

        # Client Types
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:pie-chart-bold", width=32, color="purple"),
                    dmc.Stack([
                        dmc.Text("Client Types", size="xs", c="dimmed", fw=500),
                        dmc.Text(str(total_clients), size="xl", fw=700, c="purple"),
                    ], gap=0)
                ], justify="space-between"),
                dmc.Group([
                    dmc.Badge(f"{residential} Res", color="blue", variant="light", size="sm"),
                    dmc.Badge(f"{contractor} Con", color="green", variant="light", size="sm"),
                    dmc.Badge(f"{commercial} Com", color="orange", variant="light", size="sm"),
                ], gap="xs")
            ], gap="xs")
        ], p="md", withBorder=True, radius="md"),
    ], cols=4, spacing="md")

    # Recent POs
    recent_pos = sorted(all_pos, key=lambda x: x.get('created_at', ''), reverse=True)[:5]

    content = dmc.Stack([
        # Client Type Distribution
        dmc.Paper([
            dmc.Stack([
                dmc.Text("Client Type Distribution", size="lg", fw=600),
                dmc.SimpleGrid([
                    dmc.Stack([
                        dmc.Group([
                            dmc.ThemeIcon(
                                DashIconify(icon="solar:home-2-bold", width=20),
                                size="lg",
                                radius="md",
                                color="blue",
                                variant="light"
                            ),
                            dmc.Stack([
                                dmc.Text("Residential", size="sm", fw=500),
                                dmc.Text(f"{residential} clients", size="xs", c="dimmed")
                            ], gap=0)
                        ], gap="sm"),
                        dmc.Progress(
                            value=(residential / total_clients * 100) if total_clients > 0 else 0,
                            color="blue",
                            size="md"
                        )
                    ], gap="xs"),

                    dmc.Stack([
                        dmc.Group([
                            dmc.ThemeIcon(
                                DashIconify(icon="solar:hammer-bold", width=20),
                                size="lg",
                                radius="md",
                                color="green",
                                variant="light"
                            ),
                            dmc.Stack([
                                dmc.Text("Contractor", size="sm", fw=500),
                                dmc.Text(f"{contractor} clients", size="xs", c="dimmed")
                            ], gap=0)
                        ], gap="sm"),
                        dmc.Progress(
                            value=(contractor / total_clients * 100) if total_clients > 0 else 0,
                            color="green",
                            size="md"
                        )
                    ], gap="xs"),

                    dmc.Stack([
                        dmc.Group([
                            dmc.ThemeIcon(
                                DashIconify(icon="solar:buildings-2-bold", width=20),
                                size="lg",
                                radius="md",
                                color="orange",
                                variant="light"
                            ),
                            dmc.Stack([
                                dmc.Text("Commercial", size="sm", fw=500),
                                dmc.Text(f"{commercial} clients", size="xs", c="dimmed")
                            ], gap=0)
                        ], gap="sm"),
                        dmc.Progress(
                            value=(commercial / total_clients * 100) if total_clients > 0 else 0,
                            color="orange",
                            size="md"
                        )
                    ], gap="xs"),
                ], cols=3, spacing="lg")
            ], gap="md")
        ], p="lg", withBorder=True, radius="md"),

        # Recent Purchase Orders
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    dmc.Text("Recent Purchase Orders", size="lg", fw=600),
                    dmc.Badge(f"Last {len(recent_pos)}", color="blue", variant="light")
                ], justify="space-between"),

                dmc.Stack([
                    dmc.Paper([
                        dmc.Group([
                            dmc.Stack([
                                dmc.Text(po.get('po_number', 'N/A'), fw=600, size="sm"),
                                dmc.Text(po.get('project_name') or 'No project name', size="xs", c="dimmed")
                            ], gap=2),
                            dmc.Group([
                                dmc.Text(f"${po.get('total_amount', 0):,.2f}" if po.get('total_amount') else "$0.00", fw=600, c="green"),
                                dmc.Badge(
                                    po.get('status', 'active').replace('_', ' ').title(),
                                    color="blue" if po.get('status') == 'active' else "green",
                                    variant="light"
                                )
                            ], gap="sm")
                        ], justify="space-between", align="center")
                    ], p="sm", withBorder=True, radius="sm")
                    for po in recent_pos
                ], gap="sm") if recent_pos else dmc.Alert(
                    "No purchase orders yet. Create your first PO to get started!",
                    color="blue",
                    variant="light",
                    icon=DashIconify(icon="solar:info-circle-bold")
                )
            ], gap="md")
        ], p="lg", withBorder=True, radius="md"),

        # Quick Actions
        dmc.Paper([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:lightning-bold", width=24, color="blue"),
                    dmc.Text("Quick Actions", size="md", fw=600)
                ], gap="sm"),

                dmc.SimpleGrid([
                    dmc.Button(
                        "Manage Clients",
                        leftSection=DashIconify(icon="solar:users-group-rounded-bold"),
                        variant="light",
                        color="blue",
                        size="md",
                        fullWidth=True,
                        id={"type": "nav-btn", "page": "/clients"}
                    ),
                    dmc.Button(
                        "View Purchase Orders",
                        leftSection=DashIconify(icon="solar:document-text-bold"),
                        variant="light",
                        color="green",
                        size="md",
                        fullWidth=True,
                        id={"type": "nav-btn", "page": "/purchase-orders"}
                    ),
                    dmc.Button(
                        "Add New Client",
                        leftSection=DashIconify(icon="solar:add-circle-bold"),
                        variant="light",
                        color="purple",
                        size="md",
                        fullWidth=True,
                        id={"type": "nav-btn", "page": "/clients"}
                    ),
                ], cols=3, spacing="md")
            ], gap="md")
        ], p="md", withBorder=True, radius="md", style={"background": "linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%)"})
    ], gap="md")

    return dmc.Stack([metrics, content], gap="md")
