# Dash Mantine Migration Plan
## Island Glass Leads CRM - Streamlit to Dash Migration

**Created:** October 23, 2025
**Target Framework:** Dash + Dash Mantine Components
**Estimated Effort:** 30-40 hours
**Team Size:** Up to 4 sales users
**Priority:** High (Production CRM)

---

## Executive Summary

**Why Migrate:**
- Current Streamlit UX feels fragmented and dated
- Directory and Detail pages should be unified
- Need modern card-based layout with proper modals/drawers
- Multi-user scalability (4 users)
- This will be THE CRM indefinitely - worth doing right

**What We're Building:**
- Modern CRM with card-based contractor directory
- Inline/modal detail views (no separate pages)
- Professional UX comparable to HubSpot/Notion
- Proper component library (Dash Mantine)
- Better performance with callback-based architecture

**Migration Strategy:**
- Phase 1: Infrastructure & Core Layout (6-8 hours)
- Phase 2: Contractor Directory with Cards (8-10 hours)
- Phase 3: Detail View & Outreach (6-8 hours)
- Phase 4: Discovery & Enrichment (6-8 hours)
- Phase 5: Polish & Testing (4-6 hours)

---

## Current State Analysis

### Existing Streamlit Application

**File Structure:**
```
islandGlassLeads/
├── app.py (1,400 lines - main Streamlit app)
├── modules/
│   ├── database.py (Supabase operations)
│   ├── scraper.py (Google Places API)
│   ├── enrichment.py (Claude AI enrichment)
│   └── outreach.py (Email/script generation)
├── styles/
│   └── crm_theme.css (500+ lines custom CSS)
├── .streamlit/
│   └── config.toml
├── supabase_schema.sql
└── requirements.txt
```

**Current Pages (8 total):**
1. Dashboard - Metrics and stats
2. Contractor Discovery - Google Places search
3. Website Enrichment - Claude AI analysis
4. **Contractor Directory** - Searchable list (MERGE TARGET)
5. **Contractor Detail** - Full profile view (MERGE TARGET)
6. Bulk Actions - CSV export, bulk operations
7. Add/Import Contractors - Manual entry, CSV import
8. Settings - API usage tracking

**Key Integrations:**
- ✅ Supabase (PostgreSQL with RLS enabled)
- ✅ Anthropic Claude API (website enrichment, outreach)
- ✅ Google Places API (contractor discovery)
- ✅ Async operations (enrichment)
- ✅ CSV import/export (pandas)

**Database Tables (5):**
- `contractors` - Main contractor data
- `outreach_materials` - Email templates & call scripts
- `interaction_log` - Sales activity tracking
- `app_settings` - Configuration
- `api_usage` - Claude API cost tracking

**Environment Variables:**
```
ANTHROPIC_API_KEY
SUPABASE_URL
SUPABASE_KEY (anon key)
GOOGLE_PLACES_API_KEY
```

---

## Phase 1: Infrastructure & Core Layout (6-8 hours)

### Goals
- Set up Dash project structure
- Install Dash Mantine Components
- Migrate database module (no changes needed)
- Build basic layout with navigation
- Set up routing/page structure

### Tasks

#### 1.1 Project Setup (1 hour)

**New Dependencies:**
```txt
# Add to requirements.txt
dash==2.17.1
dash-mantine-components==0.14.3
dash-iconify==0.1.2
```

**New File Structure:**
```
islandGlassLeads/
├── dash_app.py (NEW - main Dash app)
├── app.py (KEEP for now - parallel development)
├── modules/
│   ├── database.py (NO CHANGES - reuse as-is)
│   ├── scraper.py (NO CHANGES - reuse as-is)
│   ├── enrichment.py (NO CHANGES - reuse as-is)
│   └── outreach.py (NO CHANGES - reuse as-is)
├── pages/ (NEW - Dash pages)
│   ├── __init__.py
│   ├── dashboard.py
│   ├── contractors.py (MAIN PAGE - Directory + Detail merged)
│   ├── discovery.py
│   ├── enrichment.py
│   ├── bulk_actions.py
│   ├── import_contractors.py
│   └── settings.py
├── components/ (NEW - Reusable Dash components)
│   ├── __init__.py
│   ├── contractor_card.py
│   ├── contractor_detail_modal.py
│   ├── navbar.py
│   └── filters.py
├── assets/ (NEW - CSS/JS for Dash)
│   └── custom.css
└── requirements.txt (UPDATED)
```

