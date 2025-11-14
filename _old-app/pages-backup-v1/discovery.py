"""
Discovery Page
Google Places contractor discovery with search and save functionality
"""
import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc, ctx
from dash_iconify import DashIconify
from modules.database import Database
from modules.scraper import run_scraper

# Initialize database
db = Database()

# Quick search templates
SEARCH_TEMPLATES = [
    "bathroom remodeling Jacksonville FL",
    "kitchen renovation Jacksonville FL",
    "custom home builder Jacksonville FL",
    "general contractor Jacksonville FL"
]

layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Title("Contractor Discovery", order=1),
        dmc.Badge("Google Places API", color="blue", variant="light", leftSection=DashIconify(icon="solar:magnifer-bold"))
    ], justify="space-between"),

    dmc.Text("Search for contractors on Google Maps and save them to your database", c="dimmed", size="sm"),

    dmc.Space(h=10),

    # Search Form
    dmc.Paper([
        dmc.Stack([
            # Search input and max results
            dmc.Grid([
                dmc.GridCol([
                    dmc.TextInput(
                        id="discovery-search-input",
                        label="Search Query",
                        placeholder="e.g., bathroom remodeling Jacksonville FL",
                        value="bathroom remodeling Jacksonville FL",
                        leftSection=DashIconify(icon="solar:magnifer-linear"),
                        size="md",
                        description="Enter a search term as you would search on Google Maps"
                    )
                ], span=9),

                dmc.GridCol([
                    dmc.NumberInput(
                        id="discovery-max-results",
                        label="Max Results",
                        value=20,
                        min=5,
                        max=60,
                        step=5,
                        size="md",
                        description="Maximum results (up to 60 with pagination)"
                    )
                ], span=3),
            ]),

            # Quick search templates
            dmc.Stack([
                dmc.Text("Quick Search Templates:", size="sm", fw=500),
                dmc.Group([
                    dmc.Button(
                        template,
                        id={"type": "template-btn", "index": idx},
                        variant="light",
                        size="sm",
                        leftSection=DashIconify(icon="solar:magnifer-linear", width=16)
                    ) for idx, template in enumerate(SEARCH_TEMPLATES)
                ], gap="xs")
            ], gap="xs"),

            # Search button
            dmc.Button(
                "Search for Contractors",
                id="discovery-search-btn",
                fullWidth=True,
                size="lg",
                leftSection=DashIconify(icon="solar:magnifer-bold"),
                color="blue"
            )
        ], gap="md")
    ], p="md", withBorder=True),

    dmc.Space(h=10),

    # Store for search results
    dcc.Store(id="discovery-results-store"),

    # Loading and results area
    dcc.Loading(
        id="discovery-loading",
        type="default",
        children=html.Div(id="discovery-results-container")
    ),

    dmc.Space(h=10),

    # Tips section
    dmc.Accordion([
        dmc.AccordionItem([
            dmc.AccordionControl(
                "Tips for Better Results",
                icon=DashIconify(icon="solar:lightbulb-bold", width=20, color="orange")
            ),
            dmc.AccordionPanel([
                dmc.Stack([
                    dmc.Stack([
                        dmc.Text("Search Strategy:", fw=600, size="sm"),
                        dmc.List([
                            dmc.ListItem("Include location (city + state) in your search"),
                            dmc.ListItem('Use specific trade terms: "bathroom remodeling", "kitchen renovation"'),
                            dmc.ListItem('Try different variations: "general contractor", "home builder"')
                        ], size="sm")
                    ], gap="xs"),

                    dmc.Stack([
                        dmc.Text("Pagination & Duplicates:", fw=600, size="sm"),
                        dmc.List([
                            dmc.ListItem("The system fetches up to 60 results (3 pages) from Google Places"),
                            dmc.ListItem("Duplicates are automatically filtered - only NEW contractors are shown"),
                            dmc.ListItem("If all results are duplicates, try varying your search query")
                        ], size="sm")
                    ], gap="xs"),

                    dmc.Stack([
                        dmc.Text("Best Practices:", fw=600, size="sm"),
                        dmc.List([
                            dmc.ListItem("Each search respects Google's rate limits (2s delay between pages)"),
                            dmc.ListItem("Contractors are saved with phone, website, ratings, and review counts"),
                            dmc.ListItem("Cost: ~$0.003 per contractor found (included in search cost)")
                        ], size="sm")
                    ], gap="xs")
                ], gap="md")
            ])
        ], value="tips")
    ], value=None)

], gap="md")


