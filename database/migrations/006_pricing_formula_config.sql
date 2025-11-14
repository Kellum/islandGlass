-- ============================================
-- Pricing Formula Configuration
-- Allows admins to customize the final pricing formula
-- ============================================

-- Create pricing_formula_config table
CREATE TABLE IF NOT EXISTS pricing_formula_config (
    id SERIAL PRIMARY KEY,
    formula_mode TEXT NOT NULL DEFAULT 'divisor' CHECK (formula_mode IN ('divisor', 'multiplier', 'custom')),
    divisor_value DECIMAL(10,4) DEFAULT 0.28,
    multiplier_value DECIMAL(10,4) DEFAULT 3.5714,
    custom_expression TEXT,

    -- Component toggles (enable/disable parts of the formula)
    enable_base_price BOOLEAN DEFAULT TRUE,
    enable_polish BOOLEAN DEFAULT TRUE,
    enable_beveled BOOLEAN DEFAULT TRUE,
    enable_clipped_corners BOOLEAN DEFAULT TRUE,
    enable_tempered_markup BOOLEAN DEFAULT TRUE,
    enable_shape_markup BOOLEAN DEFAULT TRUE,
    enable_contractor_discount BOOLEAN DEFAULT TRUE,

    -- Metadata
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    description TEXT DEFAULT 'Default pricing formula configuration',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id),

    -- Ensure only one active config per company
    CONSTRAINT unique_active_config UNIQUE (company_id, is_active)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pricing_formula_company ON pricing_formula_config(company_id);
CREATE INDEX IF NOT EXISTS idx_pricing_formula_active ON pricing_formula_config(is_active);

-- Insert default formula configuration
-- This matches the current "Ultimate Formula: Quote Price = Total ÷ 0.28"
INSERT INTO pricing_formula_config (
    formula_mode,
    divisor_value,
    multiplier_value,
    enable_base_price,
    enable_polish,
    enable_beveled,
    enable_clipped_corners,
    enable_tempered_markup,
    enable_shape_markup,
    enable_contractor_discount,
    description,
    is_active,
    company_id
)
VALUES (
    'divisor',
    0.28,
    3.5714,  -- Equivalent: 1 ÷ 0.28 ≈ 3.5714
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    'Default Island Glass pricing formula (Quote Price = Total ÷ 0.28)',
    TRUE,
    NULL
)
ON CONFLICT ON CONSTRAINT unique_active_config DO NOTHING;

-- Create trigger for automatic timestamp updates
DROP TRIGGER IF EXISTS pricing_formula_config_updated_at ON pricing_formula_config;
CREATE TRIGGER pricing_formula_config_updated_at
    BEFORE UPDATE ON pricing_formula_config
    FOR EACH ROW
    EXECUTE FUNCTION update_calculator_settings_timestamp();

-- Create audit log table for formula changes
CREATE TABLE IF NOT EXISTS pricing_formula_audit (
    id SERIAL PRIMARY KEY,
    formula_config_id INTEGER REFERENCES pricing_formula_config(id) ON DELETE CASCADE,
    change_type TEXT NOT NULL,
    old_value JSONB,
    new_value JSONB,
    changed_by UUID REFERENCES auth.users(id),
    changed_at TIMESTAMP DEFAULT NOW(),
    reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_formula_audit_config ON pricing_formula_audit(formula_config_id);
CREATE INDEX IF NOT EXISTS idx_formula_audit_time ON pricing_formula_audit(changed_at DESC);

-- Function to log formula changes
CREATE OR REPLACE FUNCTION log_pricing_formula_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Only log if specific fields changed
    IF OLD.formula_mode != NEW.formula_mode
       OR OLD.divisor_value != NEW.divisor_value
       OR OLD.multiplier_value != NEW.multiplier_value
       OR OLD.custom_expression IS DISTINCT FROM NEW.custom_expression THEN

        INSERT INTO pricing_formula_audit (
            formula_config_id,
            change_type,
            old_value,
            new_value,
            changed_by
        ) VALUES (
            NEW.id,
            'formula_update',
            jsonb_build_object(
                'mode', OLD.formula_mode,
                'divisor', OLD.divisor_value,
                'multiplier', OLD.multiplier_value,
                'custom', OLD.custom_expression
            ),
            jsonb_build_object(
                'mode', NEW.formula_mode,
                'divisor', NEW.divisor_value,
                'multiplier', NEW.multiplier_value,
                'custom', NEW.custom_expression
            ),
            NEW.updated_by
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for formula change logging
DROP TRIGGER IF EXISTS log_formula_changes ON pricing_formula_config;
CREATE TRIGGER log_formula_changes
    AFTER UPDATE ON pricing_formula_config
    FOR EACH ROW
    EXECUTE FUNCTION log_pricing_formula_change();

-- Verify setup
SELECT
    id,
    formula_mode,
    divisor_value,
    multiplier_value,
    description,
    is_active
FROM pricing_formula_config
WHERE is_active = TRUE;

COMMENT ON TABLE pricing_formula_config IS 'Configurable pricing formula settings for calculator';
COMMENT ON COLUMN pricing_formula_config.formula_mode IS 'Formula calculation mode: divisor (÷), multiplier (×), or custom expression';
COMMENT ON COLUMN pricing_formula_config.divisor_value IS 'Value to divide total by (e.g., 0.28)';
COMMENT ON COLUMN pricing_formula_config.multiplier_value IS 'Value to multiply total by (e.g., 3.5714)';
COMMENT ON COLUMN pricing_formula_config.custom_expression IS 'Custom Python expression for advanced formula (e.g., "total * 3.5 + 10")';
COMMENT ON TABLE pricing_formula_audit IS 'Audit trail for all pricing formula changes';