#### 1.2 Basic Dash App Shell (2 hours)

**`dash_app.py` - Main Application:**
```python
"""
Island Glass Leads - Dash CRM Application
Main entry point
"""
import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from modules.database import Database
import os

# Initialize database
db = Database()

# Initialize Dash app
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    title="Island Glass Leads CRM"
)

server = app.server  # For deployment

# App layout
app.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "light",
        "primaryColor": "blue",
        "fontFamily": "Inter, sans-serif",
    },
    children=[
        dcc.Location(id='url', refresh=False),

        # Main shell with navbar
        dmc.AppShell(
            navbar={
                "width": 250,
                "breakpoint": "sm",
            },
            padding="md",
            children=[
                # Navbar
                dmc.Navbar(
                    width={"base": 250},
                    padding="md",
                    children=[
                        dmc.Stack(
                            spacing="xs",
                            children=[
                                # Logo/Title
                                dmc.Text(
                                    "Island Glass Leads",
                                    size="xl",
                                    weight=700,
                                    color="blue"
                                ),
                                dmc.Text(
                                    "CRM System",
                                    size="sm",
                                    color="dimmed"
                                ),
                                dmc.Divider(),

                                # Navigation links
                                dmc.NavLink(
                                    label="Dashboard",
                                    icon=DashIconify(icon="solar:home-2-bold"),
                                    href="/",
                                ),
                                dmc.NavLink(
                                    label="Contractors",
                                    icon=DashIconify(icon="solar:users-group-rounded-bold"),
                                    href="/contractors",
                                ),
                                dmc.NavLink(
                                    label="Discovery",
                                    icon=DashIconify(icon="solar:magnifer-bold"),
                                    href="/discovery",
                                ),
                                dmc.NavLink(
                                    label="Enrichment",
                                    icon=DashIconify(icon="solar:magic-stick-bold"),
                                    href="/enrichment",
                                ),
                                dmc.NavLink(
                                    label="Bulk Actions",
                                    icon=DashIconify(icon="solar:download-minimalistic-bold"),
                                    href="/bulk-actions",
                                ),
                                dmc.NavLink(
                                    label="Import",
                                    icon=DashIconify(icon="solar:upload-minimalistic-bold"),
                                    href="/import",
                                ),
                                dmc.NavLink(
                                    label="Settings",
                                    icon=DashIconify(icon="solar:settings-bold"),
                                    href="/settings",
                                ),
                            ]
                        )
                    ]
                ),

                # Main content area
                dmc.Container(
                    id='page-content',
                    size="xl",
                    style={"paddingTop": 20}
                )
            ]
        )
    ]
)

# Routing callback
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/':
        from pages import dashboard
        return dashboard.layout
    elif pathname == '/contractors':
        from pages import contractors
        return contractors.layout
    elif pathname == '/discovery':
        from pages import discovery
        return discovery.layout
    elif pathname == '/enrichment':
        from pages import enrichment
        return enrichment.layout
    elif pathname == '/bulk-actions':
        from pages import bulk_actions
        return bulk_actions.layout
    elif pathname == '/import':
        from pages import import_contractors
        return import_contractors.layout
    elif pathname == '/settings':
        from pages import settings
        return settings.layout
    else:
        return dmc.Text("404 - Page not found", color="red", size="xl")

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
```

#### 1.3 Create Page Stubs (1 hour)

**`pages/__init__.py`:**
```python
# Empty init file
```

