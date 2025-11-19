-- =====================================================
-- Migration: 018_add_company_id_to_interaction_log
-- Purpose: Add multi-tenant isolation to contractor interaction logs
-- Created: 2025-11-19
-- Part of: Multi-tenant SaaS implementation
-- =====================================================

-- Step 1: Add company_id column (nullable first)
ALTER TABLE interaction_log
ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id);

-- Step 2: Backfill from contractors
-- UPDATE interaction_log il
-- SET company_id = c.company_id
-- FROM contractors c
-- WHERE il.contractor_id = c.id
-- AND il.company_id IS NULL;

-- Step 3: Set default for orphaned records (if needed)
-- UPDATE interaction_log
-- SET company_id = 'YOUR-COMPANY-UUID-HERE'
-- WHERE company_id IS NULL;

-- Step 4: Make required (commented out until after backfill)
-- ALTER TABLE interaction_log
-- ALTER COLUMN company_id SET NOT NULL;

-- Step 5: Add index for performance
CREATE INDEX IF NOT EXISTS idx_interaction_log_company_id
ON interaction_log(company_id);

-- Step 6: Enable Row Level Security
ALTER TABLE interaction_log ENABLE ROW LEVEL SECURITY;

-- Step 7: Create RLS policy
DROP POLICY IF EXISTS "company_isolation_interaction_log" ON interaction_log;
CREATE POLICY "company_isolation_interaction_log"
ON interaction_log
FOR ALL
USING (company_id = (current_setting('app.company_id', true)::UUID));

-- Comments
COMMENT ON COLUMN interaction_log.company_id IS 'Company that owns this interaction record';
