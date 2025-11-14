-- =====================================================
-- SAFE MIGRATION: Add Only Missing Database Objects
-- Island Glass CRM
--
-- This script is IDEMPOTENT - safe to run multiple times
-- It only adds what's currently missing in your database:
--   - purchase_orders table & related tables
--   - locations table
--   - 3 new columns in jobs table
--   - Helper functions for PO generation
-- =====================================================

-- ============================================
-- 1. PURCHASE ORDERS TABLE (Missing)
-- ============================================
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id SERIAL PRIMARY KEY,
    po_number VARCHAR(50) NOT NULL UNIQUE,

    -- Relationships
    vendor_id INTEGER NOT NULL REFERENCES vendors(vendor_id),
    job_id INTEGER REFERENCES jobs(job_id),
    created_by INTEGER NOT NULL REFERENCES users(user_id),

    -- PO Details
    po_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_delivery_date DATE,
    actual_delivery_date DATE,

    -- Status Management
    status VARCHAR(50) NOT NULL DEFAULT 'Draft'
        CHECK (status IN ('Draft', 'Pending Approval', 'Approved', 'Sent to Vendor', 'Partially Received', 'Received', 'Cancelled')),

    -- Financial
    subtotal DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    tax_rate DECIMAL(5,2) DEFAULT 0.00,
    shipping_cost DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    -- Payment Tracking
    payment_status VARCHAR(50) DEFAULT 'Unpaid'
        CHECK (payment_status IN ('Unpaid', 'Partially Paid', 'Paid')),
    amount_paid DECIMAL(10,2) DEFAULT 0.00,

    -- QuickBooks Integration
    quickbooks_po_id VARCHAR(100) UNIQUE,
    quickbooks_txn_id VARCHAR(100),
    quickbooks_sync_enabled BOOLEAN DEFAULT FALSE,
    quickbooks_last_sync TIMESTAMP,

    -- Approval Workflow
    approved_by INTEGER REFERENCES users(user_id),
    approved_at TIMESTAMP,

    -- Shipping & Delivery
    ship_to_address TEXT,
    shipping_method VARCHAR(100),
    tracking_number VARCHAR(100),

    -- Notes & Attachments
    notes TEXT,
    internal_notes TEXT,
    terms_and_conditions TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_dates CHECK (expected_delivery_date IS NULL OR expected_delivery_date >= po_date)
);

-- ============================================
-- 2. PURCHASE ORDER ITEMS TABLE (Missing)
-- ============================================
CREATE TABLE IF NOT EXISTS po_items (
    po_item_id SERIAL PRIMARY KEY,
    po_id INTEGER NOT NULL REFERENCES purchase_orders(po_id) ON DELETE CASCADE,

    -- Item Details
    line_number INTEGER NOT NULL,
    item_type VARCHAR(50) NOT NULL CHECK (item_type IN ('Glass', 'Hardware', 'Material', 'Labor', 'Service', 'Other')),
    description TEXT NOT NULL,

    -- Specifications (for glass and materials)
    glass_type VARCHAR(100),
    glass_thickness VARCHAR(50),
    width DECIMAL(10,2),
    height DECIMAL(10,2),
    square_footage DECIMAL(10,2),

    -- Quantity & Units
    quantity DECIMAL(10,2) NOT NULL DEFAULT 1,
    unit_of_measure VARCHAR(20) DEFAULT 'Each',

    -- Pricing
    unit_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    line_total DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    -- Receiving
    quantity_received DECIMAL(10,2) DEFAULT 0.00,
    quantity_backordered DECIMAL(10,2) DEFAULT 0.00,

    -- QuickBooks Integration
    quickbooks_item_id VARCHAR(100),
    quickbooks_line_id VARCHAR(100),

    -- Relationship to Window Orders (may not exist yet)
    window_id INTEGER, -- removed REFERENCES for now

    -- Notes
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_line_number UNIQUE (po_id, line_number),
    CONSTRAINT valid_quantities CHECK (quantity > 0 AND quantity_received >= 0 AND quantity_backordered >= 0)
);

