"""
Enrichment Page
Claude AI website enrichment with bulk processing
"""
import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, ctx, MATCH, ALL
from dash_iconify import DashIconify
from modules.database import Database, get_authenticated_db
from modules.enrichment import ContractorEnrichment
import asyncio

layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Title("Website Enrichment", order=1),
        dmc.Badge("Claude AI", color="purple", variant="light", leftSection=DashIconify(icon="solar:magic-stick-bold"))
    ], justify="space-between"),

    dmc.Text("Analyze contractor websites to extract key information and generate lead scores", c="dimmed", size="sm"),

    dmc.Space(h=10),

    # Explanation section
    dmc.Accordion([
        dmc.AccordionItem([
            dmc.AccordionControl(
                dmc.Group([
                    DashIconify(icon="solar:lightbulb-bold", width=20, color="purple"),
                    dmc.Text("What is Enrichment?", fw=500)
                ], gap="xs"),
            ),
            dmc.AccordionPanel([
                dmc.Stack([
                    dmc.Text(
                        "Enrichment uses Claude AI to analyze contractor websites and extract valuable business intelligence. This process transforms basic contact info into actionable sales insights.",
                        size="sm"
                    ),

                    dmc.Space(h=5),

                    dmc.Text("What Claude AI Analyzes:", fw=600, size="sm"),
                    dmc.List([
                        dmc.ListItem([
                            dmc.Text([
                                dmc.Text("Company Specializations: ", fw=600, span=True),
                                "Kitchen remodeling, bathroom renovation, custom cabinets, etc."
                            ], size="sm")
                        ]),
                        dmc.ListItem([
                            dmc.Text([
                                dmc.Text("Glazing Opportunities: ", fw=600, span=True),
                                "Frameless showers, glass doors, backsplashes, cabinet glass inserts"
                            ], size="sm")
                        ]),
                        dmc.ListItem([
                            dmc.Text([
                                dmc.Text("Subcontractor Usage: ", fw=600, span=True),
                                "Whether they use subcontractors (your potential entry point)"
                            ], size="sm")
                        ]),
                        dmc.ListItem([
                            dmc.Text([
                                dmc.Text("Lead Score (1-10): ", fw=600, span=True),
                                "Quality rating based on fit, project types, and opportunity"
                            ], size="sm")
                        ]),
                        dmc.ListItem([
                            dmc.Text([
                                dmc.Text("Profile Notes: ", fw=600, span=True),
                                "Key insights about their business and ideal projects"
                            ], size="sm")
                        ]),
                        dmc.ListItem([
                            dmc.Text([
                                dmc.Text("Outreach Angle: ", fw=600, span=True),
                                "Personalized approach for your sales conversation"
                            ], size="sm")
                        ]),
                    ], size="sm"),

                    dmc.Space(h=5),

                    dmc.Alert(
                        [
                            dmc.Text("Cost: ~$0.03 per contractor", fw=600, size="sm"),
                            dmc.Text("Time: ~10-15 seconds per contractor", size="xs", c="dimmed"),
                            dmc.Text("Note: Contractors without websites are marked as 'failed' automatically", size="xs", c="dimmed")
                        ],
                        color="purple",
                        variant="light",
                        icon=DashIconify(icon="solar:dollar-bold")
                    )
                ], gap="xs")
            ])
        ], value="explanation")
    ], value="explanation", mb="md"),

    # Stats cards
    html.Div(id="enrichment-stats-container"),

    dmc.Space(h=10),

    # Contractor selection area
    html.Div(id="enrichment-contractors-container"),

    # Store for pending contractors
    dcc.Store(id="enrichment-pending-store"),

    # Store for enrichment progress
    dcc.Store(id="enrichment-progress-store", data={"current": 0, "total": 0, "running": False}),

    # Interval component for progress updates (disabled by default)
    dcc.Interval(id="enrichment-progress-interval", interval=1000, disabled=True, n_intervals=0),

    # Results container
    html.Div(id="enrichment-results-container"),

], gap="md")


