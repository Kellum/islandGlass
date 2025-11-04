-- ============================================================================
-- Add missing columns to public.users table (simplified version)
-- ============================================================================

BEGIN;

-- Drop the constraint if it exists (in case it was partially created)
ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_role_check;

-- Add role column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'role'
    ) THEN
        ALTER TABLE public.users ADD COLUMN role TEXT DEFAULT 'team_member';
    END IF;
END $$;

-- Add is_active column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'is_active'
    ) THEN
        ALTER TABLE public.users ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;
END $$;

-- Add created_by column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'created_by'
    ) THEN
        ALTER TABLE public.users ADD COLUMN created_by UUID;
    END IF;
END $$;

-- Add last_login column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'last_login'
    ) THEN
        ALTER TABLE public.users ADD COLUMN last_login TIMESTAMPTZ;
    END IF;
END $$;

-- Now add the constraint
ALTER TABLE public.users
ADD CONSTRAINT users_role_check
CHECK (role IN ('owner', 'admin', 'team_member'));

-- Update all existing users to be owners and active
UPDATE public.users
SET
    role = COALESCE(role, 'owner'),
    is_active = COALESCE(is_active, true)
WHERE role IS NULL OR role = '' OR is_active IS NULL;

COMMIT;

-- ============================================================================
-- Verification - Show the public.users table
-- ============================================================================

SELECT * FROM public.users;