-- ============================================
-- 3. PO RECEIVING HISTORY (Missing)
-- ============================================
CREATE TABLE IF NOT EXISTS po_receiving_history (
    receiving_id SERIAL PRIMARY KEY,
    po_id INTEGER NOT NULL REFERENCES purchase_orders(po_id),
    po_item_id INTEGER REFERENCES po_items(po_item_id),

    -- Receiving Details
    received_date DATE NOT NULL DEFAULT CURRENT_DATE,
    quantity_received DECIMAL(10,2) NOT NULL,
    received_by INTEGER NOT NULL REFERENCES users(user_id),

    -- Quality Control
    condition VARCHAR(50) DEFAULT 'Good' CHECK (condition IN ('Good', 'Damaged', 'Defective', 'Incomplete')),
    quality_notes TEXT,

    -- Location
    storage_location VARCHAR(255),

    -- Notes
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_received_quantity CHECK (quantity_received > 0)
);

-- ============================================
-- 4. PO PAYMENT HISTORY (Missing)
-- ============================================
CREATE TABLE IF NOT EXISTS po_payment_history (
    payment_id SERIAL PRIMARY KEY,
    po_id INTEGER NOT NULL REFERENCES purchase_orders(po_id),

    -- Payment Details
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) CHECK (payment_method IN ('Check', 'ACH', 'Wire Transfer', 'Credit Card', 'Cash', 'Other')),

    -- Reference
    check_number VARCHAR(50),
    transaction_reference VARCHAR(100),

    -- QuickBooks Integration
    quickbooks_payment_id VARCHAR(100),
    quickbooks_txn_id VARCHAR(100),

    -- Processing
    processed_by INTEGER NOT NULL REFERENCES users(user_id),

    -- Notes
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_payment_amount CHECK (amount_paid > 0)
);

-- ============================================
-- 5. QUICKBOOKS SYNC LOG (Missing)
-- ============================================
CREATE TABLE IF NOT EXISTS quickbooks_sync_log (
    sync_id SERIAL PRIMARY KEY,

    -- Entity Info
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('Vendor', 'PO', 'Payment', 'Item')),
    entity_id INTEGER NOT NULL,

    -- Sync Details
    sync_action VARCHAR(50) NOT NULL CHECK (sync_action IN ('Create', 'Update', 'Delete', 'Fetch')),
    sync_status VARCHAR(50) NOT NULL CHECK (sync_status IN ('Success', 'Failed', 'Pending')),

    -- QuickBooks References
    quickbooks_id VARCHAR(100),
    quickbooks_response TEXT,

    -- Error Handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- User & Timing
    initiated_by INTEGER REFERENCES users(user_id),
    sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 6. ADD MISSING COLUMNS TO JOBS TABLE
-- ============================================

-- From migration 007 (PO system)
DO $$
BEGIN
    -- Check and add estimated_material_cost
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='jobs' AND column_name='estimated_material_cost') THEN
        ALTER TABLE jobs ADD COLUMN estimated_material_cost DECIMAL(10,2) DEFAULT 0.00;
    END IF;

    -- Check and add actual_material_cost
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='jobs' AND column_name='actual_material_cost') THEN
        ALTER TABLE jobs ADD COLUMN actual_material_cost DECIMAL(10,2) DEFAULT 0.00;
    END IF;

    -- Check and add po_count
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='jobs' AND column_name='po_count') THEN
        ALTER TABLE jobs ADD COLUMN po_count INTEGER DEFAULT 0;
    END IF;

    -- Check and add materials_ordered
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='jobs' AND column_name='materials_ordered') THEN
        ALTER TABLE jobs ADD COLUMN materials_ordered BOOLEAN DEFAULT FALSE;
    END IF;

    -- Check and add materials_received
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='jobs' AND column_name='materials_received') THEN
        ALTER TABLE jobs ADD COLUMN materials_received BOOLEAN DEFAULT FALSE;
    END IF;

    -- From migration 009 (PO auto-generation)
    -- Check and add location_code
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='jobs' AND column_name='location_code') THEN
        ALTER TABLE jobs ADD COLUMN location_code VARCHAR(10);
    END IF;

    -- Check and add is_remake
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='jobs' AND column_name='is_remake') THEN
        ALTER TABLE jobs ADD COLUMN is_remake BOOLEAN DEFAULT FALSE;
    END IF;

    -- Check and add is_warranty
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='jobs' AND column_name='is_warranty') THEN
        ALTER TABLE jobs ADD COLUMN is_warranty BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- ============================================
