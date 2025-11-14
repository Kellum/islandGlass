# Pricing Formula Configuration Guide

## Overview

The pricing formula configuration system allows authorized users (Owner and Admin roles) to customize how the final quote price is calculated from the combined cost in the glass calculator.

## Accessing Formula Settings

1. Log in as Owner or Admin
2. Navigate to **Settings** → **Pricing Settings**
3. Click the **Pricing Formula** tab

## Formula Modes

### 1. Divisor Mode (Default)
**Formula:** `Quote Price = Total ÷ Divisor`

- Default divisor: **0.28** (~257% markup)
- Use when you think in terms of "divide by a fraction"
- Example: $100 ÷ 0.28 = $357.14

**When to use:** Traditional markup method, maintaining the current formula.

### 2. Multiplier Mode
**Formula:** `Quote Price = Total × Multiplier`

- Default multiplier: **3.5714** (equivalent to ÷ 0.28)
- Use when you think in terms of "multiply by a factor"
- Example: $100 × 3.5714 = $357.14

**When to use:** When you prefer thinking in multiples rather than divisions.

### 3. Custom Expression Mode
**Formula:** Write your own Python expression

- Use `total` as the variable name
- Allowed operations: `+`, `-`, `*`, `/`, `()`
- Allowed functions: `abs()`, `min()`, `max()`, `round()`
- Example expressions:
  - `total * 3.5 + 10` (multiplier plus flat fee)
  - `total * 4.0` (simple 4x markup)
  - `max(total * 3.5, 100)` (minimum quote of $100)
  - `total * (1 + 0.28)` (28% markup)

**When to use:** Complex pricing strategies, tiered pricing, minimum charges.

## Formula Components

You can enable/disable specific components of the calculation:

- **Base Price**: Square footage × base rate
- **Polish Edges**: Perimeter × polish rate
- **Beveled Edges**: Perimeter × bevel rate
- **Clipped Corners**: Number of corners × corner rate
- **Tempered Markup**: Percentage markup for tempered glass
- **Shape Markup**: Percentage markup for non-rectangular shapes
- **Contractor Discount**: Discount percentage for contractors

**Example Use Cases:**
- Disable "Contractor Discount" to remove that feature entirely
- Disable "Tempered Markup" to charge tempered glass at base price
- Disable "Polish Edges" to make polishing free

## Safety Features

### Formula Validation
All custom expressions are validated for:
- Security (no dangerous operations like `import`, `eval`, `exec`)
- Valid syntax
- Numeric results
- No division by zero
- No negative results

### Audit Trail
All formula changes are logged with:
- What changed (mode, values, components)
- Who made the change
- When the change occurred
- Old and new values

### Real-time Preview
As you adjust formula settings, you'll see:
- Example calculation with $100 combined cost
- Resulting quote price
- Formula validation status (for custom expressions)

## Example Scenarios

### Scenario 1: Increase Overall Markup
**Current:** ÷ 0.28 (257% markup)
**New:** ÷ 0.25 (300% markup)

1. Select **Divisor Mode**
2. Change divisor from 0.28 to 0.25
3. Preview shows: $100 → $400
4. Click **Save Formula Configuration**

### Scenario 2: Flat Markup Plus Service Fee
**Goal:** 3.5x markup + $15 service fee

1. Select **Custom Expression**
2. Enter: `total * 3.5 + 15`
3. Preview shows: $100 → $365
4. Validation shows "Formula is valid!"
5. Click **Save**

### Scenario 3: Remove Contractor Discounts
**Goal:** Stop offering contractor pricing

1. Scroll to **Formula Components**
2. Toggle **Contractor Discount** to OFF
3. All other components remain enabled
4. Click **Save**

## Migration Instructions

To apply the database migration:

```bash
# Connect to your Supabase database
# Run the migration file:
psql -h your-db-host -U your-user -d your-database -f database/migrations/006_pricing_formula_config.sql
```

Or use the Supabase dashboard:
1. Go to SQL Editor
2. Paste contents of `006_pricing_formula_config.sql`
3. Run the migration

## Technical Details

### Database Schema
- **Table:** `pricing_formula_config`
  - `formula_mode`: 'divisor', 'multiplier', or 'custom'
  - `divisor_value`: Value for divisor mode
  - `multiplier_value`: Value for multiplier mode
  - `custom_expression`: Python expression for custom mode
  - `enable_*`: Boolean flags for each component

- **Table:** `pricing_formula_audit`
  - Logs all formula changes
  - Links to user who made change
  - Stores old and new values as JSONB

### Code Changes
- **modules/glass_calculator.py**: Updated to support dynamic formulas
- **modules/database.py**: Added formula config CRUD methods
- **pages/pricing_settings.py**: New "Pricing Formula" tab with UI

## Support

For questions or issues:
- Check validation messages in the UI
- Review audit log for recent changes
- Test with formula preview before saving
- Contact system administrator

## Best Practices

1. **Test First**: Use the preview to verify your formula before saving
2. **Document Changes**: Know why you're changing the formula
3. **Communicate**: Tell staff when pricing formulas change
4. **Small Changes**: Make incremental adjustments rather than big jumps
5. **Monitor Impact**: Check actual quotes after changing formulas
6. **Keep History**: Don't delete audit logs - they're important for tracking

## Troubleshooting

**Problem:** Custom formula shows "Invalid expression"
**Solution:** Check syntax, use only allowed operations, ensure it returns a number

**Problem:** Quotes seem wrong after formula change
**Solution:** Check the preview, verify component toggles, review audit log

**Problem:** Can't save formula
**Solution:** Verify you're logged in as Owner/Admin, check all required fields

**Problem:** Formula doesn't seem to apply
**Solution:** Refresh the page, clear calculator cache, verify formula is saved
