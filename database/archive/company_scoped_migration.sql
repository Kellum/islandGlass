-- ============================================================
-- Company-Scoped Data Model Migration
-- Island Glass & Mirror CRM
-- ============================================================
--
-- WHAT THIS DOES:
-- Migrates from user_id isolation to company_id shared data model
-- - All employees at Island Glass see same pricing, clients, inventory
-- - Tracks who created/edited each record (audit trail)
-- - Enables soft deletes with recovery
-- - Maintains security (RLS by company_id)
--
-- TABLES AFFECTED: 17 total
-- - contractors, po_clients, po_purchase_orders, po_activities
-- - glass_config, markups, beveled_pricing, clipped_corners_pricing
-- - inventory_items, inventory_categories, inventory_units, suppliers
-- - outreach_emails, call_scripts, interactions, api_usage
--
-- SAFETY: This script is idempotent (safe to run multiple times)
-- ============================================================

BEGIN;

-- ============================================================
-- PHASE 1: CREATE COMPANIES TABLE & USER_PROFILES
-- ============================================================

-- Create companies table
CREATE TABLE IF NOT EXISTS companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create user_profiles table (if not exists)
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  role TEXT DEFAULT 'user',
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Enable RLS on user_profiles
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for user_profiles (users can see only their own profile)
DROP POLICY IF EXISTS "user_profiles_policy" ON user_profiles;
CREATE POLICY "user_profiles_policy" ON user_profiles
  FOR ALL
  USING (user_id = auth.uid());

-- Add company_id to user_profiles (if not exists)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'user_profiles' AND column_name = 'company_id'
  ) THEN
    ALTER TABLE user_profiles ADD COLUMN company_id UUID REFERENCES companies(id);
  END IF;
END $$;

-- Insert Island Glass & Mirror company (if not exists)
INSERT INTO companies (name)
VALUES ('Island Glass & Mirror')
ON CONFLICT (name) DO NOTHING;

-- Link all existing users to Island Glass & Mirror
UPDATE user_profiles
SET company_id = (SELECT id FROM companies WHERE name = 'Island Glass & Mirror')
WHERE company_id IS NULL;

-- Create user_profiles for any auth.users that don't have profiles yet
INSERT INTO user_profiles (user_id, company_id)
SELECT
  u.id as user_id,
  (SELECT id FROM companies WHERE name = 'Island Glass & Mirror') as company_id
FROM auth.users u
WHERE NOT EXISTS (
  SELECT 1 FROM user_profiles WHERE user_id = u.id
)
ON CONFLICT (user_id) DO NOTHING;

-- Make company_id required after migration
ALTER TABLE user_profiles ALTER COLUMN company_id SET NOT NULL;

-- ============================================================
-- PHASE 2: HELPER FUNCTION FOR AUDIT COLUMNS
-- ============================================================

-- Function to add audit columns to any table
CREATE OR REPLACE FUNCTION add_audit_columns(p_table_name TEXT) RETURNS VOID AS $$
BEGIN
  -- Add created_by (if not exists)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = p_table_name AND column_name = 'created_by'
  ) THEN
    EXECUTE format('ALTER TABLE %I ADD COLUMN created_by UUID REFERENCES auth.users(id)', p_table_name);
  END IF;

  -- Add created_at (if not exists)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = p_table_name AND column_name = 'created_at'
  ) THEN
    EXECUTE format('ALTER TABLE %I ADD COLUMN created_at TIMESTAMP DEFAULT NOW()', p_table_name);
  END IF;

  -- Add updated_by (if not exists)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = p_table_name AND column_name = 'updated_by'
  ) THEN
    EXECUTE format('ALTER TABLE %I ADD COLUMN updated_by UUID REFERENCES auth.users(id)', p_table_name);
  END IF;

  -- Add updated_at (if not exists)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = p_table_name AND column_name = 'updated_at'
  ) THEN
    EXECUTE format('ALTER TABLE %I ADD COLUMN updated_at TIMESTAMP DEFAULT NOW()', p_table_name);
  END IF;

  -- Add deleted_by (if not exists)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = p_table_name AND column_name = 'deleted_by'
  ) THEN
    EXECUTE format('ALTER TABLE %I ADD COLUMN deleted_by UUID REFERENCES auth.users(id)', p_table_name);
  END IF;

  -- Add deleted_at (if not exists)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = p_table_name AND column_name = 'deleted_at'
  ) THEN
    EXECUTE format('ALTER TABLE %I ADD COLUMN deleted_at TIMESTAMP', p_table_name);
  END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- PHASE 3: REFACTOR TABLE FUNCTION