# Callback to load initial stats and pending contractors
@callback(
    Output("enrichment-stats-container", "children"),
    Output("enrichment-contractors-container", "children"),
    Output("enrichment-pending-store", "data"),
    Input("enrichment-stats-container", "id"),  # Triggers on page load
    State("session-store", "data"),
)
def load_enrichment_data(_, session_data):
    """Load enrichment statistics and pending contractors"""

    # Get authenticated database
    auth_db = get_authenticated_db(session_data)
    auth_enricher = ContractorEnrichment(db=auth_db)

    # Get pending contractors
    pending_contractors = auth_enricher.get_pending_enrichments(limit=100)

    # Get stats
    try:
        enriched = auth_db.client.table("contractors").select("*", count="exact").eq("enrichment_status", "completed").execute()
        enriched_count = enriched.count if hasattr(enriched, 'count') else len(enriched.data)
    except:
        enriched_count = "N/A"

    try:
        failed = auth_db.client.table("contractors").select("*").eq("enrichment_status", "failed").execute()
        failed_contractors = failed.data if failed.data else []
        failed_count = len(failed_contractors)
    except:
        failed_contractors = []
        failed_count = "N/A"

    # Stats cards with tooltips
    stats = dmc.Stack([
        dmc.Paper([
            dmc.SimpleGrid([
                # Pending contractors
                dmc.Tooltip(
                    label="Contractors that haven't been enriched yet. They have contact info but no AI analysis.",
                    multiline=True,
                    w=300,
                    children=dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:clock-circle-bold", width=24, color="orange"),
                            dmc.Group([
                                dmc.Text("Pending", size="sm", c="dimmed"),
                                DashIconify(icon="solar:info-circle-linear", width=14, color="gray")
                            ], gap=4)
                        ], gap="xs"),
                        dmc.Text(str(len(pending_contractors)), size="xl", fw=700, c="orange"),
                        dmc.Text("Awaiting enrichment", size="xs", c="dimmed")
                    ], gap=4, style={"cursor": "help"})
                ),

                # Successfully enriched
                dmc.Tooltip(
                    label="Contractors successfully analyzed by Claude AI with lead scores, specializations, and outreach angles.",
                    multiline=True,
                    w=300,
                    children=dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:check-circle-bold", width=24, color="green"),
                            dmc.Group([
                                dmc.Text("Enriched", size="sm", c="dimmed"),
                                DashIconify(icon="solar:info-circle-linear", width=14, color="gray")
                            ], gap=4)
                        ], gap="xs"),
                        dmc.Text(str(enriched_count), size="xl", fw=700, c="green"),
                        dmc.Text("Completed successfully", size="xs", c="dimmed")
                    ], gap=4, style={"cursor": "help"})
                ),

                # Failed enrichments
                dmc.Tooltip(
                    label="Enrichment failed - usually due to missing/inaccessible websites. Click to see details below.",
                    multiline=True,
                    w=300,
                    children=dmc.Stack([
                        dmc.Group([
                            DashIconify(icon="solar:close-circle-bold", width=24, color="red"),
                            dmc.Group([
                                dmc.Text("Failed", size="sm", c="dimmed"),
                                DashIconify(icon="solar:info-circle-linear", width=14, color="gray")
                            ], gap=4)
                        ], gap="xs"),
                        dmc.Text(str(failed_count), size="xl", fw=700, c="red"),
                        dmc.Text("Enrichment failed", size="xs", c="dimmed")
                    ], gap=4, style={"cursor": "help"})
                ),
            ], cols=3, spacing="md")
        ], p="md", withBorder=True),

        # Failed contractors accordion (if any)
        dmc.Accordion([
            dmc.AccordionItem([
                dmc.AccordionControl(
                    dmc.Group([
                        DashIconify(icon="solar:danger-triangle-bold", width=20, color="red"),
                        dmc.Text(f"View Failed Enrichments ({failed_count})", fw=500)
                    ], gap="xs"),
                ),
                dmc.AccordionPanel([
                    dmc.Stack([
                        dmc.Alert(
                            "Common failure reasons: No website, website inaccessible, website requires JavaScript, or API error.",
                            color="yellow",
                            variant="light",
                            icon=DashIconify(icon="solar:info-circle-bold")
                        ),
                        dmc.Space(h=5),
                        dmc.Stack([
                            dmc.Group([
                                dmc.Stack([
                                    dmc.Text(contractor['company_name'], fw=500, size="sm"),
                                    dmc.Text(
                                        f"{contractor.get('city', 'N/A')} • {contractor.get('website', 'No website')}",
                                        size="xs",
                                        c="dimmed"
                                    )
                                ], gap=0),
                                dmc.Tooltip(
                                    label=contractor.get('lead_score_reasoning', 'No failure reason recorded. Likely no website or website inaccessible.'),
                                    multiline=True,
                                    w=400,
                                    children=dmc.Badge(
                                        "Why failed?",
                                        color="red",
                                        variant="light",
                                        leftSection=DashIconify(icon="solar:info-circle-linear", width=14),
                                        style={"cursor": "help"}
                                    )
                                )
                            ], justify="space-between", align="center")
                            for contractor in failed_contractors[:20]
                        ], gap="sm") if failed_contractors else dmc.Text("No failed enrichments.", size="sm", c="dimmed"),
                        dmc.Text(
                            f"... and {len(failed_contractors) - 20} more" if len(failed_contractors) > 20 else "",
                            size="xs",
                            c="dimmed",
                            ta="center"
                        ) if len(failed_contractors) > 20 else None
                    ], gap="xs")
                ])
            ], value="failed")
        ], value=None) if failed_count > 0 else None
    ], gap="md")

    # Contractor selection UI
    if pending_contractors:
        contractors_ui = dmc.Stack([
            dmc.Text(f"Contractors Pending Enrichment ({len(pending_contractors)})", size="lg", fw=600),

            dmc.Paper([
                dmc.Stack([
                    dmc.Text("Select contractors to enrich:", fw=500, size="sm"),
                    dmc.RadioGroup(
                        id="enrichment-selection-radio",
                        children=[
                            dmc.Radio(label="Enrich first 5", value="first_5"),
                            dmc.Radio(label="Enrich first 10", value="first_10"),
                            dmc.Radio(label="Enrich all pending", value="all"),
                            dmc.Radio(label="Select specific contractors", value="custom"),
                        ],
                        value="first_5",
                        size="sm"
                    ),

                    # Custom selection area (hidden by default)
                    html.Div(id="enrichment-custom-selection", style={"display": "none"}),

                    # Info about selection
                    html.Div(id="enrichment-selection-info"),

                    # Enrichment button
                    dmc.Button(
                        "Start Enrichment",
                        id="enrichment-start-btn",
                        fullWidth=True,
                        size="lg",
                        leftSection=DashIconify(icon="solar:magic-stick-bold"),
                        color="purple"
                    )
                ], gap="md")
            ], p="md", withBorder=True),

            # Pending contractors accordion
            dmc.Accordion([
                dmc.AccordionItem([
                    dmc.AccordionControl(
                        f"View Pending Contractors ({min(20, len(pending_contractors))} of {len(pending_contractors)})",
                        icon=DashIconify(icon="solar:list-bold", width=20)
                    ),
                    dmc.AccordionPanel([
                        dmc.Stack([
                            dmc.Group([
                                dmc.Text(f"{idx}.", size="sm", c="dimmed", style={"width": "30px"}),
                                dmc.Stack([
                                    dmc.Text(contractor['company_name'], fw=500, size="sm"),
                                    dmc.Text(
                                        f"{contractor.get('city', 'N/A')} • {contractor.get('website', 'No website')}",
                                        size="xs",
                                        c="dimmed"
                                    )
                                ], gap=0)
                            ], gap="xs")
                            for idx, contractor in enumerate(pending_contractors[:20], 1)
                        ], gap="xs"),
                        dmc.Text(
                            f"... and {len(pending_contractors) - 20} more" if len(pending_contractors) > 20 else "",
                            size="xs",
                            c="dimmed",
                            ta="center"
                        ) if len(pending_contractors) > 20 else None
                    ])
                ], value="pending")
            ], value=None)
        ], gap="md")
    else:
        contractors_ui = dmc.Alert(
            "No contractors pending enrichment. Use the Discovery page to add contractors first.",
            title="No Pending Contractors",
            color="blue",
            icon=DashIconify(icon="solar:info-circle-bold")
        )

    return stats, contractors_ui, pending_contractors


