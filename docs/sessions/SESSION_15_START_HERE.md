# Session 15 - Start Here 👈

**Previous Session:** Session 14 - Pages Built & Migrations Complete
**Current Status:** 95% Complete - Ready for Testing & Deployment
**Estimated Time:** 1-2 hours to final polish

---

## 📖 Before You Begin

**Read in this order:**
1. **THIS FILE** ← You're here
2. `SESSION_14_COMPLETE.md` - Full session 14 details
3. `checkpoint.md` - Quick project overview

---

## ✅ What's Already Done (Session 14)

**Pages (100% Complete):**
- ✅ Window Order Entry page
- ✅ Window Order Management page
- ✅ Window Label Printing page
- ✅ Navigation integrated in sidebar

**Database (100% Complete):**
- ✅ All 4 migrations run successfully
- ✅ Window manufacturing tables created
- ✅ User roles & departments configured
- ✅ Reference data populated
- ✅ Default printer configured

**Project Organization (100% Complete):**
- ✅ Reorganized from 85 → 15 root files
- ✅ Git initialized and pushed to GitHub
- ✅ Comprehensive documentation created
- ✅ Database README with migration guide
- ✅ CONTRIBUTING.md for developers

**Server Status:**
- Dash app running on http://localhost:8050
- If not, restart with: `python3 dash_app.py`

---

## 🎯 Today's Objectives

### 1. Testing (30-60 min)

**End-to-End Workflow Test:**
- [ ] Create a window order
- [ ] View order in Order Management
- [ ] Update order status
- [ ] View labels in Label Printing
- [ ] Print labels (mock mode)
- [ ] Verify print history

**Edge Cases to Test:**
- [ ] Multiple windows in one order
- [ ] Different window types (Rectangle, Circle, etc.)
- [ ] Fraction measurements (1 1/2", 3/4")
- [ ] Status workflow (pending → in_production → completed)
- [ ] Permission checks (if multiple users)

### 2. Bug Fixes (As Needed)

Based on testing, fix any issues discovered:
- UI/UX improvements
- Error handling
- Data validation
- Performance optimization

### 3. Polish (30 min)

**Optional Enhancements:**
- [ ] Add edit order functionality
- [ ] Add delete order (soft delete)
- [ ] Add label reprint from history
- [ ] Add customer linking to po_clients
- [ ] Add order search/filtering improvements
- [ ] Add bulk status updates

### 4. Deployment Prep (Optional)

If ready for production:
- [ ] Environment variables check
- [ ] Database backup
- [ ] Railway deployment config
- [ ] Production testing plan

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
open http://localhost:8050/window-order-management
open http://localhost:8050/window-label-printing

# Check database
# (Run in Supabase SQL Editor)
SELECT COUNT(*) FROM window_orders;
SELECT COUNT(*) FROM window_labels;
```

---

## 📂 Key Files Reference

### Pages
```
pages/window_order_entry.py         - Order creation form
pages/window_order_management.py    - View/manage orders
pages/window_label_printing.py      - Print queue & labels
```

### Modules
```
modules/database.py                 - 16 window methods
modules/zpl_generator.py            - Label ZPL generation
modules/label_printer.py            - Printer interface (mock)
modules/permissions.py              - Role-based access
modules/fraction_utils.py           - Measurement parsing
```

### Database
```
database/migrations/001_initial_schema.sql           - Base tables
database/migrations/002_user_roles_departments.sql   - Roles/depts
database/migrations/003_window_manufacturing.sql     - Window tables
database/migrations/004_window_seed_data.sql         - Reference data
```

### Documentation
```
checkpoint.md                       - Quick reference
README.md                          - Project overview
CONTRIBUTING.md                    - Developer guide
docs/sessions/SESSION_14_COMPLETE.md - Last session
database/README.md                 - Migration guide
```

---

## 🔍 Testing Checklist

### Create Order Test
- [ ] Navigate to Order Entry page
- [ ] Select/create PO client
- [ ] Enter customer name
- [ ] Add 2-3 windows with different types
- [ ] Use fraction measurements (e.g., 1 1/2")
- [ ] Add notes
- [ ] Submit order
- [ ] Verify success notification
- [ ] Check order appears in database

### View Order Test
- [ ] Navigate to Order Management page
- [ ] See created order in list
- [ ] Verify order details correct
- [ ] Expand order to view items
- [ ] Check window items display correctly
- [ ] Verify measurements shown as fractions

### Update Status Test
- [ ] Click "Update Status" button
- [ ] Change status to "in_production"
- [ ] Verify status updated
- [ ] Check badge color changed
- [ ] Verify timestamp updated

### Label Printing Test
- [ ] Navigate to Label Printing page
- [ ] See labels in print queue
- [ ] Verify labels grouped by PO
- [ ] Click preview on a label
- [ ] Verify ZPL code displays
- [ ] Print single label
- [ ] Check .zpl file created in labels_output/
- [ ] Print all pending
- [ ] Verify print history updated
- [ ] Check label status changed to "printed"

### Filter/Search Test
- [ ] Filter orders by status
- [ ] Search by PO number
- [ ] Filter by date range
- [ ] Clear filters
- [ ] Verify results update correctly

---

## 🐛 Known Issues / Watch For

### Potential Issues to Check
1. **Session expiration** - Token refresh working?
2. **Permission errors** - RLS policies correct?
3. **Fraction parsing** - Edge cases handled?
4. **Large orders** - Performance with 10+ windows?
5. **Concurrent users** - Multi-user testing needed?

### If You Encounter Errors

**"Not authenticated":**
- Check session_data is passed to layout
- Verify Supabase credentials in .env

**"Company ID not found":**
- Check user_profile has company_id
- Verify user is logged in

**Empty queries:**
- Check RLS policies active
- Verify company_id being passed

**Label printing fails:**
- Check labels_output/ directory exists
- Verify permissions on directory
- Check ZPL generator working

---

## 💡 Implementation Patterns

### Database Access
```python
from modules.database import get_authenticated_db

