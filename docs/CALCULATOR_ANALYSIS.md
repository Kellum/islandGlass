# Glass Calculator Analysis & Integration Plan

**Date**: November 13, 2025
**Status**: Analysis Complete - Ready for Integration
**Source**: `/Users/ryankellum/claude-proj/islandGlassLeads/_old-app/`

---

## 📋 EXECUTIVE SUMMARY

The existing glass calculator is a **sophisticated pricing tool** with:
- ✅ Real-time price calculations
- ✅ Complex formula system with validation
- ✅ Multiple glass types, thicknesses, and edge processing options
- ✅ Contractor discounts
- ✅ Minimum square footage billing
- ✅ Custom shape support (rectangular, circular, non-rectangular)
- ✅ Dynamic form validation with business rules

**Integration Complexity**: Medium
**Estimated Time**: 4-6 hours
**Approach**: Port Python logic to TypeScript, create React component

---

## 🧮 CALCULATOR FORMULA BREAKDOWN

### Core Formula (The "Ultimate Formula")

```
FINAL QUOTE PRICE = Total ÷ 0.28
```

Where `Total` is calculated through multiple steps:

### Step-by-Step Calculation

1. **Square Footage**
   ```
   Rectangular: (width × height) ÷ 144
   Circular: (π × radius²) ÷ 144
   Minimum: 3.0 sq ft (configurable)
   ```

2. **Base Price**
   ```
   base_price = billable_sq_ft × base_rate
   (base_rate varies by thickness + glass_type)
   ```

3. **Perimeter** (for edge work)
   ```
   Rectangular: 2 × (width + height)
   Circular: π × diameter
   ```

4. **Edge Processing Costs**
   ```
   Polish: perimeter × polish_rate
   Beveled: perimeter × beveled_rate
   Clipped Corners: num_corners × clip_rate
   ```

5. **Before Markups**
   ```
   before_markups = base_price + polish + beveled + clipped_corners
   ```

6. **Markups**
   ```
   Tempered: before_markups × 0.35 (35%)
   Shape (non-rectangular/circular): before_markups × 0.25 (25%)
   ```

7. **Subtotal**
   ```
   subtotal = before_markups + tempered + shape
   ```

8. **Discounts**
   ```
   Contractor Discount: subtotal × 0.15 (15%)
   discounted_subtotal = subtotal - discount
   ```

9. **Total**
   ```
   total = discounted_subtotal × quantity
   ```

10. **Final Quote Price**
    ```
    quote_price = total ÷ markup_divisor (default: 0.28)
    ```

---

## 📐 GLASS CONFIGURATION

### Supported Glass Types
1. **Clear Glass** - Standard transparent
2. **Bronze** - Tinted bronze
3. **Gray** - Tinted gray
4. **Mirror** - Reflective mirror glass

### Supported Thicknesses
- 1/8"
- 3/16"
- 1/4"
- 3/8"
- 1/2"

### Pricing Matrix
Each combination of (thickness + glass_type) has:
- `base_price` - per sq ft rate
- `polish_price` - per inch of perimeter rate

Example from database:
```
1/4"_clear:
  base_price: 4.25
  polish_price: 0.25

1/2"_mirror:
  base_price: 18.50
  polish_price: 0.27 (flat rate for mirrors)
```

---

## 🔧 EDGE PROCESSING OPTIONS

### 1. Polished Edges
- **Cost**: `perimeter × polish_rate`
- **Rate varies** by thickness/type
- **Mirrors**: Use flat polish rate (0.27)
- **Disabled for**: 1/8" glass

### 2. Beveled Edges
- **Cost**: `perimeter × beveled_rate`
- **Rates** vary by thickness:
  - 1/4": $0.45/inch
  - 3/8": $0.50/inch
  - 1/2": $0.55/inch
- **Disabled for**: 1/8" glass

### 3. Clipped Corners
- **Cost**: `num_corners × clip_rate`
- **Rates** vary by thickness and clip size:
  - Under 1": $5-8 per corner
  - Over 1": $8-12 per corner
- **Disabled for**: Circular glass, Mirrors

---

## 🚫 BUSINESS RULES & VALIDATION

### Rule 1: 1/8" Glass Restrictions
```
IF thickness == "1/8"":
  - CANNOT be tempered
  - CANNOT have polished edges
  - CANNOT have beveled edges
  - CANNOT be mirror type
```