**`pages/dashboard.py` - Placeholder:**
```python
import dash_mantine_components as dmc
from dash import html

layout = dmc.Stack([
    dmc.Title("Dashboard", order=1),
    dmc.Text("Coming in Phase 1")
])
```

Create similar stubs for:
- `contractors.py` (will be main focus in Phase 2)
- `discovery.py`
- `enrichment.py`
- `bulk_actions.py`
- `import_contractors.py`
- `settings.py`

#### 1.4 Testing Infrastructure (2 hours)

**Test Checklist:**
- ✅ Dash app runs on port 8050
- ✅ All navigation links work
- ✅ Database connection works (test with `db.get_all_contractors()`)
- ✅ Routing displays correct page stubs
- ✅ Mantine theme loads correctly
- ✅ Icons display properly

**Run Commands:**
```bash
# Install new dependencies
pip install dash dash-mantine-components dash-iconify

# Run new Dash app (parallel to Streamlit)
python dash_app.py

# Old Streamlit still works on port 8501
streamlit run app.py
```

---

## Phase 2: Contractor Directory with Cards (8-10 hours)

### Goals
- Build card-based contractor grid
- Add search and filters
- Implement card click → detail modal
- Replace old Directory + Detail pages

### Tasks

#### 2.1 Contractor Card Component (2 hours)

**`components/contractor_card.py`:**
```python
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

def create_contractor_card(contractor):
    """
    Create a single contractor card

    Args:
        contractor: Dict with contractor data from database

    Returns:
        dmc.Card component
    """
    contractor_id = contractor['id']
    company_name = contractor.get('company_name', 'Unknown')
    city = contractor.get('city', 'Unknown')
    state = contractor.get('state', 'FL')
    lead_score = contractor.get('lead_score')
    phone = contractor.get('phone', 'N/A')
    website = contractor.get('website', 'N/A')
    specializations = contractor.get('specializations', 'N/A')

    # Score badge color
    if lead_score:
        if lead_score >= 8:
            score_color = "green"
        elif lead_score >= 6:
            score_color = "blue"
        else:
            score_color = "orange"
    else:
        score_color = "gray"

    # Enrichment status badge
    status = contractor.get('enrichment_status', 'pending')
    status_colors = {
        'completed': 'green',
        'pending': 'yellow',
        'failed': 'red'
    }

    return dmc.Card(
        id={'type': 'contractor-card', 'index': contractor_id},
        children=[
            dmc.CardSection(
                dmc.Group([
                    dmc.Text(company_name, weight=700, size="lg"),
                    dmc.Badge(
                        f"{lead_score}/10" if lead_score else "Not Scored",
                        color=score_color,
                        variant="filled"
                    )
                ], position="apart")
            ),

            dmc.Space(h=10),

            # Location
            dmc.Group([
                DashIconify(icon="solar:map-point-bold", width=16),
                dmc.Text(f"{city}, {state}", size="sm", color="dimmed")
            ], spacing="xs"),

            dmc.Space(h=10),

            # Specializations
            dmc.Text(
                specializations[:60] + "..." if len(specializations) > 60 else specializations,
                size="sm",
                color="dimmed"
            ),

            dmc.Divider(style={"marginTop": 10, "marginBottom": 10}),

            # Contact info
            dmc.Group([
                DashIconify(icon="solar:phone-bold", width=16),
                dmc.Text(phone, size="sm")
            ], spacing="xs"),

            dmc.Group([
                DashIconify(icon="solar:global-bold", width=16),
                dmc.Anchor(
                    website[:30] + "..." if len(website) > 30 else website,
                    href=website if website != 'N/A' else None,
                    target="_blank",
                    size="sm"
                )
            ], spacing="xs"),

            dmc.Space(h=10),

            # Status badge
            dmc.Badge(
                status.title(),
                color=status_colors.get(status, 'gray'),
                variant="light",
                size="sm"
            ),

            dmc.Space(h=15),

            # Action buttons
            dmc.Group([
                dmc.Button(
                    "View Details",
                    id={'type': 'view-detail-btn', 'index': contractor_id},
                    variant="light",
                    fullWidth=True
                ),
                dmc.ActionIcon(
                    DashIconify(icon="solar:letter-bold", width=20),
                    id={'type': 'quick-email-btn', 'index': contractor_id},
                    variant="light",
                    color="blue",
                    size="lg"
                )
            ], grow=True)
        ],
        shadow="sm",
        padding="lg",
        radius="md",
        withBorder=True,
        style={"height": "100%", "cursor": "pointer"}
    )
```

