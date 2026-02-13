import { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Save, FileDown } from 'lucide-react';

export interface SaveModalData {
  customer_phone: string;
  customer_email: string;
  customer_notes: string;
}

interface SaveQuoteModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: SaveModalData) => Promise<void>;
  onSaveAndExport: (data: SaveModalData) => Promise<void>;
  saving: boolean;
}

const empty: SaveModalData = {
  customer_phone: '',
  customer_email: '',
  customer_notes: '',
};

export function SaveQuoteModal({
  open,
  onClose,
  onSave,
  onSaveAndExport,
  saving,
}: SaveQuoteModalProps) {
  const [formData, setFormData] = useState<SaveModalData>({ ...empty });

  const update = (field: keyof SaveModalData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const reset = () => setFormData({ ...empty });

  const handleSave = async () => {
    await onSave(formData);
    reset();
  };

  const handleSaveAndExport = async () => {
    await onSaveAndExport(formData);
    reset();
  };

  return (
    <Modal open={open} onClose={onClose} title="Save Quote">
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Phone"
            placeholder="(808) 555-1234"
            type="tel"
            value={formData.customer_phone}
            onChange={(e) => update('customer_phone', e.target.value)}
          />
          <Input
            label="Email"
            placeholder="john@example.com"
            type="email"
            value={formData.customer_email}
            onChange={(e) => update('customer_email', e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Notes</label>
          <textarea
            className="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 rounded-lg text-base transition-shadow focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
            rows={3}
            placeholder="Special instructions, delivery notes..."
            value={formData.customer_notes}
            onChange={(e) => update('customer_notes', e.target.value)}
          />
        </div>

        <div className="flex gap-3 pt-2">
          <Button
            variant="secondary"
            className="flex-1"
            onClick={handleSave}
            disabled={saving}
          >
            <Save className="w-4 h-4 mr-2" />
            {saving ? 'Saving...' : 'Save'}
          </Button>
          <Button
            className="flex-1"
            onClick={handleSaveAndExport}
            disabled={saving}
          >
            <FileDown className="w-4 h-4 mr-2" />
            {saving ? 'Saving...' : 'Save & PDF'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
