/**
 * Glass Price Calculator - TypeScript Port
 *
 * Implements all pricing formulas from GlassPricePro
 *
 * PRICING MODEL:
 * - Database stores WHOLESALE costs (base_price, polish_price) = actual cost from suppliers
 * - Calculator applies markup formula (default: ÷ 0.28) to convert wholesale → retail
 * - ULTIMATE FORMULA: Final Quote Price = Wholesale Combined Cost ÷ 0.28 (configurable)
 * - Example: $4.05/sq ft wholesale ÷ 0.28 = $14.46/sq ft retail quote
 */

export interface GlassConfigItem {
  base_price: number;
  polish_price: number;
  only_tempered?: boolean;
  no_polish?: boolean;
  never_tempered?: boolean;
}

export interface CalculatorConfig {
  glass_config: Record<string, GlassConfigItem>;
  markups: {
    tempered: number;
    shape: number;
  };
  beveled_pricing: Record<string, number>;
  clipped_corners_pricing: Record<string, number>;
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
    enable_base_price: boolean;
    enable_polish: boolean;
    enable_beveled: boolean;
    enable_clipped_corners: boolean;
    enable_tempered_markup: boolean;
    enable_shape_markup: boolean;
    enable_contractor_discount: boolean;
  };
}

export interface QuoteParams {
  width: number;
  height: number;
  thickness: string;
  glass_type: string;
  quantity?: number;
  is_polished?: boolean;
  is_beveled?: boolean;
  num_clipped_corners?: number;
  clip_size?: string;
  is_tempered?: boolean;
  is_non_rectangular?: boolean;
  is_circular?: boolean;
  diameter?: number;
  is_contractor?: boolean;
}

export interface QuoteResult {
  actual_sq_ft: number;
  billable_sq_ft: number;
  sq_ft: number;
  perimeter: number;
  base_price: number;
  polish_price?: number;
  beveled_price?: number;
  clipped_corners_price?: number;
  before_markups: number;
  tempered_price?: number;
  shape_price?: number;
  subtotal: number;
  contractor_discount?: number;
  discounted_subtotal?: number;
  total: number;
  quote_price: number;
  error?: string;
}

export class GlassPriceCalculator {
  private config: CalculatorConfig;
  private MINIMUM_SQ_FT: number;
  // private _MARKUP_DIVISOR: number; // Unused for now
  private CONTRACTOR_DISCOUNT_RATE: number;
  private FLAT_POLISH_RATE: number;
  private formula_config: CalculatorConfig['formula_config'];

  constructor(config: CalculatorConfig) {
    this.config = config;

    // Load system settings (with fallback defaults)
    const settings = config.settings || {};
    this.MINIMUM_SQ_FT = settings.minimum_sq_ft || 3.0;
    // this._MARKUP_DIVISOR = settings.markup_divisor || 0.28; // Unused for now
    this.CONTRACTOR_DISCOUNT_RATE = settings.contractor_discount_rate || 0.15;
    this.FLAT_POLISH_RATE = settings.flat_polish_rate || 0.27;

    // Load formula configuration (with fallback defaults)
    this.formula_config = config.formula_config || {
      formula_mode: 'divisor',
      divisor_value: 0.28,
      multiplier_value: 3.5714,
      custom_expression: null,
      enable_base_price: true,
      enable_polish: true,
      enable_beveled: true,
      enable_clipped_corners: true,
      enable_tempered_markup: true,
      enable_shape_markup: true,
      enable_contractor_discount: true,
    };
  }

