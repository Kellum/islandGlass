# Island Glass CRM - Complete System Plan
**Session 23 - Field Service CRM with QuickBooks Integration**
**Date**: November 4, 2024

---

## Executive Summary

Building a **field service CRM** to replace paper-based workflow with digital job management, mobile access for field teams, and QuickBooks integration for financial data.

**Core Purpose**: Track glass installation jobs from lead to completion, eliminate paper processes, provide mobile access for field teams.

---

## Current Workflow (Baseline)

```
1. Lead comes in (phone, email, website)
2. Schedule estimate on Google Calendar
3. Print calendar event → Team takes paper to site
4. Team measures on-site, draws on paper (shower/window/mirror/etc.)
5. Team returns paper to office
6. Office uploads paper to Google Drive
7. Owner creates QB Estimate (24-48 hrs)
8. Customer approves + pays deposit in QuickBooks
9. Schedule finals on Google Calendar (if needed)
10. Print paper → Team gets final measurements
11. Job sent to "orders email"
12. Someone orders glass from vendor (manual tracking)
13. Office calls customer when glass arrives
14. Schedule install on Google Calendar
15. Install happens
16. Owner sends QB Invoice
17. Customer pays final balance in QuickBooks
```

**Pain Points:**
- 📄 Lots of paper printing (calendar events, job details)
- 📁 Paper drawings uploaded to Drive (disconnected from job)
- 📅 Google Calendar not designed for job management
- ❓ Hard to see job status (where is each job in pipeline?)
- 📧 Manual email tracking for glass orders
- 📞 Manual customer communication

---

## New Workflow (With CRM)

```
1. Lead comes in → Create Job in CRM (web or mobile)
2. Schedule estimate → Assign to team in CRM
3. Team opens CRM on phone/tablet → Sees job details
4. Team measures on-site → Takes photos → Uploads to job in CRM
5. Photos automatically attached to job (no Google Drive step)
6. CRM notifies office: "Measurements complete"
7. Owner creates QB Estimate (same as now)
8. CRM pulls QB Estimate → Job status updates to "Quoted"
9. Customer approves in QB + pays deposit
10. CRM syncs → Job status: "Deposit Paid"
11. Schedule finals in CRM (if needed) → Assign team
12. Team completes finals → Upload photos
13. Office marks "Ready for fabrication" → Create vendor PO in CRM
14. Track glass order: vendor, order date, expected delivery
15. Glass arrives → CRM notifies office
16. Schedule install in CRM → Assign team
17. Team completes install → Mark complete in CRM
18. Owner sends QB Invoice
19. CRM syncs → Shows invoice balance due
20. Customer pays → CRM shows "Paid ✓"
```

**Benefits:**
- ✅ No more paper printing
- ✅ Photos attached directly to jobs
- ✅ Real-time job status for everyone
- ✅ Mobile access for field teams
- ✅ Track glass orders (vendor POs)
- ✅ See QB financial data in CRM

---

## System Architecture

### Core Entities

```
┌─────────────────┐
│     LEADS       │  Initial contact, not yet a job
└────────┬────────┘
         │ Convert to Job
         ↓
┌─────────────────┐
│   JOBS (POs)    │  Main entity - tracks job through pipeline
├─────────────────┤
│ - Job number    │
│ - Customer      │
│ - Job type      │
│ - Status        │  ← KEY: Pipeline stage
│ - QB links      │  ← Estimate #, Invoice #
│ - Dates         │
│ - Assigned to   │
└────────┬────────┘
         │
    ┌────┴────┬────────┬──────────┐
    ↓         ↓        ↓          ↓
┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
│PHOTOS  │ │NOTES │ │VENDOR  │ │SCHEDULE  │
│/ATTACH │ │/CMNT │ │POs     │ │/TASKS    │
└────────┘ └──────┘ └────────┘ └──────────┘
```

---

## Database Schema Design

### 1. Jobs Table (Enhanced POs)

**Rename**: `po_purchase_orders` → `jobs` (or keep as POs but treat as jobs)

