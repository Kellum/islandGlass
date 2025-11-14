# Island Glass CRM - Quick Reference

**Purpose**: Fast command reference and common task guide for daily development.

**Last Updated**: November 6, 2025 - Session 28

---

## 🚀 Daily Workflow Commands

### Start Development

```bash
# Start the Dash application
python3 dash_app.py

# Open in browser
open http://localhost:8050

# Stop application
# Press Ctrl+C in terminal
```

### Check Application Status

```bash
# Verify Python syntax
python3 -m py_compile pages/my_page.py

# Check for static layout pattern issues
grep -n "^layout = " pages/*.py

# Find all modals in project
grep -r "dmc.Modal" pages/

# Check recent git changes
git status
git diff
```

---

## 🔍 Common Debugging Commands

### When Callbacks Don't Fire

```bash
# 1. Check if callbacks are registered
python3 dash_app.py | grep "callback has been registered"

# 2. Find callback definitions
grep -n "@callback" pages/my_page.py

# 3. Check for session-store in page modules (should be empty!)
grep -r "State(\"session-store\"" pages/

# 4. Check for layout pattern issue
head -30 pages/my_page.py | grep "^layout"
```

### Search Documentation

```bash
# Find solutions for modal issues
grep -r "modal" docs/LESSONS_LEARNED.md

# Search troubleshooting log
grep -A 10 "silent failure" docs/TROUBLESHOOTING_LOG.md

# Find session where feature was added
grep -r "calculator" docs/sessions/

# Check what changed recently
tail -100 checkpoint.md
```

---

## 📝 Code Snippets

### New Page Template

```python
"""
Page Name
Brief description of what this page does
"""

import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, ctx
from dash_iconify import DashIconify
from modules.database import get_authenticated_db

# ✅ ALWAYS use layout function, NEVER static layout variable
def layout(session_data=None):
    return dmc.Stack([
        # Header
        dmc.Title("Page Title", order=1),
        dmc.Text("Page description", c="dimmed", size="sm"),

        # Content
        html.Div(id="page-content"),

        # Modals, stores, etc.
    ], gap="md")


# Callbacks
@callback(
    Output("page-content", "children"),
    Input("some-trigger", "n_clicks"),
    State("some-input", "value"),
    prevent_initial_call=True
)
def update_content(n_clicks, value):
    print(f"DEBUG: Callback triggered - n_clicks={n_clicks}")
    # ... logic here
    return "Updated content"
```

### Modal Template

```python
# In layout function:
dmc.Modal(
    id="my-modal",
    title="Modal Title",
    size="lg",
    children=[
        dmc.Stack([
            # Form fields
            dmc.TextInput(id="field-1", label="Field 1", required=True),
            dmc.TextInput(id="field-2", label="Field 2"),

            # Action buttons (max 2 per Group!)
            dmc.Group([
                dmc.Button("Cancel", id="cancel-btn", variant="subtle", color="gray"),
                dmc.Button("Submit", id="submit-btn", color="blue")
            ], justify="flex-end")
        ], gap="md")
    ]
)

# Toggle callback
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

# Submit callback
@callback(
    Output("my-modal", "opened", allow_duplicate=True),
    Output("notification", "children"),
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
        return dash.no_update, dmc.Notification(
            title="Error",
            message="Field 1 is required",
            color="red",
            action="show"
        )

    # Save to database
    # ...

    # Close modal, show success
    return False, dmc.Notification(
        title="Success",
        message="Saved successfully",
        color="green",
        action="show"
    )
```

### Database Method Template

```python
def get_items(self, filters=None):
    """Fetch items with optional filtering"""
    try:
        query = self.supabase.table('items').select('*')

        if self.company_id:
            query = query.eq('company_id', self.company_id)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        response = query.execute()
        return response.data or []
    except Exception as e:
        print(f"Error fetching items: {e}")
        return []


def insert_item(self, item_data, user_id=None):
    """Insert new item with audit trail"""
    try:
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
```

---

## ✅ Checklists

### Pre-Commit Checklist

- [ ] All callbacks have `prevent_initial_call=True`
- [ ] No `State("session-store", "data")` in page modules
- [ ] All pages use `def layout(session_data=None):` pattern
- [ ] No more than 2 buttons in any `dmc.Group`
- [ ] All modals have working toggle and submit callbacks
- [ ] Database methods include company_id and audit fields
- [ ] Debug prints removed or commented out
- [ ] Tested all modified features manually

### New Feature Checklist

