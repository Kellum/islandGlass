-- ============================================================
-- Glass Calculator Setup Script
-- Run this in Supabase SQL Editor after running glassprice_migration.sql
-- ============================================================

-- Step 1: Get your user ID (you'll see it in the results)
SELECT id as user_id, email FROM auth.users;

-- Step 2: REPLACE 'YOUR_USER_ID_HERE' below with the UUID from Step 1
-- Then run the rest of this script

-- ============================================================
-- SEED DATA - Glass Calculator Configuration
-- ============================================================

-- Glass configuration for all types and thicknesses
INSERT INTO glass_config (thickness, type, base_price, polish_price, only_tempered, no_polish, never_tempered, user_id)
VALUES
    -- 1/8" Clear
    ('1/8"', 'clear', 8.50, 0.65, FALSE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 3/16" Clear (must be tempered)
    ('3/16"', 'clear', 10.00, 0.75, TRUE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 1/4" Clear
    ('1/4"', 'clear', 12.50, 0.85, FALSE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 3/8" Clear
    ('3/8"', 'clear', 18.00, 1.10, FALSE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 1/2" Clear
    ('1/2"', 'clear', 22.50, 1.35, FALSE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 1/4" Bronze
    ('1/4"', 'bronze', 18.00, 0.85, FALSE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 3/8" Bronze
    ('3/8"', 'bronze', 25.00, 1.10, FALSE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 1/2" Bronze
    ('1/2"', 'bronze', 30.00, 1.35, FALSE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 1/4" Gray
    ('1/4"', 'gray', 16.50, 0.85, FALSE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 3/8" Gray
    ('3/8"', 'gray', 23.00, 1.10, FALSE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 1/2" Gray
    ('1/2"', 'gray', 28.00, 1.35, FALSE, FALSE, FALSE, 'YOUR_USER_ID_HERE'),

    -- 1/4" Mirror (cannot be tempered, flat polish only)
    ('1/4"', 'mirror', 15.00, 0.27, FALSE, TRUE, TRUE, 'YOUR_USER_ID_HERE'),

    -- 3/8" Mirror
    ('3/8"', 'mirror', 20.00, 0.27, FALSE, TRUE, TRUE, 'YOUR_USER_ID_HERE');

-- Default markups (tempered and shape)
INSERT INTO markups (name, percentage, user_id)
VALUES
    ('tempered', 35.0, 'YOUR_USER_ID_HERE'),  -- 35% markup for tempered glass
    ('shape', 25.0, 'YOUR_USER_ID_HERE');      -- 25% markup for non-rectangular shapes

-- Beveled edge pricing by thickness (not available for 1/8")
INSERT INTO beveled_pricing (glass_thickness, price_per_inch, user_id)
VALUES
    ('3/16"', 1.50, 'YOUR_USER_ID_HERE'),
    ('1/4"', 2.01, 'YOUR_USER_ID_HERE'),
    ('3/8"', 2.91, 'YOUR_USER_ID_HERE'),
    ('1/2"', 3.80, 'YOUR_USER_ID_HERE');

-- Clipped corners pricing
INSERT INTO clipped_corners_pricing (glass_thickness, clip_size, price_per_corner, user_id)
VALUES
    -- 1/4" glass
    ('1/4"', 'under_1', 5.50, 'YOUR_USER_ID_HERE'),   -- Under 1 inch clip
    ('1/4"', 'over_1', 22.18, 'YOUR_USER_ID_HERE'),   -- Over 1 inch clip

    -- 3/8" glass
    ('3/8"', 'under_1', 7.50, 'YOUR_USER_ID_HERE'),
    ('3/8"', 'over_1', 30.00, 'YOUR_USER_ID_HERE'),

    -- 1/2" glass
    ('1/2"', 'under_1', 9.00, 'YOUR_USER_ID_HERE'),
    ('1/2"', 'over_1', 35.00, 'YOUR_USER_ID_HERE');

-- ============================================================
-- OPTIONAL: Inventory Setup (if you want to use inventory management)
-- ============================================================

-- Default inventory categories
INSERT INTO inventory_categories (name, user_id)
VALUES
    ('Spacers', 'YOUR_USER_ID_HERE'),
    ('Butyl', 'YOUR_USER_ID_HERE'),
    ('Desiccant', 'YOUR_USER_ID_HERE'),
    ('Molecular Sieve', 'YOUR_USER_ID_HERE'),
    ('Glass Stock', 'YOUR_USER_ID_HERE'),
    ('Hardware', 'YOUR_USER_ID_HERE');

-- Default inventory units
INSERT INTO inventory_units (name, user_id)
VALUES
    ('pieces', 'YOUR_USER_ID_HERE'),
    ('linear feet', 'YOUR_USER_ID_HERE'),
    ('pounds', 'YOUR_USER_ID_HERE'),
    ('gallons', 'YOUR_USER_ID_HERE'),
    ('boxes', 'YOUR_USER_ID_HERE'),
    ('rolls', 'YOUR_USER_ID_HERE'),
    ('square feet', 'YOUR_USER_ID_HERE');

-- ============================================================
-- Verification Queries (run these to confirm data was inserted)
-- ============================================================

-- Check glass config
SELECT thickness, type, base_price, polish_price
FROM glass_config
WHERE user_id = 'YOUR_USER_ID_HERE'
ORDER BY thickness, type;

-- Check markups
SELECT name, percentage
FROM markups
WHERE user_id = 'YOUR_USER_ID_HERE';

-- Check beveled pricing
SELECT glass_thickness, price_per_inch
FROM beveled_pricing
WHERE user_id = 'YOUR_USER_ID_HERE'
ORDER BY glass_thickness;

-- Check clipped corners pricing
SELECT glass_thickness, clip_size, price_per_corner
FROM clipped_corners_pricing
WHERE user_id = 'YOUR_USER_ID_HERE'
ORDER BY glass_thickness, clip_size;

-- ============================================================
-- SUCCESS!
-- If all queries return data, your Glass Calculator is ready to use!
-- Navigate to http://localhost:8050/calculator
-- ============================================================