db = get_authenticated_db(session_data)
company_id = session_data.get('user_profile', {}).get('company_id')
user_id = session_data.get('user', {}).get('id')

# Get orders
orders = db.get_window_orders(company_id, status="pending")

# Update status
db.update_window_order_status(order_id, "in_production", user_id)
```

### Permission Checks
```python
from modules.permissions import get_user_window_permissions

user_profile = session_data.get('user_profile', {})
perms = get_user_window_permissions(user_profile)

if perms.can_manage_orders():
    # Show management controls
```

### Label Generation
```python
from modules.zpl_generator import ZPLGenerator
from modules.label_printer import LabelPrinter

generator = ZPLGenerator()
zpl = generator.generate_window_label(
    po_number="2024-11-001",
    window_data=item_data,
    label_number=1,
    total_labels=4
)

printer = LabelPrinter(mock_mode=True)
success, message = printer.print_label(zpl)
```

---

## 📊 Success Criteria

**Minimum to Complete:**
- [ ] Can create orders successfully
- [ ] Can view orders in management page
- [ ] Can update order status
- [ ] Can view labels in print queue
- [ ] Can print labels (mock mode)
- [ ] No critical bugs

**Nice to Have:**
- [ ] Smooth UI/UX
- [ ] All edge cases handled
- [ ] Performance optimized
- [ ] Ready for production

---

## 🚢 Deployment Checklist (Optional)

If deploying to production:

### Pre-Deployment
- [ ] All tests passing
- [ ] No known critical bugs
- [ ] Environment variables documented
- [ ] Database backup created
- [ ] Rollback plan ready

### Railway Deployment
- [ ] Connect GitHub repository
- [ ] Configure environment variables
- [ ] Set up PostgreSQL database
- [ ] Deploy application
- [ ] Run smoke tests
- [ ] Monitor logs

### Post-Deployment
- [ ] Verify all pages load
- [ ] Test critical workflows
- [ ] Check database connectivity
- [ ] Monitor error logs
- [ ] Set up monitoring/alerts

---

## 🔗 Useful Links

**Application:**
- http://localhost:8050 - Development server
- http://localhost:8050/window-order-entry - Order Entry
- http://localhost:8050/window-order-management - Order Management
- http://localhost:8050/window-label-printing - Label Printing

**Tools:**
- http://labelary.com/viewer.html - ZPL label viewer
- https://supabase.com/dashboard - Database management

**Documentation:**
- [Dash Mantine Components](https://dash-mantine-components.com/)
- [Supabase Docs](https://supabase.com/docs)
- [ZPL Documentation](https://www.zebra.com/us/en/support-downloads/knowledge-articles/zpl-programming-guide.html)

---

## 📝 Session Notes Template

Use this template to document your session:

```markdown
# Session 15 - [Your Title]

**Date**: [Date]
**Duration**: [Time]
**Status**: [Complete/In Progress]

## What Got Done
- [ ] Item 1
- [ ] Item 2

## Issues Encountered
1. [Issue description]
   - Solution: [How you fixed it]

## Testing Results
- [Pass/Fail] Test 1
- [Pass/Fail] Test 2

## Next Steps
- [ ] Task 1
- [ ] Task 2
```

---

**Ready to Test!** 🚀

Start by creating your first window order and working through the complete workflow. The system is fully functional and ready for testing!

**Estimated Time:** 1-2 hours to test and polish
**Goal:** Production-ready window manufacturing system
