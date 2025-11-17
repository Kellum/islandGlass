import { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { vendorsService } from '../services/api';

interface NewVendorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface VendorContact {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  job_title: string;
  is_primary: boolean;
}

const VENDOR_TYPES = ['Glass', 'Hardware', 'Materials', 'Services', 'Other'];

export default function NewVendorModal({ isOpen, onClose }: NewVendorModalProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    vendor_name: '',
    vendor_type: 'Glass',
    contact_person: '',
    email: '',
    phone: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    zip_code: '',
    notes: '',
  });
  const [contacts, setContacts] = useState<VendorContact[]>([
    {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      job_title: '',
      is_primary: true,
    }
  ]);
  const [error, setError] = useState<string | null>(null);

  const createVendorMutation = useMutation({
    mutationFn: vendorsService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
      resetForm();
      onClose();
    },
    onError: (error: any) => {
      console.error('Create vendor error:', error);
      const errorDetail = error.response?.data?.detail;

      if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else if (Array.isArray(errorDetail)) {
        const messages = errorDetail.map((err: any) => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
        setError(messages);
      } else {
        setError('Failed to create vendor');
      }
    },
  });

  const resetForm = () => {
    setFormData({
      vendor_name: '',
      vendor_type: 'Glass',
      contact_person: '',
      email: '',
      phone: '',
      address_line1: '',
      address_line2: '',
      city: '',
      state: '',
      zip_code: '',
      notes: '',
    });
    setContacts([
      {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        job_title: '',
        is_primary: true,
      }
    ]);
    setError(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleContactChange = (index: number, field: keyof VendorContact, value: string | boolean) => {
    const newContacts = [...contacts];
    newContacts[index] = {
      ...newContacts[index],
      [field]: value,
    };

    // If setting a contact as primary, unset all others
    if (field === 'is_primary' && value === true) {
      newContacts.forEach((contact, i) => {
        if (i !== index) {
          contact.is_primary = false;
        }
      });
    }

    setContacts(newContacts);
  };

  const addContact = () => {
    setContacts([
      ...contacts,
      {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        job_title: '',
        is_primary: false,
      }
    ]);
  };

  const removeContact = (index: number) => {
    if (contacts.length === 1) {
      setError('Must have at least one contact');
      return;
    }

    const newContacts = contacts.filter((_, i) => i !== index);

    // If we removed the primary contact, make the first one primary
    if (contacts[index].is_primary && newContacts.length > 0) {
      newContacts[0].is_primary = true;
    }

    setContacts(newContacts);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate at least one contact with first and last name
    const validContacts = contacts.filter(c => c.first_name.trim() && c.last_name.trim());
    if (validContacts.length === 0) {
      setError('At least one contact with first and last name is required');
      return;
    }

    // Ensure at least one primary contact
    const hasPrimary = validContacts.some(c => c.is_primary);
    if (!hasPrimary && validContacts.length > 0) {
      validContacts[0].is_primary = true;
    }

    // Prepare data for API
    const vendorData: any = {
      vendor_name: formData.vendor_name.trim(),
      vendor_type: formData.vendor_type,
      email: formData.email.trim() || null,
      phone: formData.phone.trim() || null,
      address_line1: formData.address_line1.trim() || null,
      address_line2: formData.address_line2.trim() || null,
      city: formData.city.trim() || null,
      state: formData.state.trim().toUpperCase() || null,
      zip_code: formData.zip_code.trim() || null,
      notes: formData.notes.trim() || null,
      is_active: true,
    };

    // Add contacts - separate primary from additional
    const primaryContact = validContacts.find(c => c.is_primary);
    const additionalContacts = validContacts.filter(c => !c.is_primary);

    if (primaryContact) {
      vendorData.primary_contact = {
        first_name: primaryContact.first_name.trim(),
        last_name: primaryContact.last_name.trim(),
        email: primaryContact.email.trim() || null,
        phone: primaryContact.phone.trim() || null,
        job_title: primaryContact.job_title.trim() || null,
        is_primary: true,
      };
    }

    if (additionalContacts.length > 0) {
      vendorData.additional_contacts = additionalContacts.map(c => ({
        first_name: c.first_name.trim(),
        last_name: c.last_name.trim(),
        email: c.email.trim() || null,
        phone: c.phone.trim() || null,
        job_title: c.job_title.trim() || null,
        is_primary: false,
      }));
    }

    createVendorMutation.mutate(vendorData);
  };

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6">
                {/* Header */}
                <div className="absolute right-0 top-0 pr-4 pt-4">
                  <button
                    type="button"
                    className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none"
                    onClick={onClose}
                  >
                    <span className="sr-only">Close</span>
                    <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                  </button>
                </div>

                <div>
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900 mb-4">
                    New Vendor
                  </Dialog.Title>

                  {/* Error Message */}
                  {error && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-600">{error}</p>
                    </div>
                  )}

                  {/* Form Fields */}
                  <form onSubmit={handleSubmit} className="mt-6 space-y-6">
                    {/* Vendor Basic Info */}
                    <div className="space-y-4">
                      <h4 className="text-sm font-medium text-gray-900">Vendor Information</h4>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label htmlFor="vendor_name" className="block text-sm font-medium text-gray-700 mb-1">
                            Company Name *
                          </label>
                          <input
                            type="text"
                            id="vendor_name"
                            name="vendor_name"
                            value={formData.vendor_name}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            placeholder="ABC Glass Supply"
                            required
                          />
                        </div>
                        <div>
                          <label htmlFor="vendor_type" className="block text-sm font-medium text-gray-700 mb-1">
                            Vendor Type
                          </label>
                          <select
                            id="vendor_type"
                            name="vendor_type"
                            value={formData.vendor_type}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          >
                            {VENDOR_TYPES.map(type => (
                              <option key={type} value={type}>{type}</option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                            Company Email
                          </label>
                          <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            placeholder="info@abcglass.com"
                          />
                        </div>
                        <div>
                          <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                            Company Phone
                          </label>
                          <input
                            type="tel"
                            id="phone"
                            name="phone"
                            value={formData.phone}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            placeholder="(808) 555-1234"
                          />
                        </div>
                      </div>

                      <div>
                        <label htmlFor="address_line1" className="block text-sm font-medium text-gray-700 mb-1">
                          Address
                        </label>
                        <input
                          type="text"
                          id="address_line1"
                          name="address_line1"
                          value={formData.address_line1}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="123 Main St"
                        />
                      </div>

                      <div className="grid grid-cols-3 gap-3">
                        <div className="col-span-2">
                          <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">
                            City
                          </label>
                          <input
                            type="text"
                            id="city"
                            name="city"
                            value={formData.city}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            placeholder="Honolulu"
                          />
                        </div>
                        <div>
                          <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-1">
                            State
                          </label>
                          <input
                            type="text"
                            id="state"
                            name="state"
                            value={formData.state}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            placeholder="HI"
                            maxLength={2}
                          />
                        </div>
                      </div>

                      <div>
                        <label htmlFor="zip_code" className="block text-sm font-medium text-gray-700 mb-1">
                          Zip Code
                        </label>
                        <input
                          type="text"
                          id="zip_code"
                          name="zip_code"
                          value={formData.zip_code}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="96815"
                        />
                      </div>
                    </div>

                    {/* Contacts Section */}
                    <div className="space-y-4 border-t pt-4">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium text-gray-900">Contacts</h4>
                        <button
                          type="button"
                          onClick={addContact}
                          className="flex items-center text-sm text-purple-600 hover:text-purple-700"
                        >
                          <PlusIcon className="h-4 w-4 mr-1" />
                          Add Contact
                        </button>
                      </div>

                      {contacts.map((contact, index) => (
                        <div key={index} className="p-4 bg-gray-50 rounded-lg space-y-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                checked={contact.is_primary}
                                onChange={(e) => handleContactChange(index, 'is_primary', e.target.checked)}
                                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                              />
                              <label className="text-sm font-medium text-gray-700">
                                Primary Contact
                              </label>
                            </div>
                            {contacts.length > 1 && (
                              <button
                                type="button"
                                onClick={() => removeContact(index)}
                                className="text-red-600 hover:text-red-700"
                              >
                                <TrashIcon className="h-5 w-5" />
                              </button>
                            )}
                          </div>

                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                First Name *
                              </label>
                              <input
                                type="text"
                                value={contact.first_name}
                                onChange={(e) => handleContactChange(index, 'first_name', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                placeholder="John"
                              />
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Last Name *
                              </label>
                              <input
                                type="text"
                                value={contact.last_name}
                                onChange={(e) => handleContactChange(index, 'last_name', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                placeholder="Doe"
                              />
                            </div>
                          </div>

                          <div className="grid grid-cols-3 gap-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Email
                              </label>
                              <input
                                type="email"
                                value={contact.email}
                                onChange={(e) => handleContactChange(index, 'email', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                placeholder="john@example.com"
                              />
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Phone
                              </label>
                              <input
                                type="tel"
                                value={contact.phone}
                                onChange={(e) => handleContactChange(index, 'phone', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                placeholder="(808) 555-1234"
                              />
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Job Title
                              </label>
                              <input
                                type="text"
                                value={contact.job_title}
                                onChange={(e) => handleContactChange(index, 'job_title', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                placeholder="Sales Rep"
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Notes */}
                    <div>
                      <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
                        Notes
                      </label>
                      <textarea
                        id="notes"
                        name="notes"
                        value={formData.notes}
                        onChange={handleInputChange}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="Additional notes about this vendor..."
                      />
                    </div>
                  </form>
                </div>

                {/* Footer */}
                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    type="button"
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                    onClick={onClose}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    onClick={handleSubmit}
                    className="px-4 py-2 text-sm font-medium text-white bg-purple-600 border border-transparent rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                    disabled={!formData.vendor_name.trim() || createVendorMutation.isPending}
                  >
                    {createVendorMutation.isPending ? 'Saving...' : 'Save Vendor'}
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}
