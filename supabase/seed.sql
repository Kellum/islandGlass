-- ============================================================
-- Island Glass Calculator - Seed Data
-- ============================================================

-- Suppliers
INSERT INTO suppliers (name)
VALUES
  ('Crystal Tempering'),
  ('M & F'),
  ('Aldora'),
  ('Cardinal')
ON CONFLICT (name) DO NOTHING;

-- Glass Configuration (wholesale costs)
INSERT INTO glass_config (thickness, type, base_price, polish_price, only_tempered, no_polish, never_tempered)
VALUES
  ('1/8"', 'clear', 8.50, 0.65, FALSE, TRUE, TRUE),
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
ON CONFLICT (thickness, type) DO NOTHING;

-- Markups
INSERT INTO markups (name, percentage)
VALUES
  ('tempered', 35.0),
  ('shape', 25.0)
ON CONFLICT (name) DO NOTHING;

-- Beveled Edge Pricing
INSERT INTO beveled_pricing (glass_thickness, price_per_inch)
VALUES
  ('3/16"', 1.50),
  ('1/4"', 2.01),
  ('3/8"', 2.91),
  ('1/2"', 3.80)
ON CONFLICT (glass_thickness) DO NOTHING;

-- Clipped Corners Pricing
INSERT INTO clipped_corners_pricing (glass_thickness, clip_size, price_per_corner)
VALUES
  ('1/4"', 'under_1', 5.50),
  ('1/4"', 'over_1', 22.18),
  ('3/8"', 'under_1', 7.50),
  ('3/8"', 'over_1', 30.00),
  ('1/2"', 'under_1', 9.00),
  ('1/2"', 'over_1', 35.00)
ON CONFLICT (glass_thickness, clip_size) DO NOTHING;

-- Calculator Settings
INSERT INTO calculator_settings (key, value)
VALUES
  ('minimum_sq_ft', 3.0),
  ('markup_divisor', 0.28),
  ('contractor_discount_rate', 0.15),
  ('flat_polish_rate', 0.27)
ON CONFLICT (key) DO NOTHING;

-- Pricing Formula Config (active)
INSERT INTO pricing_formula_config (
  formula_mode, divisor_value, multiplier_value, custom_expression,
  enable_base_price, enable_polish, enable_beveled, enable_clipped_corners,
  enable_tempered_markup, enable_shape_markup, enable_contractor_discount,
  is_active
)
VALUES (
  'divisor', 0.28, 3.5714, NULL,
  TRUE, TRUE, TRUE, TRUE,
  TRUE, TRUE, TRUE,
  TRUE
);

-- Admin config - default PIN "1234" hashed with SHA-256
-- SHA-256("1234") = 03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4
INSERT INTO admin_config (pin_hash)
VALUES ('03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4');
