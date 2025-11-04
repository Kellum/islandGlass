# Contributing to Island Glass CRM

Welcome! This guide will help you get set up and contributing to the Island Glass Leads CRM project.

## Table of Contents
- [Quick Start](#quick-start)
- [Project Architecture](#project-architecture)
- [Development Workflow](#development-workflow)
- [Database Management](#database-management)
- [Testing](#testing)
- [Code Style](#code-style)

---

## Quick Start

### Prerequisites
- Python 3.9+
- Supabase account
- Anthropic API key (for AI enrichment features)
- Google Places API key (for contractor discovery)

### 1. Clone and Setup

```bash
git clone https://github.com/Kellum/islandGlass.git
cd islandGlass
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
GOOGLE_PLACES_API_KEY=your-google-key-here
```

### 4. Set Up Database

Run migrations in order in your Supabase SQL Editor:

1. `database/migrations/001_initial_schema.sql`
2. `database/migrations/002_user_roles_departments.sql`
3. `database/migrations/003_window_manufacturing.sql`
4. `database/migrations/004_window_seed_data.sql`

See [database/README.md](database/README.md) for detailed migration instructions.

### 5. Run the Application

```bash
python3 dash_app.py
```

Open http://localhost:8050 in your browser.

---

## Project Architecture

### Tech Stack
- **Frontend**: Dash (Plotly) + Dash Mantine Components (dmc)
- **Backend**: Python 3.9+
- **Database**: Supabase (PostgreSQL with Row-Level Security)
- **AI**: Anthropic Claude (contractor enrichment)
- **APIs**: Google Places (discovery), Zebra ZPL (label printing)

### Directory Structure

```
islandGlass/
├── dash_app.py              # Main application entry point
├── modules/                 # Business logic and utilities
│   ├── auth.py             # Authentication & session management
│   ├── database.py         # Supabase operations (CRUD methods)
│   ├── permissions.py      # Role-based access control
│   ├── glass_calculator.py # Glass pricing calculations
│   ├── zpl_generator.py    # Label ZPL code generation
│   ├── label_printer.py    # Zebra printer communication
│   ├── enrichment.py       # AI-powered contractor enrichment
│   ├── outreach.py         # Email/script generation
│   └── scraper.py          # Multi-source contractor discovery
│
├── pages/                   # Dash page components
│   ├── login.py            # Authentication page
│   ├── dashboard.py        # Main dashboard
│   ├── contractors.py      # Contractor directory
│   ├── po_clients.py       # PO client management
│   ├── window_order_entry.py      # Window order creation
│   ├── inventory_page.py   # Glass inventory
│   └── calculator.py       # Glass price calculator
│
├── components/              # Reusable UI components
│   ├── auth_check.py       # Session validation
│   ├── contractor_card.py  # Contractor display card
│   └── outreach_display.py # Outreach materials display
│
├── database/                # Database files
│   ├── migrations/         # Versioned SQL migrations
│   ├── utilities/          # Helper SQL queries
│   └── archive/           # Historical migrations
│
├── docs/                    # Documentation
│   ├── sessions/           # Session notes & progress
│   ├── architecture/       # Technical design docs
│   └── archive/           # Historical documentation
│
├── tests/                   # Test files
└── labels_output/          # ZPL label files (mock mode)
```

### Key Modules Explained

#### `modules/database.py`
- `Database` class: Main Supabase interface
- `get_authenticated_db(session_data)`: Creates authenticated DB instance
- Methods for contractors, PO clients, orders, labels, inventory
- Handles Row-Level Security (RLS) policies

#### `modules/permissions.py`
- Role-based access control: Admin, Manager, Sales, Production
- `get_user_window_permissions(user_profile)`: Check user capabilities
- Department-based filtering: Sales, Production, Accounting

#### `modules/zpl_generator.py`
- `ZPLGenerator`: Creates Zebra printer label code
- Generates 4x6 labels with barcodes, measurements
- Supports multiple label formats for different window types

---

## Development Workflow

### Creating a New Page

1. Create file in `pages/` directory:
```python
# pages/my_new_page.py
from dash import html, callback, Input, Output
import dash_mantine_components as dmc
from modules.database import get_authenticated_db
from modules.permissions import get_user_window_permissions

def layout(session_data=None):
    if not session_data:
        return html.Div("Please log in")

    user_profile = session_data.get('user_profile', {})
    perms = get_user_window_permissions(user_profile)

    return dmc.Container([
        dmc.Title("My New Page"),
        # Your content here
    ])

# Register callbacks here
@callback(...)
def my_callback():
    pass
```

2. Register in `dash_app.py`:
```python
from pages import my_new_page

dash.register_page(
    "my_new_page",
    path="/my-new-page",
    layout=my_new_page.layout,
    title="My New Page"
)
```

### Adding Database Methods

1. Add method to `modules/database.py`:
```python
def get_my_data(self, company_id: int, filters: dict = None):
    """
    Get data with optional filtering.

    Args:
        company_id: Company ID for RLS filtering
        filters: Optional dict of filter criteria

    Returns:
        List of matching records
    """
    query = self.supabase.table('my_table').select('*')
    query = query.eq('company_id', company_id)

    if filters:
        # Apply filters
        pass

    result = query.execute()
    return result.data if result.data else []
```

2. Use in pages/callbacks:
```python
db = get_authenticated_db(session_data)
company_id = session_data.get('user_profile', {}).get('company_id')
data = db.get_my_data(company_id)
```

### Permission Checking

Always check permissions before showing sensitive content:

```python
from modules.permissions import get_user_window_permissions

user_profile = session_data.get('user_profile', {})
perms = get_user_window_permissions(user_profile)

if perms.is_admin():
    # Show admin controls
elif perms.can_manage_orders():
    # Show order management
elif perms.can_view_orders():
    # Show read-only view
else:
    return "Access Denied"
```

---

## Database Management

### Running Migrations

See [database/README.md](database/README.md) for detailed instructions.

**Quick reference:**
1. Open Supabase SQL Editor
2. Run migrations in numerical order (001, 002, 003, 004)
3. Verify no errors in output
4. Check RLS policies are active

### Creating New Migrations

1. Create file: `database/migrations/00X_description.sql`
2. Include:
   - Table creation
   - RLS policies
   - Indexes
   - Sample data (if needed)

3. Document in `database/README.md`

### Testing Database Changes

Use `database/utilities/` for helper queries:
- Check migration status
- Verify RLS policies
- Test data access

---

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_enrichment.py

# Run with coverage
python -m pytest --cov=modules tests/
```

### Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_my_feature.py
import pytest
from modules.database import Database

def test_my_feature():
    db = Database()
    result = db.my_method()
    assert result is not None
```

---

## Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints where possible
- Docstrings for all public functions
- Keep functions focused and small

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case()`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore()`

### Dash Components
- Use Dash Mantine Components (dmc) for UI
- Prefer functional layouts over class-based
- Keep callbacks close to related components
- Use pattern-matching callbacks for dynamic IDs

### Git Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Be descriptive: "Add window order filtering by date range"
- Reference issues: "Fix #123: Resolve label printing bug"

---

## Common Tasks

### Adding a New Role

1. Update `database/migrations/002_user_roles_departments.sql`
2. Add role logic in `modules/permissions.py`
3. Update relevant page access checks

### Adding a New Window Type

1. Add to `window_types` table in migration
2. Update `modules/zpl_generator.py` for label format
3. Update form in `pages/window_order_entry.py`

### Debugging Database Issues

1. Check Supabase logs in dashboard
2. Verify RLS policies: `database/archive/test_rls.sql`
3. Use authenticated DB instance: `get_authenticated_db(session_data)`
4. Check company_id is being passed correctly

---

## Getting Help

### Documentation
- Architecture guides: `docs/architecture/`
- Session notes: `docs/sessions/`
- Database guide: `database/README.md`

### Key Files to Review
- `docs/architecture/TECH_STACK_GUIDE.md` - Comprehensive tech overview
- `docs/sessions/SESSION_13_START_HERE.md` - Current project status
- `docs/architecture/SECURITY.md` - Security & RLS implementation

### Common Issues
- **"Not authenticated" errors**: Check session_data is passed to page layout
- **Empty database queries**: Verify RLS policies and company_id
- **Import errors**: Ensure you're in project root directory

---

## Project Status

**Current Phase**: Window Manufacturing System (70% complete)

**Active Development**:
- Window Order Management page (pending)
- Label Printing page (pending)
- Navigation integration (pending)

**Completed Features**:
- Contractor lead generation & enrichment
- PO client management
- Window order entry
- Glass inventory & calculator
- Label generation (ZPL)
- Authentication & RLS

---

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Test thoroughly
4. Commit with clear messages
5. Push and create a Pull Request

---

**Questions?** Check `docs/` directory or reach out to the team!

Happy coding!
