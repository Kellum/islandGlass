# Purchase Order System Enhancement Plan
**Session 23 - Comprehensive PO Management**
**Date**: November 4, 2024

## Current System Overview

### Existing Tables
```sql
-- po_clients (already exists)
- id, company_name, contact_name, phone, email, address, city, state, zip
- client_type (contractor/residential/commercial)
- notes, company_id, created_by, created_at, updated_by, updated_at, deleted_at

-- po_purchase_orders (already exists)
- id, po_number, client_id, status, total_amount, due_date, notes
- company_id, created_by, created_at, updated_by, updated_at, deleted_at

-- po_activities (already exists)
- id, client_id, activity_type, description, activity_date
- company_id, created_by, created_at
```

### Existing Features (Working)
✅ Create, Read, Update, Delete POs
✅ Link POs to clients
✅ Basic filtering (client, status, search)
✅ Status tracking (active/completed/cancelled/on_hold)
✅ Soft deletes with audit trail

---

## Proposed Enhancements

### 1. PO Line Items (Products/Services)
**Purpose**: Track individual items within each purchase order

#### Database Schema
```sql
CREATE TABLE po_line_items (
    id SERIAL PRIMARY KEY,
    po_id INTEGER REFERENCES po_purchase_orders(id) ON DELETE CASCADE,

    -- Product/Service Details
    item_type TEXT, -- 'product' | 'service' | 'other'
    product_name TEXT NOT NULL,
    description TEXT,

    -- Quantity & Pricing
    quantity DECIMAL(10, 2) NOT NULL DEFAULT 1,
    unit_of_measure TEXT DEFAULT 'ea', -- ea, sq ft, lin ft, hour, etc.
    unit_price DECIMAL(10, 2) NOT NULL,

    -- Calculations (can be computed but stored for history)
    subtotal DECIMAL(10, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    tax_percent DECIMAL(5, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    line_total DECIMAL(10, 2), -- subtotal - discount + tax

    -- Optional: Link to inventory/products if you build that
    product_id INTEGER, -- future: REFERENCES products(id)

    -- Ordering
    line_order INTEGER DEFAULT 0,

    -- Audit
    company_id UUID NOT NULL REFERENCES companies(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_po_line_items_po_id ON po_line_items(po_id);
CREATE INDEX idx_po_line_items_company_id ON po_line_items(company_id);
```

**Questions for You:**
- Do you want to track tax per line item or just at PO level?
- Do you need discount at line item level or just PO level?
- What units of measure do you commonly use? (ea, sq ft, lin ft, hours, etc.)
- Do you want to link to a products/inventory table in the future?

---

### 2. PO Comments/Activity Feed
**Purpose**: Team collaboration, notes, status updates

#### Database Schema
```sql
CREATE TABLE po_comments (
    id SERIAL PRIMARY KEY,
    po_id INTEGER REFERENCES po_purchase_orders(id) ON DELETE CASCADE,

    -- Comment Details
    comment_type TEXT DEFAULT 'comment', -- 'comment' | 'status_change' | 'system' | 'internal'
    comment_text TEXT NOT NULL,

    -- For system-generated comments (auto-logged events)
    event_type TEXT, -- 'created' | 'updated' | 'status_changed' | 'sent' | 'paid' | etc.
    event_data JSONB, -- flexible storage for event details

    -- Visibility
    is_internal BOOLEAN DEFAULT FALSE, -- visible only to team, not client

    -- Mentions/Notifications (future)
    mentioned_user_ids INTEGER[], -- array of user IDs @mentioned

    -- Audit
    company_id UUID NOT NULL REFERENCES companies(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP -- soft delete for comments
);

CREATE INDEX idx_po_comments_po_id ON po_comments(po_id);
CREATE INDEX idx_po_comments_created_at ON po_comments(created_at DESC);
CREATE INDEX idx_po_comments_company_id ON po_comments(company_id);
```

**Features:**
- User comments with timestamps
- System-generated activity log (PO created, status changed, email sent, etc.)
- Internal notes (not visible to client)
- Edit/delete comments
- @mentions (future)

