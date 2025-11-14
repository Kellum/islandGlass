import React, { useState } from 'react';

interface QuickClientFormProps {
  initialName?: string;
  onSubmit: (data: QuickClientData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export interface QuickClientData {
  client_type: 'residential' | 'contractor' | 'commercial';
  client_name: string;
  email: string | null;
  phone: string | null;
}

const QuickClientForm: React.FC<QuickClientFormProps> = ({
  initialName = '',
  onSubmit,
  onCancel,
  isLoading,
}) => {
  const [formData, setFormData] = useState<QuickClientData>({
    client_type: 'residential',
    client_name: initialName,
    email: null,
    phone: null,
  });

  const [errors, setErrors] = useState<Partial<Record<keyof QuickClientData, string>>>({});

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof QuickClientData, string>> = {};

    if (!formData.client_name.trim()) {
      newErrors.client_name = 'Client name is required';
    }
    if (!formData.client_type) {
      newErrors.client_type = 'Client type is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value === '' ? null : value,
    }));
    // Clear error when user types
    if (errors[name as keyof QuickClientData]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Client Type */}
      <div>
        <label htmlFor="client_type" className="block text-sm font-medium text-gray-700 mb-1">
          Client Type <span className="text-red-500">*</span>
        </label>
        <select
          id="client_type"
          name="client_type"
          value={formData.client_type}
          onChange={handleChange}
          className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.client_type ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value="residential">Residential</option>
          <option value="contractor">Contractor</option>
          <option value="commercial">Commercial</option>
        </select>
        {errors.client_type && <p className="mt-1 text-sm text-red-500">{errors.client_type}</p>}
      </div>

      {/* Client Name */}
      <div>
        <label htmlFor="client_name" className="block text-sm font-medium text-gray-700 mb-1">
          Client Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="client_name"
          name="client_name"
          value={formData.client_name}
          onChange={handleChange}
          placeholder="Enter client or company name"
          className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.client_name ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.client_name && <p className="mt-1 text-sm text-red-500">{errors.client_name}</p>}
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email || ''}
          onChange={handleChange}
          placeholder="client@example.com"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Phone */}
      <div>
        <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
          Phone
        </label>
        <input
          type="tel"
          id="phone"
          name="phone"
          value={formData.phone || ''}
          onChange={handleChange}
          placeholder="(555) 123-4567"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Form Actions */}
      <div className="flex justify-end space-x-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {isLoading ? 'Adding Client...' : 'Add Client'}
        </button>
      </div>
    </form>
  );
};

export default QuickClientForm;
