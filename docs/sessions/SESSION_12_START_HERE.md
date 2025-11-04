# Session 12 - Start Here 👈

## Before You Begin

**Read these in order:**

1. 📄 **THIS FILE** - You're here!
2. 📋 **SESSION_11_QUICK_REFERENCE.md** - 2-minute overview
3. 📖 **SESSION_11_WINDOW_MANUFACTURING_PLAN.md** - Complete spec (15-20 min read)

---

## What Happened Last Session

✅ Complete planning session
✅ Window manufacturing system fully specified
✅ All documentation created
❌ No code written yet (planning only)

---

## Critical Blocker

⚠️ **PO Clients UI is BROKEN** - Must fix first!

**Problem**: Add Client form uses old `company_name` field (doesn't exist anymore)
**Fix Time**: 15 minutes
**Instructions**: See `NEXT_SESSION_PLAN.md` Phase 1

---

## Today's Goals (6-8 hours)

### Part 1: Fix PO Clients (15 min)
- [ ] Update form field: `company_name` → `client_name`
- [ ] Add primary contact fields
- [ ] Fix save callback
- [ ] Test add client functionality

### Part 2: Build Window System (5-7 hours)
- [ ] Phase 2: User roles & permissions (30 min)
- [ ] Phase 3: Database schema - 4 tables (45 min)
- [ ] Phase 4: Backend modules (1-1.5 hrs)
- [ ] Phase 5: UI pages - 3 pages (2-3 hrs)
- [ ] Phase 6: Navigation & access control (30 min)
- [ ] Phase 7: Testing & polish (1 hr)

---

## Quick Command Reference

```bash
# Start server (if not running)
python3 dash_app.py

# Check for running servers
ps aux | grep "dash_app\|python"

# Kill old servers if needed
pkill -f dash_app.py
```

---

## Implementation Order

```
1. Read NEXT_SESSION_PLAN.md Phase 1
2. Fix pages/po_clients.py (company_name → client_name)
3. Test PO Client add/edit works
4. Read SESSION_11_WINDOW_MANUFACTURING_PLAN.md
5. Execute Phases 2-7 sequentially
6. Test each phase before moving to next
```

---

## Files You'll Create Today

**SQL:**
- `add_user_roles_and_departments.sql`
- `window_manufacturing_schema.sql`
- `window_manufacturing_seed_data.sql`

**Python Modules:**
- `modules/permissions.py`
- `modules/zpl_generator.py`
- `modules/label_printer.py`

**UI Pages:**
- `pages/window_order_entry.py`
- `pages/window_order_management.py`
- `pages/window_label_printing.py`

**Docs:**
- `WINDOW_MANUFACTURING_GUIDE.md`
- `SESSION_12_SUMMARY.md`

---

## Files You'll Modify Today

- `pages/po_clients.py` (fix forms)
- `modules/database.py` (add window methods)
- `dash_app.py` (routes, navigation)

---

## Key Technical Details

**Measurements:**
- Always inches
- Fraction support required (use existing fraction_utils.py)
- Order: Thickness < Width < Height

**Labels:**
- Zebra ZD421 printer
- 3x2 inch labels
- 1 label per window (4 windows = 4 labels)
- ZPL format

**Access Control:**
- Owners: Everything
- Manufacturing Admin: All window features
- IG Admin: Everything except window manufacturing
- IG Employee: Window ordering only

**Database:**
- Use Supabase (existing)
- Company_id scoping
- Audit trails on all tables
- Soft deletes

---

## Testing Checklist

### After Part 1 (PO Fix):
- [ ] Can open Add Client modal
- [ ] Can enter client name and contact
- [ ] Save creates both client and contact
- [ ] Client cards display correctly

### After Part 2 (Window System):
- [ ] Navigation shows/hides based on role
- [ ] Can create multi-window order
- [ ] Fractions parse correctly
- [ ] Customer autocomplete works
- [ ] ZPL labels generate
- [ ] Print queue displays
- [ ] Mock printer saves .zpl files

---

## If You Get Stuck

**Common Issues:**

1. **Import errors**: Check `dash_app.py` has all imports
2. **Database errors**: Verify migration ran successfully
3. **RLS errors**: Check user_id/company_id in queries
4. **Token expired**: User may need to re-login

**Documentation:**
- Full spec: `SESSION_11_WINDOW_MANUFACTURING_PLAN.md`
- Database methods: `modules/database.py` (line 36+)
- Existing fraction utils: `modules/fraction_utils.py`

---

## Open Questions (Optional)

Can provide later if needed:
- Complete window shape types list
- Actual printer IP address
- Sister company name
- Label branding requirements

For now: Use defaults/mock data

---

## Ready?

1. ✅ Read SESSION_11_QUICK_REFERENCE.md
2. ✅ Read SESSION_11_WINDOW_MANUFACTURING_PLAN.md
3. ✅ Start with NEXT_SESSION_PLAN.md Phase 1
4. ✅ Then execute window system phases 2-7

---

**Let's build!** 🚀

Type "ready to start" when you've read the docs and are ready to begin.
