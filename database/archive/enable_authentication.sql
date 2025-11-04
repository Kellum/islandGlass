-- ============================================================================
-- Island Glass Leads - Enable Authentication System
-- ============================================================================
--
-- PURPOSE: Add user authentication with role-based access control
--
-- ROLES:
-- - owner: Full access including user management
-- - admin: Full CRM access except user management
-- - team_member: Full CRM access (same as admin in permissive model)
--
-- INSTRUCTIONS:
-- 1. Open Supabase Dashboard > SQL Editor
-- 2. Copy and paste this entire file
-- 3. Click "Run" to execute
-- 4. Create first owner user manually in Supabase Auth dashboard
-- 5. Then insert corresponding record in users table
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- TABLE: users (User profiles linked to Supabase Auth)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'team_member')),
    created_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON public.users(is_active);

-- Enable RLS on users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Policy: Authenticated users can view all users
CREATE POLICY "Authenticated users can view users"
ON public.users
FOR SELECT
USING (auth.uid() IS NOT NULL);

-- Policy: Only owners can manage users (insert, update, delete)
CREATE POLICY "Only owners can manage users"
ON public.users
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM public.users
        WHERE id = auth.uid() AND role = 'owner' AND is_active = true
    )
);

COMMENT ON TABLE public.users IS
'User profiles linked to Supabase Auth. Owners can manage users, all authenticated users can use CRM.';


-- ============================================================================
-- Add audit columns to existing tables
-- ============================================================================

-- Add created_by and updated_by to contractors
ALTER TABLE public.contractors
ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES auth.users(id),
ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES auth.users(id);

-- Add created_by to outreach_materials
ALTER TABLE public.outreach_materials
ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES auth.users(id);

-- Add created_by to interaction_log (rename user_name to preserve existing data)
ALTER TABLE public.interaction_log
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- Keep user_name as fallback for historical data


-- ============================================================================
-- Update RLS policies to require authentication
-- ============================================================================

-- Drop existing permissive policies
DROP POLICY IF EXISTS "Allow all operations on contractors" ON public.contractors;
DROP POLICY IF EXISTS "Allow all operations on outreach_materials" ON public.outreach_materials;
DROP POLICY IF EXISTS "Allow all operations on interaction_log" ON public.interaction_log;
DROP POLICY IF EXISTS "Allow all operations on app_settings" ON public.app_settings;
DROP POLICY IF EXISTS "Allow all operations on api_usage" ON public.api_usage;

-- Contractors: All authenticated users can perform all operations
CREATE POLICY "Authenticated users can manage contractors"
ON public.contractors
FOR ALL
USING (auth.uid() IS NOT NULL)
WITH CHECK (auth.uid() IS NOT NULL);

-- Outreach materials: All authenticated users can perform all operations
CREATE POLICY "Authenticated users can manage outreach materials"
ON public.outreach_materials
FOR ALL
USING (auth.uid() IS NOT NULL)
WITH CHECK (auth.uid() IS NOT NULL);

-- Interaction log: All authenticated users can perform all operations
CREATE POLICY "Authenticated users can manage interactions"
ON public.interaction_log
FOR ALL
USING (auth.uid() IS NOT NULL)
WITH CHECK (auth.uid() IS NOT NULL);

-- App settings: All authenticated users can manage settings
CREATE POLICY "Authenticated users can manage app settings"
ON public.app_settings
FOR ALL
USING (auth.uid() IS NOT NULL)
WITH CHECK (auth.uid() IS NOT NULL);

-- API usage: All authenticated users can view and insert usage records
CREATE POLICY "Authenticated users can manage API usage"
ON public.api_usage
FOR ALL
USING (auth.uid() IS NOT NULL)
WITH CHECK (auth.uid() IS NOT NULL);


-- ============================================================================
-- Helper function to get current user role
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_user_role()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    user_role TEXT;
BEGIN
    SELECT role INTO user_role
    FROM public.users
    WHERE id = auth.uid() AND is_active = true;

    RETURN user_role;
END;
$$;

COMMENT ON FUNCTION public.get_user_role() IS
'Returns the role of the currently authenticated user. Returns NULL if user not found or inactive.';


-- ============================================================================
-- Function to update last_login timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION public.update_last_login()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE public.users
    SET last_login = NOW()
    WHERE id = auth.uid();

    RETURN NEW;
END;
$$;

-- Note: This trigger would need to be called from the application layer
-- Supabase Auth doesn't provide a built-in way to trigger on login


-- ============================================================================
-- Commit transaction
-- ============================================================================
COMMIT;

-- ============================================================================
-- SUCCESS MESSAGE & NEXT STEPS
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ Authentication system database setup complete!';
    RAISE NOTICE '';
    RAISE NOTICE '📋 Next steps:';
    RAISE NOTICE '   1. Create your first owner user:';
    RAISE NOTICE '      a) Go to Supabase Dashboard > Authentication > Users';
    RAISE NOTICE '      b) Click "Add user" → Email & password';
    RAISE NOTICE '      c) Copy the user UUID from the users list';
    RAISE NOTICE '      d) Run this SQL (replace UUID and details):';
    RAISE NOTICE '';
    RAISE NOTICE '      INSERT INTO public.users (id, email, full_name, role, is_active)';
    RAISE NOTICE '      VALUES (';
    RAISE NOTICE '        ''paste-user-uuid-here'',';
    RAISE NOTICE '        ''owner@islandglass.com'',';
    RAISE NOTICE '        ''Owner Name'',';
    RAISE NOTICE '        ''owner'',';
    RAISE NOTICE '        true';
    RAISE NOTICE '      );';
    RAISE NOTICE '';
    RAISE NOTICE '   2. Test authentication in your Dash app';
    RAISE NOTICE '   3. Additional users can be created via Settings page';
    RAISE NOTICE '';
    RAISE NOTICE '🔐 Security Status:';
    RAISE NOTICE '   - All tables now require authentication';
    RAISE NOTICE '   - User management restricted to owners';
    RAISE NOTICE '   - Audit columns added for tracking changes';
    RAISE NOTICE '   - Ready for production use';
    RAISE NOTICE '';
END $$;


-- ============================================================================
-- Example: Insert first owner user (after creating in Supabase Auth)
-- ============================================================================

-- IMPORTANT: Replace the UUID with the actual UUID from Supabase Auth dashboard
-- Uncomment and run after creating the user in Auth:

/*
INSERT INTO public.users (id, email, full_name, role, is_active)
VALUES (
    '00000000-0000-0000-0000-000000000000',  -- Replace with actual UUID from Auth
    'ryan@islandglass.com',  -- Replace with actual email
    'Ryan Kellum',  -- Replace with actual name
    'owner',
    true
);
*/
