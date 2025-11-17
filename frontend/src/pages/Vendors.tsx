import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { vendorsService } from '../services/api';
import type { Vendor } from '../types';
import Spinner from '../components/Spinner';
import NewVendorModal from '../components/NewVendorModal';
import { BuildingOfficeIcon, MagnifyingGlassIcon, PlusIcon } from '@heroicons/react/24/outline';

export default function Vendors() {
  const navigate = useNavigate();
  const [isNewVendorModalOpen, setIsNewVendorModalOpen] = useState(false);

  const { data: vendors, isLoading, error } = useQuery<Vendor[]>({
    queryKey: ['vendors'],
    queryFn: vendorsService.getAll,
  });

  if (isLoading) {
    return <Spinner size="lg" className="py-12" />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded max-w-lg">
          <p className="font-bold">Error loading vendors</p>
          <p className="text-sm">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pb-6">
      {/* New Vendor Modal */}
      <NewVendorModal
        isOpen={isNewVendorModalOpen}
        onClose={() => setIsNewVendorModalOpen(false)}
      />

      {/* Page Title and Actions */}
      <div className="mb-4 md:mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Vendors</h1>
        <button
          onClick={() => setIsNewVendorModalOpen(true)}
          className="flex items-center justify-center space-x-2 px-4 py-2.5 text-base bg-orange-600 text-white rounded-lg hover:bg-orange-700 active:bg-orange-700 transition-colors"
        >
          <PlusIcon className="h-5 w-5" />
          <span className="hidden sm:inline">New Vendor</span>
          <span className="sm:hidden">New</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-4 md:mb-6">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search vendors..."
            className="w-full pl-10 pr-4 py-2.5 text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Vendor List */}
      <div>
        {!vendors || vendors.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-8 md:p-12 text-center">
            <BuildingOfficeIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No vendors yet</h3>
            <p className="text-base text-gray-500 mb-6">Get started by adding your first vendor.</p>
            <button
              onClick={() => setIsNewVendorModalOpen(true)}
              className="inline-flex items-center space-x-2 px-6 py-3 text-base bg-orange-600 text-white rounded-lg hover:bg-orange-700 active:bg-orange-700 transition-colors"
            >
              <PlusIcon className="h-5 w-5" />
              <span>Add Vendor</span>
            </button>
          </div>
        ) : (
          <>
            {/* Mobile: Cards */}
            <div className="md:hidden space-y-3">
              {vendors.map((vendor) => (
                <div
                  key={vendor.vendor_id}
                  onClick={() => navigate(`/vendors/${vendor.vendor_id}`)}
                  className="bg-white shadow-sm rounded-lg p-4 active:bg-gray-50 transition-colors cursor-pointer"
                >
                  <h3 className="text-base font-semibold text-gray-900 mb-2">
                    {vendor.vendor_name}
                  </h3>
                  <div className="space-y-1 text-sm text-gray-600">
                    {vendor.vendor_type && (
                      <div>
                        <span className="inline-block px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                          {vendor.vendor_type}
                        </span>
                      </div>
                    )}
                    {vendor.primary_contact_name && (
                      <div>
                        <span className="font-medium text-gray-700">Contact:</span> {vendor.primary_contact_name}
                      </div>
                    )}
                    {vendor.primary_contact_email && (
                      <div className="truncate">
                        <span className="font-medium text-gray-700">Email:</span>{' '}
                        <a href={`mailto:${vendor.primary_contact_email}`} className="text-blue-600 active:text-blue-700">
                          {vendor.primary_contact_email}
                        </a>
                      </div>
                    )}
                    {vendor.primary_contact_phone && (
                      <div>
                        <span className="font-medium text-gray-700">Phone:</span>{' '}
                        <a href={`tel:${vendor.primary_contact_phone}`} className="text-blue-600 active:text-blue-700">
                          {vendor.primary_contact_phone}
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Desktop: Table */}
            <div className="hidden md:block bg-white shadow-sm rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vendor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Primary Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Phone
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {vendors.map((vendor) => (
                    <tr
                      key={vendor.vendor_id}
                      onClick={() => navigate(`/vendors/${vendor.vendor_id}`)}
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {vendor.vendor_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {vendor.vendor_type ? (
                          <span className="inline-block px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                            {vendor.vendor_type}
                          </span>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {vendor.primary_contact_name || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {vendor.primary_contact_email ? (
                          <a href={`mailto:${vendor.primary_contact_email}`} className="text-blue-600 hover:underline">
                            {vendor.primary_contact_email}
                          </a>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {vendor.primary_contact_phone ? (
                          <a href={`tel:${vendor.primary_contact_phone}`} className="text-blue-600 hover:underline">
                            {vendor.primary_contact_phone}
                          </a>
                        ) : (
                          '-'
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
