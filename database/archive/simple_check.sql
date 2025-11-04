-- Simple diagnostic - check if companies table exists

-- Test 1: Does companies table exist?
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'companies'
) as companies_table_exists;

-- Test 2: If it exists, what's in it?
SELECT * FROM companies;

-- Test 3: Check user_profiles structure
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'user_profiles'
AND column_name IN ('user_id', 'company_id')
ORDER BY column_name;
