-- ============================================================
-- PART 2: Island Glass Company Setup & Seed Data
-- ============================================================
--
-- BEFORE RUNNING THIS:
-- 1. Run setup_company_data_PART1.sql first to get your user_id
-- 2. Copy your user_id (UUID) from those results
-- 3. Use Find/Replace (Cmd+F) in this file:
--    Find: YOUR_USER_ID_HERE
--    Replace: <paste your UUID here>
-- 4. Verify you replaced ALL 8 instances
-- 5. Then run this entire script
--
-- This script will:
-- - Create "Island Glass & Mirror" company record
-- - Link your user account to the company
-- - Insert all seed data with company_id (shared across all employees)
-- - Set created_by audit trails to your user_id
--
-- Expected: 8 replacements of YOUR_USER_ID_HERE
-- ============================================================

-- ============================================================
-- STEP 1: Create Company Record
-- ============================================================

-- Check if company already exists
DO $$
DECLARE
    v_company_id UUID;
BEGIN
    -- Check if Island Glass company exists
    SELECT id INTO v_company_id
    FROM companies
    WHERE name = 'Island Glass & Mirror'
    LIMIT 1;

    -- If not found, create it with a fixed UUID
    IF v_company_id IS NULL THEN
        v_company_id := 'a0000000-0000-0000-0000-000000000001'::UUID;

        INSERT INTO companies (id, name, created_at)
        VALUES (v_company_id, 'Island Glass & Mirror', NOW());

        RAISE NOTICE 'Created Island Glass & Mirror company with ID: %', v_company_id;
    ELSE
        RAISE NOTICE 'Island Glass & Mirror company already exists with ID: %', v_company_id;
    END IF;
END $$;

-- ============================================================
-- STEP 2: Link Current User to Company
-- ============================================================

-- First, let's see what users exist
SELECT
    id as user_id,
    email,
    'Run this query first to see your user_id' as note
FROM auth.users
ORDER BY created_at DESC
LIMIT 5;

-- MANUAL STEP: Copy your user_id from the query above and replace 'YOUR_USER_ID_HERE' below
-- Then run the rest of the script

-- Update user_profiles to link user to Island Glass
DO $$
DECLARE
    v_company_id UUID := 'a0000000-0000-0000-0000-000000000001'::UUID;
    v_user_id UUID := 'YOUR_USER_ID_HERE'::UUID;  -- REPLACE THIS with your actual user_id
BEGIN
    -- Check if user_profiles record exists
    IF EXISTS (SELECT 1 FROM user_profiles WHERE user_id = v_user_id) THEN
        -- Update existing record
        UPDATE user_profiles
        SET company_id = v_company_id,
            updated_at = NOW()
        WHERE user_id = v_user_id;

        RAISE NOTICE 'Linked user % to Island Glass company', v_user_id;
    ELSE
        -- Create new user_profiles record
        INSERT INTO user_profiles (user_id, company_id, full_name, role, created_at, updated_at)
        VALUES (v_user_id, v_company_id, NULL, 'user', NOW(), NOW());

        RAISE NOTICE 'Created user_profiles record for user % and linked to Island Glass', v_user_id;
    END IF;
END $$;

-- ============================================================
-- STEP 3: Seed Data - Glass Calculator Configuration
-- ============================================================

-- Insert glass configurations for all thickness/type combinations
INSERT INTO glass_config (
    thickness,
    type,
    base_price,
    polish_price,
    only_tempered,
    no_polish,
    never_tempered,
    company_id,
    created_by,
    created_at
)
SELECT
    thickness,
    type,
    base_price,
    polish_price,
    only_tempered,
    no_polish,
    never_tempered,
    'a0000000-0000-0000-0000-000000000001'::UUID,  -- Island Glass company_id
    'YOUR_USER_ID_HERE'::UUID,                      -- created_by (REPLACE with your user_id)
    NOW()