- [ ] Design reviewed and approved
- [ ] Database migration created (if needed)
- [ ] Backend methods implemented and tested
- [ ] Frontend page/component created
- [ ] Callbacks implemented with error handling
- [ ] Modal buttons tested (if applicable)
- [ ] Session added to checkpoint.md
- [ ] Documentation updated (if architectural changes)

### Debugging Session Checklist

- [ ] Issue reproduced consistently
- [ ] Symptoms documented in notes
- [ ] Checked TROUBLESHOOTING_LOG.md for known issues
- [ ] Added debug prints to callbacks
- [ ] Checked browser console for errors
- [ ] Verified callback registration at startup
- [ ] Tested with minimal callback
- [ ] Solution documented (if new issue)

---

## 🔧 Common Fixes

### Modal Button Not Working

```bash
# 1. Check layout pattern
head -30 pages/my_page.py

# If you see: layout = dmc.Stack([...])
# Fix: Convert to function

# 2. Verify callback registration
python3 dash_app.py | grep "my_callback has been registered"

# 3. Add debug print
# In callback: print(f"🔥 CALLBACK FIRED - n_clicks={n_clicks}")
```

### Callback Blocked by Session Store

```python
# ❌ REMOVE this from page module callbacks:
State("session-store", "data")

# ✅ REPLACE with direct instantiation:
from modules.database import Database
db = Database()
user_id = None  # TODO: Get from URL or other source
```

### Third Button Not Working

```python
# ❌ BROKEN (3 buttons)
dmc.Group([
    dmc.Button("Cancel", ...),
    dmc.Button("Test", ...),
    dmc.Button("Submit", ...)  # Won't work!
])

# ✅ FIXED (2 buttons)
dmc.Group([
    dmc.Button("Cancel", ...),
    dmc.Button("Submit", ...)  # Works!
])
```

---

## 📊 Database Commands

### Run Migration

```bash
# 1. Go to Supabase dashboard: https://supabase.com
# 2. Select project
# 3. Click "SQL Editor"
# 4. Open migration file: database/migrations/XXX_migration_name.sql
# 5. Copy contents
# 6. Paste and click "Run"
```

### Query Data Directly

```bash
# In Supabase SQL Editor:

-- View all clients
SELECT * FROM po_clients WHERE deleted_at IS NULL;

-- View recent jobs
SELECT * FROM jobs ORDER BY created_at DESC LIMIT 10;

-- Check user audit trail
SELECT created_by, updated_by, created_at FROM jobs WHERE id = 'job-uuid';
```

---

## 🎯 Quick Navigation

| I Need To... | Go To... |
|--------------|----------|
| **Know what rules to follow** ⭐ | **[ARCHITECTURE_RULES.md](ARCHITECTURE_RULES.md)** |
| Learn best practices | [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md) |
| Fix a known issue | [docs/TROUBLESHOOTING_LOG.md](docs/TROUBLESHOOTING_LOG.md) |
| Check what changed | [checkpoint.md](checkpoint.md) |
| Find all documentation | [docs/README.md](docs/README.md) |
| Understand Jobs/PO system | [docs/REVISED_PO_SYSTEM_SUMMARY.md](docs/REVISED_PO_SYSTEM_SUMMARY.md) |
| See this session's changes | Top of [checkpoint.md](checkpoint.md) |

---

## 🚨 Emergency Troubleshooting

### App Won't Start

```bash
# Check for syntax errors
python3 -m py_compile dash_app.py
python3 -m py_compile pages/*.py

# Check for import errors
python3 -c "from pages import po_clients"

# Verify dependencies
pip3 list | grep dash
```

### Callbacks Not Firing at All

```bash
# 1. Check layout pattern
grep -n "^layout = " pages/*.py

# 2. Check for session-store usage
grep -r "State(\"session-store\"" pages/

# 3. Verify callback registration
python3 dash_app.py | grep "callback has been registered"
```

### Database Connection Issues

```python
# In dash_app.py or database.py:
# Check environment variables
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:10]}...")

# Test connection
from modules.database import Database
db = Database()
result = db.supabase.table('companies').select('*').limit(1).execute()
print(f"Connection test: {result.data}")
```

---

## 📞 Help Resources

**In Order of Speed:**

1. **This File** - Quick commands and common fixes (← You are here!)
2. **[docs/TROUBLESHOOTING_LOG.md](docs/TROUBLESHOOTING_LOG.md)** - Known issues with solutions
3. **[docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md)** - Comprehensive patterns and debugging methods
4. **[checkpoint.md](checkpoint.md)** - Recent changes and session history
5. **[docs/README.md](docs/README.md)** - Full documentation index

**Remember**: Most issues have been seen before. Check the docs first! 📚

---

**Last Updated**: November 6, 2025 - Session 28
**Maintained By**: Development Team
