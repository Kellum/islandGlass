# Pricing Settings Setup Guide

This guide explains how to set up the new admin-editable pricing system.

## What's New

All calculator pricing formulas are now admin-editable through a web UI:
- **Glass Pricing** - Base prices and polish prices for each thickness/type
- **Markup Percentages** - Tempered and shape markup percentages
- **Edge Work Pricing** - Beveled edge and clipped corners rates
- **System Constants** - Minimum sq ft, markup divisor, contractor discount rate, flat polish rate

## Database Setup

### Step 1: Run the Migration

Execute the SQL migration in your Supabase SQL Editor:

```bash
# Location: database/migrations/005_calculator_system_settings.sql
```

This migration:
- Creates `calculator_settings` table for global constants
- Adds soft delete support to pricing tables
- Adds `updated_at` and `updated_by` tracking
- Inserts default system settings

### Step 2: Verify Tables Exist

Run this query in Supabase to verify setup:

```sql
-- Check if all required tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'glass_config',
    'markups',
    'beveled_pricing',
    'clipped_corners_pricing',
    'calculator_settings'
  )
ORDER BY table_name;

-- Verify default settings loaded
SELECT * FROM calculator_settings ORDER BY setting_key;
```

Expected output:
```
minimum_sq_ft:             3.0
markup_divisor:            0.28
contractor_discount_rate:  0.15
flat_polish_rate:          0.27
```

## Access Control

**Who can access Pricing Settings:**
- Users with role = `owner`
- Users with role = `ig_admin`

The page automatically checks permissions. Non-admin users will see "Access Denied".

## How to Use

### Accessing Pricing Settings

1. Log in as an admin user
2. Navigate to **Pricing Settings** in the sidebar (bottom, below Settings)
3. You'll see 4 tabs: Glass Pricing, Markups, Edge Work, System Constants

### Editing Glass Pricing

**Glass Pricing Tab:**
- Shows all glass types grouped by thickness
- Edit **Base Price** ($ per sq ft) and **Polish Price** ($ per inch)
- Click **Save** after making changes
- Changes take effect immediately

Example:
```
1/4" Glass
├── Clear:   Base: $12.50/sq ft,  Polish: $0.85/inch
├── Bronze:  Base: $18.00/sq ft,  Polish: $0.85/inch
├── Gray:    Base: $16.50/sq ft,  Polish: $0.85/inch
└── Mirror:  Base: $15.00/sq ft,  Polish: $0.27/inch (flat polish)
```

### Editing Markups

**Markups Tab:**
- **Tempered**: Percentage markup for tempered glass (default 35%)
- **Shape**: Percentage markup for non-rectangular shapes (default 25%)

These percentages are applied to the base price + edge work subtotal.

### Editing Edge Work Pricing

**Edge Work Tab:**

**Beveled Edge Pricing:**
- Price per inch of perimeter
- Available for 3/16", 1/4", 3/8", 1/2" glass

**Clipped Corners Pricing:**
- Price per corner
- Two sizes: "Under 1 inch" and "Over 1 inch"
- Available for 1/4", 3/8", 1/2" glass

### Editing System Constants

**System Constants Tab** - These affect ALL calculator pricing:

1. **Minimum Square Footage** (default: 3.0)
   - Minimum billable sq ft for all orders
   - Orders under this size still billed at minimum

2. **Markup Divisor** (default: 0.28)
   - Final quote price = Total ÷ this value
   - 0.28 = ~257% markup
   - Lower divisor = higher markup

3. **Contractor Discount Rate** (default: 0.15)
   - Contractor discount as decimal (0.15 = 15%)
   - Applied to subtotal before final markup

4. **Flat Polish Rate** (default: 0.27)
   - Price per inch for flat polish on mirrors
   - Mirrors use flat polish instead of regular polish

⚠️ **Warning:** Changes to System Constants affect all quotes globally!

## Technical Details

### Database Methods

New methods in `modules/database.py`:

