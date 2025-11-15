import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { GlassPriceCalculator } from '../services/calculator';
import type { CalculatorConfig, QuoteParams, QuoteResult } from '../services/calculator';
import { fractionToDecimal, decimalToFraction } from '../utils/fractions';

// In production, the backend serves the frontend, so use relative URLs
// In development, use localhost:8000
const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '');

interface SavedItem {
  id: string;
  description: string;
  formData: QuoteParams;
  result: QuoteResult;
  widthInput: string;
  heightInput: string;
  diameterInput: string;
}

const Calculator = () => {
  const [config, setConfig] = useState<CalculatorConfig | null>(null);
  const [loading, setLoading] = useState(true);

  // Fraction input strings (what the user types)
  const [widthInput, setWidthInput] = useState('');
  const [heightInput, setHeightInput] = useState('');
  const [diameterInput, setDiameterInput] = useState('');

  // Form state (with decimal values for calculation)
  const [formData, setFormData] = useState<QuoteParams>({
    width: 0,
    height: 0,
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

  // Multiple items state
  const [items, setItems] = useState<SavedItem[]>([]);
  const [isItemsExpanded, setIsItemsExpanded] = useState(true);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

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

    // Don't calculate if no dimensions entered yet (better UX)
    const hasValidDimensions = formData.is_circular
      ? (formData.diameter && formData.diameter > 0)
      : (formData.width && formData.width > 0 && formData.height && formData.height > 0);

    if (!hasValidDimensions) return null;

    const calculator = new GlassPriceCalculator(config);
    return calculator.calculateQuote(formData);
  }, [config, formData]);

  const updateField = <K extends keyof QuoteParams>(field: K, value: QuoteParams[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Handle fraction input changes
  const handleWidthChange = (input: string) => {
    setWidthInput(input);
    const decimal = fractionToDecimal(input);
    setFormData((prev) => ({ ...prev, width: decimal }));
  };

  const handleHeightChange = (input: string) => {
    setHeightInput(input);
    const decimal = fractionToDecimal(input);
    setFormData((prev) => ({ ...prev, height: decimal }));
  };

  const handleDiameterChange = (input: string) => {
    setDiameterInput(input);
    const decimal = fractionToDecimal(input);
    setFormData((prev) => ({ ...prev, diameter: decimal }));
  };

  // Add current item to the list
  const handleAddItem = () => {
    if (!result || result.error) return;

    // Generate description
    let description = '';
    if (formData.is_circular && formData.diameter) {
      description = `${diameterInput}" Ø ${formData.thickness} ${formData.glass_type}`;
    } else {
      description = `${widthInput}" × ${heightInput}" ${formData.thickness} ${formData.glass_type}`;
    }

    const newItem: SavedItem = {
      id: Date.now().toString(),
      description,
      formData: { ...formData },
      result: { ...result },
      widthInput,
      heightInput,
      diameterInput,
    };

    setItems((prev) => [...prev, newItem]);
    // Add new item to expanded set (open by default)
    setExpandedItems((prev) => new Set(prev).add(newItem.id));

    // Reset form to defaults
    setWidthInput('');
    setHeightInput('');
    setDiameterInput('');
    setFormData({
      width: 0,
      height: 0,
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
      is_contractor: formData.is_contractor, // Keep contractor status
    });
  };

  // Remove an item from the list
  const handleRemoveItem = (id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
    setExpandedItems((prev) => {
      const newSet = new Set(prev);
      newSet.delete(id);
      return newSet;
    });
  };

  // Toggle individual item expansion
  const toggleItemExpansion = (id: string) => {
    setExpandedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  // Calculate total for all items
  const totalPrice = useMemo(() => {
    return items.reduce((sum, item) => sum + item.result.quote_price, 0);
  }, [items]);

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

            <div className="mt-4 space-y-3">
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
                  type="text"
                  value={diameterInput}
                  onChange={(e) => handleDiameterChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder='e.g., 24, 24 1/2, 3/4'
                />
                <p className="mt-1 text-xs text-gray-500">Enter as fraction (e.g., 24 1/2) or decimal</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Width (inches)
                  </label>
                  <input
                    type="text"
                    value={widthInput}
                    onChange={(e) => handleWidthChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder='e.g., 24, 24 1/2, 3/4'
                  />
                  <p className="mt-1 text-xs text-gray-500">Enter as fraction (e.g., 24 1/2) or decimal</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Height (inches)
                  </label>
                  <input
                    type="text"
                    value={heightInput}
                    onChange={(e) => handleHeightChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder='e.g., 36, 36 3/4, 1/2'
                  />
                  <p className="mt-1 text-xs text-gray-500">Enter as fraction (e.g., 36 1/4) or decimal</p>
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

          {/* Add Item Button */}
          <div className="bg-white rounded-lg shadow p-6">
            <button
              onClick={handleAddItem}
              disabled={!result || !!result?.error}
              className="w-full py-3 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium rounded-md transition-colors"
            >
              Add Item to Quote
            </button>
            <p className="mt-2 text-xs text-gray-500 text-center">
              Add this item and continue adding more pieces
            </p>
          </div>
        </div>

        {/* Right Column - Price Summary (3/7) */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow p-6 sticky top-4">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              {items.length > 0 ? 'Current Item' : 'Price Summary'}
            </h2>

            {!result ? (
              <div className="p-4 bg-gray-50 border border-gray-200 rounded-md text-center">
                <p className="text-sm text-gray-600">
                  Enter dimensions to see pricing
                </p>
              </div>
            ) : result?.error ? (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800">{result.error}</p>
              </div>
            ) : result ? (
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Area:</span>
                  <span className="font-medium text-gray-900">
                    {decimalToFraction(result.billable_sq_ft)} sq ft
                  </span>
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

            {/* Combined Total for Multiple Items */}
            {items.length > 0 && (
              <>
                <div className="mt-6 pt-6 border-t-2 border-gray-300">
                  <h3 className="text-md font-semibold text-gray-900 mb-3">Quote Total</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Items in quote:</span>
                      <span className="font-medium text-gray-900">{items.length}</span>
                    </div>
                    {result && !result.error && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Current item:</span>
                        <span className="font-medium text-gray-900">
                          ${result.quote_price.toFixed(2)}
                        </span>
                      </div>
                    )}
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Saved items total:</span>
                      <span className="font-medium text-gray-900">${totalPrice.toFixed(2)}</span>
                    </div>
                    <div className="border-t border-gray-200 pt-2">
                      <div className="flex justify-between">
                        <span className="text-lg font-bold text-gray-900">Grand Total:</span>
                        <span className="text-2xl font-bold text-blue-600">
                          ${(totalPrice + (result && !result.error ? result.quote_price : 0)).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Items List Accordion */}
                <div className="mt-4 border-t border-gray-200 pt-4">
                  <button
                    onClick={() => setIsItemsExpanded(!isItemsExpanded)}
                    className="w-full flex items-center justify-between text-left"
                  >
                    <h3 className="text-sm font-semibold text-gray-900">
                      Line Items ({items.length})
                    </h3>
                    <svg
                      className={`w-5 h-5 text-gray-600 transition-transform ${
                        isItemsExpanded ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </button>

                  {isItemsExpanded && (
                    <div className="mt-3 space-y-3">
                      {items.map((item, index) => {
                        const isItemExpanded = expandedItems.has(item.id);
                        return (
                          <div
                            key={item.id}
                            className="p-3 bg-gray-50 rounded border border-gray-200"
                          >
                            <div className="flex items-start justify-between mb-2">
                              <button
                                onClick={() => toggleItemExpansion(item.id)}
                                className="flex-1 flex items-start gap-2 text-left hover:bg-gray-100 -m-1 p-1 rounded"
                              >
                                <svg
                                  className={`w-4 h-4 text-gray-600 transition-transform flex-shrink-0 mt-0.5 ${
                                    isItemExpanded ? 'rotate-90' : ''
                                  }`}
                                  fill="none"
                                  stroke="currentColor"
                                  viewBox="0 0 24 24"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M9 5l7 7-7 7"
                                  />
                                </svg>
                                <div className="flex-1">
                                  <p className="text-xs font-semibold text-gray-900">
                                    {index + 1}. {item.description}
                                  </p>
                                  {item.formData.quantity > 1 && (
                                    <p className="text-xs text-gray-600">Qty: {item.formData.quantity}</p>
                                  )}
                                  {!isItemExpanded && (
                                    <p className="text-xs font-semibold text-gray-900 mt-1">
                                      ${item.result.quote_price.toFixed(2)}
                                    </p>
                                  )}
                                </div>
                              </button>
                              <button
                                onClick={() => handleRemoveItem(item.id)}
                                className="text-red-600 hover:text-red-800 text-xs ml-2"
                                title="Remove item"
                              >
                                ✕
                              </button>
                            </div>

                            {/* Price Breakdown */}
                            {isItemExpanded && (
                              <div className="space-y-1 pl-3 border-l-2 border-gray-300">
                            <div className="flex justify-between text-xs">
                              <span className="text-gray-600">Area:</span>
                              <span className="text-gray-900">
                                {decimalToFraction(item.result.billable_sq_ft)} sq ft
                              </span>
                            </div>

                            <div className="flex justify-between text-xs">
                              <span className="text-gray-600">Base Price:</span>
                              <span className="text-gray-900">${item.result.base_price.toFixed(2)}</span>
                            </div>

                            {item.result.polish_price && (
                              <div className="flex justify-between text-xs">
                                <span className="text-gray-600">Polish:</span>
                                <span className="text-gray-900">${item.result.polish_price.toFixed(2)}</span>
                              </div>
                            )}

                            {item.result.beveled_price && (
                              <div className="flex justify-between text-xs">
                                <span className="text-gray-600">Beveled:</span>
                                <span className="text-gray-900">${item.result.beveled_price.toFixed(2)}</span>
                              </div>
                            )}

                            {item.result.clipped_corners_price && (
                              <div className="flex justify-between text-xs">
                                <span className="text-gray-600">Clipped Corners:</span>
                                <span className="text-gray-900">${item.result.clipped_corners_price.toFixed(2)}</span>
                              </div>
                            )}

                            {item.result.tempered_price && (
                              <div className="flex justify-between text-xs">
                                <span className="text-gray-600">Tempered (35%):</span>
                                <span className="text-gray-900">${item.result.tempered_price.toFixed(2)}</span>
                              </div>
                            )}

                            {item.result.shape_price && (
                              <div className="flex justify-between text-xs">
                                <span className="text-gray-600">Shape (25%):</span>
                                <span className="text-gray-900">${item.result.shape_price.toFixed(2)}</span>
                              </div>
                            )}

                            <div className="flex justify-between text-xs font-medium text-gray-900 pt-1 border-t border-gray-300">
                              <span>Subtotal:</span>
                              <span>${item.result.subtotal.toFixed(2)}</span>
                            </div>

                            {item.result.contractor_discount && (
                              <div className="flex justify-between text-xs text-green-600">
                                <span>Contractor Discount (15%):</span>
                                <span>-${item.result.contractor_discount.toFixed(2)}</span>
                              </div>
                            )}

                            <div className="flex justify-between text-xs text-gray-900 pt-1 border-t border-gray-300">
                              <span>Cost subtotal:</span>
                              <span>${(item.result.contractor_discount ? item.result.discounted_subtotal : item.result.subtotal)?.toFixed(2)}</span>
                            </div>

                            {item.formData.quantity > 1 && (
                              <div className="flex justify-between text-xs text-gray-900">
                                <span>Quantity:</span>
                                <span>× {item.formData.quantity}</span>
                              </div>
                            )}

                            <div className="flex justify-between text-xs text-gray-900">
                              <span>Total cost:</span>
                              <span>${item.result.total.toFixed(2)}</span>
                            </div>

                            <div className="flex justify-between text-xs font-semibold text-blue-600 pt-1 border-t border-gray-300">
                              <span>Quote Price:</span>
                              <span>${item.result.quote_price.toFixed(2)}</span>
                            </div>
                          </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Calculator;
