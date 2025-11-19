-- =====================================================
-- Migration: 015_add_company_id_to_users
-- Purpose: Add company isolation to user accounts
-- Created: 2025-11-19
-- Part of: Multi-tenant SaaS implementation
-- =====================================================

-- Step 1: Add company_id column (nullable first, for safety)
ALTER TABLE users
ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id);

-- Step 2: Populate company_id from user_profiles for existing users
UPDATE users u
SET company_id = up.company_id
FROM user_profiles up
WHERE u.user_id = up.user_id
AND u.company_id IS NULL;

-- Step 3: Make company_id required for future inserts
ALTER TABLE users
ALTER COLUMN company_id SET NOT NULL;

-- Step 4: Update email uniqueness constraint
-- Old: email must be globally unique
-- New: email can be reused across different companies
ALTER TABLE users
DROP CONSTRAINT IF EXISTS users_email_key;

CREATE UNIQUE INDEX IF NOT EXISTS users_email_company_unique
ON users(email, company_id);

-- Step 5: Add index for performance
CREATE INDEX IF NOT EXISTS idx_users_company_id
ON users(company_id);

-- Step 6: Add updated_at trigger if not exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON COLUMN users.company_id IS 'Company this user belongs to - enables multi-tenant isolation';