#### 2.2 Contractor Detail Modal (2 hours)

**`components/contractor_detail_modal.py`:**
```python
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

def create_detail_modal(contractor, outreach_materials=None):
    """
    Create detail modal for a contractor

    Args:
        contractor: Dict with contractor data
        outreach_materials: Dict with emails and scripts

    Returns:
        dmc.Modal component
    """
    if not contractor:
        return dmc.Modal(opened=False)

    company_name = contractor.get('company_name', 'Unknown')
    lead_score = contractor.get('lead_score')

    # Tabs content
    contact_tab = dmc.Stack([
        dmc.Grid([
            dmc.Col([
                dmc.Text("Contact Person", size="sm", weight=500, color="dimmed"),
                dmc.Text(contractor.get('contact_person', 'N/A'), size="md")
            ], span=6),
            dmc.Col([
                dmc.Text("Phone", size="sm", weight=500, color="dimmed"),
                dmc.Group([
                    dmc.Text(contractor.get('phone', 'N/A'), size="md"),
                    dmc.ActionIcon(
                        DashIconify(icon="solar:copy-bold", width=16),
                        size="sm",
                        variant="subtle"
                    )
                ])
            ], span=6),
        ]),

        dmc.Grid([
            dmc.Col([
                dmc.Text("Email", size="sm", weight=500, color="dimmed"),
                dmc.Text(contractor.get('email', 'N/A'), size="md")
            ], span=6),
            dmc.Col([
                dmc.Text("Website", size="sm", weight=500, color="dimmed"),
                dmc.Anchor(
                    contractor.get('website', 'N/A'),
                    href=contractor.get('website'),
                    target="_blank"
                )
            ], span=6),
        ]),

        dmc.Grid([
            dmc.Col([
                dmc.Text("Address", size="sm", weight=500, color="dimmed"),
                dmc.Text(contractor.get('address', 'N/A'), size="md")
            ], span=12),
        ]),
    ], spacing="lg")

    profile_tab = dmc.Stack([
        dmc.Grid([
            dmc.Col([
                dmc.Text("Company Type", size="sm", weight=500, color="dimmed"),
                dmc.Badge(
                    contractor.get('company_type', 'N/A').title(),
                    color="blue",
                    variant="light"
                )
            ], span=6),
            dmc.Col([
                dmc.Text("Specializations", size="sm", weight=500, color="dimmed"),
                dmc.Text(contractor.get('specializations', 'N/A'), size="sm")
            ], span=6),
        ]),

        dmc.Text("Glazing Opportunities", size="sm", weight=500, color="dimmed"),
        dmc.Text(contractor.get('glazing_opportunity_types', 'N/A'), size="sm"),

        dmc.Text("Profile Notes", size="sm", weight=500, color="dimmed"),
        dmc.Text(contractor.get('profile_notes', 'No notes available'), size="sm"),

        dmc.Text("Outreach Angle", size="sm", weight=500, color="dimmed"),
        dmc.Text(contractor.get('outreach_angle', 'No outreach angle'), size="sm"),
    ], spacing="md")

    # Outreach materials tab (simplified for now)
    outreach_tab = dmc.Stack([
        dmc.Text("Email templates and call scripts will appear here", color="dimmed")
    ])

    # Activity log tab
    activity_tab = dmc.Stack([
        dmc.Text("Interaction history will appear here", color="dimmed")
    ])

    return dmc.Modal(
        id="contractor-detail-modal",
        opened=True,
        size="xl",
        title=dmc.Group([
            dmc.Text(company_name, size="xl", weight=700),
            dmc.Badge(
                f"Score: {lead_score}/10" if lead_score else "Not Scored",
                color="green" if lead_score and lead_score >= 8 else "blue",
                size="lg"
            )
        ]),
        children=[
            dmc.Tabs(
                value="contact",
                children=[
                    dmc.TabsList([
                        dmc.Tab("Contact Info", value="contact"),
                        dmc.Tab("Profile", value="profile"),
                        dmc.Tab("Outreach", value="outreach"),
                        dmc.Tab("Activity", value="activity"),
                    ]),

                    dmc.TabsPanel(contact_tab, value="contact"),
                    dmc.TabsPanel(profile_tab, value="profile"),
                    dmc.TabsPanel(outreach_tab, value="outreach"),
                    dmc.TabsPanel(activity_tab, value="activity"),
                ]
            ),

            dmc.Space(h=20),

            # Action buttons at bottom
            dmc.Group([
                dmc.Button(
                    "Generate Outreach",
                    leftIcon=DashIconify(icon="solar:magic-stick-bold"),
                    color="blue",
                    variant="filled"
                ),
                dmc.Button(
                    "Log Interaction",
                    leftIcon=DashIconify(icon="solar:notebook-bold"),
                    color="gray",
                    variant="light"
                ),
            ])
        ]
    )
```

