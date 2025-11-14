# Jobs/PO System - Quick Start

## What You Have Now

✅ Complete database schema for Jobs/PO management
✅ Jobs list page with search and filters
✅ Job detail page with overview and work items
✅ Auto-calculating costs and totals
✅ Modern UI using Dash Mantine Components

## Installation (2 Steps)

### 1. Run Database Migration

**Required before using the system!**

1. Go to https://supabase.com
2. Select your project
3. Click "SQL Editor"
4. Open: `database/migrations/008_jobs_po_system_revised.sql`
5. Copy ALL contents
6. Paste in SQL Editor
7. Click "Run"

### 2. Test It Works

1. Go to `/jobs` page
2. Click "Create New Job"
3. Fill in PO# and client
4. Save
5. Click the job card
6. Go to "Work Items" tab
7. Add a work item
8. Watch the header update with costs!

## What's Working

| Feature | Status | Location |
|---------|--------|----------|
| Jobs List | ✅ Complete | `/jobs` |
| Job Search & Filters | ✅ Complete | `/jobs` |
| Create Job | ✅ Complete | `/jobs` modal |
| Job Detail Header | ✅ Complete | `/job/<id>` |
| Overview Tab | ✅ Complete | Job detail page |
| Work Items Tab | ✅ Complete | Job detail page |
| Materials Tab | 🚧 Placeholder | Job detail page |
| Site Visits Tab | 🚧 Placeholder | Job detail page |
| Files Tab | 🚧 Placeholder | Job detail page |
| Comments Tab | 🚧 Placeholder | Job detail page |
| Schedule Tab | 🚧 Placeholder | Job detail page |

## What's Next

You have 3 options:

### Option 1: Complete Job Detail Tabs (Recommended)
Build out the remaining tabs:
- Materials tracking with vendors
- Site visits logging
- File uploads
- Comments system
- Calendar/schedule

**Say:** "complete materials tab" or "complete site visits tab"

### Option 2: Build Settings Pages
Create management interfaces for:
- Vendors master list
- Material templates

**Say:** "build settings pages"

### Option 3: Enhance Client Page
Show job history per client

**Say:** "enhance client page with jobs"

## Key Concepts

### PO = Job
Your PO number (e.g., "01-kellum.ryan-123acme") IS your job identifier. Same number internally and with vendors.

### Work Items
Track what you're doing:
- Showers, windows, mirrors, tabletops, frames
- Quantities and costs
- Flexible specifications

### Vendor Materials
Track what you're ordering:
- Which vendor
- Expected/actual delivery
- Custom descriptions
- Optional templates for common items

### Site Visits
Log every visit:
- Type (measure, install, finals, etc.)
- Who went
- Duration
- Photos and notes

## File Locations

```
Database:  database/migrations/008_jobs_po_system_revised.sql
DB Methods: modules/database.py (bottom section)
Jobs List: pages/jobs.py
Job Detail: pages/job_detail.py
Docs:      docs/REVISED_PO_SYSTEM_SUMMARY.md (full details)
```

## Troubleshooting

**Problem:** Jobs page shows "No company ID found"
**Solution:** Make sure you're logged in and have a company_id in user_profiles

**Problem:** Can't create job
**Solution:** Check that po_clients table has clients to select from

**Problem:** Costs not updating
**Solution:** Verify database triggers are active (should be after migration)

**Problem:** Work items tab is blank
**Solution:** Click "Add Work Item" to create your first one

## Need Help?

Full documentation: `docs/REVISED_PO_SYSTEM_SUMMARY.md`

Tell me what you want to build next!
