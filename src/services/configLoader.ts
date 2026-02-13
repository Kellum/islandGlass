import { supabase } from './supabase';
import type { CalculatorConfig } from './calculator';
import type {
  GlassConfigRow,
  MarkupRow,
  BeveledPricingRow,
  ClippedCornersPricingRow,
  CalculatorSettingRow,
  PricingFormulaConfigRow,
} from '../types';

export async function loadCalculatorConfig(): Promise<CalculatorConfig> {
  const [
    glassRes,
    markupsRes,
    beveledRes,
    clippedRes,
    settingsRes,
    formulaRes,
  ] = await Promise.all([
    supabase.from('glass_config').select('*'),
    supabase.from('markups').select('*'),
    supabase.from('beveled_pricing').select('*'),
    supabase.from('clipped_corners_pricing').select('*'),
    supabase.from('calculator_settings').select('*'),
    supabase.from('pricing_formula_config').select('*').eq('is_active', true).limit(1).single(),
  ]);

  // Transform glass_config rows into keyed record
  const glass_config: Record<string, { base_price: number; polish_price: number; only_tempered?: boolean; no_polish?: boolean; never_tempered?: boolean }> = {};
  for (const row of (glassRes.data as GlassConfigRow[]) || []) {
    const key = `${row.thickness}_${row.type}`;
    glass_config[key] = {
      base_price: Number(row.base_price),
      polish_price: Number(row.polish_price),
      only_tempered: row.only_tempered,
      no_polish: row.no_polish,
      never_tempered: row.never_tempered,
    };
  }

  // Transform markups into { tempered: number, shape: number }
  const markups = { tempered: 0, shape: 0 };
  for (const row of (markupsRes.data as MarkupRow[]) || []) {
    if (row.name === 'tempered') markups.tempered = Number(row.percentage);
    if (row.name === 'shape') markups.shape = Number(row.percentage);
  }

  // Transform beveled pricing into keyed record
  const beveled_pricing: Record<string, number> = {};
  for (const row of (beveledRes.data as BeveledPricingRow[]) || []) {
    beveled_pricing[row.glass_thickness] = Number(row.price_per_inch);
  }

  // Transform clipped corners pricing into keyed record
  const clipped_corners_pricing: Record<string, number> = {};
  for (const row of (clippedRes.data as ClippedCornersPricingRow[]) || []) {
    const key = `${row.glass_thickness}_${row.clip_size}`;
    clipped_corners_pricing[key] = Number(row.price_per_corner);
  }

  // Transform settings into object
  const settings = {
    minimum_sq_ft: 3.0,
    markup_divisor: 0.28,
    contractor_discount_rate: 0.15,
    flat_polish_rate: 0.27,
  };
  for (const row of (settingsRes.data as CalculatorSettingRow[]) || []) {
    if (row.key in settings) {
      (settings as Record<string, number>)[row.key] = Number(row.value);
    }
  }

  // Formula config
  const fc = formulaRes.data as PricingFormulaConfigRow | null;
  const formula_config = fc
    ? {
        formula_mode: fc.formula_mode,
        divisor_value: Number(fc.divisor_value),
        multiplier_value: Number(fc.multiplier_value),
        custom_expression: fc.custom_expression,
        enable_base_price: fc.enable_base_price,
        enable_polish: fc.enable_polish,
        enable_beveled: fc.enable_beveled,
        enable_clipped_corners: fc.enable_clipped_corners,
        enable_tempered_markup: fc.enable_tempered_markup,
        enable_shape_markup: fc.enable_shape_markup,
        enable_contractor_discount: fc.enable_contractor_discount,
      }
    : {
        formula_mode: 'divisor' as const,
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

  return {
    glass_config,
    markups,
    beveled_pricing,
    clipped_corners_pricing,
    settings,
    formula_config,
  };
}