-- 7. LOCATIONS TABLE (Missing)
-- ============================================
CREATE TABLE IF NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    location_code VARCHAR(10) NOT NULL UNIQUE,
    location_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 8. SEED LOCATION DATA
-- ============================================
INSERT INTO locations (location_code, location_name, description, is_active, sort_order)
VALUES
    ('01', 'Fernandina/Yulee, FL', 'Covers Fernandina Beach and Yulee, Florida area', TRUE, 1),
    ('02', 'Georgia', 'All jobs in Georgia', TRUE, 2),
    ('03', 'Jacksonville, FL', 'All jobs in Jacksonville, Florida area', TRUE, 3)
ON CONFLICT (location_code) DO UPDATE SET
    location_name = EXCLUDED.location_name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    sort_order = EXCLUDED.sort_order;

-- ============================================
-- 9. INDEXES FOR PERFORMANCE
-- ============================================

-- Purchase Orders
CREATE INDEX IF NOT EXISTS idx_po_number ON purchase_orders(po_number);
CREATE INDEX IF NOT EXISTS idx_po_vendor ON purchase_orders(vendor_id);
CREATE INDEX IF NOT EXISTS idx_po_job ON purchase_orders(job_id);
CREATE INDEX IF NOT EXISTS idx_po_status ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_po_date ON purchase_orders(po_date);
CREATE INDEX IF NOT EXISTS idx_po_created_by ON purchase_orders(created_by);
CREATE INDEX IF NOT EXISTS idx_po_qb_id ON purchase_orders(quickbooks_po_id);

-- PO Items
CREATE INDEX IF NOT EXISTS idx_po_items_po ON po_items(po_id);
CREATE INDEX IF NOT EXISTS idx_po_items_type ON po_items(item_type);

-- Receiving History
CREATE INDEX IF NOT EXISTS idx_receiving_po ON po_receiving_history(po_id);
CREATE INDEX IF NOT EXISTS idx_receiving_date ON po_receiving_history(received_date);

-- Payment History
CREATE INDEX IF NOT EXISTS idx_payment_po ON po_payment_history(po_id);
CREATE INDEX IF NOT EXISTS idx_payment_date ON po_payment_history(payment_date);

-- QuickBooks Sync Log
CREATE INDEX IF NOT EXISTS idx_qb_sync_entity ON quickbooks_sync_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_qb_sync_status ON quickbooks_sync_log(sync_status);
CREATE INDEX IF NOT EXISTS idx_qb_sync_timestamp ON quickbooks_sync_log(sync_timestamp);

-- Jobs table indexes for PO features
CREATE INDEX IF NOT EXISTS idx_jobs_location_code ON jobs(location_code);
CREATE INDEX IF NOT EXISTS idx_jobs_client_location ON jobs(client_id, location_code);

-- Locations indexes
CREATE INDEX IF NOT EXISTS idx_locations_code ON locations(location_code);
CREATE INDEX IF NOT EXISTS idx_locations_active ON locations(is_active);

-- ============================================
-- 10. HELPER FUNCTIONS
-- ============================================

