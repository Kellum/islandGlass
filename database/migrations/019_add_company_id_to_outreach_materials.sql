-- =====================================================
-- Migration: 019_add_company_id_to_outreach_materials
-- Purpose: Add multi-tenant isolation to generated outreach content
-- Created: 2025-11-19
-- Part of: Multi-tenant SaaS implementation
-- =====================================================

-- Step 1: Add company_id column (nullable first)
ALTER TABLE outreach_materials
ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id);

-- Step 2: Backfill from contractors
-- UPDATE outreach_materials om
-- SET company_id = c.company_id
-- FROM contractors c
-- WHERE om.contractor_id = c.id
-- AND om.company_id IS NULL;

-- Step 3: Set default for orphaned records (if needed)
-- UPDATE outreach_materials
-- SET company_id = 'YOUR-COMPANY-UUID-HERE'
-- WHERE company_id IS NULL;

-- Step 4: Make required (commented out until after backfill)
-- ALTER TABLE outreach_materials
-- ALTER COLUMN company_id SET NOT NULL;

-- Step 5: Add index for performance
CREATE INDEX IF NOT EXISTS idx_outreach_materials_company_id
ON outreach_materials(company_id);

-- Step 6: Enable Row Level Security
ALTER TABLE outreach_materials ENABLE ROW LEVEL SECURITY;

-- Step 7: Create RLS policy
DROP POLICY IF EXISTS "company_isolation_outreach_materials" ON outreach_materials;
CREATE POLICY "company_isolation_outreach_materials"
ON outreach_materials
FOR ALL
USING (company_id = (current_setting('app.company_id', true)::UUID));

-- Comments
COMMENT ON COLUMN outreach_materials.company_id IS 'Company that generated this outreach material';
