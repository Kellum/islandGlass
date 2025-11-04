-- ============================================================================
-- Fix: Infinite Recursion in Users Table RLS Policy
-- ============================================================================
--
-- PROBLEM: The "Only owners can manage users" policy queries the users table
-- from within its own RLS policy, causing infinite recursion.
--
-- SOLUTION: Use a security definer function that bypasses RLS to check role.
--
-- INSTRUCTIONS:
-- 1. Run this in Supabase SQL Editor
-- 2. This will fix the login error
--
-- ============================================================================

BEGIN;

-- Drop the problematic policy
DROP POLICY IF EXISTS "Only owners can manage users" ON public.users;

-- Create a security definer function that bypasses RLS
CREATE OR REPLACE FUNCTION public.is_owner(user_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.users
        WHERE id = user_id
        AND role = 'owner'
        AND is_active = true
    );
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.is_owner(UUID) TO authenticated;

-- Recreate the policy using the security definer function
CREATE POLICY "Only owners can manage users"
ON public.users
FOR ALL
USING (public.is_owner(auth.uid()));

-- Also add a WITH CHECK clause for inserts/updates
CREATE POLICY "Only owners can insert users"
ON public.users
FOR INSERT
WITH CHECK (public.is_owner(auth.uid()));

CREATE POLICY "Only owners can update users"
ON public.users
FOR UPDATE
USING (public.is_owner(auth.uid()));

CREATE POLICY "Only owners can delete users"
ON public.users
FOR DELETE
USING (public.is_owner(auth.uid()));

COMMIT;

-- ============================================================================
-- Verification
-- ============================================================================

-- Check that policies are created
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename = 'users'
ORDER BY policyname;
