-- ============================================================================
-- Island Glass Leads - Enable Row Level Security (RLS) and Create Policies
-- ============================================================================
--
-- PURPOSE: Fix Supabase security warnings by enabling RLS on all public tables
--
-- SECURITY MODEL: Public access (no authentication required)
-- - Uses anon key with permissive policies
-- - Allows all operations (SELECT, INSERT, UPDATE, DELETE) for now
-- - Foundation for adding user authentication in the future
--
-- INSTRUCTIONS:
-- 1. Open Supabase Dashboard > SQL Editor
-- 2. Copy and paste this entire file
-- 3. Click "Run" to execute
-- 4. Verify no errors appear
-- 5. Test your Streamlit app to ensure it still works
--
-- ROLLBACK: If anything breaks, run rollback_rls.sql
-- ============================================================================

-- Start transaction to ensure all-or-nothing execution
BEGIN;

-- ============================================================================
-- TABLE 1: contractors
-- Purpose: Core contractor data (company info, lead scores, contact details)
-- Access: Full CRUD operations needed by the app
-- ============================================================================

-- Enable RLS on contractors table
ALTER TABLE public.contractors ENABLE ROW LEVEL SECURITY;

-- Create policy: Allow all operations
CREATE POLICY "Allow all operations on contractors"
ON public.contractors
FOR ALL
USING (true)
WITH CHECK (true);

COMMENT ON POLICY "Allow all operations on contractors" ON public.contractors IS
'Permissive policy allowing full access. Replace with auth-based policies when adding user authentication.';


-- ============================================================================
-- TABLE 2: outreach_materials
-- Purpose: Email templates and call scripts generated for contractors
-- Access: Full CRUD operations needed by the app
-- Relationship: Child of contractors (CASCADE delete)
-- ============================================================================

-- Enable RLS on outreach_materials table
ALTER TABLE public.outreach_materials ENABLE ROW LEVEL SECURITY;

-- Create policy: Allow all operations
CREATE POLICY "Allow all operations on outreach_materials"
ON public.outreach_materials
FOR ALL
USING (true)
WITH CHECK (true);

COMMENT ON POLICY "Allow all operations on outreach_materials" ON public.outreach_materials IS
'Permissive policy allowing full access. Replace with auth-based policies when adding user authentication.';


-- ============================================================================
-- TABLE 3: interaction_log
-- Purpose: Track sales activities and interactions with contractors
-- Access: Full CRUD operations needed by the app
-- Relationship: Child of contractors (CASCADE delete)
-- ============================================================================

-- Enable RLS on interaction_log table
ALTER TABLE public.interaction_log ENABLE ROW LEVEL SECURITY;

-- Create policy: Allow all operations
CREATE POLICY "Allow all operations on interaction_log"
ON public.interaction_log
FOR ALL
USING (true)
WITH CHECK (true);

COMMENT ON POLICY "Allow all operations on interaction_log" ON public.interaction_log IS
'Permissive policy allowing full access. Replace with auth-based policies when adding user authentication.';


-- ============================================================================
-- TABLE 4: app_settings
-- Purpose: Key-value configuration storage for application settings
-- Access: Full CRUD operations needed by the app
-- Relationship: Standalone table
-- ============================================================================

-- Enable RLS on app_settings table
ALTER TABLE public.app_settings ENABLE ROW LEVEL SECURITY;

-- Create policy: Allow all operations
CREATE POLICY "Allow all operations on app_settings"
ON public.app_settings
FOR ALL
USING (true)
WITH CHECK (true);

COMMENT ON POLICY "Allow all operations on app_settings" ON public.app_settings IS
'Permissive policy allowing full access. Replace with auth-based policies when adding user authentication.';


-- ============================================================================
-- TABLE 5: api_usage
-- Purpose: Track Claude API token usage and costs
-- Access: Full CRUD operations needed by the app
-- Relationship: Soft link to contractors (SET NULL on delete)
-- ============================================================================

-- Enable RLS on api_usage table
ALTER TABLE public.api_usage ENABLE ROW LEVEL SECURITY;

-- Create policy: Allow all operations
CREATE POLICY "Allow all operations on api_usage"
ON public.api_usage
FOR ALL
USING (true)
WITH CHECK (true);

COMMENT ON POLICY "Allow all operations on api_usage" ON public.api_usage IS
'Permissive policy allowing full access. Replace with auth-based policies when adding user authentication.';


-- ============================================================================
-- Commit transaction
-- ============================================================================
COMMIT;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '✅ RLS enabled and policies created successfully for all 5 tables!';
    RAISE NOTICE '📋 Next steps:';
    RAISE NOTICE '   1. Test your Streamlit app to ensure it still works';
    RAISE NOTICE '   2. Run test_rls.sql to verify policies are working';
    RAISE NOTICE '   3. Check Supabase Dashboard > Database > Tables to see RLS status';
    RAISE NOTICE '';
    RAISE NOTICE '🔐 Security Status:';
    RAISE NOTICE '   - All tables now have RLS enabled';
    RAISE NOTICE '   - Using anon key with permissive policies';
    RAISE NOTICE '   - Ready to add authentication in the future';
END $$;
