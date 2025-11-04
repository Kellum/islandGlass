# Island Glass Leads - Tech Stack & Migration Guide

## 🎯 Purpose
This document serves as a reference for migrating tools and features from other projects into the Island Glass Leads CRM. Use this to understand our architecture, conventions, and implementation patterns.

---

## 🏗️ Core Architecture

### **Framework: Dash + Dash Mantine Components**
- **Main App Entry:** `dash_app.py`
- **Framework:** Python Dash (Plotly Dash)
- **UI Library:** Dash Mantine Components (DMC) v2.3.0+
- **Icons:** Dash Iconify
- **Routing:** Client-side routing with `dcc.Location`
- **State Management:** `dcc.Store` with session storage

### **Why Dash Mantine?**
We migrated from Streamlit to Dash Mantine Components for:
- Better component library (modern, Material Design-inspired)
- More control over UI/UX
- Built-in authentication support
- Better callback system for complex interactions
- Production-ready deployment options

---

## 📁 Project Structure

```
islandGlassLeads/
├── dash_app.py              # Main application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (NOT in git)
│
├── modules/                 # Business logic & data layer
│   ├── __init__.py
│   ├── database.py         # Supabase database operations
│   ├── auth.py             # Authentication & user management
│   ├── scraper.py          # Google Places API scraping
│   ├── enrichment.py       # Claude AI website enrichment
│   └── outreach.py         # Claude AI outreach generation
│
├── pages/                   # Page components (routes)
│   ├── __init__.py
│   ├── dashboard.py        # Main dashboard
│   ├── contractors.py      # Contractor directory & search
│   ├── discovery.py        # Google Places discovery
│   ├── enrichment.py       # Website enrichment queue
│   ├── bulk_actions.py     # CSV export & bulk operations
│   ├── import_contractors.py # CSV import & manual add
│   ├── login.py            # Authentication page
│   └── settings.py         # User settings & API usage
│
├── components/              # Reusable UI components
│   ├── __init__.py
│   ├── auth_check.py       # Auth utilities & session helpers
│   ├── contractor_card.py  # Contractor preview card
│   ├── contractor_detail_modal.py # Detailed contractor view
│   └── outreach_display.py # Outreach materials display
│
└── assets/                  # Static files (CSS, images)
```

---

## 🔧 Tech Stack Details

### **Backend & Data**

#### Database: Supabase (PostgreSQL)
- **ORM:** Direct Supabase Python client (`supabase-py`)
- **Authentication:** Supabase Auth with JWT tokens
- **Storage:** Supabase PostgreSQL with Row Level Security (RLS)
- **Real-time:** Not currently used, but available via Supabase Realtime

**Database Module Pattern (`modules/database.py`):**
```python
from supabase import create_client, Client
from typing import Optional, List, Dict

class Database:
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Supabase client

        Args:
            access_token: Optional JWT for RLS-enabled queries
        """
        self.client: Client = create_client(url, key)
        if access_token:
            self.client.postgrest.auth(access_token)

    def get_all_contractors(self) -> List[Dict]:
        response = self.client.table("contractors").select("*").execute()
        return response.data
```

**Key Tables:**
- `contractors` - Main contractor data with RLS policies
- `outreach_emails` - Generated email templates
- `call_scripts` - Generated call scripts
- `interactions` - Interaction tracking & CRM notes
- `user_profiles` - Extended user profile data

#### AI Services: Anthropic Claude
- **Client:** `anthropic` Python SDK
- **Models Used:**
  - `claude-3-5-sonnet-20241022` for enrichment (website analysis)
  - `claude-3-5-sonnet-20241022` for outreach generation
- **Pattern:** Async operations with `asyncio`

**AI Module Pattern (`modules/enrichment.py`):**
```python
import anthropic
import asyncio

class ContractorEnrichment:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.db = Database()

    async def enrich_contractor(self, contractor_id: int):
        # Fetch website content
        # Send to Claude for analysis
        # Parse structured response
        # Update database
        pass
```

