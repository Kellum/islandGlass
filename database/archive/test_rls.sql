-- ============================================================================
-- Island Glass Leads - Test RLS Policies
-- ============================================================================
--
-- PURPOSE: Verify that RLS is enabled and policies are working correctly
--
-- INSTRUCTIONS:
-- 1. Run enable_rls_policies.sql first
-- 2. Test your Streamlit app to make sure it works
-- 3. Open Supabase Dashboard > SQL Editor
-- 4. Copy and paste this entire file
-- 5. Click "Run" to execute
-- 6. Review the results to verify all tests pass
--
-- EXPECTED RESULTS: All queries should succeed and return data
-- ============================================================================

-- ============================================================================
-- TEST 1: Verify RLS is enabled on all tables
-- ============================================================================

SELECT
    schemaname,
    tablename,
    rowsecurity AS rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('contractors', 'outreach_materials', 'interaction_log', 'app_settings', 'api_usage')
ORDER BY tablename;

-- Expected: All tables should show rls_enabled = true

-- ============================================================================
-- TEST 2: Verify policies exist
-- ============================================================================

SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Expected: Should show 5 policies (one for each table)

-- ============================================================================
-- TEST 3: Test SELECT permissions on contractors
-- ============================================================================

SELECT
    'contractors' AS table_name,
    COUNT(*) AS row_count,
    'SELECT works ✅' AS status
FROM contractors;

-- Expected: Should return count of contractors without error

-- ============================================================================
-- TEST 4: Test SELECT permissions on outreach_materials
-- ============================================================================

SELECT
    'outreach_materials' AS table_name,
    COUNT(*) AS row_count,
    'SELECT works ✅' AS status
FROM outreach_materials;

-- Expected: Should return count without error

-- ============================================================================
-- TEST 5: Test SELECT permissions on interaction_log
-- ============================================================================

SELECT
    'interaction_log' AS table_name,
    COUNT(*) AS row_count,
    'SELECT works ✅' AS status
FROM interaction_log;

-- Expected: Should return count without error

-- ============================================================================
-- TEST 6: Test SELECT permissions on app_settings
-- ============================================================================

SELECT
    'app_settings' AS table_name,
    COUNT(*) AS row_count,
    'SELECT works ✅' AS status
FROM app_settings;

-- Expected: Should return count without error

-- ============================================================================
-- TEST 7: Test SELECT permissions on api_usage
-- ============================================================================

SELECT
    'api_usage' AS table_name,
    COUNT(*) AS row_count,
    'SELECT works ✅' AS status
FROM api_usage;

-- Expected: Should return count without error

-- ============================================================================
-- TEST 8: Test INSERT permission (contractors table)
-- ============================================================================

-- Insert a test record
INSERT INTO contractors (
    company_name,
    city,
    state,
    source,
    enrichment_status
) VALUES (
    'RLS Test Company',
    'Test City',
    'FL',
    'rls_test',
    'pending'
) RETURNING
    id,
    company_name,
    'INSERT works ✅' AS status;

-- Expected: Should successfully insert and return the new record

-- ============================================================================
-- TEST 9: Test UPDATE permission (contractors table)
-- ============================================================================

-- Update the test record we just created
UPDATE contractors
SET company_name = 'RLS Test Company (Updated)'
WHERE source = 'rls_test'
RETURNING
    id,
    company_name,
    'UPDATE works ✅' AS status;

-- Expected: Should successfully update and return the updated record

-- ============================================================================
-- TEST 10: Test DELETE permission (contractors table)
-- ============================================================================

-- Delete the test record
DELETE FROM contractors
WHERE source = 'rls_test'
RETURNING
    id,
    company_name,
    'DELETE works ✅' AS status;

-- Expected: Should successfully delete and return the deleted record

-- ============================================================================
-- TEST 11: Test INSERT on interaction_log (child table)
-- ============================================================================

-- First, get a real contractor ID to use
DO $$
DECLARE
    test_contractor_id INTEGER;
BEGIN
    -- Get the first contractor ID
    SELECT id INTO test_contractor_id FROM contractors LIMIT 1;

    -- Insert a test interaction
    IF test_contractor_id IS NOT NULL THEN
        INSERT INTO interaction_log (
            contractor_id,
            status,
            notes,
            user_name
        ) VALUES (
            test_contractor_id,
            'RLS Test',
            'This is a test interaction to verify RLS policies',
            'RLS Test User'
        );

        RAISE NOTICE '✅ INSERT on interaction_log works!';

        -- Clean up the test record
        DELETE FROM interaction_log
        WHERE status = 'RLS Test' AND user_name = 'RLS Test User';

        RAISE NOTICE '✅ DELETE on interaction_log works!';
    ELSE
        RAISE NOTICE '⚠️  No contractors found to test with';
    END IF;
END $$;

-- ============================================================================
-- TEST 12: Test app_settings (standalone table)
-- ============================================================================

-- Insert test setting
INSERT INTO app_settings (key, value)
VALUES ('rls_test_key', 'rls_test_value')
ON CONFLICT (key) DO UPDATE SET value = 'rls_test_value_updated'
RETURNING
    key,
    value,
    'INSERT/UPDATE on app_settings works ✅' AS status;

-- Clean up
DELETE FROM app_settings WHERE key = 'rls_test_key'
RETURNING
    key,
    'DELETE on app_settings works ✅' AS status;

-- ============================================================================
-- SUMMARY
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '✅ RLS POLICY TESTS COMPLETE';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'If all tests above succeeded, your RLS policies are working correctly!';
    RAISE NOTICE '';
    RAISE NOTICE '📋 What to verify:';
    RAISE NOTICE '   ✓ All tables show rls_enabled = true (Test 1)';
    RAISE NOTICE '   ✓ 5 policies exist (Test 2)';
    RAISE NOTICE '   ✓ All SELECT queries succeeded (Tests 3-7)';
    RAISE NOTICE '   ✓ INSERT, UPDATE, DELETE all worked (Tests 8-12)';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Next steps:';
    RAISE NOTICE '   1. Verify your Streamlit app works correctly';
    RAISE NOTICE '   2. Check Supabase security warnings are gone';
    RAISE NOTICE '   3. Monitor app for any issues';
    RAISE NOTICE '';
END $$;
