-- ============================================================================
-- Island Glass Leads - Rollback RLS Policies
-- ============================================================================
--
-- PURPOSE: Disable RLS and remove all policies (emergency rollback)
--
-- ⚠️  WARNING: Only run this if something breaks after enabling RLS!
--
-- WHAT THIS DOES:
-- - Drops all RLS policies created by enable_rls_policies.sql
-- - Disables Row Level Security on all tables
-- - Restores tables to their previous state (no RLS protection)
--
-- INSTRUCTIONS:
-- 1. Only run this if your app breaks after enabling RLS
-- 2. Open Supabase Dashboard > SQL Editor
-- 3. Copy and paste this entire file
-- 4. Click "Run" to execute
-- 5. Test your Streamlit app - it should work again
-- 6. Contact support or review error logs to debug the issue
--
-- NOTE: After rollback, security warnings will reappear in Supabase
-- ============================================================================

-- Start transaction to ensure all-or-nothing execution
BEGIN;

-- ============================================================================
-- Drop Policies (in reverse order of creation)
-- ============================================================================

-- Table 5: api_usage
DROP POLICY IF EXISTS "Allow all operations on api_usage" ON public.api_usage;

-- Table 4: app_settings
DROP POLICY IF EXISTS "Allow all operations on app_settings" ON public.app_settings;

-- Table 3: interaction_log
DROP POLICY IF EXISTS "Allow all operations on interaction_log" ON public.interaction_log;

-- Table 2: outreach_materials
DROP POLICY IF EXISTS "Allow all operations on outreach_materials" ON public.outreach_materials;

-- Table 1: contractors
DROP POLICY IF EXISTS "Allow all operations on contractors" ON public.contractors;

-- ============================================================================
-- Disable RLS on all tables
-- ============================================================================

ALTER TABLE public.api_usage DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.app_settings DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.interaction_log DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.outreach_materials DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.contractors DISABLE ROW LEVEL SECURITY;

-- ============================================================================
-- Commit transaction
-- ============================================================================
COMMIT;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '⚠️  RLS ROLLBACK COMPLETE';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    RAISE NOTICE '✅ All RLS policies have been removed';
    RAISE NOTICE '✅ RLS has been disabled on all tables';
    RAISE NOTICE '✅ Tables are back to their previous state';
    RAISE NOTICE '';
    RAISE NOTICE '📋 Next steps:';
    RAISE NOTICE '   1. Test your Streamlit app - it should work now';
    RAISE NOTICE '   2. Review error logs to understand what went wrong';
    RAISE NOTICE '   3. Security warnings will reappear in Supabase Dashboard';
    RAISE NOTICE '   4. Contact support if you need help debugging';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  IMPORTANT: Your database is no longer protected by RLS';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- Verify rollback was successful
-- ============================================================================

-- Check RLS status
SELECT
    tablename,
    rowsecurity AS rls_enabled,
    CASE
        WHEN rowsecurity = false THEN '✅ RLS disabled (rollback successful)'
        ELSE '❌ RLS still enabled'
    END AS status
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('contractors', 'outreach_materials', 'interaction_log', 'app_settings', 'api_usage')
ORDER BY tablename;

-- Check for remaining policies (should be empty)
SELECT
    tablename,
    COUNT(*) AS policy_count,
    CASE
        WHEN COUNT(*) = 0 THEN '✅ No policies remaining'
        ELSE '⚠️  Policies still exist'
    END AS status
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename IN ('contractors', 'outreach_materials', 'interaction_log', 'app_settings', 'api_usage')
GROUP BY tablename
ORDER BY tablename;
