import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Pencil, Trash2, Check, X, AlertTriangle } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card, CardContent } from '../ui/Card';
import { Spinner } from '../ui/Spinner';
import {
  getGlassConfigs,
  createGlassConfig,
  updateGlassConfig,
  deleteGlassConfig,
} from '../../services/adminApi';
import type { GlassConfigRow } from '../../types';

interface GlassConfigTableProps {
  onToast: (type: 'success' | 'error', message: string) => void;
}

export function GlassConfigTable({ onToast }: GlassConfigTableProps) {
  const [configs, setConfigs] = useState<GlassConfigRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<Partial<GlassConfigRow>>({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRow, setNewRow] = useState({
    thickness: '',
    type: '',
    base_price: 0,
    polish_price: 0,
    only_tempered: false,
    no_polish: false,
    never_tempered: false,
  });

  const load = async () => {
    try {
      const data = await getGlassConfigs();
      setConfigs(data);
    } catch {
      onToast('error', 'Failed to load glass configs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const startEdit = (row: GlassConfigRow) => {
    setEditingId(row.id);
    setEditValues({ ...row });
  };

  const saveEdit = async () => {
    if (!editingId || !editValues) return;
    try {
      await updateGlassConfig(editingId, editValues);
      onToast('success', 'Pricing updated');
      setEditingId(null);
      load();
    } catch {
      onToast('error', 'Failed to update');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this glass configuration?')) return;
    try {
      await deleteGlassConfig(id);
      onToast('success', 'Configuration deleted');
      load();
    } catch {
      onToast('error', 'Failed to delete');
    }
  };

  const handleCreate = async () => {
    if (!newRow.thickness || !newRow.type) {
      onToast('error', 'Thickness and type are required');
      return;
    }
    try {
      await createGlassConfig(newRow);
      onToast('success', 'New glass type added');
      setShowAddForm(false);
      setNewRow({
        thickness: '',
        type: '',
        base_price: 0,
        polish_price: 0,
        only_tempered: false,
        no_polish: false,
        never_tempered: false,
      });
      load();
    } catch {
      onToast('error', 'Failed to create');
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
    <div>
      {/* Warning Banner */}
      <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-2">
        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-amber-800">Wholesale Pricing Model</p>
          <p className="text-sm text-amber-700">
            Enter <strong>wholesale costs</strong> (from suppliers). The markup formula converts these to retail quotes.
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Glass Wholesale Costs</h3>
        <Button size="sm" onClick={() => setShowAddForm(true)}>
          <Plus className="w-4 h-4 mr-1" /> Add Type
        </Button>
      </div>

      {/* Add Form */}
      <AnimatePresence>
        {showAddForm && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden mb-4"
          >
            <Card>
              <CardContent>
                <h4 className="font-medium text-gray-900 mb-3">New Glass Configuration</h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <input
                    placeholder="Thickness"
                    value={newRow.thickness}
                    onChange={(e) => setNewRow({ ...newRow, thickness: e.target.value })}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  />
                  <input
                    placeholder="Type"
                    value={newRow.type}
                    onChange={(e) => setNewRow({ ...newRow, type: e.target.value })}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  />
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Base $/sqft"
                    value={newRow.base_price || ''}
                    onChange={(e) => setNewRow({ ...newRow, base_price: parseFloat(e.target.value) || 0 })}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  />
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Polish $/in"
                    value={newRow.polish_price || ''}
                    onChange={(e) => setNewRow({ ...newRow, polish_price: parseFloat(e.target.value) || 0 })}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  />
                </div>
                <div className="flex flex-wrap gap-4 mt-3">
                  <label className="flex items-center gap-1.5 text-sm">
                    <input type="checkbox" checked={newRow.only_tempered} onChange={(e) => setNewRow({ ...newRow, only_tempered: e.target.checked })} className="rounded" />
                    Only Tempered
                  </label>
                  <label className="flex items-center gap-1.5 text-sm">
                    <input type="checkbox" checked={newRow.no_polish} onChange={(e) => setNewRow({ ...newRow, no_polish: e.target.checked })} className="rounded" />
                    No Polish
                  </label>
                  <label className="flex items-center gap-1.5 text-sm">
                    <input type="checkbox" checked={newRow.never_tempered} onChange={(e) => setNewRow({ ...newRow, never_tempered: e.target.checked })} className="rounded" />
                    Never Tempered
                  </label>
                </div>
                <div className="flex gap-2 mt-3">
                  <Button size="sm" onClick={handleCreate}>Create</Button>
                  <Button size="sm" variant="secondary" onClick={() => setShowAddForm(false)}>Cancel</Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-3 font-medium text-gray-600">Thickness</th>
              <th className="text-left py-3 px-3 font-medium text-gray-600">Type</th>
              <th className="text-right py-3 px-3 font-medium text-gray-600">Base $/sqft</th>
              <th className="text-right py-3 px-3 font-medium text-gray-600">Polish $/in</th>
              <th className="text-center py-3 px-3 font-medium text-gray-600">Flags</th>
              <th className="text-right py-3 px-3 font-medium text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody>
            {configs.map((row) => (
              <tr key={row.id} className="border-b border-gray-100 hover:bg-gray-50">
                {editingId === row.id ? (
                  <>
                    <td className="py-2 px-3">
                      <input
                        value={editValues.thickness ?? ''}
                        onChange={(e) => setEditValues({ ...editValues, thickness: e.target.value })}
                        className="border border-gray-300 rounded px-2 py-1 w-20 text-sm"
                      />
                    </td>
                    <td className="py-2 px-3">
                      <input
                        value={editValues.type ?? ''}
                        onChange={(e) => setEditValues({ ...editValues, type: e.target.value })}
                        className="border border-gray-300 rounded px-2 py-1 w-20 text-sm"
                      />
                    </td>
                    <td className="py-2 px-3 text-right">
                      <input
                        type="number"
                        step="0.01"
                        value={editValues.base_price ?? 0}
                        onChange={(e) => setEditValues({ ...editValues, base_price: parseFloat(e.target.value) || 0 })}
                        className="border border-gray-300 rounded px-2 py-1 w-20 text-sm text-right"
                      />
                    </td>
                    <td className="py-2 px-3 text-right">
                      <input
                        type="number"
                        step="0.01"
                        value={editValues.polish_price ?? 0}
                        onChange={(e) => setEditValues({ ...editValues, polish_price: parseFloat(e.target.value) || 0 })}
                        className="border border-gray-300 rounded px-2 py-1 w-20 text-sm text-right"
                      />
                    </td>
                    <td className="py-2 px-3 text-center">
                      <div className="flex gap-2 justify-center">
                        <label className="text-xs"><input type="checkbox" checked={editValues.only_tempered ?? false} onChange={(e) => setEditValues({ ...editValues, only_tempered: e.target.checked })} className="mr-1" />OT</label>
                        <label className="text-xs"><input type="checkbox" checked={editValues.no_polish ?? false} onChange={(e) => setEditValues({ ...editValues, no_polish: e.target.checked })} className="mr-1" />NP</label>
                        <label className="text-xs"><input type="checkbox" checked={editValues.never_tempered ?? false} onChange={(e) => setEditValues({ ...editValues, never_tempered: e.target.checked })} className="mr-1" />NT</label>
                      </div>
                    </td>
                    <td className="py-2 px-3 text-right">
                      <div className="flex gap-1 justify-end">
                        <button onClick={saveEdit} className="p-1 text-green-600 hover:bg-green-50 rounded">
                          <Check className="w-4 h-4" />
                        </button>
                        <button onClick={() => setEditingId(null)} className="p-1 text-gray-400 hover:bg-gray-100 rounded">
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </>
                ) : (
                  <>
                    <td className="py-2 px-3 font-medium">{row.thickness}</td>
                    <td className="py-2 px-3 capitalize">{row.type}</td>
                    <td className="py-2 px-3 text-right tabular-nums">${Number(row.base_price).toFixed(2)}</td>
                    <td className="py-2 px-3 text-right tabular-nums">${Number(row.polish_price).toFixed(2)}</td>
                    <td className="py-2 px-3 text-center text-xs text-gray-500">
                      {[
                        row.only_tempered && 'OT',
                        row.no_polish && 'NP',
                        row.never_tempered && 'NT',
                      ]
                        .filter(Boolean)
                        .join(', ') || '—'}
                    </td>
                    <td className="py-2 px-3 text-right">
                      <div className="flex gap-1 justify-end">
                        <button onClick={() => startEdit(row)} className="p-1 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded">
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button onClick={() => handleDelete(row.id)} className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