```sql
-- Core Job Info
id SERIAL PRIMARY KEY
job_number TEXT UNIQUE NOT NULL          -- IG-2024-001
client_id INTEGER REFERENCES po_clients(id)

-- Job Details
job_type TEXT                            -- 'shower', 'window', 'mirror', 'tabletop', 'other'
job_description TEXT                     -- "Frameless shower installation"
project_name TEXT                        -- "Smith Bathroom Remodel"

-- Status & Pipeline (KEY FEATURE)
status TEXT DEFAULT 'lead'               -- see status list below
priority TEXT DEFAULT 'normal'           -- 'low', 'normal', 'high', 'urgent'

-- Scheduling
estimate_scheduled_date TIMESTAMP        -- when estimate appointment is
estimate_completed_date TIMESTAMP        -- when team finished measuring
finals_scheduled_date TIMESTAMP          -- if finals needed
finals_completed_date TIMESTAMP          -- when finals done
install_scheduled_date TIMESTAMP         -- install appointment
install_completed_date TIMESTAMP         -- job completion

-- Assignment
assigned_to UUID REFERENCES auth.users(id)  -- primary person responsible
assigned_team TEXT[]                     -- array of user IDs for team

-- QuickBooks Integration
qb_customer_id TEXT                      -- QB Customer ID
qb_estimate_id TEXT                      -- QB Estimate ID
qb_estimate_number TEXT                  -- EST-1234 (for display)
qb_estimate_total DECIMAL(10,2)          -- pulled from QB
qb_estimate_status TEXT                  -- 'pending', 'accepted', 'rejected', 'expired'
qb_invoice_id TEXT                       -- QB Invoice ID
qb_invoice_number TEXT                   -- INV-5678 (for display)
qb_invoice_total DECIMAL(10,2)           -- pulled from QB
qb_invoice_balance DECIMAL(10,2)         -- amount still owed
qb_payment_status TEXT                   -- 'unpaid', 'partial', 'paid'
qb_last_synced TIMESTAMP                 -- when we last pulled from QB

-- Financial (computed from QB)
deposit_amount DECIMAL(10,2)             -- pulled from QB payments
deposit_paid_date DATE                   -- first payment date
balance_due DECIMAL(10,2)                -- qb_invoice_balance

-- Site/Location Info
site_address TEXT                        -- job location (may differ from client billing address)
site_city TEXT
site_state TEXT
site_zip TEXT
site_contact_name TEXT                   -- on-site contact
site_contact_phone TEXT

-- Fabrication/Materials
glass_ordered_date DATE                  -- when glass was ordered
glass_expected_date DATE                 -- when glass should arrive
glass_received_date DATE                 -- when glass arrived
vendor_name TEXT                         -- which vendor (dropdown)
vendor_po_number TEXT                    -- vendor's PO/order reference

-- Flags
requires_finals BOOLEAN DEFAULT FALSE    -- does this job need final measurements?
is_rush BOOLEAN DEFAULT FALSE           -- rush job?
is_warranty BOOLEAN DEFAULT FALSE       -- warranty/repair job?

-- Notes
internal_notes TEXT                      -- not visible to customer
customer_notes TEXT                      -- visible to customer (if you build portal)
special_instructions TEXT                -- install instructions, access codes, etc.

-- Metadata
source TEXT DEFAULT 'manual'             -- 'phone', 'email', 'website', 'referral', 'manual'
tags TEXT[]                             -- ['commercial', 'repeat_customer', etc.]

-- Audit
company_id UUID NOT NULL REFERENCES companies(id)
created_by UUID REFERENCES auth.users(id)
created_at TIMESTAMP DEFAULT NOW()
updated_by UUID REFERENCES auth.users(id)
updated_at TIMESTAMP DEFAULT NOW()
deleted_at TIMESTAMP                     -- soft delete
```

**Job Status Pipeline** (critical for tracking):
```sql
-- Status progression:
'lead'                  -- Initial contact, not scheduled yet
'estimate_scheduled'    -- Appointment scheduled
'measuring'             -- Team on-site measuring now
'awaiting_estimate'     -- Measurements complete, waiting for owner to create QB estimate
'quoted'                -- QB Estimate sent to customer
'estimate_approved'     -- Customer approved, waiting for deposit
'deposit_paid'          -- Deposit received (pulled from QB)
'finals_scheduled'      -- Final measurements scheduled (if needed)
'finals_complete'       -- Final measurements done
'ready_to_order'        -- Ready to order glass
'glass_ordered'         -- Glass on order
'glass_in'              -- Glass received, ready to install
'install_scheduled'     -- Install appointment scheduled
'installing'            -- Install in progress
'install_complete'      -- Install done, waiting for final invoice
'invoiced'              -- Final invoice sent (pulled from QB)
'paid'                  -- Fully paid (pulled from QB)
'complete'              -- Job complete and closed
'on_hold'               -- Paused for some reason
'cancelled'             -- Job cancelled
```