### Rule 2: Mirror Restrictions
```
IF glass_type == "mirror":
  - CANNOT be tempered
  - CANNOT have clipped corners
  - Uses flat polish rate (0.27)
```

### Rule 3: Circular Glass Restrictions
```
IF shape == "circular":
  - CANNOT have clipped corners
  - Uses diameter instead of width/height
  - Perimeter = π × diameter
```

### Rule 4: Minimum Square Footage
```
IF actual_sq_ft < 3.0:
  billable_sq_ft = 3.0
  (3 sq ft minimum charge)
```

---

## 📊 CONFIGURATION SYSTEM

The calculator uses a database-driven configuration system with 4 main tables:

### 1. `calculator_glass_config`
Stores base pricing for each thickness/type combination
```sql
thickness | glass_type | base_price | polish_price
'1/4"'    | 'clear'    | 4.25      | 0.25
```

### 2. `calculator_beveled_pricing`
Stores beveled edge rates by thickness
```sql
thickness | rate_per_inch
'1/4"'    | 0.45
```

### 3. `calculator_clipped_corners_pricing`
Stores clipped corner rates by thickness and size
```sql
thickness | clip_size  | rate_per_corner
'1/4"'    | 'under_1'  | 6.00
```

### 4. `calculator_settings`
Stores system-wide constants
```sql
setting_key              | value
'minimum_sq_ft'          | 3.0
'markup_divisor'         | 0.28
'contractor_discount_rate'| 0.15
'flat_polish_rate'       | 0.27
```

### 5. `calculator_pricing_formula` (NEW!)
Stores configurable formula modes
```sql
formula_mode            | divisor | multiplier | custom_expression
'divisor'               | 0.28    | null       | null
'multiplier'            | null    | 3.5714     | null
'custom'                | null    | null       | 'total * 3.5 + 10'
```

---

## 🎨 UI/UX FEATURES

### Two-Column Layout
- **Left (60%)**: Input form with accordions
- **Right (40%)**: Sticky price summary with real-time updates

### Progressive Disclosure
- **Accordions** for advanced options:
  - Edge Processing (polish, beveled, clipped corners)
  - Additional Options (tempered)
- **Dynamic fields**:
  - Diameter input (shows only for circular)
  - Clip size selector (shows only when corners > 0)

### Real-Time Updates
- Price updates as user types
- Live validation feedback
- Minimum sq ft warning
- Disabled controls auto-uncheck
- Glass type options update based on thickness

### Input Validation
- **Fractions supported**: "24 1/2", "36 3/4"
- **Decimals supported**: "24.5", "36.75"
- **Whole numbers**: "24", "36"
- Parser handles all formats

---

## 💾 DATA FLOW

### Existing (Python/Dash)
```
User Input
  ↓
Dash Callbacks (calculator.py)
  ↓
GlassPriceCalculator (glass_calculator.py)
  ↓
Database Config (Supabase)
  ↓
Calculate Result
  ↓
Display UI
```

### Proposed (React/TypeScript)
```
User Input (React Form)
  ↓
React State Management
  ↓
Calculator Service (TypeScript port of glass_calculator.py)
  ↓
Backend API (GET /api/v1/calculator/config)
  ↓
Calculate Result (Client-side)
  ↓
Display UI (React Components)
```

**OR** (Backend calculation approach):
```
User Input (React Form)
  ↓
POST /api/v1/calculator/quote
  ↓
Python GlassPriceCalculator (existing)
  ↓
Return Result
  ↓
Display UI (React Components)
```

---

## 🔄 INTEGRATION OPTIONS

### Option A: Frontend-Only (Client-Side Calculation)
**Pros:**
- ✅ Real-time updates (no API delay)
- ✅ Works offline
- ✅ Reduced server load
- ✅ Faster user experience

**Cons:**
- ❌ Need to port Python logic to TypeScript
- ❌ Duplicate code (Python + TypeScript)
- ❌ Formula updates require frontend deploy
- ❌ More complex TypeScript code

**Estimated Time:** 6 hours

### Option B: Backend API (Server-Side Calculation)
**Pros:**
- ✅ Reuse existing Python calculator
- ✅ Single source of truth for formulas
- ✅ Easy to update formulas (just backend)
- ✅ Less TypeScript complexity