#### 2.3 Contractors Page Layout (3 hours)

**`pages/contractors.py`:**
```python
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, ALL, ctx
from modules.database import Database
from components.contractor_card import create_contractor_card
from components.contractor_detail_modal import create_detail_modal

db = Database()

# Page layout
layout = dmc.Stack([
    # Header
    dmc.Group([
        dmc.Title("Contractors", order=1),
        dmc.Badge("12 Total", size="lg", color="blue")  # Dynamic count later
    ], position="apart"),

    dmc.Space(h=10),

    # Search and filters
    dmc.Grid([
        dmc.Col([
            dmc.TextInput(
                id="contractor-search",
                placeholder="Search company name...",
                icon=DashIconify(icon="solar:magnifer-bold"),
                style={"width": "100%"}
            )
        ], span=4),

        dmc.Col([
            dmc.MultiSelect(
                id="city-filter",
                placeholder="Filter by city",
                data=[],  # Populated by callback
                clearable=True
            )
        ], span=3),

        dmc.Col([
            dmc.Select(
                id="status-filter",
                placeholder="Enrichment status",
                data=[
                    {"label": "All", "value": "all"},
                    {"label": "Completed", "value": "completed"},
                    {"label": "Pending", "value": "pending"},
                    {"label": "Failed", "value": "failed"},
                ],
                value="all"
            )
        ], span=2),

        dmc.Col([
            dmc.Select(
                id="sort-by",
                label="Sort by",
                data=[
                    {"label": "Company Name", "value": "name"},
                    {"label": "Score (High to Low)", "value": "score_desc"},
                    {"label": "Score (Low to High)", "value": "score_asc"},
                    {"label": "Date Added", "value": "date"},
                ],
                value="name"
            )
        ], span=3),
    ]),

    dmc.Space(h=20),

    # Contractor cards grid
    html.Div(id="contractors-grid"),

    # Detail modal (hidden by default)
    html.Div(id="detail-modal-container")
], spacing="md")


# Callback: Load and filter contractors
@callback(
    Output("contractors-grid", "children"),
    Output("city-filter", "data"),
    Input("contractor-search", "value"),
    Input("city-filter", "value"),
    Input("status-filter", "value"),
    Input("sort-by", "value"),
)
def update_contractors_grid(search, cities, status, sort_by):
    # Get all contractors
    all_contractors = db.get_all_contractors()

    # Apply filters
    filtered = all_contractors

    if search:
        filtered = [c for c in filtered if search.lower() in c.get('company_name', '').lower()]

    if cities:
        filtered = [c for c in filtered if c.get('city') in cities]

    if status and status != "all":
        filtered = [c for c in filtered if c.get('enrichment_status') == status]

    # Apply sorting
    if sort_by == "name":
        filtered.sort(key=lambda x: x.get('company_name', '').lower())
    elif sort_by == "score_desc":
        filtered.sort(key=lambda x: x.get('lead_score', 0), reverse=True)
    elif sort_by == "score_asc":
        filtered.sort(key=lambda x: x.get('lead_score', 0))
    elif sort_by == "date":
        filtered.sort(key=lambda x: x.get('date_added', ''), reverse=True)

    # Get unique cities for filter dropdown
    cities_list = sorted(list(set([c.get('city') for c in all_contractors if c.get('city')])))
    city_options = [{"label": city, "value": city} for city in cities_list]

    # Create card grid
    if not filtered:
        grid = dmc.Text("No contractors found", color="dimmed", align="center")
    else:
        cards = [
            dmc.Col(
                create_contractor_card(contractor),
                span=4,  # 3 cards per row
                xs=12,   # 1 card per row on mobile
                sm=6,    # 2 cards per row on tablet
                lg=4     # 3 cards per row on desktop
            )
            for contractor in filtered
        ]
        grid = dmc.Grid(cards, gutter="lg")

    return grid, city_options


# Callback: Open detail modal when card is clicked
@callback(
    Output("detail-modal-container", "children"),
    Input({"type": "view-detail-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def open_detail_modal(n_clicks):
    if not any(n_clicks):
        return None

    # Get which button was clicked
    triggered_id = ctx.triggered_id
    contractor_id = triggered_id['index']

    # Fetch contractor details
    contractor = db.get_contractor_by_id(contractor_id)

    # TODO: Fetch outreach materials
    # from modules.outreach import OutreachGenerator
    # outreach_gen = OutreachGenerator()
    # materials = outreach_gen.get_outreach_materials(contractor_id)

    return create_detail_modal(contractor)
```

