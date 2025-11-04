-- ============================================================
-- PART 1: Get Your User ID
-- ============================================================
-- Run this query FIRST to find your user_id
-- Copy the user_id from the results and use it in PART 2
-- ============================================================

SELECT
    id as user_id,
    email,
    created_at,
    '👆 Copy the user_id above and use it in PART 2' as instructions
FROM auth.users
ORDER BY created_at DESC
LIMIT 5;

-- ============================================================
-- After running this, you should see your user account(s)
-- Copy the UUID from the user_id column
-- Then open setup_company_data_PART2.sql and replace YOUR_USER_ID_HERE
-- ============================================================
