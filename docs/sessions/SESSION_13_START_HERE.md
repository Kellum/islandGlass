# Session 13 - Start Here 👈

**Previous Session:** Session 12 - Backend & Forms Complete
**Current Status:** 70% Complete - Need 2 UI Pages + Integration
**Estimated Time:** 3-4 hours to completion

---

## 📖 Before You Begin

**Read in this order:**
1. **THIS FILE** ← You're here
2. `SESSION_12_CHECKPOINT.md` - Full session 12 details (if needed)

---

## ✅ What's Already Done

**Backend (100% Complete):**
- ✅ SQL migrations ready (3 files)
- ✅ Python modules created (permissions, ZPL, printer, database)
- ✅ 16 database methods for window system
- ✅ PO Clients form enhanced (dynamic fields + multiple contacts)
- ✅ Window Order Entry page (full-featured multi-window form)

**Server Status:**
- Dash app should be running on http://localhost:8050
- If not, restart with: `python3 dash_app.py`

---

## 🎯 Today's Objectives

### Create 2 Remaining Pages (3-4 hours)

1. **Window Order Management Page** (1.5-2 hrs)
   - File: `pages/window_order_management.py`
   - View all orders in table/card layout
   - Filters: Date, PO, Status, Window type
   - Expandable details showing window items
   - Status update dropdown
   - "View Labels" button

2. **Label Printing Page** (1.5-2 hrs)
   - File: `pages/window_label_printing.py`
   - Print queue grouped by PO
   - Individual label cards
   - Print buttons (single, batch, all)
   - Label preview modal
   - Print history section
   - Printer status indicator

3. **Integration** (30 min)
   - Update `dash_app.py` with navigation
   - Add role-based menu items
   - Test page routing

4. **Database Setup** (5 min)
   - Run 3 SQL migrations in Supabase

5. **Testing** (30-60 min)
   - Follow test checklist
   - Create sample orders
   - Test label generation
   - Verify role-based access

---

## 🚀 Quick Start Commands

```bash
# Check if server is running
ps aux | grep dash_app

# Start server if needed
python3 dash_app.py

# Kill old servers if needed
pkill -f dash_app.py

# Navigate to pages
open http://localhost:8050/window-order-entry
open http://localhost:8050/po-clients
```

---

## 📂 Key Files Reference

### SQL Migrations (Run in Order)
```
1. add_user_roles_and_departments.sql
2. window_manufacturing_schema.sql
3. window_manufacturing_seed_data.sql
```

### Python Modules (Already Created)
```
modules/permissions.py       - Role-based access control
modules/zpl_generator.py     - Label ZPL code generation
modules/label_printer.py     - Printer communication (mock mode)
modules/database.py          - 16 window methods added
modules/fraction_utils.py    - Measurement parsing (existing)
```

### UI Pages
```
✅ pages/po_clients.py              - Enhanced with dynamic forms
✅ pages/window_order_entry.py      - Order creation form
⏳ pages/window_order_management.py - Need to create
⏳ pages/window_label_printing.py   - Need to create
```

### Documentation
```
SESSION_12_CHECKPOINT.md         - Full session 12 details
SESSION_13_START_HERE.md         - This file
SESSION_11_WINDOW_MANUFACTURING_PLAN.md - Original spec
```

---

## 🔍 Implementation Patterns

### Pattern 1: Database Methods to Use

```python
from modules.database import get_authenticated_db

# In callbacks:
db = get_authenticated_db(session_data)
company_id = session_data.get('user_profile', {}).get('company_id')
user_id = session_data.get('user', {}).get('id')

# Get orders
orders = db.get_window_orders(company_id, status="pending")

# Get order details
order = db.get_window_order_by_id(order_id)
items = db.get_window_order_items(order_id)

# Get labels
labels = db.get_labels_for_order(order_id)
pending = db.get_pending_labels(company_id)

# Update status
db.update_window_order_status(order_id, "in_production", user_id)

# Print label
db.update_label_print_status(label_id, "printed", user_id, zpl_code)
```

### Pattern 2: Permissions Check

```python
from modules.permissions import get_user_window_permissions

# In page or callback:
user_profile = session_data.get('user_profile', {})
perms = get_user_window_permissions(user_profile)

if not perms.can_manage_orders():
    return "Access Denied"

if perms.can_print_labels():
    # Show print controls
```

### Pattern 3: Label Generation & Printing

```python
from modules.zpl_generator import ZPLGenerator
from modules.label_printer import LabelPrinter

# Generate ZPL
generator = ZPLGenerator()
zpl = generator.generate_window_label(
    po_number="2024-11-001",
    window_data={
        'thickness': 1.5,
        'width': 36,
        'height': 48,
        'window_type': 'Rectangle'
    },
    label_number=1,
    total_labels=4
)

# Print (mock mode)
printer = LabelPrinter(mock_mode=True)
success, message = printer.print_label(zpl, filename="label_001")
```

### Pattern 4: Fraction Display

```python
from modules.fraction_utils import format_fraction
from fractions import Fraction

# Convert decimal to fraction for display
thickness = 1.5  # From database
frac = Fraction(thickness).limit_denominator(16)
display = format_fraction(frac)  # Returns "1 1/2"
```

---

## 📋 Page 1: Order Management Layout Outline