---

### 2. Job Attachments (Photos/Files)

```sql
CREATE TABLE job_attachments (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,

    -- File Details
    file_name TEXT NOT NULL,
    file_size INTEGER,                   -- bytes
    file_type TEXT,                      -- 'image/jpeg', 'application/pdf', etc.
    file_extension TEXT,                 -- .jpg, .png, .pdf

    -- Storage (Supabase Storage)
    storage_path TEXT NOT NULL,          -- path in Supabase bucket
    storage_bucket TEXT DEFAULT 'job-attachments',

    -- Metadata
    attachment_type TEXT,                -- 'measurement_photo', 'drawing', 'contract', 'other'
    description TEXT,
    taken_at TIMESTAMP,                  -- when photo was taken (EXIF data)
    taken_by UUID REFERENCES auth.users(id),  -- which team member uploaded

    -- Location (from EXIF if available)
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Job Phase
    phase TEXT,                          -- 'estimate', 'finals', 'install', 'complete'

    -- Visibility
    is_client_visible BOOLEAN DEFAULT FALSE,  -- show in customer portal?

    -- Audit
    company_id UUID NOT NULL REFERENCES companies(id),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_job_attachments_job_id ON job_attachments(job_id);
CREATE INDEX idx_job_attachments_type ON job_attachments(attachment_type);
```

---

### 3. Job Comments/Activity Feed

```sql
CREATE TABLE job_comments (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,

    -- Comment Details
    comment_type TEXT DEFAULT 'comment',  -- 'comment', 'status_change', 'system', 'internal'
    comment_text TEXT NOT NULL,

    -- System Events (auto-logged)
    event_type TEXT,                     -- 'created', 'status_changed', 'assigned', 'photo_uploaded', etc.
    event_data JSONB,                    -- flexible storage

    -- Status Changes (track what changed)
    old_status TEXT,
    new_status TEXT,

    -- Visibility
    is_internal BOOLEAN DEFAULT FALSE,   -- internal notes vs. customer-visible

    -- Mentions
    mentioned_user_ids UUID[],           -- @mention users for notifications

    -- Audit
    company_id UUID NOT NULL REFERENCES companies(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_job_comments_job_id ON job_comments(job_id);
CREATE INDEX idx_job_comments_created_at ON job_comments(created_at DESC);
```

---

### 4. Vendor Purchase Orders (Glass Orders)

```sql
CREATE TABLE vendor_purchase_orders (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,

    -- Vendor Info
    vendor_name TEXT NOT NULL,           -- 'ABC Glass Supply', etc.
    vendor_contact_name TEXT,
    vendor_contact_phone TEXT,
    vendor_contact_email TEXT,

    -- Order Details
    vendor_po_number TEXT,               -- vendor's order/reference number
    our_po_number TEXT,                  -- our internal PO# for this order
    order_date DATE DEFAULT CURRENT_DATE,
    expected_delivery_date DATE,
    actual_delivery_date DATE,

    -- Items (could be line items, but simple text for now)
    items_description TEXT,              -- "3/8\" tempered glass, 48x72, hinges, clips"

    -- Costs
    subtotal DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    total_cost DECIMAL(10,2),

    -- Status
    status TEXT DEFAULT 'ordered',       -- 'ordered', 'in_production', 'shipped', 'delivered', 'cancelled'

    -- Tracking
    tracking_number TEXT,
    carrier TEXT,                        -- 'UPS', 'FedEx', 'Will Call', etc.

    -- Notes
    notes TEXT,
    internal_notes TEXT,

    -- Audit
    company_id UUID NOT NULL REFERENCES companies(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_vendor_pos_job_id ON vendor_purchase_orders(job_id);
CREATE INDEX idx_vendor_pos_status ON vendor_purchase_orders(status);
```

---

### 5. QuickBooks Sync Log

