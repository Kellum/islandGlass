"""
Glass pricing calculator module
Implements all pricing formulas from GlassPricePro

ULTIMATE FORMULA: Final Quote Price = Combined Cost ÷ 0.28 (configurable)
"""

from typing import Dict, Optional, Any
import math
import re


class GlassPriceCalculator:
    """
    Calculate glass prices based on GlassPricePro formulas

    ULTIMATE FORMULA: Final Quote Price = Combined Cost ÷ markup_divisor

    Formula breakdown:
    1. Square footage = (width × height) ÷ 144  [min configurable sq ft]
    2. Base price = sq_ft × base_rate
    3. Perimeter = 2 × (width + height)  [or π × diameter for circular]
    4. Edge costs = perimeter × edge_rate
    5. Before markups = base + edges
    6. Tempered markup = before_markups × tempered%
    7. Shape markup = before_markups × shape%
    8. Subtotal = before_markups + tempered + shape
    9. Contractor discount = subtotal × configurable%
    10. Total = (subtotal - discount) × quantity
    11. QUOTE PRICE = total ÷ markup_divisor
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize calculator with pricing configuration

        Args:
            config: Dict containing:
                - glass_config: Dict[str, Dict] - base and polish prices
                - markups: Dict[str, float] - tempered%, shape%
                - beveled_pricing: Dict[str, float] - rates by thickness
                - clipped_corners_pricing: Dict[str, Dict] - rates by thickness/size
                - settings: Dict[str, float] - system constants (minimum_sq_ft, markup_divisor, etc.)
                - formula_config: Dict[str, Any] - pricing formula configuration (optional)
        """
        self.config = config

        # Load system settings (with fallback defaults)
        settings = config.get('settings', {})
        self.MINIMUM_SQ_FT = settings.get('minimum_sq_ft', 3.0)
        self.MARKUP_DIVISOR = settings.get('markup_divisor', 0.28)
        self.CONTRACTOR_DISCOUNT_RATE = settings.get('contractor_discount_rate', 0.15)
        self.FLAT_POLISH_RATE = settings.get('flat_polish_rate', 0.27)

        # Load formula configuration (with fallback defaults)
        self.formula_config = config.get('formula_config', {
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
        })

    def validate_custom_formula(self, expression: str) -> tuple[bool, str]:
        """
        Validate a custom formula expression for safety

        Args:
            expression: Python expression string (e.g., "total * 3.5 + 10")

        Returns:
            (is_valid, error_message) tuple
        """
        if not expression or not expression.strip():
            return False, "Expression cannot be empty"

        # Check for dangerous patterns
        dangerous_patterns = [
            r'import\s',
            r'__\w+__',
            r'exec\s*\(',
            r'eval\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'compile\s*\(',
            r'globals\s*\(',
            r'locals\s*\(',
            r'vars\s*\(',
            r'dir\s*\(',
            r'getattr\s*\(',
            r'setattr\s*\(',
            r'delattr\s*\(',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return False, f"Expression contains forbidden operation: {pattern}"

        # Test evaluation with a sample value
        try:
            # Create safe namespace with only allowed operations
            safe_namespace = {
                'total': 100.0,
                'abs': abs,
                'min': min,
                'max': max,
                'round': round,
                '__builtins__': {}
            }
            result = eval(expression, safe_namespace)

            # Check result is a valid number
            if not isinstance(result, (int, float)):
                return False, "Expression must return a numeric value"

            if result < 0:
                return False, "Expression produced a negative result"

            if math.isnan(result) or math.isinf(result):
                return False, "Expression produced an invalid result (NaN or Inf)"

            return True, ""

        except ZeroDivisionError:
            return False, "Expression causes division by zero"
        except Exception as e:
            return False, f"Invalid expression: {str(e)}"

    def apply_pricing_formula(self, total: float) -> float:
        """
        Apply the configured pricing formula to calculate final quote price

        Args:
            total: Combined cost before final markup

        Returns:
            Final quote price
        """
        mode = self.formula_config.get('formula_mode', 'divisor')

        if mode == 'divisor':
            divisor = self.formula_config.get('divisor_value', 0.28)
            if divisor == 0:
                # Prevent division by zero, fallback to default
                divisor = 0.28
            return total / divisor

        elif mode == 'multiplier':
            multiplier = self.formula_config.get('multiplier_value', 3.5714)
            return total * multiplier

        elif mode == 'custom':
            expression = self.formula_config.get('custom_expression')
            if not expression:
                # Fallback to divisor mode
                return total / 0.28

            # Validate before evaluating
            is_valid, error = self.validate_custom_formula(expression)
            if not is_valid:
                print(f"Custom formula validation failed: {error}. Using default.")
                return total / 0.28

            try:
                # Safe evaluation with restricted namespace
                safe_namespace = {
                    'total': total,
                    'abs': abs,
                    'min': min,
                    'max': max,
                    'round': round,
                    '__builtins__': {}
                }
                result = eval(expression, safe_namespace)
                return float(result)
            except Exception as e:
                print(f"Error evaluating custom formula: {e}. Using default.")
                return total / 0.28

        else:
            # Unknown mode, use default
            return total / 0.28

    def calculate_square_footage(
        self,
        width: float,
        height: float,
        is_circular: bool = False,
        diameter: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate square footage with minimum billable

        Args:
            width: Width in inches
            height: Height in inches
            is_circular: If true, calculate as circle
            diameter: Diameter in inches (for circular glass)

        Returns:
            Dict with 'actual_sq_ft' and 'billable_sq_ft' (minimum 3 sq ft)
        """
        if is_circular and diameter:
            radius = diameter / 2
            actual_sq_ft = (math.pi * radius ** 2) / 144
        else:
            actual_sq_ft = (width * height) / 144

        billable_sq_ft = max(actual_sq_ft, self.MINIMUM_SQ_FT)

        return {
            'actual_sq_ft': actual_sq_ft,
            'billable_sq_ft': billable_sq_ft
        }

    def calculate_perimeter(
        self,
        width: float,
        height: float,
        is_circular: bool = False,
        diameter: Optional[float] = None
    ) -> float:
        """
        Calculate perimeter in inches

        Args:
            width: Width in inches
            height: Height in inches
            is_circular: If true, calculate as circle
            diameter: Diameter in inches (for circular glass)

        Returns:
            Perimeter in inches
        """
        if is_circular and diameter:
            return math.pi * diameter
        else:
            return 2 * (width + height)

    def calculate_base_price(
        self,
        thickness: str,
        glass_type: str,
        sq_ft: float
    ) -> float:
        """
        Calculate base glass price

        Args:
            thickness: Glass thickness (e.g., "1/4\"")
            glass_type: Type of glass (clear, bronze, gray, mirror)
            sq_ft: Square footage

        Returns:
            Base price
        """
        key = f"{thickness}_{glass_type}"
        base_rate = self.config['glass_config'].get(key, {}).get('base_price', 0)
        return sq_ft * base_rate

    def calculate_polish_price(
        self,
        thickness: str,
        glass_type: str,
        perimeter: float,
        is_flat_polish: bool = False
    ) -> float:
        """
        Calculate edge polish price

        Args:
            thickness: Glass thickness
            glass_type: Type of glass
            perimeter: Perimeter in inches
            is_flat_polish: Use flat polish rate (mirrors)

        Returns:
            Polish price
        """
        if is_flat_polish:
            rate = self.FLAT_POLISH_RATE  # Use configurable flat polish rate for mirrors
        else:
            key = f"{thickness}_{glass_type}"
            rate = self.config['glass_config'].get(key, {}).get('polish_price', 0)

        return perimeter * rate

    def calculate_beveled_price(
        self,
        thickness: str,
        perimeter: float
    ) -> float:
        """
        Calculate beveled edge price

        Not available for 1/8" glass

        Args:
            thickness: Glass thickness
            perimeter: Perimeter in inches

        Returns:
            Beveled price or 0 if not available
        """
        if thickness == '1/8"':
            return 0

        rate = self.config['beveled_pricing'].get(thickness, 0)
        return perimeter * rate

    def calculate_clipped_corners_price(
        self,
        thickness: str,
        num_corners: int,
        clip_size: str = 'under_1'
    ) -> float:
        """
        Calculate clipped corners price

        Args:
            thickness: Glass thickness
            num_corners: Number of corners (1-4)
            clip_size: 'under_1' or 'over_1' inch

        Returns:
            Clipped corners price
        """
        key = f"{thickness}_{clip_size}"
        rate = self.config['clipped_corners_pricing'].get(key, 0)
        return num_corners * rate

    def calculate_tempered_markup(
        self,
        before_markups: float,
        glass_type: str,
        force_tempered: bool = False
    ) -> float:
        """
        Calculate tempered glass markup

        Never applied to mirrors

        Args:
            before_markups: Base + edges price
            glass_type: Type of glass
            force_tempered: Force tempering regardless of config

        Returns:
            Tempered markup amount
        """
        if glass_type == 'mirror':
            return 0

        if not force_tempered:
            return 0

        tempered_percent = self.config['markups'].get('tempered', 0)
        return before_markups * (tempered_percent / 100)

    def calculate_shape_markup(
        self,
        before_markups: float,
        is_non_rectangular: bool = False,
        is_circular: bool = False
    ) -> float:
        """
        Calculate shape markup

        Args:
            before_markups: Base + edges price
            is_non_rectangular: Non-rectangular shape
            is_circular: Circular shape

        Returns:
            Shape markup amount
        """
        if not (is_non_rectangular or is_circular):
            return 0

        shape_percent = self.config['markups'].get('shape', 0)
        return before_markups * (shape_percent / 100)

    def calculate_contractor_discount(
        self,
        subtotal: float,
        is_contractor: bool = False
    ) -> float:
        """
        Calculate contractor discount (15%)

        Args:
            subtotal: Price before discount
            is_contractor: Apply contractor pricing

        Returns:
            Discount amount
        """
        if not is_contractor:
            return 0

        return subtotal * self.CONTRACTOR_DISCOUNT_RATE

    def validate_quote_params(
        self,
        thickness: str,
        glass_type: str,
        is_polished: bool,
        is_beveled: bool,
        is_tempered: bool,
        num_clipped_corners: int,
        is_circular: bool
    ) -> Optional[str]:
        """
        Validate quote parameters against business rules

        Returns:
            Error message string if invalid, None if valid
        """
        # Rule 1: 1/8" glass cannot have ANY edge work (no polish, no bevel, no tempered)
        if thickness == '1/8"':
            if is_tempered:
                return "1/8\" glass cannot be tempered"
            if is_polished:
                return "1/8\" glass cannot be polished"
            if is_beveled:
                return "1/8\" glass cannot have beveled edges"

        # Rule 2: 1/8" glass cannot be mirror
        if thickness == '1/8"' and glass_type == 'mirror':
            return "1/8\" mirror is not available"

        # Rule 3: Mirrors cannot be tempered
        if glass_type == 'mirror' and is_tempered:
            return "Mirror glass cannot be tempered"

        # Rule 4: Clipped corners only available for non-mirror glass
        if num_clipped_corners > 0 and glass_type == 'mirror':
            return "Clipped corners are not available for mirrors"

        # Rule 5: Clipped corners not available for circular glass
        if num_clipped_corners > 0 and is_circular:
            return "Clipped corners are not available for circular glass"

        return None

    def calculate_quote(
        self,
        width: float,
        height: float,
        thickness: str,
        glass_type: str,
        quantity: int = 1,
        is_polished: bool = False,
        is_beveled: bool = False,
        num_clipped_corners: int = 0,
        clip_size: str = 'under_1',
        is_tempered: bool = False,
        is_non_rectangular: bool = False,
        is_circular: bool = False,
        diameter: Optional[float] = None,
        is_contractor: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate complete glass quote

        Args:
            width: Width in inches
            height: Height in inches
            thickness: Glass thickness
            glass_type: Type of glass
            quantity: Number of pieces
            is_polished: Apply polish
            is_beveled: Apply beveled edges
            num_clipped_corners: Number of clipped corners (0-4)
            clip_size: Clip size ('under_1' or 'over_1')
            is_tempered: Temper the glass
            is_non_rectangular: Non-rectangular shape
            is_circular: Circular glass
            diameter: Diameter for circular glass
            is_contractor: Apply contractor discount

        Returns:
            Dict with price breakdown:
                - actual_sq_ft
                - billable_sq_ft
                - sq_ft (billable, for backward compatibility)
                - perimeter
                - base_price
                - polish_price (if applicable)
                - beveled_price (if applicable)
                - clipped_corners_price (if applicable)
                - before_markups
                - tempered_price (if applicable)
                - shape_price (if applicable)
                - subtotal
                - contractor_discount (if applicable)
                - discounted_subtotal (if applicable)
                - total (after quantity)
                - quote_price (total ÷ 0.28)
                - error (if validation fails)
        """
        # Validate parameters first
        validation_error = self.validate_quote_params(
            thickness=thickness,
            glass_type=glass_type,
            is_polished=is_polished,
            is_beveled=is_beveled,
            is_tempered=is_tempered,
            num_clipped_corners=num_clipped_corners,
            is_circular=is_circular
        )

        if validation_error:
            return {
                'error': validation_error,
                'actual_sq_ft': 0,
                'billable_sq_ft': 0,
                'sq_ft': 0,
                'perimeter': 0,
                'base_price': 0,
                'total': 0,
                'quote_price': 0
            }

        # Calculate dimensions
        sq_ft_result = self.calculate_square_footage(width, height, is_circular, diameter)
        actual_sq_ft = sq_ft_result['actual_sq_ft']
        billable_sq_ft = sq_ft_result['billable_sq_ft']
        perimeter = self.calculate_perimeter(width, height, is_circular, diameter)

        # Base price using billable sq ft (check if enabled)
        base_price = 0
        if self.formula_config.get('enable_base_price', True):
            base_price = self.calculate_base_price(thickness, glass_type, billable_sq_ft)

        # Edge processing (check if enabled)
        polish_price = 0
        if is_polished and self.formula_config.get('enable_polish', True):
            is_flat = (glass_type == 'mirror')
            polish_price = self.calculate_polish_price(thickness, glass_type, perimeter, is_flat)

        beveled_price = 0
        if is_beveled and self.formula_config.get('enable_beveled', True):
            beveled_price = self.calculate_beveled_price(thickness, perimeter)

        clipped_corners_price = 0
        if num_clipped_corners > 0 and self.formula_config.get('enable_clipped_corners', True):
            clipped_corners_price = self.calculate_clipped_corners_price(
                thickness, num_clipped_corners, clip_size
            )

        # Before markups subtotal
        before_markups = base_price + polish_price + beveled_price + clipped_corners_price

        # Markups (check if enabled)
        tempered_price = 0
        if self.formula_config.get('enable_tempered_markup', True):
            tempered_price = self.calculate_tempered_markup(before_markups, glass_type, is_tempered)

        shape_price = 0
        if self.formula_config.get('enable_shape_markup', True):
            shape_price = self.calculate_shape_markup(before_markups, is_non_rectangular, is_circular)

        # Subtotal
        subtotal = before_markups + tempered_price + shape_price

        # Contractor discount (check if enabled)
        contractor_discount = 0
        if self.formula_config.get('enable_contractor_discount', True):
            contractor_discount = self.calculate_contractor_discount(subtotal, is_contractor)

        discounted_subtotal = subtotal - contractor_discount

        # Final total
        total = discounted_subtotal * quantity

        # Quote price (Apply configured formula)
        quote_price = self.apply_pricing_formula(total)

        return {
            'actual_sq_ft': round(actual_sq_ft, 2),
            'billable_sq_ft': round(billable_sq_ft, 2),
            'sq_ft': round(billable_sq_ft, 2),  # Backward compatibility
            'perimeter': round(perimeter, 2),
            'base_price': round(base_price, 2),
            'polish_price': round(polish_price, 2) if polish_price > 0 else None,
            'beveled_price': round(beveled_price, 2) if beveled_price > 0 else None,
            'clipped_corners_price': round(clipped_corners_price, 2) if clipped_corners_price > 0 else None,
            'before_markups': round(before_markups, 2),
            'tempered_price': round(tempered_price, 2) if tempered_price > 0 else None,
            'shape_price': round(shape_price, 2) if shape_price > 0 else None,
            'subtotal': round(subtotal, 2),
            'contractor_discount': round(contractor_discount, 2) if contractor_discount > 0 else None,
            'discounted_subtotal': round(discounted_subtotal, 2) if contractor_discount > 0 else None,
            'total': round(total, 2),
            'quote_price': round(quote_price, 2)
        }


# Example usage for testing:
if __name__ == "__main__":
    # Sample configuration
    config = {
        'glass_config': {
            '1/4"_clear': {'base_price': 12.50, 'polish_price': 0.85},
            '1/4"_bronze': {'base_price': 18.00, 'polish_price': 0.85},
            '1/4"_mirror': {'base_price': 15.00, 'polish_price': 0.27},
        },
        'markups': {
            'tempered': 35.0,  # 35%
            'shape': 25.0      # 25%
        },
        'beveled_pricing': {
            '1/4"': 2.01,
            '3/8"': 2.91,
            '1/2"': 3.80
        },
        'clipped_corners_pricing': {
            '1/4"_under_1': 5.50,
            '1/4"_over_1': 22.18,
        }
    }

    calc = GlassPriceCalculator(config)

    # Example quote: 24" x 36" clear glass, 1/4" thick, polished, tempered
    result = calc.calculate_quote(
        width=24,
        height=36,
        thickness='1/4"',
        glass_type='clear',
        quantity=1,
        is_polished=True,
        is_tempered=True,
        is_contractor=False
    )

    print("Glass Quote Test:")
    print("=" * 50)
    print(f"  Dimensions: 24\" x 36\" ({result['sq_ft']} sq ft)")
    print(f"  Base Price: ${result['base_price']:.2f}")
    print(f"  Polish: ${result['polish_price']:.2f}")
    print(f"  Tempered Markup: ${result['tempered_price']:.2f}")
    print(f"  Total: ${result['total']:.2f}")
    print(f"  QUOTE PRICE: ${result['quote_price']:.2f}")
