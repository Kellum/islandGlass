# Next Session Plan - Dynamic Client Form Implementation

## Session 11 Objectives

**Goal:** Update `pages/po_clients.py` to work with new `client_name` schema and multiple contacts system

**Estimated Time:** 45-60 minutes for basic functionality, 1-2 hours for full multi-contact UI

---

## Phase 1: Quick Fix (15 minutes) - GET IT WORKING

### Priority: Critical - App Currently Broken

**What to Change:**
1. Replace all `company_name` references with `client_name`
2. Update Add Client callback to create client + primary contact
3. Update Client Cards to display `client_name`

**Specific Changes:**

### File: `pages/po_clients.py`

#### Change 1: Update Modal Form Field
**Location:** Lines 83-88
```python
# OLD:
dmc.TextInput(
    id="new-client-company",
    label="Company Name",
    placeholder="Enter company name",
    required=True
),

# NEW:
dmc.TextInput(
    id="new-client-name",
    label="Client Name",
    placeholder="Enter name or company name",
    required=True
),
```

#### Change 2: Add Primary Contact Fields
**Location:** After line 93 (after client name input)
```python
# Add section divider
dmc.Divider(label="Primary Contact", labelPosition="center"),

dmc.Grid([
    dmc.GridCol([
        dmc.TextInput(
            id="new-contact-first",
            label="First Name",
            placeholder="John",
            required=True
        )
    ], span=6),
    dmc.GridCol([
        dmc.TextInput(
            id="new-contact-last",
            label="Last Name",
            placeholder="Doe",
            required=True
        )
    ], span=6),
]),

dmc.Grid([
    dmc.GridCol([
        dmc.TextInput(
            id="new-contact-email",
            label="Contact Email",
            placeholder="john@company.com"
        )
    ], span=6),
    dmc.GridCol([
        dmc.TextInput(
            id="new-contact-phone",
            label="Contact Phone",
            placeholder="(555) 123-4567"
        )
    ], span=6),
]),

dmc.TextInput(
    id="new-contact-jobtitle",
    label="Job Title / Role",
    placeholder="Project Manager, Owner, etc."
),
```

#### Change 3: Update Save Callback
**Location:** Around lines 260-290 (find the `add_new_client` callback)

**Current callback State inputs:** Look for line with `State("new-client-company", "value")`

**OLD State inputs:**
```python
State("new-client-company", "value"),
State("new-client-contact", "value"),
```

**NEW State inputs:**
```python
State("new-client-name", "value"),
State("new-client-type", "value"),
State("new-contact-first", "value"),
State("new-contact-last", "value"),
State("new-contact-email", "value"),
State("new-contact-phone", "value"),
State("new-contact-jobtitle", "value"),
```

**Update callback function signature:**
```python
def add_new_client(
    n_clicks, opened, session_data,
    client_name, client_type,  # Changed from company_name
    contact_first, contact_last, contact_email, contact_phone, contact_jobtitle,  # New
    email, phone, address, city, state, zip_code
):
```

**Update save logic:**
```python
# Validate required fields
if not client_name or not contact_first or not contact_last:
    return dash.no_update, dmc.Notification(
        title="Validation Error",
        message="Client name and contact first/last name are required",
        color="red",
        icon=DashIconify(icon="solar:close-circle-bold")
    )

# Get authenticated database
db = get_authenticated_db(session_data)
user_id = session_data.get('user', {}).get('id')

if not user_id:
    return dash.no_update, dmc.Notification(
        title="Authentication Error",
        message="User not authenticated",
        color="red"
    )

# Create client
client_data = {
    'client_name': client_name,
    'client_type': client_type or 'contractor',
    'email': email,
    'phone': phone,
    'address': address,
    'city': city,
    'state': state,
    'zip': zip_code
}

client = db.insert_po_client(client_data, user_id)

if not client:
    return dash.no_update, dmc.Notification(
        title="Error",
        message="Failed to create client",
        color="red"
    )

# Create primary contact
contact_data = {
    'client_id': client['id'],
    'first_name': contact_first,
    'last_name': contact_last,
    'email': contact_email,
    'phone': contact_phone,
    'job_title': contact_jobtitle,
    'is_primary': True
}

contact = db.insert_client_contact(contact_data, user_id)

if not contact:
    # Rollback: delete the client
    db.delete_po_client(client['id'], user_id)
    return dash.no_update, dmc.Notification(
        title="Error",
        message="Failed to create contact",
        color="red"
    )

return False, dmc.Notification(
    title="Success",
    message=f"Client '{client_name}' added successfully",
    color="green",
    icon=DashIconify(icon="solar:check-circle-bold")
)
```

