# Session 11 Summary - Window Manufacturing Planning

**Date**: November 3, 2025
**Type**: Planning Session (No code written)
**Duration**: ~90 minutes of Q&A and planning
**Outcome**: Complete specification for Window Manufacturing System

---

## Session Objective

Plan and document a complete window ordering and Zebra label printing system to be integrated into the existing Island Glass Leads application.

---

## What Was Accomplished

### 1. Business Requirements Gathering

**User Access Hierarchy Defined:**
- Super Admin (Owners) → Full access to everything
- IG Manufacturing Admin → All window features + other sections
- IG Admin → Everything except window manufacturing
- IG Employee (General) → Window order entry only
- Sales (Future) → CRM only (contractors + PO tracker)

**Access Control Strategy:**
- Extend existing `user_profiles` table
- Add `department` column alongside existing `role` column
- Combo approach for flexible permission management
- Create dedicated permissions helper module

### 2. System Architecture Planning

**Three Main Components:**

1. **Order Entry** (All IG Employees)
   - Multi-window order form
   - PO number with autocomplete and fuzzy matching
   - Customer selection (links to po_clients or manual entry)
   - Dynamic window line items with fraction support
   - "Add Another Window" functionality
   - Order review before submission

2. **Order Management** (Manufacturing Admin Only)
   - Dashboard view of all orders
   - Expandable order details
   - Filtering by date, PO, status, shape
   - Bulk status updates
   - Link to print queue

3. **Label Printing** (Manufacturing Admin Only)
   - ZPL label generation for Zebra ZD421
   - Print queue (grouped by PO)
   - Label preview
   - Batch printing options
   - Print history tracking
   - Printer configuration

### 3. Technical Specifications

**Measurements:**
- Units: Inches always
- Format: Fraction support (1 1/2", 36 1/4", etc.)
- Order: Thickness < Width < Height (glazing standard)
- Use existing `modules/fraction_utils.py`

**Labels:**
- Printer: Zebra ZD421
- Size: 3x2 inches (configurable)
- Format: ZPL (Zebra Programming Language)
- Quantity: 1 label per physical window (4 windows = 4 separate labels)
- Content: PO number, dimensions, shape, label count, date, optional barcode

**Printing:**
- Network printing (IP-based)
- Mock/simulation mode for development
- .zpl file download capability
- Reprint functionality (stored ZPL code)

### 4. Database Schema Design

**Four New Tables:**

1. **window_orders**
   - PO number, customer info, status, notes
   - Optional FK to po_clients
   - Company scoping and audit trails

2. **window_order_items**
   - Window specifications (type, thickness, width, height)
   - Quantity per spec
   - Shape notes for custom windows
   - Linked to orders

3. **window_labels**
   - Generated ZPL code (stored for reprint)
   - Print status and history
   - Timestamp and user tracking
   - Linked to order items

4. **label_printer_config**
   - Printer settings (IP, port, label size)
   - Active/default flags
   - Company scoping

**All tables:**
- Use company_id for multi-tenant isolation
- Full audit trails (created_by, updated_by, deleted_by)
- Soft delete support (deleted_at)
- RLS policies enforcing company scoping

### 5. Integration Planning

**PO/Customer System:**
- Optional link to existing po_clients table
- Manual customer entry if not in system
- Fuzzy matching for "did you mean" suggestions
- Prevent duplicate PO numbers within company

**QuickBooks:**
- Placeholder structure for future integration
- Database fields ready for QB sync
- Mock data for development
- Flag for QB-synced vs manual customers

**Existing Systems:**
- Reuse fraction_utils.py for measurements
- Integrate with existing auth system
- Share company_id model
- Use established RLS patterns

### 6. Implementation Plan Created

**7 Phases:**
1. Fix PO Clients UI (15 min) - Critical blocker
2. User role system (30 min)
3. Database schema (45 min)
4. Backend modules (1-1.5 hrs)
5. UI pages (2-3 hrs)
6. Navigation & access control (30 min)
7. Polish & testing (1 hr)

**Total estimated time:** 6-8 hours

---

## Key Design Decisions

### Integration Strategy
**Decision:** Integrate into existing dash_app.py
**Reasoning:**
- Shared authentication system
- Single database (Supabase)
- Unified navigation
- Company scoping consistency
- Easier deployment and maintenance

### Data Model
**Decision:** Separate tables with optional FK link to po_clients
**Reasoning:**
- Different access control requirements
- Different workflow from PO tracking
- Sister company might not be in CRM
- Allows future QuickBooks sync
- Maintains clean separation of concerns

### Printer Approach
**Decision:** Mock printer mode with network printing capability
**Reasoning:**
- Can develop/test without physical printer
- Network printing ready when printer available
- .zpl file download as fallback
- Stored ZPL enables reprinting

### Role System
**Decision:** Combo of role + department columns
**Reasoning:**
- Flexible granular control
- Future-proof for more roles
- Easy to extend (sales, accounting, etc.)
- Simple permission checks