-- Update timestamp trigger function (may already exist, safe to recreate)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Extract street number function
CREATE OR REPLACE FUNCTION extract_street_number(address_text TEXT)
RETURNS VARCHAR AS $$
DECLARE
    street_number VARCHAR;
BEGIN
    SELECT regexp_replace(address_text, '^[^0-9]*([0-9]+).*', '\1')
    INTO street_number;

    IF street_number = address_text OR street_number = '' THEN
        RETURN NULL;
    END IF;

    RETURN street_number;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Format name for PO function
CREATE OR REPLACE FUNCTION format_name_for_po(
    company_name_param TEXT,
    contact_name_param TEXT,
    is_remake_param BOOLEAN,
    is_warranty_param BOOLEAN
)
RETURNS VARCHAR AS $$
DECLARE
    formatted_name VARCHAR;
    first_name VARCHAR;
    last_name VARCHAR;
    name_parts TEXT[];
BEGIN
    -- Handle remake jobs
    IF is_remake_param = TRUE THEN
        IF contact_name_param IS NOT NULL AND contact_name_param != '' THEN
            name_parts := regexp_split_to_array(TRIM(contact_name_param), '\s+');
            last_name := name_parts[array_length(name_parts, 1)];
            RETURN 'RMK.' || REPLACE(last_name, ' ', '');
        ELSE
            RETURN 'RMK.' || REPLACE(TRIM(company_name_param), ' ', '');
        END IF;
    END IF;

    -- Handle warranty jobs
    IF is_warranty_param = TRUE THEN
        IF contact_name_param IS NOT NULL AND contact_name_param != '' THEN
            name_parts := regexp_split_to_array(TRIM(contact_name_param), '\s+');
            last_name := name_parts[array_length(name_parts, 1)];
            RETURN 'WAR.' || REPLACE(last_name, ' ', '');
        ELSE
            RETURN 'WAR.' || REPLACE(TRIM(company_name_param), ' ', '');
        END IF;
    END IF;

    -- Regular jobs
    IF company_name_param IS NOT NULL AND company_name_param != '' THEN
        formatted_name := REPLACE(TRIM(company_name_param), ' ', '');
    ELSIF contact_name_param IS NOT NULL AND contact_name_param != '' THEN
        name_parts := regexp_split_to_array(TRIM(contact_name_param), '\s+');
        IF array_length(name_parts, 1) >= 2 THEN
            first_name := name_parts[1];
            last_name := name_parts[array_length(name_parts, 1)];
            formatted_name := first_name || '.' || last_name;
        ELSE
            formatted_name := contact_name_param;
        END IF;
    ELSE
        RETURN 'UNKNOWN';
    END IF;

    formatted_name := regexp_replace(formatted_name, '[^a-zA-Z0-9.]', '', 'g');
    RETURN formatted_name;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Count duplicate POs function
CREATE OR REPLACE FUNCTION count_duplicate_pos(
    client_id_param INTEGER,
    location_code_param VARCHAR,
    name_part VARCHAR,
    street_number_param VARCHAR
)
RETURNS INTEGER AS $$
DECLARE
    po_count INTEGER;
    base_po VARCHAR;
BEGIN
    base_po := 'PO-' || location_code_param || '-' || name_part || '.' || street_number_param;

    SELECT COUNT(*)
    INTO po_count
    FROM jobs
    WHERE client_id = client_id_param
        AND location_code = location_code_param
        AND (
            po_number = base_po
            OR po_number LIKE base_po || '-%'
        )
        AND deleted_at IS NULL;

    RETURN COALESCE(po_count, 0);
END;
$$ LANGUAGE plpgsql;

-- Recalculate PO totals function
CREATE OR REPLACE FUNCTION recalculate_po_totals(po_id_param INTEGER)
RETURNS VOID AS $$
DECLARE
    items_total DECIMAL(10,2);
    tax_amt DECIMAL(10,2);
    shipping DECIMAL(10,2);
    tax_rt DECIMAL(5,2);
