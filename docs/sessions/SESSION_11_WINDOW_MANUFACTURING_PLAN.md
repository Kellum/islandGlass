# Session 11 - Window Manufacturing System Planning

## Overview
Planning session for building a complete window ordering and Zebra label printing system integrated into Island Glass Leads app.

---

## Business Requirements (Clarified Session 11)

### User Access Hierarchy

**Role-Based Access Control:**

1. **Super Admin (Owners)**
   - Access: EVERYTHING app-wide
   - CRM, GlassPricePro, Window Manufacturing (all features)

2. **IG Manufacturing Admin**
   - Access: All window manufacturing features + potentially other sections
   - Can view: Order Entry, Order Management, Label Printing
   - Full window system access

3. **IG Admin**
   - Access: Everything EXCEPT IG Manufacturing features
   - Cannot see window ordering/management/printing

4. **IG Employee (General)**
   - Access: Window Order Entry ONLY
   - Can submit window orders
   - Cannot see order management or label printing

5. **Sales** (Future Phase)
   - Access: Contractor dashboard + PO/Client tracker only
   - No window manufacturing access

**Implementation:**
- Use existing `user_profiles` table which already has `role` column
- Add `department` column for additional granularity
- Combo approach: `role` + `department` for flexible access control

---

## System Requirements

### Window Order Entry (All IG Employees)

**Form Features:**
- PO Number field with intelligent autocomplete
  - Fuzzy matching against existing POs
  - "Did you mean: PO:01-smith.Johns?" suggestions
  - Can select existing or create new

- Customer/Client selection
  - Dropdown of existing customers (will integrate QuickBooks API later)
  - Search with autocomplete
  - Option to add new customer
  - Link to existing `po_clients` table (optional FK)

- Dynamic Window Line Items
  - Window Type dropdown: Rectangle, Arch, Half Moon, Triangle, Circle, Oval, Pentagon, Hexagon, Octagon, Trapezoid, Custom Shape, etc.
  - Thickness input (fraction support required)
  - Width input (fraction support required)
  - Height input (fraction support required)
  - Quantity field (how many identical windows)
  - Shape notes/description (for custom shapes)

- Multi-Window Order Building
  - "Add Another Window" button
  - Display running list of all windows in order
  - Edit/remove individual window line items
  - Visual summary of total windows

- Order Review & Submit
  - Review all windows before submission
  - Show total window count
  - Confirmation notification

**Example Workflow:**
```
PO: 2024-11-001
Customer: ABC Construction

Add Window 1:
  - Type: Rectangle
  - Thickness: 1 1/2"
  - Width: 36"
  - Height: 48"
  - Quantity: 4

Add Window 2:
  - Type: Rectangle
  - Thickness: 1 1/2"
  - Width: 30"
  - Height: 60"
  - Quantity: 2

Add Window 3:
  - Type: Half Moon
  - Thickness: 1 1/2"
  - Width: 42"
  - Height: 42"
  - Quantity: 1

Total: 7 windows under one PO
```

---

### Order Management Dashboard (Manufacturing Admin Only)

**Features:**
- View all submitted orders in table/card layout
- Order information displayed:
  - PO Number
  - Customer name
  - Total window count
  - Submission date
  - Status (Pending / In Production / Printed / Completed)

- Expandable order details
  - Click to see all window line items
  - Full specifications for each window type

- Filtering & Search
  - Filter by: Date range, PO number, Status, Window shape
  - Search bar for quick lookup

- Bulk Actions
  - Mark orders as printed/completed
  - Update status for individual windows

- Navigation
  - "View Labels" button → redirects to print queue

---

### Label Printing System (Manufacturing Admin Only)

**Core Functionality:**

**Label Generation:**
- Automatic label generation based on quantity
  - 4 windows ordered = 4 physical labels generated
  - Each label uniquely numbered: "Window 1 of 4", "Window 2 of 4", etc.

**Print Queue:**
- Display all pending labels
- Group by PO number (expandable)
- Show label details:
  - PO Number
  - Window dimensions: "1.5 x 36 x 48"
  - Window shape/type
  - Label number of total
  - Order date

**Label Preview:**
- Preview individual labels before printing
- Visual representation of ZPL output

**Printing Options:**
- Print individual label
- Print all labels for specific PO
- Print selected labels (checkbox selection)
- Print all pending labels (batch)
- Download .zpl files (individual or batch)

**Print History:**
- Track which labels printed
- Timestamp and user who printed
- Status tracking per label
- Reprint capability

**Printer Configuration:**
- Select active printer from list
- Configure printer connection (IP address, port)
- Test print functionality
- Printer status indicator

---

## Technical Requirements

### Measurements
- **Units:** Inches always
- **Format:** Must support fractions (use existing `modules/fraction_utils.py`)
  - Parse inputs: "36 1/2", "3/4", "48.5"
  - Store as decimal in database
  - Display as fractions in labels
- **Order:** Thickness < Width < Height (glazing industry standard)

