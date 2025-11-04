-- ============================================================
-- Find the Island Glass Company UUID
-- ============================================================

-- Show the actual company UUID that exists
SELECT
    id,
    name,
    created_at,
    'Copy this UUID and use it to replace a0000000-0000-0000-0000-000000000001 in PART2' as instructions
FROM companies
WHERE name = 'Island Glass & Mirror';

-- This will show you the REAL UUID
-- You need to:
-- 1. Copy the 'id' value from above
-- 2. Open setup_company_data_PART2.sql
-- 3. Find and Replace:
--    Find: a0000000-0000-0000-0000-000000000001
--    Replace: <the real UUID from above>
-- 4. Then run the PART2 script
