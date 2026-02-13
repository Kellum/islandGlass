// Re-export calculator types from the calculator service
import type { QuoteParams, QuoteResult } from '../services/calculator';
export type {
  GlassConfigItem,
  CalculatorConfig,
  QuoteParams,
  QuoteResult,
} from '../services/calculator';

// Database row types (matching Supabase tables)
export interface GlassConfigRow {
  id: number;
  thickness: string;
  type: string;
  base_price: number;
  polish_price: number;
  only_tempered: boolean;
  no_polish: boolean;
  never_tempered: boolean;
  created_at: string;
  updated_at: string;
}

export interface MarkupRow {
  id: number;
  name: string;
  percentage: number;
}

export interface BeveledPricingRow {
  id: number;
  glass_thickness: string;
  price_per_inch: number;
}

export interface ClippedCornersPricingRow {
  id: number;
  glass_thickness: string;
  clip_size: string;
  price_per_corner: number;
}

export interface CalculatorSettingRow {
  id: number;
  key: string;
  value: number;
}

export interface PricingFormulaConfigRow {
  id: number;
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
  is_active: boolean;
  created_at: string;
}

export interface PricingFormulaAuditRow {
  id: number;
  table_name: string;
  record_id: number | null;
  action: string;
  old_values: Record<string, unknown> | null;
  new_values: Record<string, unknown> | null;
  changed_at: string;
}

export interface AdminConfigRow {
  id: number;
  pin_hash: string;
}

// Quote item for multi-item support
export interface QuoteItem {
  id: string;
  description: string;
  formData: QuoteParams;
  result: QuoteResult;
  widthInput: string;
  heightInput: string;
  diameterInput: string;
}

// Re-export quote types
export type {
  SavedQuote,
  SavedQuoteLineItem,
  SavedQuoteWithItems,
  SaveQuoteFormData,
} from './quote';

// Toast notification
export interface Toast {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}
