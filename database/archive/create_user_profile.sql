-- ============================================================================
-- Create user profile in public.users for existing auth user
-- ============================================================================
--
-- This creates a profile in public.users that matches your auth.users record
-- The ID must match between auth.users and public.users
--
-- ============================================================================

-- First, let's see your auth user ID and email
SELECT id, email, created_at
FROM auth.users
ORDER BY created_at DESC
LIMIT 5;

-- Now create the matching profile in public.users
-- Replace 'YOUR_NAME_HERE' with your actual name
INSERT INTO public.users (id, email, full_name, role, is_active, created_at)
SELECT
    id,
    email,
    'Ryan Kellum' as full_name,  -- CHANGE THIS to your actual name
    'owner' as role,
    true as is_active,
    created_at
FROM auth.users
WHERE email = 'ry@islandglassandmirror.com'  -- CHANGE THIS to your actual email
ON CONFLICT (id) DO UPDATE SET
    role = 'owner',
    is_active = true,
    full_name = EXCLUDED.full_name;

-- Verify the profile was created
SELECT id, email, full_name, role, is_active, created_at
FROM public.users;