FROM (
    VALUES
        -- 1/8" Clear
        ('1/8"', 'clear', 8.50, 0.65, FALSE, FALSE, FALSE),

        -- 3/16" Clear (must be tempered)
        ('3/16"', 'clear', 10.00, 0.75, TRUE, FALSE, FALSE),

        -- 1/4" Clear
        ('1/4"', 'clear', 12.50, 0.85, FALSE, FALSE, FALSE),

        -- 3/8" Clear
        ('3/8"', 'clear', 18.00, 1.10, FALSE, FALSE, FALSE),

        -- 1/2" Clear
        ('1/2"', 'clear', 22.50, 1.35, FALSE, FALSE, FALSE),

        -- 1/4" Bronze
        ('1/4"', 'bronze', 18.00, 0.85, FALSE, FALSE, FALSE),

        -- 3/8" Bronze
        ('3/8"', 'bronze', 25.00, 1.10, FALSE, FALSE, FALSE),

        -- 1/2" Bronze
        ('1/2"', 'bronze', 30.00, 1.35, FALSE, FALSE, FALSE),

        -- 1/4" Gray
        ('1/4"', 'gray', 16.50, 0.85, FALSE, FALSE, FALSE),

        -- 3/8" Gray
        ('3/8"', 'gray', 23.00, 1.10, FALSE, FALSE, FALSE),

        -- 1/2" Gray
        ('1/2"', 'gray', 28.00, 1.35, FALSE, FALSE, FALSE),

        -- 1/4" Mirror (cannot be tempered, flat polish only)
        ('1/4"', 'mirror', 15.00, 0.27, FALSE, TRUE, TRUE),

        -- 3/8" Mirror
        ('3/8"', 'mirror', 20.00, 0.27, FALSE, TRUE, TRUE)
) AS data(thickness, type, base_price, polish_price, only_tempered, no_polish, never_tempered)
WHERE NOT EXISTS (
    -- Prevent duplicate inserts if script is run multiple times
    SELECT 1 FROM glass_config
    WHERE glass_config.thickness = data.thickness
      AND glass_config.type = data.type
      AND glass_config.company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
);

-- Insert default markups (tempered and shape)
INSERT INTO markups (
    name,
    percentage,
    company_id,
    created_by,
    created_at
)
SELECT
    name,
    percentage,
    'a0000000-0000-0000-0000-000000000001'::UUID,
    'YOUR_USER_ID_HERE'::UUID,  -- created_by (REPLACE with your user_id)
    NOW()
FROM (
    VALUES
        ('tempered', 35.0),  -- 35% markup for tempered glass
        ('shape', 25.0)      -- 25% markup for non-rectangular shapes
) AS data(name, percentage)
WHERE NOT EXISTS (
    SELECT 1 FROM markups
    WHERE markups.name = data.name
      AND markups.company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
);

-- Insert beveled edge pricing by thickness
INSERT INTO beveled_pricing (
    glass_thickness,
    price_per_inch,
    company_id,
    created_by,
    created_at
)
SELECT
    glass_thickness,
    price_per_inch,
    'a0000000-0000-0000-0000-0000-000000000001'::UUID,
    'YOUR_USER_ID_HERE'::UUID,  -- created_by (REPLACE with your user_id)
    NOW()
FROM (
    VALUES
        ('3/16"', 1.50),
        ('1/4"', 2.01),
        ('3/8"', 2.91),
        ('1/2"', 3.80)
) AS data(glass_thickness, price_per_inch)
WHERE NOT EXISTS (
    SELECT 1 FROM beveled_pricing
    WHERE beveled_pricing.glass_thickness = data.glass_thickness
      AND beveled_pricing.company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
);

-- Insert clipped corners pricing
INSERT INTO clipped_corners_pricing (
    glass_thickness,
    clip_size,
    price_per_corner,
    company_id,
    created_by,
    created_at
)
SELECT
    glass_thickness,
    clip_size,
    price_per_corner,
    'a0000000-0000-0000-0000-0000-000000000001'::UUID,
    'YOUR_USER_ID_HERE'::UUID,  -- created_by (REPLACE with your user_id)
    NOW()
FROM (
    VALUES
        -- 1/4" glass
        ('1/4"', 'under_1', 5.50),   -- Under 1 inch clip
        ('1/4"', 'over_1', 22.18),   -- Over 1 inch clip

        -- 3/8" glass
        ('3/8"', 'under_1', 7.50),
        ('3/8"', 'over_1', 30.00),

        -- 1/2" glass
        ('1/2"', 'under_1', 9.00),
        ('1/2"', 'over_1', 35.00)
) AS data(glass_thickness, clip_size, price_per_corner)
WHERE NOT EXISTS (
    SELECT 1 FROM clipped_corners_pricing
    WHERE clipped_corners_pricing.glass_thickness = data.glass_thickness
      AND clipped_corners_pricing.clip_size = data.clip_size
      AND clipped_corners_pricing.company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
);

-- ============================================================
-- STEP 4: Seed Data - Inventory Reference Data
-- ============================================================

-- Insert default inventory categories
INSERT INTO inventory_categories (
    name,
    company_id,
    created_by,
    created_at
)
SELECT
    name,
    'a0000000-0000-0000-0000-000000000001'::UUID,
    'YOUR_USER_ID_HERE'::UUID,  -- created_by (REPLACE with your user_id)
    NOW()
