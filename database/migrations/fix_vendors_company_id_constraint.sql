-- Migration: Fix vendors table company_id foreign key constraint
-- Date: November 17, 2025
-- Description: Remove foreign key constraint on vendors.company_id
--              The company_id should be a TEXT field for tenant isolation,
--              not a foreign key to users table

-- Check if company_id column exists and what type it is
-- If it has a foreign key constraint, drop it

-- Drop the foreign key constraint if it exists
ALTER TABLE vendors DROP CONSTRAINT IF EXISTS vendors_company_id_fkey;

-- Ensure company_id is TEXT type (not INTEGER) and nullable
-- First, check if the column exists
DO $$
BEGIN
    -- Try to alter the column to TEXT if it exists and is wrong type
    BEGIN
        ALTER TABLE vendors ALTER COLUMN company_id TYPE TEXT;
    EXCEPTION
        WHEN undefined_column THEN
            -- Column doesn't exist, add it
            ALTER TABLE vendors ADD COLUMN IF NOT EXISTS company_id TEXT;
        WHEN OTHERS THEN
            -- Column exists but may have wrong type, try to convert
            RAISE NOTICE 'Column company_id exists, attempting type conversion';
    END;
END $$;

-- Make sure company_id is nullable (no NOT NULL constraint)
ALTER TABLE vendors ALTER COLUMN company_id DROP NOT NULL;

-- Add comment
COMMENT ON COLUMN vendors.company_id IS 'Tenant/company ID for multi-tenancy (no foreign key constraint - managed at application level)';
