-- ============================================
-- Add User Roles and Departments (FIXED VERSION)
-- Window Manufacturing System - Phase 2
-- Handles existing data gracefully
-- ============================================

-- First, let's see what roles currently exist
DO $$
DECLARE
    existing_roles TEXT[];
BEGIN
    -- Get unique existing roles
    SELECT ARRAY_AGG(DISTINCT role) INTO existing_roles
    FROM user_profiles
    WHERE role IS NOT NULL;

    RAISE NOTICE 'Existing roles in database: %', existing_roles;
END $$;

-- Add department column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles'
        AND column_name = 'department'
    ) THEN
        ALTER TABLE user_profiles
        ADD COLUMN department TEXT;

        COMMENT ON COLUMN user_profiles.department IS 'User department for additional access control granularity';
    END IF;
END $$;

-- Map old role values to new role values
UPDATE user_profiles
SET role = CASE
    WHEN role = 'admin' THEN 'ig_admin'
    WHEN role = 'manager' THEN 'ig_manufacturing_admin'
    WHEN role = 'employee' THEN 'ig_employee'
    WHEN role = 'production' THEN 'ig_manufacturing_admin'
    WHEN role IN ('owner', 'ig_admin', 'ig_employee', 'ig_manufacturing_admin', 'sales') THEN role
    ELSE 'ig_employee'  -- Default for unknown roles
END
WHERE role IS NOT NULL;

-- Set default role for null values
UPDATE user_profiles
SET role = 'ig_employee'
WHERE role IS NULL;

-- Now add constraint (after data is cleaned)
DO $$
BEGIN
    -- Drop old constraint if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'user_profiles'
        AND constraint_name = 'user_profiles_role_check'
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT user_profiles_role_check;
    END IF;

    -- Add new constraint
    ALTER TABLE user_profiles
    ADD CONSTRAINT user_profiles_role_check
    CHECK (role IN ('owner', 'ig_admin', 'ig_employee', 'ig_manufacturing_admin', 'sales'));
END $$;

-- Add constraint for department values
DO $$
BEGIN
    -- Drop old constraint if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'user_profiles'
        AND constraint_name = 'user_profiles_department_check'
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT user_profiles_department_check;
    END IF;

    -- Add new constraint
    ALTER TABLE user_profiles
    ADD CONSTRAINT user_profiles_department_check
    CHECK (department IN ('sales', 'manufacturing', 'admin', 'general', NULL));
END $$;

-- Set default departments based on roles
UPDATE user_profiles
SET department = CASE
    WHEN role = 'ig_manufacturing_admin' THEN 'manufacturing'
    WHEN role = 'sales' THEN 'sales'
    WHEN role IN ('owner', 'ig_admin') THEN 'admin'
    ELSE 'general'
END
WHERE department IS NULL;

-- Create indexes for faster role/department lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON user_profiles(role);
CREATE INDEX IF NOT EXISTS idx_user_profiles_department ON user_profiles(department);

-- ============================================
-- Create helper function to check permissions
-- ============================================

CREATE OR REPLACE FUNCTION has_window_manufacturing_access(user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    user_role TEXT;
    user_dept TEXT;
BEGIN
    SELECT role, department INTO user_role, user_dept
    FROM user_profiles
    WHERE id = user_id;

    -- Owners have access to everything
    IF user_role = 'owner' THEN
        RETURN TRUE;
    END IF;

    -- IG Manufacturing Admin has full window access
    IF user_role = 'ig_manufacturing_admin' THEN
        RETURN TRUE;
    END IF;

    -- IG Admin has full access
    IF user_role = 'ig_admin' THEN
        RETURN TRUE;
    END IF;

    -- Manufacturing department employees have access
    IF user_dept = 'manufacturing' THEN
        RETURN TRUE;
    END IF;

    -- Otherwise no access
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- Verify the migration
-- ============================================

-- Show updated roles and departments
SELECT
    id,
    role,
    department,
    created_at
FROM user_profiles
ORDER BY created_at DESC
LIMIT 10;

-- Show role distribution
SELECT
    role,
    COUNT(*) as user_count
FROM user_profiles
GROUP BY role
ORDER BY user_count DESC;

-- Show department distribution
SELECT
    department,
    COUNT(*) as user_count
FROM user_profiles
GROUP BY department
ORDER BY user_count DESC;