# Callback to update selection info and show/hide custom selection
@callback(
    Output("enrichment-selection-info", "children"),
    Output("enrichment-custom-selection", "style"),
    Output("enrichment-custom-selection", "children"),
    Input("enrichment-selection-radio", "value"),
    State("enrichment-pending-store", "data"),
)
def update_selection_info(selection, pending_contractors):
    """Update info about how many contractors will be enriched"""
    if not pending_contractors:
        return None, {"display": "none"}, None

    if selection == "first_5":
        count = min(5, len(pending_contractors))
        return dmc.Alert(
            f"Will enrich {count} contractor(s). Cost: ~${count * 0.03:.2f}",
            color="blue",
            variant="light"
        ), {"display": "none"}, None

    elif selection == "first_10":
        count = min(10, len(pending_contractors))
        return dmc.Alert(
            f"Will enrich {count} contractor(s). Cost: ~${count * 0.03:.2f}",
            color="blue",
            variant="light"
        ), {"display": "none"}, None

    elif selection == "all":
        count = len(pending_contractors)
        return dmc.Alert(
            f"Will enrich ALL {count} contractor(s). This may take several minutes. Cost: ~${count * 0.03:.2f}",
            color="yellow",
            variant="light",
            title="Large Batch"
        ), {"display": "none"}, None

    elif selection == "custom":
        # Show checkboxes for custom selection
        checkboxes = dmc.Stack([
            dmc.Checkbox(
                label=f"{contractor['company_name']} - {contractor.get('city', 'N/A')}",
                id={"type": "enrich-checkbox", "index": contractor['id']},
                size="sm"
            )
            for contractor in pending_contractors[:20]
        ], gap="xs")

        if len(pending_contractors) > 20:
            checkboxes = dmc.Stack([
                checkboxes,
                dmc.Text(f"Showing first 20 of {len(pending_contractors)} contractors", size="xs", c="dimmed")
            ], gap="xs")

        return dmc.Alert(
            "Select contractors below",
            color="blue",
            variant="light"
        ), {"display": "block"}, checkboxes

    return None, {"display": "none"}, None