```python
# Get all settings
db.get_calculator_settings() → Dict

# Update methods (all require user_id for audit trail)
db.update_calculator_setting(setting_key, setting_value, user_id)
db.update_glass_config(id, base_price, polish_price, user_id)
db.update_markup(name, percentage, user_id)
db.update_beveled_pricing(id, price_per_inch, user_id)
db.update_clipped_corners_pricing(id, price_per_corner, user_id)
```

### Calculator Integration

The `GlassPriceCalculator` class now loads settings from the database:

```python
# Old (hardcoded)
MINIMUM_SQ_FT = 3.0
MARKUP_DIVISOR = 0.28
CONTRACTOR_DISCOUNT_RATE = 0.15

# New (from database)
config = db.get_calculator_config()
calc = GlassPriceCalculator(config)
# Uses config['settings'] for all constants
```

### Audit Trail

All pricing changes are tracked:
- `updated_at` - Timestamp of last change
- `updated_by` - User ID who made the change

Query audit history:
```sql
SELECT
  thickness,
  type,
  base_price,
  polish_price,
  updated_at,
  updated_by
FROM glass_config
WHERE updated_at > NOW() - INTERVAL '7 days'
ORDER BY updated_at DESC;
```

## Testing Changes

### Test 1: Update a Glass Price

1. Go to **Pricing Settings** → **Glass Pricing**
2. Change 1/4" Clear base price from $12.50 to $13.00
3. Click **Save**
4. Go to **Glass Calculator**
5. Enter: 24" x 36" x 1/4" Clear glass
6. Verify new price is calculated with $13.00/sq ft base

### Test 2: Update System Constant

1. Go to **Pricing Settings** → **System Constants**
2. Change "Minimum Square Footage" from 3.0 to 2.5
3. Click **Save**
4. Go to **Glass Calculator**
5. Enter: 12" x 24" (2.0 sq ft)
6. Verify it now bills at 2.5 sq ft instead of 3.0 sq ft

### Test 3: Update Markup Percentage

1. Go to **Pricing Settings** → **Markups**
2. Change "Tempered" from 35% to 40%
3. Click **Save**
4. Go to **Glass Calculator**
5. Create quote with tempered glass
6. Verify tempered markup is now 40% of base+edges

## Rollback Plan

If you need to restore original pricing:

```sql
-- Reset to original system constants
UPDATE calculator_settings
SET setting_value = 3.0
WHERE setting_key = 'minimum_sq_ft';

UPDATE calculator_settings
SET setting_value = 0.28
WHERE setting_key = 'markup_divisor';

UPDATE calculator_settings
SET setting_value = 0.15
WHERE setting_key = 'contractor_discount_rate';

UPDATE calculator_settings
SET setting_value = 0.27
WHERE setting_key = 'flat_polish_rate';
```

For glass pricing, refer to the original seed data in:
`database/archive/setup_glass_calculator.sql`

## Troubleshooting

### Error: "No glass pricing configuration found"

**Cause:** Database tables not populated

**Fix:** Run the setup SQL:
```bash
database/archive/setup_glass_calculator.sql
```

### Error: "Table calculator_settings does not exist"

**Cause:** Migration not run

**Fix:** Run:
```bash
database/migrations/005_calculator_system_settings.sql
```

### Changes not taking effect in calculator

**Cause:** Browser cache or old config in memory

**Fix:**
1. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
2. Restart the Dash app
3. Verify changes saved: Check database directly

### "Access Denied" message

**Cause:** User role is not `owner` or `ig_admin`

**Fix:** Update user role:
```sql
UPDATE user_profiles
SET role = 'ig_admin'
WHERE user_id = 'YOUR_USER_ID';
```

## Future Enhancements

Potential additions:
- Price history tracking (changelog)
- Bulk import/export pricing via CSV
- Price effective dates (scheduled changes)
- Multi-location pricing (different rates per branch)
- Competitor price comparison
- Automatic price suggestions based on market data
