-- =====================================================
-- REVISED: Jobs/PO System - Complete Project Management
-- Island Glass CRM
--
-- Key Concept: PO = Job (same entity)
-- Focus: Comprehensive project management hub
-- =====================================================

-- ============================================
-- 1. VENDORS TABLE (Master List)
-- ============================================
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL UNIQUE,
    vendor_type VARCHAR(50) CHECK (vendor_type IN ('Glass', 'Hardware', 'Materials', 'Services', 'Other')),

    -- Contact Information
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),

    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),

    -- Status & Notes
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. MATERIAL TEMPLATES (Master List for Quick Add)
-- ============================================
CREATE TABLE IF NOT EXISTS material_templates (
    template_id SERIAL PRIMARY KEY,
    template_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) CHECK (category IN ('Glass', 'Hardware', 'Frame', 'Misc', 'Custom')),
    description TEXT,

    -- Optional default vendor
    typical_vendor_id INTEGER REFERENCES vendors(vendor_id),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. JOBS TABLE (PO = Job)
-- ============================================
CREATE TABLE IF NOT EXISTS jobs (
    job_id SERIAL PRIMARY KEY,

    -- Job Identification
    po_number VARCHAR(100) NOT NULL UNIQUE,  -- e.g., "01-kellum.ryan-123acme"
    client_id INTEGER REFERENCES po_clients(id),

    -- Dates
    job_date DATE DEFAULT CURRENT_DATE,
    estimated_completion_date DATE,
    actual_completion_date DATE,

    -- Status
    status VARCHAR(50) DEFAULT 'Quote' CHECK (status IN
        ('Quote', 'Scheduled', 'In Progress', 'Pending Materials',
         'Ready for Install', 'Installed', 'Completed', 'Cancelled', 'On Hold')),

    -- Financials
    total_estimate DECIMAL(10,2) DEFAULT 0.00,
    actual_cost DECIMAL(10,2) DEFAULT 0.00,
    material_cost DECIMAL(10,2) DEFAULT 0.00,
    labor_cost DECIMAL(10,2) DEFAULT 0.00,
    profit_margin DECIMAL(5,2),  -- Percentage

    -- Details
    job_description TEXT,
    internal_notes TEXT,
    customer_notes TEXT,

    -- Site Information
    site_address TEXT,
    site_contact_name VARCHAR(255),
    site_contact_phone VARCHAR(50),

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES auth.users(id)
);