  /**
   * Validate a custom formula expression for safety
   */
  private validateCustomFormula(expression: string): { isValid: boolean; error: string } {
    if (!expression || !expression.trim()) {
      return { isValid: false, error: 'Expression cannot be empty' };
    }

    // Check for dangerous patterns
    const dangerousPatterns = [
      /import\s/i,
      /__\w+__/,
      /eval\s*\(/i,
      /exec\s*\(/i,
      /function\s*\(/i,
      /=>/,
      /new\s+/i,
    ];

    for (const pattern of dangerousPatterns) {
      if (pattern.test(expression)) {
        return { isValid: false, error: `Expression contains forbidden operation: ${pattern}` };
      }
    }

    // Test evaluation with a sample value
    try {
      const total = 100.0;
      // Use Function constructor for safe evaluation (safer than eval)
      const func = new Function('total', 'Math', `return ${expression}`);
      const result = func(total, Math);

      // Check result is a valid number
      if (typeof result !== 'number') {
        return { isValid: false, error: 'Expression must return a numeric value' };
      }

      if (result < 0) {
        return { isValid: false, error: 'Expression produced a negative result' };
      }

      if (isNaN(result) || !isFinite(result)) {
        return { isValid: false, error: 'Expression produced an invalid result (NaN or Inf)' };
      }

      return { isValid: true, error: '' };
    } catch (e) {
      return { isValid: false, error: `Invalid expression: ${e}` };
    }
  }

  /**
   * Apply the configured pricing formula to calculate final quote price
   */
  private applyPricingFormula(total: number): number {
    const mode = this.formula_config.formula_mode;

    if (mode === 'divisor') {
      let divisor = this.formula_config.divisor_value;
      if (divisor === 0) {
        // Prevent division by zero, fallback to default
        divisor = 0.28;
      }
      return total / divisor;
    } else if (mode === 'multiplier') {
      const multiplier = this.formula_config.multiplier_value;
      return total * multiplier;
    } else if (mode === 'custom') {
      const expression = this.formula_config.custom_expression;
      if (!expression) {
        // Fallback to divisor mode
        return total / 0.28;
      }

      // Validate before evaluating
      const { isValid, error } = this.validateCustomFormula(expression);
      if (!isValid) {
        console.error(`Custom formula validation failed: ${error}. Using default.`);
        return total / 0.28;
      }

      try {
        const func = new Function('total', 'Math', `return ${expression}`);
        const result = func(total, Math);
        return Number(result);
      } catch (e) {
        console.error(`Error evaluating custom formula: ${e}. Using default.`);
        return total / 0.28;
      }
    } else {
      // Unknown mode, use default
      return total / 0.28;
    }
  }

  /**
   * Calculate square footage with minimum billable
   */
  calculateSquareFootage(
    width: number,
    height: number,
    is_circular: boolean = false,
    diameter?: number
  ): { actual_sq_ft: number; billable_sq_ft: number } {
    let actual_sq_ft: number;

    if (is_circular && diameter) {
      const radius = diameter / 2;
      actual_sq_ft = (Math.PI * radius ** 2) / 144;
    } else {
      actual_sq_ft = (width * height) / 144;
    }

    const billable_sq_ft = Math.max(actual_sq_ft, this.MINIMUM_SQ_FT);

    return {
      actual_sq_ft,
      billable_sq_ft,
    };
  }

  /**
   * Calculate perimeter in inches
   */
  calculatePerimeter(
    width: number,
    height: number,
    is_circular: boolean = false,
    diameter?: number
  ): number {
    if (is_circular && diameter) {
      return Math.PI * diameter;
    } else {
      return 2 * (width + height);
    }
  }

  /**
   * Calculate base glass price
   *
   * NOTE: base_price is the WHOLESALE cost per sq ft (from supplier)
   * The markup formula (÷ 0.28) is applied later to get retail quote price
   */
  calculateBasePrice(thickness: string, glass_type: string, sq_ft: number): number {
    const key = `${thickness}_${glass_type}`;
    const base_rate = this.config.glass_config[key]?.base_price || 0; // WHOLESALE cost/sq ft
    return sq_ft * base_rate;
  }

  /**
   * Calculate edge polish price
   */
  calculatePolishPrice(
    thickness: string,
    glass_type: string,
    perimeter: number,
    is_flat_polish: boolean = false
  ): number {
    let rate: number;

    if (is_flat_polish) {
      rate = this.FLAT_POLISH_RATE; // Use configurable flat polish rate for mirrors
    } else {
      const key = `${thickness}_${glass_type}`;
      rate = this.config.glass_config[key]?.polish_price || 0;
    }

    return perimeter * rate;
  }

  /**
   * Calculate beveled edge price (not available for 1/8" glass)
   */
  calculateBeveledPrice(thickness: string, perimeter: number): number {
    if (thickness === '1/8"') {
      return 0;
    }

    const rate = this.config.beveled_pricing[thickness] || 0;
    return perimeter * rate;
  }

  /**
   * Calculate clipped corners price
   */
  calculateClippedCornersPrice(
    thickness: string,
    num_corners: number,
    clip_size: string = 'under_1'
  ): number {
    const key = `${thickness}_${clip_size}`;
    const rate = this.config.clipped_corners_pricing[key] || 0;
    return num_corners * rate;
  }

  /**
   * Calculate tempered glass markup (never applied to mirrors)
   */
  calculateTemperedMarkup(
    before_markups: number,
    glass_type: string,
    force_tempered: boolean = false
  ): number {
    if (glass_type === 'mirror') {
      return 0;
    }

    if (!force_tempered) {
      return 0;
    }

    const tempered_percent = this.config.markups?.tempered || 0;
    return before_markups * (tempered_percent / 100);
  }

  /**
   * Calculate shape markup
   */
  calculateShapeMarkup(
    before_markups: number,
    is_non_rectangular: boolean = false,
    is_circular: boolean = false
  ): number {
    if (!is_non_rectangular && !is_circular) {
      return 0;
    }

    const shape_percent = this.config.markups?.shape || 0;
    return before_markups * (shape_percent / 100);
  }

  /**
   * Calculate contractor discount (15%)
   */
  calculateContractorDiscount(subtotal: number, is_contractor: boolean = false): number {
    if (!is_contractor) {
      return 0;
    }

    return subtotal * this.CONTRACTOR_DISCOUNT_RATE;
  }

  /**
   * Validate quote parameters against business rules
   */
  validateQuoteParams(
    thickness: string,
    glass_type: string,
    is_polished: boolean,
    is_beveled: boolean,
    is_tempered: boolean,
    num_clipped_corners: number,
    is_circular: boolean
  ): string | null {
    // Rule 1: 1/8" glass cannot have ANY edge work (no polish, no bevel, no tempered)
    if (thickness === '1/8"') {
      if (is_tempered) {
        return '1/8" glass cannot be tempered';
      }
      if (is_polished) {
        return '1/8" glass cannot be polished';
      }
      if (is_beveled) {
        return '1/8" glass cannot have beveled edges';
      }
    }

    // Rule 2: 1/8" glass cannot be mirror
    if (thickness === '1/8"' && glass_type === 'mirror') {
      return '1/8" mirror is not available';
    }

    // Rule 3: Mirrors cannot be tempered
    if (glass_type === 'mirror' && is_tempered) {
      return 'Mirror glass cannot be tempered';
    }

    // Rule 4: Clipped corners only available for non-mirror glass
    if (num_clipped_corners > 0 && glass_type === 'mirror') {
      return 'Clipped corners are not available for mirrors';
    }

    // Rule 5: Clipped corners not available for circular glass
    if (num_clipped_corners > 0 && is_circular) {
      return 'Clipped corners are not available for circular glass';
    }

    return null;
  }

  /**
   * Calculate complete glass quote
   */
  calculateQuote(params: QuoteParams): QuoteResult {
    const {
      width,
      height,
      thickness,
      glass_type,
      quantity = 1,
      is_polished = false,
      is_beveled = false,
      num_clipped_corners = 0,
      clip_size = 'under_1',
      is_tempered = false,
      is_non_rectangular = false,
      is_circular = false,
      diameter,
      is_contractor = false,
    } = params;

    // Validate parameters first
    const validation_error = this.validateQuoteParams(
      thickness,
      glass_type,
      is_polished,
      is_beveled,
      is_tempered,
      num_clipped_corners,
      is_circular
    );

    if (validation_error) {
      return {
        error: validation_error,
        actual_sq_ft: 0,
        billable_sq_ft: 0,
        sq_ft: 0,
        perimeter: 0,
        base_price: 0,
        before_markups: 0,
        subtotal: 0,
        total: 0,
        quote_price: 0,
      };
    }

    // Calculate dimensions
    const sq_ft_result = this.calculateSquareFootage(width, height, is_circular, diameter);
    const actual_sq_ft = sq_ft_result.actual_sq_ft;
    const billable_sq_ft = sq_ft_result.billable_sq_ft;
    const perimeter = this.calculatePerimeter(width, height, is_circular, diameter);

    // Base price using billable sq ft (check if enabled)
    let base_price = 0;
    if (this.formula_config.enable_base_price) {
      base_price = this.calculateBasePrice(thickness, glass_type, billable_sq_ft);
    }

    // Edge processing (check if enabled)
    let polish_price = 0;
    if (is_polished && this.formula_config.enable_polish) {
      const is_flat = glass_type === 'mirror';
      polish_price = this.calculatePolishPrice(thickness, glass_type, perimeter, is_flat);
    }

    let beveled_price = 0;
    if (is_beveled && this.formula_config.enable_beveled) {
      beveled_price = this.calculateBeveledPrice(thickness, perimeter);
    }

    let clipped_corners_price = 0;
    if (num_clipped_corners > 0 && this.formula_config.enable_clipped_corners) {
      clipped_corners_price = this.calculateClippedCornersPrice(
        thickness,
        num_clipped_corners,
        clip_size
      );
    }

    // Before markups subtotal
    const before_markups = base_price + polish_price + beveled_price + clipped_corners_price;

    // Markups (check if enabled)
    let tempered_price = 0;
    if (this.formula_config.enable_tempered_markup) {
      tempered_price = this.calculateTemperedMarkup(before_markups, glass_type, is_tempered);
    }

    let shape_price = 0;
    if (this.formula_config.enable_shape_markup) {
      shape_price = this.calculateShapeMarkup(before_markups, is_non_rectangular, is_circular);
    }

    // Subtotal
    const subtotal = before_markups + tempered_price + shape_price;

    // Contractor discount (check if enabled)
    let contractor_discount = 0;
    if (this.formula_config.enable_contractor_discount) {
      contractor_discount = this.calculateContractorDiscount(subtotal, is_contractor);
    }

    const discounted_subtotal = subtotal - contractor_discount;

    // Final total
    const total = discounted_subtotal * quantity;

    // Quote price (Apply configured formula)
    const quote_price = this.applyPricingFormula(total);

    return {
      actual_sq_ft: Number(actual_sq_ft.toFixed(2)),
      billable_sq_ft: Number(billable_sq_ft.toFixed(2)),
      sq_ft: Number(billable_sq_ft.toFixed(2)), // Backward compatibility
      perimeter: Number(perimeter.toFixed(2)),
      base_price: Number(base_price.toFixed(2)),
      polish_price: polish_price > 0 ? Number(polish_price.toFixed(2)) : undefined,
      beveled_price: beveled_price > 0 ? Number(beveled_price.toFixed(2)) : undefined,
      clipped_corners_price:
        clipped_corners_price > 0 ? Number(clipped_corners_price.toFixed(2)) : undefined,
      before_markups: Number(before_markups.toFixed(2)),
      tempered_price: tempered_price > 0 ? Number(tempered_price.toFixed(2)) : undefined,
      shape_price: shape_price > 0 ? Number(shape_price.toFixed(2)) : undefined,
      subtotal: Number(subtotal.toFixed(2)),
      contractor_discount:
        contractor_discount > 0 ? Number(contractor_discount.toFixed(2)) : undefined,
      discounted_subtotal:
        contractor_discount > 0 ? Number(discounted_subtotal.toFixed(2)) : undefined,
      total: Number(total.toFixed(2)),
      quote_price: Number(quote_price.toFixed(2)),
    };
  }
}