```python
layout = dmc.Stack([
    # Header
    dmc.Title("Order Management"),

    # Filters Card
    dmc.Card([
        dmc.Grid([
            dmc.TextInput(id="search-po"),      # PO search
            dmc.Select(id="filter-status"),     # Status filter
            dmc.DateRangePicker(id="filter-date"), # Date range
        ])
    ]),

    # Orders Table/Cards
    html.Div(id="orders-container"),
])

# Callbacks needed:
@callback(Output("orders-container"), Input("filter-status"))
def load_orders(status):
    orders = db.get_window_orders(company_id, status)
    # Render as cards with expandable details

@callback(Output("order-status"), Input("status-dropdown"))
def update_status(new_status):
    db.update_window_order_status(order_id, new_status, user_id)
```

---

## 📋 Page 2: Label Printing Layout Outline

```python
layout = dmc.Stack([
    # Header with printer status
    dmc.Group([
        dmc.Title("Label Printing"),
        dmc.Badge(id="printer-status", children="Online")
    ]),

    # Print Queue Card
    dmc.Card([
        dmc.Text("Print Queue"),
        dmc.Accordion(id="labels-by-po")  # Group by PO
    ]),

    # Actions
    dmc.Group([
        dmc.Button("Print Selected"),
        dmc.Button("Print All Pending"),
        dmc.Button("Test Printer")
    ]),

    # Print History
    html.Div(id="print-history"),
])

# Callbacks needed:
@callback(Output("labels-by-po"), Input("page-load"))
def load_print_queue():
    labels = db.get_pending_labels(company_id)
    # Group by PO and render accordion

@callback(Input("print-button"), State("label-id"))
def print_label(label_id):
    label = db.get_label_by_id(label_id)
    # Generate ZPL and print
    # Update print status
```

---

## 🧪 Testing Checklist

After creating pages:

### 1. Database Migrations
- [ ] Run SQL files in Supabase (in order)
- [ ] Verify tables exist
- [ ] Check RLS policies active

### 2. Order Management Page
- [ ] Navigate to /window-order-management
- [ ] See list of orders (if any exist)
- [ ] Filter by status
- [ ] Expand order details
- [ ] Change status
- [ ] Click "View Labels" button

### 3. Label Printing Page
- [ ] Navigate to /window-label-printing
- [ ] See pending labels grouped by PO
- [ ] Print single label (check .zpl file created)
- [ ] Print batch
- [ ] Check print history updates

### 4. Navigation
- [ ] Window menu items appear
- [ ] Correct pages visible based on role
- [ ] Links work correctly

### 5. End-to-End Flow
- [ ] Create order via Order Entry
- [ ] View order in Order Management
- [ ] See labels in Print Queue
- [ ] Print labels
- [ ] Verify status updates

---

## 🐛 Common Issues & Solutions

### Issue: "Module not found" errors
**Solution:** Check imports at top of file
```python
from modules.database import get_authenticated_db
from modules.permissions import get_user_window_permissions
```

### Issue: Database queries return empty
**Solution:** Check RLS policies - need authenticated session
```python
db = get_authenticated_db(session_data)  # Use this, not Database()
```

### Issue: Labels not generating
**Solution:** Check that window items were created
```python
items = db.get_window_order_items(order_id)
print(f"Found {len(items)} items")
```

### Issue: Printer "errors"
**Solution:** Mock mode is expected - check `labels_output/` folder for .zpl files
```python
printer = LabelPrinter(mock_mode=True)  # This is correct for development
```

### Issue: Navigation not showing
**Solution:** Check user has correct role
```python
user_profile = session_data.get('user_profile', {})
print(f"Role: {user_profile.get('role')}")
```

---

## 📦 Output Directory

When printing labels in mock mode:
```
labels_output/
├── label_20241104_120000.zpl
├── batch_20241104_120100_label001.zpl
└── batch_20241104_120100_label002.zpl
```

Each .zpl file contains ZPL code that can be:
- Sent to actual Zebra printer
- Previewed at labelary.com/viewer.html
- Stored for reprinting

---

## 🎯 Success Criteria

**Minimum to Complete:**
- [ ] Both pages created and functional
- [ ] Navigation integrated
- [ ] Database migrations run
- [ ] Can create order end-to-end
- [ ] Can view orders and labels
- [ ] Can print labels (mock mode)

**Bonus if Time Permits:**
- [ ] Add edit order functionality
- [ ] Add label reprint from history
- [ ] Add advanced filtering
- [ ] Link customers to po_clients

---

## 💡 Tips for Efficiency

1. **Copy patterns from window_order_entry.py**
   - Already has good callback structure
   - Reuse card layouts and styles

2. **Use existing components**
   - DashIconify for icons
   - dmc.Card for containers
   - dmc.Accordion for expandable sections

3. **Test incrementally**
   - Create page skeleton first
   - Add one callback at a time
   - Test each feature before moving on

4. **Don't overthink UI**
   - Simple tables/cards work fine
   - Focus on functionality over polish
   - Can improve styling later

---

## 🔗 Useful Links

**Dash Mantine Components:**
- https://dash-mantine-components.com/

**ZPL Viewer (for testing labels):**
- http://labelary.com/viewer.html

**Documentation:**
- See SESSION_12_CHECKPOINT.md for full technical details
- See SESSION_11_WINDOW_MANUFACTURING_PLAN.md for original spec

---

**Ready to Build!** 🚀

Start with Order Management page, then Label Printing, then integrate navigation. You've got this!

**Estimated Time Remaining:** 3-4 hours to MVP completion
