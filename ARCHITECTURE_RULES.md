# Island Glass CRM - Architecture Rules & Best Practices

**Purpose**: Mandatory architectural rules and best practices for this project. These are NOT suggestions - they are REQUIREMENTS.

**Last Updated**: November 6, 2025 - Session 28

---

## 🚨 CRITICAL RULES - NEVER BREAK THESE

### Rule 1: Page Layouts MUST Be Functions

**REQUIRED PATTERN:**
```python
def layout(session_data=None):
    return dmc.Stack([...])
```

**FORBIDDEN PATTERN:**
```python
layout = dmc.Stack([...])  # ❌ NEVER DO THIS
```

**Why**: Static layouts break modal callbacks silently. Components register before routing initializes.

**Enforcement**: Before creating ANY new page, use this exact template:
```python
"""
Page Description
"""

import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, ctx
from dash_iconify import DashIconify
from modules.database import get_authenticated_db

def layout(session_data=None):
    """Page layout - MUST be a function, NEVER a variable"""
    return dmc.Stack([
        # Your content here
    ], gap="md")
```

**Verification Command:**
```bash
# This should return NOTHING
grep "^layout = " pages/YOUR_NEW_PAGE.py
```

---

### Rule 2: NEVER Reference session-store in Page Modules

**FORBIDDEN PATTERN:**
```python
# In pages/my_page.py
@callback(
    Output(...),
    Input(...),
    State("session-store", "data"),  # ❌ BLOCKS CALLBACK!
    prevent_initial_call=True
)
def my_callback(n_clicks, session_data):
    ...
```

**ALLOWED PATTERN (Option 1 - Temporary):**
```python
@callback(
    Output(...),
    Input(...),
    # NO session-store State
    prevent_initial_call=True
)
def my_callback(n_clicks):
    from modules.database import Database
    db = Database()
    user_id = None  # Accept this limitation temporarily
    ...
```

**ALLOWED PATTERN (Option 2 - Recommended):**
```python
# Access session_data via layout function parameter
def layout(session_data=None):
    user_id = None
    if session_data and 'session' in session_data:
        user_id = session_data['session'].get('user', {}).get('id')

    # Use user_id in layout rendering
    return dmc.Stack([...])
```

**Why**: Page module callbacks cannot access stores defined in main app. Dash validation fails silently.

**Verification Command:**
```bash
# This should return NOTHING
grep 'State("session-store"' pages/YOUR_NEW_PAGE.py
```

---

### Rule 3: Maximum 2 Buttons Per dmc.Group

**ALLOWED PATTERN:**
```python
dmc.Group([
    dmc.Button("Cancel", id="cancel-btn"),
    dmc.Button("Submit", id="submit-btn")
], justify="flex-end")
```

**FORBIDDEN PATTERN:**
```python
dmc.Group([
    dmc.Button("Cancel", id="cancel-btn"),
    dmc.Button("Test", id="test-btn"),
    dmc.Button("Submit", id="submit-btn")  # ❌ Third button won't work!
], justify="flex-end")
```

**Alternative if you need 3+ buttons:**
```python
dmc.Stack([
    dmc.Button("Button 1", ...),
    dmc.Button("Button 2", ...),
    dmc.Button("Button 3", ...)
], gap="xs")
```

**Why**: DMC Group has a bug where the third button doesn't register clicks.

---

### Rule 4: Always Use prevent_initial_call=True

**REQUIRED PATTERN:**
```python
@callback(
    Output(...),
    Input(...),
    prevent_initial_call=True  # ✅ REQUIRED
)
def my_callback(...):
    ...
```

**FORBIDDEN PATTERN:**
```python
@callback(
    Output(...),
    Input(...)
    # Missing prevent_initial_call
)
def my_callback(...):
    ...
```

**Why**: Without this, callbacks fire on page load with None values, causing errors.

**Exception**: Only use `prevent_initial_call=False` or `prevent_initial_call='initial_duplicate'` if you explicitly need the callback to run on page load AND you've handled None values.

---

### Rule 5: Pattern-Matching Containers Need children=[]

**REQUIRED PATTERN:**
```python
html.Div(id="dynamic-container", children=[])  # ✅ Explicit empty list
```

**FORBIDDEN PATTERN:**
```python
html.Div(id="dynamic-container")  # ❌ Missing children
```

**Why**: Pattern-matching callbacks with `ALL` or `MATCH` fail silently without explicit empty container.

---

## 📋 MANDATORY CHECKLISTS

### Before Creating a New Page

Copy this checklist into your planning:

