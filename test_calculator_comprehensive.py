"""
Comprehensive Calculator Testing Script
Tests all validation rules and pricing calculations
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from root .env
load_dotenv('/Users/ryankellum/claude-proj/islandGlassLeads/.env')

sys.path.insert(0, '/Users/ryankellum/claude-proj/islandGlassLeads')

from modules.glass_calculator import GlassPriceCalculator
from modules.database import Database


def print_test_header(test_name):
    """Print a formatted test header"""
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)


def print_result(passed, expected, actual, message=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {message}")
    if not passed:
        print(f"  Expected: {expected}")
        print(f"  Actual: {actual}")


def test_validation_rules():
    """Test all validation rules from CALCULATOR_VALIDATION_TESTS.md"""
    print_test_header("Validation Rules")

    # Get calculator config from database
    db = Database()
    config = db.get_calculator_config()
    calc = GlassPriceCalculator(config)

    # Test 1: 1/8" glass cannot have ANY edge work
    print("\n--- Test 1: 1/8\" Glass Cannot Have Edge Work ---")

    result = calc.calculate_quote(
        width=24, height=36, thickness='1/8"', glass_type='clear',
        is_polished=True
    )
    print_result(
        passed='error' in result,
        expected="Error message",
        actual=result.get('error', 'No error'),
        message="1/8\" glass + polished should error"
    )

    result = calc.calculate_quote(
        width=24, height=36, thickness='1/8"', glass_type='clear',
        is_beveled=True
    )
    print_result(
        passed='error' in result,
        expected="Error message",
        actual=result.get('error', 'No error'),
        message="1/8\" glass + beveled should error"
    )

    result = calc.calculate_quote(
        width=24, height=36, thickness='1/8"', glass_type='clear',
        is_tempered=True
    )
    print_result(
        passed='error' in result,
        expected="Error message",
        actual=result.get('error', 'No error'),
        message="1/8\" glass + tempered should error"
    )

    # Test 2: 1/8" mirror is not available
    print("\n--- Test 2: 1/8\" Mirror Not Available ---")

    result = calc.calculate_quote(
        width=24, height=36, thickness='1/8"', glass_type='mirror'
    )
    print_result(
        passed='error' in result,
        expected="Error message",
        actual=result.get('error', 'No error'),
        message="1/8\" mirror should error"
    )

    # Test 3: Mirrors cannot be tempered
    print("\n--- Test 3: Mirrors Cannot Be Tempered ---")

    result = calc.calculate_quote(
        width=24, height=36, thickness='1/4"', glass_type='mirror',
        is_tempered=True
    )
    print_result(
        passed='error' in result,
        expected="Error message",
        actual=result.get('error', 'No error'),
        message="Mirror + tempered should error"
    )

    # Test 4: Clipped corners only for glass (not mirrors)
    print("\n--- Test 4: Clipped Corners Not Available for Mirrors ---")

    result = calc.calculate_quote(
        width=24, height=36, thickness='1/4"', glass_type='mirror',
        num_clipped_corners=2
    )
    print_result(
        passed='error' in result,
        expected="Error message",
        actual=result.get('error', 'No error'),
        message="Mirror + clipped corners should error"
    )

    # Test 5: Clipped corners not available for circular glass
    print("\n--- Test 5: Clipped Corners Not Available for Circular Glass ---")

    result = calc.calculate_quote(
        width=24, height=36, thickness='1/4"', glass_type='clear',
        is_circular=True, diameter=24, num_clipped_corners=2
    )
    print_result(
        passed='error' in result,
        expected="Error message",
        actual=result.get('error', 'No error'),
        message="Circular + clipped corners should error"
    )


def test_pricing_accuracy():
    """Test pricing calculations match expected formulas"""
    print_test_header("Pricing Accuracy Tests")

    db = Database()
    config = db.get_calculator_config()
    calc = GlassPriceCalculator(config)

    # Test from CALCULATOR_VALIDATION_TESTS.md
    print("\n--- Expected Calculation Test ---")
    print("Configuration: 24\" x 36\", 1/4\" clear, polished, tempered")
    print("Expected calculation:")
    print("  1. Square footage: (24 × 36) ÷ 144 = 6 sq ft")
    print("  2. Base price: 6 × $12.50 = $75.00")
    print("  3. Perimeter: 2 × (24 + 36) = 120 inches")
    print("  4. Polish: 120 × $0.85 = $102.00")
    print("  5. Before markups: $75.00 + $102.00 = $177.00")
    print("  6. Tempered markup (35%): $177.00 × 0.35 = $61.95")
    print("  7. Subtotal: $177.00 + $61.95 = $238.95")
    print("  8. Quote price: $238.95 ÷ 0.28 = $853.39")

    result = calc.calculate_quote(
        width=24,
        height=36,
        thickness='1/4"',
        glass_type='clear',
        is_polished=True,
        is_tempered=True,
        is_contractor=False
    )

    print("\nActual results:")
    if 'error' in result:
        print(f"  ❌ ERROR: {result['error']}")
    else:
        print(f"  Square footage: {result['billable_sq_ft']} sq ft")
        print(f"  Base price: ${result['base_price']:.2f}")
        print(f"  Perimeter: {result['perimeter']}")
        print(f"  Polish: ${result.get('polish_price', 0):.2f}")
        print(f"  Before markups: ${result['before_markups']:.2f}")
        print(f"  Tempered: ${result.get('tempered_price', 0):.2f}")
        print(f"  Subtotal: ${result['subtotal']:.2f}")
        print(f"  Quote price: ${result['quote_price']:.2f}")

        # Validate each step
        print("\nValidation:")
        print_result(result['billable_sq_ft'] == 6.0, 6.0, result['billable_sq_ft'], "Square footage")
        print_result(result['base_price'] == 75.0, 75.0, result['base_price'], "Base price")
        print_result(result['perimeter'] == 120.0, 120.0, result['perimeter'], "Perimeter")

        polish_price = result.get('polish_price', 0)
        print_result(polish_price == 102.0, 102.0, polish_price, "Polish price")
        print_result(result['before_markups'] == 177.0, 177.0, result['before_markups'], "Before markups")

        tempered_price = result.get('tempered_price', 0)
        print_result(tempered_price == 61.95, 61.95, tempered_price, "Tempered markup")
        print_result(result['subtotal'] == 238.95, 238.95, result['subtotal'], "Subtotal")
        print_result(result['quote_price'] == 853.39, 853.39, result['quote_price'], "Quote price")


def test_additional_scenarios():
    """Test additional realistic scenarios"""
    print_test_header("Additional Scenarios")

    db = Database()
    config = db.get_calculator_config()
    calc = GlassPriceCalculator(config)

    # Scenario 1: Small piece with minimum charge
    print("\n--- Scenario 1: Small Piece (Minimum Charge) ---")
    result = calc.calculate_quote(
        width=12, height=12, thickness='1/4"', glass_type='clear'
    )
    if 'error' not in result:
        print(f"  Actual sq ft: {result['actual_sq_ft']}")
        print(f"  Billable sq ft: {result['billable_sq_ft']}")
        print(f"  Quote price: ${result['quote_price']:.2f}")
        print_result(
            result['billable_sq_ft'] >= 3.0,
            "≥ 3.0",
            result['billable_sq_ft'],
            "Minimum charge applied"
        )

    # Scenario 2: Circular mirror with polish
    print("\n--- Scenario 2: Circular Mirror with Polish ---")
    result = calc.calculate_quote(
        width=0, height=0, thickness='1/4"', glass_type='mirror',
        is_circular=True, diameter=30, is_polished=True
    )
    if 'error' not in result:
        print(f"  Diameter: 30\"")
        print(f"  Square footage: {result['billable_sq_ft']}")
        print(f"  Perimeter: {result['perimeter']:.2f}")
        print(f"  Base price: ${result['base_price']:.2f}")
        print(f"  Polish: ${result.get('polish_price', 0):.2f}")
        print(f"  Quote price: ${result['quote_price']:.2f}")

    # Scenario 3: Rectangular with beveled and clipped corners
    print("\n--- Scenario 3: Beveled + Clipped Corners ---")
    result = calc.calculate_quote(
        width=48, height=60, thickness='3/8"', glass_type='clear',
        is_beveled=True, num_clipped_corners=4, clip_size='under_1'
    )
    if 'error' not in result:
        print(f"  Size: 48\" x 60\"")
        print(f"  Base price: ${result['base_price']:.2f}")
        print(f"  Beveled: ${result.get('beveled_price', 0):.2f}")
        print(f"  Clipped corners: ${result.get('clipped_corners_price', 0):.2f}")
        print(f"  Quote price: ${result['quote_price']:.2f}")

    # Scenario 4: Contractor pricing
    print("\n--- Scenario 4: Contractor Discount ---")
    result_regular = calc.calculate_quote(
        width=36, height=48, thickness='1/4"', glass_type='clear',
        is_polished=True, is_contractor=False
    )
    result_contractor = calc.calculate_quote(
        width=36, height=48, thickness='1/4"', glass_type='clear',
        is_polished=True, is_contractor=True
    )
    if 'error' not in result_regular and 'error' not in result_contractor:
        print(f"  Regular price: ${result_regular['quote_price']:.2f}")
        print(f"  Contractor price: ${result_contractor['quote_price']:.2f}")
        discount = result_contractor.get('contractor_discount', 0)
        print(f"  Discount: ${discount:.2f}")
        print_result(
            result_contractor['quote_price'] < result_regular['quote_price'],
            "Lower price",
            f"${result_contractor['quote_price']:.2f}",
            "Contractor pricing is cheaper"
        )

    # Scenario 5: Non-rectangular shape markup
    print("\n--- Scenario 5: Non-Rectangular Shape ---")
    result_rect = calc.calculate_quote(
        width=30, height=40, thickness='1/4"', glass_type='clear',
        is_non_rectangular=False
    )
    result_custom = calc.calculate_quote(
        width=30, height=40, thickness='1/4"', glass_type='clear',
        is_non_rectangular=True
    )
    if 'error' not in result_rect and 'error' not in result_custom:
        print(f"  Rectangular: ${result_rect['quote_price']:.2f}")
        print(f"  Custom shape: ${result_custom['quote_price']:.2f}")
        shape_markup = result_custom.get('shape_price', 0)
        print(f"  Shape markup: ${shape_markup:.2f}")
        print_result(
            result_custom['quote_price'] > result_rect['quote_price'],
            "Higher price",
            f"${result_custom['quote_price']:.2f}",
            "Custom shape is more expensive"
        )


def test_config_loading():
    """Test that configuration is loaded correctly"""
    print_test_header("Configuration Loading")

    db = Database()
    config = db.get_calculator_config()

    print("\nGlass Config Keys:")
    glass_config = config.get('glass_config', {})
    for key in sorted(glass_config.keys()):
        item = glass_config[key]
        print(f"  {key}: base=${item.get('base_price', 0):.2f}, polish=${item.get('polish_price', 0):.2f}")

    print("\nMarkups:")
    markups = config.get('markups', {})
    print(f"  Tempered: {markups.get('tempered', 0)}%")
    print(f"  Shape: {markups.get('shape', 0)}%")

    print("\nSettings:")
    settings = config.get('settings', {})
    print(f"  Minimum sq ft: {settings.get('minimum_sq_ft', 0)}")
    print(f"  Markup divisor: {settings.get('markup_divisor', 0)}")
    print(f"  Contractor discount rate: {settings.get('contractor_discount_rate', 0) * 100}%")

    print("\nFormula Config:")
    formula = config.get('formula_config', {})
    print(f"  Mode: {formula.get('formula_mode', 'N/A')}")
    print(f"  Divisor: {formula.get('divisor_value', 'N/A')}")
    print(f"  Components enabled:")
    print(f"    Base price: {formula.get('enable_base_price', False)}")
    print(f"    Polish: {formula.get('enable_polish', False)}")
    print(f"    Beveled: {formula.get('enable_beveled', False)}")
    print(f"    Tempered markup: {formula.get('enable_tempered_markup', False)}")
    print(f"    Shape markup: {formula.get('enable_shape_markup', False)}")
    print(f"    Contractor discount: {formula.get('enable_contractor_discount', False)}")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("GLASS CALCULATOR COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    try:
        test_config_loading()
        test_validation_rules()
        test_pricing_accuracy()
        test_additional_scenarios()

        print("\n" + "=" * 80)
        print("TEST SUITE COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ERROR: Test suite failed with exception:")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
