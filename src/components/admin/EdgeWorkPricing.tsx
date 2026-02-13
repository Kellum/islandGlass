import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card, CardContent } from '../ui/Card';
import { Spinner } from '../ui/Spinner';
import {
  getBeveledPricing,
  updateBeveledPricing,
  getClippedCornersPricing,
  updateClippedCornersPricing,
} from '../../services/adminApi';
import type { BeveledPricingRow, ClippedCornersPricingRow } from '../../types';

interface EdgeWorkPricingProps {
  onToast: (type: 'success' | 'error', message: string) => void;
}

export function EdgeWorkPricing({ onToast }: EdgeWorkPricingProps) {
  const [beveled, setBeveled] = useState<BeveledPricingRow[]>([]);
  const [clipped, setClipped] = useState<ClippedCornersPricingRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingBeveled, setSavingBeveled] = useState(false);
  const [savingClipped, setSavingClipped] = useState(false);
  const [savedBeveled, setSavedBeveled] = useState(false);
  const [savedClipped, setSavedClipped] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [b, c] = await Promise.all([getBeveledPricing(), getClippedCornersPricing()]);
        setBeveled(b);
        setClipped(c);
      } catch {
        onToast('error', 'Failed to load edge work pricing');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const saveBeveled = async () => {
    setSavingBeveled(true);
    try {
      for (const row of beveled) {
        await updateBeveledPricing(row.id, row.price_per_inch);
      }
      onToast('success', 'Beveled pricing saved');
      setSavedBeveled(true);
      setTimeout(() => setSavedBeveled(false), 2000);
    } catch {
      onToast('error', 'Failed to save beveled pricing');
    } finally {
      setSavingBeveled(false);
    }
  };

  const saveClipped = async () => {
    setSavingClipped(true);
    try {
      for (const row of clipped) {
        await updateClippedCornersPricing(row.id, row.price_per_corner);
      }
      onToast('success', 'Clipped corners pricing saved');
      setSavedClipped(true);
      setTimeout(() => setSavedClipped(false), 2000);
    } catch {
      onToast('error', 'Failed to save clipped corners pricing');
    } finally {
      setSavingClipped(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Beveled Pricing */}
      <Card>
        <CardContent>
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Beveled Edge Pricing ($ per inch)
          </h3>
          <div className="space-y-3 max-w-md">
            {beveled.map((row, i) => (
              <div key={row.id} className="flex items-center gap-3">
                <label className="text-sm text-gray-600 w-24">{row.glass_thickness}:</label>
                <span className="text-sm text-gray-500">$</span>
                <input
                  type="number"
                  step="0.01"
                  value={row.price_per_inch}
                  onChange={(e) => {
                    const updated = [...beveled];
                    updated[i] = { ...row, price_per_inch: parseFloat(e.target.value) || 0 };
                    setBeveled(updated);
                  }}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-28"
                />
                <span className="text-sm text-gray-500">per inch</span>
              </div>
            ))}
            <Button size="sm" onClick={saveBeveled} disabled={savingBeveled}>
              {savingBeveled ? (
                <Spinner size="sm" />
              ) : savedBeveled ? (
                <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} className="flex items-center gap-1">
                  <Check className="w-4 h-4" /> Saved
                </motion.span>
              ) : (
                'Save Beveled Pricing'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Clipped Corners Pricing */}
      <Card>
        <CardContent>
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Clipped Corners Pricing ($ per corner)
          </h3>
          <table className="text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 font-medium text-gray-600">Thickness</th>
                <th className="text-left py-2 px-3 font-medium text-gray-600">Clip Size</th>
                <th className="text-right py-2 px-3 font-medium text-gray-600">$ / Corner</th>
              </tr>
            </thead>
            <tbody>
              {clipped.map((row, i) => (
                <tr key={row.id} className="border-b border-gray-100">
                  <td className="py-2 px-3">{row.glass_thickness}</td>
                  <td className="py-2 px-3 capitalize">{row.clip_size.replace('_', ' ')}</td>
                  <td className="py-2 px-3 text-right">
                    <input
                      type="number"
                      step="0.01"
                      value={row.price_per_corner}
                      onChange={(e) => {
                        const updated = [...clipped];
                        updated[i] = { ...row, price_per_corner: parseFloat(e.target.value) || 0 };
                        setClipped(updated);
                      }}
                      className="border border-gray-300 rounded px-2 py-1 w-24 text-sm text-right"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-4">
            <Button size="sm" onClick={saveClipped} disabled={savingClipped}>
              {savingClipped ? (
                <Spinner size="sm" />
              ) : savedClipped ? (
                <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} className="flex items-center gap-1">
                  <Check className="w-4 h-4" /> Saved
                </motion.span>
              ) : (
                'Save Clipped Corners Pricing'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