**Questions for You:**
- Do you want to be able to edit/delete comments?
- Should comments support rich text or just plain text?
- Do you want file attachments on comments or separate?

---

### 3. File Attachments
**Purpose**: Attach documents, photos, PDFs to POs

#### Database Schema
```sql
CREATE TABLE po_attachments (
    id SERIAL PRIMARY KEY,
    po_id INTEGER REFERENCES po_purchase_orders(id) ON DELETE CASCADE,

    -- File Details
    file_name TEXT NOT NULL,
    file_size INTEGER, -- bytes
    file_type TEXT, -- mime type: 'application/pdf', 'image/jpeg', etc.
    file_extension TEXT, -- .pdf, .jpg, .docx, etc.

    -- Storage
    storage_path TEXT NOT NULL, -- Supabase Storage path
    storage_bucket TEXT DEFAULT 'po-attachments',

    -- Metadata
    description TEXT,
    attachment_type TEXT, -- 'quote', 'invoice', 'contract', 'photo', 'drawing', 'other'

    -- Visibility
    is_client_visible BOOLEAN DEFAULT TRUE,

    -- Audit
    company_id UUID NOT NULL REFERENCES companies(id),
    uploaded_by UUID REFERENCES auth.users(id),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_po_attachments_po_id ON po_attachments(po_id);
CREATE INDEX idx_po_attachments_company_id ON po_attachments(company_id);
```

**Questions for You:**
- What file types do you need to support? (PDF, images, Excel, Word, etc.)
- Max file size limit? (e.g., 10MB per file)
- Do you want to organize attachments by type (quotes, invoices, photos, etc.)?
- Should some attachments be internal-only (not visible to client)?

---

### 4. Custom Fields System
**Purpose**: Flexible data storage for company-specific needs

#### Approach 1: JSONB Column (Flexible, Simple)
```sql
-- Add to po_purchase_orders table
ALTER TABLE po_purchase_orders
ADD COLUMN custom_fields JSONB DEFAULT '{}'::jsonb;

-- Example data:
{
  "sales_rep": "John Smith",
  "project_type": "Residential Remodel",
  "lead_source": "Referral",
  "installation_date": "2024-12-15",
  "warranty_months": 12,
  "special_instructions": "Call before delivery"
}

-- Create index for fast queries
CREATE INDEX idx_po_custom_fields ON po_purchase_orders USING gin(custom_fields);
```

#### Approach 2: Dedicated Custom Fields Table (More Structured)
```sql
CREATE TABLE po_custom_field_definitions (
    id SERIAL PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id),

    field_name TEXT NOT NULL, -- internal name (lowercase, no spaces)
    field_label TEXT NOT NULL, -- display name
    field_type TEXT NOT NULL, -- 'text' | 'number' | 'date' | 'select' | 'checkbox' | 'textarea'
    field_options JSONB, -- for select dropdowns: ["Option 1", "Option 2"]

    default_value TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,

    -- Where it appears
    show_on_create BOOLEAN DEFAULT TRUE,
    show_on_view BOOLEAN DEFAULT TRUE,
    show_on_pdf BOOLEAN DEFAULT TRUE,

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE po_custom_field_values (
    id SERIAL PRIMARY KEY,
    po_id INTEGER REFERENCES po_purchase_orders(id) ON DELETE CASCADE,
    field_id INTEGER REFERENCES po_custom_field_definitions(id) ON DELETE CASCADE,

    field_value TEXT, -- stored as text, converted based on field_type

    company_id UUID NOT NULL REFERENCES companies(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(po_id, field_id) -- one value per field per PO
);
```

**Questions for You:**
- **Which approach do you prefer?** JSONB (simpler) or Structured (more control)?
- What custom fields do you think you'll need? Examples:
  - Sales rep name
  - Project type
  - Lead source
  - Installation/delivery date
  - Deposit amount/date
  - Payment terms
  - Special instructions
  - Warranty period
  - Reference number
  - Commission %
  - Priority level

