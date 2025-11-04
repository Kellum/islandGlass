-- ============================================
-- Add User Roles and Departments
-- Window Manufacturing System - Phase 2
-- ============================================

-- Add department column to user_profiles if it doesn't exist
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

-- Ensure role column exists and has proper constraints
DO $$
BEGIN
    -- Check if role column has a constraint
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.constraint_column_usage
        WHERE table_name = 'user_profiles'
        AND column_name = 'role'
    ) THEN
        -- Add constraint if it doesn't exist
        ALTER TABLE user_profiles
        ADD CONSTRAINT user_profiles_role_check
        CHECK (role IN ('owner', 'ig_admin', 'ig_employee', 'ig_manufacturing_admin', 'sales'));
    END IF;
END $$;

-- Add constraint for department values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.constraint_column_usage
        WHERE table_name = 'user_profiles'
        AND column_name = 'department'
    ) THEN
        ALTER TABLE user_profiles
        ADD CONSTRAINT user_profiles_department_check
        CHECK (department IN ('sales', 'manufacturing', 'admin', 'general', NULL));
    END IF;
END $$;

-- Create index for faster role/department lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON user_profiles(role);
CREATE INDEX IF NOT EXISTS idx_user_profiles_department ON user_profiles(department);

-- Update existing users with sensible defaults if role is null
UPDATE user_profiles
SET role = 'ig_employee'
WHERE role IS NULL;

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

    -- IG Employees with manufacturing department can access order entry
    IF user_role = 'ig_employee' AND user_dept = 'manufacturing' THEN
        RETURN TRUE;
    END IF;

    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- Create helper function for management access
-- ============================================

CREATE OR REPLACE FUNCTION has_window_management_access(user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    user_role TEXT;
BEGIN
    SELECT role INTO user_role
    FROM user_profiles
    WHERE id = user_id;

    -- Only owners and manufacturing admins can manage orders
    RETURN user_role IN ('owner', 'ig_manufacturing_admin');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- Verification Query
-- ============================================

-- Check that everything was created successfully
DO $$
DECLARE
    dept_exists BOOLEAN;
    role_constraint_exists BOOLEAN;
BEGIN
    -- Check department column
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'department'
    ) INTO dept_exists;

    IF NOT dept_exists THEN
        RAISE EXCEPTION 'Department column was not created successfully';
    END IF;

    RAISE NOTICE '✓ User roles and departments configured successfully';
    RAISE NOTICE '✓ Helper functions created for permission checking';
    RAISE NOTICE '✓ Indexes created for performance';
END $$;

-- Display current user roles (for verification)
SELECT
    COUNT(*) as total_users,
    role,
    department,
    COUNT(*) as count_by_role
FROM user_profiles
WHERE deleted_at IS NULL
GROUP BY role, department
ORDER BY role, department;
