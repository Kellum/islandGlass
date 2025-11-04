-- ============================================================
-- Island Glass Seed Data - AUTOMATIC VERSION
-- No manual find-and-replace needed!
-- ============================================================
--
-- This script automatically:
-- 1. Finds the Island Glass & Mirror company_id
-- 2. Uses the FIRST user account as the creator
-- 3. Inserts all seed data
--
-- Just run this entire script - no editing required!
-- ============================================================

DO $$
DECLARE
    v_company_id UUID;
    v_user_id UUID;
    v_insert_count INT;
BEGIN
    -- ============================================================
    -- STEP 1: Get Company ID
    -- ============================================================

    SELECT id INTO v_company_id
    FROM companies
    WHERE name = 'Island Glass & Mirror'
    LIMIT 1;

    IF v_company_id IS NULL THEN
        RAISE EXCEPTION 'Island Glass & Mirror company not found! Run complete_company_migration.sql first.';
    END IF;

    RAISE NOTICE 'Found company ID: %', v_company_id;

    -- ============================================================
    -- STEP 2: Get User ID (use first user)
    -- ============================================================

    SELECT id INTO v_user_id
    FROM auth.users
    ORDER BY created_at ASC
    LIMIT 1;

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'No users found! Create a user account first.';
    END IF;

    RAISE NOTICE 'Using user ID: %', v_user_id;

    -- ============================================================
    -- STEP 3: Link User to Company (if not already linked)
    -- ============================================================

    IF EXISTS (SELECT 1 FROM user_profiles WHERE user_id = v_user_id) THEN
        UPDATE user_profiles
        SET company_id = v_company_id,
            updated_at = NOW()
        WHERE user_id = v_user_id;
        RAISE NOTICE 'Updated user_profiles for user %', v_user_id;
    ELSE
        INSERT INTO user_profiles (user_id, company_id, full_name, role, created_at, updated_at)
        VALUES (v_user_id, v_company_id, NULL, 'user', NOW(), NOW());
        RAISE NOTICE 'Created user_profiles for user %', v_user_id;
    END IF;

    -- ============================================================
    -- STEP 4: Insert Glass Config (13 records)
    -- ============================================================

    INSERT INTO glass_config (
        thickness, type, base_price, polish_price,
        only_tempered, no_polish, never_tempered,
        company_id, created_by, created_at
    )
    SELECT * FROM (VALUES
        ('1/8"', 'clear', 8.50, 0.65, FALSE, FALSE, FALSE),
        ('3/16"', 'clear', 10.00, 0.75, TRUE, FALSE, FALSE),
        ('1/4"', 'clear', 12.50, 0.85, FALSE, FALSE, FALSE),
        ('3/8"', 'clear', 18.00, 1.10, FALSE, FALSE, FALSE),
        ('1/2"', 'clear', 22.50, 1.35, FALSE, FALSE, FALSE),
        ('1/4"', 'bronze', 18.00, 0.85, FALSE, FALSE, FALSE),
        ('3/8"', 'bronze', 25.00, 1.10, FALSE, FALSE, FALSE),
        ('1/2"', 'bronze', 30.00, 1.35, FALSE, FALSE, FALSE),
        ('1/4"', 'gray', 16.50, 0.85, FALSE, FALSE, FALSE),
        ('3/8"', 'gray', 23.00, 1.10, FALSE, FALSE, FALSE),
        ('1/2"', 'gray', 28.00, 1.35, FALSE, FALSE, FALSE),
        ('1/4"', 'mirror', 15.00, 0.27, FALSE, TRUE, TRUE),
        ('3/8"', 'mirror', 20.00, 0.27, FALSE, TRUE, TRUE)
    ) AS data(thickness, type, base_price, polish_price, only_tempered, no_polish, never_tempered)
    WHERE NOT EXISTS (
        SELECT 1 FROM glass_config
        WHERE glass_config.thickness = data.thickness
          AND glass_config.type = data.type
          AND glass_config.company_id = v_company_id
    );

    GET DIAGNOSTICS v_insert_count = ROW_COUNT;
    RAISE NOTICE 'Inserted % glass configurations', v_insert_count;

    -- Add company_id and created_by to the SELECT
    UPDATE glass_config
    SET company_id = v_company_id, created_by = v_user_id
    WHERE company_id IS NULL OR created_by IS NULL;

    -- ============================================================
    -- STEP 5: Insert Markups (2 records)
    -- ============================================================

    INSERT INTO markups (name, percentage, company_id, created_by, created_at)
    SELECT * FROM (VALUES
        ('tempered', 35.0),
        ('shape', 25.0)
    ) AS data(name, percentage)
    WHERE NOT EXISTS (
        SELECT 1 FROM markups
        WHERE markups.name = data.name
          AND markups.company_id = v_company_id
    );

    UPDATE markups
    SET company_id = v_company_id, created_by = v_user_id
    WHERE company_id IS NULL OR created_by IS NULL;

    GET DIAGNOSTICS v_insert_count = ROW_COUNT;
    RAISE NOTICE 'Inserted markups';

    -- ============================================================
    -- STEP 6: Insert Beveled Pricing (4 records)
    -- ============================================================

    INSERT INTO beveled_pricing (glass_thickness, price_per_inch, company_id, created_by, created_at)
    SELECT * FROM (VALUES
        ('3/16"', 1.50),
        ('1/4"', 2.01),
        ('3/8"', 2.91),
        ('1/2"', 3.80)
    ) AS data(glass_thickness, price_per_inch)
    WHERE NOT EXISTS (
        SELECT 1 FROM beveled_pricing
        WHERE beveled_pricing.glass_thickness = data.glass_thickness
          AND beveled_pricing.company_id = v_company_id
    );

    UPDATE beveled_pricing
    SET company_id = v_company_id, created_by = v_user_id
    WHERE company_id IS NULL OR created_by IS NULL;

    RAISE NOTICE 'Inserted beveled pricing';

    -- ============================================================
    -- STEP 7: Insert Clipped Corners Pricing (6 records)
    -- ============================================================

    INSERT INTO clipped_corners_pricing (
        glass_thickness, clip_size, price_per_corner,
        company_id, created_by, created_at
    )
    SELECT * FROM (VALUES
        ('1/4"', 'under_1', 5.50),
        ('1/4"', 'over_1', 22.18),
        ('3/8"', 'under_1', 7.50),
        ('3/8"', 'over_1', 30.00),
        ('1/2"', 'under_1', 9.00),
        ('1/2"', 'over_1', 35.00)
    ) AS data(glass_thickness, clip_size, price_per_corner)
    WHERE NOT EXISTS (
        SELECT 1 FROM clipped_corners_pricing
        WHERE clipped_corners_pricing.glass_thickness = data.glass_thickness
          AND clipped_corners_pricing.clip_size = data.clip_size
          AND clipped_corners_pricing.company_id = v_company_id
    );

    UPDATE clipped_corners_pricing
    SET company_id = v_company_id, created_by = v_user_id
    WHERE company_id IS NULL OR created_by IS NULL;

    RAISE NOTICE 'Inserted clipped corners pricing';

    -- ============================================================
    -- STEP 8: Insert Inventory Categories (6 records)
    -- ============================================================

    INSERT INTO inventory_categories (name, company_id, created_by, created_at)
    SELECT * FROM (VALUES
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
          AND inventory_categories.company_id = v_company_id
    );

    UPDATE inventory_categories
    SET company_id = v_company_id, created_by = v_user_id
    WHERE company_id IS NULL OR created_by IS NULL;

    RAISE NOTICE 'Inserted inventory categories';

    -- ============================================================
    -- STEP 9: Insert Inventory Units (7 records)
    -- ============================================================

    INSERT INTO inventory_units (name, company_id, created_by, created_at)
    SELECT * FROM (VALUES
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
          AND inventory_units.company_id = v_company_id
    );

    UPDATE inventory_units
    SET company_id = v_company_id, created_by = v_user_id
    WHERE company_id IS NULL OR created_by IS NULL;

    RAISE NOTICE 'Inserted inventory units';

    -- ============================================================
    -- STEP 10: Summary
    -- ============================================================

    RAISE NOTICE '====================================';
    RAISE NOTICE 'SEED DATA COMPLETE!';
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Company: %', v_company_id;
    RAISE NOTICE 'User: %', v_user_id;

END $$;

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Show summary
SELECT
    'Setup Complete!' as status,
    (SELECT COUNT(*) FROM glass_config WHERE deleted_at IS NULL) as glass_configs,
    (SELECT COUNT(*) FROM markups WHERE deleted_at IS NULL) as markups,
    (SELECT COUNT(*) FROM beveled_pricing WHERE deleted_at IS NULL) as beveled_prices,
    (SELECT COUNT(*) FROM clipped_corners_pricing WHERE deleted_at IS NULL) as corner_prices,
    (SELECT COUNT(*) FROM inventory_categories WHERE deleted_at IS NULL) as categories,
    (SELECT COUNT(*) FROM inventory_units WHERE deleted_at IS NULL) as units;

-- Show glass configurations
SELECT
    thickness,
    type,
    base_price,
    polish_price,
    'Glass Config' as record_type
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

-- ============================================================
-- SUCCESS!
-- Your Glass Calculator is now ready to use!
-- Navigate to http://localhost:8050/calculator
-- ============================================================
