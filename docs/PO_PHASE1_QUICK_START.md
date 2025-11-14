# PO System Phase 1 - Quick Start Guide

## What You Have

✅ **Complete database schema** ready to deploy
✅ **Vendor management UI** with full CRUD operations
✅ **QuickBooks integration** with OAuth and sync capabilities
✅ **Auto-calculation triggers** for PO totals and job costs
✅ **Comprehensive documentation** and implementation plan

---

## Critical: Database Migration Required

Before you can use any of the new PO system features, you **must** run the database migration in Supabase.

### Quick Migration Steps

1. **Open Supabase Dashboard**
   - Go to https://supabase.com
   - Select your project

2. **Go to SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New query"

3. **Run the Migration**
   - Open: `database/migrations/007_po_system_phase1.sql`
   - Copy ALL contents (the entire file)
   - Paste into Supabase SQL editor
   - Click "Run" or press `Ctrl/Cmd + Enter`

4. **Verify Success**
   - You should see "Success. No rows returned"
   - Check the "Table Editor" to see new tables:
     - vendors
     - purchase_orders
     - po_items
     - po_receiving_history
     - po_payment_history
     - quickbooks_sync_log

---

## Important: Code Needs Supabase Adapter Updates

The vendor management and QuickBooks pages were initially written for direct PostgreSQL, but your app uses **Supabase's Python client**.

### What Needs to Change

The following files need database query updates:
- `pages/vendors.py`
- `pages/quickbooks_settings.py`
- `modules/quickbooks_integration.py`

### Quick Fix Pattern

