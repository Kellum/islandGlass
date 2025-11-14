-- ============================================
-- Window Manufacturing System - Seed Data
-- Phase 3b: Initial configuration data
-- ============================================

-- This script should be run AFTER window_manufacturing_schema.sql
-- It creates default printer configurations for existing companies

-- ============================================
-- Insert default printer config for each company
-- ============================================

INSERT INTO label_printer_config (
    name,
    ip_address,
    port,
    label_width,
    label_height,
    is_active,
    is_default,
    company_id,
    created_by
)
SELECT
    'Zebra ZD421 (Mock)' as name,
    '192.168.1.100' as ip_address,  -- Placeholder IP
    9100 as port,
    3.0 as label_width,   -- 3 inch width
    2.0 as label_height,  -- 2 inch height
    TRUE as is_active,
    TRUE as is_default,
    c.id as company_id,
    NULL as created_by  -- Optional field, set to NULL for seed data
FROM companies c
WHERE NOT EXISTS (
    -- Don't create if one already exists for this company
    SELECT 1 FROM label_printer_config lpc
    WHERE lpc.company_id = c.id
);

-- ============================================
-- Verification
-- ============================================

DO $$
DECLARE
    printer_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO printer_count FROM label_printer_config;

    RAISE NOTICE '';
    RAISE NOTICE '============================================';
    RAISE NOTICE '✓ Seed Data Loaded Successfully';
    RAISE NOTICE '============================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Printer Configurations: %', printer_count;
    RAISE NOTICE '';
    RAISE NOTICE 'Next Steps:';
    RAISE NOTICE '  1. Update printer IP addresses in admin settings';
    RAISE NOTICE '  2. Test label generation';
    RAISE NOTICE '  3. Configure actual Zebra printer connection';
    RAISE NOTICE '';
    RAISE NOTICE '============================================';
END $$;

-- Display created printer configs
SELECT
    lpc.id,
    lpc.name,
    lpc.ip_address,
    lpc.port,
    lpc.label_width || ' x ' || lpc.label_height || ' inches' as label_size,
    lpc.is_default,
    c.name as company_name
FROM label_printer_config lpc
JOIN companies c ON c.id = lpc.company_id
ORDER BY c.name;