```sql
CREATE TABLE qb_sync_log (
    id SERIAL PRIMARY KEY,

    -- What was synced
    sync_type TEXT NOT NULL,             -- 'customer', 'estimate', 'invoice', 'payment', 'product'
    entity_type TEXT,                    -- 'Customer', 'Estimate', 'Invoice'
    qb_entity_id TEXT,                   -- QB's ID
    crm_entity_id INTEGER,               -- our ID (job, client, etc.)

    -- Direction
    direction TEXT NOT NULL,             -- 'pull' (from QB) or 'push' (to QB)

    -- Result
    status TEXT NOT NULL,                -- 'success', 'error', 'skipped'
    error_message TEXT,

    -- Data
    request_data JSONB,                  -- what we sent/requested
    response_data JSONB,                 -- what we received

    -- Timing
    synced_at TIMESTAMP DEFAULT NOW(),
    duration_ms INTEGER,                 -- how long sync took

    -- Context
    company_id UUID NOT NULL REFERENCES companies(id),
    triggered_by UUID REFERENCES auth.users(id)  -- who triggered sync (or NULL for automatic)
);

CREATE INDEX idx_qb_sync_log_entity ON qb_sync_log(entity_type, qb_entity_id);
CREATE INDEX idx_qb_sync_log_synced_at ON qb_sync_log(synced_at DESC);
CREATE INDEX idx_qb_sync_log_status ON qb_sync_log(status);
```

---

### 6. QuickBooks Tokens (Secure Storage)

```sql
CREATE TABLE qb_tokens (
    id SERIAL PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) UNIQUE,

    -- OAuth Tokens
    access_token TEXT NOT NULL,          -- encrypted
    refresh_token TEXT NOT NULL,         -- encrypted
    realm_id TEXT NOT NULL,              -- QB Company ID

    -- Token Metadata
    token_type TEXT DEFAULT 'Bearer',
    expires_at TIMESTAMP NOT NULL,
    refresh_token_expires_at TIMESTAMP NOT NULL,

    -- Connection Status
    is_active BOOLEAN DEFAULT TRUE,
    last_refreshed_at TIMESTAMP DEFAULT NOW(),
    last_error TEXT,

    -- Audit
    connected_at TIMESTAMP DEFAULT NOW(),
    connected_by UUID REFERENCES auth.users(id),
    disconnected_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_qb_tokens_company_id ON qb_tokens(company_id);
```

---

