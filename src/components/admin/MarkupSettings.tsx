import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, DollarSign, Percent, Ruler, ToggleLeft } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card, CardContent } from '../ui/Card';
import { Spinner } from '../ui/Spinner';
import { Toggle } from '../ui/Toggle';
import {
  getMarkups,
  updateMarkup,
  getCalculatorSettings,
  updateCalculatorSetting,
  getFormulaConfig,
  updateFormulaConfig,
} from '../../services/adminApi';
import type { MarkupRow, CalculatorSettingRow, PricingFormulaConfigRow } from '../../types';

interface MarkupSettingsProps {
  onToast: (type: 'success' | 'error', message: string) => void;
}

function formatDollars(value: number): string {
  return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function MarkupSettings({ onToast }: MarkupSettingsProps) {
  const [markups, setMarkups] = useState<MarkupRow[]>([]);
  const [settings, setSettings] = useState<CalculatorSettingRow[]>([]);
  const [formula, setFormula] = useState<PricingFormulaConfigRow | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showCheck, setShowCheck] = useState(false);
  const [markupMode, setMarkupMode] = useState<'percentage' | 'dollar'>('percentage');

  useEffect(() => {
    (async () => {
      try {
        const [m, s, f] = await Promise.all([
          getMarkups(),
          getCalculatorSettings(),
          getFormulaConfig(),
        ]);
        setMarkups(m);
        setSettings(s);
        setFormula(f);
      } catch {
        onToast('error', 'Failed to load settings');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Helper to find a setting by key
  const getSetting = (key: string) => settings.find((s) => s.key === key);
  const updateSettingValue = (key: string, value: number) => {
    setSettings((prev) =>
      prev.map((s) => (s.key === key ? { ...s, value } : s))
    );
  };

  // Helper to find a markup by name
  const getMarkup = (name: string) => markups.find((m) => m.name === name);
  const updateMarkupValue = (name: string, percentage: number) => {
    setMarkups((prev) =>
      prev.map((m) => (m.name === name ? { ...m, percentage } : m))
    );
  };

  // Markup mode: percentage means "mark up by X%" (e.g. 257% → sell = cost × 3.57)
  //              dollar means "for every $1 of cost, charge $X" (e.g. $3.57)
  // Both convert to divisor_value = 1 / multiplier
  const handleMarkupChange = (rawValue: string) => {
    const num = parseFloat(rawValue);
    if (markupMode === 'percentage') {
      // percentage → multiplier = 1 + pct/100 → divisor = 1/multiplier
      if (!isNaN(num) && num > 0) {
        const multiplier = 1 + num / 100;
        setFormula((f) =>
          f ? { ...f, divisor_value: parseFloat((1 / multiplier).toFixed(6)) } : f
        );
      } else {
        setFormula((f) => (f ? { ...f, divisor_value: 0 } : f));
      }
    } else {
      // dollar multiplier → divisor = 1/multiplier
      if (!isNaN(num) && num > 0) {
        setFormula((f) =>
          f ? { ...f, divisor_value: parseFloat((1 / num).toFixed(6)) } : f
        );
      } else {
        setFormula((f) => (f ? { ...f, divisor_value: 0 } : f));
      }
    }
  };

  // Display values derived from the divisor
  const currentMultiplierRaw = formula && formula.divisor_value > 0 ? 1 / formula.divisor_value : 0;
  const markupDisplayValue =
    formula && formula.divisor_value > 0
      ? markupMode === 'percentage'
        ? ((1 / formula.divisor_value - 1) * 100).toFixed(0)
        : (1 / formula.divisor_value).toFixed(2)
      : '';

  const saveAll = async () => {
    if (!formula) return;
    setSaving(true);
    try {
      // 1. Save formula config (includes toggles)
      await updateFormulaConfig({
        formula_mode: formula.formula_mode,
        divisor_value: formula.divisor_value,
        multiplier_value: formula.multiplier_value,
        custom_expression: formula.custom_expression,
        enable_base_price: formula.enable_base_price,
        enable_polish: formula.enable_polish,
        enable_beveled: formula.enable_beveled,
        enable_clipped_corners: formula.enable_clipped_corners,
        enable_tempered_markup: formula.enable_tempered_markup,
        enable_shape_markup: formula.enable_shape_markup,
        enable_contractor_discount: formula.enable_contractor_discount,
      });

      // 2. Save markups
      for (const m of markups) {
        await updateMarkup(m.id, m.percentage);
      }

      // 3. Save calculator settings
      for (const s of settings) {
        await updateCalculatorSetting(s.id, s.value);
      }

      onToast('success', 'All settings saved');
      setShowCheck(true);
      setTimeout(() => setShowCheck(false), 2500);
    } catch {
      onToast('error', 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  const temperedMarkup = getMarkup('tempered');
  const shapeMarkup = getMarkup('shape');
  const minSqFt = getSetting('minimum_sq_ft');
  const contractorRate = getSetting('contractor_discount_rate');
  const polishRate = getSetting('flat_polish_rate');

  const toggleItems: { key: keyof PricingFormulaConfigRow; label: string }[] = [
    { key: 'enable_base_price', label: 'Include glass cost' },
    { key: 'enable_polish', label: 'Include polishing' },
    { key: 'enable_beveled', label: 'Include beveled edges' },
    { key: 'enable_clipped_corners', label: 'Include clipped corners' },
    { key: 'enable_tempered_markup', label: 'Include tempered markup' },
    { key: 'enable_shape_markup', label: 'Include shape markup' },
    { key: 'enable_contractor_discount', label: 'Include contractor discount' },
  ];

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Section 1: Your Markup */}
      <Card>
        <CardContent>
          <div className="flex items-center gap-2 mb-4">
            <DollarSign className="w-5 h-5 text-primary-600" />
            <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">Your Markup</h3>
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            How much do you mark up on cost?
          </p>

          {/* Mode picker */}
          <div className="inline-flex rounded-lg border border-gray-200 dark:border-gray-700 p-0.5 mb-4">
            <button
              type="button"
              onClick={() => setMarkupMode('percentage')}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                markupMode === 'percentage'
                  ? 'bg-primary-600 text-white font-medium'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              Percentage
            </button>
            <button
              type="button"
              onClick={() => setMarkupMode('dollar')}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                markupMode === 'dollar'
                  ? 'bg-primary-600 text-white font-medium'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              Dollar
            </button>
          </div>

          <div className="flex items-center gap-3 mb-4">
            {markupMode === 'percentage' ? (
              <>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
                  Mark up by
                </label>
                <input
                  type="number"
                  step="1"
                  min="0"
                  value={markupDisplayValue}
                  onChange={(e) => handleMarkupChange(e.target.value)}
                  className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm w-24 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-900 dark:text-gray-100"
                />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">%</span>
              </>
            ) : (
              <>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
                  For every $1 of cost, charge:
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 text-sm">$</span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={markupDisplayValue}
                    onChange={(e) => handleMarkupChange(e.target.value)}
                    className="border border-gray-300 dark:border-gray-600 rounded-lg pl-7 pr-3 py-2 text-sm w-28 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-900 dark:text-gray-100"
                  />
                </div>
              </>
            )}
          </div>

          {currentMultiplierRaw > 0 && (
            <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-100 dark:border-blue-800 rounded-lg p-4">
              <p className="text-sm text-blue-900 dark:text-blue-200">
                <span className="font-medium">Example:</span> If glass costs you{' '}
                <span className="font-semibold">$10.00</span>
              </p>
              <p className="text-sm text-blue-900 dark:text-blue-200 mt-1">
                You charge the customer:{' '}
                <span className="font-semibold text-blue-700 dark:text-blue-300">
                  ${formatDollars(10 * currentMultiplierRaw)}
                </span>
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Section 2: Extra Charges */}
      <Card>
        <CardContent>
          <div className="flex items-center gap-2 mb-4">
            <Percent className="w-5 h-5 text-primary-600" />
            <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">Extra Charges</h3>
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Extra charges for special glass types and shapes.
          </p>

          <div className="space-y-5">
            {/* Tempered */}
            {temperedMarkup && (
              <div>
                <div className="flex items-center gap-3">
                  <label className="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap">
                    Tempered glass adds
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={temperedMarkup.percentage}
                    onChange={(e) =>
                      updateMarkupValue('tempered', parseFloat(e.target.value) || 0)
                    }
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm w-20 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-900 dark:text-gray-100"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">% to the price</span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 ml-1">
                  A $100 piece of tempered glass would cost{' '}
                  <span className="font-medium">
                    ${formatDollars(100 * (1 + temperedMarkup.percentage / 100))}
                  </span>
                </p>
              </div>
            )}

            {/* Shape */}
            {shapeMarkup && (
              <div>
                <div className="flex items-center gap-3">
                  <label className="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap">
                    Custom/circular shapes add
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={shapeMarkup.percentage}
                    onChange={(e) =>
                      updateMarkupValue('shape', parseFloat(e.target.value) || 0)
                    }
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm w-20 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-900 dark:text-gray-100"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">% to the price</span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 ml-1">
                  A $100 custom-shape piece would cost{' '}
                  <span className="font-medium">
                    ${formatDollars(100 * (1 + shapeMarkup.percentage / 100))}
                  </span>
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Section 3: Pricing Rules */}
      <Card>
        <CardContent>
          <div className="flex items-center gap-2 mb-4">
            <Ruler className="w-5 h-5 text-primary-600" />
            <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">Pricing Rules</h3>
          </div>

          <div className="space-y-5">
            {/* Minimum sq ft */}
            {minSqFt && (
              <div>
                <div className="flex items-center gap-3">
                  <label className="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap">
                    Minimum charge:
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={minSqFt.value}
                    onChange={(e) =>
                      updateSettingValue('minimum_sq_ft', parseFloat(e.target.value) || 0)
                    }
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm w-20 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-900 dark:text-gray-100"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">square feet</span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 ml-1">
                  Even if the piece is smaller, charge for at least this many square feet.
                </p>
              </div>
            )}

            {/* Contractor discount */}
            {contractorRate && (
              <div>
                <div className="flex items-center gap-3">
                  <label className="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap">
                    Contractor discount:
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    max="100"
                    value={Math.round(contractorRate.value * 100)}
                    onChange={(e) =>
                      updateSettingValue(
                        'contractor_discount_rate',
                        (parseFloat(e.target.value) || 0) / 100
                      )
                    }
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm w-20 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-900 dark:text-gray-100"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">%</span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 ml-1">
                  Contractors get this percentage off the retail price.
                </p>
              </div>
            )}

            {/* Polish rate */}
            {polishRate && (
              <div>
                <div className="flex items-center gap-3">
                  <label className="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap">
                    Mirror polish rate per inch:
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 text-sm">$</span>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={polishRate.value}
                      onChange={(e) =>
                        updateSettingValue(
                          'flat_polish_rate',
                          parseFloat(e.target.value) || 0
                        )
                      }
                      className="border border-gray-300 dark:border-gray-600 rounded-lg pl-7 pr-3 py-2 text-sm w-24 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-900 dark:text-gray-100"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Section 4: What's included */}
      <Card>
        <CardContent>
          <div className="flex items-center gap-2 mb-4">
            <ToggleLeft className="w-5 h-5 text-primary-600" />
            <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">
              What goes into the price?
            </h3>
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            Enable or disable each component of the pricing calculation.
          </p>

          <div className="space-y-1">
            {toggleItems.map(({ key, label }) => (
              <Toggle
                key={key}
                checked={(formula?.[key] as boolean) ?? true}
                onChange={(checked) =>
                  setFormula((f) => (f ? { ...f, [key]: checked } : f))
                }
                label={label}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Single Save Button */}
      <div className="sticky bottom-4 flex justify-end">
        <Button
          onClick={saveAll}
          disabled={saving}
          className="shadow-lg px-6"
        >
          {saving ? (
            <span className="flex items-center gap-2">
              <Spinner size="sm" />
              Saving…
            </span>
          ) : showCheck ? (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="flex items-center gap-1"
            >
              <Check className="w-4 h-4" /> Saved!
            </motion.span>
          ) : (
            'Save All Settings'
          )}
        </Button>
      </div>
    </div>
  );
}
