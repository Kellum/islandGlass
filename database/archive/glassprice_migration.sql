-- GlassPricePro Migration to Island Glass Leads
-- Adds: Glass Calculator, PO Tracker, Inventory Management
-- Database: Supabase (PostgreSQL with RLS)
-- Created: 2025-11-02

-- ============================================================
-- GLASS CALCULATOR TABLES
-- ============================================================

-- Glass configuration (base pricing matrix: type × thickness)
CREATE TABLE IF NOT EXISTS glass_config (
    id SERIAL PRIMARY KEY,
    thickness TEXT NOT NULL,      -- '1/8"', '3/16"', '1/4"', '3/8"', '1/2"'
    type TEXT NOT NULL,            -- 'clear', 'bronze', 'gray', 'mirror'
    base_price DECIMAL(10,2),     -- Price per sq ft
    polish_price DECIMAL(10,2),   -- Price per inch for polish
    only_tempered BOOLEAN DEFAULT FALSE,    -- Must be tempered (3/16" clear)
    no_polish BOOLEAN DEFAULT FALSE,        -- Cannot be polished
    never_tempered BOOLEAN DEFAULT FALSE,   -- Cannot be tempered (mirrors)
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(thickness, type, user_id)
);

-- Markup percentages (tempered, shape)
CREATE TABLE IF NOT EXISTS markups (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,            -- 'tempered', 'shape'
    percentage DECIMAL(5,2),       -- e.g., 35.0 for 35%
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(name, user_id)
);

-- Beveled edge pricing
CREATE TABLE IF NOT EXISTS beveled_pricing (
    id SERIAL PRIMARY KEY,
    glass_thickness TEXT NOT NULL,  -- '1/4"', '3/8"', '1/2"'
    price_per_inch DECIMAL(10,2),   -- Price per inch of perimeter
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(glass_thickness, user_id)
);

-- Clipped corners pricing
CREATE TABLE IF NOT EXISTS clipped_corners_pricing (
    id SERIAL PRIMARY KEY,
    glass_thickness TEXT NOT NULL,  -- '1/4"', '3/8"', '1/2"'
    clip_size TEXT NOT NULL,        -- 'under_1', 'over_1'
    price_per_corner DECIMAL(10,2), -- Price per corner
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(glass_thickness, clip_size, user_id)
);

-- ============================================================
-- PO TRACKER TABLES
-- ============================================================

-- Clients (customers for purchase orders)
CREATE TABLE IF NOT EXISTS po_clients (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    state TEXT DEFAULT 'FL',
    zip TEXT,
    client_type TEXT,              -- 'contractor', 'residential', 'commercial'
    tags TEXT[],                   -- Custom tags for filtering
    notes TEXT,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Purchase orders
CREATE TABLE IF NOT EXISTS po_purchase_orders (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES po_clients(id) ON DELETE CASCADE,
    po_number TEXT,
    status TEXT DEFAULT 'quoted',   -- 'quoted', 'ordered', 'in_production', 'completed', 'invoiced'
    total_amount DECIMAL(10,2),
    due_date DATE,
    notes TEXT,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Activity log for clients and POs
CREATE TABLE IF NOT EXISTS po_activities (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES po_clients(id) ON DELETE CASCADE,
    po_id INTEGER REFERENCES po_purchase_orders(id) ON DELETE CASCADE,
    activity_type TEXT,             -- 'call', 'email', 'meeting', 'note'
    description TEXT NOT NULL,
    created_by TEXT,                -- User who created activity
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- INVENTORY TABLES
-- ============================================================

-- Suppliers (shared between inventory and PO tracker)
CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    website TEXT,
    notes TEXT,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Inventory categories
CREATE TABLE IF NOT EXISTS inventory_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(name, user_id)
);

-- Inventory units
CREATE TABLE IF NOT EXISTS inventory_units (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,             -- 'pieces', 'linear feet', 'pounds', 'gallons', 'boxes', 'rolls'
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(name, user_id)
);

-- Inventory items
CREATE TABLE IF NOT EXISTS inventory_items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER REFERENCES inventory_categories(id) ON DELETE SET NULL,
    quantity DECIMAL(10,2) DEFAULT 0,
    unit_id INTEGER REFERENCES inventory_units(id) ON DELETE SET NULL,
    cost_per_unit DECIMAL(10,2),
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    low_stock_threshold DECIMAL(10,2) DEFAULT 10,
    sort_order INTEGER DEFAULT 0,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================================

ALTER TABLE glass_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE markups ENABLE ROW LEVEL SECURITY;
ALTER TABLE beveled_pricing ENABLE ROW LEVEL SECURITY;
ALTER TABLE clipped_corners_pricing ENABLE ROW LEVEL SECURITY;
ALTER TABLE po_clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE po_purchase_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE po_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_units ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_items ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- RLS POLICIES - GLASS CALCULATOR
-- ============================================================

-- glass_config policies
CREATE POLICY "Users can view their own glass_config"
    ON glass_config FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own glass_config"
    ON glass_config FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own glass_config"
    ON glass_config FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own glass_config"
    ON glass_config FOR DELETE
    USING (auth.uid() = user_id);

-- markups policies
CREATE POLICY "Users can view their own markups"
    ON markups FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own markups"
    ON markups FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own markups"
    ON markups FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own markups"
    ON markups FOR DELETE
    USING (auth.uid() = user_id);

-- beveled_pricing policies
CREATE POLICY "Users can view their own beveled_pricing"
    ON beveled_pricing FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own beveled_pricing"
    ON beveled_pricing FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own beveled_pricing"
    ON beveled_pricing FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own beveled_pricing"
    ON beveled_pricing FOR DELETE
    USING (auth.uid() = user_id);

-- clipped_corners_pricing policies
CREATE POLICY "Users can view their own clipped_corners_pricing"
    ON clipped_corners_pricing FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own clipped_corners_pricing"
    ON clipped_corners_pricing FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own clipped_corners_pricing"
    ON clipped_corners_pricing FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own clipped_corners_pricing"
    ON clipped_corners_pricing FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================
-- RLS POLICIES - PO TRACKER
-- ============================================================

-- po_clients policies
CREATE POLICY "Users can view their own po_clients"
    ON po_clients FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own po_clients"
    ON po_clients FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own po_clients"
    ON po_clients FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own po_clients"
    ON po_clients FOR DELETE
    USING (auth.uid() = user_id);

-- po_purchase_orders policies
CREATE POLICY "Users can view their own po_purchase_orders"
    ON po_purchase_orders FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own po_purchase_orders"
    ON po_purchase_orders FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own po_purchase_orders"
    ON po_purchase_orders FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own po_purchase_orders"
    ON po_purchase_orders FOR DELETE
    USING (auth.uid() = user_id);

-- po_activities policies
CREATE POLICY "Users can view their own po_activities"
    ON po_activities FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own po_activities"
    ON po_activities FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own po_activities"
    ON po_activities FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own po_activities"
    ON po_activities FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================
-- RLS POLICIES - INVENTORY
-- ============================================================

-- suppliers policies
CREATE POLICY "Users can view their own suppliers"
    ON suppliers FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own suppliers"
    ON suppliers FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own suppliers"
    ON suppliers FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own suppliers"
    ON suppliers FOR DELETE
    USING (auth.uid() = user_id);

-- inventory_categories policies
CREATE POLICY "Users can view their own inventory_categories"
    ON inventory_categories FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own inventory_categories"
    ON inventory_categories FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own inventory_categories"
    ON inventory_categories FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own inventory_categories"
    ON inventory_categories FOR DELETE
    USING (auth.uid() = user_id);

-- inventory_units policies
CREATE POLICY "Users can view their own inventory_units"
    ON inventory_units FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own inventory_units"
    ON inventory_units FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own inventory_units"
    ON inventory_units FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own inventory_units"
    ON inventory_units FOR DELETE
    USING (auth.uid() = user_id);

-- inventory_items policies
CREATE POLICY "Users can view their own inventory_items"
    ON inventory_items FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own inventory_items"
    ON inventory_items FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own inventory_items"
    ON inventory_items FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own inventory_items"
    ON inventory_items FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================
-- SEED DATA
-- ============================================================
-- Note: Run this section AFTER creating a user account
-- Replace 'YOUR_USER_ID' with actual user ID from auth.users

-- Example seed data (commented out - run manually with real user_id):
/*
-- Glass config for common types
INSERT INTO glass_config (thickness, type, base_price, polish_price, only_tempered, no_polish, never_tempered, user_id)
VALUES
    ('1/8"', 'clear', 8.50, 0.65, FALSE, FALSE, FALSE, 'YOUR_USER_ID'),
    ('3/16"', 'clear', 10.00, 0.75, TRUE, FALSE, FALSE, 'YOUR_USER_ID'),
    ('1/4"', 'clear', 12.50, 0.85, FALSE, FALSE, FALSE, 'YOUR_USER_ID'),
    ('3/8"', 'clear', 18.00, 1.10, FALSE, FALSE, FALSE, 'YOUR_USER_ID'),
    ('1/2"', 'clear', 22.50, 1.35, FALSE, FALSE, FALSE, 'YOUR_USER_ID'),
    ('1/4"', 'bronze', 18.00, 0.85, FALSE, FALSE, FALSE, 'YOUR_USER_ID'),
    ('1/4"', 'gray', 16.50, 0.85, FALSE, FALSE, FALSE, 'YOUR_USER_ID'),
    ('1/4"', 'mirror', 15.00, 0.27, FALSE, TRUE, TRUE, 'YOUR_USER_ID');

-- Default markups
INSERT INTO markups (name, percentage, user_id)
VALUES
    ('tempered', 35.0, 'YOUR_USER_ID'),
    ('shape', 25.0, 'YOUR_USER_ID');

-- Beveled pricing (not available for 1/8")
INSERT INTO beveled_pricing (glass_thickness, price_per_inch, user_id)
VALUES
    ('3/16"', 1.50, 'YOUR_USER_ID'),
    ('1/4"', 2.01, 'YOUR_USER_ID'),
    ('3/8"', 2.91, 'YOUR_USER_ID'),
    ('1/2"', 3.80, 'YOUR_USER_ID');

-- Clipped corners pricing
INSERT INTO clipped_corners_pricing (glass_thickness, clip_size, price_per_corner, user_id)
VALUES
    ('1/4"', 'under_1', 5.50, 'YOUR_USER_ID'),
    ('1/4"', 'over_1', 22.18, 'YOUR_USER_ID'),
    ('3/8"', 'under_1', 7.50, 'YOUR_USER_ID'),
    ('3/8"', 'over_1', 30.00, 'YOUR_USER_ID');

-- Default inventory categories
INSERT INTO inventory_categories (name, user_id)
VALUES
    ('Spacers', 'YOUR_USER_ID'),
    ('Butyl', 'YOUR_USER_ID'),
    ('Desiccant', 'YOUR_USER_ID'),
    ('Molecular Sieve', 'YOUR_USER_ID'),
    ('Glass', 'YOUR_USER_ID'),
    ('Hardware', 'YOUR_USER_ID');

-- Default inventory units
INSERT INTO inventory_units (name, user_id)
VALUES
    ('pieces', 'YOUR_USER_ID'),
    ('linear feet', 'YOUR_USER_ID'),
    ('pounds', 'YOUR_USER_ID'),
    ('gallons', 'YOUR_USER_ID'),
    ('boxes', 'YOUR_USER_ID'),
    ('rolls', 'YOUR_USER_ID');
*/
