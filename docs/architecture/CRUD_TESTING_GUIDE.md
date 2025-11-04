# CRUD Testing Guide - Island Glass CRM
## Session 10 - Company-Scoped Data Model Verification

**Objective:** Test all CRUD operations to verify:
1. Company-scoped data sharing works correctly
2. Audit trails capture user actions (created_by, updated_by, deleted_by)
3. Soft deletes work properly (deleted_at)
4. RLS policies enforce company filtering

---

## Prerequisites

### Before You Start
- [ ] App running at http://localhost:8050
- [ ] Logged in with valid user account
- [ ] Fresh JWT token (log out/in if needed)
- [ ] Supabase dashboard open for database verification

### Test Environment
- **Database:** Supabase (company-scoped schema)
- **User:** Your current logged-in user
- **Company:** Island Glass & Mirror (auto-linked)

---

## Test Plan

### Phase 1: PO Clients CRUD

#### Test 1.1: Add New Client ✅
**What to test:** Create operation with audit trail

**Steps:**
1. Go to http://localhost:8050/po-clients
2. Click "Add New Client" button
3. Fill in form:
   - Company Name: `Test Client Corp`
   - Contact Name: `John Doe`
   - Email: `john@testclient.com`
   - Phone: `(555) 123-4567`
   - Address: `123 Test St`
   - City: `Victoria`
   - Province: `BC`
   - Postal Code: `V8W 1A1`
   - Type: `Contractor`
4. Click "Save Client"

**Expected Results:**
- ✅ Success notification appears
- ✅ New client card appears in list
- ✅ Client displays with all entered information

**Database Verification:**
```sql
-- Run in Supabase SQL Editor
SELECT
  id,
  company_name,
  contact_name,
  company_id,
  created_by,
  created_at,
  updated_by,
  deleted_at
FROM po_clients
WHERE company_name = 'Test Client Corp';
```

**Expected Database State:**
- `company_id`: Should match your company UUID
- `created_by`: Should match your user_id
- `created_at`: Should be current timestamp
- `updated_by`: Should be NULL (no updates yet)
- `deleted_at`: Should be NULL (not deleted)

---

#### Test 1.2: Edit Client ✅
**What to test:** Update operation with audit trail

**Steps:**
1. Find "Test Client Corp" card
2. Click "Edit" button
3. Change:
   - Phone: `(555) 999-8888`
   - Email: `john.doe@testclient.com`
4. Click "Save Changes"

**Expected Results:**
- ✅ Success notification appears
- ✅ Client card updates with new information
- ✅ Updated phone and email display correctly

**Database Verification:**
```sql
SELECT
  company_name,
  phone,
  email,
  created_by,
  updated_by,
  updated_at
FROM po_clients
WHERE company_name = 'Test Client Corp';
```

**Expected Database State:**
- `created_by`: Should remain unchanged (original creator)
- `updated_by`: Should now match your user_id
- `updated_at`: Should be current timestamp
- `phone` and `email`: Should match new values

---

#### Test 1.3: Soft Delete Client ✅
**What to test:** Soft delete with audit trail

**Steps:**
1. Find "Test Client Corp" card
2. Click "Delete" button
3. Confirm deletion in modal

**Expected Results:**
- ✅ Success notification appears
- ✅ Client card disappears from list
- ✅ Client no longer visible in UI

**Database Verification:**
```sql
SELECT
  company_name,
  created_by,
  updated_by,
  deleted_by,
  deleted_at
FROM po_clients
WHERE company_name = 'Test Client Corp';
```

**Expected Database State:**
- Record should STILL EXIST (soft delete)
- `deleted_by`: Should match your user_id
- `deleted_at`: Should be current timestamp
- `created_by` and `updated_by`: Should remain unchanged

**Verify Soft Delete Filter:**
```sql
-- This should return ZERO rows (filtered out)
SELECT *
FROM po_clients
WHERE company_name = 'Test Client Corp'
  AND deleted_at IS NULL;

-- This should return ONE row (shows deleted records)
SELECT *
FROM po_clients
WHERE company_name = 'Test Client Corp';
```

---

### Phase 2: Inventory CRUD

#### Test 2.1: Add New Inventory Item ✅
**What to test:** Create operation with company scoping

**Steps:**
1. Go to http://localhost:8050/inventory
2. Click "Add Item" button
3. Fill in form:
   - Item Name: `Test Spacer Bars`
   - Category: `Spacers`
   - Quantity: `500`
   - Unit: `pcs`
   - Cost per Unit: `0.15`
   - Supplier: (leave blank or select one)
   - Low Stock Threshold: `100`
4. Click "Save Item"

**Expected Results:**
- ✅ Success notification appears
- ✅ New item card appears in list
- ✅ Total Value calculated correctly (500 × $0.15 = $75.00)
- ✅ Low stock badge NOT showing (qty 500 > threshold 100)

**Database Verification:**
```sql
SELECT
  item_name,
  quantity,
  cost_per_unit,
  company_id,
  created_by,
  created_at,
  deleted_at
FROM inventory_items
WHERE item_name = 'Test Spacer Bars';
```

**Expected Database State:**
- `company_id`: Should match your company UUID
- `created_by`: Should match your user_id
- `deleted_at`: Should be NULL

---

#### Test 2.2: Edit Inventory Item ✅
**What to test:** Update operation with audit trail

**Steps:**
1. Find "Test Spacer Bars" card
2. Click "Edit" button
3. Change:
   - Quantity: `80` (below threshold to trigger low stock alert)
   - Cost per Unit: `0.18`
4. Click "Save Changes"

**Expected Results:**
- ✅ Success notification appears
- ✅ Item card updates with new values
- ✅ Total Value recalculated (80 × $0.18 = $14.40)
- ✅ RED "Low Stock" badge appears (qty 80 < threshold 100)

