import React, { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import type { Job } from '../types';
import { clientsService, jobsService } from '../services/api';
import ClientAutocomplete from './ClientAutocomplete';
import QuickClientForm, { type QuickClientData } from './QuickClientForm';
import Modal from './Modal';
import { SparklesIcon } from '@heroicons/react/24/outline';

interface JobFormProps {
  job?: Job; // If provided, we're editing; otherwise creating
  onSubmit: (data: JobFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
  clientLocked?: boolean; // If true, client cannot be changed (e.g., when creating from client detail page)
}

export interface JobFormData {
  client_id: number;
  po_number: string;
  location_code: string | null;
  is_remake: boolean;
  is_warranty: boolean;
  status: 'Quote' | 'Scheduled' | 'In Progress' | 'Pending Materials' | 'Ready for Install' | 'Installed' | 'Completed' | 'Cancelled' | 'On Hold';
  job_date: string | null;
  estimated_completion_date: string | null;
  job_description: string | null;
  total_estimate: number | null;
  site_address: string | null;
  site_contact_name: string | null;
  site_contact_phone: string | null;
  internal_notes: string | null;
  customer_notes: string | null;
}

const JobForm: React.FC<JobFormProps> = ({ job, onSubmit, onCancel, isLoading, clientLocked = false }) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<JobFormData>({
    client_id: job?.client_id || 0,
    po_number: job?.po_number || '',
    location_code: job?.location_code || null,
    is_remake: job?.is_remake || false,
    is_warranty: job?.is_warranty || false,
    status: job?.status || 'Quote',
    job_date: job?.job_date || null,
    estimated_completion_date: job?.estimated_completion_date || null,
    job_description: job?.job_description || null,
    total_estimate: job?.total_estimate || null,
    site_address: job?.site_address || null,
    site_contact_name: job?.site_contact_name || null,
    site_contact_phone: job?.site_contact_phone || null,
    internal_notes: job?.internal_notes || null,
    customer_notes: job?.customer_notes || null,
  });

  const [isGeneratingPO, setIsGeneratingPO] = useState(false);
  const [poWarning, setPoWarning] = useState<string | null>(null);

  // Fetch locked client details if client is locked
  const { data: lockedClient } = useQuery({
    queryKey: ['client', formData.client_id],
    queryFn: () => clientsService.getById(formData.client_id),
    enabled: clientLocked && formData.client_id > 0,
  });

  const [errors, setErrors] = useState<Partial<Record<keyof JobFormData, string>>>({});
  const [isQuickClientModalOpen, setIsQuickClientModalOpen] = useState(false);
  const [pendingClientName, setPendingClientName] = useState('');

  // Create client mutation
  const createClientMutation = useMutation({
    mutationFn: (data: QuickClientData) => clientsService.create(data),
    onSuccess: (newClient) => {
      // Invalidate clients list to refetch
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      // Auto-select the newly created client
      setFormData((prev) => ({ ...prev, client_id: newClient.id }));
      setIsQuickClientModalOpen(false);
      setPendingClientName('');
      // Clear client_id error if it exists
      setErrors((prev) => ({ ...prev, client_id: undefined }));
    },
    onError: (error: Error) => {
      alert(`Failed to create client: ${error.message}`);
    },
  });

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof JobFormData, string>> = {};

    if (!formData.client_id || formData.client_id === 0) {
      newErrors.client_id = 'Client is required';
    }
    if (!formData.po_number.trim()) {
      newErrors.po_number = 'PO Number is required';
    }
    if (!formData.status) {
      newErrors.status = 'Status is required';
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

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value === '' ? null : value,
    }));
    // Clear error when user types
    if (errors[name as keyof JobFormData]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value === '' ? null : parseFloat(value),
    }));
    if (errors[name as keyof JobFormData]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSelectClient = (clientId: number) => {
    setFormData((prev) => ({ ...prev, client_id: clientId }));
    setErrors((prev) => ({ ...prev, client_id: undefined }));
  };

  const handleRequestNewClient = (searchTerm: string) => {
    setPendingClientName(searchTerm);
    setIsQuickClientModalOpen(true);
  };

  const handleQuickClientSubmit = (data: QuickClientData) => {
    createClientMutation.mutate(data);
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: checked,
    }));
    // Clear error when user changes
    if (errors[name as keyof JobFormData]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleGeneratePO = async () => {
    // Validate required fields for PO generation
    if (!formData.client_id || formData.client_id === 0) {
      setErrors((prev) => ({ ...prev, client_id: 'Please select a client first' }));
      return;
    }
    if (!formData.location_code) {
      setErrors((prev) => ({ ...prev, location_code: 'Please select a location' }));
      return;
    }

    setIsGeneratingPO(true);
    setPoWarning(null);

    try {
      const result = await jobsService.generatePO({
        client_id: formData.client_id,
        location_code: formData.location_code,
        is_remake: formData.is_remake,
        is_warranty: formData.is_warranty,
        site_address: formData.site_address,
      });

      // Update PO number in form
      setFormData((prev) => ({ ...prev, po_number: result.po_number }));

      // Show warning if duplicate
      if (result.warning) {
        setPoWarning(result.warning);
      }

      // Clear PO number error if it exists
      setErrors((prev) => ({ ...prev, po_number: undefined }));
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to generate PO number';
      alert(`Error: ${errorMessage}`);
    } finally {
      setIsGeneratingPO(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-4xl mx-auto">
      {/* Basic Information Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900 border-b pb-2">Basic Information</h3>

        {/* Client Selection - Full Width */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="block text-sm font-medium text-gray-700">
              Client <span className="text-red-500">*</span>
            </label>
            {!clientLocked && (
              <button
                type="button"
                onClick={() => {
                  setPendingClientName('');
                  setIsQuickClientModalOpen(true);
                }}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                + Add Client
              </button>
            )}
          </div>
          {clientLocked ? (
            <div className="w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-700 flex items-center justify-between">
              <span>
                {lockedClient?.client_name || `Client #${formData.client_id}`}
              </span>
              <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
                Locked
              </span>
            </div>
          ) : (
            <ClientAutocomplete
              selectedClientId={formData.client_id || null}
              onSelectClient={handleSelectClient}
              onRequestNewClient={handleRequestNewClient}
              error={errors.client_id}
            />
          )}
        </div>

        {/* PO Generation Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4 space-y-3">
          <h4 className="text-sm font-medium text-blue-900">PO Number Generation</h4>

          {/* Location Code Selector */}
          <div>
            <label htmlFor="location_code" className="block text-sm font-medium text-gray-700 mb-1">
              Location <span className="text-red-500">*</span>
            </label>
            <select
              id="location_code"
              name="location_code"
              value={formData.location_code || ''}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.location_code ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select location...</option>
              <option value="01">01 - Fernandina Beach & Yulee, FL</option>
              <option value="02">02 - Georgia</option>
              <option value="03">03 - Jacksonville, FL</option>
            </select>
            {errors.location_code && <p className="mt-1 text-sm text-red-500">{errors.location_code}</p>}
          </div>

          {/* Remake/Warranty Checkboxes */}
          <div className="flex space-x-6">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                name="is_remake"
                checked={formData.is_remake}
                onChange={handleCheckboxChange}
                disabled={formData.is_warranty}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:opacity-50"
              />
              <span className="text-sm font-medium text-gray-700">Is Remake</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                name="is_warranty"
                checked={formData.is_warranty}
                onChange={handleCheckboxChange}
                disabled={formData.is_remake}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:opacity-50"
              />
              <span className="text-sm font-medium text-gray-700">Is Warranty</span>
            </label>
          </div>

          {/* Auto-Generate PO Button */}
          <button
            type="button"
            onClick={handleGeneratePO}
            disabled={isGeneratingPO || !formData.client_id || !formData.location_code}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <SparklesIcon className="w-4 h-4" />
            <span>{isGeneratingPO ? 'Generating...' : 'Auto-Generate PO Number'}</span>
          </button>

          {/* PO Warning */}
          {poWarning && (
            <div className="flex items-start space-x-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
              <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{poWarning}</span>
            </div>
          )}
        </div>

        {/* 2-column grid for compact fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* PO Number */}
          <div className="md:col-span-2">
            <label htmlFor="po_number" className="block text-sm font-medium text-gray-700 mb-1">
              PO Number <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="po_number"
              name="po_number"
              value={formData.po_number}
              onChange={handleChange}
              placeholder="Use Auto-Generate or enter manually"
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.po_number ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.po_number && <p className="mt-1 text-sm text-red-500">{errors.po_number}</p>}
          </div>

          {/* Status */}
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status <span className="text-red-500">*</span>
            </label>
            <select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.status ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="Quote">Quote</option>
              <option value="Scheduled">Scheduled</option>
              <option value="In Progress">In Progress</option>
              <option value="Pending Materials">Pending Materials</option>
              <option value="Ready for Install">Ready for Install</option>
              <option value="Installed">Installed</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
              <option value="On Hold">On Hold</option>
            </select>
            {errors.status && <p className="mt-1 text-sm text-red-500">{errors.status}</p>}
          </div>

          {/* Job Date */}
          <div>
            <label htmlFor="job_date" className="block text-sm font-medium text-gray-700 mb-1">
              Job Date
            </label>
            <input
              type="date"
              id="job_date"
              name="job_date"
              value={formData.job_date || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Estimated Completion Date */}
          <div>
            <label
              htmlFor="estimated_completion_date"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Estimated Completion Date
            </label>
            <input
              type="date"
              id="estimated_completion_date"
              name="estimated_completion_date"
              value={formData.estimated_completion_date || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Total Estimate */}
          <div>
            <label htmlFor="total_estimate" className="block text-sm font-medium text-gray-700 mb-1">
              Total Estimate ($)
            </label>
            <input
              type="number"
              step="0.01"
              id="total_estimate"
              name="total_estimate"
              value={formData.total_estimate || ''}
              onChange={handleNumberChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Job Description */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900 border-b pb-2">Description</h3>
        <div>
          <label htmlFor="job_description" className="block text-sm font-medium text-gray-700 mb-1">
            Job Description
          </label>
          <textarea
            id="job_description"
            name="job_description"
            value={formData.job_description || ''}
            onChange={handleChange}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Site Information */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900 border-b pb-2">Site Information</h3>

        <div>
          <label htmlFor="site_address" className="block text-sm font-medium text-gray-700 mb-1">
            Site Address
          </label>
          <input
            type="text"
            id="site_address"
            name="site_address"
            value={formData.site_address || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label
            htmlFor="site_contact_name"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Site Contact Name
          </label>
          <input
            type="text"
            id="site_contact_name"
            name="site_contact_name"
            value={formData.site_contact_name || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label
            htmlFor="site_contact_phone"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Site Contact Phone
          </label>
          <input
            type="tel"
            id="site_contact_phone"
            name="site_contact_phone"
            value={formData.site_contact_phone || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Notes */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900 border-b pb-2">Notes</h3>

        <div>
          <label htmlFor="internal_notes" className="block text-sm font-medium text-gray-700 mb-1">
            Internal Notes
          </label>
          <textarea
            id="internal_notes"
            name="internal_notes"
            value={formData.internal_notes || ''}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Notes visible only to team members"
          />
        </div>

        <div>
          <label htmlFor="customer_notes" className="block text-sm font-medium text-gray-700 mb-1">
            Customer Notes
          </label>
          <textarea
            id="customer_notes"
            name="customer_notes"
            value={formData.customer_notes || ''}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Notes visible to customer"
          />
        </div>
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
          {isLoading ? 'Saving...' : job ? 'Update Job' : 'Create Job'}
        </button>
      </div>

      {/* Quick Client Creation Modal */}
      <Modal
        isOpen={isQuickClientModalOpen}
        onClose={() => setIsQuickClientModalOpen(false)}
        title="Add New Client"
        size="md"
        zIndex={60}
      >
        <QuickClientForm
          initialName={pendingClientName}
          onSubmit={handleQuickClientSubmit}
          onCancel={() => setIsQuickClientModalOpen(false)}
          isLoading={createClientMutation.isPending}
        />
      </Modal>
    </form>
  );
};

export default JobForm;
