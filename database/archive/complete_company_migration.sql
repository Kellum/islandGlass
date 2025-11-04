-- ============================================================
-- Complete Company-Scoped Migration
-- Island Glass & Mirror CRM
-- ============================================================
--
-- WHAT THIS DOES:
-- - Creates companies table and user_profiles
-- - Creates ALL tables with company_id from the start
-- - Sets up company-scoped RLS policies
-- - Creates user-private tables
-- - Creates collaboration tables
--
-- RUN THIS INSTEAD OF: glassprice_migration.sql + company_scoped_migration.sql
-- This is a fresh start with the correct schema.
--
-- ============================================================

BEGIN;

-- ============================================================
-- STEP 1: COMPANIES & USER PROFILES
-- ============================================================

-- Create companies table
CREATE TABLE IF NOT EXISTS companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  role TEXT DEFAULT 'user',
  preferences JSONB DEFAULT '{}',
  company_id UUID NOT NULL REFERENCES companies(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users see only their own profile
DROP POLICY IF EXISTS "user_profiles_policy" ON user_profiles;
CREATE POLICY "user_profiles_policy" ON user_profiles
  FOR ALL
  USING (user_id = auth.uid());

-- Insert Island Glass & Mirror
INSERT INTO companies (name)
VALUES ('Island Glass & Mirror')
ON CONFLICT (name) DO NOTHING;

-- Create profiles for existing users
INSERT INTO user_profiles (user_id, company_id)
SELECT
  u.id as user_id,
  (SELECT id FROM companies WHERE name = 'Island Glass & Mirror') as company_id
FROM auth.users u
WHERE NOT EXISTS (
  SELECT 1 FROM user_profiles WHERE user_id = u.id
)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================================
-- STEP 2: GLASS CALCULATOR TABLES (COMPANY-SCOPED)
-- ============================================================

-- Glass configuration (base pricing matrix)
CREATE TABLE IF NOT EXISTS glass_config (
  id SERIAL PRIMARY KEY,
  thickness TEXT NOT NULL,
  type TEXT NOT NULL,
  base_price DECIMAL(10,2),
  polish_price DECIMAL(10,2),
  only_tempered BOOLEAN DEFAULT FALSE,
  no_polish BOOLEAN DEFAULT FALSE,
  never_tempered BOOLEAN DEFAULT FALSE,

  -- Company scoping
  company_id UUID NOT NULL REFERENCES companies(id),

  -- Audit trail
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP,

  UNIQUE(thickness, type, company_id)
);

-- Markups (tempered, shape)
CREATE TABLE IF NOT EXISTS markups (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  percentage DECIMAL(5,2),

  company_id UUID NOT NULL REFERENCES companies(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP,

  UNIQUE(name, company_id)
);

-- Beveled edge pricing
CREATE TABLE IF NOT EXISTS beveled_pricing (
  id SERIAL PRIMARY KEY,
  glass_thickness TEXT NOT NULL,
  price_per_inch DECIMAL(10,2),

  company_id UUID NOT NULL REFERENCES companies(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP,

  UNIQUE(glass_thickness, company_id)
);

-- Clipped corners pricing
CREATE TABLE IF NOT EXISTS clipped_corners_pricing (
  id SERIAL PRIMARY KEY,
  glass_thickness TEXT NOT NULL,
  clip_size TEXT NOT NULL,
  price_per_corner DECIMAL(10,2),

  company_id UUID NOT NULL REFERENCES companies(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP,

  UNIQUE(glass_thickness, clip_size, company_id)
);

-- ============================================================
-- STEP 3: PO TRACKER TABLES (COMPANY-SCOPED)
-- ============================================================

-- Clients
CREATE TABLE IF NOT EXISTS po_clients (
  id SERIAL PRIMARY KEY,
  company_name TEXT NOT NULL,
  contact_name TEXT,
  phone TEXT,
  email TEXT,
  address TEXT,
  city TEXT,
  state TEXT,
  zip TEXT,
  client_type TEXT DEFAULT 'contractor',
  notes TEXT,

  company_id UUID NOT NULL REFERENCES companies(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP
);

-- Purchase Orders
CREATE TABLE IF NOT EXISTS po_purchase_orders (
  id SERIAL PRIMARY KEY,
  po_number TEXT UNIQUE,
  client_id INTEGER REFERENCES po_clients(id),
  status TEXT DEFAULT 'quoted',
  total_amount DECIMAL(10,2),
  due_date DATE,
  notes TEXT,

  company_id UUID NOT NULL REFERENCES companies(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP
);

-- Activities (calls, emails, meetings)
CREATE TABLE IF NOT EXISTS po_activities (
  id SERIAL PRIMARY KEY,
  client_id INTEGER REFERENCES po_clients(id),
  activity_type TEXT NOT NULL,
  description TEXT,
  activity_date TIMESTAMP DEFAULT NOW(),

  company_id UUID NOT NULL REFERENCES companies(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP
);

-- ============================================================
-- STEP 4: INVENTORY TABLES (COMPANY-SCOPED)
-- ============================================================

-- Categories
CREATE TABLE IF NOT EXISTS inventory_categories (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,

  company_id UUID NOT NULL REFERENCES companies(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP,

  UNIQUE(name, company_id)
);

-- Units
CREATE TABLE IF NOT EXISTS inventory_units (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,

  company_id UUID NOT NULL REFERENCES companies(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP,

  UNIQUE(name, company_id)
);

-- Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  contact_name TEXT,
  phone TEXT,
  email TEXT,
  website TEXT,

  company_id UUID NOT NULL REFERENCES companies(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP
);

-- Items
CREATE TABLE IF NOT EXISTS inventory_items (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category_id INTEGER REFERENCES inventory_categories(id),
  unit_id INTEGER REFERENCES inventory_units(id),
  supplier_id INTEGER REFERENCES suppliers(id),
  quantity DECIMAL(10,2) DEFAULT 0,
  cost_per_unit DECIMAL(10,2),
  low_stock_threshold DECIMAL(10,2),

  company_id UUID NOT NULL REFERENCES companies(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP
);

-- ============================================================
-- STEP 5: USER-PRIVATE TABLES
-- ============================================================

-- Bookmarks (user-private)
CREATE TABLE IF NOT EXISTS user_bookmarks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  entity_type TEXT NOT NULL,
  entity_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE user_bookmarks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_bookmarks_policy" ON user_bookmarks
  FOR ALL USING (user_id = auth.uid());

-- Private Notes (user-private)
CREATE TABLE IF NOT EXISTS user_private_notes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  entity_type TEXT NOT NULL,
  entity_id INTEGER NOT NULL,
  note_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE user_private_notes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_private_notes_policy" ON user_private_notes
  FOR ALL USING (user_id = auth.uid());

-- Dashboard Settings (user-private)
CREATE TABLE IF NOT EXISTS user_dashboard_settings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  settings JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id)
);

ALTER TABLE user_dashboard_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_dashboard_settings_policy" ON user_dashboard_settings
  FOR ALL USING (user_id = auth.uid());

-- Notifications (user-private)
CREATE TABLE IF NOT EXISTS user_notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  notification_type TEXT NOT NULL,
  entity_type TEXT,
  entity_id INTEGER,
  message TEXT NOT NULL,
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE user_notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_notifications_policy" ON user_notifications
  FOR ALL USING (user_id = auth.uid());

-- ============================================================
-- STEP 6: COLLABORATION TABLES (COMPANY-SHARED)
-- ============================================================

-- Comments (company-shared)
CREATE TABLE IF NOT EXISTS entity_comments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id),
  entity_type TEXT NOT NULL,
  entity_id INTEGER NOT NULL,
  comment_text TEXT NOT NULL,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  mentions UUID[],
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP
);

ALTER TABLE entity_comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "entity_comments_select" ON entity_comments
  FOR SELECT USING (
    company_id = (SELECT company_id FROM user_profiles WHERE user_id = auth.uid())
    AND deleted_at IS NULL
  );

CREATE POLICY "entity_comments_insert" ON entity_comments
  FOR INSERT WITH CHECK (
    company_id = (SELECT company_id FROM user_profiles WHERE user_id = auth.uid())
  );

CREATE POLICY "entity_comments_update" ON entity_comments
  FOR UPDATE USING (created_by = auth.uid());

-- ============================================================
-- STEP 7: RLS POLICIES FOR COMPANY-SCOPED TABLES
-- ============================================================

-- Helper function to create standard RLS policies
CREATE OR REPLACE FUNCTION create_company_rls_policies(p_table_name TEXT) RETURNS VOID AS $$
BEGIN
  -- Enable RLS
  EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', p_table_name);

  -- SELECT policy
  EXECUTE format('
    CREATE POLICY %I ON %I
    FOR SELECT USING (
      company_id = (SELECT company_id FROM user_profiles WHERE user_id = auth.uid())
      AND deleted_at IS NULL
    )
  ', p_table_name || '_select', p_table_name);

  -- INSERT policy
  EXECUTE format('
    CREATE POLICY %I ON %I
    FOR INSERT WITH CHECK (
      company_id = (SELECT company_id FROM user_profiles WHERE user_id = auth.uid())
    )
  ', p_table_name || '_insert', p_table_name);

  -- UPDATE policy
  EXECUTE format('
    CREATE POLICY %I ON %I
    FOR UPDATE USING (
      company_id = (SELECT company_id FROM user_profiles WHERE user_id = auth.uid())
    )
  ', p_table_name || '_update', p_table_name);

  -- DELETE policy
  EXECUTE format('
    CREATE POLICY %I ON %I
    FOR DELETE USING (
      company_id = (SELECT company_id FROM user_profiles WHERE user_id = auth.uid())
    )
  ', p_table_name || '_delete', p_table_name);

  RAISE NOTICE 'Created RLS policies for: %', p_table_name;
END;
$$ LANGUAGE plpgsql;

-- Apply RLS to all company-scoped tables
SELECT create_company_rls_policies('glass_config');
SELECT create_company_rls_policies('markups');
SELECT create_company_rls_policies('beveled_pricing');
SELECT create_company_rls_policies('clipped_corners_pricing');
SELECT create_company_rls_policies('po_clients');
SELECT create_company_rls_policies('po_purchase_orders');
SELECT create_company_rls_policies('po_activities');
SELECT create_company_rls_policies('inventory_categories');
SELECT create_company_rls_policies('inventory_units');
SELECT create_company_rls_policies('suppliers');
SELECT create_company_rls_policies('inventory_items');

-- ============================================================
-- STEP 8: CREATE INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_glass_config_company ON glass_config(company_id);
CREATE INDEX IF NOT EXISTS idx_po_clients_company ON po_clients(company_id);
CREATE INDEX IF NOT EXISTS idx_inventory_items_company ON inventory_items(company_id);
CREATE INDEX IF NOT EXISTS idx_glass_config_deleted ON glass_config(deleted_at);
CREATE INDEX IF NOT EXISTS idx_po_clients_deleted ON po_clients(deleted_at);

-- ============================================================
-- STEP 9: VERIFICATION
-- ============================================================

SELECT 'Migration Complete!' as status;

SELECT 'Companies:' as info, * FROM companies;

SELECT 'User Profiles:' as info, COUNT(*) as count FROM user_profiles;

SELECT
  'Tables Created' as info,
  COUNT(*) as table_count
FROM information_schema.tables
WHERE table_name IN (
  'glass_config', 'markups', 'beveled_pricing', 'clipped_corners_pricing',
  'po_clients', 'po_purchase_orders', 'po_activities',
  'inventory_items', 'inventory_categories', 'inventory_units', 'suppliers',
  'user_bookmarks', 'user_private_notes', 'user_dashboard_settings',
  'user_notifications', 'entity_comments'
);

COMMIT;

-- ============================================================
-- SUCCESS!
-- ============================================================
--
-- All tables created with company_id from the start
-- RLS policies configured correctly
-- Ready to insert seed data
--
-- NEXT: Run setup_glass_calculator.sql (after updating it for company_id)
-- ============================================================
