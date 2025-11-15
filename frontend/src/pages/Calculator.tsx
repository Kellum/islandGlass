import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { GlassPriceCalculator } from '../services/calculator';
import type { CalculatorConfig, QuoteParams } from '../services/calculator';

// In production, the backend serves the frontend, so use relative URLs
// In development, use localhost:8000
const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '');

const Calculator = () => {
  const [config, setConfig] = useState<CalculatorConfig | null>(null);
  const [loading, setLoading] = useState(true);

  // Form state
  const [formData, setFormData] = useState<QuoteParams>({
    width: 24,
    height: 36,
    thickness: '1/4"',
    glass_type: 'clear',
    quantity: 1,
    is_polished: false,
    is_beveled: false,
    num_clipped_corners: 0,
    clip_size: 'under_1',
    is_tempered: false,
    is_non_rectangular: false,
    is_circular: false,
    is_contractor: false,
  });

  // Fetch config on mount
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get(`${API_URL}/api/v1/calculator/config`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setConfig(response.data);
      } catch (error) {
        console.error('Error fetching calculator config:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []);

  // Calculate price on every form change
  const result = useMemo(() => {
    if (!config) return null;
    const calculator = new GlassPriceCalculator(config);
    return calculator.calculateQuote(formData);
  }, [config, formData]);

  const updateField = <K extends keyof QuoteParams>(field: K, value: QuoteParams[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const showMinimumWarning =
    result && result.actual_sq_ft < (config?.settings.minimum_sq_ft || 3.0);

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Glass Price Calculator</h1>
        <p className="mt-1 text-sm text-gray-500">Calculate quotes for glass orders</p>
      </div>

      {/* Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-7 gap-6">
        {/* Left Column - Form (4/7) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Basic Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h2>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Glass Type
                </label>
                <select
                  value={formData.glass_type}
                  onChange={(e) => updateField('glass_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="clear">Clear</option>
                  <option value="bronze">Bronze</option>
                  <option value="gray">Gray</option>
                  <option value="mirror">Mirror</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Thickness
                </label>
                <select
                  value={formData.thickness}
                  onChange={(e) => updateField('thickness', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value='1/8"'>1/8"</option>
                  <option value='3/16"'>3/16"</option>
                  <option value='1/4"'>1/4"</option>
                  <option value='3/8"'>3/8"</option>
                  <option value='1/2"'>1/2"</option>
                </select>
              </div>
            </div>

            <div className="mt-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_contractor}
                  onChange={(e) => updateField('is_contractor', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Contractor Pricing (15% discount)</span>
              </label>
            </div>
          </div>

          {/* Dimensions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Dimensions</h2>

            {/* Shape Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Shape</label>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    updateField('is_circular', false);
                    updateField('is_non_rectangular', false);
                  }}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium ${
                    !formData.is_circular && !formData.is_non_rectangular
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Rectangular
                </button>
                <button
                  onClick={() => {
                    updateField('is_circular', true);
                    updateField('is_non_rectangular', false);
                  }}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium ${
                    formData.is_circular
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Circular
                </button>
                <button
                  onClick={() => {
                    updateField('is_circular', false);
                    updateField('is_non_rectangular', true);
                  }}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium ${
                    formData.is_non_rectangular && !formData.is_circular
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Custom
                </button>
              </div>
            </div>

            {formData.is_circular ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Diameter (inches)
                </label>
                <input
                  type="number"
                  value={formData.diameter || 24}
                  onChange={(e) => updateField('diameter', Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                  step="0.125"
                />
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Width (inches)
                  </label>
                  <input
                    type="number"
                    value={formData.width}
                    onChange={(e) => updateField('width', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                    step="0.125"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Height (inches)
                  </label>
                  <input
                    type="number"
                    value={formData.height}
                    onChange={(e) => updateField('height', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                    step="0.125"
                  />
                </div>
              </div>
            )}

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
              <input
                type="number"
                value={formData.quantity}
                onChange={(e) => updateField('quantity', Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
              />
            </div>

            {showMinimumWarning && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                <p className="text-sm text-yellow-800">
                  {result?.actual_sq_ft.toFixed(2)} sq ft - Minimum charge of{' '}
                  {config?.settings.minimum_sq_ft} sq ft applies
                </p>
              </div>
            )}
          </div>

          {/* Edge Processing */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Edge Processing</h2>

            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_polished}
                  onChange={(e) => updateField('is_polished', e.target.checked)}
                  disabled={formData.thickness === '1/8"'}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
                />
                <span className="ml-2 text-sm text-gray-700">Polished Edges</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_beveled}
                  onChange={(e) => updateField('is_beveled', e.target.checked)}
                  disabled={formData.thickness === '1/8"'}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
                />
                <span className="ml-2 text-sm text-gray-700">Beveled Edges</span>
              </label>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Clipped Corners
                  </label>
                  <input
                    type="number"
                    value={formData.num_clipped_corners}
                    onChange={(e) => updateField('num_clipped_corners', Number(e.target.value))}
                    disabled={formData.is_circular || formData.glass_type === 'mirror'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    min="0"
                    max="4"
                  />
                </div>
                {formData.num_clipped_corners! > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Clip Size
                    </label>
                    <select
                      value={formData.clip_size}
                      onChange={(e) => updateField('clip_size', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="under_1">Under 1"</option>
                      <option value="over_1">Over 1"</option>
                    </select>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Additional Options */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Additional Options</h2>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_tempered}
                onChange={(e) => updateField('is_tempered', e.target.checked)}
                disabled={formData.thickness === '1/8"' || formData.glass_type === 'mirror'}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
              />
              <span className="ml-2 text-sm text-gray-700">Tempered Glass</span>
            </label>
          </div>
        </div>

        {/* Right Column - Price Summary (3/7) */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow p-6 sticky top-4">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Price Summary</h2>

            {result?.error ? (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800">{result.error}</p>
              </div>
            ) : result ? (
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Area:</span>
                  <span className="font-medium text-gray-900">{result.billable_sq_ft} sq ft</span>
                </div>

                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Base Price:</span>
                  <span className="font-medium text-gray-900">${result.base_price.toFixed(2)}</span>
                </div>

                {result.polish_price && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Polish:</span>
                    <span className="font-medium text-gray-900">
                      ${result.polish_price.toFixed(2)}
                    </span>
                  </div>
                )}

                {result.beveled_price && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Beveled:</span>
                    <span className="font-medium text-gray-900">
                      ${result.beveled_price.toFixed(2)}
                    </span>
                  </div>
                )}

                {result.clipped_corners_price && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Clipped Corners:</span>
                    <span className="font-medium text-gray-900">
                      ${result.clipped_corners_price.toFixed(2)}
                    </span>
                  </div>
                )}

                {result.tempered_price && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Tempered (35%):</span>
                    <span className="font-medium text-gray-900">
                      ${result.tempered_price.toFixed(2)}
                    </span>
                  </div>
                )}

                {result.shape_price && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Shape Markup (25%):</span>
                    <span className="font-medium text-gray-900">
                      ${result.shape_price.toFixed(2)}
                    </span>
                  </div>
                )}

                <div className="border-t border-gray-200 pt-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Subtotal:</span>
                    <span className="font-medium text-gray-900">${result.subtotal.toFixed(2)}</span>
                  </div>
                </div>

                {result.contractor_discount && (
                  <div className="flex justify-between text-sm text-green-600">
                    <span>Contractor Discount (15%):</span>
                    <span className="font-medium">-${result.contractor_discount.toFixed(2)}</span>
                  </div>
                )}

                <div className="border-t border-gray-200 pt-3">
                  <div className="flex justify-between">
                    <span className="text-lg font-semibold text-gray-900">Quote Price:</span>
                    <span className="text-2xl font-bold text-blue-600">
                      ${result.quote_price.toFixed(2)}
                    </span>
                  </div>
                </div>

                {formData.quantity! > 1 && (
                  <div className="text-xs text-gray-500 text-center pt-2">
                    For quantity of {formData.quantity}
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Calculator;