**Cons:**
- ❌ API latency on every input change
- ❌ Requires backend API endpoint
- ❌ No offline support
- ❌ Higher server load

**Estimated Time:** 4 hours

### Option C: Hybrid (Recommended)
**Pros:**
- ✅ Backend API for initial config fetch
- ✅ Frontend TypeScript for calculations
- ✅ Real-time updates without API calls
- ✅ Offline-capable after config load
- ✅ Best of both worlds

**Cons:**
- ❌ Moderate complexity
- ❌ TypeScript calculator still needed

**Estimated Time:** 5 hours

---

## 🎯 RECOMMENDED APPROACH

### Phase 1: Backend API Setup (1 hour)
1. Create `/api/v1/calculator/config` endpoint
   - Returns: glass_config, markups, beveled_pricing, clipped_corners_pricing, settings, formula_config
   - Same format as Python `get_calculator_config()`

2. Test endpoint with existing test data

### Phase 2: TypeScript Calculator Port (2 hours)
1. Create `/frontend/src/services/calculator.ts`
2. Port `GlassPriceCalculator` class to TypeScript
3. Implement all calculation methods
4. Add TypeScript types for all interfaces

### Phase 3: React Calculator Component (2 hours)
1. Create `/frontend/src/pages/Calculator.tsx`
2. Two-column layout (form + price summary)
3. All input fields with validation
4. Real-time price updates (using TypeScript calculator)
5. Accordion sections for advanced options
6. Business rules validation (disable controls)

### Phase 4: Testing & Refinement (1 hour)
1. Test all glass types and thicknesses
2. Verify formulas match Python version
3. Test edge cases (minimums, circular, mirrors)
4. Polish UI/UX

**Total Estimated Time:** 6 hours

---

## 📝 TECHNICAL REQUIREMENTS

### Backend (New API Endpoint)
```python
# /backend/routers/calculator.py

@router.get("/config")
def get_calculator_config(current_user: dict = Depends(get_current_user)):
    """
    Get calculator configuration including:
    - Glass pricing (base + polish rates)
    - Beveled pricing
    - Clipped corners pricing
    - System settings (minimum sq ft, markup divisor, etc.)
    - Formula configuration
    """
    db = Database()
    config = db.get_calculator_config()
    return config
```

### Frontend (TypeScript Calculator)
```typescript
// /frontend/src/services/calculator.ts

interface CalculatorConfig {
  glass_config: Record<string, {base_price: number; polish_price: number}>;
  markups: {tempered: number; shape: number};
  beveled_pricing: Record<string, number>;
  clipped_corners_pricing: Record<string, Record<string, number>>;
  settings: {
    minimum_sq_ft: number;
    markup_divisor: number;
    contractor_discount_rate: number;
    flat_polish_rate: number;
  };
  formula_config: {
    formula_mode: 'divisor' | 'multiplier' | 'custom';
    divisor_value: number;
    multiplier_value: number;
    custom_expression: string | null;
  };
}

class GlassPriceCalculator {
  constructor(private config: CalculatorConfig) {}

  calculateQuote(params: QuoteParams): QuoteResult {
    // Port Python logic here
  }
}
```

### Frontend (React Component)
```tsx
// /frontend/src/pages/Calculator.tsx

export default function Calculator() {
  const [config, setConfig] = useState<CalculatorConfig>();
  const [formData, setFormData] = useState<FormData>(initialState);

  // Fetch config on mount
  useEffect(() => {
    fetch('/api/v1/calculator/config')
      .then(res => res.json())
      .then(setConfig);
  }, []);

  // Calculate price on every form change
  const result = useMemo(() => {
    if (!config) return null;
    const calculator = new GlassPriceCalculator(config);
    return calculator.calculateQuote(formData);
  }, [config, formData]);

  return (
    <div className="grid grid-cols-7 gap-6">
      <div className="col-span-4">{/* Form */}</div>
      <div className="col-span-3 sticky top-4">{/* Price Summary */}</div>
    </div>
  );
}
```

---

## 🎨 UI COMPONENT HIERARCHY

