-- =====================================================
-- Migration: 021_backfill_company_ids
-- Purpose: Backfill all company_id columns and set NOT NULL
-- Created: 2025-11-19
-- Part of: Multi-tenant SaaS implementation
-- IMPORTANT: Must run AFTER creating Island Glass company (migration 020)
-- =====================================================

-- Define the Island Glass company UUID
DO $$
DECLARE
    island_glass_uuid UUID := '720d425e-bb02-4612-9b35-70bded465dca';
    affected_rows INTEGER;
BEGIN
    -- Verify company exists
    IF NOT EXISTS (SELECT 1 FROM companies WHERE id = island_glass_uuid) THEN
        RAISE EXCEPTION 'Island Glass company not found. Run migration 020 first.';
    END IF;

    RAISE NOTICE 'Starting backfill with company ID: %', island_glass_uuid;

    -- Backfill contractors
    UPDATE contractors
    SET company_id = island_glass_uuid
    WHERE company_id IS NULL;
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RAISE NOTICE 'Updated % contractors', affected_rows;

    -- Backfill api_usage (from contractors if possible, otherwise direct)
    UPDATE api_usage au
    SET company_id = c.company_id
    FROM contractors c
    WHERE au.contractor_id = c.id
    AND au.company_id IS NULL;
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RAISE NOTICE 'Updated % api_usage records from contractors', affected_rows;

    -- Backfill remaining api_usage records
    UPDATE api_usage
    SET company_id = island_glass_uuid
    WHERE company_id IS NULL;
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RAISE NOTICE 'Updated % remaining api_usage records', affected_rows;

    -- Backfill interaction_log (from contractors)
    UPDATE interaction_log il
    SET company_id = c.company_id
    FROM contractors c
    WHERE il.contractor_id = c.id
    AND il.company_id IS NULL;
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RAISE NOTICE 'Updated % interaction_log records', affected_rows;

    -- Backfill remaining interaction_log records
    UPDATE interaction_log
    SET company_id = island_glass_uuid
    WHERE company_id IS NULL;
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RAISE NOTICE 'Updated % remaining interaction_log records', affected_rows;

    -- Backfill outreach_materials (from contractors)
    UPDATE outreach_materials om
    SET company_id = c.company_id
    FROM contractors c
    WHERE om.contractor_id = c.id
    AND om.company_id IS NULL;
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RAISE NOTICE 'Updated % outreach_materials records', affected_rows;

    -- Backfill remaining outreach_materials records
    UPDATE outreach_materials
    SET company_id = island_glass_uuid
    WHERE company_id IS NULL;
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RAISE NOTICE 'Updated % remaining outreach_materials records', affected_rows;

    RAISE NOTICE 'Backfill complete!';
END $$;

-- Now make all company_id columns NOT NULL

-- Contractors
ALTER TABLE contractors
ALTER COLUMN company_id SET NOT NULL;

-- API Usage
ALTER TABLE api_usage
ALTER COLUMN company_id SET NOT NULL;

-- Interaction Log
ALTER TABLE interaction_log
ALTER COLUMN company_id SET NOT NULL;

-- Outreach Materials
ALTER TABLE outreach_materials
ALTER COLUMN company_id SET NOT NULL;

-- Verify all tables have company_id set
DO $$
DECLARE
    null_count INTEGER;
BEGIN
    -- Check contractors
    SELECT COUNT(*) INTO null_count FROM contractors WHERE company_id IS NULL;
    IF null_count > 0 THEN
        RAISE EXCEPTION 'Found % contractors with NULL company_id', null_count;
    END IF;

    -- Check api_usage
    SELECT COUNT(*) INTO null_count FROM api_usage WHERE company_id IS NULL;
    IF null_count > 0 THEN
        RAISE EXCEPTION 'Found % api_usage records with NULL company_id', null_count;
    END IF;

    -- Check interaction_log
    SELECT COUNT(*) INTO null_count FROM interaction_log WHERE company_id IS NULL;
    IF null_count > 0 THEN
        RAISE EXCEPTION 'Found % interaction_log records with NULL company_id', null_count;
    END IF;

    -- Check outreach_materials
    SELECT COUNT(*) INTO null_count FROM outreach_materials WHERE company_id IS NULL;
    IF null_count > 0 THEN
        RAISE EXCEPTION 'Found % outreach_materials records with NULL company_id', null_count;
    END IF;

    RAISE NOTICE 'All company_id constraints verified successfully!';
END $$;
