-- =====================================================
-- PO Auto-Generation Enhancement
-- Island Glass CRM
--
-- Adds fields to support automated PO number generation
-- based on location, client name, and address
-- =====================================================

-- ============================================
-- 1. ADD NEW FIELDS TO JOBS TABLE
-- ============================================

ALTER TABLE jobs
ADD COLUMN IF NOT EXISTS location_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS is_remake BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_warranty BOOLEAN DEFAULT FALSE;

-- Add check constraint to prevent both is_remake and is_warranty being true
ALTER TABLE jobs
ADD CONSTRAINT chk_remake_or_warranty CHECK (
    NOT (is_remake = TRUE AND is_warranty = TRUE)
);

-- Add index for location_code for faster queries
CREATE INDEX IF NOT EXISTS idx_jobs_location_code ON jobs(location_code);

-- Add composite index for duplicate PO detection
CREATE INDEX IF NOT EXISTS idx_jobs_client_location ON jobs(client_id, location_code);

-- ============================================
-- 2. CREATE LOCATIONS REFERENCE TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    location_code VARCHAR(10) NOT NULL UNIQUE,
    location_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,

    -- Audit Trail
    company_id UUID REFERENCES auth.users(id),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add update trigger for locations
CREATE TRIGGER update_locations_updated_at BEFORE UPDATE ON locations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_locations_code ON locations(location_code);
CREATE INDEX IF NOT EXISTS idx_locations_active ON locations(is_active);

-- ============================================
-- 3. SEED LOCATION DATA
-- ============================================

INSERT INTO locations (location_code, location_name, description, is_active, sort_order)
VALUES
    ('01', 'Fernandina/Yulee, FL', 'Covers Fernandina Beach and Yulee, Florida area', TRUE, 1),
    ('02', 'Georgia', 'All jobs in Georgia', TRUE, 2),
    ('03', 'Jacksonville, FL', 'All jobs in Jacksonville, Florida area', TRUE, 3)
ON CONFLICT (location_code) DO UPDATE SET
    location_name = EXCLUDED.location_name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    sort_order = EXCLUDED.sort_order;

-- ============================================
-- 4. HELPER FUNCTION: EXTRACT STREET NUMBER
-- ============================================

CREATE OR REPLACE FUNCTION extract_street_number(address_text TEXT)
RETURNS VARCHAR AS $$
DECLARE
    street_number VARCHAR;
BEGIN
    -- Extract first sequence of digits from address
    -- Example: "123 Main St Apt 4B" -> "123"
    SELECT regexp_replace(address_text, '^[^0-9]*([0-9]+).*', '\1')
    INTO street_number;

    -- Return NULL if no number found
    IF street_number = address_text OR street_number = '' THEN
        RETURN NULL;
    END IF;

    RETURN street_number;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- 5. HELPER FUNCTION: FORMAT NAME FOR PO
-- ============================================

CREATE OR REPLACE FUNCTION format_name_for_po(
    company_name_param TEXT,
    contact_name_param TEXT,
    is_remake_param BOOLEAN,
    is_warranty_param BOOLEAN
)
RETURNS VARCHAR AS $$
DECLARE
    formatted_name VARCHAR;
    first_name VARCHAR;
    last_name VARCHAR;
    name_parts TEXT[];
BEGIN
    -- Handle remake jobs: "RMK.LastName"
    IF is_remake_param = TRUE THEN
        -- Try to extract last name from contact_name or use company_name
        IF contact_name_param IS NOT NULL AND contact_name_param != '' THEN
            name_parts := regexp_split_to_array(TRIM(contact_name_param), '\s+');
            -- Get last element as last name
            last_name := name_parts[array_length(name_parts, 1)];
            RETURN 'RMK.' || REPLACE(last_name, ' ', '');
        ELSE
            -- Use company name if no contact name
            RETURN 'RMK.' || REPLACE(TRIM(company_name_param), ' ', '');
        END IF;
    END IF;

    -- Handle warranty jobs: "WAR.LastName"
    IF is_warranty_param = TRUE THEN
        -- Try to extract last name from contact_name or use company_name
        IF contact_name_param IS NOT NULL AND contact_name_param != '' THEN
            name_parts := regexp_split_to_array(TRIM(contact_name_param), '\s+');
            -- Get last element as last name
            last_name := name_parts[array_length(name_parts, 1)];
            RETURN 'WAR.' || REPLACE(last_name, ' ', '');
        ELSE
            -- Use company name if no contact name
            RETURN 'WAR.' || REPLACE(TRIM(company_name_param), ' ', '');
        END IF;
    END IF;

    -- Regular jobs: Use company name if available, otherwise format contact name as "FirstName.LastName"
    IF company_name_param IS NOT NULL AND company_name_param != '' THEN
        -- Use company name, remove spaces
        formatted_name := REPLACE(TRIM(company_name_param), ' ', '');
    ELSIF contact_name_param IS NOT NULL AND contact_name_param != '' THEN
        -- Split contact name into parts
        name_parts := regexp_split_to_array(TRIM(contact_name_param), '\s+');

        IF array_length(name_parts, 1) >= 2 THEN
            -- Get first and last name
            first_name := name_parts[1];
            last_name := name_parts[array_length(name_parts, 1)];
            formatted_name := first_name || '.' || last_name;
        ELSE
            -- Only one name provided, use it as-is
            formatted_name := contact_name_param;
        END IF;
    ELSE
        -- No name available
        RETURN 'UNKNOWN';
    END IF;

    -- Clean up special characters, keep only alphanumeric and dots
    formatted_name := regexp_replace(formatted_name, '[^a-zA-Z0-9.]', '', 'g');

    RETURN formatted_name;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- 6. HELPER FUNCTION: COUNT DUPLICATE POs
-- ============================================

CREATE OR REPLACE FUNCTION count_duplicate_pos(
    client_id_param INTEGER,
    location_code_param VARCHAR,
    name_part VARCHAR,
    street_number_param VARCHAR
)
RETURNS INTEGER AS $$
DECLARE
    po_count INTEGER;
    base_po VARCHAR;
BEGIN
    -- Build base PO pattern (without sequence number)
    base_po := 'PO-' || location_code_param || '-' || name_part || '.' || street_number_param;

    -- Count existing POs that match this pattern
    SELECT COUNT(*)
    INTO po_count
    FROM jobs
    WHERE client_id = client_id_param
        AND location_code = location_code_param
        AND (
            po_number = base_po
            OR po_number LIKE base_po || '-%'
        )
        AND deleted_at IS NULL;

    RETURN COALESCE(po_count, 0);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- END OF PO AUTO-GENERATION MIGRATION
-- =====================================================
