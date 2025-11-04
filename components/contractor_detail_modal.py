"""
Contractor Detail Modal Component
Full contractor details in a modal with tabbed sections
"""
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from components.outreach_display import create_outreach_tab, create_activity_tab


def create_detail_modal(contractor, outreach_materials=None, interactions=None, is_open=True, active_tab="contact"):
    """
    Create detail modal for a contractor

    Args:
        contractor: Dict with contractor data
        outreach_materials: Dict with emails and scripts (optional)
        is_open: Boolean to control modal visibility

    Returns:
        dmc.Modal component
    """
    if not contractor:
        return dmc.Modal(opened=False, id="contractor-detail-modal")

    company_name = contractor.get('company_name', 'Unknown')
    lead_score = contractor.get('lead_score')
    contractor_id = contractor.get('id')

    # Contact Info Tab
    contact_tab = dmc.Stack([
        dmc.Grid([
            dmc.GridCol([
                dmc.Text("Contact Person", size="sm", fw=500, c="dimmed"),
                dmc.Text(contractor.get('contact_person') or 'N/A', size="md")
            ], span=6),
            dmc.GridCol([
                dmc.Text("Phone", size="sm", fw=500, c="dimmed"),
                dmc.Group([
                    dmc.Text(contractor.get('phone') or 'N/A', size="md"),
                    dmc.ActionIcon(
                        DashIconify(icon="solar:copy-bold", width=16),
                        size="sm",
                        variant="subtle",
                        id={'type': 'copy-phone-btn', 'index': contractor_id}
                    ) if contractor.get('phone') else None
                ], gap=10)
            ], span=6),
        ]),

        dmc.Space(h=15),

        dmc.Grid([
            dmc.GridCol([
                dmc.Text("Email", size="sm", fw=500, c="dimmed"),
                dmc.Group([
                    dmc.Text(contractor.get('email') or 'N/A', size="md"),
                    dmc.ActionIcon(
                        DashIconify(icon="solar:copy-bold", width=16),
                        size="sm",
                        variant="subtle",
                        id={'type': 'copy-email-btn', 'index': contractor_id}
                    ) if contractor.get('email') else None
                ], gap=10)
            ], span=6),
            dmc.GridCol([
                dmc.Text("Website", size="sm", fw=500, c="dimmed"),
                dmc.Anchor(
                    contractor.get('website') or 'N/A',
                    href=contractor.get('website'),
                    target="_blank",
                    size="md"
                ) if contractor.get('website') and contractor.get('website') != 'N/A' else dmc.Text('N/A', size="md")
            ], span=6),
        ]),

        dmc.Space(h=15),

        dmc.Grid([
            dmc.GridCol([
                dmc.Text("Address", size="sm", fw=500, c="dimmed"),
                dmc.Text(contractor.get('address') or 'N/A', size="md")
            ], span=12),
        ]),

        dmc.Space(h=15),

        dmc.Grid([
            dmc.GridCol([
                dmc.Text("City", size="sm", fw=500, c="dimmed"),
                dmc.Text(f"{contractor.get('city', 'N/A')}, {contractor.get('state', 'FL')} {contractor.get('zip', '')}", size="md")
            ], span=6),
            dmc.GridCol([
                dmc.Text("Source", size="sm", fw=500, c="dimmed"),
                dmc.Text(contractor.get('source', 'N/A'), size="md")
            ], span=6),
        ]),
    ], gap="lg")

    # Profile Tab
    profile_tab = dmc.Stack([
        dmc.Grid([
            dmc.GridCol([
                dmc.Text("Company Type", size="sm", fw=500, c="dimmed"),
                dmc.Badge(
                    (contractor.get('company_type') or 'N/A').title(),
                    color="blue",
                    variant="light",
                    size="lg"
                )
            ], span=6),
            dmc.GridCol([
                dmc.Text("Enrichment Status", size="sm", fw=500, c="dimmed"),
                dmc.Badge(
                    (contractor.get('enrichment_status') or 'pending').title(),
                    color={'completed': 'green', 'pending': 'yellow', 'failed': 'red'}.get(
                        contractor.get('enrichment_status'), 'gray'
                    ),
                    variant="light",
                    size="lg"
                )
            ], span=6),
        ]),

        dmc.Space(h=15),

        dmc.Text("Specializations", size="sm", fw=500, c="dimmed"),
        dmc.Text(contractor.get('specializations') or 'N/A', size="sm"),

        dmc.Space(h=15),

        dmc.Text("Glazing Opportunities", size="sm", fw=500, c="dimmed"),
        dmc.Text(contractor.get('glazing_opportunity_types') or 'N/A', size="sm"),

        dmc.Space(h=15),

        dmc.Text("Subcontractor Usage", size="sm", fw=500, c="dimmed"),
        dmc.Text((contractor.get('uses_subcontractors') or 'unknown').title(), size="sm"),

        dmc.Space(h=15),

        dmc.Accordion(
            children=[
                dmc.AccordionItem([
                    dmc.AccordionControl("Profile Notes"),
                    dmc.AccordionPanel(
                        dmc.Text(contractor.get('profile_notes') or 'No notes available', size="sm")
                    )
                ], value="notes"),
                dmc.AccordionItem([
                    dmc.AccordionControl("Outreach Angle"),
                    dmc.AccordionPanel(
                        dmc.Text(contractor.get('outreach_angle') or 'No outreach angle', size="sm")
                    )
                ], value="outreach"),
            ]
        )
    ], gap="md")

    # Outreach Tab - use helper function
    outreach_tab = create_outreach_tab(contractor_id, outreach_materials)

    # Activity Tab - use helper function
    activity_tab = create_activity_tab(contractor_id, interactions)

    return dmc.Modal(
        id="contractor-detail-modal",
        opened=is_open,
        size="xl",
        title=dmc.Group([
            dmc.Text(company_name, size="xl", fw=700),
            dmc.Badge(
                f"Score: {lead_score}/10" if lead_score else "Not Scored",
                color="green" if lead_score and lead_score >= 8 else "blue",
                size="lg",
                variant="filled"
            )
        ], justify="space-between"),
        children=[
            html.Div([
                dmc.LoadingOverlay(
                    id={'type': 'outreach-loading-overlay', 'index': contractor_id},
                    visible=False,
                    overlayProps={"radius": "sm", "blur": 2},
                    loaderProps={"color": "blue", "type": "dots"}
                ),
                dmc.Tabs(
                    id={'type': 'contractor-tabs', 'index': contractor_id},
                    value=active_tab,
                    children=[
                        dmc.TabsList([
                            dmc.TabsTab("Contact Info", value="contact", leftSection=DashIconify(icon="solar:user-bold", width=18)),
                            dmc.TabsTab("Profile", value="profile", leftSection=DashIconify(icon="solar:document-text-bold", width=18)),
                            dmc.TabsTab("Outreach", value="outreach", leftSection=DashIconify(icon="solar:letter-bold", width=18)),
                            dmc.TabsTab("Activity", value="activity", leftSection=DashIconify(icon="solar:clock-circle-bold", width=18)),
                        ]),

                        dmc.TabsPanel(contact_tab, value="contact", pt="md"),
                        dmc.TabsPanel(profile_tab, value="profile", pt="md"),
                        dmc.TabsPanel(outreach_tab, value="outreach", pt="md"),
                        dmc.TabsPanel(activity_tab, value="activity", pt="md"),
                    ]
                ),

                dmc.Space(h=20),

                # Outreach quantity controls
                dmc.Paper([
                    dmc.Text("Outreach Generation Options", size="sm", fw=500, mb=10),
                    dmc.Grid([
                        dmc.GridCol([
                            dmc.Text("Number of Emails:", size="sm", c="dimmed", mb=5),
                            dmc.SegmentedControl(
                                id={'type': 'email-quantity', 'index': contractor_id},
                                value="3",
                                data=[
                                    {"label": "1", "value": "1"},
                                    {"label": "2", "value": "2"},
                                    {"label": "3", "value": "3"},
                                ],
                                size="sm"
                            )
                        ], span=6),
                        dmc.GridCol([
                            dmc.Text("Number of Call Scripts:", size="sm", c="dimmed", mb=5),
                            dmc.SegmentedControl(
                                id={'type': 'script-quantity', 'index': contractor_id},
                                value="2",
                                data=[
                                    {"label": "1", "value": "1"},
                                    {"label": "2", "value": "2"},
                                ],
                                size="sm"
                            )
                        ], span=6),
                    ])
                ], p="md", withBorder=True, mb=15),

                # Action buttons at bottom
                dmc.Group([
                    dmc.Button(
                        "Generate Outreach",
                        leftSection=DashIconify(icon="solar:magic-stick-bold", width=18),
                        color="blue",
                        variant="filled",
                        id={'type': 'generate-outreach-btn', 'index': contractor_id},
                        loading=False
                    ),
                ], justify="flex-end")
            ], style={"position": "relative"})
        ]
    )
