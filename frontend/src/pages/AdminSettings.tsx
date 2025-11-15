import { useState, useEffect } from 'react';
import api from '../services/api';

interface GlassConfig {
  id: number;
  thickness: string;
  type: string;
  base_price: number;
  polish_price: number;
  only_tempered: boolean;
  no_polish: boolean;
  never_tempered: boolean;
}

interface CalculatorSettings {
  minimum_sq_ft: number;
  markup_divisor: number;
  contractor_discount_rate: number;
  flat_polish_rate: number;
}

interface FormulaConfig {
  formula_mode: string;
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
}

export default function AdminSettings() {
  const [activeTab, setActiveTab] = useState('wholesale');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // State for each section
  const [glassConfigs, setGlassConfigs] = useState<GlassConfig[]>([]);
  const [markups, setMarkups] = useState<Record<string, number>>({});
  const [beveledPricing, setBeveledPricing] = useState<Record<string, number>>({});
  const [clippedCornersPricing, setClippedCornersPricing] = useState<Record<number, number>>({});
  const [settings, setSettings] = useState<CalculatorSettings>({
    minimum_sq_ft: 3.0,
    markup_divisor: 0.28,
    contractor_discount_rate: 0.15,
    flat_polish_rate: 0.27
  });
  const [formulaConfig, setFormulaConfig] = useState<FormulaConfig>({
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
    enable_contractor_discount: true
  });

  // Edit states
  const [editingGlass, setEditingGlass] = useState<number | null>(null);
  const [newGlass, setNewGlass] = useState<Partial<GlassConfig> | null>(null);

  // Sort state
  const [sortColumn, setSortColumn] = useState<'thickness' | 'type' | 'base_price' | 'polish_price'>('thickness');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const response = await api.get('/calculator/config');
      const config = response.data;

      // Parse glass configs
      const glassArray: GlassConfig[] = Object.entries(config.glass_config).map(([key, value]: [string, any]) => {
        const [thickness, type] = key.split('_');
        return {
          id: value.id, // Use actual ID from backend
          thickness,
          type,
          base_price: value.base_price,
          polish_price: value.polish_price,
          only_tempered: value.only_tempered,
          no_polish: value.no_polish,
          never_tempered: value.never_tempered
        };
      });

      setGlassConfigs(glassArray);
      setMarkups(config.markups || {});
      setBeveledPricing(config.beveled_pricing || {});
      setClippedCornersPricing(config.clipped_corners_pricing || {});
      setSettings(config.settings || settings);
      setFormulaConfig(config.formula_config || formulaConfig);
    } catch (error: any) {
      showMessage('error', 'Failed to load configuration: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  // Helper function to convert thickness string to numeric value for sorting
  const thicknessToNumber = (thickness: string): number => {
    const cleaned = thickness.replace('"', '');
    if (cleaned.includes('/')) {
      const [numerator, denominator] = cleaned.split('/').map(Number);
      return numerator / denominator;
    }
    return parseFloat(cleaned);
  };

  // Handle column header click to sort
  const handleSort = (column: 'thickness' | 'type' | 'base_price' | 'polish_price') => {
    if (sortColumn === column) {
      // Toggle direction if same column
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New column, default to ascending
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  // Get sorted glass configs
  const sortedGlassConfigs = [...glassConfigs].sort((a, b) => {
    let compareValue = 0;

    switch (sortColumn) {
      case 'thickness':
        compareValue = thicknessToNumber(a.thickness) - thicknessToNumber(b.thickness);
        break;
      case 'type':
        compareValue = a.type.localeCompare(b.type);
        break;
      case 'base_price':
        compareValue = a.base_price - b.base_price;
        break;
      case 'polish_price':
        compareValue = a.polish_price - b.polish_price;
        break;
    }

    return sortDirection === 'asc' ? compareValue : -compareValue;
  });

  // Render sort indicator
  const SortIndicator = ({ column }: { column: string }) => {
    if (sortColumn !== column) return null;
    return (
      <span className="ml-1 text-xs">
        {sortDirection === 'asc' ? '▲' : '▼'}
      </span>
    );
  };

  const handleUpdateGlass = async (glass: GlassConfig) => {
    try {
      await api.put(`/api/v1/calculator/admin/glass-config/${glass.id}`, glass);
      showMessage('success', 'Wholesale pricing updated');
      setEditingGlass(null);
      loadConfig();
    } catch (error: any) {
      showMessage('error', 'Failed to update: ' + error.message);
    }
  };

  const handleCreateGlass = async () => {
    if (!newGlass) return;
    try {
      await api.post('/api/v1/calculator/admin/glass-config', newGlass);
      showMessage('success', 'Wholesale pricing created');
      setNewGlass(null);
      loadConfig();
    } catch (error: any) {
      showMessage('error', 'Failed to create: ' + error.message);
    }
  };

  const handleDeleteGlass = async (id: number) => {
    if (!confirm('Are you sure you want to delete this pricing configuration?')) return;
    try {
      await api.delete(`/api/v1/calculator/admin/glass-config/${id}`);
      showMessage('success', 'Pricing configuration deleted');
      loadConfig();
    } catch (error: any) {
      showMessage('error', 'Failed to delete: ' + error.message);
    }
  };

  const handleUpdateMarkupsAndSettings = async () => {
    try {
      // Update markups
      const markupUpdates = Object.entries(markups).map(([name, percentage]) => ({ name, percentage }));
      await api.put('/api/v1/calculator/admin/markups', markupUpdates);

      // Update settings
      await api.put('/api/v1/calculator/admin/settings', settings);

      showMessage('success', 'Markup formula settings updated');
    } catch (error: any) {
      showMessage('error', 'Failed to update: ' + error.message);
    }
  };

  const handleUpdateBeveledPricing = async () => {
    try {
      const updates = Object.entries(beveledPricing).map(([glass_thickness, price_per_inch]) => ({
        glass_thickness,
        price_per_inch
      }));
      await api.put('/api/v1/calculator/admin/beveled-pricing', updates);
      showMessage('success', 'Beveled pricing updated');
    } catch (error: any) {
      showMessage('error', 'Failed to update beveled pricing: ' + error.message);
    }
  };

  const handleUpdateClippedCorners = async () => {
    try {
      const updates = Object.entries(clippedCornersPricing).map(([num_corners, price]) => ({
        num_corners: parseInt(num_corners),
        price
      }));
      await api.put('/api/v1/calculator/admin/clipped-corners-pricing', updates);
      showMessage('success', 'Clipped corners pricing updated');
    } catch (error: any) {
      showMessage('error', 'Failed to update clipped corners pricing: ' + error.message);
    }
  };

  const handleUpdateFormulaConfig = async () => {
    try {
      await api.put('/api/v1/calculator/admin/formula-config', formulaConfig);
      showMessage('success', 'Formula configuration updated');
    } catch (error: any) {
      showMessage('error', 'Failed to update formula config: ' + error.message);
    }
  };

  const tabs = [
    { id: 'wholesale', label: 'Wholesale Pricing' },
    { id: 'formula', label: 'Markup Formula' },
    { id: 'edgework', label: 'Edge Work Pricing' },
    { id: 'users', label: 'User Management' },
    { id: 'company', label: 'Company Settings' },
    { id: 'audit', label: 'Audit Log' }
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Admin Settings</h1>
        <p className="text-gray-600">Manage system configuration, pricing, users, and company settings</p>
      </div>

      {message && (
        <div className={`mb-4 p-4 rounded ${message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
          {message.text}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {loading && <div className="text-center py-8">Loading...</div>}

      {/* Wholesale Pricing Tab */}
      {activeTab === 'wholesale' && !loading && (
        <div>
          {/* Warning Banner */}
          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-amber-600 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <h3 className="text-sm font-semibold text-amber-800 mb-1">Wholesale Pricing Model</h3>
                <p className="text-sm text-amber-700">
                  Enter <strong>WHOLESALE costs</strong> here (your actual cost from suppliers).
                  The calculator automatically applies the markup formula (÷ {formulaConfig.divisor_value}) to generate retail customer quotes.
                </p>
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Glass Wholesale Costs</h2>
            <button
              onClick={() => setNewGlass({ thickness: '', type: '', base_price: 0, polish_price: 0, only_tempered: false, no_polish: false, never_tempered: false })}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Add New Glass Type
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    className="px-4 py-2 border text-left cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('thickness')}
                  >
                    Thickness <SortIndicator column="thickness" />
                  </th>
                  <th
                    className="px-4 py-2 border text-left cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('type')}
                  >
                    Type <SortIndicator column="type" />
                  </th>
                  <th
                    className="px-4 py-2 border text-left cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('base_price')}
                  >
                    Wholesale Cost ($/sq ft) <SortIndicator column="base_price" />
                  </th>
                  <th
                    className="px-4 py-2 border text-left cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('polish_price')}
                  >
                    Wholesale Polish ($/inch) <SortIndicator column="polish_price" />
                  </th>
                  <th className="px-4 py-2 border text-center">Only Tempered</th>
                  <th className="px-4 py-2 border text-center">No Polish</th>
                  <th className="px-4 py-2 border text-center">Never Tempered</th>
                  <th className="px-4 py-2 border text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedGlassConfigs.map((glass) => (
                  <tr key={glass.id} className="hover:bg-gray-50">
                    {editingGlass === glass.id ? (
                      <>
                        <td className="px-4 py-2 border">
                          <input
                            type="text"
                            value={glass.thickness}
                            onChange={(e) => setGlassConfigs(prev => prev.map(g => g.id === glass.id ? { ...g, thickness: e.target.value } : g))}
                            className="w-full border rounded px-2 py-1"
                          />
                        </td>
                        <td className="px-4 py-2 border">
                          <input
                            type="text"
                            value={glass.type}
                            onChange={(e) => setGlassConfigs(prev => prev.map(g => g.id === glass.id ? { ...g, type: e.target.value } : g))}
                            className="w-full border rounded px-2 py-1"
                          />
                        </td>
                        <td className="px-4 py-2 border">
                          <input
                            type="number"
                            step="0.01"
                            value={glass.base_price}
                            onChange={(e) => setGlassConfigs(prev => prev.map(g => g.id === glass.id ? { ...g, base_price: parseFloat(e.target.value) } : g))}
                            className="w-full border rounded px-2 py-1"
                          />
                        </td>
                        <td className="px-4 py-2 border">
                          <input
                            type="number"
                            step="0.01"
                            value={glass.polish_price}
                            onChange={(e) => setGlassConfigs(prev => prev.map(g => g.id === glass.id ? { ...g, polish_price: parseFloat(e.target.value) } : g))}
                            className="w-full border rounded px-2 py-1"
                          />
                        </td>
                        <td className="px-4 py-2 border text-center">
                          <input
                            type="checkbox"
                            checked={glass.only_tempered}
                            onChange={(e) => setGlassConfigs(prev => prev.map(g => g.id === glass.id ? { ...g, only_tempered: e.target.checked } : g))}
                          />
                        </td>
                        <td className="px-4 py-2 border text-center">
                          <input
                            type="checkbox"
                            checked={glass.no_polish}
                            onChange={(e) => setGlassConfigs(prev => prev.map(g => g.id === glass.id ? { ...g, no_polish: e.target.checked } : g))}
                          />
                        </td>
                        <td className="px-4 py-2 border text-center">
                          <input
                            type="checkbox"
                            checked={glass.never_tempered}
                            onChange={(e) => setGlassConfigs(prev => prev.map(g => g.id === glass.id ? { ...g, never_tempered: e.target.checked } : g))}
                          />
                        </td>
                        <td className="px-4 py-2 border text-center">
                          <button
                            onClick={() => handleUpdateGlass(glass)}
                            className="text-green-600 hover:text-green-800 mr-2"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingGlass(null)}
                            className="text-gray-600 hover:text-gray-800"
                          >
                            Cancel
                          </button>
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="px-4 py-2 border">{glass.thickness}</td>
                        <td className="px-4 py-2 border capitalize">{glass.type}</td>
                        <td className="px-4 py-2 border">${glass.base_price.toFixed(2)}</td>
                        <td className="px-4 py-2 border">${glass.polish_price.toFixed(2)}</td>
                        <td className="px-4 py-2 border text-center">{glass.only_tempered ? '✓' : ''}</td>
                        <td className="px-4 py-2 border text-center">{glass.no_polish ? '✓' : ''}</td>
                        <td className="px-4 py-2 border text-center">{glass.never_tempered ? '✓' : ''}</td>
                        <td className="px-4 py-2 border text-center">
                          <button
                            onClick={() => setEditingGlass(glass.id)}
                            className="text-blue-600 hover:text-blue-800 mr-2"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteGlass(glass.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Delete
                          </button>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* New Glass Form */}
          {newGlass && (
            <div className="mt-4 p-4 border rounded bg-gray-50">
              <h3 className="font-semibold mb-2">Add New Glass Configuration</h3>
              <div className="grid grid-cols-7 gap-4">
                <input
                  type="text"
                  placeholder="Thickness"
                  value={newGlass.thickness || ''}
                  onChange={(e) => setNewGlass({ ...newGlass, thickness: e.target.value })}
                  className="border rounded px-2 py-1"
                />
                <input
                  type="text"
                  placeholder="Type"
                  value={newGlass.type || ''}
                  onChange={(e) => setNewGlass({ ...newGlass, type: e.target.value })}
                  className="border rounded px-2 py-1"
                />
                <input
                  type="number"
                  step="0.01"
                  placeholder="Wholesale Cost"
                  value={newGlass.base_price || 0}
                  onChange={(e) => setNewGlass({ ...newGlass, base_price: parseFloat(e.target.value) })}
                  className="border rounded px-2 py-1"
                />
                <input
                  type="number"
                  step="0.01"
                  placeholder="Polish Cost"
                  value={newGlass.polish_price || 0}
                  onChange={(e) => setNewGlass({ ...newGlass, polish_price: parseFloat(e.target.value) })}
                  className="border rounded px-2 py-1"
                />
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newGlass.only_tempered || false}
                    onChange={(e) => setNewGlass({ ...newGlass, only_tempered: e.target.checked })}
                    className="mr-1"
                  />
                  Only Temp
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newGlass.no_polish || false}
                    onChange={(e) => setNewGlass({ ...newGlass, no_polish: e.target.checked })}
                    className="mr-1"
                  />
                  No Polish
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newGlass.never_tempered || false}
                    onChange={(e) => setNewGlass({ ...newGlass, never_tempered: e.target.checked })}
                    className="mr-1"
                  />
                  Never Temp
                </label>
              </div>
              <div className="mt-2">
                <button
                  onClick={handleCreateGlass}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 mr-2"
                >
                  Create
                </button>
                <button
                  onClick={() => setNewGlass(null)}
                  className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Markup Formula Tab (Consolidated) */}
      {activeTab === 'formula' && !loading && (
        <div>
          <h2 className="text-xl font-semibold mb-6">Markup Formula Configuration</h2>

          {/* Formula Mode Section */}
          <div className="bg-white border rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Pricing Formula</h3>
            <div className="space-y-4 max-w-2xl">
              <div>
                <label className="block font-medium mb-2">Formula Mode:</label>
                <select
                  value={formulaConfig.formula_mode}
                  onChange={(e) => setFormulaConfig({ ...formulaConfig, formula_mode: e.target.value })}
                  className="border rounded px-3 py-2 w-64"
                >
                  <option value="divisor">Divisor (Wholesale ÷ X)</option>
                  <option value="multiplier">Multiplier (Wholesale × X)</option>
                  <option value="custom">Custom Expression</option>
                </select>
              </div>

              {formulaConfig.formula_mode === 'divisor' && (
                <div className="flex items-center gap-4">
                  <label className="w-40">Divisor Value:</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formulaConfig.divisor_value}
                    onChange={(e) => setFormulaConfig({ ...formulaConfig, divisor_value: parseFloat(e.target.value) })}
                    className="border rounded px-3 py-2 w-32"
                  />
                  <span className="text-gray-600 text-sm">Quote = Wholesale ÷ {formulaConfig.divisor_value}</span>
                </div>
              )}

              {formulaConfig.formula_mode === 'multiplier' && (
                <div className="flex items-center gap-4">
                  <label className="w-40">Multiplier Value:</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formulaConfig.multiplier_value}
                    onChange={(e) => setFormulaConfig({ ...formulaConfig, multiplier_value: parseFloat(e.target.value) })}
                    className="border rounded px-3 py-2 w-32"
                  />
                  <span className="text-gray-600 text-sm">Quote = Wholesale × {formulaConfig.multiplier_value}</span>
                </div>
              )}

              {formulaConfig.formula_mode === 'custom' && (
                <div>
                  <label className="block font-medium mb-2">Custom Expression:</label>
                  <input
                    type="text"
                    value={formulaConfig.custom_expression || ''}
                    onChange={(e) => setFormulaConfig({ ...formulaConfig, custom_expression: e.target.value })}
                    placeholder="e.g., total * 2 + 50"
                    className="border rounded px-3 py-2 w-full"
                  />
                  <p className="text-sm text-gray-600 mt-1">Use 'total' as the variable. Example: total * 2 + 50</p>
                </div>
              )}
            </div>

            <button
              onClick={handleUpdateFormulaConfig}
              className="mt-4 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Save Formula Configuration
            </button>
          </div>

          {/* Markups Section */}
          <div className="bg-white border rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Markup Percentages</h3>
            <div className="space-y-4 max-w-md">
              {Object.entries(markups).map(([name, percentage]) => (
                <div key={name} className="flex items-center gap-4">
                  <label className="w-40 capitalize">{name}:</label>
                  <input
                    type="number"
                    step="0.01"
                    value={percentage}
                    onChange={(e) => setMarkups({ ...markups, [name]: parseFloat(e.target.value) })}
                    className="border rounded px-3 py-2 w-32"
                  />
                  <span className="text-gray-600">%</span>
                </div>
              ))}
            </div>
          </div>

          {/* System Settings Section */}
          <div className="bg-white border rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">System Settings</h3>
            <div className="space-y-4 max-w-md">
              <div className="flex items-center gap-4">
                <label className="w-60">Minimum Square Footage:</label>
                <input
                  type="number"
                  step="0.1"
                  value={settings.minimum_sq_ft}
                  onChange={(e) => setSettings({ ...settings, minimum_sq_ft: parseFloat(e.target.value) })}
                  className="border rounded px-3 py-2 w-32"
                />
                <span className="text-gray-600">sq ft</span>
              </div>
              <div className="flex items-center gap-4">
                <label className="w-60">Contractor Discount Rate:</label>
                <input
                  type="number"
                  step="0.01"
                  value={settings.contractor_discount_rate}
                  onChange={(e) => setSettings({ ...settings, contractor_discount_rate: parseFloat(e.target.value) })}
                  className="border rounded px-3 py-2 w-32"
                />
                <span className="text-gray-600">%</span>
              </div>
              <div className="flex items-center gap-4">
                <label className="w-60">Flat Polish Rate (mirrors):</label>
                <span className="text-gray-600">$</span>
                <input
                  type="number"
                  step="0.01"
                  value={settings.flat_polish_rate}
                  onChange={(e) => setSettings({ ...settings, flat_polish_rate: parseFloat(e.target.value) })}
                  className="border rounded px-3 py-2 w-32"
                />
                <span className="text-gray-600">per inch</span>
              </div>
            </div>
          </div>

          {/* Enable/Disable Components */}
          <div className="bg-white border rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Enable/Disable Formula Components</h3>
            <div className="grid grid-cols-2 gap-3 max-w-2xl">
              {[
                ['enable_base_price', 'Base Price'],
                ['enable_polish', 'Polish'],
                ['enable_beveled', 'Beveled'],
                ['enable_clipped_corners', 'Clipped Corners'],
                ['enable_tempered_markup', 'Tempered Markup'],
                ['enable_shape_markup', 'Shape Markup'],
                ['enable_contractor_discount', 'Contractor Discount']
              ].map(([key, label]) => (
                <label key={key} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formulaConfig[key as keyof FormulaConfig] as boolean}
                    onChange={(e) => setFormulaConfig({ ...formulaConfig, [key]: e.target.checked })}
                    className="rounded"
                  />
                  <span>{label}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={handleUpdateMarkupsAndSettings}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
          >
            Save All Markup & Settings
          </button>

          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-sm text-yellow-800">
              <strong>Note:</strong> Changing the formula configuration will create a new version.
              The previous configuration will be archived for audit purposes.
            </p>
          </div>
        </div>
      )}

      {/* Edge Work Pricing Tab (Consolidated) */}
      {activeTab === 'edgework' && !loading && (
        <div>
          <h2 className="text-xl font-semibold mb-6">Edge Work Pricing</h2>

          {/* Beveled Pricing */}
          <div className="bg-white border rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Beveled Edge Pricing ($/inch)</h3>
            <div className="space-y-4 max-w-md">
              {Object.entries(beveledPricing).map(([thickness, price]) => (
                <div key={thickness} className="flex items-center gap-4">
                  <label className="w-40">{thickness}:</label>
                  <span className="text-gray-600">$</span>
                  <input
                    type="number"
                    step="0.01"
                    value={price}
                    onChange={(e) => setBeveledPricing({ ...beveledPricing, [thickness]: parseFloat(e.target.value) })}
                    className="border rounded px-3 py-2 w-32"
                  />
                  <span className="text-gray-600">per inch</span>
                </div>
              ))}
            </div>
            <button
              onClick={handleUpdateBeveledPricing}
              className="mt-4 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Save Beveled Pricing
            </button>
          </div>

          {/* Clipped Corners Pricing */}
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Clipped Corners Pricing</h3>
            <div className="space-y-4 max-w-md">
              {Object.entries(clippedCornersPricing).map(([numCorners, price]) => (
                <div key={numCorners} className="flex items-center gap-4">
                  <label className="w-40">{numCorners} corners:</label>
                  <span className="text-gray-600">$</span>
                  <input
                    type="number"
                    step="0.01"
                    value={price}
                    onChange={(e) => setClippedCornersPricing({ ...clippedCornersPricing, [parseInt(numCorners)]: parseFloat(e.target.value) })}
                    className="border rounded px-3 py-2 w-32"
                  />
                </div>
              ))}
            </div>
            <button
              onClick={handleUpdateClippedCorners}
              className="mt-4 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Save Clipped Corners Pricing
            </button>
          </div>
        </div>
      )}

      {/* User Management Tab (Placeholder) */}
      {activeTab === 'users' && !loading && (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">User Management Coming Soon</h3>
          <p className="text-gray-600">Manage users, roles, and permissions from this tab.</p>
        </div>
      )}

      {/* Company Settings Tab (Placeholder) */}
      {activeTab === 'company' && !loading && (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Company Settings Coming Soon</h3>
          <p className="text-gray-600">Configure company information, branding, and preferences.</p>
        </div>
      )}

      {/* Audit Log Tab (Placeholder) */}
      {activeTab === 'audit' && !loading && (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Audit Log Coming Soon</h3>
          <p className="text-gray-600">View history of configuration changes and system events.</p>
        </div>
      )}
    </div>
  );
}
