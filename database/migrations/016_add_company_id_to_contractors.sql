-- =====================================================
-- Migration: 016_add_company_id_to_contractors
-- Purpose: Add multi-tenant isolation to contractor leads
-- Created: 2025-11-19
-- Part of: Multi-tenant SaaS implementation
-- =====================================================

-- Step 1: Add company_id column (nullable first)
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id);

-- Step 2: Backfill existing data with Island Glass company
-- NOTE: This will be updated after creating the company record
-- For now, we'll leave it NULL and require manual assignment
-- UPDATE contractors
-- SET company_id = 'YOUR-COMPANY-UUID-HERE'
-- WHERE company_id IS NULL;

-- Step 3: Make it required (commented out until after backfill)
-- ALTER TABLE contractors
-- ALTER COLUMN company_id SET NOT NULL;

-- Step 4: Add index for performance
CREATE INDEX IF NOT EXISTS idx_contractors_company_id
ON contractors(company_id);

-- Step 5: Enable Row Level Security
ALTER TABLE contractors ENABLE ROW LEVEL SECURITY;

-- Step 6: Create RLS policy
DROP POLICY IF EXISTS "company_isolation_contractors" ON contractors;
CREATE POLICY "company_isolation_contractors"
ON contractors
FOR ALL
USING (company_id = (current_setting('app.company_id', true)::UUID));

-- Step 7: Add updated_at trigger if not exists
DROP TRIGGER IF EXISTS update_contractors_updated_at ON contractors;
CREATE TRIGGER update_contractors_updated_at
    BEFORE UPDATE ON contractors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON COLUMN contractors.company_id IS 'Company that owns this contractor lead - required for multi-tenancy';

-- NOTE: After running this migration, you must:
-- 1. Create your company record (migration 017 or manual insert)
-- 2. Update contractors: UPDATE contractors SET company_id = 'your-uuid' WHERE company_id IS NULL;
-- 3. Then run: ALTER TABLE contractors ALTER COLUMN company_id SET NOT NULL;