#### External APIs
- **Google Places API:** Contractor discovery (`modules/scraper.py`)
- **Anthropic API:** Website enrichment & outreach generation

---

### **Frontend & UI**

#### Dash Mantine Components (DMC)
**Key Components Used:**

```python
import dash_mantine_components as dmc
from dash import html, dcc, callback, Input, Output, State
from dash_iconify import DashIconify

# Layout pattern
layout = dmc.Stack([
    dmc.Title("Page Title", order=1),
    dmc.Text("Description", c="dimmed"),
    dmc.Space(h=20),

    dmc.Grid([
        dmc.GridCol(
            dmc.Card([...], withBorder=True, shadow="sm"),
            span=4
        )
    ]),
])

# Callback pattern
@callback(
    Output('target-id', 'children'),
    Input('button-id', 'n_clicks'),
    State('session-store', 'data'),
    prevent_initial_call=True
)
def handle_click(n_clicks, session_data):
    # Access authenticated database
    auth_db = get_authenticated_db(session_data)

    # Business logic
    data = auth_db.get_all_contractors()

    # Return DMC components
    return dmc.Stack([...])
```

**Common DMC Components:**
- `dmc.Stack`, `dmc.Group` - Layout containers
- `dmc.Card` - Card containers with borders/shadows
- `dmc.Button`, `dmc.ActionIcon` - Buttons
- `dmc.TextInput`, `dmc.NumberInput`, `dmc.Select` - Form inputs
- `dmc.Badge`, `dmc.Chip` - Status indicators
- `dmc.Modal`, `dmc.Drawer` - Overlays
- `dmc.Table` - Data tables
- `dmc.Alert`, `dmc.Notification` - User feedback
- `DashIconify` - Icon system (Solar icon set primarily)

#### Component Pattern (Reusable Components)

**File:** `components/contractor_card.py`
```python
def create_contractor_card(contractor):
    """
    Create a reusable contractor card component

    Args:
        contractor: Dict with contractor data

    Returns:
        dmc.Card component
    """
    return dmc.Card(
        children=[...],
        id={'type': 'contractor-card', 'index': contractor['id']},
        shadow="sm",
        padding="lg",
        withBorder=True
    )
```

**Usage in pages:**
```python
from components.contractor_card import create_contractor_card

cards = [create_contractor_card(c) for c in contractors]
```

---

## 🔐 Authentication System

### Architecture
- **Provider:** Supabase Auth
- **Flow:** Email/Password with JWT tokens
- **Session Management:** `dcc.Store` with `storage_type='session'`
- **RLS:** Database-level security with user-specific data access

### Implementation Pattern

**Login Page (`pages/login.py`):**
```python
@callback(
    Output('login-session-store', 'data'),
    Output('login-redirect-trigger', 'data'),
    Input('login-button', 'n_clicks'),
    State('login-email', 'value'),
    State('login-password', 'value')
)
def handle_login(n_clicks, email, password):
    auth = AuthManager()
    result = auth.login(email, password)

    if result['success']:
        session_data = {
            'authenticated': True,
            'access_token': result['access_token'],
            'user': result['user']
        }
        return session_data, {'redirect': True}
    return None, None
```

**Protected Routes (`dash_app.py`):**
```python
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('session-store', 'data')
)
def display_page(pathname, session_data):
    # Check authentication
    if not session_data or not session_data.get('authenticated'):
        return dmc.Alert("Please log in")

    # Route to pages
    if pathname == '/':
        return dashboard.layout
    elif pathname == '/contractors':
        return contractors.layout
```

**Database with Auth (`modules/database.py`):**
```python
def get_authenticated_db(session_data):
    """Get database instance with user's access token for RLS"""
    if not session_data:
        return None

    access_token = session_data.get('access_token')
    return Database(access_token=access_token)
```

---

## 🎨 UI/UX Patterns