-- ============================================
-- 4. JOB WORK ITEMS (What You're Doing)
-- ============================================
CREATE TABLE IF NOT EXISTS job_work_items (
    item_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,

    -- Work Type
    work_type VARCHAR(50) CHECK (work_type IN
        ('Shower', 'Window/IG', 'Mirror', 'Tabletop', 'Mirror Frame', 'Custom')),

    -- Basic Info
    quantity INTEGER DEFAULT 1,
    description TEXT,  -- Custom details

    -- Optional Specifications (JSON for flexibility)
    specifications JSONB,  -- Can store dimensions, glass type, etc. when needed

    -- Costs
    estimated_cost DECIMAL(10,2) DEFAULT 0.00,
    actual_cost DECIMAL(10,2) DEFAULT 0.00,

    -- Status & Ordering
    status VARCHAR(50) DEFAULT 'Pending',
    sort_order INTEGER DEFAULT 0,
    notes TEXT,

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. JOB VENDOR MATERIALS (Material Tracking)
-- ============================================
CREATE TABLE IF NOT EXISTS job_vendor_materials (
    material_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    vendor_id INTEGER REFERENCES vendors(vendor_id),

    -- Material Description (Custom Text Entry)
    description TEXT NOT NULL,  -- e.g., "shower door, crystalline bypass"

    -- Optional template reference
    template_id INTEGER REFERENCES material_templates(template_id),

    -- Tracking
    ordered_date DATE,
    expected_delivery_date DATE,
    actual_delivery_date DATE,

    -- Cost
    cost DECIMAL(10,2) DEFAULT 0.00,

    -- Shipping/Tracking
    tracking_number VARCHAR(100),
    carrier VARCHAR(100),

    -- Status
    status VARCHAR(50) DEFAULT 'Not Ordered' CHECK (status IN
        ('Not Ordered', 'Ordered', 'In Transit', 'Delivered', 'Installed', 'Cancelled')),

    -- Notes
    notes TEXT,

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 6. JOB SITE VISITS
-- ============================================
CREATE TABLE IF NOT EXISTS job_site_visits (
    visit_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,

    -- Visit Details
    visit_date DATE NOT NULL,
    visit_time TIME,
    duration_hours DECIMAL(4,2),

    -- Visit Type
    visit_type VARCHAR(50) CHECK (visit_type IN
        ('Measure/Estimate', 'Install', 'Remeasure', 'Finals',
         'Adjustment', 'Delivery', 'Inspection', 'Service Call', 'Custom')),
    custom_visit_type VARCHAR(100),  -- If visit_type = 'Custom'

    -- Who Went
    employee_name VARCHAR(255),
    employee_id UUID REFERENCES auth.users(id),

    -- Details
    notes TEXT,
    outcome TEXT,
    issues_found TEXT,

    -- Photos (array of file IDs or paths)
    photos TEXT[],

    -- Status
    completed BOOLEAN DEFAULT FALSE,

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 7. JOB FILES (Photos, PDFs, Documents)
-- ============================================
CREATE TABLE IF NOT EXISTS job_files (
    file_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,

    -- File Information
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) CHECK (file_type IN
        ('Photo', 'PDF', 'Drawing', 'Document', 'Video', 'Other')),
    file_size INTEGER,  -- bytes

    -- Storage
    file_path TEXT NOT NULL,  -- Supabase storage URL or path
    thumbnail_path TEXT,  -- For images

    -- Metadata
    description TEXT,
    tags TEXT[],  -- For categorization

    -- Related to specific visit or work item?
    visit_id INTEGER REFERENCES job_site_visits(visit_id),
    work_item_id INTEGER REFERENCES job_work_items(item_id),

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    uploaded_by UUID REFERENCES auth.users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 8. JOB COMMENTS (Employee Discussion)
-- ============================================
CREATE TABLE IF NOT EXISTS job_comments (
    comment_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,

    -- Comment Content
    comment_text TEXT NOT NULL,
    comment_type VARCHAR(50) DEFAULT 'Note' CHECK (comment_type IN
        ('Note', 'Update', 'Issue', 'Resolution', 'Question', 'Answer')),

    -- Author
    user_id UUID NOT NULL REFERENCES auth.users(id),
    user_name VARCHAR(255),

    -- Threading (optional - for replies)
    parent_comment_id INTEGER REFERENCES job_comments(comment_id),

    -- Editing
    edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP,

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 9. JOB SCHEDULE (Calendar Integration)
-- ============================================
CREATE TABLE IF NOT EXISTS job_schedule (
    schedule_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,

    -- Event Details
    event_type VARCHAR(50) CHECK (event_type IN
        ('Measure', 'Install', 'Delivery', 'Follow-up', 'Deadline', 'Custom')),
    custom_event_type VARCHAR(100),

    -- Timing
    scheduled_date DATE NOT NULL,
    scheduled_time TIME,
    duration_hours DECIMAL(4,2),

    -- Assignment
    assigned_to UUID REFERENCES auth.users(id),
    assigned_name VARCHAR(255),

    -- Status
    status VARCHAR(50) DEFAULT 'Scheduled' CHECK (status IN
        ('Scheduled', 'Confirmed', 'In Progress', 'Completed', 'Cancelled', 'Rescheduled')),

    -- Reminders
    send_reminder BOOLEAN DEFAULT FALSE,
    reminder_sent BOOLEAN DEFAULT FALSE,

    -- Notes
    notes TEXT,

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 10. INDEXES FOR PERFORMANCE
-- ============================================

-- Vendors
CREATE INDEX IF NOT EXISTS idx_vendors_name ON vendors(vendor_name);
CREATE INDEX IF NOT EXISTS idx_vendors_type ON vendors(vendor_type);
CREATE INDEX IF NOT EXISTS idx_vendors_active ON vendors(is_active);

-- Material Templates
CREATE INDEX IF NOT EXISTS idx_material_templates_category ON material_templates(category);
CREATE INDEX IF NOT EXISTS idx_material_templates_active ON material_templates(is_active);

-- Jobs
CREATE INDEX IF NOT EXISTS idx_jobs_po_number ON jobs(po_number);
CREATE INDEX IF NOT EXISTS idx_jobs_client ON jobs(client_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_date ON jobs(job_date);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company_id);

-- Work Items
CREATE INDEX IF NOT EXISTS idx_work_items_job ON job_work_items(job_id);
CREATE INDEX IF NOT EXISTS idx_work_items_type ON job_work_items(work_type);

-- Vendor Materials
CREATE INDEX IF NOT EXISTS idx_vendor_materials_job ON job_vendor_materials(job_id);
CREATE INDEX IF NOT EXISTS idx_vendor_materials_vendor ON job_vendor_materials(vendor_id);
CREATE INDEX IF NOT EXISTS idx_vendor_materials_status ON job_vendor_materials(status);

-- Site Visits
CREATE INDEX IF NOT EXISTS idx_site_visits_job ON job_site_visits(job_id);
CREATE INDEX IF NOT EXISTS idx_site_visits_date ON job_site_visits(visit_date);
CREATE INDEX IF NOT EXISTS idx_site_visits_employee ON job_site_visits(employee_id);

-- Files
CREATE INDEX IF NOT EXISTS idx_job_files_job ON job_files(job_id);
CREATE INDEX IF NOT EXISTS idx_job_files_type ON job_files(file_type);

-- Comments
CREATE INDEX IF NOT EXISTS idx_job_comments_job ON job_comments(job_id);
CREATE INDEX IF NOT EXISTS idx_job_comments_user ON job_comments(user_id);

-- Schedule
CREATE INDEX IF NOT EXISTS idx_job_schedule_job ON job_schedule(job_id);
CREATE INDEX IF NOT EXISTS idx_job_schedule_date ON job_schedule(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_job_schedule_assigned ON job_schedule(assigned_to);

-- ============================================
-- 11. TRIGGERS FOR AUTO-UPDATE
-- ============================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to relevant tables
CREATE TRIGGER update_vendors_updated_at BEFORE UPDATE ON vendors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_material_templates_updated_at BEFORE UPDATE ON material_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_items_updated_at BEFORE UPDATE ON job_work_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vendor_materials_updated_at BEFORE UPDATE ON job_vendor_materials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_site_visits_updated_at BEFORE UPDATE ON job_site_visits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_schedule_updated_at BEFORE UPDATE ON job_schedule
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 12. FUNCTIONS FOR JOB CALCULATIONS
-- ============================================

-- Calculate total material cost for a job
CREATE OR REPLACE FUNCTION calculate_job_material_cost(job_id_param INTEGER)
RETURNS DECIMAL AS $$
DECLARE
    total DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(cost), 0)
    INTO total
    FROM job_vendor_materials
    WHERE job_id = job_id_param;

    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- Calculate total work item cost for a job
CREATE OR REPLACE FUNCTION calculate_job_work_item_cost(job_id_param INTEGER)
RETURNS DECIMAL AS $$
DECLARE
    total DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(actual_cost), 0)
    INTO total
    FROM job_work_items
    WHERE job_id = job_id_param;

    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- Update job totals when materials or work items change
CREATE OR REPLACE FUNCTION update_job_costs()
RETURNS TRIGGER AS $$
DECLARE
    job_id_var INTEGER;
    material_total DECIMAL(10,2);
    work_item_total DECIMAL(10,2);
BEGIN
    -- Get job_id from the triggering row
    IF TG_OP = 'DELETE' THEN
        job_id_var := OLD.job_id;
    ELSE
        job_id_var := NEW.job_id;
    END IF;

    -- Calculate totals
    material_total := calculate_job_material_cost(job_id_var);
    work_item_total := calculate_job_work_item_cost(job_id_var);

    -- Update job
    UPDATE jobs
    SET
        material_cost = material_total,
        actual_cost = material_total + COALESCE(labor_cost, 0)
    WHERE job_id = job_id_var;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER job_vendor_materials_changed
AFTER INSERT OR UPDATE OR DELETE ON job_vendor_materials
FOR EACH ROW EXECUTE FUNCTION update_job_costs();

CREATE TRIGGER job_work_items_changed
AFTER INSERT OR UPDATE OR DELETE ON job_work_items
FOR EACH ROW EXECUTE FUNCTION update_job_costs();

-- ============================================
-- 13. SEED DATA
-- ============================================

-- Sample Vendors
INSERT INTO vendors (vendor_name, vendor_type, phone, is_active)
VALUES
    ('Crystal Tempering', 'Glass', '555-0100', TRUE),
    ('ABC Hardware Supply', 'Hardware', '555-0200', TRUE),
    ('Premium Glass Distributors', 'Glass', '555-0300', TRUE)
ON CONFLICT (vendor_name) DO NOTHING;

-- Sample Material Templates
INSERT INTO material_templates (template_name, category, description, sort_order)
VALUES
    ('Shower Door - Crystalline Bypass', 'Glass', 'Standard crystalline bypass shower door', 1),
    ('Window IG Unit - Double Pane', 'Glass', 'Insulated glass unit, double pane', 2),
    ('Mirror - Standard', 'Glass', 'Standard mirror glass', 3),
    ('Door Hardware - Heavy Duty', 'Hardware', 'Heavy duty door hardware set', 4),
    ('Shower Hardware Kit', 'Hardware', 'Complete shower hardware kit', 5)
ON CONFLICT DO NOTHING;

-- =====================================================
-- END OF REVISED JOBS/PO MIGRATION
-- =====================================================