---

### 5. Default PO Fields Discussion

#### Current Fields
- ✅ PO Number (unique)
- ✅ Client (linked to po_clients)
- ✅ Status (active/completed/cancelled/on_hold)
- ✅ Total Amount
- ✅ PO Date
- ✅ Notes (general)

#### Proposed Additional Default Fields
Let's discuss what should be standard vs. custom:

```sql
-- Potential additions to po_purchase_orders table:
ALTER TABLE po_purchase_orders ADD COLUMN:

-- Financial
project_name TEXT,           -- name/description of the project
subtotal DECIMAL(10,2),      -- before tax/discounts
tax_rate DECIMAL(5,2),       -- sales tax %
tax_amount DECIMAL(10,2),    -- calculated tax
discount_amount DECIMAL(10,2), -- total discount
grand_total DECIMAL(10,2),   -- final amount (computed from line items)

-- Dates
issue_date DATE,             -- when PO was issued (different from created_at)
due_date DATE,               -- when payment/completion is due
delivery_date DATE,          -- expected delivery
completed_date DATE,         -- when work was completed

-- Payment Tracking
deposit_amount DECIMAL(10,2),
deposit_paid_date DATE,
balance_due DECIMAL(10,2),
payment_terms TEXT,          -- "Net 30", "50% deposit", etc.
payment_status TEXT,         -- 'unpaid' | 'partial' | 'paid' | 'overdue'

-- References
quote_number TEXT,           -- link to original quote
invoice_number TEXT,         -- link to invoice
external_po_number TEXT,     -- client's PO number if different

-- Contact/Logistics
billing_address TEXT,
shipping_address TEXT,
contact_person TEXT,         -- specific contact for this PO
contact_phone TEXT,
contact_email TEXT,

-- Workflow
priority TEXT,               -- 'low' | 'normal' | 'high' | 'urgent'
assigned_to UUID REFERENCES auth.users(id), -- owner/sales rep
approval_status TEXT,        -- 'draft' | 'pending_approval' | 'approved' | 'rejected'
approved_by UUID REFERENCES auth.users(id),
approved_at TIMESTAMP,

-- Visibility
is_archived BOOLEAN DEFAULT FALSE,
is_template BOOLEAN DEFAULT FALSE, -- for PO templates feature
template_name TEXT,

-- Metadata
source TEXT,                 -- 'manual' | 'calculator' | 'quote_conversion' | 'template'
tags TEXT[],                 -- array of tags for categorization
```

**Questions for You - Which of these do you need?**

**Essential (should be default fields):**
- [ ] Project name/description
- [ ] Issue date (separate from created_at)
- [ ] Due date (payment due)
- [ ] Delivery/installation date
- [ ] Quote number reference
- [ ] Invoice number reference
- [ ] Payment terms
- [ ] Payment status tracking
- [ ] Assigned to (sales rep/owner)
- [ ] Priority level
- [ ] Deposit amount & paid date
- [ ] Billing/shipping addresses

