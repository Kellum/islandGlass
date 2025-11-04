"""
Glass pricing calculator module
Implements all pricing formulas from GlassPricePro

ULTIMATE FORMULA: Final Quote Price = Combined Cost ÷ 0.28
"""

from typing import Dict, Optional, Any
import math


class GlassPriceCalculator:
    """
    Calculate glass prices based on GlassPricePro formulas

    ULTIMATE FORMULA: Final Quote Price = Combined Cost ÷ 0.28

    Formula breakdown:
    1. Square footage = (width × height) ÷ 144  [min 3 sq ft]
    2. Base price = sq_ft × base_rate
    3. Perimeter = 2 × (width + height)  [or π × diameter for circular]
    4. Edge costs = perimeter × edge_rate
    5. Before markups = base + edges
    6. Tempered markup = before_markups × tempered%
    7. Shape markup = before_markups × shape%
    8. Subtotal = before_markups + tempered + shape
    9. Contractor discount = subtotal × 15%
    10. Total = (subtotal - discount) × quantity
    11. QUOTE PRICE = total ÷ 0.28
    """

    MINIMUM_SQ_FT = 3.0
    MARKUP_DIVISOR = 0.28
    CONTRACTOR_DISCOUNT_RATE = 0.15

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize calculator with pricing configuration

        Args:
            config: Dict containing:
                - glass_config: Dict[str, Dict] - base and polish prices
                - markups: Dict[str, float] - tempered%, shape%
                - beveled_pricing: Dict[str, float] - rates by thickness
                - clipped_corners_pricing: Dict[str, Dict] - rates by thickness/size
        """
        self.config = config

    def calculate_square_footage(
        self,
        width: float,
        height: float,
        is_circular: bool = False,
        diameter: Optional[float] = None
    ) -> float:
        """
        Calculate square footage with minimum billable

        Args:
            width: Width in inches
            height: Height in inches
            is_circular: If true, calculate as circle
            diameter: Diameter in inches (for circular glass)

        Returns:
            Square footage (minimum 3 sq ft)
        """
        if is_circular and diameter:
            radius = diameter / 2
            sq_ft = (math.pi * radius ** 2) / 144
        else:
            sq_ft = (width * height) / 144

        return max(sq_ft, self.MINIMUM_SQ_FT)

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
            rate = 0.27  # Flat polish default for mirrors
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
                - sq_ft
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
        """
        # Calculate dimensions
        sq_ft = self.calculate_square_footage(width, height, is_circular, diameter)
        perimeter = self.calculate_perimeter(width, height, is_circular, diameter)

        # Base price
        base_price = self.calculate_base_price(thickness, glass_type, sq_ft)

        # Edge processing
        polish_price = 0
        if is_polished:
            is_flat = (glass_type == 'mirror')
            polish_price = self.calculate_polish_price(thickness, glass_type, perimeter, is_flat)

        beveled_price = 0
        if is_beveled:
            beveled_price = self.calculate_beveled_price(thickness, perimeter)

        clipped_corners_price = 0
        if num_clipped_corners > 0:
            clipped_corners_price = self.calculate_clipped_corners_price(
                thickness, num_clipped_corners, clip_size
            )

        # Before markups subtotal
        before_markups = base_price + polish_price + beveled_price + clipped_corners_price

        # Markups
        tempered_price = self.calculate_tempered_markup(before_markups, glass_type, is_tempered)
        shape_price = self.calculate_shape_markup(before_markups, is_non_rectangular, is_circular)

        # Subtotal
        subtotal = before_markups + tempered_price + shape_price

        # Contractor discount
        contractor_discount = self.calculate_contractor_discount(subtotal, is_contractor)
        discounted_subtotal = subtotal - contractor_discount

        # Final total
        total = discounted_subtotal * quantity

        # Quote price (ULTIMATE FORMULA)
        quote_price = total / self.MARKUP_DIVISOR

        return {
            'sq_ft': round(sq_ft, 2),
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