#### 2.4 Testing & Refinement (1-2 hours)

**Test Checklist:**
- ✅ Cards display correctly in grid
- ✅ Search filters contractors in real-time
- ✅ City and status filters work
- ✅ Sorting works for all options
- ✅ Click "View Details" opens modal
- ✅ Modal displays correct contractor data
- ✅ Modal tabs switch correctly
- ✅ Responsive design (test on mobile/tablet)

---

## Phase 3: Detail View & Outreach (6-8 hours)

### Goals
- Complete outreach materials display in modal
- Add "Generate Outreach" functionality
- Implement interaction logging
- Add quick actions (copy phone, email, etc.)

### Tasks

#### 3.1 Outreach Materials in Modal (2 hours)

**Update `contractor_detail_modal.py`:**
- Display email templates in accordion
- Display call scripts
- Add copy buttons for each template
- Show generation status

#### 3.2 Generate Outreach Callback (2 hours)

**Add to `pages/contractors.py`:**
```python
@callback(
    Output("outreach-generation-status", "children"),
    Input("generate-outreach-btn", "n_clicks"),
    State("selected-contractor-id", "data"),
    prevent_initial_call=True
)
def generate_outreach(n_clicks, contractor_id):
    if not contractor_id:
        return None

    from modules.outreach import OutreachGenerator
    outreach_gen = OutreachGenerator()

    result = outreach_gen.generate_all_outreach(contractor_id)

    if result['success']:
        return dmc.Notification(
            title="Success!",
            message="Outreach materials generated",
            color="green",
            icon=DashIconify(icon="solar:check-circle-bold")
        )
    else:
        return dmc.Notification(
            title="Error",
            message=result['message'],
            color="red"
        )
```

#### 3.3 Interaction Logging (2 hours)

**Add interaction log form to modal:**
- Status dropdown
- Notes textarea
- User name input
- Submit button
- Display interaction history in Activity tab

