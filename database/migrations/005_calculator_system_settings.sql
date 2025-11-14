-- ============================================
-- Calculator System Settings
-- Stores global calculator constants (editable by admins)
-- ============================================

-- Create calculator_settings table
CREATE TABLE IF NOT EXISTS calculator_settings (
    id SERIAL PRIMARY KEY,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value DECIMAL(10,4) NOT NULL,
    description TEXT,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_calculator_settings_key ON calculator_settings(setting_key);
CREATE INDEX IF NOT EXISTS idx_calculator_settings_company ON calculator_settings(company_id);

-- Insert default system settings
-- Note: Replace 'YOUR_COMPANY_ID' with actual company ID when running
INSERT INTO calculator_settings (setting_key, setting_value, description, company_id)
VALUES
    ('minimum_sq_ft', 3.0, 'Minimum billable square footage for all glass orders', NULL),
    ('markup_divisor', 0.28, 'Final quote price divisor (Quote Price = Total ÷ 0.28)', NULL),
    ('contractor_discount_rate', 0.15, 'Contractor discount percentage (15% = 0.15)', NULL),
    ('flat_polish_rate', 0.27, 'Flat polish rate per inch for mirror glass', NULL)
ON CONFLICT (setting_key) DO NOTHING;

-- Add soft delete to existing pricing tables
ALTER TABLE glass_config ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL;
ALTER TABLE markups ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL;
ALTER TABLE beveled_pricing ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL;
ALTER TABLE clipped_corners_pricing ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL;

-- Add updated_at and updated_by tracking to pricing tables
ALTER TABLE glass_config ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE glass_config ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES auth.users(id);

ALTER TABLE markups ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE markups ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES auth.users(id);

ALTER TABLE beveled_pricing ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE beveled_pricing ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES auth.users(id);

ALTER TABLE clipped_corners_pricing ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE clipped_corners_pricing ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES auth.users(id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_calculator_settings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
DROP TRIGGER IF EXISTS calculator_settings_updated_at ON calculator_settings;
CREATE TRIGGER calculator_settings_updated_at
    BEFORE UPDATE ON calculator_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_calculator_settings_timestamp();

DROP TRIGGER IF EXISTS glass_config_updated_at ON glass_config;
CREATE TRIGGER glass_config_updated_at
    BEFORE UPDATE ON glass_config
    FOR EACH ROW
    EXECUTE FUNCTION update_calculator_settings_timestamp();

DROP TRIGGER IF EXISTS markups_updated_at ON markups;
CREATE TRIGGER markups_updated_at
    BEFORE UPDATE ON markups
    FOR EACH ROW
    EXECUTE FUNCTION update_calculator_settings_timestamp();

DROP TRIGGER IF EXISTS beveled_pricing_updated_at ON beveled_pricing;
CREATE TRIGGER beveled_pricing_updated_at
    BEFORE UPDATE ON beveled_pricing
    FOR EACH ROW
    EXECUTE FUNCTION update_calculator_settings_timestamp();

DROP TRIGGER IF EXISTS clipped_corners_pricing_updated_at ON clipped_corners_pricing;
CREATE TRIGGER clipped_corners_pricing_updated_at
    BEFORE UPDATE ON clipped_corners_pricing
    FOR EACH ROW
    EXECUTE FUNCTION update_calculator_settings_timestamp();

-- Verify setup
SELECT
    setting_key,
    setting_value,
    description,
    updated_at
FROM calculator_settings
ORDER BY setting_key;

COMMENT ON TABLE calculator_settings IS 'Global calculator constants editable by admins';
COMMENT ON COLUMN calculator_settings.setting_key IS 'Unique identifier for the setting';
COMMENT ON COLUMN calculator_settings.setting_value IS 'Numeric value of the setting';
COMMENT ON COLUMN calculator_settings.description IS 'Human-readable description of what this setting controls';