**Database Verification:**
```sql
SELECT
  item_name,
  quantity,
  cost_per_unit,
  created_by,
  updated_by,
  updated_at
FROM inventory_items
WHERE item_name = 'Test Spacer Bars';
```

**Expected Database State:**
- `created_by`: Should remain unchanged
- `updated_by`: Should match your user_id
- `updated_at`: Should be current timestamp

---

#### Test 2.3: Soft Delete Inventory Item ✅
**What to test:** Soft delete with audit trail

**Steps:**
1. Find "Test Spacer Bars" card
2. Click "Delete" button
3. Confirm deletion

**Expected Results:**
- ✅ Success notification appears
- ✅ Item card disappears from list

**Database Verification:**
```sql
SELECT
  item_name,
  deleted_by,
  deleted_at
FROM inventory_items
WHERE item_name = 'Test Spacer Bars';
```

**Expected Database State:**
- Record should STILL EXIST
- `deleted_by`: Should match your user_id
- `deleted_at`: Should be current timestamp

---

### Phase 3: Company Scoping Verification

#### Test 3.1: Verify All Data Has Company ID ✅

**Run this query to check all tables:**
```sql
-- Check PO Clients
SELECT 'po_clients' as table_name, COUNT(*) as total,
       COUNT(DISTINCT company_id) as companies
FROM po_clients;

-- Check Inventory Items
SELECT 'inventory_items' as table_name, COUNT(*) as total,
       COUNT(DISTINCT company_id) as companies
FROM inventory_items;

-- Check Glass Config
SELECT 'glass_config' as table_name, COUNT(*) as total,
       COUNT(DISTINCT company_id) as companies
FROM glass_config;
```

**Expected Results:**
- All counts should show `companies = 1` (single company)
- All records should have the same `company_id`

---

#### Test 3.2: Verify Audit Trails ✅

**Check that audit columns are populated:**
```sql
-- Check created_by is set on all records
SELECT 'Missing created_by' as issue, COUNT(*) as count
FROM po_clients
WHERE created_by IS NULL;

-- Should return 0 rows

-- Check updated_by is set on edited records
SELECT company_name, created_by, updated_by, updated_at
FROM po_clients
WHERE updated_by IS NOT NULL;

-- Should show records that were edited
```

---

#### Test 3.3: Verify Soft Deletes Work ✅

**Check that deleted records are hidden but preserved:**
```sql
-- Count active vs deleted
SELECT
  'Active' as status, COUNT(*) as count
FROM po_clients
WHERE deleted_at IS NULL
UNION ALL
SELECT
  'Deleted' as status, COUNT(*) as count
FROM po_clients
WHERE deleted_at IS NOT NULL;
```

**Expected Results:**
- Active count should exclude deleted records
- Deleted count should include all soft-deleted records
- Deleted records should have `deleted_by` populated

---

## Testing Checklist

### PO Clients
- [ ] Can add new client
- [ ] New client has correct `company_id`
- [ ] New client has `created_by` set to your user_id
- [ ] Can edit existing client
- [ ] Edited client has `updated_by` set to your user_id
- [ ] Can delete client (soft delete)
- [ ] Deleted client has `deleted_by` and `deleted_at` set
- [ ] Deleted client disappears from UI
- [ ] Deleted client still exists in database

### Inventory
- [ ] Can add new item
- [ ] New item has correct `company_id`
- [ ] New item has `created_by` set
- [ ] Can edit existing item
- [ ] Edited item has `updated_by` set
- [ ] Low stock alert triggers correctly
- [ ] Can delete item (soft delete)
- [ ] Deleted item has audit trail
- [ ] Deleted item disappears from UI

### Company Scoping
- [ ] All records belong to same company
- [ ] RLS policies filter by company_id
- [ ] Multiple users see same data (test in Phase 4)

---

## Common Issues & Troubleshooting

### Issue: "JWT expired" error
**Symptom:** Database queries fail with PGRST303 error

**Solution:**
- Log out and log back in to get fresh token
- Token refresh should prevent this automatically
- Check token-refresh-interval is working

---

### Issue: Client/item doesn't appear after adding
**Symptom:** Success notification shows but card doesn't appear

**Possible Causes:**
1. Soft delete filter excluding it (check `deleted_at IS NULL` in query)
2. Company_id mismatch (check database directly)
3. Frontend state not refreshing (reload page)

**Debug:**
```sql
-- Check if record exists
SELECT * FROM po_clients
ORDER BY created_at DESC
LIMIT 5;
```

---

### Issue: Audit trail not populating
**Symptom:** `created_by` or `updated_by` is NULL

**Possible Causes:**
1. User not logged in properly
2. Session data missing user_id
3. Database method not receiving user_id parameter

**Debug:**
- Check browser console for errors
- Add debug logging to callback
- Verify session-store has user data

---

## Success Criteria

All tests pass when:
1. ✅ All CRUD operations work without errors
2. ✅ All records have correct `company_id`
3. ✅ Audit trails capture all user actions
4. ✅ Soft deletes preserve data with proper flags
5. ✅ UI correctly filters out deleted records
6. ✅ Database queries confirm company scoping

---

## Next Steps After Testing

Once CRUD tests pass:
1. **Multi-User Testing** (Session 11)
   - Create 2nd user account
   - Verify both users see same data
   - Test concurrent editing

2. **Phase 2 Features**
   - PO detail pages
   - Client detail pages
   - Activity logging
   - Comments system

3. **Production Readiness**
   - User onboarding documentation
   - Admin pricing UI
   - PDF quote generation
   - Email integration

---

**Testing Date:** ___________
**Tester:** ___________
**Results:** ___________
