-- Migration: Fix vendor_contacts RLS issue
-- Date: November 17, 2025
-- Description: Disable RLS on vendor_contacts to match vendors table pattern
--              The Python backend doesn't set current_setting('app.current_company_id'),
--              so company isolation is handled at the application level via company_id column

-- Drop the existing RLS policy
DROP POLICY IF EXISTS vendor_contacts_company_isolation ON vendor_contacts;

-- Disable RLS on vendor_contacts table
ALTER TABLE vendor_contacts DISABLE ROW LEVEL SECURITY;

-- Add comment explaining the change
COMMENT ON TABLE vendor_contacts IS 'Multiple contacts per vendor (company isolation handled at application level via company_id column)';
