-- ============================================================
-- Glass Calculator Pricing Seed Data
-- Populates pricing tables with default values
-- ============================================================

-- INSTRUCTIONS:
-- 1. Get your company_id: SELECT id, name FROM companies;
-- 2. Get your user_id: SELECT id, email FROM auth.users;
-- 3. Replace the variables below with your actual UUIDs
-- 4. Run this entire script in Supabase SQL Editor

-- ============================================================
-- SET YOUR IDs HERE
-- ============================================================
DO $$
DECLARE
    v_company_id UUID;
    v_user_id UUID;
BEGIN
    -- Get the first company (or modify to select yours)
    SELECT id INTO v_company_id FROM companies LIMIT 1;

    -- Get the first user (or modify to select yours)
    SELECT id INTO v_user_id FROM auth.users LIMIT 1;

    -- Display the IDs being used
    RAISE NOTICE 'Using Company ID: %', v_company_id;
    RAISE NOTICE 'Using User ID: %', v_user_id;

    -- ============================================================
    -- GLASS CONFIGURATION
    -- ============================================================

    INSERT INTO glass_config (thickness, type, base_price, polish_price, only_tempered, no_polish, never_tempered, company_id, created_by)
    VALUES
        -- 1/8" Clear
        ('1/8"', 'clear', 8.50, 0.65, FALSE, FALSE, FALSE, v_company_id, v_user_id),

        -- 3/16" Clear (must be tempered)
        ('3/16"', 'clear', 10.00, 0.75, TRUE, FALSE, FALSE, v_company_id, v_user_id),

        -- 1/4" Clear
        ('1/4"', 'clear', 12.50, 0.85, FALSE, FALSE, FALSE, v_company_id, v_user_id),

        -- 3/8" Clear
        ('3/8"', 'clear', 18.00, 1.10, FALSE, FALSE, FALSE, v_company_id, v_user_id),

        -- 1/2" Clear
        ('1/2"', 'clear', 22.50, 1.35, FALSE, FALSE, FALSE, v_company_id, v_user_id),

        -- 1/4" Bronze
        ('1/4"', 'bronze', 18.00, 0.85, FALSE, FALSE, FALSE, v_company_id, v_user_id),

        -- 3/8" Bronze
        ('3/8"', 'bronze', 25.00, 1.10, FALSE, FALSE, FALSE, v_company_id, v_user_id),

        -- 1/2" Bronze
        ('1/2"', 'bronze', 30.00, 1.35, FALSE, FALSE, FALSE, v_company_id, v_user_id),

        -- 1/4" Gray
        ('1/4"', 'gray', 16.50, 0.85, FALSE, FALSE, FALSE, v_company_id, v_user_id),

        -- 3/8" Gray
        ('3/8"', 'gray', 23.00, 1.10, FALSE, FALSE, FALSE, v_company_id, v_user_id),

        -- 1/2" Gray
        ('1/2"', 'gray', 28.00, 1.35, FALSE, FALSE, FALSE, v_company_id, v_user_id),

        -- 1/4" Mirror (cannot be tempered, flat polish only)
        ('1/4"', 'mirror', 15.00, 0.27, FALSE, TRUE, TRUE, v_company_id, v_user_id),

        -- 3/8" Mirror
        ('3/8"', 'mirror', 20.00, 0.27, FALSE, TRUE, TRUE, v_company_id, v_user_id)
    ON CONFLICT (thickness, type, company_id) DO NOTHING;

    -- ============================================================
    -- MARKUPS
    -- ============================================================

    INSERT INTO markups (name, percentage, company_id, created_by)
    VALUES
        ('tempered', 35.0, v_company_id, v_user_id),  -- 35% markup for tempered glass
        ('shape', 25.0, v_company_id, v_user_id)      -- 25% markup for non-rectangular shapes
    ON CONFLICT (name, company_id) DO NOTHING;

    -- ============================================================
    -- BEVELED EDGE PRICING
    -- ============================================================

    INSERT INTO beveled_pricing (glass_thickness, price_per_inch, company_id, created_by)
    VALUES
        ('3/16"', 1.50, v_company_id, v_user_id),
        ('1/4"', 2.01, v_company_id, v_user_id),
        ('3/8"', 2.91, v_company_id, v_user_id),
        ('1/2"', 3.80, v_company_id, v_user_id)
    ON CONFLICT (glass_thickness, company_id) DO NOTHING;

    -- ============================================================
    -- CLIPPED CORNERS PRICING
    -- ============================================================

    INSERT INTO clipped_corners_pricing (glass_thickness, clip_size, price_per_corner, company_id, created_by)
    VALUES
        -- 1/4" glass
        ('1/4"', 'under_1', 5.50, v_company_id, v_user_id),   -- Under 1 inch clip
        ('1/4"', 'over_1', 22.18, v_company_id, v_user_id),   -- Over 1 inch clip

        -- 3/8" glass
        ('3/8"', 'under_1', 7.50, v_company_id, v_user_id),
        ('3/8"', 'over_1', 30.00, v_company_id, v_user_id),

        -- 1/2" glass
        ('1/2"', 'under_1', 9.00, v_company_id, v_user_id),
        ('1/2"', 'over_1', 35.00, v_company_id, v_user_id)
    ON CONFLICT (glass_thickness, clip_size, company_id) DO NOTHING;

    RAISE NOTICE 'Pricing data seeded successfully!';

END $$;

-- ============================================================
-- VERIFY INSERTION
-- ============================================================

-- Check glass configuration
SELECT
    'Glass Config' as table_name,
    COUNT(*) as row_count
FROM glass_config
WHERE deleted_at IS NULL;

-- Check markups
SELECT
    'Markups' as table_name,
    COUNT(*) as row_count
FROM markups
WHERE deleted_at IS NULL;

-- Check beveled pricing
SELECT
    'Beveled Pricing' as table_name,
    COUNT(*) as row_count
FROM beveled_pricing
WHERE deleted_at IS NULL;

-- Check clipped corners
SELECT
    'Clipped Corners' as table_name,
    COUNT(*) as row_count
FROM clipped_corners_pricing
WHERE deleted_at IS NULL;

-- Display all glass configurations
SELECT
    thickness,
    type,
    base_price,
    polish_price,
    only_tempered,
    no_polish,
    never_tempered
FROM glass_config
WHERE deleted_at IS NULL
ORDER BY
    CASE thickness
        WHEN '1/8"' THEN 1
        WHEN '3/16"' THEN 2
        WHEN '1/4"' THEN 3
        WHEN '3/8"' THEN 4
        WHEN '1/2"' THEN 5
    END,
    type;