# Callback to handle enrichment
@callback(
    Output("enrichment-results-container", "children"),
    Output("enrichment-progress-store", "data"),
    Output("enrichment-progress-interval", "disabled"),
    Input("enrichment-start-btn", "n_clicks"),
    State("enrichment-selection-radio", "value"),
    State("enrichment-pending-store", "data"),
    State({"type": "enrich-checkbox", "index": ALL}, "checked"),
    State({"type": "enrich-checkbox", "index": ALL}, "id"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def start_enrichment(n_clicks, selection, pending_contractors, checked_values, checkbox_ids, session_data):
    """Start enrichment process"""
    if not n_clicks or not pending_contractors:
        return dash.no_update, dash.no_update, dash.no_update

    # Get authenticated database
    auth_db = get_authenticated_db(session_data)
    auth_enricher = ContractorEnrichment(db=auth_db)

    # Determine which contractors to enrich
    selected_ids = []

    if selection == "first_5":
        selected_ids = [c['id'] for c in pending_contractors[:5]]
    elif selection == "first_10":
        selected_ids = [c['id'] for c in pending_contractors[:10]]
    elif selection == "all":
        selected_ids = [c['id'] for c in pending_contractors]
    elif selection == "custom":
        # Get checked contractors
        if checked_values and checkbox_ids:
            selected_ids = [checkbox_ids[i]["index"] for i, checked in enumerate(checked_values) if checked]

    if not selected_ids:
        return dmc.Alert(
            "No contractors selected. Please select at least one contractor.",
            title="No Selection",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        ), {"current": 0, "total": 0, "running": False}, True

    # Start enrichment
    results = []
    enriched_count = 0
    failed_count = 0
    total = len(selected_ids)

    progress_ui = [
        dmc.Alert(
            f"Starting enrichment for {total} contractor(s)...",
            title="Enrichment In Progress",
            color="blue",
            icon=DashIconify(icon="solar:magic-stick-bold")
        ),
        dmc.Space(h=10)
    ]

    # Process each contractor
    for idx, contractor_id in enumerate(selected_ids, 1):
        # Get contractor details
        contractor = next((c for c in pending_contractors if c['id'] == contractor_id), None)
        if not contractor:
            continue

        # Enrich contractor
        try:
            result = asyncio.run(auth_enricher.enrich_contractor(contractor_id))

            if result and result.get('success'):
                enriched_count += 1
                results.append(
                    dmc.Alert(
                        f"✅ {contractor['company_name']} - Lead Score: {result.get('lead_score', 'N/A')}/10",
                        color="green",
                        variant="light"
                    )
                )
            else:
                failed_count += 1
                results.append(
                    dmc.Alert(
                        f"❌ {contractor['company_name']} - {result.get('error', 'Unknown error')}",
                        color="red",
                        variant="light"
                    )
                )
        except Exception as e:
            failed_count += 1
            results.append(
                dmc.Alert(
                    f"❌ {contractor['company_name']} - Error: {str(e)}",
                    color="red",
                    variant="light"
                )
            )

    # Build final results UI
    final_ui = [
        dmc.Alert(
            f"Enrichment complete! Successfully enriched {enriched_count} of {total} contractor(s). {failed_count} failed.",
            title="Enrichment Complete",
            color="green" if failed_count == 0 else "yellow",
            icon=DashIconify(icon="solar:check-circle-bold")
        ),
        dmc.Space(h=10),

        dmc.Paper([
            dmc.SimpleGrid([
                dmc.Stack([
                    dmc.Text("Total Processed", size="xs", c="dimmed"),
                    dmc.Text(str(total), size="xl", fw=700),
                ], gap=0, align="center"),

                dmc.Stack([
                    dmc.Text("Successful", size="xs", c="dimmed"),
                    dmc.Text(str(enriched_count), size="xl", fw=700, c="green"),
                ], gap=0, align="center"),

                dmc.Stack([
                    dmc.Text("Failed", size="xs", c="dimmed"),
                    dmc.Text(str(failed_count), size="xl", fw=700, c="red"),
                ], gap=0, align="center"),

                dmc.Stack([
                    dmc.Text("Est. Cost", size="xs", c="dimmed"),
                    dmc.Text(f"${enriched_count * 0.03:.2f}", size="xl", fw=700, c="blue"),
                ], gap=0, align="center"),
            ], cols=4, spacing="md")
        ], p="md", withBorder=True),

        dmc.Space(h=10),

        dmc.Accordion([
            dmc.AccordionItem([
                dmc.AccordionControl("View Detailed Results"),
                dmc.AccordionPanel(dmc.Stack(results, gap="xs"))
            ], value="results")
        ], value="results"),

        dmc.Space(h=10),

        dmc.Button(
            "Refresh Page",
            id="enrichment-refresh-btn",
            variant="light",
            leftSection=DashIconify(icon="solar:refresh-bold"),
            fullWidth=True
        )
    ]

    return dmc.Stack(final_ui, gap="md"), {"current": total, "total": total, "running": False}, True


# Callback to refresh page
@callback(
    Output("enrichment-stats-container", "children", allow_duplicate=True),
    Output("enrichment-contractors-container", "children", allow_duplicate=True),
    Output("enrichment-pending-store", "data", allow_duplicate=True),
    Output("enrichment-results-container", "children", allow_duplicate=True),
    Input("enrichment-refresh-btn", "n_clicks"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def refresh_page(n_clicks, session_data):
    """Refresh the page after enrichment"""
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Get authenticated database
    auth_db = get_authenticated_db(session_data)
    auth_enricher = ContractorEnrichment(db=auth_db)

    # Reload data (same as initial load)
    pending_contractors = auth_enricher.get_pending_enrichments(limit=100)

    try:
        enriched = auth_db.client.table("contractors").select("*", count="exact").eq("enrichment_status", "completed").execute()
        enriched_count = enriched.count if hasattr(enriched, 'count') else len(enriched.data)
    except:
        enriched_count = "N/A"

    try:
        failed = auth_db.client.table("contractors").select("*", count="exact").eq("enrichment_status", "failed").execute()
        failed_count = failed.count if hasattr(failed, 'count') else len(failed.data)
    except:
        failed_count = "N/A"

    stats = dmc.Paper([
        dmc.SimpleGrid([
            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:clock-circle-bold", width=24, color="orange"),
                    dmc.Text("Pending", size="sm", c="dimmed")
                ], gap="xs"),
                dmc.Text(str(len(pending_contractors)), size="xl", fw=700, c="orange"),
                dmc.Text("Awaiting enrichment", size="xs", c="dimmed")
            ], gap=4),

            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:check-circle-bold", width=24, color="green"),
                    dmc.Text("Enriched", size="sm", c="dimmed")
                ], gap="xs"),
                dmc.Text(str(enriched_count), size="xl", fw=700, c="green"),
                dmc.Text("Completed successfully", size="xs", c="dimmed")
            ], gap=4),

            dmc.Stack([
                dmc.Group([
                    DashIconify(icon="solar:close-circle-bold", width=24, color="red"),
                    dmc.Text("Failed", size="sm", c="dimmed")
                ], gap="xs"),
                dmc.Text(str(failed_count), size="xl", fw=700, c="red"),
                dmc.Text("Enrichment failed", size="xs", c="dimmed")
            ], gap=4),
        ], cols=3, spacing="md")
    ], p="md", withBorder=True)

    if pending_contractors:
        contractors_ui = dmc.Stack([
            dmc.Text(f"Contractors Pending Enrichment ({len(pending_contractors)})", size="lg", fw=600),
            dmc.Alert(
                "Page refreshed. Select contractors to enrich.",
                color="green",
                variant="light",
                icon=DashIconify(icon="solar:check-circle-bold")
            )
        ], gap="md")
    else:
        contractors_ui = dmc.Alert(
            "No contractors pending enrichment. Great job!",
            title="All Caught Up",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold")
        )

    return stats, contractors_ui, pending_contractors, None
