/**
 * Fraction utilities for glass measurements
 * Handles conversion between fractions and decimals
 */

/**
 * Convert a fraction string to decimal
 * Supports formats like: "24", "24 1/2", "1/4", "24.5"
 */
export function fractionToDecimal(input: string): number {
  if (!input || input.trim() === '') return 0;

  const trimmed = input.trim();

  // Handle decimal input (like "24.5")
  if (!trimmed.includes('/') && !isNaN(Number(trimmed))) {
    return Number(trimmed);
  }

  // Split on space to separate whole number from fraction
  const parts = trimmed.split(' ');

  let whole = 0;
  let fraction = 0;

  if (parts.length === 1) {
    // Either just a whole number or just a fraction
    if (parts[0].includes('/')) {
      // Just a fraction like "1/4"
      const [numerator, denominator] = parts[0].split('/').map(Number);
      // Guard against division by zero or incomplete input
      if (denominator && denominator !== 0 && !isNaN(numerator) && !isNaN(denominator)) {
        fraction = numerator / denominator;
      }
    } else {
      // Just a whole number
      whole = Number(parts[0]);
    }
  } else if (parts.length === 2) {
    // Whole number and fraction like "24 1/2"
    whole = Number(parts[0]);
    const [numerator, denominator] = parts[1].split('/').map(Number);
    // Guard against division by zero or incomplete input
    if (denominator && denominator !== 0 && !isNaN(numerator) && !isNaN(denominator)) {
      fraction = numerator / denominator;
    }
  }

  const result = whole + fraction;
  // Return 0 if result is not a valid number
  return isNaN(result) || !isFinite(result) ? 0 : result;
}

/**
 * Convert a decimal to the nearest fraction (in 1/8" increments)
 * Returns a formatted string like "24 1/2" or "3/4"
 */
export function decimalToFraction(decimal: number, precision: number = 8): string {
  // Guard against invalid inputs
  if (!isFinite(decimal) || isNaN(decimal)) return '0';
  if (decimal === 0) return '0';

  const whole = Math.floor(decimal);
  const remainder = decimal - whole;

  if (remainder === 0) {
    return whole.toString();
  }

  // Find the closest fraction with the given precision
  const numerator = Math.round(remainder * precision);

  if (numerator === 0) {
    return whole.toString();
  }

  if (numerator === precision) {
    return (whole + 1).toString();
  }

  // Simplify the fraction using GCD
  const gcd = (a: number, b: number): number => {
    // Guard against invalid inputs to prevent infinite recursion
    if (!isFinite(a) || !isFinite(b) || isNaN(a) || isNaN(b)) return 1;
    if (b === 0) return a;
    return gcd(b, a % b);
  };

  const divisor = gcd(numerator, precision);
  const simplifiedNum = numerator / divisor;
  const simplifiedDen = precision / divisor;

  const fractionPart = `${simplifiedNum}/${simplifiedDen}`;

  if (whole === 0) {
    return fractionPart;
  }

  return `${whole} ${fractionPart}`;
}

/**
 * Format a measurement for display (always as fraction)
 */
export function formatMeasurement(value: number, unit: string = '"'): string {
  const fraction = decimalToFraction(value);
  return `${fraction}${unit}`;
}