### Label Specifications
- **Printer:** Zebra ZD421
- **Current Label Size:** 3x2 inches (configurable for future)
- **Label Content:**
  - PO Number (prominent, large font)
  - Window dimensions: "Thickness x Width x Height"
  - Window shape/type
  - Label numbering: "Window X of Y"
  - Order date
  - Optional: Barcode of PO number (Code 128)

### ZPL Generation
- Create Python module: `modules/zpl_generator.py`
- Generate ZPL (Zebra Programming Language) code
- Handle different label sizes
- Support special characters and fractions
- Clear, readable format for manufacturing floor

### Printing
- Create Python module: `modules/label_printer.py`
- Network printing capability (IP-based connection)
- Mock/simulation mode (no physical printer needed for development)
- File download capability (.zpl files)
- Error handling for connection issues

---

## Database Schema

### New Tables

#### 1. window_orders
```sql
id (SERIAL PRIMARY KEY)
po_number (TEXT NOT NULL, unique per company)
customer_name (TEXT NOT NULL)
customer_id (INTEGER, FK to po_clients, NULLABLE)
order_date (TIMESTAMP DEFAULT NOW())
status (TEXT: 'pending', 'in_production', 'printed', 'completed')
notes (TEXT)
total_windows (INTEGER, calculated)

-- Standard company-scoped audit trail
company_id (UUID NOT NULL, FK to companies)
created_by (UUID, FK to auth.users)
updated_by (UUID, FK to auth.users)
deleted_by (UUID, FK to auth.users)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
deleted_at (TIMESTAMP)
```

#### 2. window_order_items
```sql
id (SERIAL PRIMARY KEY)
order_id (INTEGER, FK to window_orders)
window_type (TEXT: 'Rectangle', 'Arch', 'Half Moon', 'Triangle', etc.)
thickness (NUMERIC, stored as decimal)
width (NUMERIC, stored as decimal)
height (NUMERIC, stored as decimal)
quantity (INTEGER NOT NULL, how many identical windows)
shape_notes (TEXT, for custom shapes)

-- Standard company-scoped audit trail
company_id (UUID NOT NULL, FK to companies)
created_by (UUID, FK to auth.users)
updated_by (UUID, FK to auth.users)
deleted_by (UUID, FK to auth.users)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
deleted_at (TIMESTAMP)
```

#### 3. window_labels
```sql
id (SERIAL PRIMARY KEY)
order_item_id (INTEGER, FK to window_order_items)
label_number (INTEGER, which label in sequence: 1 of 4, 2 of 4, etc.)
zpl_code (TEXT, generated ZPL for reprinting)
print_status (TEXT: 'pending', 'printed', 'reprinted')
printed_at (TIMESTAMP)
printed_by (UUID, FK to auth.users)

-- Standard company-scoped audit trail
company_id (UUID NOT NULL, FK to companies)
created_by (UUID, FK to auth.users)
created_at (TIMESTAMP)
```