### Color Scheme
- **Primary:** Blue (`color="blue"`)
- **Success/High Priority:** Green (`color="green"`)
- **Warning/Medium:** Yellow/Orange (`color="yellow"`, `color="orange"`)
- **Danger/Failed:** Red (`color="red"`)
- **Neutral/Pending:** Gray (`color="gray"`)

### Icon System
- **Library:** Dash Iconify
- **Icon Set:** Primarily Solar (Bold variant)
- **Usage:** `DashIconify(icon="solar:icon-name-bold", width=20)`

**Common Icons:**
- `solar:home-2-bold` - Dashboard
- `solar:users-group-rounded-bold` - Contractors
- `solar:magnifer-bold` - Discovery/Search
- `solar:magic-stick-bold` - AI/Enrichment
- `solar:phone-bold` - Phone
- `solar:global-bold` - Website
- `solar:map-point-bold` - Location

### Responsive Layout
```python
# Grid system with responsive columns
dmc.Grid([
    dmc.GridCol(
        content,
        span={'base': 12, 'sm': 6, 'lg': 4}  # Mobile: 12, Tablet: 6, Desktop: 4
    )
])
```

### Pattern Matching Callbacks
```python
# Handle multiple similar elements
@callback(
    Output('modal', 'opened'),
    Input({'type': 'view-detail-btn', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def handle_view_buttons(n_clicks_list):
    triggered = callback_context.triggered_id
    contractor_id = triggered['index']
    # Load contractor details
```

---

## 🔄 State Management Patterns

### Session Store
```python
# In dash_app.py
dcc.Store(id='session-store', storage_type='session', data={'authenticated': False})

# In callbacks
@callback(
    Output('component', 'children'),
    State('session-store', 'data')
)
def update(session_data):
    user = session_data.get('user', {})
    access_token = session_data.get('access_token')
```

### Page-Level State
```python
# In page files
dcc.Store(id='page-state', data={'filter': 'all', 'sort': 'name'})

@callback(
    Output('page-state', 'data'),
    Input('filter-dropdown', 'value')
)
def update_filter(value):
    return {'filter': value}
```

---

## 📦 Dependencies

### Core Python Packages
```txt
# Web Framework
dash>=2.17.1
dash-mantine-components>=2.3.0
dash-iconify>=0.1.2

# Backend Services
supabase>=2.3.4
anthropic>=0.18.1
aiohttp>=3.9.0

# Data Processing
pandas>=2.1.4

# Utilities
python-dotenv>=1.0.0

# Deployment
gunicorn>=21.2.0
```

### Environment Variables
```bash
# .env file (NEVER commit this)
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://....supabase.co
SUPABASE_KEY=eyJh...
SUPABASE_SERVICE_ROLE_KEY=eyJh...
GOOGLE_PLACES_API_KEY=AIza...
```

---

## 🚀 Deployment & Running

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python3 dash_app.py

# Server runs on http://localhost:8050
```

### Production
```bash
# Using Gunicorn
gunicorn dash_app:server -b 0.0.0.0:8050
```

---

## 🧩 Migration Guide for New Features

### Step 1: Identify the Feature Type

**Is it a new page?**
- Create file in `pages/` directory
- Follow the layout pattern with `dmc.Stack`
- Register callbacks with `@callback` decorator
- Import and route in `dash_app.py`

**Is it a reusable component?**
- Create function in `components/` directory
- Return DMC component structure
- Export and use in pages

**Is it business logic?**
- Create class/functions in `modules/` directory
- Integrate with Database class
- Follow async patterns if using AI

### Step 2: Understand Your Current Stack

**If coming from React/Next.js:**
- Components → Python functions returning DMC components
- useState → dcc.Store
- useEffect → callbacks with Intervals or State dependencies
- API routes → Module functions + Supabase direct queries
- CSS → DMC `style={}` props or `className`

**If coming from Streamlit:**
- `st.button()` → `dmc.Button()` with callback
- `st.text_input()` → `dmc.TextInput()` with callback
- `st.columns()` → `dmc.Grid()` with `dmc.GridCol()`
- `st.session_state` → `dcc.Store(storage_type='session')`
- `st.rerun()` → Return updated components from callback

**If coming from Flask:**
- Routes → Page files in `pages/`
- Templates → DMC component structures
- Form handling → Callbacks with Input/State
- Database queries → `modules/database.py` methods

### Step 3: Code Translation Examples

#### Example 1: Form with Submission

**Other Stack (Streamlit):**
```python
email = st.text_input("Email")
if st.button("Submit"):
    save_to_db(email)
    st.success("Saved!")
