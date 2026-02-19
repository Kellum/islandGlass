import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Pencil, Trash2, Check, X, AlertTriangle, ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card, CardContent } from '../ui/Card';
import { Spinner } from '../ui/Spinner';
import {
  getGlassConfigs,
  getSuppliers,
  createGlassConfig,
  updateGlassConfig,
  deleteGlassConfig,
} from '../../services/adminApi';
import type { GlassConfigRow, SupplierRow } from '../../types';

type SortField = 'thickness' | 'type' | 'base_price' | 'polish_price' | 'supplier';
type SortDir = 'asc' | 'desc';

const THICKNESS_ORDER: Record<string, number> = {
  '1/8"': 1,
  '3/16"': 2,
  '1/4"': 3,
  '3/8"': 4,
  '1/2"': 5,
};

interface GlassConfigTableProps {
  onToast: (type: 'success' | 'error', message: string) => void;
}

export function GlassConfigTable({ onToast }: GlassConfigTableProps) {
  const [configs, setConfigs] = useState<GlassConfigRow[]>([]);
  const [suppliers, setSuppliers] = useState<SupplierRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortField, setSortField] = useState<SortField | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>('asc');
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
    supplier_id: null as number | null,
  });

  const load = async () => {
    try {
      const [configData, supplierData] = await Promise.all([
        getGlassConfigs(),
        getSuppliers(),
      ]);
      setConfigs(configData);
      setSuppliers(supplierData);
    } catch {
      onToast('error', 'Failed to load glass configs');
    } finally {
      setLoading(false);
    }
  };

  const supplierName = (id: number | null) => {
    if (!id) return '—';
    return suppliers.find((s) => s.id === id)?.name ?? '—';
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
        supplier_id: null,
      });
      load();
    } catch {
      onToast('error', 'Failed to create');
    }
  };

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      if (sortDir === 'asc') {
        setSortDir('desc');
      } else {
        // Third click: clear sort
        setSortField(null);
        setSortDir('asc');
      }
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  };

  const sortedConfigs = useMemo(() => {
    if (!sortField) return configs;

    return [...configs].sort((a, b) => {
      let cmp = 0;
      if (sortField === 'thickness') {
        cmp = (THICKNESS_ORDER[a.thickness] ?? 99) - (THICKNESS_ORDER[b.thickness] ?? 99);
      } else if (sortField === 'type') {
        cmp = a.type.localeCompare(b.type);
      } else if (sortField === 'base_price') {
        cmp = Number(a.base_price) - Number(b.base_price);
      } else if (sortField === 'polish_price') {
        cmp = Number(a.polish_price) - Number(b.polish_price);
      } else if (sortField === 'supplier') {
        cmp = supplierName(a.supplier_id).localeCompare(supplierName(b.supplier_id));
      }
      return sortDir === 'desc' ? -cmp : cmp;
    });
  }, [configs, sortField, sortDir]);

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <ArrowUpDown className="w-3.5 h-3.5 opacity-40" />;
    return sortDir === 'asc'
      ? <ArrowUp className="w-3.5 h-3.5 text-primary-600" />
      : <ArrowDown className="w-3.5 h-3.5 text-primary-600" />;
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
      <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-800 rounded-lg flex items-start gap-2">
        <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-amber-800 dark:text-amber-300">Wholesale Pricing Model</p>
          <p className="text-sm text-amber-700 dark:text-amber-400">
            Enter <strong>wholesale costs</strong> (from suppliers). The markup formula converts these to retail quotes.
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Glass Wholesale Costs</h3>
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
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-3">New Glass Configuration</h4>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                  <input
                    placeholder="Thickness"
                    value={newRow.thickness}
                    onChange={(e) => setNewRow({ ...newRow, thickness: e.target.value })}
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm dark:bg-gray-900 dark:text-gray-100"
                  />
                  <input
                    placeholder="Type"
                    value={newRow.type}
                    onChange={(e) => setNewRow({ ...newRow, type: e.target.value })}
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm dark:bg-gray-900 dark:text-gray-100"
                  />
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Base $/sqft"
                    value={newRow.base_price || ''}
                    onChange={(e) => setNewRow({ ...newRow, base_price: parseFloat(e.target.value) || 0 })}
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm dark:bg-gray-900 dark:text-gray-100"
                  />
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Polish $/in"
                    value={newRow.polish_price || ''}
                    onChange={(e) => setNewRow({ ...newRow, polish_price: parseFloat(e.target.value) || 0 })}
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm dark:bg-gray-900 dark:text-gray-100"
                  />
                  <select
                    value={newRow.supplier_id ?? ''}
                    onChange={(e) => setNewRow({ ...newRow, supplier_id: e.target.value ? Number(e.target.value) : null })}
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm dark:bg-gray-900 dark:text-gray-100"
                  >
                    <option value="">No Supplier</option>
                    {suppliers.map((s) => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
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
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-left py-3 px-3 font-medium text-gray-600 dark:text-gray-400">
                <button onClick={() => toggleSort('thickness')} className="inline-flex items-center gap-1 hover:text-gray-900 dark:hover:text-gray-200 transition-colors">
                  Thickness <SortIcon field="thickness" />
                </button>
              </th>
              <th className="text-left py-3 px-3 font-medium text-gray-600 dark:text-gray-400">
                <button onClick={() => toggleSort('type')} className="inline-flex items-center gap-1 hover:text-gray-900 dark:hover:text-gray-200 transition-colors">
                  Type <SortIcon field="type" />
                </button>
              </th>
              <th className="text-right py-3 px-3 font-medium text-gray-600 dark:text-gray-400">
                <button onClick={() => toggleSort('base_price')} className="inline-flex items-center gap-1 ml-auto hover:text-gray-900 dark:hover:text-gray-200 transition-colors">
                  Base $/sqft <SortIcon field="base_price" />
                </button>
              </th>
              <th className="text-right py-3 px-3 font-medium text-gray-600 dark:text-gray-400">
                <button onClick={() => toggleSort('polish_price')} className="inline-flex items-center gap-1 ml-auto hover:text-gray-900 dark:hover:text-gray-200 transition-colors">
                  Polish $/in <SortIcon field="polish_price" />
                </button>
              </th>
              <th className="text-left py-3 px-3 font-medium text-gray-600 dark:text-gray-400">
                <button onClick={() => toggleSort('supplier')} className="inline-flex items-center gap-1 hover:text-gray-900 dark:hover:text-gray-200 transition-colors">
                  Supplier <SortIcon field="supplier" />
                </button>
              </th>
              <th className="text-center py-3 px-3 font-medium text-gray-600 dark:text-gray-400">Flags</th>
              <th className="text-right py-3 px-3 font-medium text-gray-600 dark:text-gray-400">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedConfigs.map((row) => (
              <tr key={row.id} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                {editingId === row.id ? (
                  <>
                    <td className="py-2 px-3">
                      <input
                        value={editValues.thickness ?? ''}
                        onChange={(e) => setEditValues({ ...editValues, thickness: e.target.value })}
                        className="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 w-20 text-sm dark:bg-gray-900 dark:text-gray-100"
                      />
                    </td>
                    <td className="py-2 px-3">
                      <input
                        value={editValues.type ?? ''}
                        onChange={(e) => setEditValues({ ...editValues, type: e.target.value })}
                        className="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 w-20 text-sm dark:bg-gray-900 dark:text-gray-100"
                      />
                    </td>
                    <td className="py-2 px-3 text-right">
                      <input
                        type="number"
                        step="0.01"
                        value={editValues.base_price ?? 0}
                        onChange={(e) => setEditValues({ ...editValues, base_price: parseFloat(e.target.value) || 0 })}
                        className="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 w-20 text-sm text-right dark:bg-gray-900 dark:text-gray-100"
                      />
                    </td>
                    <td className="py-2 px-3 text-right">
                      <input
                        type="number"
                        step="0.01"
                        value={editValues.polish_price ?? 0}
                        onChange={(e) => setEditValues({ ...editValues, polish_price: parseFloat(e.target.value) || 0 })}
                        className="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 w-20 text-sm text-right dark:bg-gray-900 dark:text-gray-100"
                      />
                    </td>
                    <td className="py-2 px-3">
                      <select
                        value={editValues.supplier_id ?? ''}
                        onChange={(e) => setEditValues({ ...editValues, supplier_id: e.target.value ? Number(e.target.value) : null })}
                        className="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 w-full text-sm dark:bg-gray-900 dark:text-gray-100"
                      >
                        <option value="">—</option>
                        {suppliers.map((s) => (
                          <option key={s.id} value={s.id}>{s.name}</option>
                        ))}
                      </select>
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
                        <button onClick={saveEdit} className="p-1 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30 rounded">
                          <Check className="w-4 h-4" />
                        </button>
                        <button onClick={() => setEditingId(null)} className="p-1 text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
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
                    <td className="py-2 px-3 text-sm text-gray-600 dark:text-gray-400">{supplierName(row.supplier_id)}</td>
                    <td className="py-2 px-3 text-center text-xs text-gray-500 dark:text-gray-400">
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
                        <button onClick={() => startEdit(row)} className="p-1 text-gray-400 dark:text-gray-500 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/30 rounded">
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button onClick={() => handleDelete(row.id)} className="p-1 text-gray-400 dark:text-gray-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded">
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
