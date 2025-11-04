-- ============================================================================
-- Add role column to users table
-- ============================================================================
--
-- This adds the role column that was missing from the users table
-- and sets your existing user as an owner
--
-- INSTRUCTIONS:
-- 1. Run this in Supabase SQL Editor
-- 2. Your user will be set as owner
--
-- ============================================================================

BEGIN;

-- Add role column if it doesn't exist
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS role TEXT NOT NULL DEFAULT 'team_member';

-- Add constraint to ensure role is valid
ALTER TABLE public.users
ADD CONSTRAINT users_role_check
CHECK (role IN ('owner', 'admin', 'team_member'));

-- Add is_active column if it doesn't exist
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true;

-- Add created_by column if it doesn't exist
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES public.users(id);

-- Add last_login column if it doesn't exist
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ;

-- Update all existing users to be owners (you can change this later)
UPDATE public.users
SET role = 'owner', is_active = true
WHERE role IS NULL OR role = '';

COMMIT;

-- ============================================================================
-- Verification
-- ============================================================================

-- Check the users table structure
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'users'
ORDER BY ordinal_position;

-- Show all users with their roles
SELECT id, email, full_name, role, is_active, created_at, last_login
FROM public.users
ORDER BY created_at;