#### 4. label_printer_config
```sql
id (SERIAL PRIMARY KEY)
name (TEXT NOT NULL)
ip_address (TEXT)
port (INTEGER DEFAULT 9100)
label_width (NUMERIC, in inches)
label_height (NUMERIC, in inches)
is_active (BOOLEAN DEFAULT TRUE)
is_default (BOOLEAN DEFAULT FALSE)

-- Standard company-scoped audit trail
company_id (UUID NOT NULL, FK to companies)
created_by (UUID, FK to auth.users)
updated_by (UUID, FK to auth.users)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**All tables:**
- RLS policies filtering by `company_id`
- Soft delete support (deleted_at column)
- Audit trail (created_by, updated_by, deleted_by)

---

## Integration Points

### PO/Customer System
- **Current State:** `po_clients` table exists with client_name and contacts
- **Integration:**
  - Window orders can optionally link to `po_clients.id`
  - Not required (sister company might not be in CRM)
  - Allow manual customer name entry if not linked

### QuickBooks Integration
- **Phase:** Placeholder for now
- **Future:**
  - Sync customers from QuickBooks API
  - Flag: `po_clients.synced_from_qb` (boolean)
  - Auto-populate customer dropdown
  - Cross-reference PO numbers
- **Current:** Build structure to support it, use mock data

### Existing Fraction Utils
- **Module:** `modules/fraction_utils.py` already exists
- **Usage:** Reuse for window measurements
- **Verify:** Ensure it handles glazing measurements correctly

---

## Implementation Phases

### Phase 1: PO Clients UI Fix (15-20 min)
**Priority:** Critical - Must fix before adding window system
- Fix broken Add/Edit Client forms from Session 10
- Update field names: `company_name` → `client_name`
- Add primary contact creation
- See `NEXT_SESSION_PLAN.md` for detailed steps

### Phase 2: User Role System (30 min)
- Extend `user_profiles` table with `department` column
- Update `role` values: 'owner', 'admin', 'manufacturing_admin', 'employee'
- Create `modules/permissions.py` helper
- Add database methods for role checking

### Phase 3: Database Schema (45 min)
- Create `window_manufacturing_schema.sql`
- 4 new tables with RLS policies
- Test with sample data

### Phase 4: Backend Modules (1-1.5 hrs)
- Extend `modules/database.py` with window order methods
- Create `modules/zpl_generator.py` for labels
- Create `modules/label_printer.py` for printing
- Fuzzy matching for customer autocomplete

### Phase 5: UI Pages (2-3 hrs)
- `pages/window_order_entry.py` - Order form
- `pages/window_order_management.py` - Dashboard
- `pages/window_label_printing.py` - Print queue

### Phase 6: Navigation & Access (30 min)
- Update `dash_app.py` with new routes
- Role-based navigation filtering
- Protected routes

### Phase 7: Polish & Testing (1 hr)
- QuickBooks placeholder
- Fuzzy matching implementation
- Seed data for testing
- Error handling

**Total Estimated Time:** 6-8 hours

---

## Files to Create

### SQL Migrations
1. `add_user_roles_and_departments.sql` - User role system
2. `window_manufacturing_schema.sql` - All window tables
3. `window_manufacturing_seed_data.sql` - Test data

### Python Modules
4. `modules/permissions.py` - Access control helper
5. `modules/zpl_generator.py` - ZPL label generation
6. `modules/label_printer.py` - Printer interface

### UI Pages
7. `pages/window_order_entry.py` - Order entry form
8. `pages/window_order_management.py` - Order dashboard
9. `pages/window_label_printing.py` - Print queue/history

### Documentation
10. `WINDOW_MANUFACTURING_GUIDE.md` - Complete setup guide
11. `SESSION_11_SUMMARY.md` - Implementation summary (after execution)

### Files to Modify
- `pages/po_clients.py` - Fix broken forms (Phase 1)
- `modules/database.py` - Add window order CRUD methods
- `dash_app.py` - Add routes, navigation, role filtering

---

## Testing Checklist

### PO Client Fix
- [ ] Add client form opens without errors
- [ ] Can enter client_name and contact info
- [ ] Save creates both client and primary contact records
- [ ] Client cards display correctly

### User Roles
- [ ] Roles assigned correctly in database
- [ ] Role retrieval methods work
- [ ] Permission checks function properly

### Window Orders
- [ ] Can create order with multiple window types
- [ ] Fraction measurements parse correctly
- [ ] Customer autocomplete with fuzzy matching works
- [ ] PO number validation (duplicate detection)
- [ ] Order saves with all line items

### Labels
- [ ] Correct number of labels generated (4 windows = 4 labels)
- [ ] ZPL code generates properly
- [ ] Label preview displays
- [ ] Mock printer saves .zpl files
- [ ] Print queue shows all pending labels
- [ ] Print history tracks correctly

### Access Control
- [ ] Navigation filters based on role
- [ ] Employees see only order entry
- [ ] Manufacturing admins see all 3 pages
- [ ] Protected routes redirect properly

### Integration
- [ ] Customer links to po_clients when selected
- [ ] Manual customer entry works
- [ ] Fuzzy matching suggests similar entries
- [ ] All RLS policies enforce company isolation
- [ ] Soft deletes work correctly

---

## Key Design Decisions

### Why Not Separate App?
- **Decision:** Integrate into existing dash_app.py
- **Reason:** Shared authentication, database, company scoping
- **Benefit:** Single deployment, unified navigation

### Why Company-Scoped?
- **Decision:** Use existing company_id model
- **Reason:** Multi-tenant ready, follows established pattern
- **Benefit:** Easy to scale if other companies need window manufacturing

### Why Separate from PO System?
- **Decision:** New tables, optional FK to po_clients
- **Reason:** Different workflow, different access control
- **Benefit:** Clean separation, can link later via QuickBooks

### Why Store ZPL Code?
- **Decision:** Store generated ZPL in window_labels table
- **Reason:** Enable reprinting without regeneration
- **Benefit:** Print history, troubleshooting, consistency

---

## Open Questions for Next Session

1. **Window Shape Types:** Need complete list of window types for dropdown (user will provide)

2. **Printer Details:** Actual IP address and connection details for ZD421 (build with mock for now)

3. **Sister Company Name:** What's the actual name for display purposes?

4. **Label Branding:** Any company logos or specific formatting requirements for labels?

5. **Barcode Requirement:** Do you need PO number as scannable barcode on labels?

6. **Order Workflow:** Any approval process before orders go to manufacturing?

7. **Notification System:** Should manufacturing admins get notified of new orders?

---

## Next Session Start Point

**Session 12 will begin with:**
1. Quick fix of PO Clients UI (15 min)
2. Implementation of Window Manufacturing System (5-7 hours)
3. Full testing and documentation

**Prerequisites:**
- [ ] User confirms plan
- [ ] User provides complete window shape types list (optional, can use defaults)
- [ ] User confirms printer will be tested with mock mode initially

**Current Status:**
- PO Clients UI: Broken (needs Session 10 fix)
- Window Manufacturing: Fully planned, ready to implement
- User Roles: Needs implementation
- Database: Ready to add new tables

---

**Planning Session Completed:** November 3, 2025
**Ready for Execution:** Session 12
**Estimated Implementation Time:** 6-8 hours
