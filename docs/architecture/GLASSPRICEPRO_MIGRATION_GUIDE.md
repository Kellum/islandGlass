# GlassPricePro → Dash Mantine Migration Guide

**Project:** Island Glass & Mirror - GlassPricePro Tools
**Target Framework:** Dash + Dash Mantine Components
**Source:** React + TypeScript + Express + PostgreSQL
**Created:** 2025-11-02

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What is GlassPricePro?](#what-is-glasspricepro)
3. [Complete Feature List](#complete-feature-list)
4. [Database Schema](#database-schema)
5. [Python Calculation Modules](#python-calculation-modules)
6. [Dash Implementation Guide](#dash-implementation-guide)
7. [Phase-by-Phase Build Plan](#phase-by-phase-build-plan)
8. [Component Mapping Reference](#component-mapping-reference)

---

## Executive Summary

### What You're Building

**GlassPricePro** is a comprehensive glass manufacturing and pricing management system for Island Glass & Mirror. This guide provides everything needed to rebuild all its features in Dash + Mantine.

### Key Business Value

- **Pricing Calculators**: 5 specialized calculators for accurate glass/IGU quotes
- **Manufacturing Optimization**: Spacer cutting optimization saves 10-20% material costs
- **Production Management**: Kanban workflow from order to delivery
- **Inventory & PO Tracking**: Complete supply chain and client relationship management
- **Product Catalog**: AI-powered PDF import for supplier catalogs
- **Admin Tools**: Comprehensive pricing configuration and wiki system

### Migration Strategy

**Build from scratch, not merge.** The React/TypeScript codebase cannot be directly ported, but:

✅ **100% Portable**: All business logic (formulas, calculations, optimization algorithms)
✅ **100% Reusable**: PostgreSQL database schema (reuse as-is)
✅ **Adaptable**: UI patterns translate cleanly to Dash Mantine
✅ **Improved**: Python offers better data processing (pandas, numpy, fractions module)

### Estimated Effort

- **Core Calculators**: 15-20 hours (Phase 1-2)
- **Data Management**: 10-15 hours (Phase 3)
- **Advanced Features**: 15-20 hours (Phase 4-5)
- **Polish & Testing**: 5-10 hours (Phase 6)
- **Total**: 45-65 hours

---

## What is GlassPricePro?

### Domain

GlassPricePro is a **B2B glass manufacturing and pricing system** that handles:

1. **Custom Glass Quoting** - Calculate prices for any glass configuration
2. **Insulated Glass Units (IGUs)** - Multi-pane windows with muntins
3. **Manufacturing Workflow** - From order receipt to installation
4. **Supply Chain** - Inventory, suppliers, purchase orders
5. **Client Relationships** - PO tracking, activity logging

### Users

- **Sales Team** - Quote generation, client management
- **Production Team** - Manufacturing workflow, kanban boards
- **Management** - Inventory, pricing configuration, reporting

---

## Complete Feature List

### 1. Calculators (5 Total)

#### A. Glass Calculator V2
**File Reference**: `client/src/pages/calculator-v2.tsx` & `client/src/components/calculator-form.tsx`

**Purpose**: Primary glass pricing tool with full feature set

**Features**:
- Glass type selection (clear, bronze, gray, mirror)
- Thickness options (1/8", 3/16", 1/4", 3/8", 1/2")
- Rectangular or circular shapes
- Dimension inputs (supports fractions like "24 1/2")
- Edge processing: polish, beveled, clipped corners
- Tempered glass markup
- Shape markup (non-rectangular, circular)
- Contractor discount (15%)
- Quantity multiplier
- Real-time price calculation
- Shopping cart system (add multiple items)
- PDF quote generation with CAD drawings
- Price breakdown display

**Business Logic**:
```
Minimum billable: 3 sq ft
Square footage = (width × height) ÷ 144  [or π × r² ÷ 144 for circular]
Base price = sq ft × base rate per sq ft
Perimeter = 2 × (width + height)  [or π × diameter for circular]
Polish price = perimeter × polish rate per inch
Beveled price = perimeter × beveled rate per inch (varies by thickness)
Clipped corners price = num corners × price per corner
Tempered markup = (base + edges) × tempered percentage
Shape markup = (base + edges) × shape percentage
Contractor discount = subtotal × 0.15
Final total = (subtotal - discount) × quantity

ULTIMATE FORMULA: Final Quote Price = Combined Cost ÷ 0.28
```

#### B. IGU Calculator
**File Reference**: `client/src/pages/igu-calculator.tsx` & `client/src/components/igu-calculator-form.tsx`

**Purpose**: Insulated Glass Unit (multi-pane window) pricing with muntins

**Features**:
- Glass type selection (clear only - standard for IGUs)
- Thickness selection (3/16", 1/4")
- Airspace selection (3/8", 1/2", 5/8", 3/4", 1")
- Dimension inputs (width, height)
- Muntin options:
  - GBG (Grids Between Glass)
  - SDL (Simulated Divided Lites)
  - None
- Muntin pattern selection (colonial, prairie, custom)
- Tempered options (both panes, outside only, inside only, none)
- Low-E coating options
- Argon gas fill option
- Quantity and pricing
- PDF quote generation

**Business Logic**:
```
Base price calculation similar to glass calculator
Additional costs:
- Airspace cost (varies by thickness)
- Muntin cost (per pattern, GBG vs SDL)
- Low-E coating per sq ft
- Argon fill per sq ft
- Dual tempering markup
```

#### C. Spacer Calculator
**File Reference**: `client/src/pages/spacer-calculator.tsx`

**Purpose**: **Manufacturing optimization tool** - calculates spacer requirements and optimizes cutting from stock

**Features**:
- Multi-section project organization
- Window dimension inputs (fractions supported)
- Quantity per window
- Spacer size selection (common IGU spacer sizes)
- Automatic spacer calculation: `(width × 2) + (height × 2)`
- Glass dimension calculation (subtracts spacer deduction)
- **Cutting optimization algorithm**:
  - Groups identical lengths
  - Optimizes cuts from 152" stock sticks
  - Accounts for 1/8" blade kerf
  - Minimizes waste
  - Efficiency percentage calculation
- **Glass sheet optimization**:
  - 2D bin packing for glass sheet cutting
  - Sheet size configuration
  - Waste calculation
- Export results to CSV

**Business Value**: Reduces material waste by 10-20%, critical for large projects

**Algorithm** (Python-ready):
```python
STICK_LENGTH = 152  # inches
BLADE_KERF = 0.125  # 1/8" per cut

def optimize_cutting(lengths_with_quantities):
    """
    Bin packing algorithm for 1D cutting stock problem
    - Sort lengths descending
    - First-fit-decreasing heuristic
    - Track waste per stick
    """
    sticks = []
    for length, qty in sorted(lengths_with_quantities, reverse=True):
        for _ in range(qty):
            # Try to fit in existing stick
            placed = False
            for stick in sticks:
                if stick['remaining'] >= length + BLADE_KERF:
                    stick['cuts'].append(length)
                    stick['remaining'] -= (length + BLADE_KERF)
                    placed = True
                    break
            # Create new stick if needed
            if not placed:
                sticks.append({
                    'cuts': [length],
                    'remaining': STICK_LENGTH - length
                })

    total_waste = sum(s['remaining'] for s in sticks)
    efficiency = ((len(sticks) * STICK_LENGTH) - total_waste) / (len(sticks) * STICK_LENGTH)
    return sticks, efficiency
```

#### D. Fraction Calculator
**File Reference**: `client/src/pages/fraction-calculator.tsx`

**Purpose**: Construction measurement arithmetic (fractions, mixed numbers)

**Features**:
- Add, subtract, multiply, divide fractions
- Mixed number support (e.g., "24 1/2 + 3/4")
- Decimal conversion
- Simplification to lowest terms
- Real-time calculation

**Python Implementation**:
```python
from fractions import Fraction

def parse_measurement(input_str):
    """Parse mixed numbers, fractions, decimals"""
    input_str = input_str.strip()

    # Mixed number: "24 1/2"
    if ' ' in input_str:
        parts = input_str.split()
        whole = int(parts[0])
        frac = Fraction(parts[1])
        return whole + frac

    # Fraction: "3/4"
    elif '/' in input_str:
        return Fraction(input_str)

    # Decimal: "24.5"
    else:
        return Fraction(float(input_str)).limit_denominator()

def format_fraction(frac):
    """Format as mixed number if > 1"""
    if frac >= 1:
        whole = int(frac)
        remainder = frac - whole
        if remainder == 0:
            return str(whole)
        return f"{whole} {remainder.numerator}/{remainder.denominator}"
    return f"{frac.numerator}/{frac.denominator}"

# Example usage:
a = parse_measurement("24 1/2")
b = parse_measurement("3/4")
result = a + b  # Fraction(99, 4)
print(format_fraction(result))  # "24 3/4"
```

#### E. IG Quote Calculator
**File Reference**: `client/src/pages/ig-quote.tsx` & `client/src/components/ig-quote-calculator.tsx`

**Purpose**: Quick IGU quotes (simplified version)

**Features**:
- Streamlined IGU quoting interface
- Fewer options than full IGU Calculator
- Faster workflow for common configurations

---

### 2. Production Management

#### A. Production Kanban Board
**File Reference**: `client/src/pages/production-kanban.tsx`

**Purpose**: Visual workflow management for glass manufacturing

**Features**:
- **Configurable stages**: Glass Status, Spacer Status, In Production, Ready to Schedule
- **Drag-and-drop cards** between stages (uses @dnd-kit)
- **Job cards** with:
  - Company name
  - Due date with color coding (overdue = red, today = yellow, future = green)
  - Priority (low/medium/high) with badge
  - Assigned to (team member)
  - Notes count
- **Notes system**:
  - Add notes to any job
  - Timestamp and user tracking
  - Real-time updates
- **Filters**:
  - Priority filter
  - Assigned to filter
  - Search by company name
- **Card actions**:
  - Edit job details
  - Delete job
  - Archive completed jobs

**Dash Implementation**:
```python
import dash_mantine_components as dmc
from dash import html, Input, Output, State, callback, MATCH, ALL

# Use dash-draggable for drag-drop (or custom callbacks)
# Alternative: dash-drag-drop extension

layout = dmc.Grid([
    # Column for each stage
    dmc.Col([
        dmc.Stack([
            dmc.Title(stage_name, order=4),
            dmc.Badge(f"{len(jobs)} jobs"),
            html.Div(id={'type': 'job-container', 'stage': stage_id})
        ])
    ], span=3)
    for stage_id, stage_name in enumerate(stages)
])

@callback(
    Output({'type': 'job-container', 'stage': MATCH}, 'children'),
    Input('jobs-store', 'data'),
    State({'type': 'job-container', 'stage': MATCH}, 'id')
)
def update_stage(jobs_data, container_id):
    stage_id = container_id['stage']
    stage_jobs = [j for j in jobs_data if j['stage_id'] == stage_id]

    return [
        create_job_card(job)
        for job in sorted(stage_jobs, key=lambda x: x['priority'])
    ]

def create_job_card(job):
    return dmc.Card([
        dmc.Group([
            dmc.Text(job['company'], weight=700),
            dmc.Badge(
                job['priority'],
                color='red' if job['priority'] == 'high' else 'yellow'
            )
        ], position='apart'),
        dmc.Text(f"Due: {job['due_date']}", size='sm', color='dimmed'),
        dmc.Text(f"Notes: {job['notes_count']}", size='xs'),
        dmc.Group([
            dmc.ActionIcon(
                DashIconify(icon="solar:pen-bold"),
                id={'type': 'edit-job', 'index': job['id']},
                variant='light'
            ),
            dmc.ActionIcon(
                DashIconify(icon="solar:trash-bin-trash-bold"),
                id={'type': 'delete-job', 'index': job['id']},
                color='red'
            )
        ])
    ], withBorder=True, shadow='sm', p='sm')
```

**Database Tables**:
```sql
CREATE TABLE production_stages (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,
    color TEXT
);

CREATE TABLE production_jobs (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    stage_id INTEGER REFERENCES production_stages(id),
    due_date DATE,
    priority TEXT CHECK (priority IN ('low', 'medium', 'high')),
    assigned_to TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE production_notes (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES production_jobs(id) ON DELETE CASCADE,
    note TEXT NOT NULL,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 3. PO Tracker (CRM System)

#### A. Clients Management
**File Reference**: `client/src/pages/po-tracker/clients.tsx`

**Purpose**: Customer relationship management

**Features**:
- **View modes**: Card view or table/list view (togglable, persisted)
- **Client cards** showing:
  - Company name
  - Contact person
  - Phone, email, address
  - Client type (contractor/residential/commercial)
  - Location (city/state)
  - Tags (custom labels)
  - Number of POs
- **Filters**:
  - Search by name/company
  - Filter by city
  - Filter by client type
  - Filter by tags
- **Sorting**:
  - Name A-Z
  - Company A-Z
  - PO count (high to low)
  - Recently added
- **Actions**:
  - Add new client
  - Edit client
  - Delete client
  - View client detail page

**Dash Pattern**:
```python
# Toggle between card and list view
@callback(
    Output('clients-container', 'children'),
    Input('view-toggle', 'value'),  # 'card' or 'list'
    Input('search-input', 'value'),
    Input('city-filter', 'value'),
    State('clients-data', 'data')
)
def render_clients(view_mode, search, city_filter, clients):
    filtered = filter_clients(clients, search, city_filter)

    if view_mode == 'card':
        return dmc.Grid([
            dmc.Col(create_client_card(client), span=4)
            for client in filtered
        ], gutter='lg')
    else:
        return dmc.Table([
            create_client_row(client)
            for client in filtered
        ])
```

#### B. Client Detail Page
**File Reference**: `client/src/pages/po-tracker/client-detail.tsx`

**Purpose**: Comprehensive view of single client

**Features**:
- **Header**: Company name, contact info, edit button
- **Client info section**: All contact details, type, location
- **Purchase Orders tab**:
  - List of all POs for this client
  - PO status badges
  - Total value
  - Due dates
  - Quick actions (view, edit, delete)
- **Activity Log tab**:
  - Chronological history
  - Call logs, emails, meetings, notes
  - User who created each activity
  - Timestamps
- **Actions**:
  - Add new PO
  - Log new activity
  - Edit client info
  - Delete client

#### C. Purchase Order Detail
**File Reference**: `client/src/pages/po-tracker/po-detail.tsx`

**Purpose**: Individual PO management

**Features**:
- **PO header**: PO number, client, date, status
- **Line items**:
  - Product/service description
  - Quantity
  - Unit price
  - Total
- **Financials**:
  - Subtotal
  - Tax
  - Total
- **Status tracking**: Quoted, Ordered, In Production, Completed, Invoiced
- **Notes and attachments**
- **Activity log** specific to this PO

**Database Schema**:
```sql
CREATE TABLE po_clients (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    client_type TEXT,
    tags TEXT[],
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE po_purchase_orders (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES po_clients(id) ON DELETE CASCADE,
    po_number TEXT UNIQUE,
    status TEXT,
    total_amount DECIMAL(10,2),
    due_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE po_activities (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES po_clients(id),
    po_id INTEGER REFERENCES po_purchase_orders(id),
    activity_type TEXT,  -- call, email, meeting, note
    description TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 4. Inventory Management

**File Reference**: `client/src/pages/inventory.tsx`

**Purpose**: Track IGU manufacturing supplies

**Features**:
- **Inventory items**:
  - Name
  - Category (spacers, butyl, molecular sieve, desiccant, etc.)
  - Stock quantity
  - Unit (pieces, linear feet, pounds, gallons, boxes, rolls)
  - Cost per unit
  - Supplier
  - Low stock threshold
- **Visual indicators**:
  - Low stock warning (red badge if qty < threshold)
  - Color-coded categories
- **Drag-to-reorder** items (saves sort order to database)
- **Actions**:
  - Add item
  - Edit item
  - Duplicate item (quick creation)
  - Delete item
- **Filters**:
  - Category filter
  - Low stock only toggle
  - Search by name

**Dash Implementation**:
```python
# Sortable table with drag handles
import dash_mantine_components as dmc
from dash_iconify import DashIconify

def create_inventory_table(items):
    return dmc.Table([
        html.Thead([
            html.Tr([
                html.Th(""),  # Drag handle
                html.Th("Item"),
                html.Th("Category"),
                html.Th("Stock"),
                html.Th("Unit"),
                html.Th("Cost/Unit"),
                html.Th("Actions")
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(DashIconify(icon="solar:hamburger-menu-bold")),  # Drag handle
                html.Td(item['name']),
                html.Td(dmc.Badge(item['category'])),
                html.Td([
                    dmc.Text(item['quantity']),
                    dmc.Badge(
                        "Low",
                        color='red',
                        size='xs'
                    ) if item['quantity'] < item['low_stock_threshold'] else None
                ]),
                html.Td(item['unit']),
                html.Td(f"${item['cost_per_unit']:.2f}"),
                html.Td(dmc.Group([
                    dmc.ActionIcon(
                        DashIconify(icon="solar:pen-bold"),
                        id={'type': 'edit-inventory', 'index': item['id']}
                    ),
                    dmc.ActionIcon(
                        DashIconify(icon="solar:copy-bold"),
                        id={'type': 'duplicate-inventory', 'index': item['id']}
                    ),
                    dmc.ActionIcon(
                        DashIconify(icon="solar:trash-bold"),
                        id={'type': 'delete-inventory', 'index': item['id']},
                        color='red'
                    )
                ]))
            ], id={'type': 'inventory-row', 'index': item['id']})
            for item in items
        ])
    ])
```

**Database Schema**:
```sql
CREATE TABLE inventory_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE inventory_units (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER REFERENCES inventory_categories(id),
    quantity DECIMAL(10,2),
    unit_id INTEGER REFERENCES inventory_units(id),
    cost_per_unit DECIMAL(10,2),
    supplier_id INTEGER REFERENCES suppliers(id),
    low_stock_threshold DECIMAL(10,2),
    sort_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 5. Product Catalog & Admin

#### A. Product Catalog
**File Reference**: `client/src/pages/admin-products.tsx`

**Purpose**: Flexible billable items beyond glass

**Features**:
- **Product types**:
  - Hardware (hinges, handles, locks)
  - Installation services
  - Delivery fees
  - Holes/cutouts
  - Safety backing
  - Custom fabrication
- **Pricing methods**:
  - Fixed price (e.g., $50 per installation)
  - Per-inch (e.g., $2.50 per linear inch for sealing)
  - Per-sqft (e.g., $8 per sq ft for coating)
  - Percentage (e.g., 15% of glass cost for delivery)
- **Supplier tracking**: Internal cost vs customer price
- **Categories**: Organization and filtering
- **PDF Import** (AI-powered):
  - Upload supplier PDF catalog
  - Extract text using pdf-parse (Python: PyPDF2/pdfplumber)
  - Send to OpenAI API with structured prompt
  - Parse products with pricing
  - Preview extracted data
  - Bulk import to database

**AI Extraction Flow**:
```python
import anthropic
import pdfplumber

def extract_products_from_pdf(pdf_path):
    """Extract product data from PDF using Claude AI"""

    # 1. Extract text from PDF
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # 2. Send to Claude for structured extraction
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""
    Extract product information from this supplier catalog.

    For each product, extract:
    - Product name
    - Cost (our cost from supplier)
    - Category (hardware, service, material, etc.)
    - Pricing method (fixed, per-inch, per-sqft, percentage)
    - Unit (if applicable)

    Return as JSON array:
    [
      {{
        "name": "3/8\" Beveled Mirror",
        "cost": 45.50,
        "category": "mirror",
        "pricing_method": "per-sqft",
        "unit": "sqft"
      }},
      ...
    ]

    Catalog text:
    {text[:10000]}  # Limit to first 10k chars for API
    """

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    # 3. Parse JSON response
    import json
    products = json.loads(message.content[0].text)

    return products

def preview_import(products):
    """Show preview UI before importing"""
    return dmc.Table([
        html.Thead([
            html.Tr([
                html.Th(dmc.Checkbox(id='select-all')),
                html.Th("Name"),
                html.Th("Cost"),
                html.Th("Category"),
                html.Th("Pricing Method")
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(dmc.Checkbox(id={'type': 'select-product', 'index': i})),
                html.Td(p['name']),
                html.Td(f"${p['cost']:.2f}"),
                html.Td(p['category']),
                html.Td(p['pricing_method'])
            ])
            for i, p in enumerate(products)
        ])
    ])
```

#### B. Suppliers Management
**File Reference**: `client/src/pages/admin-suppliers.tsx`

**Features**:
- Supplier name, contact info
- Product associations
- Cost tracking
- Payment terms
- CRUD operations

#### C. Categories Management
**File Reference**: `client/src/pages/admin-categories.tsx`

**Features**:
- Product categories
- Inventory categories
- Wiki categories
- Color coding
- Sorting

#### D. Glass Pricing Configuration
**File Reference**: `client/src/pages/admin.tsx`

**Features**:
- **Base pricing table**: Glass type × thickness matrix
- **Polish pricing**: Per-inch rates by thickness
- **Beveled pricing**: Per-inch rates by thickness
- **Clipped corners pricing**: Per-corner rates by thickness
- **Markups**: Tempered percentage, shape percentage
- **Special rules**:
  - Only tempered flag (3/16" clear must be tempered)
  - No polish flag
  - Never tempered flag (mirrors)
- Inline editing with validation

**Database Schema**:
```sql
CREATE TABLE glass_config (
    id SERIAL PRIMARY KEY,
    thickness TEXT NOT NULL,  -- '1/8"', '3/16"', '1/4"', '3/8"', '1/2"'
    type TEXT NOT NULL,       -- 'clear', 'bronze', 'gray', 'mirror'
    base_price DECIMAL(10,2),
    polish_price DECIMAL(10,2),
    only_tempered BOOLEAN DEFAULT FALSE,
    no_polish BOOLEAN DEFAULT FALSE,
    never_tempered BOOLEAN DEFAULT FALSE,
    UNIQUE(thickness, type)
);

CREATE TABLE markups (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,         -- 'tempered', 'shape'
    percentage DECIMAL(5,2)
);

CREATE TABLE beveled_pricing (
    id SERIAL PRIMARY KEY,
    glass_thickness TEXT UNIQUE,
    price_per_inch DECIMAL(10,2)
);

CREATE TABLE clipped_corners_pricing (
    id SERIAL PRIMARY KEY,
    glass_thickness TEXT,
    clip_size TEXT,          -- 'under_1', 'over_1'
    price_per_corner DECIMAL(10,2),
    UNIQUE(glass_thickness, clip_size)
);
```

#### E. Wiki System
**File Reference**: `client/src/pages/wiki.tsx`, `client/src/pages/wiki-category.tsx`, `client/src/pages/wiki-article.tsx`

**Features**:
- Internal documentation and knowledge base
- Categories for organization
- Markdown article editing
- Search functionality
- Recent articles
- User contributions tracking

**Database Schema**:
```sql
CREATE TABLE wiki_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    color TEXT
);

CREATE TABLE wiki_articles (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES wiki_categories(id),
    title TEXT NOT NULL,
    content TEXT,
    author TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Database Schema

### Complete PostgreSQL Schema

```sql
-- Users (authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    replit_id TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    name TEXT,
    profile_image TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Glass Configuration
CREATE TABLE glass_config (
    id SERIAL PRIMARY KEY,
    thickness TEXT NOT NULL,
    type TEXT NOT NULL,
    base_price DECIMAL(10,2),
    polish_price DECIMAL(10,2),
    only_tempered BOOLEAN DEFAULT FALSE,
    no_polish BOOLEAN DEFAULT FALSE,
    never_tempered BOOLEAN DEFAULT FALSE,
    UNIQUE(thickness, type)
);

CREATE TABLE markups (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    percentage DECIMAL(5,2)
);

CREATE TABLE beveled_pricing (
    id SERIAL PRIMARY KEY,
    glass_thickness TEXT UNIQUE,
    price_per_inch DECIMAL(10,2)
);

CREATE TABLE clipped_corners_pricing (
    id SERIAL PRIMARY KEY,
    glass_thickness TEXT,
    clip_size TEXT,
    price_per_corner DECIMAL(10,2),
    UNIQUE(glass_thickness, clip_size)
);

-- Product Catalog
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    website TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE product_categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE product_catalog (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER REFERENCES product_categories(id),
    supplier_id INTEGER REFERENCES suppliers(id),
    cost DECIMAL(10,2),
    price DECIMAL(10,2),
    pricing_method TEXT CHECK (pricing_method IN ('fixed', 'per-inch', 'per-sqft', 'percentage')),
    unit TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Inventory
CREATE TABLE inventory_categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE inventory_units (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER REFERENCES inventory_categories(id),
    quantity DECIMAL(10,2),
    unit_id INTEGER REFERENCES inventory_units(id),
    cost_per_unit DECIMAL(10,2),
    supplier_id INTEGER REFERENCES suppliers(id),
    low_stock_threshold DECIMAL(10,2),
    sort_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Production Kanban
CREATE TABLE production_stages (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,
    color TEXT
);

CREATE TABLE production_jobs (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    stage_id INTEGER REFERENCES production_stages(id),
    due_date DATE,
    priority TEXT CHECK (priority IN ('low', 'medium', 'high')),
    assigned_to TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE production_notes (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES production_jobs(id) ON DELETE CASCADE,
    note TEXT NOT NULL,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- PO Tracker
CREATE TABLE po_clients (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    client_type TEXT,
    tags TEXT[],
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE po_purchase_orders (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES po_clients(id) ON DELETE CASCADE,
    po_number TEXT UNIQUE,
    status TEXT,
    total_amount DECIMAL(10,2),
    due_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE po_activities (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES po_clients(id),
    po_id INTEGER REFERENCES po_purchase_orders(id),
    activity_type TEXT,
    description TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Wiki
CREATE TABLE wiki_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    color TEXT
);

CREATE TABLE wiki_articles (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES wiki_categories(id),
    title TEXT NOT NULL,
    content TEXT,
    author TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Pricing Formulas (Future)
CREATE TABLE pricing_formulas (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT,
    formula TEXT,
    variables JSONB,
    description TEXT
);
```

---

## Python Calculation Modules

### Module 1: Fraction Utilities

**File**: `modules/fraction_utils.py`

```python
"""
Fraction and measurement utilities for glass calculations
Handles mixed numbers, fractions, and decimal conversions
"""

from fractions import Fraction
from typing import Union


def parse_measurement(input_str: str) -> Fraction:
    """
    Parse mixed numbers, fractions, or decimals

    Examples:
        "24 1/2" -> Fraction(49, 2)
        "3/4" -> Fraction(3, 4)
        "24.5" -> Fraction(49, 2)
        "24" -> Fraction(24, 1)

    Args:
        input_str: Input measurement string

    Returns:
        Fraction object

    Raises:
        ValueError: If input cannot be parsed
    """
    input_str = input_str.strip()

    if not input_str:
        raise ValueError("Empty input")

    # Mixed number: "24 1/2"
    if ' ' in input_str:
        parts = input_str.split()
        if len(parts) != 2:
            raise ValueError(f"Invalid mixed number format: {input_str}")

        whole = int(parts[0])
        frac = Fraction(parts[1])

        # Handle negative mixed numbers
        if whole < 0:
            return whole - frac
        return whole + frac

    # Fraction: "3/4"
    elif '/' in input_str:
        return Fraction(input_str)

    # Decimal: "24.5"
    elif '.' in input_str:
        return Fraction(float(input_str)).limit_denominator()

    # Whole number: "24"
    else:
        return Fraction(int(input_str))


def format_fraction(frac: Fraction, max_denominator: int = 16) -> str:
    """
    Format fraction as mixed number for display

    Examples:
        Fraction(49, 2) -> "24 1/2"
        Fraction(3, 4) -> "3/4"
        Fraction(24, 1) -> "24"

    Args:
        frac: Fraction to format
        max_denominator: Maximum denominator for simplification

    Returns:
        Formatted string
    """
    # Limit denominator for cleaner display
    frac = frac.limit_denominator(max_denominator)

    # Whole number
    if frac.denominator == 1:
        return str(frac.numerator)

    # Mixed number (>= 1)
    if abs(frac) >= 1:
        whole = int(frac)
        remainder = frac - whole

        if remainder == 0:
            return str(whole)

        # Handle negative
        if whole < 0:
            return f"{whole} {abs(remainder.numerator)}/{remainder.denominator}"

        return f"{whole} {remainder.numerator}/{remainder.denominator}"

    # Proper fraction (< 1)
    return f"{frac.numerator}/{frac.denominator}"


def to_decimal(input_str: str) -> float:
    """
    Convert measurement string to decimal

    Args:
        input_str: Measurement string (fraction, mixed, or decimal)

    Returns:
        Float value
    """
    frac = parse_measurement(input_str)
    return float(frac)


def validate_measurement(input_str: str) -> bool:
    """
    Validate if string is a valid measurement

    Args:
        input_str: Input string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        parse_measurement(input_str)
        return True
    except (ValueError, ZeroDivisionError):
        return False


# Example usage:
if __name__ == "__main__":
    # Test cases
    tests = [
        "24 1/2",
        "3/4",
        "24.5",
        "24",
        "-12 3/4"
    ]

    for test in tests:
        frac = parse_measurement(test)
        print(f"{test:>10} -> {format_fraction(frac):>10} = {float(frac):.4f}")
```

### Module 2: Glass Price Calculator

**File**: `modules/glass_calculator.py`

```python
"""
Glass pricing calculator module
Implements all pricing formulas from GlassPricePro
"""

from typing import Dict, Optional, Any
from decimal import Decimal
import math


class GlassPriceCalculator:
    """
    Calculate glass prices based on GlassPricePro formulas

    ULTIMATE FORMULA: Final Quote Price = Combined Cost ÷ 0.28
    """

    MINIMUM_SQ_FT = 3.0
    MARKUP_DIVISOR = 0.28

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize calculator with pricing configuration

        Args:
            config: Dict containing:
                - glass_config: Dict[str, Dict] - base and polish prices
                - markups: Dict[str, float] - tempered%, shape%
                - beveled_pricing: Dict[str, float] - rates by thickness
                - clipped_corners_pricing: Dict[str, Dict] - rates by thickness/size
        """
        self.config = config

    def calculate_square_footage(
        self,
        width: float,
        height: float,
        is_circular: bool = False,
        diameter: Optional[float] = None
    ) -> float:
        """
        Calculate square footage with minimum billable

        Args:
            width: Width in inches
            height: Height in inches
            is_circular: If true, calculate as circle
            diameter: Diameter in inches (for circular glass)

        Returns:
            Square footage (minimum 3 sq ft)
        """
        if is_circular and diameter:
            radius = diameter / 2
            sq_ft = (math.pi * radius ** 2) / 144
        else:
            sq_ft = (width * height) / 144

        return max(sq_ft, self.MINIMUM_SQ_FT)

    def calculate_perimeter(
        self,
        width: float,
        height: float,
        is_circular: bool = False,
        diameter: Optional[float] = None
    ) -> float:
        """
        Calculate perimeter in inches

        Args:
            width: Width in inches
            height: Height in inches
            is_circular: If true, calculate as circle
            diameter: Diameter in inches (for circular glass)

        Returns:
            Perimeter in inches
        """
        if is_circular and diameter:
            return math.pi * diameter
        else:
            return 2 * (width + height)

    def calculate_base_price(
        self,
        thickness: str,
        glass_type: str,
        sq_ft: float
    ) -> float:
        """
        Calculate base glass price

        Args:
            thickness: Glass thickness (e.g., "1/4\"")
            glass_type: Type of glass (clear, bronze, gray, mirror)
            sq_ft: Square footage

        Returns:
            Base price
        """
        key = f"{thickness}_{glass_type}"
        base_rate = self.config['glass_config'].get(key, {}).get('base_price', 0)
        return sq_ft * base_rate

    def calculate_polish_price(
        self,
        thickness: str,
        glass_type: str,
        perimeter: float,
        is_flat_polish: bool = False
    ) -> float:
        """
        Calculate edge polish price

        Args:
            thickness: Glass thickness
            glass_type: Type of glass
            perimeter: Perimeter in inches
            is_flat_polish: Use flat polish rate (mirrors)

        Returns:
            Polish price
        """
        if is_flat_polish:
            rate = 0.27  # Flat polish default
        else:
            key = f"{thickness}_{glass_type}"
            rate = self.config['glass_config'].get(key, {}).get('polish_price', 0)

        return perimeter * rate

    def calculate_beveled_price(
        self,
        thickness: str,
        perimeter: float
    ) -> float:
        """
        Calculate beveled edge price

        Not available for 1/8" glass

        Args:
            thickness: Glass thickness
            perimeter: Perimeter in inches

        Returns:
            Beveled price or 0 if not available
        """
        if thickness == '1/8"':
            return 0

        rate = self.config['beveled_pricing'].get(thickness, 0)
        return perimeter * rate

    def calculate_clipped_corners_price(
        self,
        thickness: str,
        num_corners: int,
        clip_size: str = 'under_1'
    ) -> float:
        """
        Calculate clipped corners price

        Args:
            thickness: Glass thickness
            num_corners: Number of corners (1-4)
            clip_size: 'under_1' or 'over_1' inch

        Returns:
            Clipped corners price
        """
        key = f"{thickness}_{clip_size}"
        rate = self.config['clipped_corners_pricing'].get(key, 0)
        return num_corners * rate

    def calculate_tempered_markup(
        self,
        before_markups: float,
        glass_type: str,
        force_tempered: bool = False
    ) -> float:
        """
        Calculate tempered glass markup

        Never applied to mirrors

        Args:
            before_markups: Base + edges price
            glass_type: Type of glass
            force_tempered: Force tempering regardless of config

        Returns:
            Tempered markup amount
        """
        if glass_type == 'mirror':
            return 0

        if not force_tempered:
            return 0

        tempered_percent = self.config['markups'].get('tempered', 0)
        return before_markups * (tempered_percent / 100)

    def calculate_shape_markup(
        self,
        before_markups: float,
        is_non_rectangular: bool = False,
        is_circular: bool = False
    ) -> float:
        """
        Calculate shape markup

        Args:
            before_markups: Base + edges price
            is_non_rectangular: Non-rectangular shape
            is_circular: Circular shape

        Returns:
            Shape markup amount
        """
        if not (is_non_rectangular or is_circular):
            return 0

        shape_percent = self.config['markups'].get('shape', 0)
        return before_markups * (shape_percent / 100)

    def calculate_contractor_discount(
        self,
        subtotal: float,
        is_contractor: bool = False
    ) -> float:
        """
        Calculate contractor discount (15%)

        Args:
            subtotal: Price before discount
            is_contractor: Apply contractor pricing

        Returns:
            Discount amount
        """
        if not is_contractor:
            return 0

        return subtotal * 0.15

    def calculate_quote(
        self,
        width: float,
        height: float,
        thickness: str,
        glass_type: str,
        quantity: int = 1,
        is_polished: bool = False,
        is_beveled: bool = False,
        num_clipped_corners: int = 0,
        clip_size: str = 'under_1',
        is_tempered: bool = False,
        is_non_rectangular: bool = False,
        is_circular: bool = False,
        diameter: Optional[float] = None,
        is_contractor: bool = False
    ) -> Dict[str, float]:
        """
        Calculate complete glass quote

        Args:
            width: Width in inches
            height: Height in inches
            thickness: Glass thickness
            glass_type: Type of glass
            quantity: Number of pieces
            is_polished: Apply polish
            is_beveled: Apply beveled edges
            num_clipped_corners: Number of clipped corners (0-4)
            clip_size: Clip size ('under_1' or 'over_1')
            is_tempered: Temper the glass
            is_non_rectangular: Non-rectangular shape
            is_circular: Circular glass
            diameter: Diameter for circular glass
            is_contractor: Apply contractor discount

        Returns:
            Dict with price breakdown:
                - base_price
                - polish_price (if applicable)
                - beveled_price (if applicable)
                - clipped_corners_price (if applicable)
                - before_markups
                - tempered_price (if applicable)
                - shape_price (if applicable)
                - subtotal
                - contractor_discount (if applicable)
                - discounted_subtotal (if applicable)
                - total (after quantity)
                - quote_price (total ÷ 0.28)
        """
        # Calculate dimensions
        sq_ft = self.calculate_square_footage(width, height, is_circular, diameter)
        perimeter = self.calculate_perimeter(width, height, is_circular, diameter)

        # Base price
        base_price = self.calculate_base_price(thickness, glass_type, sq_ft)

        # Edge processing
        polish_price = 0
        if is_polished:
            is_flat = (glass_type == 'mirror')
            polish_price = self.calculate_polish_price(thickness, glass_type, perimeter, is_flat)

        beveled_price = 0
        if is_beveled:
            beveled_price = self.calculate_beveled_price(thickness, perimeter)

        clipped_corners_price = 0
        if num_clipped_corners > 0:
            clipped_corners_price = self.calculate_clipped_corners_price(
                thickness, num_clipped_corners, clip_size
            )

        # Before markups subtotal
        before_markups = base_price + polish_price + beveled_price + clipped_corners_price

        # Markups
        tempered_price = self.calculate_tempered_markup(before_markups, glass_type, is_tempered)
        shape_price = self.calculate_shape_markup(before_markups, is_non_rectangular, is_circular)

        # Subtotal
        subtotal = before_markups + tempered_price + shape_price

        # Contractor discount
        contractor_discount = self.calculate_contractor_discount(subtotal, is_contractor)
        discounted_subtotal = subtotal - contractor_discount

        # Final total
        total = discounted_subtotal * quantity

        # Quote price (ULTIMATE FORMULA)
        quote_price = total / self.MARKUP_DIVISOR

        return {
            'sq_ft': round(sq_ft, 2),
            'perimeter': round(perimeter, 2),
            'base_price': round(base_price, 2),
            'polish_price': round(polish_price, 2) if polish_price > 0 else None,
            'beveled_price': round(beveled_price, 2) if beveled_price > 0 else None,
            'clipped_corners_price': round(clipped_corners_price, 2) if clipped_corners_price > 0 else None,
            'before_markups': round(before_markups, 2),
            'tempered_price': round(tempered_price, 2) if tempered_price > 0 else None,
            'shape_price': round(shape_price, 2) if shape_price > 0 else None,
            'subtotal': round(subtotal, 2),
            'contractor_discount': round(contractor_discount, 2) if contractor_discount > 0 else None,
            'discounted_subtotal': round(discounted_subtotal, 2) if contractor_discount > 0 else None,
            'total': round(total, 2),
            'quote_price': round(quote_price, 2)
        }


# Example usage:
if __name__ == "__main__":
    # Sample configuration
    config = {
        'glass_config': {
            '1/4"_clear': {'base_price': 12.50, 'polish_price': 0.85},
            '1/4"_bronze': {'base_price': 18.00, 'polish_price': 0.85},
            '1/4"_mirror': {'base_price': 15.00, 'polish_price': 0.27},
        },
        'markups': {
            'tempered': 35.0,  # 35%
            'shape': 25.0      # 25%
        },
        'beveled_pricing': {
            '1/4"': 2.01,
            '3/8"': 2.91,
            '1/2"': 3.80
        },
        'clipped_corners_pricing': {
            '1/4"_under_1': 5.50,
            '1/4"_over_1': 22.18,
        }
    }

    calc = GlassPriceCalculator(config)

    # Example quote: 24" x 36" clear glass, 1/4" thick, polished, tempered
    result = calc.calculate_quote(
        width=24,
        height=36,
        thickness='1/4"',
        glass_type='clear',
        quantity=1,
        is_polished=True,
        is_tempered=True,
        is_contractor=False
    )

    print("Glass Quote:")
    print(f"  Dimensions: 24\" x 36\" ({result['sq_ft']} sq ft)")
    print(f"  Base Price: ${result['base_price']:.2f}")
    print(f"  Polish: ${result['polish_price']:.2f}")
    print(f"  Tempered Markup: ${result['tempered_price']:.2f}")
    print(f"  Total: ${result['total']:.2f}")
    print(f"  QUOTE PRICE: ${result['quote_price']:.2f}")
```

### Module 3: Spacer Optimizer

**File**: `modules/spacer_optimizer.py`

```python
"""
Spacer cutting optimization module
Minimizes waste when cutting IGU spacers from stock
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class SpacerCut:
    """Represents a single spacer piece to be cut"""
    length: float  # inches
    quantity: int
    label: str  # e.g., "Section A - Window 1"


@dataclass
class CuttingStick:
    """Represents a stock stick with cuts"""
    cuts: List[float]
    remaining: float
    waste: float
    efficiency: float


class SpacerOptimizer:
    """
    Optimize spacer cutting to minimize waste
    Uses First-Fit-Decreasing bin packing algorithm
    """

    STICK_LENGTH = 152.0  # inches (standard stock length)
    BLADE_KERF = 0.125    # 1/8" kerf per cut

    def __init__(self, stick_length: float = STICK_LENGTH, blade_kerf: float = BLADE_KERF):
        """
        Initialize optimizer

        Args:
            stick_length: Length of stock sticks in inches
            blade_kerf: Width of saw blade cut in inches
        """
        self.stick_length = stick_length
        self.blade_kerf = blade_kerf

    def optimize(self, cuts: List[SpacerCut]) -> Tuple[List[CuttingStick], Dict]:
        """
        Optimize cutting pattern

        Args:
            cuts: List of SpacerCut objects

        Returns:
            Tuple of (sticks_list, summary_dict)
        """
        # Expand cuts by quantity and sort descending
        all_lengths = []
        for cut in cuts:
            all_lengths.extend([cut.length] * cut.quantity)

        all_lengths.sort(reverse=True)

        # First-Fit-Decreasing algorithm
        sticks = []

        for length in all_lengths:
            # Try to fit in existing stick
            placed = False
            for stick in sticks:
                space_needed = length + (self.blade_kerf if stick.cuts else 0)
                if stick.remaining >= space_needed:
                    stick.cuts.append(length)
                    stick.remaining -= space_needed
                    placed = True
                    break

            # Create new stick if needed
            if not placed:
                new_stick = CuttingStick(
                    cuts=[length],
                    remaining=self.stick_length - length,
                    waste=0,
                    efficiency=0
                )
                sticks.append(new_stick)

        # Calculate waste and efficiency
        total_used = 0
        total_waste = 0

        for stick in sticks:
            stick.waste = stick.remaining
            used = self.stick_length - stick.waste
            stick.efficiency = (used / self.stick_length) * 100
            total_used += used
            total_waste += stick.waste

        total_length = len(sticks) * self.stick_length
        overall_efficiency = (total_used / total_length) * 100 if total_length > 0 else 0

        summary = {
            'total_sticks': len(sticks),
            'total_length_used': round(total_used, 2),
            'total_waste': round(total_waste, 2),
            'efficiency_percent': round(overall_efficiency, 2),
            'total_pieces': len(all_lengths)
        }

        return sticks, summary

    def calculate_spacer_length(
        self,
        window_width: float,
        window_height: float
    ) -> float:
        """
        Calculate total spacer needed for one window

        Spacer forms a rectangle around the IGU

        Args:
            window_width: Window width in inches
            window_height: Window height in inches

        Returns:
            Total spacer length (perimeter)
        """
        return 2 * (window_width + window_height)

    def calculate_glass_dimensions(
        self,
        window_width: float,
        window_height: float,
        spacer_thickness: float
    ) -> Tuple[float, float]:
        """
        Calculate glass dimensions from window dimensions

        Glass is smaller than window by spacer thickness

        Args:
            window_width: Window width in inches
            window_height: Window height in inches
            spacer_thickness: Spacer bar thickness (e.g., 0.5 for 1/2")

        Returns:
            Tuple of (glass_width, glass_height)
        """
        glass_width = window_width - (spacer_thickness * 2)
        glass_height = window_height - (spacer_thickness * 2)
        return glass_width, glass_height


# Example usage:
if __name__ == "__main__":
    optimizer = SpacerOptimizer()

    # Example project: 3 windows
    cuts = [
        SpacerCut(length=48.5, quantity=4, label="Window 1 - 24x36"),
        SpacerCut(length=36.5, quantity=4, label="Window 2 - 18x30"),
        SpacerCut(length=42.0, quantity=4, label="Window 3 - 20x32"),
    ]

    sticks, summary = optimizer.optimize(cuts)

    print("Spacer Cutting Optimization Results")
    print("=" * 50)
    print(f"Total Sticks Required: {summary['total_sticks']}")
    print(f"Total Pieces: {summary['total_pieces']}")
    print(f"Total Length Used: {summary['total_length_used']}\"")
    print(f"Total Waste: {summary['total_waste']}\"")
    print(f"Efficiency: {summary['efficiency_percent']:.1f}%")
    print("\nCutting Plan:")
    print("=" * 50)

    for i, stick in enumerate(sticks, 1):
        print(f"\nStick #{i}:")
        print(f"  Cuts: {', '.join(f'{c:.2f}\"' for c in stick.cuts)}")
        print(f"  Waste: {stick.waste:.2f}\"")
        print(f"  Efficiency: {stick.efficiency:.1f}%")
```

---

## Dash Implementation Guide

### Project Structure

```
glassprice_dash/
├── app.py                          # Main Dash app
├── modules/
│   ├── __init__.py
│   ├── database.py                 # Database operations (PostgreSQL)
│   ├── fraction_utils.py           # Fraction parsing/formatting
│   ├── glass_calculator.py         # Pricing calculations
│   ├── spacer_optimizer.py         # Cutting optimization
│   └── pdf_extractor.py            # AI-powered PDF parsing
├── pages/
│   ├── __init__.py
│   ├── home.py                     # Dashboard
│   ├── calculator_v2.py            # Main glass calculator
│   ├── igu_calculator.py           # IGU calculator
│   ├── spacer_calculator.py        # Spacer optimization
│   ├── fraction_calculator.py      # Fraction arithmetic
│   ├── production_kanban.py        # Kanban board
│   ├── inventory.py                # Inventory management
│   ├── po_clients.py               # PO tracker - clients
│   ├── po_client_detail.py         # Client detail page
│   ├── po_detail.py                # PO detail page
│   ├── admin_pricing.py            # Pricing configuration
│   ├── admin_products.py           # Product catalog
│   ├── admin_suppliers.py          # Suppliers
│   └── wiki.py                     # Wiki system
├── components/
│   ├── __init__.py
│   ├── navbar.py                   # Navigation sidebar
│   ├── calculator_form.py          # Glass calc form
│   ├── price_display.py            # Price breakdown component
│   ├── job_card.py                 # Kanban job card
│   └── client_card.py              # Client card component
├── assets/
│   └── custom.css                  # Custom styles
├── requirements.txt
└── .env
```

### Dependencies

**requirements.txt**:
```txt
# Core Dash
dash==2.17.1
dash-mantine-components==0.14.3
dash-iconify==0.1.2

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# Data processing
pandas==2.1.4
numpy==1.26.2

# PDF processing
PyPDF2==3.0.1
pdfplumber==0.11.0

# AI integration
anthropic==0.8.1

# Utilities
python-dotenv==1.0.0
```

### Main Application Shell

**app.py**:
```python
"""
GlassPricePro - Dash Application
Main entry point
"""

import dash
from dash import Dash, html, dcc, Input, Output, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Dash app
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    title="GlassPricePro"
)

server = app.server

# Main layout
app.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "light",
        "primaryColor": "blue",
        "fontFamily": "Inter, sans-serif",
    },
    children=[
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='cart-store', data=[]),
        dcc.Store(id='user-store', data={}),

        dmc.AppShell(
            navbar={
                "width": 280,
                "breakpoint": "sm",
            },
            padding="md",
            children=[
                # Navbar
                dmc.Navbar(
                    width={"base": 280},
                    padding="md",
                    children=[
                        dmc.Stack([
                            # Logo
                            dmc.Group([
                                DashIconify(icon="solar:home-smile-angle-bold", width=32, color="#228be6"),
                                dmc.Stack([
                                    dmc.Text("GlassPricePro", size="xl", weight=700),
                                    dmc.Text("Island Glass & Mirror", size="xs", color="dimmed")
                                ], spacing=0)
                            ]),

                            dmc.Divider(),

                            # Calculators section
                            dmc.Text("Calculators", size="xs", color="dimmed", weight=500),
                            dmc.NavLink(
                                label="Glass Calculator",
                                icon=DashIconify(icon="solar:calculator-bold"),
                                href="/calculator",
                            ),
                            dmc.NavLink(
                                label="IGU Calculator",
                                icon=DashIconify(icon="solar:layers-bold"),
                                href="/igu-calculator",
                            ),
                            dmc.NavLink(
                                label="Spacer Calculator",
                                icon=DashIconify(icon="solar:ruler-bold"),
                                href="/spacer-calculator",
                            ),
                            dmc.NavLink(
                                label="Fraction Calculator",
                                icon=DashIconify(icon="solar:calculator-minimalistic-bold"),
                                href="/fraction-calculator",
                            ),

                            dmc.Divider(),

                            # Management section
                            dmc.Text("Management", size="xs", color="dimmed", weight=500),
                            dmc.NavLink(
                                label="Production Kanban",
                                icon=DashIconify(icon="solar:widget-bold"),
                                href="/production",
                            ),
                            dmc.NavLink(
                                label="Inventory",
                                icon=DashIconify(icon="solar:box-bold"),
                                href="/inventory",
                            ),
                            dmc.NavLink(
                                label="PO Tracker",
                                icon=DashIconify(icon="solar:document-text-bold"),
                                href="/po-tracker",
                            ),

                            dmc.Divider(),

                            # Admin section
                            dmc.Text("Admin", size="xs", color="dimmed", weight=500),
                            dmc.NavLink(
                                label="Pricing Config",
                                icon=DashIconify(icon="solar:settings-bold"),
                                href="/admin/pricing",
                            ),
                            dmc.NavLink(
                                label="Products",
                                icon=DashIconify(icon="solar:tag-bold"),
                                href="/admin/products",
                            ),
                            dmc.NavLink(
                                label="Wiki",
                                icon=DashIconify(icon="solar:book-bold"),
                                href="/wiki",
                            ),
                        ], spacing="xs")
                    ]
                ),

                # Main content
                dmc.Container(
                    id='page-content',
                    size="xl",
                    style={"paddingTop": 20}
                )
            ]
        )
    ]
)

# Routing
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/' or pathname == '/calculator':
        from pages import calculator_v2
        return calculator_v2.layout
    elif pathname == '/igu-calculator':
        from pages import igu_calculator
        return igu_calculator.layout
    elif pathname == '/spacer-calculator':
        from pages import spacer_calculator
        return spacer_calculator.layout
    elif pathname == '/fraction-calculator':
        from pages import fraction_calculator
        return fraction_calculator.layout
    elif pathname == '/production':
        from pages import production_kanban
        return production_kanban.layout
    elif pathname == '/inventory':
        from pages import inventory
        return inventory.layout
    elif pathname == '/po-tracker':
        from pages import po_clients
        return po_clients.layout
    elif pathname == '/admin/pricing':
        from pages import admin_pricing
        return admin_pricing.layout
    elif pathname == '/admin/products':
        from pages import admin_products
        return admin_products.layout
    elif pathname == '/wiki':
        from pages import wiki
        return wiki.layout
    else:
        return dmc.Text("404 - Page not found", color="red", size="xl")

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
```

---

## Phase-by-Phase Build Plan

### Phase 1: Foundation (8-10 hours)

**Goal**: Set up infrastructure and build core glass calculator

#### Tasks:

1. **Project Setup** (2 hours)
   - Create project structure
   - Install dependencies
   - Set up PostgreSQL database
   - Create database tables
   - Test connection

2. **Build Main App Shell** (2 hours)
   - Create `app.py` with navigation
   - Build navbar component
   - Set up routing
   - Test page navigation

3. **Fraction Utilities Module** (1 hour)
   - Implement `fraction_utils.py`
   - Test parsing and formatting
   - Integrate with Dash inputs

4. **Glass Calculator Module** (2 hours)
   - Implement `glass_calculator.py`
   - Test all calculation formulas
   - Verify against original app

5. **Glass Calculator Page** (3 hours)
   - Build form with all inputs
   - Connect to calculation module
   - Display price breakdown
   - Add to cart functionality

**Deliverable**: Working glass calculator with accurate pricing

---

### Phase 2: Additional Calculators (10-12 hours)

**Goal**: Build IGU, Spacer, and Fraction calculators

#### Tasks:

1. **IGU Calculator** (4 hours)
   - Build IGU pricing module
   - Create IGU calculator page
   - Add muntin options
   - Tempered/Low-E options

2. **Spacer Calculator** (4 hours)
   - Implement `spacer_optimizer.py`
   - Build spacer calculator page
   - Multi-section input
   - Cutting optimization display
   - Glass sheet optimization

3. **Fraction Calculator** (2 hours)
   - Build simple fraction arithmetic page
   - Add/subtract/multiply/divide
   - Real-time calculation

**Deliverable**: All 5 calculators functional

---

### Phase 3: Data Management (12-15 hours)

**Goal**: Build PO Tracker, Inventory, Production Kanban

#### Tasks:

1. **Database Module** (2 hours)
   - Create `database.py`
   - CRUD operations for all tables
   - Connection pooling

2. **Inventory Page** (3 hours)
   - Build inventory table
   - Add/edit/delete items
   - Low stock alerts
   - Drag-to-reorder (optional)

3. **PO Tracker - Clients** (4 hours)
   - Client cards/list view
   - Search and filters
   - Add/edit/delete clients

4. **PO Tracker - Detail Pages** (3 hours)
   - Client detail page
   - PO detail page
   - Activity logging

5. **Production Kanban** (4 hours)
   - Build kanban board
   - Job cards
   - Drag-drop between stages
   - Notes system

**Deliverable**: Complete CRM and production management

---

### Phase 4: Admin Tools (10-12 hours)

**Goal**: Pricing configuration, product catalog, PDF import

#### Tasks:

1. **Pricing Configuration Page** (3 hours)
   - Glass config table (inline editing)
   - Markups configuration
   - Beveled/clipped corners pricing

2. **Product Catalog** (3 hours)
   - Product CRUD
   - Supplier management
   - Category management
   - Pricing method selection

3. **PDF Import with AI** (4 hours)
   - PDF upload component
   - Text extraction (pdfplumber)
   - Claude AI integration
   - Preview and import

4. **Suppliers & Categories** (2 hours)
   - Supplier management page
   - Category management page

**Deliverable**: Complete admin system

---

### Phase 5: Advanced Features (8-10 hours)

**Goal**: PDF generation, Wiki, polish features

#### Tasks:

1. **Quote PDF Generation** (4 hours)
   - Use ReportLab or WeasyPrint
   - Generate PDF with CAD drawing
   - Price breakdown display
   - Download functionality

2. **Wiki System** (3 hours)
   - Wiki categories
   - Article CRUD
   - Markdown editing
   - Search

3. **Shopping Cart System** (2 hours)
   - Add items from calculators
   - Cart display
   - Edit quantities
   - Generate multi-item quote

**Deliverable**: Complete feature parity

---

### Phase 6: Polish & Testing (5-8 hours)

**Goal**: Refinement, responsive design, testing

#### Tasks:

1. **Responsive Design** (2 hours)
   - Test on mobile/tablet
   - Adjust layouts
   - Fix breakpoints

2. **User Testing** (2 hours)
   - Test all features
   - Fix bugs
   - Performance optimization

3. **Documentation** (2 hours)
   - User guide
   - Admin documentation
   - Code comments

4. **Deployment** (2 hours)
   - Production config
   - Environment variables
   - Deploy to hosting

**Deliverable**: Production-ready application

---

## Component Mapping Reference

### React → Dash Mantine

| React/Shadcn Component | Dash Mantine Equivalent | Notes |
|------------------------|------------------------|-------|
| `<Input>` | `dmc.TextInput()` | Similar props |
| `<Select>` | `dmc.Select()` | Use `data` for options |
| `<Button>` | `dmc.Button()` | Use `variant` prop |
| `<Card>` | `dmc.Card()` | Use `withBorder`, `shadow` |
| `<Dialog>` | `dmc.Modal()` | Use `opened` state |
| `<Tabs>` | `dmc.Tabs()` | Similar structure |
| `<Table>` | `dmc.Table()` | Use `striped`, `highlightOnHover` |
| `<Badge>` | `dmc.Badge()` | Use `color`, `variant` |
| `<Checkbox>` | `dmc.Checkbox()` | Similar |
| `<RadioGroup>` | `dmc.RadioGroup()` | Use `children` with `dmc.Radio()` |
| `<Textarea>` | `dmc.Textarea()` | Similar |
| `<Switch>` | `dmc.Switch()` | Similar |
| `<Slider>` | `dmc.Slider()` | Similar |
| `<Accordion>` | `dmc.Accordion()` | Similar structure |
| `<Alert>` | `dmc.Alert()` | Use `icon`, `color` |
| Drag & Drop (@dnd-kit) | `dash-draggable` or custom callbacks | More complex in Dash |

### Patterns

**React Hook Form + Zod → Dash Callbacks**:
```python
# React pattern:
const form = useForm({ resolver: zodResolver(schema) })
const onSubmit = (data) => { ... }

# Dash pattern:
@callback(
    Output('form-result', 'children'),
    Input('submit-btn', 'n_clicks'),
    State('input-1', 'value'),
    State('input-2', 'value'),
    prevent_initial_call=True
)
def handle_submit(n_clicks, input1, input2):
    # Validation
    if not input1 or not input2:
        return dmc.Notification(
            title="Error",
            message="All fields required",
            color="red"
        )

    # Process
    result = do_something(input1, input2)
    return dmc.Notification(
        title="Success",
        message="Saved!",
        color="green"
    )
```

**React Query → Dash Stores + Callbacks**:
```python
# React pattern:
const { data, isLoading } = useQuery(['key'], fetchFn)

# Dash pattern:
dcc.Store(id='data-store', data=[])
dcc.Interval(id='refresh-interval', interval=60000)  # 1 min

@callback(
    Output('data-store', 'data'),
    Input('refresh-interval', 'n_intervals')
)
def fetch_data(n):
    return fetch_from_database()

@callback(
    Output('display', 'children'),
    Input('data-store', 'data')
)
def display_data(data):
    if not data:
        return dmc.Loader()
    return create_table(data)
```

---

## Quick Start Checklist

### Before You Begin

- [ ] Read through this entire guide
- [ ] Set up PostgreSQL database
- [ ] Create `.env` file with:
  ```
  DATABASE_URL=postgresql://user:pass@localhost/glassprice
  ANTHROPIC_API_KEY=your_key_here
  ```
- [ ] Install Python 3.11+
- [ ] Create virtual environment

### First Session (Phase 1, Task 1-2)

1. Create project directory
2. Install dependencies: `pip install -r requirements.txt`
3. Create database tables (use schema from this guide)
4. Create `app.py` with basic shell
5. Test that app runs: `python app.py`
6. Access at `http://localhost:8050`

### First Goal

Get the basic navigation working and one calculator (Glass Calculator) functional within 4-6 hours.

---

## Success Criteria

### Must Have (MVP)

- ✅ Glass Calculator V2 with accurate pricing
- ✅ IGU Calculator functional
- ✅ Spacer Calculator with optimization
- ✅ Production Kanban with drag-drop
- ✅ Inventory management
- ✅ PO Tracker basic functionality
- ✅ Admin pricing configuration

### Should Have

- ✅ All 5 calculators complete
- ✅ PDF import with AI extraction
- ✅ Quote PDF generation
- ✅ Wiki system
- ✅ Shopping cart

### Nice to Have

- 🎯 Real-time collaboration
- 🎯 Advanced reporting
- 🎯 Email integration
- 🎯 Mobile app (Dash Mobile)

---

## Tips for Claude Code

1. **Start Simple**: Build one feature at a time, test thoroughly
2. **Use the Modules**: The Python modules in this guide are production-ready
3. **Follow the Schema**: Database schema is proven and complete
4. **Test Calculations**: Verify all pricing formulas against examples
5. **Dash Patterns**: Use pattern matching callbacks (`MATCH`, `ALL`) for dynamic lists
6. **Responsive**: Always test on mobile - use Mantine's responsive props
7. **Error Handling**: Validate all user inputs, especially measurements
8. **Performance**: Use `dcc.Store` for client-side caching, minimize database calls

---

## Questions to Resolve

Before starting, clarify:

1. **Authentication**: What auth system? (Replit Auth, custom, none?)
2. **Hosting**: Where will this be deployed? (Railway, Heroku, self-hosted?)
3. **Users**: How many concurrent users expected?
4. **Design**: Any specific branding/color preferences?
5. **Features**: Any features to skip or prioritize differently?

---

**Ready to build when you are!** 🚀

This guide contains everything needed to recreate GlassPricePro in Dash Mantine. Start with Phase 1, Task 1, and work through systematically. The Python modules are ready to use, the database schema is complete, and the Dash patterns are proven.

Good luck! 🥋