```markdown
- [ ] Layout is a FUNCTION: `def layout(session_data=None):`
- [ ] NO `State("session-store", "data")` in callbacks
- [ ] All callbacks have `prevent_initial_call=True`
- [ ] No more than 2 buttons in any `dmc.Group`
- [ ] Pattern-matching containers have `children=[]`
- [ ] Verified with: `grep "^layout = " pages/my_page.py` returns nothing
- [ ] Verified with: `grep 'State("session-store"' pages/my_page.py` returns nothing
```

### Before Creating a New Modal

```markdown
- [ ] Modal defined inside layout FUNCTION (not static layout)
- [ ] Toggle callback implemented (open/cancel)
- [ ] Submit callback with validation
- [ ] Action buttons limited to 2 per Group
- [ ] Test button clicks immediately
- [ ] Added debug print: `print(f"🔥 CALLBACK FIRED")`
```

### Before Committing Code

```markdown
- [ ] Ran: `python3 -m py_compile pages/*.py` (no errors)
- [ ] Ran: `grep "^layout = " pages/*.py` (returns nothing)
- [ ] Ran: `grep 'State("session-store"' pages/*.py` (returns nothing)
- [ ] Tested all modified features manually
- [ ] Debug prints removed or commented out
- [ ] Updated checkpoint.md with changes
```

---

## 🏗️ REQUIRED CODE TEMPLATES

### New Page Template (COPY THIS EXACTLY)

```python
"""
Page Name - Brief Description

Features:
- Feature 1
- Feature 2
"""

import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, ctx, dcc
from dash_iconify import DashIconify
from modules.database import get_authenticated_db

# ===== LAYOUT FUNCTION (REQUIRED PATTERN) =====
def layout(session_data=None):
    """
    Page layout - MUST be a function
    Args:
        session_data: Session data from main app (optional)
    Returns:
        dmc.Stack: Page layout
    """
    return dmc.Stack([
        # Header
        dmc.Group([
            dmc.Stack([
                dmc.Title("Page Title", order=1),
                dmc.Text("Page description", c="dimmed", size="sm")
            ], gap=0),
            dmc.Button(
                "Action Button",
                id="action-btn",
                leftSection=DashIconify(icon="solar:add-circle-bold", width=20),
                color="blue"
            )
        ], justify="space-between"),

        dmc.Space(h=10),

        # Content
        html.Div(id="page-content"),

        # Modals (if needed)
        # Stores (if needed)
        # Notification container (if needed)

    ], gap="md")


# ===== CALLBACKS =====
@callback(
    Output("page-content", "children"),
    Input("action-btn", "n_clicks"),
    prevent_initial_call=True  # REQUIRED
)
def update_content(n_clicks):
    """
    Update page content
    """
    # Debug print (remove before commit)
    print(f"🔥 update_content fired - n_clicks={n_clicks}")

    # Your logic here
    return "Content"
```

### Modal Template (COPY THIS EXACTLY)

```python
# In layout function:
dmc.Modal(
    id="my-modal",
    title="Modal Title",
    size="lg",
    children=[
        dmc.Stack([
            # Form fields
            dmc.TextInput(
                id="field-1",
                label="Field 1",
                placeholder="Enter value",
                required=True
            ),
            dmc.TextInput(
                id="field-2",
                label="Field 2",
                placeholder="Enter value"
            ),

            # Action buttons (MAX 2!)
            dmc.Group([
                dmc.Button(
                    "Cancel",
                    id="cancel-modal-btn",
                    variant="subtle",
                    color="gray"
                ),
                dmc.Button(
                    "Submit",
                    id="submit-modal-btn",
                    color="blue"
                )
            ], justify="flex-end")
        ], gap="md")
    ]
)

# Toggle callback
@callback(
    Output("my-modal", "opened"),
    Input("open-modal-btn", "n_clicks"),
    Input("cancel-modal-btn", "n_clicks"),
    State("my-modal", "opened"),
    prevent_initial_call=True
)
def toggle_modal(open_clicks, cancel_clicks, is_opened):
    """Toggle modal open/close"""
    triggered_id = ctx.triggered_id

    if triggered_id == "open-modal-btn":
        return True
    elif triggered_id == "cancel-modal-btn":
        return False

    return is_opened


# Submit callback
@callback(
    Output("my-modal", "opened", allow_duplicate=True),
    Output("notification-container", "children"),
    Input("submit-modal-btn", "n_clicks"),
    State("field-1", "value"),
    State("field-2", "value"),
    prevent_initial_call=True
)
def submit_modal(n_clicks, field1, field2):
    """Handle modal submission"""
    # Debug print (remove before commit)
    print(f"🔥 submit_modal fired - field1={field1}, field2={field2}")

    # Validation
    if not field1:
        return dash.no_update, dmc.Notification(
            title="Validation Error",
            message="Field 1 is required",
            color="red",
            icon=DashIconify(icon="solar:danger-circle-bold"),
            action="show"
        )

    # Save to database
    from modules.database import Database
    db = Database()
    # ... save logic ...

    # Close modal and show success
    return False, dmc.Notification(
        title="Success",
        message="Saved successfully",
        color="green",
        icon=DashIconify(icon="solar:check-circle-bold"),
        action="show"
    )
```

### Database Method Template (COPY THIS EXACTLY)

```python
def get_items(self, filters=None):
    """
    Fetch items with optional filtering

    Args:
        filters (dict): Optional filter criteria (e.g., {'status': 'active'})

    Returns:
        list: List of item dictionaries, empty list on error
    """
    try:
        query = self.supabase.table('items').select('*')

        # REQUIRED: Company scoping (multi-tenant security)
        if self.company_id:
            query = query.eq('company_id', self.company_id)

        # Apply filters
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        # REQUIRED: Exclude soft-deleted items
        query = query.is_('deleted_at', 'null')

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
        # REQUIRED: Add audit fields
        full_data = {
            **item_data,
            'company_id': self.company_id,  # Multi-tenant
            'created_by': user_id,          # Audit
            'updated_by': user_id           # Audit
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
        # REQUIRED: Add audit field
        updates['updated_by'] = user_id

        response = (
            self.supabase.table('items')
            .update(updates)
            .eq('id', item_id)
            .eq('company_id', self.company_id)  # REQUIRED: Security
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
        # REQUIRED: Soft delete (don't actually delete data)
        response = (
            self.supabase.table('items')
            .update({
                'deleted_at': 'now()',
                'updated_by': user_id
            })
            .eq('id', item_id)
            .eq('company_id', self.company_id)  # REQUIRED: Security
            .execute()
        )
        return bool(response.data)

    except Exception as e:
        print(f"Error deleting item: {e}")
        return False
```

---

## 🎯 DEVELOPMENT WORKFLOW

### Step 1: Planning (BEFORE writing code)

```markdown
1. Check if similar feature exists
   - Search: `grep -r "similar_feature" pages/`
   - Copy working pattern

2. Review architecture rules (this file)
   - Verify layout will be a function
   - Plan callbacks without session-store
   - Count buttons in groups (max 2)

3. Check documentation
   - LESSONS_LEARNED.md for patterns
   - TROUBLESHOOTING_LOG.md for known issues
   - QUICK_REFERENCE.md for templates
```

### Step 2: Implementation (WHILE writing code)

```markdown
1. Copy exact template (don't modify the pattern!)
2. Fill in your specific logic
3. Add debug prints: `print(f"🔥 callback_name fired")`
4. Test incrementally (don't write everything first)
```

### Step 3: Testing (BEFORE committing)

```markdown
1. Run syntax check:
   python3 -m py_compile pages/my_page.py

2. Run architecture checks:
   grep "^layout = " pages/my_page.py          # Should be empty
   grep 'State("session-store"' pages/my_page.py  # Should be empty

3. Start app and verify:
   python3 dash_app.py | grep "callback has been registered"

4. Manual testing:
   - Navigate to page
   - Click all buttons
   - Verify callbacks fire (check terminal)
   - Test validation
   - Test error cases
```

### Step 4: Documentation (AFTER testing)

```markdown
1. Update checkpoint.md:
   - What was built
   - Files modified
   - Known issues

2. If new pattern or issue discovered:
   - Add to LESSONS_LEARNED.md
   - Or add to TROUBLESHOOTING_LOG.md

3. Remove debug prints:
   - Or comment them out for future debugging
```

---

## 🚫 FORBIDDEN PATTERNS

These patterns are NEVER allowed:

```python
# ❌ FORBIDDEN #1: Static layout
layout = dmc.Stack([...])

# ❌ FORBIDDEN #2: session-store in page callbacks
State("session-store", "data")

# ❌ FORBIDDEN #3: Three or more buttons in Group
dmc.Group([btn1, btn2, btn3])

# ❌ FORBIDDEN #4: Missing prevent_initial_call
@callback(Output(...), Input(...))

# ❌ FORBIDDEN #5: Pattern-matching without children
html.Div(id="dynamic-container")  # Missing children=[]

# ❌ FORBIDDEN #6: Database methods without company_id
query = self.supabase.table('items').select('*')
# Missing: .eq('company_id', self.company_id)

# ❌ FORBIDDEN #7: Hard delete instead of soft delete
self.supabase.table('items').delete().eq('id', item_id)
# Should use: .update({'deleted_at': 'now()'})

# ❌ FORBIDDEN #8: No error handling
def get_items(self):
    return self.supabase.table('items').select('*').execute().data
    # Missing: try/except, return [] on error
```

---

## ✅ REQUIRED PATTERNS

These patterns are ALWAYS required:

```python
# ✅ REQUIRED #1: Layout as function
def layout(session_data=None):
    return dmc.Stack([...])

# ✅ REQUIRED #2: prevent_initial_call in callbacks
@callback(
    Output(...),
    Input(...),
    prevent_initial_call=True  # ALWAYS
)

# ✅ REQUIRED #3: Error handling in database methods
def get_items(self):
    try:
        # query logic
        return response.data or []
    except Exception as e:
        print(f"Error: {e}")
        return []

# ✅ REQUIRED #4: Company scoping in queries
query = query.eq('company_id', self.company_id)

# ✅ REQUIRED #5: Audit fields in inserts/updates
data = {
    **item_data,
    'created_by': user_id,
    'updated_by': user_id
}

# ✅ REQUIRED #6: Soft delete (not hard delete)
.update({'deleted_at': 'now()'})

# ✅ REQUIRED #7: Debug prints during development
print(f"🔥 callback_name fired - param={value}")
```

---

## 🔍 VERIFICATION COMMANDS

Run these before every commit:

```bash
# Check for static layouts (should return nothing)
grep "^layout = " pages/*.py

# Check for session-store usage (should return nothing)
grep 'State("session-store"' pages/*.py

# Check for missing prevent_initial_call (manual review needed)
grep -A 3 "@callback" pages/*.py | grep -v "prevent_initial_call"

# Syntax check all pages
for file in pages/*.py; do python3 -m py_compile "$file"; done

# Check for hard deletes (should use soft delete)
grep -r "\.delete()" modules/*.py pages/*.py
```

---

## 📚 REFERENCE DOCUMENTATION

When in doubt, check these in order:

1. **This file** (ARCHITECTURE_RULES.md) - Mandatory rules
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Templates and commands
3. **[docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md)** - Patterns and explanations
4. **[docs/TROUBLESHOOTING_LOG.md](docs/TROUBLESHOOTING_LOG.md)** - Known issues
5. **[checkpoint.md](checkpoint.md)** - Recent changes

---

## 🎓 FOR AI ASSISTANTS

**If you are an AI assistant working on this project:**

1. **Read this file FIRST** before making ANY architectural decisions
2. **Never suggest** patterns in the FORBIDDEN section
3. **Always use** templates from the REQUIRED section
4. **Ask the user** if unsure about a pattern (don't guess!)
5. **Run verification commands** before claiming work is complete
6. **Update documentation** when discovering new patterns or issues

**When debugging:**
1. Check TROUBLESHOOTING_LOG.md for known issues first
2. Use debugging methodologies from LESSONS_LEARNED.md
3. Don't repeat failed attempts from previous sessions

**When implementing:**
1. Copy templates from this file EXACTLY
2. Don't modify the core patterns
3. Test incrementally, not all at once

---

## 🔄 UPDATING THIS FILE

**When to update:**
- New architectural pattern discovered (add to REQUIRED or FORBIDDEN)
- New rule needed to prevent regression (add to CRITICAL RULES)
- Better template developed (update template section)
- New verification command needed (add to VERIFICATION)

**How to update:**
1. Add new rule with clear WHY explanation
2. Add verification command if applicable
3. Update date at top of file
4. Cross-reference to LESSONS_LEARNED.md if detailed explanation needed

---

## 📊 COMPLIANCE CHECKLIST

Before merging ANY code to main:

```markdown
- [ ] All layouts are functions (verified with grep)
- [ ] No session-store in page callbacks (verified with grep)
- [ ] All callbacks have prevent_initial_call=True
- [ ] No groups with 3+ buttons
- [ ] All pattern-matching containers have children=[]
- [ ] All database methods have error handling
- [ ] All queries have company_id scoping
- [ ] All inserts/updates have audit fields
- [ ] All deletes are soft deletes
- [ ] Syntax check passed on all files
- [ ] Manual testing completed
- [ ] Debug prints removed or commented
- [ ] Documentation updated
```

---

**Remember**: These rules exist because we learned them the hard way (3+ hours debugging in Session 27). Following them saves time and prevents regressions.

**Last Updated**: November 6, 2025 - Session 28
**Status**: Living document - update as we learn
**Enforcement**: MANDATORY for all code changes