---

## Documents Created

1. **SESSION_11_WINDOW_MANUFACTURING_PLAN.md** (Primary)
   - Complete technical specification
   - Database schema details
   - Implementation phases
   - Testing checklist
   - Open questions for next session

2. **SESSION_11_QUICK_REFERENCE.md**
   - TL;DR summary
   - Quick start guide for Session 12
   - File reference
   - Critical info

3. **checkpoint.md** (Updated)
   - Added Session 11 summary
   - Updated status and next steps
   - Full planning context preserved

4. **plan.md** (Updated)
   - Added Phase 1.6: Window Manufacturing System
   - Updated status and priorities
   - Roadmap adjusted

---

## Files to Create (Session 12)

### SQL Migrations
1. `add_user_roles_and_departments.sql` - Role system
2. `window_manufacturing_schema.sql` - 4 tables + RLS
3. `window_manufacturing_seed_data.sql` - Test data

### Python Modules
4. `modules/permissions.py` - Access control helper
5. `modules/zpl_generator.py` - Zebra label generation
6. `modules/label_printer.py` - Print interface

### UI Pages
7. `pages/window_order_entry.py` - Order form
8. `pages/window_order_management.py` - Dashboard
9. `pages/window_label_printing.py` - Print queue

### Documentation
10. `WINDOW_MANUFACTURING_GUIDE.md` - Setup guide
11. `SESSION_12_SUMMARY.md` - Implementation summary

---

## Files to Modify (Session 12)

1. **pages/po_clients.py** - Fix broken Add Client form
2. **modules/database.py** - Add window order CRUD methods
3. **dash_app.py** - Routes, navigation, role filtering

---

## Critical Path for Next Session

### Must Do First
⚠️ **Fix PO Clients UI** (15 min)
- Currently broken since Session 10
- Required before proceeding
- See `NEXT_SESSION_PLAN.md` Phase 1

### Then Execute
✅ **Window Manufacturing System** (5-7 hours)
- Follow 7-phase implementation plan
- See `SESSION_11_WINDOW_MANUFACTURING_PLAN.md`

---

## Open Questions

To be clarified in Session 12 or future sessions:

1. **Window Shape Types**: Need complete list (or use defaults for now)
2. **Printer Details**: Actual Zebra ZD421 IP address (mock mode for now)
3. **Sister Company Name**: What to display in UI?
4. **Label Branding**: Logos or specific formatting?
5. **Barcode**: Need scannable PO barcode on labels?
6. **Approval Workflow**: Any approval before manufacturing?
7. **Notifications**: Alert manufacturing admins of new orders?

---

## Testing Requirements

### Phase 1 Testing
- [ ] PO Client forms functional
- [ ] Client + contact creation works
- [ ] Client cards display correctly

### Window System Testing
- [ ] User roles assigned and checked
- [ ] Navigation filters by role
- [ ] Multi-window orders save correctly
- [ ] Fractions parse and display
- [ ] Customer autocomplete works
- [ ] Fuzzy matching suggests alternatives
- [ ] ZPL labels generate with correct data
- [ ] Label count matches window count
- [ ] Print queue displays properly
- [ ] Mock printer saves .zpl files
- [ ] Print history tracks who/when
- [ ] RLS policies enforce isolation

---

## Session Statistics

**Planning Time**: ~90 minutes
**Questions Answered**: 4 multi-option + 6 clarification questions
**Documents Created**: 4 (2 new + 2 updated)
**Code Written**: 0 (planning only)
**Estimated Implementation Time**: 6-8 hours
**Next Session**: Session 12 - Implementation

---

## Success Criteria for Next Session

Session 12 will be considered successful when:

1. ✅ PO Clients UI is fixed and functional
2. ✅ User role system implemented and tested
3. ✅ 4 database tables created with RLS
4. ✅ 3 backend modules created and working
5. ✅ 3 UI pages built and accessible
6. ✅ Navigation filters by role correctly
7. ✅ Can submit multi-window order
8. ✅ Labels generate and download as .zpl
9. ✅ Print queue shows pending labels
10. ✅ All integration points working

---

## Context for Future Claude Sessions

**When resuming this project:**

1. Read `SESSION_11_QUICK_REFERENCE.md` first (fastest overview)
2. Then read `SESSION_11_WINDOW_MANUFACTURING_PLAN.md` (full spec)
3. Check `checkpoint.md` Session 11 section for context
4. Verify PO Clients UI status before starting window system

**Current blockers:**
- PO Clients UI broken since Session 10 (must fix first)

**Ready to build:**
- Full specification complete
- Database schema designed
- Implementation plan with time estimates
- All integration points identified
- Testing checklist prepared

---

**Session 11 Complete** ✅
**Next**: Session 12 - Implementation
**Status**: Ready to Build 🚀