```
Calculator Page
├── Header (Title + Badge)
├── Grid Container (7 columns)
│   ├── Form Section (4 columns)
│   │   ├── Basic Info
│   │   │   ├── PO/Job Name Input
│   │   │   └── Contractor Checkbox
│   │   ├── Dimensions
│   │   │   ├── Width Input
│   │   │   ├── Height Input
│   │   │   ├── Quantity Input
│   │   │   └── Minimum Warning Alert
│   │   ├── Glass Configuration
│   │   │   ├── Glass Type Select
│   │   │   └── Thickness Select
│   │   ├── Shape Selection
│   │   │   ├── Segmented Control
│   │   │   └── Diameter Input (conditional)
│   │   ├── Edge Processing Accordion
│   │   │   ├── Polish Checkbox
│   │   │   ├── Beveled Checkbox
│   │   │   ├── Clipped Corners Number
│   │   │   └── Clip Size Select (conditional)
│   │   └── Additional Options Accordion
│   │       └── Tempered Checkbox
│   └── Price Summary (3 columns, sticky)
│       ├── Area Badge
│       ├── Base Price
│       ├── Edge Work (conditional)
│       ├── Markups (conditional)
│       ├── Discount (conditional)
│       ├── Divider
│       ├── Final Quote Price
│       └── Calculate Button
└── Results Container (full width)
    └── Detailed Breakdown Card (after calculate)
```

---

## 🧪 TEST CASES

### Test Case 1: Basic Clear Glass
```
Input:
  - Width: 24"
  - Height: 36"
  - Type: Clear
  - Thickness: 1/4"
  - Quantity: 1

Expected:
  - Sq Ft: 6.0
  - Base: $25.50 (6.0 × 4.25)
  - Quote: $91.07 ($25.50 ÷ 0.28)
```

### Test Case 2: Mirror with Polish
```
Input:
  - Width: 30"
  - Height: 40"
  - Type: Mirror
  - Thickness: 1/4"
  - Polish: Yes

Expected:
  - Sq Ft: 8.33
  - Base: $83.33
  - Polish: $37.80 (140" × 0.27)
  - Quote: $432.61 ($121.13 ÷ 0.28)
```

### Test Case 3: Below Minimum
```
Input:
  - Width: 12"
  - Height: 12"
  - Type: Clear
  - Thickness: 1/4"

Expected:
  - Actual: 1.0 sq ft
  - Billable: 3.0 sq ft (minimum)
  - Base: $12.75 (3.0 × 4.25)
  - Warning: "1.00 sq ft - Minimum charge of 3 sq ft applies"
```

### Test Case 4: Circular Glass
```
Input:
  - Shape: Circular
  - Diameter: 24"
  - Type: Clear
  - Thickness: 1/4"
  - Polish: Yes

Expected:
  - Sq Ft: 3.14
  - Perimeter: 75.40"
  - Base: $13.35
  - Polish: $18.85
  - Shape Markup: 25%
  - Quote: $153.06
```

---

## 📚 REFERENCE FILES

### Existing Code (Python)
- `/pages-backup-v1/calculator.py` - UI layout
- `/modules/glass_calculator.py` - Core calculation logic
- `/modules/fraction_utils.py` - Input parsing
- `/modules/database.py` - Config fetching

### Database Schema
- `/database/archive/setup_glass_calculator.sql` - Table definitions
- Tables: calculator_glass_config, calculator_beveled_pricing, calculator_clipped_corners_pricing, calculator_settings, calculator_pricing_formula

### React Version (Reference)
- `/GlassPricePro/client/src/components/ig-quote-calculator.tsx`
- `/GlassPricePro/client/src/components/calculator-form.tsx`

---

## ✅ NEXT STEPS

1. **Create Backend API Endpoint** (30 min)
   - GET /api/v1/calculator/config
   - Test with Postman

2. **Port Calculator to TypeScript** (2 hours)
   - Create calculator.ts service
   - Implement all calculation methods
   - Add comprehensive TypeScript types

3. **Build React Component** (2 hours)
   - Create Calculator.tsx page
   - Two-column layout with Tailwind
   - All form inputs with validation
   - Real-time price updates

4. **Test & Refine** (1 hour)
   - Test all scenarios
   - Verify formulas
   - Polish UI

**Total:** ~6 hours for full integration

---

**Status**: ✅ Analysis Complete - Ready to Build!
**Complexity**: Medium
**Priority**: High (Core business functionality)