FROM (
    VALUES
        ('Spacers'),
        ('Butyl'),
        ('Desiccant'),
        ('Molecular Sieve'),
        ('Glass Stock'),
        ('Hardware')
) AS data(name)
WHERE NOT EXISTS (
    SELECT 1 FROM inventory_categories
    WHERE inventory_categories.name = data.name
      AND inventory_categories.company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
);

-- Insert default inventory units
INSERT INTO inventory_units (
    name,
    company_id,
    created_by,
    created_at
)
SELECT
    name,
    'a0000000-0000-0000-0000-000000000001'::UUID,
    'YOUR_USER_ID_HERE'::UUID,  -- created_by (REPLACE with your user_id)
    NOW()
FROM (
    VALUES
        ('pieces'),
        ('linear feet'),
        ('pounds'),
        ('gallons'),
        ('boxes'),
        ('rolls'),
        ('square feet')
) AS data(name)
WHERE NOT EXISTS (
    SELECT 1 FROM inventory_units
    WHERE inventory_units.name = data.name
      AND inventory_units.company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
);

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Show company info
SELECT
    id,
    name,
    created_at,
    'Company Record' as record_type
FROM companies
WHERE id = 'a0000000-0000-0000-0000-000000000001'::UUID;

-- Show current user's company linkage (replace YOUR_USER_ID_HERE)
SELECT
    user_id,
    company_id,
    full_name,
    role,
    'User Profile' as record_type
FROM user_profiles
WHERE user_id = 'YOUR_USER_ID_HERE'::UUID;

-- Check glass configurations (should return 13 rows)
SELECT
    thickness,
    type,
    base_price,
    polish_price,
    CASE
        WHEN only_tempered THEN 'Must be tempered'
        WHEN never_tempered THEN 'Cannot be tempered'
        ELSE 'Optional tempered'
    END as tempered_rule,
    'Glass Config' as record_type
FROM glass_config
WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
ORDER BY
    CASE thickness
        WHEN '1/8"' THEN 1
        WHEN '3/16"' THEN 2
        WHEN '1/4"' THEN 3
        WHEN '3/8"' THEN 4
        WHEN '1/2"' THEN 5
    END,
    type;

-- Check markups (should return 2 rows)
SELECT
    name,
    percentage || '%' as percentage,
    'Markup' as record_type
FROM markups
WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID;

-- Check beveled pricing (should return 4 rows)
SELECT
    glass_thickness,
    '$' || price_per_inch || '/inch' as price,
    'Beveled Pricing' as record_type
FROM beveled_pricing
WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
ORDER BY
    CASE glass_thickness
        WHEN '3/16"' THEN 1
        WHEN '1/4"' THEN 2
        WHEN '3/8"' THEN 3
        WHEN '1/2"' THEN 4
    END;

-- Check clipped corners pricing (should return 6 rows)
SELECT
    glass_thickness,
    CASE clip_size
        WHEN 'under_1' THEN 'Under 1"'
        WHEN 'over_1' THEN 'Over 1"'
    END as clip_size,
    '$' || price_per_corner || '/corner' as price,
    'Clipped Corner' as record_type
FROM clipped_corners_pricing
WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
ORDER BY glass_thickness, clip_size;

-- Check inventory categories (should return 6 rows)
SELECT
    name,
    'Inventory Category' as record_type
FROM inventory_categories
WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
ORDER BY name;

-- Check inventory units (should return 7 rows)
SELECT
    name,
    'Inventory Unit' as record_type
FROM inventory_units
WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID
ORDER BY name;

-- ============================================================
-- SUMMARY
-- ============================================================

SELECT
    'Setup Complete!' as status,
    (SELECT COUNT(*) FROM glass_config WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID) as glass_configs,
    (SELECT COUNT(*) FROM markups WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID) as markups,
    (SELECT COUNT(*) FROM beveled_pricing WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID) as beveled_prices,
    (SELECT COUNT(*) FROM clipped_corners_pricing WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID) as corner_prices,
    (SELECT COUNT(*) FROM inventory_categories WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID) as categories,
    (SELECT COUNT(*) FROM inventory_units WHERE company_id = 'a0000000-0000-0000-0000-000000000001'::UUID) as units;

-- ============================================================
-- SUCCESS!
-- Expected Results:
--   - 13 glass configurations
--   - 2 markups
--   - 4 beveled pricing records
--   - 6 clipped corner pricing records
--   - 6 inventory categories
--   - 7 inventory units
--
-- Your Glass Calculator is now ready to use!
-- Navigate to http://localhost:8050/calculator
--
-- All data is company-scoped, meaning:
--   - ALL Island Glass employees will see this data
--   - created_by field tracks who set up the data (you!)
--   - When you add more users, they'll automatically see all this data
-- ============================================================
