import { supabase } from './supabase';
import type {
  GlassConfigRow,
  SupplierRow,
  LocationRow,
  MarkupRow,
  BeveledPricingRow,
  ClippedCornersPricingRow,
  CalculatorSettingRow,
  PricingFormulaConfigRow,
  PricingFormulaAuditRow,
  AdminConfigRow,
} from '../types';

// ---- PIN Validation ----

async function hashPin(pin: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(pin);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}

export async function validatePin(pin: string): Promise<boolean> {
  const pinHash = await hashPin(pin);
  const { data } = await supabase.from('admin_config').select('pin_hash').limit(1).single();
  if (!data) return false;
  return (data as AdminConfigRow).pin_hash === pinHash;
}

export async function updatePin(newPin: string): Promise<void> {
  const pinHash = await hashPin(newPin);
  const { data } = await supabase.from('admin_config').select('id').limit(1).single();
  if (data) {
    await supabase.from('admin_config').update({ pin_hash: pinHash }).eq('id', data.id);
  }
}

// ---- Audit Log ----

async function logAudit(
  tableName: string,
  recordId: number | null,
  action: string,
  oldValues: Record<string, unknown> | null,
  newValues: Record<string, unknown> | null
) {
  await supabase.from('pricing_formula_audit').insert({
    table_name: tableName,
    record_id: recordId,
    action,
    old_values: oldValues,
    new_values: newValues,
  });
}

// ---- Suppliers CRUD ----

export async function getSuppliers(): Promise<SupplierRow[]> {
  const { data, error } = await supabase.from('suppliers').select('*').order('name');
  if (error) throw error;
  return data as SupplierRow[];
}

export async function createSupplier(name: string): Promise<SupplierRow> {
  const { data, error } = await supabase.from('suppliers').insert({ name }).select().single();
  if (error) throw error;
  await logAudit('suppliers', data.id, 'INSERT', null, { name });
  return data as SupplierRow;
}

export async function updateSupplier(id: number, name: string): Promise<SupplierRow> {
  const { data: old } = await supabase.from('suppliers').select('*').eq('id', id).single();
  const { data, error } = await supabase.from('suppliers').update({ name }).eq('id', id).select().single();
  if (error) throw error;
  await logAudit('suppliers', id, 'UPDATE', old as Record<string, unknown>, { name });
  return data as SupplierRow;
}

export async function deleteSupplier(id: number): Promise<void> {
  const { data: old } = await supabase.from('suppliers').select('*').eq('id', id).single();
  const { error } = await supabase.from('suppliers').delete().eq('id', id);
  if (error) throw error;
  await logAudit('suppliers', id, 'DELETE', old as Record<string, unknown>, null);
}

// ---- Locations CRUD ----

export async function getLocations(): Promise<LocationRow[]> {
  const { data, error } = await supabase.from('locations').select('*').order('name');
  if (error) throw error;
  return data as LocationRow[];
}

export async function createLocation(name: string, location_number: number): Promise<LocationRow> {
  const { data, error } = await supabase
    .from('locations')
    .insert({ name, location_number })
    .select()
    .single();
  if (error) throw error;
  await logAudit('locations', data.id, 'INSERT', null, { name, location_number });
  return data as LocationRow;
}

export async function updateLocation(id: number, name: string, location_number: number): Promise<LocationRow> {
  const { data: old } = await supabase.from('locations').select('*').eq('id', id).single();
  const { data, error } = await supabase
    .from('locations')
    .update({ name, location_number })
    .eq('id', id)
    .select()
    .single();
  if (error) throw error;
  await logAudit('locations', id, 'UPDATE', old as Record<string, unknown>, { name, location_number });
  return data as LocationRow;
}

export async function deleteLocation(id: number): Promise<void> {
  const { data: old } = await supabase.from('locations').select('*').eq('id', id).single();
  const { error } = await supabase.from('locations').delete().eq('id', id);
  if (error) throw error;
  await logAudit('locations', id, 'DELETE', old as Record<string, unknown>, null);
}

// ---- Glass Config CRUD ----

export async function getGlassConfigs(): Promise<GlassConfigRow[]> {
  const { data, error } = await supabase.from('glass_config').select('*').order('id');
  if (error) throw error;
  return data as GlassConfigRow[];
}

export async function createGlassConfig(
  config: Omit<GlassConfigRow, 'id' | 'created_at' | 'updated_at'>
): Promise<GlassConfigRow> {
  const { data, error } = await supabase.from('glass_config').insert(config).select().single();
  if (error) throw error;
  await logAudit('glass_config', data.id, 'INSERT', null, config as unknown as Record<string, unknown>);
  return data as GlassConfigRow;
}

export async function updateGlassConfig(
  id: number,
  updates: Partial<GlassConfigRow>
): Promise<GlassConfigRow> {
  // Fetch old values for audit
  const { data: old } = await supabase.from('glass_config').select('*').eq('id', id).single();

  const { data, error } = await supabase
    .from('glass_config')
    .update(updates)
    .eq('id', id)
    .select()
    .single();
  if (error) throw error;
  await logAudit('glass_config', id, 'UPDATE', old as Record<string, unknown>, updates as Record<string, unknown>);
  return data as GlassConfigRow;
}

