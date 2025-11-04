-- ============================================================
-- Create Island Glass & Mirror Company Record
-- Run this if the companies table exists but is empty
-- ============================================================

-- Insert the Island Glass company with the fixed UUID
INSERT INTO companies (id, name, created_at, updated_at)
VALUES (
    'a0000000-0000-0000-0000-000000000001'::UUID,
    'Island Glass & Mirror',
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Verify it was created
SELECT
    id,
    name,
    created_at,
    '✅ Company created successfully!' as status
FROM companies
WHERE id = 'a0000000-0000-0000-0000-000000000001'::UUID;
