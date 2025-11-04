-- ============================================================
-- Check Migration Status
-- Run this to see if the migration has been completed
-- ============================================================

-- Check if companies table exists
SELECT
    'companies table' as check_name,
    CASE
        WHEN EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'companies'
        ) THEN '✅ EXISTS'
        ELSE '❌ MISSING - Need to run complete_company_migration.sql'
    END as status;

-- Check if user_profiles has company_id column
SELECT
    'user_profiles.company_id column' as check_name,
    CASE
        WHEN EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'user_profiles'
            AND column_name = 'company_id'
        ) THEN '✅ EXISTS'
        ELSE '❌ MISSING - Need to run complete_company_migration.sql'
    END as status;

-- Check if glass_config has company_id column
SELECT
    'glass_config.company_id column' as check_name,
    CASE
        WHEN EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'glass_config'
            AND column_name = 'company_id'
        ) THEN '✅ EXISTS'
        ELSE '❌ MISSING - Need to run complete_company_migration.sql'
    END as status;

-- Check if Island Glass company exists
SELECT
    'Island Glass & Mirror company' as check_name,
    CASE
        WHEN EXISTS (
            SELECT FROM companies WHERE name = 'Island Glass & Mirror'
        ) THEN '✅ EXISTS'
        ELSE '❌ MISSING - Need to run complete_company_migration.sql'
    END as status;

-- If all checks pass, show company info
SELECT
    '=' as separator,
    'Company Info (if exists)' as section;

SELECT
    id,
    name,
    created_at
FROM companies
WHERE name = 'Island Glass & Mirror';
