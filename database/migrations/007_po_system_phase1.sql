-- =====================================================
-- PHASE 1: Purchase Order System - Database Schema
-- Island Glass CRM
-- =====================================================

-- ============================================
-- 1. VENDORS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL,
    vendor_type VARCHAR(50) NOT NULL CHECK (vendor_type IN ('Glass', 'Hardware', 'Materials', 'Services', 'Other')),
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',

    -- QuickBooks Integration
    quickbooks_vendor_id VARCHAR(100) UNIQUE,
    quickbooks_display_name VARCHAR(255),
    quickbooks_sync_enabled BOOLEAN DEFAULT FALSE,
    quickbooks_last_sync TIMESTAMP,

    -- Payment & Terms
    payment_terms VARCHAR(100) DEFAULT 'Net 30',
    account_number VARCHAR(100),
    tax_id VARCHAR(50),

    -- Status & Notes
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,

    -- Metadata
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_vendor_name UNIQUE (vendor_name)
);

-- ============================================
-- 2. PURCHASE ORDERS TABLE
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
-- 3. PURCHASE ORDER ITEMS TABLE
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

    -- Relationship to Window Orders
    window_id INTEGER REFERENCES window_orders(window_id),

    -- Notes
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_line_number UNIQUE (po_id, line_number),
    CONSTRAINT valid_quantities CHECK (quantity > 0 AND quantity_received >= 0 AND quantity_backordered >= 0)
);

-- ============================================
-- 4. PO RECEIVING HISTORY
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
-- 5. PO PAYMENT HISTORY
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
-- 6. ENHANCE JOBS TABLE
-- ============================================
-- Add PO-related columns to existing jobs table
ALTER TABLE jobs
    ADD COLUMN IF NOT EXISTS estimated_material_cost DECIMAL(10,2) DEFAULT 0.00,
    ADD COLUMN IF NOT EXISTS actual_material_cost DECIMAL(10,2) DEFAULT 0.00,
    ADD COLUMN IF NOT EXISTS po_count INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS materials_ordered BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS materials_received BOOLEAN DEFAULT FALSE;

-- ============================================
-- 7. QUICKBOOKS SYNC LOG
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
-- 8. INDEXES FOR PERFORMANCE
-- ============================================

-- Vendors
CREATE INDEX IF NOT EXISTS idx_vendors_type ON vendors(vendor_type);
CREATE INDEX IF NOT EXISTS idx_vendors_active ON vendors(is_active);
CREATE INDEX IF NOT EXISTS idx_vendors_qb_id ON vendors(quickbooks_vendor_id);

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
CREATE INDEX IF NOT EXISTS idx_po_items_window ON po_items(window_id);

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

-- ============================================
-- 9. TRIGGERS FOR AUTO-UPDATE
-- ============================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_vendors_updated_at BEFORE UPDATE ON vendors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_po_updated_at BEFORE UPDATE ON purchase_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_po_items_updated_at BEFORE UPDATE ON po_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 10. FUNCTIONS FOR PO CALCULATIONS
-- ============================================

-- Function to recalculate PO totals
CREATE OR REPLACE FUNCTION recalculate_po_totals(po_id_param INTEGER)
RETURNS VOID AS $$
DECLARE
    items_total DECIMAL(10,2);
    tax_amt DECIMAL(10,2);
    shipping DECIMAL(10,2);
    tax_rt DECIMAL(5,2);
BEGIN
    -- Get current tax rate and shipping
    SELECT tax_rate, shipping_cost
    INTO tax_rt, shipping
    FROM purchase_orders
    WHERE po_id = po_id_param;

    -- Calculate items total
    SELECT COALESCE(SUM(line_total), 0)
    INTO items_total
    FROM po_items
    WHERE po_id = po_id_param;

    -- Calculate tax
    tax_amt := ROUND((items_total * tax_rt / 100), 2);

    -- Update PO totals
    UPDATE purchase_orders
    SET subtotal = items_total,
        tax_amount = tax_amt,
        total_amount = items_total + tax_amt + COALESCE(shipping, 0)
    WHERE po_id = po_id_param;
END;
$$ LANGUAGE plpgsql;

-- Function to update job material costs
CREATE OR REPLACE FUNCTION update_job_material_costs(job_id_param INTEGER)
RETURNS VOID AS $$
DECLARE
    total_cost DECIMAL(10,2);
    po_total INTEGER;
    all_received BOOLEAN;
BEGIN
    -- Calculate total PO cost for this job
    SELECT COALESCE(SUM(total_amount), 0), COUNT(*)
    INTO total_cost, po_total
    FROM purchase_orders
    WHERE job_id = job_id_param
    AND status NOT IN ('Draft', 'Cancelled');

    -- Check if all POs are received
    SELECT BOOL_AND(status = 'Received')
    INTO all_received
    FROM purchase_orders
    WHERE job_id = job_id_param
    AND status NOT IN ('Draft', 'Cancelled');

    -- Update job
    UPDATE jobs
    SET actual_material_cost = total_cost,
        po_count = po_total,
        materials_ordered = (po_total > 0),
        materials_received = COALESCE(all_received, FALSE)
    WHERE job_id = job_id_param;
END;
$$ LANGUAGE plpgsql;

-- Trigger to recalculate PO totals when items change
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

CREATE TRIGGER po_items_changed
AFTER INSERT OR UPDATE OR DELETE ON po_items
FOR EACH ROW EXECUTE FUNCTION trigger_recalculate_po_totals();

-- Trigger to update job costs when PO changes
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

CREATE TRIGGER po_changed
AFTER INSERT OR UPDATE OR DELETE ON purchase_orders
FOR EACH ROW EXECUTE FUNCTION trigger_update_job_costs();

-- ============================================
-- 11. SEED DATA - DEFAULT VENDORS
-- ============================================
INSERT INTO vendors (vendor_name, vendor_type, contact_person, email, phone, is_active)
VALUES
    ('Main Glass Supplier', 'Glass', 'John Smith', 'orders@glassupply.com', '555-0100', TRUE),
    ('Hardware Depot', 'Hardware', 'Jane Doe', 'sales@hardwaredepot.com', '555-0200', TRUE),
    ('Building Materials Co', 'Materials', 'Bob Johnson', 'info@buildmat.com', '555-0300', TRUE)
ON CONFLICT (vendor_name) DO NOTHING;

-- ============================================
-- 12. GRANT PERMISSIONS
-- ============================================
-- Note: Adjust these based on your user roles
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- =====================================================
-- END OF PHASE 1 MIGRATION
-- =====================================================
