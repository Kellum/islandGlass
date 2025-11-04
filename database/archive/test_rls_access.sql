-- ============================================================
-- Test RLS Access - Run this while logged into the app
-- ============================================================

-- Test 1: Check user_profiles linking
SELECT
    'Your user profile' as test,
    user_id,
    company_id,
    full_name,
    role
FROM user_profiles
WHERE user_id = auth.uid();

-- Test 2: Check company exists
SELECT
    'Your company' as test,
    c.id as company_id,
    c.name as company_name
FROM companies c
JOIN user_profiles up ON up.company_id = c.id
WHERE up.user_id = auth.uid();

-- Test 3: Try to read glass_config (should work if RLS is configured correctly)
SELECT
    'Glass configs visible to you' as test,
    COUNT(*) as count
FROM glass_config
WHERE deleted_at IS NULL;

-- Test 4: Check your actual glass configs
SELECT
    thickness,
    type,
    base_price,
    company_id
FROM glass_config
WHERE deleted_at IS NULL
ORDER BY thickness, type
LIMIT 5;
