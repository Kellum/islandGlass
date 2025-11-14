# Island Glass CRM - Lessons Learned & Best Practices

**Purpose**: Internal knowledge base documenting hard-won lessons, architectural decisions, and debugging breakthroughs from the Island Glass CRM project.

**Last Updated**: November 6, 2025 - Session 28

---

## Table of Contents

1. [Critical Architectural Lessons](#critical-architectural-lessons)
2. [Dash Framework Patterns](#dash-framework-patterns)
3. [Debugging Methodologies](#debugging-methodologies)
4. [Database & Backend Patterns](#database--backend-patterns)
5. [UI/UX Best Practices](#uiux-best-practices)
6. [Session Management & Auth](#session-management--auth)
7. [Common Pitfalls & Solutions](#common-pitfalls--solutions)

---

## Critical Architectural Lessons

### Lesson 1: Layout Functions vs Static Layouts

**Discovery Date**: November 6, 2025 (Session 28)
**Severity**: 🔴 CRITICAL - Causes silent callback failures
**Session References**: 27 (debugging), 28 (solution)

#### The Problem

Using static layout variables in Dash multi-page apps breaks modal button callbacks silently.

**Broken Pattern:**
```python
# ❌ NEVER DO THIS in page modules
layout = dmc.Stack([
    dmc.Modal(id="my-modal", children=[...])
])
```

**Why It Breaks:**
- Layout evaluated ONCE at module import (app startup)
- Components register in callback graph BEFORE routing system initializes
- Button clicks trigger events, but Dash can't match them to callback outputs
- Zero error messages - completely silent failure
- Browser shows "updating..." but server receives nothing

**Working Pattern:**
```python
# ✅ ALWAYS DO THIS in page modules
def layout(session_data=None):
    return dmc.Stack([
        dmc.Modal(id="my-modal", children=[...])
    ])
```

**Why It Works:**
- Layout evaluated on EACH route visit
- Fresh component registration with proper route context
- Callback dependency graph builds correctly
- All button callbacks work normally

#### Symptoms to Watch For

If you see ALL these symptoms together, suspect static layout pattern:
1. ✓ Modal opens successfully
2. ✓ Form inputs work
3. ✓ Button shows "updating..." for split second
4. ✓ Callback registers at startup (debug prints confirm)
5. ✗ Callback never executes (no server output)
6. ✗ No errors in browser console
7. ✗ No errors in server logs

#### Pages Affected

**Fixed:**
- ✅ `pages/po_clients.py` - Session 28

**Still Using Static Layouts (at risk):**
```
pages/bulk_actions.py:17
pages/calculator.py:22
pages/contractors.py:17
pages/dashboard.py:14
pages/discovery.py:23
pages/enrichment.py:13
pages/import_contractors.py:23
pages/inventory_page.py:20
pages/purchase_orders.py:21
pages/quickbooks_settings.py:32
pages/settings.py:16
pages/vendors.py:345
pages/window_order_entry.py:29
```

**Action Required:** Convert to layout functions BEFORE adding modals/dynamic components.

#### Detection Command

```bash
# Find all pages with static layout pattern
grep -n "^layout = " pages/*.py
```

#### Prevention Checklist

When creating a new page:
- [ ] Start with `def layout(session_data=None):`
- [ ] Include `session_data` parameter for auth access
- [ ] Return the layout structure
- [ ] Test modal buttons immediately after creation
- [ ] Add debug prints to confirm callbacks fire

#### References
- **Troubleshooting Log**: Issue #4 (lines 213-420)
- **Checkpoint**: Session 28 (lines 1-75)
- **Files Modified**: `pages/po_clients.py:22-364`

---

### Lesson 2: Session Store Cannot Be Accessed from Page Modules

**Discovery Date**: November 5, 2025 (Session 26)
**Severity**: 🔴 CRITICAL - Silently blocks callbacks
**Session References**: 26

#### The Problem

Page module callbacks cannot reliably reference `State("session-store", "data")` when `session-store` is defined in `dash_app.py`.

**Broken Pattern:**
```python
# In dash_app.py
app.layout = dmc.MantineProvider([
    dcc.Store(id="session-store", data=...)
])

# In pages/my_page.py
@callback(
    Output("result", "children"),
    Input("submit-btn", "n_clicks"),
    State("session-store", "data"),  # ❌ BLOCKS THE CALLBACK!
    prevent_initial_call=True
)
def my_callback(n_clicks, session_data):
    # This never executes
    ...
```

**Why It Breaks:**
- Dash validation fails silently
- Page modules can't access stores from main app as States/Inputs
- No error message - callback just never fires
- Browser shows "updating..." but nothing happens

#### The Solution

**Option 1: Direct Database Instantiation (Quick Fix)**
```python
@callback(
    Output("result", "children"),
    Input("submit-btn", "n_clicks"),
    # NO State("session-store", "data")
    prevent_initial_call=True
)
def my_callback(n_clicks):
    from modules.database import Database
    db = Database()  # Direct instantiation
    user_id = None  # Temporarily no tracking
    # ... rest of logic
```

**Trade-offs:**
- ⚠️ No user_id tracking (`created_by` and `updated_by` are NULL)
- ⚠️ No session validation
- ✅ Callback actually fires
- ✅ Feature works

**Option 2: URL Query Parameters (Recommended)**
```python
# Pass session data via URL
dcc.Location(id='url', refresh=False)

@callback(
    Output("result", "children"),
    Input("submit-btn", "n_clicks"),
    State('url', 'search'),  # Use URL params instead
    prevent_initial_call=True
)
def my_callback(n_clicks, search):
    # Parse user_id from query params
    ...
```

**Option 3: Local Session Store Sync**
```python
# Add to page layout
dcc.Store(id="local-session-cache")

# Sync callback (runs in main app, not page module)
@callback(
    Output("local-session-cache", "data"),
    Input("session-store", "data")
)
def sync_session(session_data):
    return session_data

# Use in page callbacks
@callback(
    Output("result", "children"),
    Input("submit-btn", "n_clicks"),
    State("local-session-cache", "data"),  # Use local copy
    prevent_initial_call=True
)
def my_callback(n_clicks, session_data):
    ...
```

#### Prevention Rule

**Never use `State("session-store", "data")` or `Input("session-store", "data")` in page module callbacks.**

#### References
- **Troubleshooting Log**: Issue #1 (lines 9-109)
- **Checkpoint**: Session 26 (lines 49-189)

---

### Lesson 3: Button Grouping Limit (3+ Buttons Bug)

**Discovery Date**: November 5, 2025 (Session 26)
**Severity**: 🟡 MODERATE - Third button doesn't fire
**Session References**: 26

#### The Problem

Having 3+ buttons in a `dmc.Group` causes the third button to not register clicks.

**Broken Pattern:**
```python
dmc.Group([
    dmc.Button("Cancel", ...),      # Button 1 - works
    dmc.Button("Test", ...),         # Button 2 - works
    dmc.Button("Submit", ...)        # Button 3 - DOESN'T WORK!
], justify="flex-end")
```

#### The Solution

**Option 1: Remove Extra Button**
```python
dmc.Group([
    dmc.Button("Cancel", ...),
    dmc.Button("Submit", ...)  # Now works!
], justify="flex-end")
```

**Option 2: Use Different Layout**
```python
dmc.Stack([
    dmc.Button("Button 1", ...),
    dmc.Button("Button 2", ...),
    dmc.Button("Button 3", ...)
])
```

**Option 3: Multiple Groups**
```python
dmc.Group([
    dmc.Group([dmc.Button("Cancel", ...)]),
    dmc.Group([
        dmc.Button("Test", ...),
        dmc.Button("Submit", ...)
    ])
], justify="space-between")
```

#### Prevention Rule

**Avoid having more than 2 buttons in a single `dmc.Group`.**

#### References
- **Troubleshooting Log**: Issue #3 (lines 153-210)
- **Checkpoint**: Session 26

---

## Dash Framework Patterns

### Pattern 1: Modal Implementation

**Recommended Modal Structure:**

```python
def layout(session_data=None):
    return dmc.Stack([
        # Page content
        html.Div(id="page-content"),

        # Modal definition
        dmc.Modal(
            id="my-modal",
            title="Modal Title",
            size="lg",
            children=[
                dmc.Stack([
                    # Form fields
                    dmc.TextInput(id="field-1", label="Field 1"),
                    dmc.TextInput(id="field-2", label="Field 2"),

                    # Action buttons (max 2 in Group!)
                    dmc.Group([
                        dmc.Button("Cancel", id="cancel-btn", variant="subtle"),
                        dmc.Button("Submit", id="submit-btn", color="blue")
                    ], justify="flex-end")
                ], gap="md")
            ]
        )
    ], gap="md")
```

**Modal Toggle Callback:**

```python
@callback(
    Output("my-modal", "opened"),
    Input("open-modal-btn", "n_clicks"),
    Input("cancel-btn", "n_clicks"),
    State("my-modal", "opened"),
    prevent_initial_call=True
)
def toggle_modal(open_clicks, cancel_clicks, is_opened):
    triggered_id = ctx.triggered_id

    if triggered_id == "open-modal-btn":
        return True
    elif triggered_id == "cancel-btn":
        return False

    return is_opened
```

**Submit Callback:**

```python
@callback(
    Output("my-modal", "opened", allow_duplicate=True),
    Output("page-content", "children"),
    Input("submit-btn", "n_clicks"),
    State("field-1", "value"),
    State("field-2", "value"),
    prevent_initial_call=True
)
def submit_form(n_clicks, field1, field2):
    if not n_clicks:
        return dash.no_update, dash.no_update

    # Validate
    if not field1:
        return dash.no_update, "Error: Field 1 required"

    # Save to database
    # ...

    # Close modal and refresh content
    return False, "Success!"
```

### Pattern 2: Dynamic Component Management

**Progressive Disclosure (Conditional Fields):**

```python
# Callback to show/hide fields
@callback(
    Output("conditional-field", "style"),
    Input("trigger-select", "value")
)
def toggle_field(selected_value):
    if selected_value == "show-field":
        return {}  # Show
    return {"display": "none"}  # Hide
```

**Pattern-Matching Callbacks:**

```python
# Container must have explicit empty children
html.Div(id="dynamic-container", children=[])  # ✅ REQUIRED!

@callback(
    Output("dynamic-container", "children"),
    Input("add-item-btn", "n_clicks"),
    State({"type": "dynamic-input", "index": ALL}, "value"),
    prevent_initial_call=True
)
def add_dynamic_item(n_clicks, existing_values):
    # Create new items dynamically
    new_item = dmc.TextInput(
        id={"type": "dynamic-input", "index": n_clicks},
        placeholder=f"Item {n_clicks}"
    )
    return existing_values + [new_item]
```

### Pattern 3: Callback Best Practices

**Callback Structure Template:**

```python
@callback(
    # Outputs
    Output("component-1", "property"),
    Output("component-2", "property", allow_duplicate=True),  # If needed

    # Inputs (triggers)
    Input("trigger-btn", "n_clicks"),

    # States (read without triggering)
    State("input-field", "value"),
    State("session-store", "data"),  # ⚠️ Only in dash_app.py, NOT page modules

    prevent_initial_call=True  # ✅ Almost always use this
)
def my_callback(n_clicks, input_value, session_data):
    """Clear docstring explaining what this callback does"""

    # Guard clause - check if actually triggered
    if not n_clicks:
        return dash.no_update, dash.no_update

    # Early validation
    if not input_value:
        return "Error", dash.no_update

    # Get triggered component
    triggered_id = ctx.triggered_id

    # Main logic
    try:
        # ... do work ...
        result = process_data(input_value)
        return result, "Success"
    except Exception as e:
        print(f"Error in my_callback: {e}")
        return "Error", f"Failed: {str(e)}"
```

**Callback Debugging Template:**

```python
@callback(...)
def my_callback(...):
    print("=" * 80)
    print(f"🔥 CALLBACK TRIGGERED: {ctx.triggered_id}")
    print(f"Input values: {locals()}")
    print("=" * 80)

    # ... rest of callback
```

---

## Debugging Methodologies

### Methodology 1: Silent Callback Failure Investigation

**When a callback doesn't fire (no debug output, no errors):**

#### Step 1: Verify Callback Registration
```python
# Add debug print OUTSIDE callback
print("DEBUG: my_callback has been registered!")

@callback(...)
def my_callback(...):
    print("🔥 CALLBACK FIRED")  # This should print when triggered
    ...
```

**Expected Output on App Start:**
```
DEBUG: my_callback has been registered!
Dash is running on http://127.0.0.1:8050/
```

**When Button Clicked:**
```
🔥 CALLBACK FIRED
```

If registration prints but callback doesn't fire → Architectural issue (layout pattern, session-store, etc.)

#### Step 2: Check Component Hierarchy

```python
# Verify all State/Input IDs exist in layout
@callback(
    Output("output-div", "children"),
    Input("submit-btn", "n_clicks"),
    State("non-existent-field", "value"),  # ❌ Will block callback!
    prevent_initial_call=True
)
```

**Validation:** Search layout for each ID:
```bash
grep -n "id=\"non-existent-field\"" pages/my_page.py
```

#### Step 3: Simplify to Minimal Callback

```python
# Create test button with absolutely minimal callback
dmc.Button("TEST", id="simple-test-btn")

@callback(
    Output("test-output", "children"),
    Input("simple-test-btn", "n_clicks"),
    prevent_initial_call=True
)
def test_simple(n_clicks):
    print(f"🔥 TEST BUTTON CLICKED: {n_clicks}")
    return f"Clicked {n_clicks} times"
```

If this works → Original callback has configuration issue
If this fails → Page-level architectural issue (layout pattern!)

#### Step 4: Check Browser Network Tab

1. Open DevTools → Network tab
2. Filter: "Fetch/XHR"
3. Click button
4. Look for `_dash-update-component` request

**If request appears:**
- Status 200 → Callback executed, check response body
- Status 500 → Server error, check terminal
- Status 400 → Validation error, check payload

**If no request:**
- Component ID not found in callback graph
- Layout registration issue (likely static layout pattern!)

### Methodology 2: Comparative Debugging

**When one page works but another doesn't:**

#### Step 1: Side-by-Side File Comparison
```bash
# Compare layout patterns
head -30 pages/working_page.py
head -30 pages/broken_page.py
```

Look for:
- `def layout():` vs `layout =`
- Import differences
- Component structure differences

#### Step 2: Copy Working Pattern
1. Identify working modal implementation
2. Copy EXACT structure (modal, buttons, callback)
3. Adapt to your use case
4. Test incrementally

#### Step 3: Diff Callbacks
```bash
# Extract just the callback decorators
grep -A 1 "@callback" pages/working_page.py > working_callbacks.txt
grep -A 1 "@callback" pages/broken_page.py > broken_callbacks.txt
diff working_callbacks.txt broken_callbacks.txt
```

### Methodology 3: Systematic Elimination

**When multiple things could be wrong:**

1. **Remove all States** → Test if callback fires
2. **Remove allow_duplicate** → Test if callback fires
3. **Simplify Output** → Single output instead of multiple
4. **Remove validation** → Just print and return
5. **Test outside modal** → Move button to main layout

Work backwards from simplest possible callback to full implementation.

---

## Database & Backend Patterns

### Pattern 1: Database Method Structure

**Standard CRUD Method Template:**

```python
def get_items(self, filters=None):
    """
    Fetch items with optional filtering

    Args:
        filters (dict): Optional filter criteria

    Returns:
        list: List of item dictionaries
    """
    try:
        query = self.supabase.table('items').select('*')

        # Company scoping (multi-tenant)
        if self.company_id:
            query = query.eq('company_id', self.company_id)

        # Apply filters
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        response = query.execute()
        return response.data or []
    except Exception as e:
        print(f"Error fetching items: {e}")
        return []


def insert_item(self, item_data, user_id=None):
    """
    Insert new item with audit trail

    Args:
        item_data (dict): Item data (without audit fields)
        user_id (str): User ID for audit trail

    Returns:
        dict: Inserted item or None on failure
    """
    try:
        # Add audit fields
        full_data = {
            **item_data,
            'company_id': self.company_id,
            'created_by': user_id,
            'updated_by': user_id
        }

        response = self.supabase.table('items').insert(full_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error inserting item: {e}")
        return None


def update_item(self, item_id, updates, user_id=None):
    """
    Update existing item

    Args:
        item_id (str): Item UUID
        updates (dict): Fields to update
        user_id (str): User ID for audit trail

    Returns:
        dict: Updated item or None on failure
    """
    try:
        # Add audit field
        updates['updated_by'] = user_id

        response = (
            self.supabase.table('items')
            .update(updates)
            .eq('id', item_id)
            .eq('company_id', self.company_id)  # Security: only update own company
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating item: {e}")
        return None


def delete_item(self, item_id, user_id=None):
    """
    Soft delete item

    Args:
        item_id (str): Item UUID
        user_id (str): User ID for audit trail

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Soft delete - set deleted_at timestamp
        response = (
            self.supabase.table('items')
            .update({
                'deleted_at': 'now()',
                'updated_by': user_id
            })
            .eq('id', item_id)
            .eq('company_id', self.company_id)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        print(f"Error deleting item: {e}")
        return False
```

### Pattern 2: Audit Trail Implementation

**All tables should have:**
```sql
created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
created_by UUID REFERENCES auth.users(id),
updated_by UUID REFERENCES auth.users(id),
deleted_at TIMESTAMP WITH TIME ZONE,
company_id UUID REFERENCES companies(id) NOT NULL
```

**Auto-update trigger:**
```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER items_updated_at
    BEFORE UPDATE ON items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

---

## UI/UX Best Practices

### Best Practice 1: Form Validation

**Client-Side Validation:**
```python
dmc.TextInput(
    id="email-input",
    label="Email",
    placeholder="user@example.com",
    required=True,  # Shows asterisk
    type="email",  # Browser validation
    description="We'll never share your email"
)
```

**Server-Side Validation in Callback:**
```python
@callback(...)
def submit_form(n_clicks, email, name):
    # Guard clause
    if not n_clicks:
        return dash.no_update, dash.no_update

    # Validation
    if not email or not name:
        return dash.no_update, dmc.Notification(
            title="Validation Error",
            message="Email and name are required",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )

    if "@" not in email:
        return dash.no_update, dmc.Notification(
            title="Invalid Email",
            message="Please enter a valid email address",
            color="red",
            action="show"
        )

    # Process...
```

### Best Practice 2: Loading States

**Show feedback during async operations:**

```python
@callback(
    Output("submit-btn", "loading"),
    Output("result", "children"),
    Input("submit-btn", "n_clicks"),
    prevent_initial_call=True
)
def handle_submit(n_clicks):
    # Button shows loading spinner automatically
    time.sleep(2)  # Simulate slow operation

    return False, "Done!"  # Stop loading, show result
```

### Best Practice 3: Notification Patterns

**Success Notification:**
```python
dmc.Notification(
    title="Success",
    message="Client created successfully",
    color="green",
    icon=DashIconify(icon="solar:check-circle-bold"),
    action="show",
    autoClose=3000  # Auto-dismiss after 3 seconds
)
```

**Error Notification:**
```python
dmc.Notification(
    title="Error",
    message=f"Failed to save: {str(error)}",
    color="red",
    icon=DashIconify(icon="solar:danger-circle-bold"),
    action="show",
    autoClose=5000
)
```

---

## Session Management & Auth

### Pattern 1: Session Data Access

**In dash_app.py (Main App):**
```python
# ✅ CAN access session-store
@callback(
    Output("user-display", "children"),
    Input("session-store", "data")
)
def update_user_display(session_data):
    if not session_data or 'session' not in session_data:
        return "Not logged in"

    user = session_data['session'].get('user', {})
    return f"Welcome, {user.get('email')}"
```

**In pages/my_page.py (Page Module):**
```python
# ❌ CANNOT access session-store as State/Input
# ✅ CAN receive via layout function parameter

def layout(session_data=None):
    # Access session_data here
    user_email = "Guest"
    if session_data and 'session' in session_data:
        user_email = session_data['session'].get('user', {}).get('email', 'Guest')

    return dmc.Stack([
        dmc.Text(f"Logged in as: {user_email}")
    ])
```

### Pattern 2: Protected Routes

**Check authentication in layout:**
```python
def layout(session_data=None):
    # Check if user is authenticated
    if not session_data or 'session' not in session_data:
        return dmc.Stack([
            dmc.Alert(
                "Please log in to access this page",
                title="Authentication Required",
                color="red"
            ),
            dmc.Button("Go to Login", href="/login")
        ])

    # User is authenticated - show page content
    return dmc.Stack([...])
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Forgetting prevent_initial_call

**Problem:**
```python
@callback(
    Output("result", "children"),
    Input("submit-btn", "n_clicks")
    # Missing: prevent_initial_call=True
)
def my_callback(n_clicks):
    # This runs on page load with n_clicks=None!
    # Causes error if you don't guard against None
    ...
```

**Solution:**
```python
@callback(
    Output("result", "children"),
    Input("submit-btn", "n_clicks"),
    prevent_initial_call=True  # ✅ Add this
)
def my_callback(n_clicks):
    # Only runs when button actually clicked
    ...
```

### Pitfall 2: Incorrect allow_duplicate Usage

**Problem:**
```python
# Two outputs to same component in different callbacks
@callback(
    Output("my-div", "children"),  # First callback
    Input("btn-1", "n_clicks")
)
def callback1(n):
    return "From callback 1"

@callback(
    Output("my-div", "children"),  # ❌ Duplicate output!
    Input("btn-2", "n_clicks")
)
def callback2(n):
    return "From callback 2"
```

**Solution:**
```python
@callback(
    Output("my-div", "children", allow_duplicate=True),  # ✅ Add this
    Input("btn-2", "n_clicks"),
    prevent_initial_call=True  # ✅ Required with allow_duplicate
)
def callback2(n):
    return "From callback 2"
```

### Pitfall 3: Mutating State

**Problem:**
```python
@callback(
    Output("data-store", "data"),
    Input("add-btn", "n_clicks"),
    State("data-store", "data")
)
def add_item(n_clicks, current_data):
    current_data.append(new_item)  # ❌ Mutating state directly
    return current_data  # Dash may not detect change!
```

**Solution:**
```python
@callback(
    Output("data-store", "data"),
    Input("add-btn", "n_clicks"),
    State("data-store", "data")
)
def add_item(n_clicks, current_data):
    new_data = current_data.copy()  # ✅ Create new object
    new_data.append(new_item)
    return new_data
```

---

## Quick Reference Checklist

### New Page Creation Checklist

- [ ] Use `def layout(session_data=None):` pattern
- [ ] Return layout structure from function
- [ ] Test page loads without errors
- [ ] Add authentication check if needed
- [ ] Test all buttons/inputs before moving on

### New Modal Checklist

- [ ] Modal defined in layout function (not static layout)
- [ ] Toggle callback implemented (open/cancel/close)
- [ ] Submit callback with validation
- [ ] Action buttons limited to 2 per `dmc.Group`
- [ ] Test modal open → submit → close flow
- [ ] Verify callback executes (debug print)

### New Callback Checklist

- [ ] Include `prevent_initial_call=True`
- [ ] Use `allow_duplicate=True` only when needed
- [ ] Verify all Input/State IDs exist in layout
- [ ] Add debug print for troubleshooting
- [ ] Test callback fires (check terminal output)
- [ ] Handle None/empty values gracefully
- [ ] Return appropriate number of outputs

### Database Method Checklist

- [ ] Include docstring with Args/Returns
- [ ] Add company_id filtering (multi-tenant)
- [ ] Add audit trail fields (created_by, updated_by)
- [ ] Use try/except with error logging
- [ ] Return None or [] on failure
- [ ] Test with real data before deploying

---

## Documentation Index

### Project Documentation Files

| File | Purpose | Primary Use Case |
|------|---------|------------------|
| **LESSONS_LEARNED.md** (this file) | Master knowledge base, architectural patterns, debugging methods | Learning from past issues, preventing regressions |
| **TROUBLESHOOTING_LOG.md** | Specific recurring issues with solutions | Quick lookup when encountering known problems |
| **checkpoint.md** | Session-by-session progress tracker | Understanding what was built when, current project state |
| **REVISED_PO_SYSTEM_SUMMARY.md** | Complete Jobs/PO system architecture | Understanding the Jobs/PO system design |
| **QUICK_START_JOBS_SYSTEM.md** | User guide for Jobs/PO features | Learning how to use the Jobs/PO system |

### When to Use Which Document

**"I'm seeing weird behavior, has this happened before?"**
→ Check **TROUBLESHOOTING_LOG.md** first

**"What's the right way to implement [feature]?"**
→ Check **LESSONS_LEARNED.md** patterns section

**"What was built in Session X?"**
→ Check **checkpoint.md**

**"How does the Jobs/PO system work?"**
→ Check **REVISED_PO_SYSTEM_SUMMARY.md**

**"I'm debugging a callback that won't fire"**
→ Check **LESSONS_LEARNED.md** → Debugging Methodologies → Silent Callback Failure

---

## Contributing to This Document

### When to Add a Lesson

Add a new lesson when:
1. You spend >2 hours debugging something
2. The solution is non-obvious
3. The issue could recur in other parts of the codebase
4. The fix involves changing an architectural pattern

### Lesson Template

```markdown
### Lesson X: [Brief Title]

**Discovery Date**: Month Day, Year (Session #)
**Severity**: 🔴 CRITICAL / 🟡 MODERATE / 🔵 INFO
**Session References**: Session numbers

#### The Problem

[Clear description of what was broken]

**Broken Pattern:**
```python
# ❌ Bad code example
```

**Why It Breaks:**
- Bullet points explaining the root cause
- Technical details about why this fails

**Working Pattern:**
```python
# ✅ Good code example
```

**Why It Works:**
- Bullet points explaining why the fix works

#### Symptoms to Watch For

1. Observable symptom 1
2. Observable symptom 2

#### Prevention Rule

**Clear rule statement to prevent this issue**

#### References
- Links to other documentation
- File paths with line numbers
```

---

**Last Updated**: November 6, 2025 - Session 28
**Maintained By**: Development Team
**Next Review**: After every significant debugging session