**Nice-to-Have (could be custom fields):**
- [ ] External PO number (client's reference)
- [ ] Contact person for this specific PO
- [ ] Approval workflow (draft → pending → approved)
- [ ] Tags/categories
- [ ] Source tracking
- [ ] Template functionality

**Definitely Custom Fields:**
- Anything company-specific
- Industry-specific fields
- Fields that vary by project type

---

## Feature Priority & Implementation Order

### Phase 1: Foundation (Session 23)
**Goal**: Core data structures + PO details view

1. ✅ **Database Design** (this document)
2. **Create Migration Script** - All new tables
3. **Update Database Methods** - CRUD for line items, comments, attachments
4. **Build PO Details Page** - Comprehensive view with all data
   - Header: PO info, client info, status
   - Tab 1: Line Items (editable table)
   - Tab 2: Comments/Activity Feed
   - Tab 3: Attachments
   - Tab 4: Custom Fields
   - Tab 5: History/Audit Log

### Phase 2: Line Items (Session 23-24)
5. **Line Items UI** - Add/edit/remove items
6. **Auto-calculate Totals** - Subtotal → discounts → tax → grand total
7. **Unit of Measure System** - Dropdown with common units

### Phase 3: Comments & Activity (Session 24)
8. **Comments UI** - Add/view comments
9. **Activity Feed** - Auto-log system events
10. **Internal Notes** - Toggle visibility

### Phase 4: Attachments (Session 24-25)
11. **File Upload** - Supabase Storage integration
12. **File Management** - View, download, delete
13. **Attachment Types** - Categorization

### Phase 5: Custom Fields (Session 25)
14. **Choose Approach** - JSONB vs. Structured
15. **Admin UI** - Define custom fields (if structured)
16. **PO Form Integration** - Show custom fields on create/edit
17. **Validation** - Required fields, data types

### Phase 6: Advanced Features (Session 26-27)
18. **PDF Export** - Generate professional PO documents
19. **Email System** - Send POs to clients
20. **Date Range Filtering** - Enhanced search
21. **Table Sorting** - Sortable columns
22. **PO Templates** - Reusable PO configurations

### Phase 7: Analytics (Session 28)
23. **Reporting Dashboard** - Metrics and insights
24. **Charts** - Revenue, status breakdown, trends

---

## Decision Points - Let's Discuss

### 1. Line Items Tax & Discounts
**Option A**: Line-item level (most flexible)
- Each line has its own discount % and tax %
- Good for mixed orders (some items taxed, some not)

**Option B**: PO level only (simpler)
- One discount and one tax rate for entire PO
- Cleaner UI, easier to understand

**Option C**: Hybrid (recommended)
- Tax at PO level (one rate applies to all)
- Discount available at both line and PO level

**Your preference?**

### 2. Custom Fields Approach
**JSONB Pros**:
- Simple to implement
- Infinitely flexible
- No UI needed to define fields
- Just edit the JSON

**JSONB Cons**:
- Less structured
- No UI validation
- Harder to report on
- No field definitions/labels

**Structured Pros**:
- Admin can define fields in UI
- Proper validation
- Field types (text, number, date, dropdown)
- Required field enforcement
- Better reporting

**Structured Cons**:
- More complex to build
- Extra admin UI needed
- More tables to manage

**Your preference?**

### 3. Payment Tracking
Do you want to track payments within the PO system?

**Option A**: Simple status field
- Just "unpaid", "partial", "paid"
- Track deposit paid date
- No detailed payment history

**Option B**: Full payment tracking
- Separate `po_payments` table
- Multiple payments per PO
- Payment date, amount, method
- Full payment history

**Your preference?**

### 4. Approval Workflow
Do you need PO approval before sending to client?

**Simple**:
- Draft → Active (manual status change)

**Advanced**:
- Draft → Pending Approval → Approved/Rejected → Active
- Approval permissions by role
- Email notifications for approvals

**Your preference?**

---

## Next Steps

1. **Review this document** - Let me know your thoughts
2. **Answer the decision questions** - I'll finalize the schema
3. **Prioritize features** - What do you want first?
4. **Start building** - Migration script → Database methods → UI

---

## Questions Summary

Please answer these to help me build the right system for you:

### Line Items
- Tax per line or PO level?
- Discount per line or PO level?
- Common units of measure?
- Link to future products/inventory table?

### Comments
- Edit/delete comments?
- Rich text or plain text?
- Attachments on comments or separate?

### Attachments
- File types to support?
- Max file size?
- Organize by type?
- Internal-only attachments?

### Custom Fields
- **JSONB or Structured approach?** (pick one)
- What custom fields do you need?

### Default Fields
- Which proposed fields should be standard?
- Which should be custom?

### Payment Tracking
- Simple status or full payment history?

### Approval Workflow
- Simple (manual) or advanced (automated)?

### Priority
- What features do you want first?
- What can wait for later phases?

---

**Let me know your answers and we'll start building!** 🚀
