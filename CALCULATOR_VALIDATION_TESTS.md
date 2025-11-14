# Glass Calculator Validation Tests

## Test Cases for Missing Rules Implementation

This document outlines all validation rules that have been implemented to match the old GlassPricePro calculator.

---

## ✅ Test 1: 1/8" Glass Cannot Have ANY Edge Work

**Steps:**
1. Select thickness: `1/8"`
2. Select glass type: `clear`, `bronze`, or `gray`
3. Open "Edge Processing" accordion
4. Try to check "Polished Edges" checkbox
5. Try to check "Beveled Edges" checkbox
6. Try to check "Tempered Glass" checkbox

**Expected Results:**
- ✅ ALL edge work checkboxes should be **disabled** (greyed out):
  - Polished Edges: disabled
  - Beveled Edges: disabled
  - Tempered Glass: disabled
- ✅ If any were previously checked, they should be automatically **unchecked**
- ✅ Backend validation should reject if somehow submitted

**Rationale:** 1/8" glass is too thin for any edge processing (polish, bevel, or tempering).

---

## ✅ Test 2: 1/8" Mirror Is Not Available

**Steps:**
1. Select thickness: `1/8"`
2. Look at Glass Type dropdown

**Expected Results:**
- ✅ "Mirror" option should **not appear** in the dropdown
- ✅ Available options: Clear Glass, Bronze, Gray
- ✅ If mirror was previously selected, auto-switch to "clear"
- ✅ Backend validation should reject if somehow submitted

**Rationale:** 1/8" mirror glass is not stocked/available.

---

## ✅ Test 3: Mirrors Cannot Be Tempered

**Steps:**
1. Select glass type: `mirror` (any thickness except 1/8")
2. Try to check "Tempered Glass" checkbox

**Expected Results:**
- ✅ Tempered checkbox should be **disabled** (greyed out)
- ✅ If previously checked, it should be automatically **unchecked**
- ✅ Backend validation should reject if somehow submitted

**Rationale:** Mirror backing prevents tempering process.

---

## ✅ Test 4: Clipped Corners Only for Glass (Not Mirrors)

**Steps:**
1. Select glass type: `mirror`
2. Open "Edge Processing" accordion
3. Try to enter a value in "Clipped Corners" field

**Expected Results:**
- ✅ Clipped corners input should be **disabled** (greyed out)
- ✅ Value should be automatically set to `0`
- ✅ Backend validation should reject if somehow submitted

**Rationale:** Clipped corners are only available for regular glass, not mirrors.

---

## ✅ Test 5: Clipped Corners Not Available for Circular Glass

**Steps:**
1. Select shape: `Circular`
2. Open "Edge Processing" accordion
3. Try to enter a value in "Clipped Corners" field

**Expected Results:**
- ✅ Clipped corners input should be **disabled** (greyed out)
- ✅ Value should be automatically set to `0`
- ✅ Backend validation should reject if somehow submitted

**Rationale:** Circular glass has no corners to clip.

---

## 🔄 Test 6: Multiple Rule Interactions

**Test 6a: Switch from 1/4" Clear to 1/8" Clear**
1. Select 1/4" clear glass
2. Check "Polished", "Tempered" and "Beveled"
3. Switch thickness to 1/8"

**Expected Results:**
- ✅ All three checkboxes ("Polished", "Tempered", "Beveled") should auto-uncheck
- ✅ All three checkboxes should be disabled

**Test 6b: Switch from 1/4" Clear to Mirror**
1. Select 1/4" clear glass
2. Check "Tempered"
3. Enter "2" clipped corners
4. Switch glass type to "Mirror"

**Expected Results:**
- ✅ "Tempered" should auto-uncheck and disable
- ✅ "Clipped Corners" should reset to 0 and disable

**Test 6c: Switch from Rectangular to Circular**
1. Select rectangular shape
2. Enter "2" clipped corners
3. Switch shape to "Circular"

**Expected Results:**
- ✅ "Clipped Corners" should reset to 0 and disable

---

## 🎯 Test 7: Backend Validation (Failsafe)

Even if UI controls are bypassed, backend should reject invalid combinations:

**Invalid Combinations to Test:**
1. `1/8" clear + polished` → Should return error: "1/8" glass cannot be polished"
2. `1/8" clear + tempered` → Should return error: "1/8" glass cannot be tempered"
3. `1/8" clear + beveled` → Should return error: "1/8" glass cannot have beveled edges"
4. `1/8" + mirror` → Should return error: "1/8" mirror is not available"
5. `1/4" mirror + tempered` → Should return error: "Mirror glass cannot be tempered"
6. `1/4" mirror + clipped corners` → Should return error: "Clipped corners are not available for mirrors"
7. `Circular + clipped corners` → Should return error: "Clipped corners are not available for circular glass"

---

## 📊 Test 8: Pricing Accuracy

Verify that pricing calculations match old app:

**Test Configuration:**
- Width: 24"
- Height: 36"
- Thickness: 1/4"
- Glass Type: Clear
- Polished: Yes
- Tempered: Yes
- Contractor Discount: No

**Expected Calculation:**
1. Square footage: (24 × 36) ÷ 144 = 6 sq ft
2. Base price: 6 × $12.50 = $75.00
3. Perimeter: 2 × (24 + 36) = 120 inches
4. Polish: 120 × $0.85 = $102.00
5. Before markups: $75.00 + $102.00 = $177.00
6. Tempered markup (35%): $177.00 × 0.35 = $61.95
7. Subtotal: $177.00 + $61.95 = $238.95
8. Quote price: $238.95 ÷ 0.28 = **$853.39**

---

## 🔧 Manual Testing Checklist

Open the calculator at `http://localhost:8050/calculator` and verify:

- [ ] Test 1: 1/8" glass cannot have ANY edge work (polish, bevel, tempered)
- [ ] Test 2: 1/8" mirror is not available
- [ ] Test 3: Mirrors cannot be tempered
- [ ] Test 4: Mirrors cannot have clipped corners
- [ ] Test 5: Circular glass cannot have clipped corners
- [ ] Test 6a: Multiple rules work together (thickness change)
- [ ] Test 6b: Multiple rules work together (glass type change)
- [ ] Test 6c: Multiple rules work together (shape change)
- [ ] Test 7: Backend validation rejects invalid combinations
- [ ] Test 8: Pricing calculation is accurate

---

## 📝 Implementation Summary

### Files Modified:

1. **`pages/calculator.py`**
   - Added callback to disable controls based on selections
   - Added callback to auto-uncheck disabled controls
   - Added callback to filter glass types for 1/8" thickness
   - Added error handling for backend validation failures

2. **`modules/glass_calculator.py`**
   - Added `validate_quote_params()` method
   - Validation checks all 6 business rules
   - Returns error dict if validation fails

### Business Rules Implemented:

1. ✅ 1/8" glass cannot have ANY edge work (polished, beveled, or tempered)
2. ✅ 1/8" glass cannot be mirror
3. ✅ Mirrors cannot be tempered
4. ✅ Clipped corners only for glass (not mirrors)
5. ✅ Clipped corners not for circular glass

---

## 🎉 Success Criteria

All validation rules from the old GlassPricePro calculator are now implemented:
- UI prevents invalid selections
- Controls are disabled/hidden appropriately
- Invalid combinations are automatically corrected
- Backend validation provides failsafe protection
- User sees clear error messages
- Pricing calculations match old system exactly
