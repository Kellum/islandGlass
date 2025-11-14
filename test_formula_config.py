"""
Test the new pricing formula configuration system
"""

from modules.glass_calculator import GlassPriceCalculator

# Test 1: Default divisor mode (backwards compatible)
print("=" * 60)
print("TEST 1: Default Divisor Mode (0.28)")
print("=" * 60)

config = {
    'glass_config': {
        '1/4"_clear': {'base_price': 12.50, 'polish_price': 0.85},
    },
    'markups': {
        'tempered': 35.0,
        'shape': 25.0
    },
    'beveled_pricing': {},
    'clipped_corners_pricing': {},
    'settings': {
        'minimum_sq_ft': 3.0,
        'markup_divisor': 0.28,
        'contractor_discount_rate': 0.15,
        'flat_polish_rate': 0.27
    },
    'formula_config': {
        'formula_mode': 'divisor',
        'divisor_value': 0.28,
        'multiplier_value': 3.5714,
        'custom_expression': None,
        'enable_base_price': True,
        'enable_polish': True,
        'enable_beveled': True,
        'enable_clipped_corners': True,
        'enable_tempered_markup': True,
        'enable_shape_markup': True,
        'enable_contractor_discount': True
    }
}

calc = GlassPriceCalculator(config)

result = calc.calculate_quote(
    width=24,
    height=36,
    thickness='1/4"',
    glass_type='clear',
    quantity=1,
    is_polished=True,
    is_tempered=True
)

print(f"24\" x 36\" clear glass, polished, tempered:")
print(f"  Base Price: ${result['base_price']:.2f}")
print(f"  Polish: ${result['polish_price']:.2f}")
print(f"  Tempered Markup: ${result['tempered_price']:.2f}")
print(f"  Total Cost: ${result['total']:.2f}")
print(f"  QUOTE PRICE (÷ 0.28): ${result['quote_price']:.2f}")
print()

# Test 2: Multiplier mode
print("=" * 60)
print("TEST 2: Multiplier Mode (× 3.5714)")
print("=" * 60)

config['formula_config']['formula_mode'] = 'multiplier'
calc2 = GlassPriceCalculator(config)

result2 = calc2.calculate_quote(
    width=24,
    height=36,
    thickness='1/4"',
    glass_type='clear',
    quantity=1,
    is_polished=True,
    is_tempered=True
)

print(f"Same glass with multiplier mode:")
print(f"  Total Cost: ${result2['total']:.2f}")
print(f"  QUOTE PRICE (× 3.5714): ${result2['quote_price']:.2f}")
print(f"  Should be similar to divisor: ${result['quote_price']:.2f}")
print()

# Test 3: Custom formula
print("=" * 60)
print("TEST 3: Custom Formula (total * 4.0)")
print("=" * 60)

config['formula_config']['formula_mode'] = 'custom'
config['formula_config']['custom_expression'] = 'total * 4.0'
calc3 = GlassPriceCalculator(config)

result3 = calc3.calculate_quote(
    width=24,
    height=36,
    thickness='1/4"',
    glass_type='clear',
    quantity=1,
    is_polished=True,
    is_tempered=True
)

print(f"Same glass with custom formula (total * 4.0):")
print(f"  Total Cost: ${result3['total']:.2f}")
print(f"  QUOTE PRICE (× 4.0): ${result3['quote_price']:.2f}")
print()

# Test 4: Disable components
print("=" * 60)
print("TEST 4: Disabled Components (no polish, no tempered)")
print("=" * 60)

config['formula_config']['formula_mode'] = 'divisor'
config['formula_config']['enable_polish'] = False
config['formula_config']['enable_tempered_markup'] = False
calc4 = GlassPriceCalculator(config)

result4 = calc4.calculate_quote(
    width=24,
    height=36,
    thickness='1/4"',
    glass_type='clear',
    quantity=1,
    is_polished=True,  # Requested but disabled
    is_tempered=True   # Requested but disabled
)

print(f"Same glass with polish and tempered DISABLED:")
print(f"  Base Price: ${result4['base_price']:.2f}")
print(f"  Polish: ${result4['polish_price'] if result4['polish_price'] else '$0.00 (DISABLED)'}")
print(f"  Tempered Markup: ${result4['tempered_price'] if result4['tempered_price'] else '$0.00 (DISABLED)'}")
print(f"  Total Cost: ${result4['total']:.2f}")
print(f"  QUOTE PRICE: ${result4['quote_price']:.2f}")
print()

# Test 5: Formula validation
print("=" * 60)
print("TEST 5: Formula Validation")
print("=" * 60)

test_formulas = [
    ("total * 3.5", True, "Simple multiplication"),
    ("total / 0.28", True, "Division"),
    ("total * 3.5 + 10", True, "With addition"),
    ("max(total * 3, 100)", True, "Using max()"),
    ("total * (1 + 0.5)", True, "With parentheses"),
    ("import os", False, "Dangerous: import"),
    ("__builtins__", False, "Dangerous: builtins"),
    ("eval('total')", False, "Dangerous: eval"),
    ("total / 0", False, "Division by zero"),
    ("'string'", False, "Non-numeric result"),
]

for expr, expected_valid, description in test_formulas:
    is_valid, error = calc.validate_custom_formula(expr)
    status = "✓" if is_valid == expected_valid else "✗"
    result_text = "VALID" if is_valid else f"INVALID: {error}"
    print(f"{status} {description:30s} → {result_text}")

print()
print("=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
