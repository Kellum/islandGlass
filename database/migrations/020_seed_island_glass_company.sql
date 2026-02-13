-- =====================================================
-- Migration: 020_seed_island_glass_company
-- Purpose: Create Island Glass & Mirror company record
-- Created: 2025-11-19
-- Part of: Multi-tenant SaaS implementation
-- =====================================================

-- Create Island Glass & Mirror company
-- This is the foundational company record that all existing data will reference

INSERT INTO companies (
    id,
    company_name,
    slug,
    primary_contact_name,
    primary_contact_email,
    primary_contact_phone,
    city,
    state,
    country,
    plan_tier,
    status,
    trial_ends_at,
    created_at
) VALUES (
    '720d425e-bb02-4612-9b35-70bded465dca',  -- Fixed UUID for reference
    'Island Glass & Mirror',
    'island-glass',
    'Ryan Kellum',
    'ryan@islandglass.com',  -- TODO: Update with actual email
    '(904) XXX-XXXX',        -- TODO: Update with actual phone
    'Jacksonville',
    'FL',
    'USA',
    'enterprise',             -- Full access for founder
    'active',
    NULL,                     -- No trial - direct to enterprise
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Verify the company was created
DO $$
DECLARE
    company_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO company_count
    FROM companies
    WHERE id = '720d425e-bb02-4612-9b35-70bded465dca';

    IF company_count = 0 THEN
        RAISE EXCEPTION 'Failed to create Island Glass company record';
    ELSE
        RAISE NOTICE 'Island Glass company created successfully with ID: 720d425e-bb02-4612-9b35-70bded465dca';
    END IF;
END $$;

-- Export the company ID for use in subsequent migrations
-- This can be referenced as: '720d425e-bb02-4612-9b35-70bded465dca'