# Callback to handle template button clicks
@callback(
    Output("discovery-search-input", "value"),
    Input({"type": "template-btn", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def update_search_from_template(n_clicks):
    """Update search input when template button is clicked"""
    if not any(n_clicks):
        return dash.no_update

    # Get which button was clicked
    button_id = ctx.triggered_id
    if button_id:
        idx = button_id["index"]
        return SEARCH_TEMPLATES[idx]

    return dash.no_update


# Callback to handle search
@callback(
    Output("discovery-results-container", "children"),
    Output("discovery-results-store", "data"),
    Input("discovery-search-btn", "n_clicks"),
    State("discovery-search-input", "value"),
    State("discovery-max-results", "value"),
    prevent_initial_call=True
)
def search_contractors(n_clicks, search_query, max_results):
    """Search for contractors using Google Places API"""
    if not n_clicks or not search_query:
        return None, None

    try:
        # Run the scraper
        results = run_scraper(search_query, max_results, db)

        # Build results UI
        components = []

        # Success message
        if results['duplicates'] > 0:
            components.append(
                dmc.Alert(
                    f"Found {results['duplicates']} duplicate(s) already in database - showing only NEW contractors below",
                    title="Duplicates Filtered",
                    color="blue",
                    icon=DashIconify(icon="solar:info-circle-bold")
                )
            )

        # Metrics with tooltips
        components.append(
            dmc.Paper([
                dmc.SimpleGrid([
                    dmc.Tooltip(
                        label="Total contractors returned from Google Places API search",
                        children=dmc.Stack([
                            dmc.Group([
                                dmc.Text("Total Found", size="xs", c="dimmed"),
                                DashIconify(icon="solar:info-circle-linear", width=12, color="gray")
                            ], gap=4, justify="center"),
                            dmc.Text(str(results['total_found']), size="xl", fw=700),
                            dmc.Text("From Google Places", size="xs", c="dimmed")
                        ], gap=0, align="center", style={"cursor": "help"})
                    ),

                    dmc.Tooltip(
                        label="New contractors that weren't already in your database. These were added.",
                        children=dmc.Stack([
                            dmc.Group([
                                dmc.Text("New Contractors", size="xs", c="dimmed"),
                                DashIconify(icon="solar:info-circle-linear", width=12, color="gray")
                            ], gap=4, justify="center"),
                            dmc.Text(str(len(results['contractors'])), size="xl", fw=700, c="green"),
                            dmc.Text("Not duplicates", size="xs", c="dimmed")
                        ], gap=0, align="center", style={"cursor": "help"})
                    ),

                    dmc.Tooltip(
                        label="Number of new contractors successfully saved to your Supabase database",
                        children=dmc.Stack([
                            dmc.Group([
                                dmc.Text("Saved", size="xs", c="dimmed"),
                                DashIconify(icon="solar:info-circle-linear", width=12, color="gray")
                            ], gap=4, justify="center"),
                            dmc.Text(str(results['saved']), size="xl", fw=700, c="blue"),
                            dmc.Text("To database", size="xs", c="dimmed")
                        ], gap=0, align="center", style={"cursor": "help"})
                    ),

                    dmc.Tooltip(
                        label="Contractors already in your database (matched by phone number or company name). These were automatically skipped.",
                        multiline=True,
                        w=300,
                        children=dmc.Stack([
                            dmc.Group([
                                dmc.Text("Duplicates Skipped", size="xs", c="dimmed"),
                                DashIconify(icon="solar:info-circle-linear", width=12, color="gray")
                            ], gap=4, justify="center"),
                            dmc.Text(str(results['duplicates']), size="xl", fw=700, c="gray"),
                            dmc.Text("Already in DB", size="xs", c="dimmed")
                        ], gap=0, align="center", style={"cursor": "help"})
                    ),
                ], cols=4, spacing="md")
            ], p="md", withBorder=True)
        )

        components.append(dmc.Space(h=10))

        # Show discovered contractors
        if results['contractors']:
            components.append(
                dmc.Text(f"{len(results['contractors'])} New Contractor(s)", size="lg", fw=600)
            )

            if results['duplicates'] > 0:
                components.append(
                    dmc.Text(
                        f"Showing only new contractors • {results['duplicates']} duplicates were automatically skipped",
                        size="sm",
                        c="dimmed"
                    )
                )

            components.append(dmc.Space(h=10))

            # Contractor cards
            for idx, contractor in enumerate(results['contractors'], 1):
                components.append(
                    dmc.Accordion([
                        dmc.AccordionItem([
                            dmc.AccordionControl(
                                dmc.Group([
                                    dmc.Text(f"{idx}. {contractor.get('company_name', 'Unknown')}", fw=500),
                                    dmc.Group([
                                        dmc.Badge(
                                            f"⭐ {contractor.get('google_rating', 'N/A')}",
                                            color="yellow",
                                            variant="light"
                                        ),
                                        dmc.Text(
                                            f"{contractor.get('review_count', 0)} reviews",
                                            size="sm",
                                            c="dimmed"
                                        )
                                    ], gap="xs")
                                ], justify="space-between")
                            ),
                            dmc.AccordionPanel([
                                dmc.Grid([
                                    dmc.GridCol([
                                        dmc.Stack([
                                            dmc.Group([
                                                DashIconify(icon="solar:phone-bold", width=16),
                                                dmc.Text("Phone:", fw=600, size="sm")
                                            ], gap="xs"),
                                            dmc.Text(contractor.get('phone', 'N/A'), size="sm"),

                                            dmc.Group([
                                                DashIconify(icon="solar:map-point-bold", width=16),
                                                dmc.Text("Address:", fw=600, size="sm")
                                            ], gap="xs"),
                                            dmc.Text(contractor.get('address', 'N/A'), size="sm"),

                                            dmc.Group([
                                                DashIconify(icon="solar:city-bold", width=16),
                                                dmc.Text("City:", fw=600, size="sm")
                                            ], gap="xs"),
                                            dmc.Text(contractor.get('city', 'N/A'), size="sm"),
                                        ], gap="xs")
                                    ], span=6),

                                    dmc.GridCol([
                                        dmc.Stack([
                                            dmc.Group([
                                                DashIconify(icon="solar:star-bold", width=16),
                                                dmc.Text("Rating:", fw=600, size="sm")
                                            ], gap="xs"),
                                            dmc.Text(
                                                f"{contractor.get('google_rating', 'N/A')} ({contractor.get('review_count', 0)} reviews)",
                                                size="sm"
                                            ),

                                            dmc.Group([
                                                DashIconify(icon="solar:global-bold", width=16),
                                                dmc.Text("Website:", fw=600, size="sm")
                                            ], gap="xs"),
                                            dmc.Text(contractor.get('website', 'N/A'), size="sm"),

                                            dmc.Group([
                                                DashIconify(icon="solar:database-bold", width=16),
                                                dmc.Text("Source:", fw=600, size="sm")
                                            ], gap="xs"),
                                            dmc.Text("Google Places API", size="sm"),
                                        ], gap="xs")
                                    ], span=6),
                                ])
                            ])
                        ], value=f"contractor-{idx}")
                    ], value=None)
                )

        elif results['duplicates'] > 0:
            components.append(
                dmc.Alert(
                    f"All {results['duplicates']} result(s) were duplicates! Try a different search or increase max results.",
                    title="All Duplicates",
                    color="yellow",
                    icon=DashIconify(icon="solar:danger-triangle-bold")
                )
            )
        else:
            components.append(
                dmc.Alert(
                    "No contractors found. Try a different search query.",
                    title="No Results",
                    color="red",
                    icon=DashIconify(icon="solar:close-circle-bold")
                )
            )

        return dmc.Stack(components, gap="md"), results

    except Exception as e:
        return dmc.Alert(
            f"Error during search: {str(e)}",
            title="Search Error",
            color="red",
            icon=DashIconify(icon="solar:danger-bold")
        ), None
