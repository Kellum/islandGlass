-- ============================================================
-- Client Name Migration + Multiple Contacts System
-- Island Glass & Mirror CRM
-- ============================================================
--
-- WHAT THIS DOES:
-- 1. Renames po_clients.company_name → client_name
-- 2. Creates po_client_contacts table for multiple contacts per client
-- 3. Migrates existing contact_name data to new contacts table
-- 4. Removes old contact_name field from po_clients
--
-- RUN THIS IN: Supabase SQL Editor
--
-- ============================================================

BEGIN;

-- ============================================================
-- STEP 1: Rename company_name to client_name
-- ============================================================

ALTER TABLE po_clients
RENAME COLUMN company_name TO client_name;

-- ============================================================
-- STEP 2: Create po_client_contacts table
-- ============================================================

CREATE TABLE IF NOT EXISTS po_client_contacts (
  id SERIAL PRIMARY KEY,
  client_id INTEGER NOT NULL REFERENCES po_clients(id) ON DELETE CASCADE,

  -- Contact information
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  job_title TEXT,  -- e.g., "Project Manager", "Owner", "Accountant"
  is_primary BOOLEAN DEFAULT FALSE,

  -- Company scoping
  company_id UUID NOT NULL REFERENCES companies(id),

  -- Audit trail
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_by UUID REFERENCES auth.users(id),
  deleted_at TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_po_client_contacts_client_id
  ON po_client_contacts(client_id);

CREATE INDEX IF NOT EXISTS idx_po_client_contacts_company_id
  ON po_client_contacts(company_id);

-- Enable RLS
ALTER TABLE po_client_contacts ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Company-scoped access
DROP POLICY IF EXISTS "po_client_contacts_policy" ON po_client_contacts;
CREATE POLICY "po_client_contacts_policy" ON po_client_contacts
  FOR ALL
  USING (
    company_id = (
      SELECT company_id
      FROM user_profiles
      WHERE user_id = auth.uid()
    )
  );

-- ============================================================
-- STEP 3: Migrate existing contact_name data
-- ============================================================

-- Insert existing contact names as primary contacts
-- This handles the case where contact_name exists and is not null
INSERT INTO po_client_contacts (
  client_id,
  first_name,
  last_name,
  is_primary,
  company_id,
  created_by,
  created_at
)
SELECT
  id as client_id,
  -- Try to split contact_name into first and last
  -- If there's a space, take everything before first space as first_name
  CASE
    WHEN contact_name IS NOT NULL AND position(' ' IN contact_name) > 0
    THEN SUBSTRING(contact_name FROM 1 FOR position(' ' IN contact_name) - 1)
    WHEN contact_name IS NOT NULL
    THEN contact_name
    ELSE 'Contact'
  END as first_name,
  -- Everything after first space is last_name
  CASE
    WHEN contact_name IS NOT NULL AND position(' ' IN contact_name) > 0
    THEN SUBSTRING(contact_name FROM position(' ' IN contact_name) + 1)
    ELSE ''
  END as last_name,
  TRUE as is_primary,
  company_id,
  created_by,
  created_at
FROM po_clients
WHERE contact_name IS NOT NULL AND contact_name != '';

-- ============================================================
-- STEP 4: Remove old contact_name column
-- ============================================================

ALTER TABLE po_clients
DROP COLUMN IF EXISTS contact_name;

-- ============================================================
-- STEP 5: Add helper function to get primary contact
-- ============================================================

-- This function returns the primary contact for a client
CREATE OR REPLACE FUNCTION get_primary_contact(p_client_id INTEGER)
RETURNS TABLE (
  full_name TEXT,
  email TEXT,
  phone TEXT,
  job_title TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    first_name || ' ' || last_name as full_name,
    po_client_contacts.email,
    po_client_contacts.phone,
    po_client_contacts.job_title
  FROM po_client_contacts
  WHERE client_id = p_client_id
    AND is_primary = TRUE
    AND deleted_at IS NULL
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMIT;

-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================
--
-- What changed:
-- ✅ po_clients.company_name → po_clients.client_name
-- ✅ Created po_client_contacts table with RLS
-- ✅ Migrated existing contact_name data to new table
-- ✅ Removed po_clients.contact_name column
-- ✅ Added helper function for primary contact lookup
--
-- Next steps:
-- 1. Update modules/database.py to use client_name
-- 2. Update pages/po_clients.py to use new contacts system
-- 3. Test with existing data
--
-- ============================================================
