# Session 16: Formula Configuration System

**Date:** 2025-11-04
**Status:** ✅ COMPLETE

## Overview

Implemented a comprehensive pricing formula configuration system that allows admin users to customize the final pricing calculation formula in the glass calculator. The system supports three modes (divisor, multiplier, custom expressions), component toggles, validation, and audit logging.

## What Was Built

### 1. Database Schema (`006_pricing_formula_config.sql`)
- **pricing_formula_config table**: Stores formula configuration
  - Three modes: divisor, multiplier, custom
  - Component enable/disable toggles
  - Active configuration tracking
  - Audit trail support

- **pricing_formula_audit table**: Logs all formula changes
  - Tracks who changed what and when
  - Stores old/new values as JSONB
  - Automatic trigger-based logging

### 2. Database Methods (`modules/database.py`)
- `get_pricing_formula_config()`: Retrieve active formula config
- `update_pricing_formula_config()`: Update formula settings
- `get_formula_audit_log()`: Retrieve change history
- Updated `get_calculator_config()` to include formula config

### 3. Calculator Engine (`modules/glass_calculator.py`)
- **Formula validation**: `validate_custom_formula()`
  - Security checks (no imports, eval, etc.)
  - Syntax validation
  - Safe evaluation with restricted namespace
  - Result validation (numeric, positive, finite)

- **Formula application**: `apply_pricing_formula()`
  - Divisor mode: `total ÷ divisor`
  - Multiplier mode: `total × multiplier`
  - Custom mode: Safe eval of expression
  - Automatic fallback on errors

- **Component toggles**: Respects enable/disable flags
  - Base price, polish, beveled, clipped corners
  - Tempered markup, shape markup
  - Contractor discount

### 4. User Interface (`pages/pricing_settings.py`)
- **New "Pricing Formula" tab** with:
  - Formula mode selector (radio buttons)
  - Mode-specific inputs (divisor/multiplier/custom)
  - Real-time formula validation
  - Live preview with example calculation
  - Component enable/disable toggles
  - Save button with confirmation

- **Interactive features**:
  - Show/hide inputs based on selected mode
  - Real-time validation messages
  - Example calculation updates as you type
  - Warning alerts for critical changes

## Formula Modes

### Divisor Mode (Default)
```
Quote Price = Total ÷ 0.28
```
- Maintains backward compatibility
- Default divisor: 0.28 (~257% markup)
- Adjustable from 0.01 to 1.0

### Multiplier Mode
```
Quote Price = Total × 3.5714
```
- Alternative way to express markup
- Default: 3.5714 (equivalent to ÷ 0.28)
- Adjustable from 1.0 to 10.0

### Custom Expression Mode
```
Quote Price = [custom expression]
```
- Write custom Python expressions
- Use `total` as variable
- Allowed: `+`, `-`, `*`, `/`, `()`, `abs()`, `min()`, `max()`, `round()`
- Examples:
  - `total * 3.5 + 10` (markup + flat fee)
  - `max(total * 3, 100)` (minimum $100)
  - `total * (1 + 0.28)` (28% markup)

## Component Toggles

Each pricing component can be independently enabled/disabled:
- Base Price (sq ft calculation)
- Polish Edges
- Beveled Edges
- Clipped Corners
- Tempered Markup
- Shape Markup
- Contractor Discount

**Use case:** Disable contractor discount to remove that feature entirely, or disable tempered markup to charge tempered glass at base price.

## Safety Features

### 1. Formula Validation
- Blocks dangerous operations (import, eval, exec, file access)
- Prevents division by zero
- Ensures numeric results
- No negative or infinite values
- Real-time feedback in UI

### 2. Audit Logging
- Every formula change is logged
- Tracks: what changed, who changed it, when
- Stores both old and new values
- Queryable for compliance/debugging

### 3. Access Control
- Only Owner and Admin roles can access
- Session validation required
- User ID tracked on all changes

### 4. Fallback Safety
- If custom formula fails, uses default (÷ 0.28)
- If divisor is zero, uses default
- Validation before saving prevents bad formulas

## Testing

Created comprehensive test suite (`test_formula_config.py`):

✅ **All tests passing:**
1. Default divisor mode (backward compatible)
2. Multiplier mode (equivalent results)
3. Custom formula (flexible calculations)
4. Disabled components (no polish, no tempered)
5. Formula validation (security & syntax)

**Test Results:**
- Divisor & Multiplier produce same result (✓)
- Custom formula calculates correctly (✓)
- Disabled components = $0 (✓)
- 10/10 validation tests pass (✓)