#### 3.4 Quick Actions (1-2 hours)

**Add to cards and modal:**
- Copy phone number
- Copy email
- Open website in new tab
- Quick email button (opens modal with email template)

---

## Phase 4: Discovery & Enrichment (6-8 hours)

### Goals
- Migrate Discovery page from Streamlit
- Migrate Enrichment page from Streamlit
- Keep modules/scraper.py and modules/enrichment.py unchanged
- Add progress indicators and notifications

### Tasks

#### 4.1 Discovery Page (3 hours)

**`pages/discovery.py`:**
- Search input with templates
- Max results slider
- Search button
- Results display with loading state
- Progress indicator during scraping
- Results cards for new contractors

**Key Features:**
- Use `dmc.LoadingOverlay` during search
- Display results in cards similar to contractors page
- Show "Save to Database" buttons
- Real-time duplicate detection

#### 4.2 Enrichment Page (3 hours)

**`pages/enrichment.py`:**
- Pending contractors list
- Selection options (first 5, first 10, all, custom)
- Enrichment button
- Progress bar
- Real-time results display

**Key Features:**
- Use `dcc.Interval` for progress updates
- Display enrichment results as they complete
- Show score, company type, specializations
- Error handling for failed enrichments

---

## Phase 5: Polish & Testing (4-6 hours)

### Goals
- Complete remaining pages (Dashboard, Bulk Actions, Import, Settings)
- Add notifications system
- Responsive design testing
- Multi-user testing
- Performance optimization

### Tasks

#### 5.1 Dashboard Page (1 hour)

**`pages/dashboard.py`:**
- Summary metrics (total contractors, enriched, high priority)
- Recent activity
- Quick action buttons
- Charts (optional: lead score distribution)

#### 5.2 Bulk Actions Page (1 hour)

**`pages/bulk_actions.py`:**
- Export to CSV (all/filtered)
- Bulk enrichment
- Bulk outreach generation
- Database statistics

#### 5.3 Import Page (1 hour)

**`pages/import_contractors.py`:**
- Manual entry form
- CSV upload with preview
- Import progress
- Validation and duplicate detection

#### 5.4 Settings Page (1 hour)

**`pages/settings.py`:**
- API usage tracking
- Budget monitoring
- Connection status
- Configuration options

#### 5.5 Testing & Refinement (1-2 hours)

**Final Testing:**
- Test all pages with 4 concurrent users (simulate with multiple browsers)
- Test on mobile, tablet, desktop
- Verify all database operations work
- Check for console errors
- Performance profiling

---

## Migration Checklist

### Pre-Migration
- [ ] Read through entire plan
- [ ] Set up development environment
- [ ] Create backup of current Streamlit app
- [ ] Install Dash dependencies

### Phase 1: Infrastructure
- [ ] Create new file structure
- [ ] Set up `dash_app.py`
- [ ] Create page stubs
- [ ] Test basic routing
- [ ] Verify database connection

### Phase 2: Contractors Page
- [ ] Build contractor card component
- [ ] Build detail modal component
- [ ] Implement filtering and search
- [ ] Test card grid responsiveness
- [ ] Test modal interactions

### Phase 3: Outreach
- [ ] Display outreach materials
- [ ] Implement generation callback
- [ ] Add interaction logging
- [ ] Add quick actions

### Phase 4: Discovery & Enrichment
- [ ] Migrate discovery page
- [ ] Migrate enrichment page
- [ ] Test async operations
- [ ] Verify API integrations

### Phase 5: Polish
- [ ] Complete dashboard
- [ ] Complete bulk actions
- [ ] Complete import page
- [ ] Complete settings
- [ ] Final testing

### Post-Migration
- [ ] Deploy Dash app
- [ ] Train users on new UI
- [ ] Monitor for bugs
- [ ] Collect feedback
- [ ] Archive Streamlit app

---

## Code Reuse Strategy