```

**Island Glass Stack (Dash Mantine):**
```python
# Layout
layout = dmc.Stack([
    dmc.TextInput(id='email-input', label="Email"),
    dmc.Button("Submit", id='submit-btn'),
    html.Div(id='feedback')
])

# Callback
@callback(
    Output('feedback', 'children'),
    Input('submit-btn', 'n_clicks'),
    State('email-input', 'value'),
    prevent_initial_call=True
)
def handle_submit(n_clicks, email):
    db = Database()
    db.save_email(email)
    return dmc.Alert("Saved!", color="green")
```

#### Example 2: Data Table with Actions

**Other Stack (React):**
```jsx
const Table = ({ data }) => (
  <table>
    {data.map(row => (
      <tr key={row.id}>
        <td>{row.name}</td>
        <td><button onClick={() => handleView(row.id)}>View</button></td>
      </tr>
    ))}
  </table>
)
```

**Island Glass Stack (Dash Mantine):**
```python
# Component
def create_table(data):
    return dmc.Table([
        dmc.TableThead([
            dmc.TableTr([
                dmc.TableTh("Name"),
                dmc.TableTh("Actions")
            ])
        ]),
        dmc.TableTbody([
            dmc.TableTr([
                dmc.TableTd(row['name']),
                dmc.TableTd(dmc.Button(
                    "View",
                    id={'type': 'view-btn', 'index': row['id']}
                ))
            ]) for row in data
        ])
    ])

# Callback
@callback(
    Output('detail-modal', 'opened'),
    Input({'type': 'view-btn', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def handle_view(n_clicks_list):
    triggered = callback_context.triggered_id
    row_id = triggered['index']
    # Load and display details
    return True
```

#### Example 3: AI Integration

**Pattern for Claude AI:**
```python
# In modules/your_feature.py
import anthropic
import os

class YourFeature:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.db = Database()

    async def process_with_ai(self, input_text: str):
        """Process input with Claude AI"""
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"Your prompt here: {input_text}"
                }]
            )

            result = message.content[0].text
            # Parse and store result
            return {"success": True, "data": result}

        except Exception as e:
            return {"success": False, "error": str(e)}

# In page callback
import asyncio
from modules.your_feature import YourFeature

@callback(...)
def process_button_click(...):
    feature = YourFeature()
    result = asyncio.run(feature.process_with_ai(user_input))
    if result['success']:
        return dmc.Alert(result['data'], color="green")
```

### Step 4: Database Operations

**Pattern:**
```python
# Add method to modules/database.py
class Database:
    def your_new_method(self, param: str) -> List[Dict]:
        """Description of what this does"""
        try:
            response = self.client.table("your_table")\
                .select("*")\
                .eq("column", param)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error: {e}")
            return []

# Use in callbacks
@callback(...)
def your_callback(session_data):
    db = get_authenticated_db(session_data)
    data = db.your_new_method("value")
    return create_display(data)