## Files Created/Modified

### New Files
- `database/migrations/006_pricing_formula_config.sql`
- `test_formula_config.py`
- `FORMULA_CONFIGURATION_GUIDE.md`
- `docs/sessions/SESSION_16_FORMULA_CONFIGURATION.md`

### Modified Files
- `modules/database.py` (+170 lines)
  - Added 3 new methods for formula config
  - Updated get_calculator_config()

- `modules/glass_calculator.py` (+126 lines)
  - Added validate_custom_formula()
  - Added apply_pricing_formula()
  - Updated __init__() to load formula config
  - Modified calculate_quote() to respect component toggles

- `pages/pricing_settings.py` (+549 lines)
  - Added "Pricing Formula" tab
  - Added load_pricing_formula() callback
  - Added 4 interactive callbacks:
    - toggle_formula_inputs()
    - validate_custom_expression()
    - update_formula_preview()
    - save_formula_config()

## Usage Instructions

### For End Users (Admin/Owner)

1. **Navigate to Settings**
   - Log in as Owner or Admin
   - Go to Pricing Settings
   - Click "Pricing Formula" tab

2. **Choose Formula Mode**
   - Divisor: Traditional method (÷ 0.28)
   - Multiplier: Alternative method (× 3.5714)
   - Custom: Write your own expression

3. **Adjust Values**
   - Enter new divisor/multiplier
   - OR write custom expression
   - Watch preview update in real-time

4. **Configure Components**
   - Toggle any components on/off
   - Disabled = always $0

5. **Save Changes**
   - Click "Save Formula Configuration"
   - Changes take effect immediately
   - All quotes use new formula

### For Developers

1. **Run Migration**
   ```bash
   # Via Supabase SQL Editor or psql
   psql -f database/migrations/006_pricing_formula_config.sql
   ```

2. **Calculator Usage**
   ```python
   from modules.database import Database
   from modules.glass_calculator import GlassPriceCalculator

   db = Database()
   config = db.get_calculator_config()  # Now includes formula_config
   calc = GlassPriceCalculator(config)

   result = calc.calculate_quote(...)  # Uses configured formula
   ```

3. **Custom Formula Examples**
   ```python
   # Flat markup + fee
   "total * 3.5 + 15"

   # Minimum quote
   "max(total * 3, 100)"

   # Tiered pricing
   "total * 4 if total < 100 else total * 3.5"  # Note: Not supported yet
   ```

## Future Enhancements (Optional)

1. **Tiered Pricing**: Support `if/else` in custom expressions
2. **Formula History**: View/restore previous formulas
3. **Formula Templates**: Save named formulas for quick switching
4. **Testing Mode**: Preview formula on historical quotes
5. **Role-based Restrictions**: Require Owner approval for changes
6. **Scheduled Changes**: Set formula to change at future date
7. **A/B Testing**: Compare two formulas side-by-side

## Migration Checklist

Before deploying to production:

- [ ] Run database migration `006_pricing_formula_config.sql`
- [ ] Verify default config is inserted
- [ ] Test formula calculations
- [ ] Train admin users on new UI
- [ ] Document company's formula strategy
- [ ] Set up monitoring for formula changes
- [ ] Test audit log functionality

## Key Learnings

1. **Safe Evaluation**: Python's `eval()` can be made safe with:
   - Restricted namespace (`__builtins__: {}`)
   - Pattern matching for dangerous operations
   - Result validation

2. **UI/UX**: Real-time preview and validation are critical for:
   - Building user confidence
   - Preventing errors
   - Understanding formula impact

3. **Flexibility vs. Safety**: Balance between:
   - Powerful customization (custom expressions)
   - Safe defaults (fallback to 0.28)
   - User-friendly modes (divisor/multiplier)

4. **Audit Trail**: Essential for:
   - Compliance and accountability
   - Debugging pricing issues
   - Understanding formula history

## Summary

Successfully implemented a comprehensive, secure, and user-friendly formula configuration system. The system:

✅ Maintains backward compatibility (default ÷ 0.28)
✅ Offers flexible formula modes
✅ Validates for security and correctness
✅ Provides real-time feedback
✅ Logs all changes for audit
✅ Allows component-level control
✅ All tests passing

**Impact:** Finance team can now adjust pricing formulas without code changes, experiment with different markup strategies, and disable specific pricing components as needed.

## Related Sessions
- Session 14: Calculator validation and settings
- Session 15: Calculator audit and pricing structure

## Next Steps
- Deploy migration to production
- Train admin users
- Monitor formula usage
- Gather feedback on UI/UX
