import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Pencil, Trash2, Check, X } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card, CardContent } from '../ui/Card';
import { Spinner } from '../ui/Spinner';
import {
  getLocations,
  createLocation,
  updateLocation,
  deleteLocation,
} from '../../services/adminApi';
import type { LocationRow } from '../../types';

interface LocationsTableProps {
  onToast: (type: 'success' | 'error', message: string) => void;
}

export function LocationsTable({ onToast }: LocationsTableProps) {
  const [locations, setLocations] = useState<LocationRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState('');
  const [editNumber, setEditNumber] = useState<number>(1);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newName, setNewName] = useState('');
  const [newNumber, setNewNumber] = useState<number>(1);

  const load = async () => {
    try {
      const data = await getLocations();
      setLocations(data);
    } catch {
      onToast('error', 'Failed to load locations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const startEdit = (row: LocationRow) => {
    setEditingId(row.id);
    setEditName(row.name);
    setEditNumber(row.location_number);
  };

  const saveEdit = async () => {
    if (!editingId || !editName.trim()) return;
    try {
      await updateLocation(editingId, editName.trim(), editNumber);
      onToast('success', 'Location updated');
      setEditingId(null);
      load();
    } catch {
      onToast('error', 'Failed to update location');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this location?')) return;
    try {
      await deleteLocation(id);
      onToast('success', 'Location deleted');
      load();
    } catch {
      onToast('error', 'Failed to delete location.');
    }
  };

  const handleCreate = async () => {
    if (!newName.trim()) {
      onToast('error', 'Location name is required');
      return;
    }
    try {
      await createLocation(newName.trim(), newNumber);
      onToast('success', 'Location added');
      setShowAddForm(false);
      setNewName('');
      setNewNumber(1);
      load();
    } catch {
      onToast('error', 'Failed to add location. Name may already exist.');
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
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Locations</h3>
        <Button size="sm" onClick={() => setShowAddForm(true)}>
          <Plus className="w-4 h-4 mr-1" /> Add Location
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
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-3">New Location</h4>
                <div className="flex gap-3">
                  <input
                    placeholder="Location name"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm flex-1 dark:bg-gray-900 dark:text-gray-100"
                    autoFocus
                  />
                  <input
                    type="number"
                    placeholder="#"
                    min={0}
                    value={newNumber}
                    onChange={(e) => setNewNumber(parseInt(e.target.value) || 0)}
                    onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
                    className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm w-20 dark:bg-gray-900 dark:text-gray-100"
                  />
                  <Button size="sm" onClick={handleCreate}>Create</Button>
                  <Button size="sm" variant="secondary" onClick={() => { setShowAddForm(false); setNewName(''); setNewNumber(1); }}>Cancel</Button>
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
              <th className="text-left py-3 px-3 font-medium text-gray-600 dark:text-gray-400">Name</th>
              <th className="text-left py-3 px-3 font-medium text-gray-600 dark:text-gray-400">Number</th>
              <th className="text-right py-3 px-3 font-medium text-gray-600 dark:text-gray-400">Actions</th>
            </tr>
          </thead>
          <tbody>
            {locations.length === 0 ? (
              <tr>
                <td colSpan={3} className="py-8 text-center text-gray-500 dark:text-gray-400">
                  No locations added yet.
                </td>
              </tr>
            ) : (
              locations.map((row) => (
                <tr key={row.id} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                  {editingId === row.id ? (
                    <>
                      <td className="py-2 px-3">
                        <input
                          value={editName}
                          onChange={(e) => setEditName(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && saveEdit()}
                          className="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 w-full text-sm dark:bg-gray-900 dark:text-gray-100"
                          autoFocus
                        />
                      </td>
                      <td className="py-2 px-3">
                        <input
                          type="number"
                          min={0}
                          value={editNumber}
                          onChange={(e) => setEditNumber(parseInt(e.target.value) || 0)}
                          onKeyDown={(e) => e.key === 'Enter' && saveEdit()}
                          className="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 w-20 text-sm dark:bg-gray-900 dark:text-gray-100"
                        />
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
                      <td className="py-2 px-3 font-medium">{row.name}</td>
                      <td className="py-2 px-3 text-gray-600 dark:text-gray-400">{String(row.location_number).padStart(2, '0')}</td>
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
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