```

---

## 📋 Checklist for Migrating a Feature

- [ ] Identify feature type (page/component/module)
- [ ] Review similar existing code in this project
- [ ] Create file in appropriate directory
- [ ] Convert UI to DMC components
- [ ] Convert state management to dcc.Store + callbacks
- [ ] Integrate with Database class for data operations
- [ ] Add authentication checks if needed
- [ ] Test with development server
- [ ] Update this guide if you discover new patterns!

---

## 🆘 Common Patterns & Solutions

### Loading States
```python
@callback(
    Output('content', 'children'),
    Output('loading', 'data'),
    Input('button', 'n_clicks'),
    prevent_initial_call=True
)
def load_data(n_clicks):
    # Return loading state first
    return dmc.Loader(), True

    # Then return actual content
    data = fetch_data()
    return create_content(data), False
```

### Error Handling
```python
@callback(...)
def handle_action(...):
    try:
        result = perform_action()
        return dmc.Alert("Success!", color="green")
    except Exception as e:
        return dmc.Alert(f"Error: {str(e)}", color="red")
```

### Pagination
```python
@callback(
    Output('table', 'children'),
    Input('page-number', 'value'),
    State('session-store', 'data')
)
def paginate(page, session_data):
    db = get_authenticated_db(session_data)
    limit = 20
    offset = (page - 1) * limit

    # Supabase pagination
    data = db.client.table("contractors")\
        .select("*")\
        .range(offset, offset + limit - 1)\
        .execute()

    return create_table(data.data)
```

---

## 🎓 Learning Resources

### Dash Documentation
- **Official Docs:** https://dash.plotly.com/
- **DMC Docs:** https://www.dash-mantine-components.com/
- **Dash Iconify:** https://github.com/snehilvj/dash-iconify

### Supabase
- **Python Client:** https://supabase.com/docs/reference/python/
- **Auth Guide:** https://supabase.com/docs/guides/auth
- **RLS Policies:** https://supabase.com/docs/guides/auth/row-level-security

### Claude AI
- **API Reference:** https://docs.anthropic.com/
- **Best Practices:** Use prompt caching, structured outputs

---

## 💡 Tips for Success

1. **Start Small:** Migrate one component at a time
2. **Follow Patterns:** Look at existing pages/components for reference
3. **Test Often:** Run `python3 dash_app.py` frequently during development
4. **Use Type Hints:** Makes code more maintainable
5. **Authentication:** Always use `get_authenticated_db(session_data)` for user-specific data
6. **Async AI Calls:** Use `asyncio.run()` in callbacks for Claude API calls
7. **Error Messages:** Always show user-friendly errors with `dmc.Alert`

---

## 📝 Code Snippets Library

### New Page Template
```python
"""
Your Page Name
Description of what this page does
"""
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State
from dash_iconify import DashIconify
from modules.database import get_authenticated_db

layout = dmc.Stack([
    dmc.Title("Page Title", order=1),
    dmc.Text("Description", c="dimmed"),

    # Your content here
    html.Div(id='page-content')
], gap="md")

@callback(
    Output('page-content', 'children'),
    Input('session-store', 'data'),
)
def load_page(session_data):
    db = get_authenticated_db(session_data)
    # Your logic here
    return dmc.Text("Content")
```

### Modal Pattern
```python
# In layout
dmc.Modal(
    id='detail-modal',
    title="Details",
    size="lg",
    children=[html.Div(id='modal-content')]
)

# Callback to open/close
@callback(
    Output('detail-modal', 'opened'),
    Output('modal-content', 'children'),
    Input('open-btn', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_modal(n_clicks):
    return True, dmc.Text("Modal content")
```

### File Upload Pattern
```python
dmc.FileInput(
    id='file-upload',
    label="Upload CSV",
    accept=".csv"
)

@callback(
    Output('upload-result', 'children'),
    Input('file-upload', 'contents'),
    State('file-upload', 'filename')
)
def handle_upload(contents, filename):
    if contents:
        import pandas as pd
        import base64
        import io

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Process dataframe
        return dmc.Alert(f"Uploaded {len(df)} rows", color="green")
```

---

**Questions? Check existing code first, then ask!**

This is a living document - update it as you discover new patterns!