#### Change 4: Update Client Cards Display
**Location:** Find the function that generates client cards (around line 180-250)

Look for references to `client.get('company_name')` and replace with:
```python
client.get('client_name')
```

Also update the card to show primary contact:
```python
# After client name, add:
# Get primary contact
primary = db.get_primary_contact(client['id'])
if primary:
    contact_text = f"📞 {primary['full_name']}"
    if primary.get('email'):
        contact_text += f" • {primary['email']}"
```

---

## Phase 2: Dynamic Form Behavior (30 minutes)

### Goal: Show different fields based on Client Type

**What to Add:**

### 1. Move Client Type to Top of Form
**Location:** Before client name field
```python
dmc.Select(
    id="new-client-type",
    label="Client Type",
    placeholder="Select client type",
    data=[
        {"value": "residential", "label": "Residential"},
        {"value": "contractor", "label": "Contractor"},
        {"value": "commercial", "label": "Commercial"}
    ],
    required=True,
    description="Choose the type of client"
),

dmc.Space(h="sm"),
```

### 2. Add Dynamic Client Name Section
Replace the simple "Client Name" field with:
```python
# Container for dynamic client name fields
html.Div(id="client-name-fields-container"),
```

### 3. Add Callback to Show/Hide Fields
```python
@callback(
    Output("client-name-fields-container", "children"),
    Input("new-client-type", "value")
)
def update_client_name_fields(client_type):
    if not client_type:
        return dmc.Alert(
            "Please select a client type first",
            color="blue",
            icon=DashIconify(icon="solar:info-circle-bold")
        )

    if client_type == "residential":
        # For residential: First + Last Name
        return dmc.Stack([
            dmc.Text("Client Name", size="sm", fw=500),
            dmc.Grid([
                dmc.GridCol([
                    dmc.TextInput(
                        id="new-client-first",
                        placeholder="First Name",
                        required=True
                    )
                ], span=6),
                dmc.GridCol([
                    dmc.TextInput(
                        id="new-client-last",
                        placeholder="Last Name",
                        required=True
                    )
                ], span=6),
            ])
        ])
    else:
        # For contractor/commercial: Company Name
        return dmc.TextInput(
            id="new-client-company",
            label="Company Name",
            placeholder="Enter company name",
            required=True
        )
```

### 4. Update Save Callback
Modify the callback to handle both cases:
```python
# Add to State inputs:
State("new-client-first", "value"),  # For residential
State("new-client-last", "value"),   # For residential
State("new-client-company", "value"), # For commercial/contractor

# In callback logic:
if client_type == "residential":
    if not client_first or not client_last:
        return error...
    client_name = f"{client_first} {client_last}"
else:
    if not company_name:
        return error...
    client_name = company_name
```

---

## Phase 3: Multiple Contacts UI (1 hour)

### Goal: Allow adding multiple contacts per client

**Components Needed:**

### 1. Additional Contacts Section
Add after primary contact:
```python
dmc.Divider(label="Additional Contacts (Optional)", labelPosition="center"),

html.Div(id="additional-contacts-list"),

dmc.Button(
    "Add Another Contact",
    id="add-contact-button",
    variant="subtle",
    leftSection=DashIconify(icon="solar:add-circle-bold"),
    fullWidth=True
),

# Hidden store for contacts data
dcc.Store(id="contacts-store", data=[])
```

### 2. Add Contact Callback
```python
@callback(
    Output("additional-contacts-list", "children"),
    Output("contacts-store", "data"),
    Input("add-contact-button", "n_clicks"),
    State("contacts-store", "data"),
    prevent_initial_call=True
)
def add_contact_card(n_clicks, contacts):
    if not contacts:
        contacts = []

    contact_id = len(contacts)
    contacts.append({'id': contact_id})

    # Generate contact cards
    cards = []
    for i, contact in enumerate(contacts):
        cards.append(
            dmc.Card([
                dmc.Group([
                    dmc.Text(f"Contact #{i+1}", fw=500),
                    dmc.ActionIcon(
                        DashIconify(icon="solar:trash-bin-bold"),
                        id={'type': 'remove-contact', 'index': i},
                        color="red",
                        variant="subtle"
                    )
                ], justify="space-between"),

                dmc.Grid([
                    dmc.GridCol([
                        dmc.TextInput(
                            id={'type': 'contact-first', 'index': i},
                            placeholder="First Name"
                        )
                    ], span=6),
                    dmc.GridCol([
                        dmc.TextInput(
                            id={'type': 'contact-last', 'index': i},
                            placeholder="Last Name"
                        )
                    ], span=6),
                ]),

                # ... email, phone, job title fields ...
            ], withBorder=True, p="sm", mb="sm")
        )

    return cards, contacts
```

