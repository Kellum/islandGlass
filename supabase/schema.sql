-- ============================================================
-- Island Glass Calculator - Supabase Schema
-- Standalone calculator with simplified single-tenant schema
-- ============================================================

-- Suppliers (internal tracking)
CREATE TABLE IF NOT EXISTS suppliers (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Locations (store locations with configurable number for PO naming)
CREATE TABLE IF NOT EXISTS locations (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  location_number INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Glass Configuration (wholesale pricing)
CREATE TABLE IF NOT EXISTS glass_config (
  id SERIAL PRIMARY KEY,
  thickness TEXT NOT NULL,
  type TEXT NOT NULL,
  base_price NUMERIC(10,2) NOT NULL DEFAULT 0,
  polish_price NUMERIC(10,2) NOT NULL DEFAULT 0,
  only_tempered BOOLEAN NOT NULL DEFAULT FALSE,
  no_polish BOOLEAN NOT NULL DEFAULT FALSE,
  never_tempered BOOLEAN NOT NULL DEFAULT FALSE,
  supplier_id INTEGER REFERENCES suppliers(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(thickness, type)
);

-- Markup percentages (tempered, shape)
CREATE TABLE IF NOT EXISTS markups (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  percentage NUMERIC(10,2) NOT NULL DEFAULT 0
);

-- Beveled edge pricing by thickness
CREATE TABLE IF NOT EXISTS beveled_pricing (
  id SERIAL PRIMARY KEY,
  glass_thickness TEXT NOT NULL UNIQUE,
  price_per_inch NUMERIC(10,4) NOT NULL DEFAULT 0
);

-- Clipped corners pricing by thickness + clip size
CREATE TABLE IF NOT EXISTS clipped_corners_pricing (
  id SERIAL PRIMARY KEY,
  glass_thickness TEXT NOT NULL,
  clip_size TEXT NOT NULL DEFAULT 'under_1',
  price_per_corner NUMERIC(10,2) NOT NULL DEFAULT 0,
  UNIQUE(glass_thickness, clip_size)
);

-- Calculator system settings (key-value pairs)
CREATE TABLE IF NOT EXISTS calculator_settings (
  id SERIAL PRIMARY KEY,
  key TEXT NOT NULL UNIQUE,
  value NUMERIC(10,4) NOT NULL DEFAULT 0
);

-- Pricing formula configuration
CREATE TABLE IF NOT EXISTS pricing_formula_config (
  id SERIAL PRIMARY KEY,
  formula_mode TEXT NOT NULL DEFAULT 'divisor' CHECK (formula_mode IN ('divisor', 'multiplier', 'custom')),
  divisor_value NUMERIC(10,4) NOT NULL DEFAULT 0.28,
  multiplier_value NUMERIC(10,4) NOT NULL DEFAULT 3.5714,
  custom_expression TEXT,
  enable_base_price BOOLEAN NOT NULL DEFAULT TRUE,
  enable_polish BOOLEAN NOT NULL DEFAULT TRUE,
  enable_beveled BOOLEAN NOT NULL DEFAULT TRUE,
  enable_clipped_corners BOOLEAN NOT NULL DEFAULT TRUE,
  enable_tempered_markup BOOLEAN NOT NULL DEFAULT TRUE,
  enable_shape_markup BOOLEAN NOT NULL DEFAULT TRUE,
  enable_contractor_discount BOOLEAN NOT NULL DEFAULT TRUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Pricing formula audit log
CREATE TABLE IF NOT EXISTS pricing_formula_audit (
  id SERIAL PRIMARY KEY,
  table_name TEXT NOT NULL,
  record_id INTEGER,
  action TEXT NOT NULL,
  old_values JSONB,
  new_values JSONB,
  changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Admin config (PIN hash)
CREATE TABLE IF NOT EXISTS admin_config (
  id SERIAL PRIMARY KEY,
  pin_hash TEXT NOT NULL
);

-- ============================================================
-- Auto-update timestamp trigger
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER glass_config_updated_at
  BEFORE UPDATE ON glass_config
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- Row Level Security (RLS)
-- All tables readable by anon, writable by anon (MVP)
-- ============================================================
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE glass_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE markups ENABLE ROW LEVEL SECURITY;
ALTER TABLE beveled_pricing ENABLE ROW LEVEL SECURITY;
ALTER TABLE clipped_corners_pricing ENABLE ROW LEVEL SECURITY;
ALTER TABLE calculator_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE pricing_formula_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE pricing_formula_audit ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_config ENABLE ROW LEVEL SECURITY;

-- Read policies (anon can read all)
CREATE POLICY "anon_read_suppliers" ON suppliers FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_locations" ON locations FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_glass_config" ON glass_config FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_markups" ON markups FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_beveled" ON beveled_pricing FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_clipped" ON clipped_corners_pricing FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_settings" ON calculator_settings FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_formula" ON pricing_formula_config FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_audit" ON pricing_formula_audit FOR SELECT TO anon USING (true);
CREATE POLICY "anon_read_admin" ON admin_config FOR SELECT TO anon USING (true);

-- Write policies (anon can write all - PIN validated client-side for MVP)
CREATE POLICY "anon_write_suppliers" ON suppliers FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_write_locations" ON locations FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_write_glass_config" ON glass_config FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_write_markups" ON markups FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_write_beveled" ON beveled_pricing FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_write_clipped" ON clipped_corners_pricing FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_write_settings" ON calculator_settings FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_write_formula" ON pricing_formula_config FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_write_audit" ON pricing_formula_audit FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_write_admin" ON admin_config FOR ALL TO anon USING (true) WITH CHECK (true);

-- ============================================================
-- Quotes & Line Items (Save Quotes feature)
-- ============================================================

CREATE SEQUENCE IF NOT EXISTS quote_number_seq START WITH 1001;

CREATE TABLE IF NOT EXISTS quotes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quote_number INTEGER NOT NULL UNIQUE DEFAULT nextval('quote_number_seq'),
  po_number TEXT DEFAULT '',
  customer_first_name TEXT NOT NULL DEFAULT '',
  customer_last_name TEXT NOT NULL DEFAULT '',
  customer_phone TEXT DEFAULT '',
  customer_email TEXT DEFAULT '',
  customer_notes TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'draft',
  is_contractor BOOLEAN NOT NULL DEFAULT FALSE,
  subtotal NUMERIC(10,2) NOT NULL DEFAULT 0,
  discount_amount NUMERIC(10,2) NOT NULL DEFAULT 0,
  grand_total NUMERIC(10,2) NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ DEFAULT (now() + INTERVAL '30 days')
);

CREATE TABLE IF NOT EXISTS quote_line_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quote_id UUID NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
  sort_order INTEGER NOT NULL DEFAULT 0,
  description TEXT NOT NULL,
  form_data JSONB NOT NULL,
  result JSONB NOT NULL,
  line_total NUMERIC(10,2) NOT NULL DEFAULT 0,
  width_input TEXT DEFAULT '',
  height_input TEXT DEFAULT '',
  diameter_input TEXT DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER quotes_updated_at
  BEFORE UPDATE ON quotes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quote_line_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_all_quotes" ON quotes FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_line_items" ON quote_line_items FOR ALL TO anon USING (true) WITH CHECK (true);