**Old style (won't work):**
```python
vendors = db.fetch_all("SELECT * FROM vendors")
```

**New style (Supabase):**
```python
response = db.client.table("vendors").select("*").execute()
vendors = response.data
```

### Option 1: Add Database Helper Methods

Add these methods to `modules/database.py`:

```python
def get_all_vendors(self) -> List[Dict]:
    """Get all vendors"""
    try:
        response = self.client.table("vendors").select("*").order("vendor_name").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching vendors: {e}")
        return []

def get_vendor_by_id(self, vendor_id: int) -> Optional[Dict]:
    """Get a single vendor by ID"""
    try:
        response = self.client.table("vendors").select("*").eq("vendor_id", vendor_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching vendor: {e}")
        return None

def insert_vendor(self, vendor_data: Dict, user_id: str) -> Optional[Dict]:
    """Insert a new vendor"""
    try:
        vendor_data['created_by'] = user_id
        response = self.client.table("vendors").insert(vendor_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error inserting vendor: {e}")
        return None

def update_vendor(self, vendor_id: int, updates: Dict, user_id: str) -> bool:
    """Update vendor"""
    try:
        updates['updated_by'] = user_id
        self.client.table("vendors").update(updates).eq("vendor_id", vendor_id).execute()
        return True
    except Exception as e:
        print(f"Error updating vendor: {e}")
        return False
```

### Option 2: Wait for Full Adapter Rewrite

If you want me to rewrite the pages to work with Supabase, that's Phase 1.5 before we move to Phase 2.

---

## What to Do Next

### Choice A: Full Implementation Path
1. Run database migration in Supabase ✅
2. Add vendor database methods to `modules/database.py`
3. Update `pages/vendors.py` to use new methods
4. Update `modules/quickbooks_integration.py`
5. Update `pages/quickbooks_settings.py`
6. Test vendor management
7. Configure QuickBooks (optional)
8. Move to Phase 2 (PO creation)

### Choice B: Quick Test Path
1. Run database migration in Supabase ✅
2. Test directly in Supabase Table Editor
3. Add a few vendors manually
4. Verify foreign keys and triggers work
5. Then do full code updates

### Choice C: Skip to Phase 2
1. Run database migration ✅
2. Skip vendor management UI for now
3. Add vendors directly in Supabase
4. Build PO creation UI next
5. Come back to vendor UI later

---

## Phase 2 Preview (Not Yet Built)

Once Phase 1 is working, Phase 2 will add:

### Purchase Order Creation
- Create PO from existing vendors
- Add multiple line items (glass, hardware, materials)
- Calculate totals automatically
- Link POs to jobs
- Status workflow (Draft → Approved → Sent → Received)

### Receiving
- Mark items as received
- Track quantities
- Quality control notes
- Update job costs automatically

### Payment Tracking
- Record payments against POs
- Track outstanding balances
- Sync payments to QuickBooks

---

## Testing Without Full UI

You can test the database schema immediately after migration:

```sql
-- Add a test vendor
INSERT INTO vendors (vendor_name, vendor_type, email, phone, is_active)
VALUES ('Test Glass Supply', 'Glass', 'test@example.com', '555-1234', TRUE);

-- Verify it worked
SELECT * FROM vendors;

-- Create a test PO
INSERT INTO purchase_orders (
    po_number, vendor_id, po_date, status, total_amount, created_by
) VALUES (
    'PO-TEST-001',
    1,  -- Use the vendor_id from above
    CURRENT_DATE,
    'Draft',
    0.00,
    (SELECT user_id FROM user_profiles LIMIT 1)  -- Use your user ID
);

-- Add a line item
INSERT INTO po_items (
    po_id, line_number, item_type, description,
    quantity, unit_price, line_total
) VALUES (
    1,  -- Use the po_id from above
    1,
    'Glass',
    'Test Glass Panel',
    5,
    100.00,
    500.00
);

-- Check if totals auto-calculated
SELECT * FROM purchase_orders WHERE po_id = 1;
-- Should show subtotal = 500.00, total_amount = 500.00
```

---

## Quick Reference

### File Locations
```
Database Migration:  database/migrations/007_po_system_phase1.sql
Vendor UI:          pages/vendors.py
QB Integration:     modules/quickbooks_integration.py
QB Settings:        pages/quickbooks_settings.py
Migration Helper:   apply_po_migration.py
Full Docs:          docs/PO_PHASE1_IMPLEMENTATION_SUMMARY.md
This Guide:         docs/PO_PHASE1_QUICK_START.md
Original Plan:      docs/PO_SYSTEM_ENHANCEMENT_PLAN.md
```

### New Database Tables
- `vendors` - Vendor information
- `purchase_orders` - PO headers
- `po_items` - PO line items
- `po_receiving_history` - Receiving log
- `po_payment_history` - Payment log
- `quickbooks_sync_log` - QB sync audit trail

### Jobs Table Additions
- `estimated_material_cost` - Estimated cost
- `actual_material_cost` - Actual from POs
- `po_count` - Number of POs for this job
- `materials_ordered` - Boolean flag
- `materials_received` - Boolean flag

---

## Need Help?

**Issue:** Migration fails in Supabase
- Check if tables already exist
- Look for foreign key constraint errors
- Verify user_profiles table exists (for foreign keys)

**Issue:** Vendor page won't load
- Vendors table must exist first (run migration)
- Check browser console for errors
- Database adapter mismatch (see "Code Needs Updates" above)

**Issue:** QuickBooks won't connect
- Need valid Client ID and Secret from developer.intuit.com
- Redirect URI must match exactly
- Check token expiration

---

## Status Summary

| Component | Status | Action Required |
|-----------|--------|-----------------|
| Database Schema | ✅ Ready | Run migration in Supabase |
| Vendor Management | ⚠️ Code complete | Update Supabase adapters |
| QuickBooks Integration | ⚠️ Code complete | Update Supabase adapters |
| PO Creation | ❌ Not built | Phase 2 |
| Receiving | ❌ Not built | Phase 2 |
| Payments | ❌ Not built | Phase 2 |
| Reports | ❌ Not built | Phase 3 |

---

**Ready to proceed?**

Say **"update Supabase adapters"** and I'll rewrite the vendor and QuickBooks pages to work with your Supabase database.

Or say **"start Phase 2"** and I'll begin building the PO creation interface (vendor management can be done manually in Supabase for now).