-- ============================================================

-- Function to refactor a table from user_id to company_id
CREATE OR REPLACE FUNCTION refactor_to_company_scope(p_table_name TEXT) RETURNS VOID AS $$
DECLARE
  policy_record RECORD;
BEGIN
  -- 0. Check if table exists first
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_name = p_table_name
  ) THEN
    RAISE NOTICE 'Table % does not exist, skipping...', p_table_name;
    RETURN;
  END IF;

  RAISE NOTICE 'Refactoring table: %', p_table_name;

  -- 1. Drop all existing RLS policies for this table
  FOR policy_record IN
    SELECT policyname
    FROM pg_policies
    WHERE tablename = p_table_name
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON %I', policy_record.policyname, p_table_name);
  END LOOP;

  -- 2. Add company_id column (if not exists)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = p_table_name AND column_name = 'company_id'
  ) THEN
    EXECUTE format('ALTER TABLE %I ADD COLUMN company_id UUID REFERENCES companies(id)', p_table_name);
  END IF;

  -- 3. Migrate existing data: set company_id from user's company
  -- (assumes user_id column exists and user_profiles has company_id)
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = p_table_name AND column_name = 'user_id'
  ) THEN
    EXECUTE format('
      UPDATE %I
      SET company_id = (
        SELECT company_id
        FROM user_profiles
        WHERE user_id = %I.user_id
        LIMIT 1
      )
      WHERE company_id IS NULL
    ', p_table_name, p_table_name);

    -- 4. Migrate created_by from user_id (for audit trail)
    IF EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_name = p_table_name AND column_name = 'created_by'
    ) THEN
      EXECUTE format('
        UPDATE %I
        SET created_by = user_id
        WHERE created_by IS NULL AND user_id IS NOT NULL
      ', p_table_name);
    END IF;
  END IF;

  -- 5. If company_id is still NULL, set to Island Glass (fallback)
  EXECUTE format('
    UPDATE %I
    SET company_id = (SELECT id FROM companies WHERE name = ''Island Glass & Mirror'')
    WHERE company_id IS NULL
  ', p_table_name);

  -- 6. Make company_id required
  EXECUTE format('ALTER TABLE %I ALTER COLUMN company_id SET NOT NULL', p_table_name);

  -- 7. Add audit columns
  PERFORM add_audit_columns(p_table_name);

  -- 8. Create new company-scoped RLS policies

  -- SELECT policy: Users can view their company's data
  EXECUTE format('
    CREATE POLICY %I ON %I
    FOR SELECT
    USING (
      company_id = (
        SELECT company_id
        FROM user_profiles
        WHERE user_id = auth.uid()
      )
      AND deleted_at IS NULL
    )
  ', p_table_name || '_select_policy', p_table_name);

  -- INSERT policy: Users can insert for their company
  EXECUTE format('
    CREATE POLICY %I ON %I
    FOR INSERT
    WITH CHECK (
      company_id = (
        SELECT company_id
        FROM user_profiles
        WHERE user_id = auth.uid()
      )
    )
  ', p_table_name || '_insert_policy', p_table_name);

  -- UPDATE policy: Users can update their company's data
  EXECUTE format('
    CREATE POLICY %I ON %I
    FOR UPDATE
    USING (
      company_id = (
        SELECT company_id
        FROM user_profiles
        WHERE user_id = auth.uid()
      )
    )
  ', p_table_name || '_update_policy', p_table_name);

  -- DELETE policy: Users can delete their company's data
  EXECUTE format('
    CREATE POLICY %I ON %I
    FOR DELETE
    USING (
      company_id = (
        SELECT company_id
        FROM user_profiles
        WHERE user_id = auth.uid()
      )
    )
  ', p_table_name || '_delete_policy', p_table_name);

  -- 9. Drop user_id column (optional - keep for now as reference)
  -- EXECUTE format('ALTER TABLE %I DROP COLUMN IF EXISTS user_id', p_table_name);

  RAISE NOTICE 'Successfully refactored table: %', p_table_name;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- PHASE 4: REFACTOR ALL 17 TABLES
-- ============================================================

-- CRM Tables (Contractors/Sales)
SELECT refactor_to_company_scope('contractors');
SELECT refactor_to_company_scope('outreach_emails');
SELECT refactor_to_company_scope('call_scripts');
SELECT refactor_to_company_scope('interactions');
SELECT refactor_to_company_scope('api_usage');

-- PO Tracker Tables (Clients/Manufacturing)
SELECT refactor_to_company_scope('po_clients');
SELECT refactor_to_company_scope('po_purchase_orders');
SELECT refactor_to_company_scope('po_activities');

-- Glass Calculator Tables
SELECT refactor_to_company_scope('glass_config');
SELECT refactor_to_company_scope('markups');
SELECT refactor_to_company_scope('beveled_pricing');
SELECT refactor_to_company_scope('clipped_corners_pricing');

-- Inventory Tables
SELECT refactor_to_company_scope('inventory_items');
SELECT refactor_to_company_scope('inventory_categories');
SELECT refactor_to_company_scope('inventory_units');
SELECT refactor_to_company_scope('suppliers');

-- ============================================================
-- PHASE 5: CREATE USER-PRIVATE TABLES
-- ============================================================

-- User Bookmarks (private per user)
CREATE TABLE IF NOT EXISTS user_bookmarks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  entity_type TEXT NOT NULL, -- 'client', 'contractor', 'po', 'inventory'
  entity_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE user_bookmarks ENABLE ROW LEVEL SECURITY;

-- RLS: Users see only their bookmarks
CREATE POLICY "user_bookmarks_policy" ON user_bookmarks
  FOR ALL
  USING (user_id = auth.uid());

-- User Private Notes (private per user)
CREATE TABLE IF NOT EXISTS user_private_notes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  entity_type TEXT NOT NULL, -- 'client', 'contractor', 'po', 'inventory'
  entity_id INTEGER NOT NULL,
  note_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE user_private_notes ENABLE ROW LEVEL SECURITY;

-- RLS: Users see only their notes
CREATE POLICY "user_private_notes_policy" ON user_private_notes
  FOR ALL
  USING (user_id = auth.uid());

-- User Dashboard Settings (private per user)
CREATE TABLE IF NOT EXISTS user_dashboard_settings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  settings JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Enable RLS
ALTER TABLE user_dashboard_settings ENABLE ROW LEVEL SECURITY;

-- RLS: Users see only their settings
CREATE POLICY "user_dashboard_settings_policy" ON user_dashboard_settings
  FOR ALL
  USING (user_id = auth.uid());

-- User Notifications (private per user)
CREATE TABLE IF NOT EXISTS user_notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  notification_type TEXT NOT NULL, -- 'mention', 'assignment', 'comment', 'system'
  entity_type TEXT, -- 'client', 'contractor', 'po'
  entity_id INTEGER,
  message TEXT NOT NULL,
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE user_notifications ENABLE ROW LEVEL SECURITY;

-- RLS: Users see only their notifications
CREATE POLICY "user_notifications_policy" ON user_notifications
  FOR ALL
  USING (user_id = auth.uid());

-- ============================================================
-- PHASE 6: CREATE COLLABORATION TABLES (COMPANY-SHARED)
-- ============================================================

-- Entity Comments (company-shared)
CREATE TABLE IF NOT EXISTS entity_comments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id),
  entity_type TEXT NOT NULL, -- 'client', 'contractor', 'po', 'inventory'
  entity_id INTEGER NOT NULL,
  comment_text TEXT NOT NULL,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  mentions UUID[], -- Array of user_ids mentioned
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP
);

-- Enable RLS
ALTER TABLE entity_comments ENABLE ROW LEVEL SECURITY;

-- RLS: Users can view their company's comments
CREATE POLICY "entity_comments_select_policy" ON entity_comments
  FOR SELECT
  USING (
    company_id = (
      SELECT company_id
      FROM user_profiles
      WHERE user_id = auth.uid()
    )
    AND deleted_at IS NULL
  );

-- RLS: Users can insert comments for their company
CREATE POLICY "entity_comments_insert_policy" ON entity_comments
  FOR INSERT
  WITH CHECK (
    company_id = (
      SELECT company_id
      FROM user_profiles
      WHERE user_id = auth.uid()
    )
  );

-- RLS: Users can update their own comments
CREATE POLICY "entity_comments_update_policy" ON entity_comments
  FOR UPDATE
  USING (created_by = auth.uid());

-- RLS: Users can delete their own comments (soft delete)
CREATE POLICY "entity_comments_delete_policy" ON entity_comments
  FOR UPDATE
  USING (created_by = auth.uid());

-- ============================================================
-- PHASE 7: CREATE INDEXES FOR PERFORMANCE
-- ============================================================

-- Company-scoped table indexes
CREATE INDEX IF NOT EXISTS idx_contractors_company_id ON contractors(company_id);
CREATE INDEX IF NOT EXISTS idx_po_clients_company_id ON po_clients(company_id);
CREATE INDEX IF NOT EXISTS idx_glass_config_company_id ON glass_config(company_id);
CREATE INDEX IF NOT EXISTS idx_inventory_items_company_id ON inventory_items(company_id);

-- Soft delete indexes
CREATE INDEX IF NOT EXISTS idx_contractors_deleted_at ON contractors(deleted_at);
CREATE INDEX IF NOT EXISTS idx_po_clients_deleted_at ON po_clients(deleted_at);
CREATE INDEX IF NOT EXISTS idx_inventory_items_deleted_at ON inventory_items(deleted_at);

-- User-private table indexes
CREATE INDEX IF NOT EXISTS idx_user_bookmarks_user_id ON user_bookmarks(user_id);
CREATE INDEX IF NOT EXISTS idx_user_private_notes_user_id ON user_private_notes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id ON user_notifications(user_id, read);

-- Collaboration table indexes
CREATE INDEX IF NOT EXISTS idx_entity_comments_company_id ON entity_comments(company_id);
CREATE INDEX IF NOT EXISTS idx_entity_comments_entity ON entity_comments(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_comments_created_by ON entity_comments(created_by);

-- ============================================================
-- PHASE 8: VERIFICATION QUERIES
-- ============================================================

-- Show companies
SELECT 'Companies:' as info, * FROM companies;

-- Show user profiles with company linkage
SELECT
  'User Profiles:' as info,
  user_id,
  full_name,
  company_id,
  (SELECT name FROM companies WHERE id = user_profiles.company_id) as company_name
FROM user_profiles;

-- Verify contractors table structure
SELECT
  'Contractors Table Structure:' as info,
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns
WHERE table_name = 'contractors'
  AND column_name IN ('id', 'company_id', 'created_by', 'updated_by', 'deleted_by', 'deleted_at')
ORDER BY ordinal_position;

-- Count records per table
SELECT 'contractors' as table_name, COUNT(*) as record_count FROM contractors WHERE deleted_at IS NULL
UNION ALL
SELECT 'po_clients', COUNT(*) FROM po_clients WHERE deleted_at IS NULL
UNION ALL
SELECT 'glass_config', COUNT(*) FROM glass_config WHERE deleted_at IS NULL
UNION ALL
SELECT 'inventory_items', COUNT(*) FROM inventory_items WHERE deleted_at IS NULL;

-- Show RLS policies
SELECT
  'RLS Policies:' as info,
  tablename,
  policyname,
  cmd as command
FROM pg_policies
WHERE tablename IN ('contractors', 'po_clients', 'glass_config', 'user_bookmarks')
ORDER BY tablename, policyname;

COMMIT;

-- ============================================================
-- MIGRATION COMPLETE!
-- ============================================================
--
-- NEXT STEPS:
-- 1. Update modules/database.py to use company_id and audit trails
-- 2. Test all CRUD operations
-- 3. Update page callbacks to pass user_id for audit trails
-- 4. Build UI for bookmarks, private notes, notifications (Phase 2)
--
-- VERIFY SUCCESS:
-- - All employees see same pricing, clients, inventory
-- - Each record tracks who created/edited it
-- - Soft deletes work (deleted_at IS NOT NULL)
-- - User-private features (bookmarks, notes) only visible to owner
-- - Company-shared comments visible to all employees
--
-- ============================================================