### Keep Unchanged (0 hours)
These modules work perfectly as-is:
- ✅ `modules/database.py`
- ✅ `modules/scraper.py`
- ✅ `modules/enrichment.py`
- ✅ `modules/outreach.py`
- ✅ `.env` file
- ✅ `supabase_schema.sql`

### Translate to Dash (30-40 hours)
Only the UI layer needs rewriting:
- ❌ `app.py` → `dash_app.py` + `pages/*.py`
- ❌ `styles/crm_theme.css` → `assets/custom.css` (minimal, Mantine handles most)

---

## Deployment

### Local Development
```bash
# Run Dash app
python dash_app.py

# Access at http://localhost:8050
```

### Production (Railway)
Update `railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn dash_app:server -b 0.0.0.0:$PORT"
```

Add to `requirements.txt`:
```
gunicorn==21.2.0
```

---

## Resources

### Documentation
- [Dash Mantine Components Docs](https://www.dash-mantine-components.com/)
- [Dash Callbacks Guide](https://dash.plotly.com/basic-callbacks)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) (alternative)
- [Dash Iconify](https://github.com/snehilvj/dash-iconify) (icons)

### Example Apps
- [Dash Gallery](https://dash.gallery/)
- [Mantine Component Showcase](https://www.dash-mantine-components.com/components)

### Support
- Dash Community Forum
- Stack Overflow (dash tag)
- Plotly Discord

---

## Risk Assessment

### High Risk
- ⚠️ **Learning curve** - Dash callbacks are different from Streamlit
  - Mitigation: Start with simple pages, learn incrementally
- ⚠️ **Time estimate accuracy** - Could take longer than 40 hours
  - Mitigation: Phase-based approach allows stopping points

### Medium Risk
- ⚠️ **Async operations** - Enrichment requires background processing
  - Mitigation: Use `dcc.Interval` for polling, keep enrichment module unchanged
- ⚠️ **Multi-user conflicts** - Simultaneous edits to same contractor
  - Mitigation: Supabase handles this, add optimistic UI updates

### Low Risk
- ✅ **Database compatibility** - No changes needed
- ✅ **API integrations** - No changes needed
- ✅ **Data loss** - Can run both apps in parallel during migration

---

## Success Criteria

### Must Have (MVP)
- ✅ Unified Contractors page with cards + detail modal
- ✅ Search, filter, sort working
- ✅ Discovery and enrichment functional
- ✅ Outreach generation and display
- ✅ 4 users can use simultaneously without issues

### Should Have
- ✅ Responsive design (mobile/tablet)
- ✅ All 7 pages migrated
- ✅ Professional appearance (modern CRM feel)
- ✅ CSV import/export working

### Nice to Have
- 🎯 Real-time updates across users
- 🎯 Advanced filtering (date ranges, score ranges)
- 🎯 Bulk selection of contractors
- 🎯 Email sending directly from app

---

## Timeline

**Aggressive (20 hours/week):**
- Week 1: Phases 1-2 (Infrastructure + Contractors page)
- Week 2: Phases 3-4 (Outreach + Discovery/Enrichment)
- Week 3: Phase 5 (Polish + Testing)

**Realistic (10 hours/week):**
- Weeks 1-2: Phase 1-2
- Weeks 3-4: Phase 3-4
- Week 5-6: Phase 5

**Conservative (5 hours/week):**
- 6-8 weeks total

---

## Next Session Kickoff

**Start with Phase 1, Task 1.1:**
1. Install dependencies: `pip install dash dash-mantine-components dash-iconify`
2. Create `dash_app.py` skeleton
3. Test that it runs on port 8050
4. Keep Streamlit running on 8501 for reference

**First Goal:**
Get the basic app shell working with navigation in the first hour.

**Questions to Answer:**
- Do you have any existing design preferences (colors, spacing)?
- Do you want dark mode support?
- Any specific Mantine components you want to explore first?

---

**Ready to start when you are!** 🚀