BEGIN
    SELECT tax_rate, shipping_cost
    INTO tax_rt, shipping
    FROM purchase_orders
    WHERE po_id = po_id_param;

    SELECT COALESCE(SUM(line_total), 0)
    INTO items_total
    FROM po_items
    WHERE po_id = po_id_param;

    tax_amt := ROUND((items_total * tax_rt / 100), 2);

    UPDATE purchase_orders
    SET subtotal = items_total,
        tax_amount = tax_amt,
        total_amount = items_total + tax_amt + COALESCE(shipping, 0)
    WHERE po_id = po_id_param;
END;
$$ LANGUAGE plpgsql;

-- Update job material costs function
CREATE OR REPLACE FUNCTION update_job_material_costs(job_id_param INTEGER)
RETURNS VOID AS $$
DECLARE
    total_cost DECIMAL(10,2);
    po_total INTEGER;
    all_received BOOLEAN;
BEGIN
    SELECT COALESCE(SUM(total_amount), 0), COUNT(*)
    INTO total_cost, po_total
    FROM purchase_orders
    WHERE job_id = job_id_param
    AND status NOT IN ('Draft', 'Cancelled');

    SELECT BOOL_AND(status = 'Received')
    INTO all_received
    FROM purchase_orders
    WHERE job_id = job_id_param
    AND status NOT IN ('Draft', 'Cancelled');

    UPDATE jobs
    SET actual_material_cost = total_cost,
        po_count = po_total,
        materials_ordered = (po_total > 0),
        materials_received = COALESCE(all_received, FALSE)
    WHERE job_id = job_id_param;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 11. TRIGGERS
-- ============================================

-- Trigger functions
CREATE OR REPLACE FUNCTION trigger_recalculate_po_totals()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM recalculate_po_totals(OLD.po_id);
        RETURN OLD;
    ELSE
        PERFORM recalculate_po_totals(NEW.po_id);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION trigger_update_job_costs()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        IF OLD.job_id IS NOT NULL THEN
            PERFORM update_job_material_costs(OLD.job_id);
        END IF;
        RETURN OLD;
    ELSE
        IF NEW.job_id IS NOT NULL THEN
            PERFORM update_job_material_costs(NEW.job_id);
        END IF;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Drop triggers if they exist (to avoid conflicts) and recreate
DROP TRIGGER IF EXISTS update_po_updated_at ON purchase_orders;
CREATE TRIGGER update_po_updated_at BEFORE UPDATE ON purchase_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_po_items_updated_at ON po_items;
CREATE TRIGGER update_po_items_updated_at BEFORE UPDATE ON po_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_locations_updated_at ON locations;
CREATE TRIGGER update_locations_updated_at BEFORE UPDATE ON locations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS po_items_changed ON po_items;
CREATE TRIGGER po_items_changed
AFTER INSERT OR UPDATE OR DELETE ON po_items
FOR EACH ROW EXECUTE FUNCTION trigger_recalculate_po_totals();

DROP TRIGGER IF EXISTS po_changed ON purchase_orders;
CREATE TRIGGER po_changed
AFTER INSERT OR UPDATE OR DELETE ON purchase_orders
FOR EACH ROW EXECUTE FUNCTION trigger_update_job_costs();

-- Add check constraint to jobs table (only if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_remake_or_warranty'
    ) THEN
        ALTER TABLE jobs
        ADD CONSTRAINT chk_remake_or_warranty CHECK (
            NOT (is_remake = TRUE AND is_warranty = TRUE)
        );
    END IF;
END $$;

-- =====================================================
-- MIGRATION COMPLETE!
-- =====================================================

-- Verify what was created
SELECT
    'Tables created/verified:' as status,
    COUNT(*) as count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('purchase_orders', 'po_items', 'po_receiving_history', 'po_payment_history', 'quickbooks_sync_log', 'locations');