export async function deleteGlassConfig(id: number): Promise<void> {
  const { data: old } = await supabase.from('glass_config').select('*').eq('id', id).single();
  const { error } = await supabase.from('glass_config').delete().eq('id', id);
  if (error) throw error;
  await logAudit('glass_config', id, 'DELETE', old as Record<string, unknown>, null);
}

// ---- Markups CRUD ----

export async function getMarkups(): Promise<MarkupRow[]> {
  const { data, error } = await supabase.from('markups').select('*').order('id');
  if (error) throw error;
  return data as MarkupRow[];
}

export async function updateMarkup(id: number, percentage: number): Promise<void> {
  const { data: old } = await supabase.from('markups').select('*').eq('id', id).single();
  const { error } = await supabase.from('markups').update({ percentage }).eq('id', id);
  if (error) throw error;
  await logAudit('markups', id, 'UPDATE', old as Record<string, unknown>, { percentage });
}

// ---- Beveled Pricing CRUD ----

export async function getBeveledPricing(): Promise<BeveledPricingRow[]> {
  const { data, error } = await supabase.from('beveled_pricing').select('*').order('id');
  if (error) throw error;
  return data as BeveledPricingRow[];
}

export async function updateBeveledPricing(id: number, price_per_inch: number): Promise<void> {
  const { data: old } = await supabase.from('beveled_pricing').select('*').eq('id', id).single();
  const { error } = await supabase.from('beveled_pricing').update({ price_per_inch }).eq('id', id);
  if (error) throw error;
  await logAudit('beveled_pricing', id, 'UPDATE', old as Record<string, unknown>, { price_per_inch });
}

// ---- Clipped Corners Pricing CRUD ----

export async function getClippedCornersPricing(): Promise<ClippedCornersPricingRow[]> {
  const { data, error } = await supabase.from('clipped_corners_pricing').select('*').order('id');
  if (error) throw error;
  return data as ClippedCornersPricingRow[];
}

export async function updateClippedCornersPricing(
  id: number,
  price_per_corner: number
): Promise<void> {
  const { data: old } = await supabase
    .from('clipped_corners_pricing')
    .select('*')
    .eq('id', id)
    .single();
  const { error } = await supabase
    .from('clipped_corners_pricing')
    .update({ price_per_corner })
    .eq('id', id);
  if (error) throw error;
  await logAudit('clipped_corners_pricing', id, 'UPDATE', old as Record<string, unknown>, { price_per_corner });
}

// ---- Calculator Settings CRUD ----

export async function getCalculatorSettings(): Promise<CalculatorSettingRow[]> {
  const { data, error } = await supabase.from('calculator_settings').select('*').order('id');
  if (error) throw error;
  return data as CalculatorSettingRow[];
}

export async function updateCalculatorSetting(id: number, value: number): Promise<void> {
  const { data: old } = await supabase
    .from('calculator_settings')
    .select('*')
    .eq('id', id)
    .single();
  const { error } = await supabase.from('calculator_settings').update({ value }).eq('id', id);
  if (error) throw error;
  await logAudit('calculator_settings', id, 'UPDATE', old as Record<string, unknown>, { value });
}

// ---- Formula Config CRUD ----

export async function getFormulaConfig(): Promise<PricingFormulaConfigRow | null> {
  const { data, error } = await supabase
    .from('pricing_formula_config')
    .select('*')
    .eq('is_active', true)
    .limit(1)
    .single();
  if (error) return null;
  return data as PricingFormulaConfigRow;
}

export async function updateFormulaConfig(
  updates: Partial<PricingFormulaConfigRow>
): Promise<void> {
  // Deactivate current active config
  const { data: old } = await supabase
    .from('pricing_formula_config')
    .select('*')
    .eq('is_active', true)
    .limit(1)
    .single();

  if (old) {
    await supabase
      .from('pricing_formula_config')
      .update({ is_active: false })
      .eq('id', old.id);

    // Insert new version
    const newConfig = {
      formula_mode: updates.formula_mode ?? old.formula_mode,
      divisor_value: updates.divisor_value ?? old.divisor_value,
      multiplier_value: updates.multiplier_value ?? old.multiplier_value,
      custom_expression: updates.custom_expression ?? old.custom_expression,
      enable_base_price: updates.enable_base_price ?? old.enable_base_price,
      enable_polish: updates.enable_polish ?? old.enable_polish,
      enable_beveled: updates.enable_beveled ?? old.enable_beveled,
      enable_clipped_corners: updates.enable_clipped_corners ?? old.enable_clipped_corners,
      enable_tempered_markup: updates.enable_tempered_markup ?? old.enable_tempered_markup,
      enable_shape_markup: updates.enable_shape_markup ?? old.enable_shape_markup,
      enable_contractor_discount:
        updates.enable_contractor_discount ?? old.enable_contractor_discount,
      is_active: true,
    };

    const { error } = await supabase.from('pricing_formula_config').insert(newConfig);
    if (error) throw error;
    await logAudit('pricing_formula_config', old.id, 'UPDATE', old as Record<string, unknown>, newConfig);
  }
}

// ---- Audit Log ----

export async function getAuditLog(limit: number = 50): Promise<PricingFormulaAuditRow[]> {
  const { data, error } = await supabase
    .from('pricing_formula_audit')
    .select('*')
    .order('changed_at', { ascending: false })
    .limit(limit);
  if (error) throw error;
  return data as PricingFormulaAuditRow[];
}
