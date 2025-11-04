"""
Fraction and measurement utilities for glass calculations
Handles mixed numbers, fractions, and decimal conversions

Used by Glass Calculator for parsing dimension inputs like "24 1/2"
"""

from fractions import Fraction
from typing import Union


def parse_measurement(input_str: str) -> Fraction:
    """
    Parse mixed numbers, fractions, or decimals

    Examples:
        "24 1/2" -> Fraction(49, 2)
        "3/4" -> Fraction(3, 4)
        "24.5" -> Fraction(49, 2)
        "24" -> Fraction(24, 1)

    Args:
        input_str: Input measurement string

    Returns:
        Fraction object

    Raises:
        ValueError: If input cannot be parsed
    """
    input_str = input_str.strip()

    if not input_str:
        raise ValueError("Empty input")

    # Mixed number: "24 1/2"
    if ' ' in input_str:
        parts = input_str.split()
        if len(parts) != 2:
            raise ValueError(f"Invalid mixed number format: {input_str}")

        whole = int(parts[0])
        frac = Fraction(parts[1])

        # Handle negative mixed numbers
        if whole < 0:
            return whole - frac
        return whole + frac

    # Fraction: "3/4"
    elif '/' in input_str:
        return Fraction(input_str)

    # Decimal: "24.5"
    elif '.' in input_str:
        return Fraction(float(input_str)).limit_denominator()

    # Whole number: "24"
    else:
        return Fraction(int(input_str))


def format_fraction(frac: Fraction, max_denominator: int = 16) -> str:
    """
    Format fraction as mixed number for display

    Examples:
        Fraction(49, 2) -> "24 1/2"
        Fraction(3, 4) -> "3/4"
        Fraction(24, 1) -> "24"

    Args:
        frac: Fraction to format
        max_denominator: Maximum denominator for simplification

    Returns:
        Formatted string
    """
    # Limit denominator for cleaner display
    frac = frac.limit_denominator(max_denominator)

    # Whole number
    if frac.denominator == 1:
        return str(frac.numerator)

    # Mixed number (>= 1)
    if abs(frac) >= 1:
        whole = int(frac)
        remainder = frac - whole

        if remainder == 0:
            return str(whole)

        # Handle negative
        if whole < 0:
            return f"{whole} {abs(remainder.numerator)}/{remainder.denominator}"

        return f"{whole} {remainder.numerator}/{remainder.denominator}"

    # Proper fraction (< 1)
    return f"{frac.numerator}/{frac.denominator}"


def to_decimal(input_str: str) -> float:
    """
    Convert measurement string to decimal

    Args:
        input_str: Measurement string (fraction, mixed, or decimal)

    Returns:
        Float value
    """
    frac = parse_measurement(input_str)
    return float(frac)


def validate_measurement(input_str: str) -> bool:
    """
    Validate if string is a valid measurement

    Args:
        input_str: Input string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        parse_measurement(input_str)
        return True
    except (ValueError, ZeroDivisionError):
        return False


# Example usage for testing:
if __name__ == "__main__":
    # Test cases
    tests = [
        "24 1/2",
        "3/4",
        "24.5",
        "24",
        "-12 3/4",
        "48",
        "0.125"
    ]

    print("Fraction Utils Test:")
    print("=" * 50)
    for test in tests:
        frac = parse_measurement(test)
        formatted = format_fraction(frac)
        decimal = float(frac)
        print(f"{test:>10} -> {formatted:>10} = {decimal:.4f}")
