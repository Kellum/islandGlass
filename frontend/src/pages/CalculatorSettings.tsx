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

interface Markup {
  name: string;
  percentage: number;
}

interface BeveledPricing {
  glass_thickness: string;
  price_per_inch: number;
}

interface ClippedCornersPricing {
  num_corners: number;
  price: number;
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

export default function CalculatorSettings() {
  const [activeTab, setActiveTab] = useState('glass');
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

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/calculator/config');
      const config = response.data;

      // Parse glass configs
      const glassArray: GlassConfig[] = Object.entries(config.glass_config).map(([key, value]: [string, any]) => {
        const [thickness, type] = key.split('_');
        return {
          id: Math.random(), // Temporary ID - we'll need actual IDs from backend
          thickness,
          type,
          ...value
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

  const handleUpdateGlass = async (glass: GlassConfig) => {
    try {
      await api.put(`/api/v1/calculator/admin/glass-config/${glass.id}`, glass);
      showMessage('success', 'Glass configuration updated');
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
      showMessage('success', 'Glass configuration created');
      setNewGlass(null);
      loadConfig();
    } catch (error: any) {
      showMessage('error', 'Failed to create: ' + error.message);
    }
  };

  const handleDeleteGlass = async (id: number) => {
    if (!confirm('Are you sure you want to delete this glass configuration?')) return;
    try {
      await api.delete(`/api/v1/calculator/admin/glass-config/${id}`);
      showMessage('success', 'Glass configuration deleted');
      loadConfig();
    } catch (error: any) {
      showMessage('error', 'Failed to delete: ' + error.message);
    }
  };

  const handleUpdateMarkups = async () => {
    try {
      const updates = Object.entries(markups).map(([name, percentage]) => ({ name, percentage }));
      await api.put('/api/v1/calculator/admin/markups', updates);
      showMessage('success', 'Markups updated');
    } catch (error: any) {
      showMessage('error', 'Failed to update markups: ' + error.message);
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

  const handleUpdateSettings = async () => {
    try {
      await api.put('/api/v1/calculator/admin/settings', settings);
      showMessage('success', 'System settings updated');
    } catch (error: any) {
      showMessage('error', 'Failed to update settings: ' + error.message);
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
    { id: 'glass', label: 'Glass Pricing' },
    { id: 'markups', label: 'Markups' },
    { id: 'beveled', label: 'Beveled Pricing' },
    { id: 'clipped', label: 'Clipped Corners' },
    { id: 'settings', label: 'System Settings' },
    { id: 'formula', label: 'Formula Config' }
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Calculator Settings</h1>
        <p className="text-gray-600">Manage pricing, formulas, and calculator configuration</p>
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

      {/* Glass Pricing Tab */}
      {activeTab === 'glass' && !loading && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Glass Pricing Matrix</h2>
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
                  <th className="px-4 py-2 border text-left">Thickness</th>
                  <th className="px-4 py-2 border text-left">Type</th>
                  <th className="px-4 py-2 border text-left">Base Price ($/sq ft)</th>
                  <th className="px-4 py-2 border text-left">Polish Price ($/inch)</th>
                  <th className="px-4 py-2 border text-center">Only Tempered</th>
                  <th className="px-4 py-2 border text-center">No Polish</th>
                  <th className="px-4 py-2 border text-center">Never Tempered</th>
                  <th className="px-4 py-2 border text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {glassConfigs.map((glass) => (
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
                  placeholder="Base Price"
                  value={newGlass.base_price || 0}
                  onChange={(e) => setNewGlass({ ...newGlass, base_price: parseFloat(e.target.value) })}
                  className="border rounded px-2 py-1"
                />
                <input
                  type="number"
                  step="0.01"
                  placeholder="Polish Price"
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

      {/* Markups Tab */}
      {activeTab === 'markups' && !loading && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Markup Percentages</h2>
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
            <button
              onClick={handleUpdateMarkups}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Save Markups
            </button>
          </div>
        </div>
      )}

      {/* Beveled Pricing Tab */}
      {activeTab === 'beveled' && !loading && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Beveled Pricing ($/inch)</h2>
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
            <button
              onClick={handleUpdateBeveledPricing}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Save Beveled Pricing
            </button>
          </div>
        </div>
      )}

      {/* Clipped Corners Tab */}
      {activeTab === 'clipped' && !loading && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Clipped Corners Pricing</h2>
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
            <button
              onClick={handleUpdateClippedCorners}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Save Clipped Corners Pricing
            </button>
          </div>
        </div>
      )}

      {/* System Settings Tab */}
      {activeTab === 'settings' && !loading && (
        <div>
          <h2 className="text-xl font-semibold mb-4">System Settings</h2>
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
              <label className="w-60">Markup Divisor:</label>
              <input
                type="number"
                step="0.01"
                value={settings.markup_divisor}
                onChange={(e) => setSettings({ ...settings, markup_divisor: parseFloat(e.target.value) })}
                className="border rounded px-3 py-2 w-32"
              />
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
            <button
              onClick={handleUpdateSettings}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Save System Settings
            </button>
          </div>
        </div>
      )}

      {/* Formula Config Tab */}
      {activeTab === 'formula' && !loading && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Pricing Formula Configuration</h2>
          <div className="space-y-6 max-w-2xl">
            <div>
              <label className="block font-medium mb-2">Formula Mode:</label>
              <select
                value={formulaConfig.formula_mode}
                onChange={(e) => setFormulaConfig({ ...formulaConfig, formula_mode: e.target.value })}
                className="border rounded px-3 py-2 w-64"
              >
                <option value="divisor">Divisor (Cost ÷ X)</option>
                <option value="multiplier">Multiplier (Cost × X)</option>
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
                <span className="text-gray-600 text-sm">Quote = Cost ÷ {formulaConfig.divisor_value}</span>
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
                <span className="text-gray-600 text-sm">Quote = Cost × {formulaConfig.multiplier_value}</span>
              </div>
            )}

            {formulaConfig.formula_mode === 'custom' && (
              <div>
                <label className="block font-medium mb-2">Custom Expression:</label>
                <input
                  type="text"
                  value={formulaConfig.custom_expression || ''}
                  onChange={(e) => setFormulaConfig({ ...formulaConfig, custom_expression: e.target.value })}
                  placeholder="e.g., cost * 2 + 50"
                  className="border rounded px-3 py-2 w-full"
                />
                <p className="text-sm text-gray-600 mt-1">Use 'cost' as the variable. Example: cost * 2 + 50</p>
              </div>
            )}

            <div>
              <h3 className="font-medium mb-3">Enable/Disable Components:</h3>
              <div className="grid grid-cols-2 gap-3">
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
              onClick={handleUpdateFormulaConfig}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Save Formula Configuration
            </button>

            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> Changing the formula configuration will create a new version.
                The previous configuration will be archived for audit purposes.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