### 7. Product/Service Catalog (Pulled from QB)

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,

    -- QuickBooks Reference
    qb_item_id TEXT UNIQUE,              -- QB Item ID
    qb_item_name TEXT NOT NULL,          -- QB Item Name
    qb_item_type TEXT,                   -- 'Service', 'Inventory', 'NonInventory'

    -- Product Details
    product_name TEXT NOT NULL,          -- display name (may differ from QB)
    product_category TEXT,               -- 'shower', 'window', 'mirror', 'hardware', 'labor'
    description TEXT,

    -- Pricing (from QB)
    unit_price DECIMAL(10,2),
    unit_of_measure TEXT DEFAULT 'ea',  -- 'ea', 'sq ft', 'lin ft', 'hour'

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_taxable BOOLEAN DEFAULT FALSE,

    -- Sync
    qb_last_synced TIMESTAMP,

    -- Audit
    company_id UUID NOT NULL REFERENCES companies(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_products_qb_item_id ON products(qb_item_id);
CREATE INDEX idx_products_category ON products(product_category);
CREATE INDEX idx_products_active ON products(is_active);
```

---

## QuickBooks Integration Details

### Authentication Flow

1. **Admin clicks "Connect to QuickBooks"**
2. Redirect to Intuit OAuth
3. User authorizes app
4. Receive tokens, store encrypted in `qb_tokens` table
5. Auto-refresh tokens before expiration

### Sync Strategy - PULL from QuickBooks (Primary)

**What We Pull:**
1. **Customers** (hourly or on-demand)
2. **Estimates** (every 15 min or on-demand)
3. **Invoices** (every 15 min or on-demand)
4. **Payments** (every 15 min to update payment status)
5. **Products/Services** (daily or on-demand)

**Pull Flow Example - Estimates:**
```python
# Every 15 minutes or when user clicks "Sync"
def sync_estimates_from_qb():
    """Pull new/updated estimates from QuickBooks"""

    # Get last sync time
    last_sync = get_last_qb_sync('estimate')

    # Query QB for estimates modified since last sync
    estimates = qb_client.query(
        "SELECT * FROM Estimate WHERE MetaData.LastUpdatedTime > '{last_sync}'"
    )

    for qb_estimate in estimates:
        # Find matching job by QB customer ID
        job = db.find_job_by_qb_customer_id(qb_estimate.CustomerRef.value)

        if job:
            # Update job with estimate data
            db.update_job({
                'id': job.id,
                'qb_estimate_id': qb_estimate.Id,
                'qb_estimate_number': qb_estimate.DocNumber,
                'qb_estimate_total': qb_estimate.TotalAmt,
                'qb_estimate_status': get_estimate_status(qb_estimate),
                'qb_last_synced': datetime.now(),
                'status': 'quoted'  # update job status
            })

            # Log activity
            db.log_job_comment({
                'job_id': job.id,
                'comment_type': 'system',
                'event_type': 'qb_estimate_synced',
                'comment_text': f'QuickBooks estimate {qb_estimate.DocNumber} synced. Total: ${qb_estimate.TotalAmt}'
            })
```

**Pull Flow Example - Payments:**
```python
def sync_payments_from_qb():
    """Pull payment status for invoiced jobs"""

    # Get all jobs with QB invoices
    jobs_with_invoices = db.get_jobs_with_qb_invoices()

    for job in jobs_with_invoices:
        # Fetch invoice from QB
        qb_invoice = qb_client.get('Invoice', job.qb_invoice_id)

        # Calculate payment status
        balance = qb_invoice.Balance
        total = qb_invoice.TotalAmt
        paid = total - balance

        payment_status = 'unpaid'
        if balance == 0:
            payment_status = 'paid'
        elif paid > 0:
            payment_status = 'partial'

        # Update job
        db.update_job({
            'id': job.id,
            'qb_invoice_balance': balance,
            'qb_payment_status': payment_status,
            'balance_due': balance,
            'qb_last_synced': datetime.now()
        })

        # Update status if fully paid
        if payment_status == 'paid' and job.status != 'paid':
            db.update_job_status(job.id, 'paid')
            db.log_job_comment({
                'job_id': job.id,
                'comment_type': 'system',
                'event_type': 'payment_received',
                'comment_text': f'Invoice fully paid. Balance: $0.00'
            })
```

### Push to QuickBooks (Optional - Phase 2)

**What We Could Push (Future):**
- New customers created in CRM → Create QB Customer
- Job data → Create QB Job (Sub-customer)
- *(Owner still creates estimates/invoices manually in QB)*

---

## UI/UX Design

### Mobile-First Job View (For Field Teams)

**Job Detail Page - Mobile:**
```
┌─────────────────────────────────────────┐
│  ← Back          JOB IG-2024-123    •••│
├─────────────────────────────────────────┤
│                                          │
│  🟢 Estimate Scheduled                  │
│                                          │
│  📍 Smith Residence                     │
│  1234 Ocean Blvd, Jacksonville FL       │
│                                          │
│  📅 Today at 10:00 AM                   │
│  👤 Assigned: John & Mike               │
│                                          │
├─────────────────────────────────────────┤
│ CUSTOMER                                 │
│ Jane Smith                              │
│ 📞 (904) 555-1234                       │
│ ✉️  jane@email.com                      │
├─────────────────────────────────────────┤
│ JOB DETAILS                             │
│ Frameless shower installation           │
│ 48" x 72" neo-angle shower              │
│                                          │
│ Special Instructions:                   │
│ Call before arriving, use side door     │
├─────────────────────────────────────────┤
│ PHOTOS (2)                              │
│ ┌────┐ ┌────┐                           │
│ │📷 │ │📷 │ [+ Add Photo]              │
│ └────┘ └────┘                           │
├─────────────────────────────────────────┤
│ ACTIONS                                  │
│ ┌─────────────────────────────────────┐│
│ │  ✓  Mark Measurements Complete      ││
│ └─────────────────────────────────────┘│
│ ┌─────────────────────────────────────┐│
│ │  📷  Take Photo                     ││
│ └─────────────────────────────────────┘│
│ ┌─────────────────────────────────────┐│
│ │  💬  Add Note                       ││
│ └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### Desktop Job Pipeline View

**Jobs Dashboard - Kanban Board:**
```
┌───────────┬───────────┬───────────┬───────────┬───────────┐
│   LEAD    │  QUOTED   │DEPOSIT PD │GLASS ORD  │SCHEDULED  │
│    (5)    │   (12)    │   (8)     │   (6)     │   (4)     │
├───────────┼───────────┼───────────┼───────────┼───────────┤
│           │           │           │           │           │
│ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │
│ │IG-123 │ │ │IG-119 │ │ │IG-115 │ │ │IG-110 │ │ │IG-105 │ │
│ │Smith  │ │ │Johnson│ │ │Brown  │ │ │Wilson │ │ │Davis  │ │
│ │Shower │ │ │Window │ │ │Mirror │ │ │Shower │ │ │Window │ │
│ │$2,450 │ │ │$1,200 │ │ │$350   │ │ │$3,100 │ │ │$950   │ │
│ │📅 Today│ │ │📅 3d  │ │ │✓ Paid │ │ │🚚 Arr.│ │ │📅 Mon │ │
│ └───────┘ │ └───────┘ │ └───────┘ │ └───────┘ │ └───────┘ │
│           │           │           │           │           │
│ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │
│ │...    │ │ │...    │ │ │...    │ │ │...    │ │ │...    │ │
│ └───────┘ │ └───────┘ │ └───────┘ │ └───────┘ │ └───────┘ │
└───────────┴───────────┴───────────┴───────────┴───────────┘

Drag cards to move between statuses
```

### Job Details Page - Desktop (Full View)

**Tabs:**
1. **Overview** - Summary, customer info, QB data, status timeline
2. **Photos** - Grid view of all photos, organized by phase
3. **Activity** - Comments, status changes, system events
4. **Glass Order** - Vendor PO details, tracking
5. **Documents** - Contracts, permits, other files
6. **QuickBooks** - Estimate/invoice details, payment history

**Overview Tab:**
```
┌─────────────────────────────────────────────────────────────┐
│ JOB IG-2024-123        Status: Deposit Paid    Priority: 🔴│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐│
│ │ CUSTOMER         │  │ JOB DETAILS      │  │ QUICKBOOKS ││
│ │                  │  │                  │  │            ││
│ │ Jane Smith       │  │ Type: Shower     │  │ Estimate:  ││
│ │ (904) 555-1234   │  │                  │  │ EST-1234   ││
│ │ jane@email.com   │  │ Frameless neo-   │  │ $2,450.00  ││
│ │                  │  │ angle shower     │  │            ││
│ │ 📍 1234 Ocean Bd │  │                  │  │ Deposit:   ││
│ │ Jacksonville FL  │  │ Requires finals: │  │ $1,225.00 ✓││
│ │                  │  │ ☐ No             │  │            ││
│ │ [View in QB]     │  │                  │  │ Balance:   ││
│ └──────────────────┘  │ Rush: ☐ No       │  │ $1,225.00  ││
│                       │                  │  │            ││
│ ┌──────────────────┐  │ Assigned:        │  │ Status:    ││
│ │ TIMELINE         │  │ 👤 John Smith    │  │ PENDING ⏳ ││
│ │                  │  │                  │  │            ││
│ │ ✓ Lead created   │  │ Team:            │  │ [Sync Now] ││
│ │   Nov 1, 9:00 AM │  │ John & Mike      │  └────────────┘│
│ │                  │  └──────────────────┘                ││
│ │ ✓ Estimate sched │                                      ││
│ │   Nov 1, 9:15 AM │  ┌──────────────────────────────────┐││
│ │                  │  │ SPECIAL INSTRUCTIONS             │││
│ │ ✓ Measured       │  │                                  │││
│ │   Nov 2, 10:30AM │  │ • Call before arriving           │││
│ │                  │  │ • Use side door                  │││
│ │ ✓ Quoted         │  │ • Dog in backyard, ask to secure│││
│ │   Nov 2, 3:00 PM │  └──────────────────────────────────┘││
│ │                  │                                      ││
│ │ ✓ Deposit paid   │  ┌──────────────────────────────────┐││
│ │   Nov 3, 11:00AM │  │ NOTES (3)                        │││
│ │                  │  │                                  │││
│ │ ⏳ Glass ordered │  │ Mike: Customer wants chrome     │││
│ │   Pending        │  │ hinges, not brushed nickel      │││
│ │                  │  │ 2 hours ago                      │││
│ └──────────────────┘  └──────────────────────────────────┘││
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan - Session 23+

### Phase 1: Foundation & QuickBooks Setup (Sessions 23-24)

**Goals:** Database migrations, QB authentication, basic sync

1. **Database Migration** (Session 23)
   - Create/modify tables: jobs, job_attachments, job_comments, vendor_purchase_orders
   - Add QB fields to jobs table
   - Create qb_tokens, qb_sync_log, products tables
   - Add indexes

2. **QuickBooks Integration Setup** (Session 23-24)
   - Install `python-quickbooks` library
   - Create QB OAuth flow (connect/disconnect)
   - Build token storage/refresh system
   - Test QB connection

3. **Basic QB Sync - Customers** (Session 24)
   - Pull customers from QB → Create/update in CRM
   - Manual sync button
   - Display sync status

4. **Basic QB Sync - Estimates** (Session 24)
   - Pull estimates from QB
   - Match to jobs by customer
   - Display estimate # and total on job

### Phase 2: Core Job Management (Sessions 24-25)

**Goals:** Job pipeline, mobile view, status tracking

5. **Job Status System** (Session 24)
   - Implement status field with dropdown
   - Create status change workflow
   - Auto-log status changes to activity feed

6. **Job Details Page - Desktop** (Session 25)
   - Overview tab with customer, job details, QB data
   - Timeline view showing status progression
   - Edit job details
   - Status change buttons

7. **Job Pipeline View** (Session 25)
   - Kanban board by status
   - Drag-and-drop to change status
   - Job cards with key info
   - Filters: assigned to, date range, job type

8. **Mobile-Optimized Job View** (Session 25)
   - Responsive design for phones/tablets
   - Large touch targets
   - Simplified view (only essential info)

### Phase 3: Photo Uploads & Attachments (Sessions 25-26)

**Goals:** Replace paper drawings with photos

9. **File Upload System** (Session 25)
   - Supabase Storage setup (job-attachments bucket)
   - Upload component (drag-drop or camera)
   - Mobile camera integration

10. **Photo Gallery** (Session 26)
    - Grid view of photos per job
    - Lightbox for viewing
    - Organize by phase (estimate, finals, install)
    - Delete photos
    - Download photos

11. **Photo Upload from Mobile** (Session 26)
    - Camera button on mobile job view
    - Upload directly from phone camera
    - Capture GPS/location data
    - Thumbnail generation

### Phase 4: Comments & Activity Feed (Session 26)

**Goals:** Team communication, system logging

12. **Activity Feed** (Session 26)
    - Display all comments and system events
    - Filter by type (comments only, system events only)
    - Expandable timeline view

13. **Add Comments** (Session 26)
    - Comment input box
    - Internal vs. customer notes toggle
    - Auto-log when photos uploaded, status changed, etc.

14. **Notifications** (Session 26, optional)
    - Email notifications for @mentions
    - Team notifications for status changes
    - Customer notifications (optional)

### Phase 5: Vendor Purchase Orders (Session 27)

**Goals:** Track glass orders

15. **Create Vendor PO** (Session 27)
    - Form to create vendor PO from job
    - Vendor selection (dropdown of common vendors)
    - Items description, costs, expected delivery

16. **Vendor PO List View** (Session 27)
    - See all vendor POs by status
    - Filter by vendor, date range
    - Link to parent job

17. **Vendor PO on Job Details** (Session 27)
    - Show vendor PO status on job page
    - Track delivery status
    - Mark as delivered

### Phase 6: Enhanced QB Sync (Session 28)

**Goals:** Pull invoices, payments, products

18. **Invoice Sync** (Session 28)
    - Pull invoices from QB
    - Match to jobs
    - Display invoice #, balance due, payment status

19. **Payment Sync** (Session 28)
    - Pull payment status from QB invoices
    - Update job status when fully paid
    - Display payment history

20. **Products Sync** (Session 28)
    - Pull QB Products/Services
    - Create products table in CRM
    - Admin page to view/map products

21. **Automatic Sync** (Session 28)
    - Background job (runs every 15 min)
    - Sync estimates, invoices, payments
    - Only sync what changed (Change Data Capture)

### Phase 7: Scheduling & Dispatch (Session 29)

**Goals:** Replace Google Calendar

22. **Calendar View** (Session 29)
    - Weekly/monthly calendar
    - Show jobs with scheduled dates
    - Color code by job type or status
    - Click to view job details

23. **Schedule Job** (Session 29)
    - Date/time picker
    - Assign team members
    - Add to calendar
    - Send notifications

24. **Team Assignment** (Session 29)
    - Assign primary person + team
    - Team member view (see my jobs)
    - Filter by assigned person

### Phase 8: Reporting & Analytics (Session 30)

**Goals:** Business insights

25. **Job Analytics Dashboard** (Session 30)
    - Jobs by status (pie chart)
    - Revenue by month (bar chart)
    - Average job value
    - Jobs by type

26. **Financial Reports** (Session 30)
    - Outstanding balances (pulled from QB)
    - Deposit collected vs. total
    - Revenue forecast (quoted jobs)

27. **Performance Metrics** (Session 30)
    - Time from lead to quote
    - Quote acceptance rate
    - Time from approval to install
    - Customer satisfaction (future: survey system)

---

## Custom Fields Decision

Based on your workflow, I recommend **JSONB approach** for custom fields:

**Why:**
- Simpler to implement
- You said "for future use" - suggests experimental
- Flexibility to add fields as you discover needs
- No admin UI needed immediately

**Default fields are enough for now:**
- Job type, status, dates, assignments, QB links, vendor info

**Custom fields stored as JSONB**:
- Easy to add: `{ "lead_source": "Referral", "commission_percent": 5 }`
- Query later if needed
- Can build admin UI in Phase 9 if you want structured fields

---

## Technology Stack

**Backend:**
- Python 3
- Supabase (PostgreSQL)
- `python-quickbooks` library
- `intuit-oauth` for QB authentication

**Frontend:**
- Dash + Dash Mantine Components
- Mobile-responsive design
- Camera/file upload components

**File Storage:**
- Supabase Storage (for photos/attachments)

**Background Jobs:**
- Python scheduler (APScheduler or similar)
- Or Supabase Edge Functions for cron jobs

---

## Security & Permissions

**Role-Based Access:**
- **Owner**: Full access, can see financial data, connect QB
- **Admin**: Manage jobs, assign teams, cannot disconnect QB
- **Team Member**: View assigned jobs, upload photos, add notes, cannot see other teams' jobs
- **Office**: Create jobs, schedule, track status, limited financial access

**QuickBooks Token Security:**
- Tokens encrypted at rest
- Stored in Supabase (RLS protected)
- Auto-refresh before expiration
- Audit log for all QB API calls

---

## Success Metrics

**After Phase 1-3 (Core System):**
- ✅ No more printing Google Calendar
- ✅ 100% of jobs tracked in CRM with status
- ✅ Photos uploaded from mobile (no more Google Drive step)
- ✅ QB estimates/invoices visible in CRM

**After Phase 4-6 (Full Features):**
- ✅ Glass orders tracked (vendor, delivery dates)
- ✅ Team knows what to do each day (assigned jobs)
- ✅ Office sees pipeline at a glance
- ✅ Customer balance due visible in real-time

**Long-term:**
- ✅ Quote-to-cash cycle time reduced 30%
- ✅ Customer communication improved (less "when's my install?" calls)
- ✅ Job profitability tracked (cost vs. invoice)

---

## Next Steps - START HERE

### Immediate (Session 23 - Today):

1. **Review this plan** - Does it match your vision?
2. **Answer remaining questions:**
   - Approved?
   - Any changes?
   - What should we build first?

3. **If approved, I'll start:**
   - Create database migration script (all tables)
   - Set up QuickBooks OAuth flow
   - Install python-quickbooks library
   - Create basic QB sync for customers

### This Week (Sessions 23-25):
- Complete QB integration foundation
- Build job details page
- Create mobile job view
- Photo upload system
- Job status pipeline

---

## Questions to Finalize

1. **Job numbering format:** Do you want auto-generated job numbers like "IG-2024-001" or manual entry?

2. **Customer data:** Should we pull ALL customers from QB or only when referenced in an estimate?

3. **Photo organization:** Organize by phase (estimate/finals/install) or just chronological?

4. **Vendor list:** Do you have 3-5 main vendors for glass? Should we create a vendors table or just text field?

5. **Team members:** How many people will use this? (for user accounts setup)

6. **Mobile devices:** What devices will teams use? iPads? iPhones? Android?

7. **Start with:** Which feature is most urgent? Photo uploads? QB sync? Pipeline view?

---

**Ready to build?** Let me know if this plan looks good and I'll start implementing! 🚀
