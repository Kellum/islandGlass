-- =====================================================
-- Migration: 017_add_company_id_to_api_usage
-- Purpose: Add multi-tenant isolation to API usage tracking
-- Created: 2025-11-19
-- Part of: Multi-tenant SaaS implementation
-- =====================================================

-- Step 1: Add company_id column (nullable first)
ALTER TABLE api_usage
ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id);

-- Step 2: Backfill from contractors if possible
-- UPDATE api_usage au
-- SET company_id = c.company_id
-- FROM contractors c
-- WHERE au.contractor_id = c.id
-- AND au.company_id IS NULL;

-- Step 3: Set default for remaining records (if needed)
-- UPDATE api_usage
-- SET company_id = 'YOUR-COMPANY-UUID-HERE'
-- WHERE company_id IS NULL;

-- Step 4: Make required (commented out until after backfill)
-- ALTER TABLE api_usage
-- ALTER COLUMN company_id SET NOT NULL;

-- Step 5: Add index for performance
CREATE INDEX IF NOT EXISTS idx_api_usage_company_id
ON api_usage(company_id);

-- Step 6: Enable Row Level Security
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

-- Step 7: Create RLS policy
DROP POLICY IF EXISTS "company_isolation_api_usage" ON api_usage;
CREATE POLICY "company_isolation_api_usage"
ON api_usage
FOR ALL
USING (company_id = (current_setting('app.company_id', true)::UUID));

-- Comments
COMMENT ON COLUMN api_usage.company_id IS 'Company that incurred this API usage - for billing and tracking';
