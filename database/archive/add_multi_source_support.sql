-- Database Migration: Add Multi-Source Discovery Support
-- Purpose: Track contractors from multiple data sources (Google, Houzz, Yelp, etc.)
-- Created: October 27, 2025
-- Prerequisites: Run after Crawl4AI integration is complete

-- ==============================================================================
-- COLUMN ADDITIONS
-- ==============================================================================

-- Track which sources provided data for this contractor
-- Example: ['google_places', 'houzz', 'yelp']
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS sources TEXT[] DEFAULT '{}';

-- Store raw data from each source in JSON format (for debugging/auditing)
-- Example: {'google': {...}, 'houzz': {...}}
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS source_data JSONB DEFAULT '{}';

-- Track when contractor was first discovered
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS discovery_date TIMESTAMP DEFAULT NOW();

-- Track when data was last verified/updated from any source
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS last_verified TIMESTAMP;

-- ==============================================================================
-- INDEXES
-- ==============================================================================

-- GIN index for faster queries on sources array
-- Enables fast lookups like: WHERE 'houzz' = ANY(sources)
CREATE INDEX IF NOT EXISTS idx_contractors_sources
ON contractors USING GIN(sources);

-- Index for discovery date queries (recent contractors, etc.)
CREATE INDEX IF NOT EXISTS idx_contractors_discovery_date
ON contractors(discovery_date DESC);

-- Index for last_verified (find stale data)
CREATE INDEX IF NOT EXISTS idx_contractors_last_verified
ON contractors(last_verified DESC NULLS LAST);

-- ==============================================================================
-- COMMENTS (Documentation)
-- ==============================================================================

COMMENT ON COLUMN contractors.sources IS
'Array of data sources that provided data for this contractor: google_places, houzz, yelp, homeadvisor, thumbtack, bbb, csv_import, manual_entry';

COMMENT ON COLUMN contractors.source_data IS
'Raw data from each source in JSON format for debugging and data validation. Structure: {"google": {...}, "houzz": {...}}';

COMMENT ON COLUMN contractors.discovery_date IS
'Timestamp when contractor was first added to database from any source';

COMMENT ON COLUMN contractors.last_verified IS
'Timestamp when contractor data was last updated or verified from any source';

-- ==============================================================================
-- HELPER FUNCTIONS
-- ==============================================================================

-- Function to update last_verified when contractor is modified
CREATE OR REPLACE FUNCTION update_last_verified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_verified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update last_verified on UPDATE
DROP TRIGGER IF EXISTS contractors_update_verified ON contractors;
CREATE TRIGGER contractors_update_verified
    BEFORE UPDATE ON contractors
    FOR EACH ROW
    EXECUTE FUNCTION update_last_verified();

-- ==============================================================================
-- DATA MIGRATION
-- ==============================================================================

-- Update existing contractors to have default source values
-- Contractors from Google Places API
UPDATE contractors
SET sources = ARRAY['google_places']
WHERE source = 'google_places'
  AND (sources IS NULL OR sources = '{}');

-- Contractors from manual entry
UPDATE contractors
SET sources = ARRAY['manual_entry']
WHERE source = 'manual'
  AND (sources IS NULL OR sources = '{}');

-- Contractors from CSV import
UPDATE contractors
SET sources = ARRAY['csv_import']
WHERE source = 'csv_import'
  AND (sources IS NULL OR sources = '{}');

-- Set discovery_date to created_at for existing contractors
UPDATE contractors
SET discovery_date = date_added
WHERE discovery_date IS NULL
  AND date_added IS NOT NULL;

-- ==============================================================================
-- VALIDATION
-- ==============================================================================

-- Verify migration completed successfully
DO $$
DECLARE
    total_contractors INTEGER;
    contractors_with_sources INTEGER;
    contractors_with_discovery_date INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_contractors FROM contractors;
    SELECT COUNT(*) INTO contractors_with_sources FROM contractors WHERE sources IS NOT NULL AND sources != '{}';
    SELECT COUNT(*) INTO contractors_with_discovery_date FROM contractors WHERE discovery_date IS NOT NULL;

    RAISE NOTICE '=== Multi-Source Support Migration Results ===';
    RAISE NOTICE 'Total contractors: %', total_contractors;
    RAISE NOTICE 'Contractors with sources: %', contractors_with_sources;
    RAISE NOTICE 'Contractors with discovery_date: %', contractors_with_discovery_date;

    IF contractors_with_sources < total_contractors THEN
        RAISE WARNING 'Some contractors missing source data. Check source column values.';
    END IF;

    IF contractors_with_discovery_date < total_contractors THEN
        RAISE WARNING 'Some contractors missing discovery_date. Check date_added column.';
    END IF;

    RAISE NOTICE '===========================================';
END $$;

-- ==============================================================================
-- USAGE EXAMPLES
-- ==============================================================================

-- Example 1: Find contractors from multiple sources (cross-referenced)
-- SELECT company_name, sources, google_rating
-- FROM contractors
-- WHERE array_length(sources, 1) > 1
-- ORDER BY array_length(sources, 1) DESC;

-- Example 2: Find contractors only from Houzz
-- SELECT company_name, website, sources
-- FROM contractors
-- WHERE 'houzz' = ANY(sources);

-- Example 3: Find recently discovered contractors
-- SELECT company_name, sources, discovery_date
-- FROM contractors
-- WHERE discovery_date > NOW() - INTERVAL '7 days'
-- ORDER BY discovery_date DESC;

-- Example 4: Find contractors with stale data (>30 days old)
-- SELECT company_name, sources, last_verified
-- FROM contractors
-- WHERE last_verified < NOW() - INTERVAL '30 days'
--    OR last_verified IS NULL;

-- Example 5: Count contractors by source
-- SELECT unnest(sources) AS source, COUNT(*) AS count
-- FROM contractors
-- GROUP BY source
-- ORDER BY count DESC;

-- ==============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ==============================================================================

-- Uncomment and run if you need to rollback this migration:

-- DROP TRIGGER IF EXISTS contractors_update_verified ON contractors;
-- DROP FUNCTION IF EXISTS update_last_verified();
-- DROP INDEX IF EXISTS idx_contractors_sources;
-- DROP INDEX IF EXISTS idx_contractors_discovery_date;
-- DROP INDEX IF EXISTS idx_contractors_last_verified;
-- ALTER TABLE contractors DROP COLUMN IF EXISTS sources;
-- ALTER TABLE contractors DROP COLUMN IF EXISTS source_data;
-- ALTER TABLE contractors DROP COLUMN IF EXISTS discovery_date;
-- ALTER TABLE contractors DROP COLUMN IF EXISTS last_verified;

-- ==============================================================================
-- MIGRATION COMPLETE
-- ==============================================================================

RAISE NOTICE 'Multi-source support migration completed successfully!';
RAISE NOTICE 'Next steps:';
RAISE NOTICE '1. Upgrade Python to 3.10+';
RAISE NOTICE '2. Install Crawl4AI (pip install crawl4ai beautifulsoup4 lxml)';
RAISE NOTICE '3. Implement scraper modules in modules/scrapers/';
RAISE NOTICE '4. Update Discovery page with source selector';
RAISE NOTICE '5. Test parallel search execution';