### 3. Update Save to Handle Multiple Contacts
```python
# After creating client and primary contact:

# Get additional contacts from pattern-matching inputs
ctx_inputs = ctx.inputs_list
additional_contacts = []

for input_group in ctx_inputs:
    if input_group.get('id', {}).get('type') == 'contact-first':
        index = input_group['id']['index']
        # Collect all fields for this contact...
        additional_contacts.append({...})

# Save additional contacts
for contact_data in additional_contacts:
    contact_data['client_id'] = client['id']
    contact_data['is_primary'] = False
    db.insert_client_contact(contact_data, user_id)
```

---

## Testing Checklist

### Phase 1 Testing:
- [ ] Modal opens without errors
- [ ] Can enter client name and contact info
- [ ] Save button creates client record
- [ ] Save button creates primary contact record
- [ ] Success notification appears
- [ ] Client card displays with client_name
- [ ] Primary contact shows on card

### Phase 2 Testing:
- [ ] Client Type dropdown appears first
- [ ] Selecting "Residential" shows First/Last Name fields
- [ ] Selecting "Contractor" shows Company Name field
- [ ] Validation requires correct fields based on type
- [ ] Residential saves as "FirstName LastName"
- [ ] Contractor saves as company name

### Phase 3 Testing:
- [ ] "Add Another Contact" button works
- [ ] Can add multiple contact cards
- [ ] Can remove contact cards
- [ ] All contacts save to database
- [ ] Only one contact marked as primary
- [ ] Contact count shows on client card

---

## File Locations Reference

```
pages/po_clients.py:
  Line 76-165:   Add Client Modal (form fields)
  Line ~260-290: add_new_client callback (save logic)
  Line ~180-250: Client cards generation (display logic)
  Line ~300-350: Search/filter callbacks

modules/database.py:
  Line 505-512:  get_all_po_clients()
  Line 523-551:  search_po_clients()
  Line 690-703:  get_client_contacts()
  Line 705-717:  get_primary_contact()
  Line 719-744:  insert_client_contact()
```

---

## Common Pitfalls to Avoid

1. **Don't forget to import `get_authenticated_db`** - Already imported, but verify
2. **User ID required** - All insert/update/delete methods need user_id parameter
3. **Pattern-matching IDs** - Use `{'type': 'contact-first', 'index': i}` format
4. **Validation** - Check both client data AND contact data before saving
5. **Error handling** - If contact save fails, rollback client creation
6. **Soft deletes** - Use `is_("deleted_at", "null")` in queries
7. **Primary contact** - Always set `is_primary=True` for first contact

---

## Quick Reference: Database Methods

```python
# Get authenticated database
from modules.database import get_authenticated_db
db = get_authenticated_db(session_data)

# Insert client
client = db.insert_po_client({
    'client_name': 'ABC Corp',
    'client_type': 'commercial',
    'email': 'info@abc.com',
    'phone': '(555) 123-4567',
    'address': '123 Main St',
    'city': 'Victoria',
    'state': 'BC',
    'zip': 'V8W 1A1'
}, user_id)

# Insert contact
contact = db.insert_client_contact({
    'client_id': client['id'],
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@abc.com',
    'phone': '(555) 987-6543',
    'job_title': 'Project Manager',
    'is_primary': True
}, user_id)

# Get contacts
contacts = db.get_client_contacts(client_id)
primary = db.get_primary_contact(client_id)

# Update contact
db.update_client_contact(contact_id, {
    'email': 'newemail@abc.com',
    'job_title': 'Senior PM'
}, user_id)

# Set primary
db.set_primary_contact(client_id, contact_id, user_id)

# Delete contact
db.delete_client_contact(contact_id, user_id)
```

---

**Ready to implement!** Start with Phase 1 to get basic functionality working, then add Phases 2 & 3 as time permits.
