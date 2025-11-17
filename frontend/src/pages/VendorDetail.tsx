import { useQuery } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { vendorsService } from '../services/api';
import Spinner from '../components/Spinner';
import type { VendorDetail } from '../types';
import {
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  UserIcon,
  ArrowLeftIcon,
  TagIcon
} from '@heroicons/react/24/outline';

export default function VendorDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: vendor, isLoading, error } = useQuery<VendorDetail>({
    queryKey: ['vendor', id],
    queryFn: () => vendorsService.getById(Number(id)),
    enabled: !!id,
  });

  if (isLoading) {
    return <Spinner size="lg" className="py-12" />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded max-w-lg">
          <p className="font-bold">Error loading vendor</p>
          <p className="text-sm">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  if (!vendor) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-yellow-50 border border-yellow-400 text-yellow-700 px-4 py-3 rounded max-w-lg">
          <p className="font-bold">Vendor not found</p>
        </div>
      </div>
    );
  }

  // Get primary contact
  const primaryContact = vendor.contacts?.find(c => c.is_primary);

  return (
    <div className="pb-6">
      {/* Back Button */}
      <button
        onClick={() => navigate('/vendors')}
        className="mb-4 flex items-center text-purple-600 hover:text-purple-700 transition-colors"
      >
        <ArrowLeftIcon className="h-5 w-5 mr-2" />
        Back to Vendors
      </button>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
              {vendor.vendor_name}
            </h1>
            {vendor.vendor_type && (
              <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-700">
                <TagIcon className="h-4 w-4 mr-1" />
                {vendor.vendor_type}
              </div>
            )}
          </div>
          <div className="mt-4 md:mt-0 flex space-x-3">
            <button
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Edit Vendor
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Vendor Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Company Information */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <BuildingOfficeIcon className="h-5 w-5 mr-2 text-purple-600" />
              Company Information
            </h2>
            <div className="space-y-3">
              {vendor.email && (
                <div className="flex items-start">
                  <EnvelopeIcon className="h-5 w-5 mr-3 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Company Email</p>
                    <a href={`mailto:${vendor.email}`} className="text-blue-600 hover:underline">
                      {vendor.email}
                    </a>
                  </div>
                </div>
              )}
              {vendor.phone && (
                <div className="flex items-start">
                  <PhoneIcon className="h-5 w-5 mr-3 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Company Phone</p>
                    <a href={`tel:${vendor.phone}`} className="text-blue-600 hover:underline">
                      {vendor.phone}
                    </a>
                  </div>
                </div>
              )}
              {(vendor.address_line1 || vendor.city || vendor.state) && (
                <div className="flex items-start">
                  <MapPinIcon className="h-5 w-5 mr-3 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Address</p>
                    <div className="text-gray-900">
                      {vendor.address_line1 && <p>{vendor.address_line1}</p>}
                      {vendor.address_line2 && <p>{vendor.address_line2}</p>}
                      {(vendor.city || vendor.state || vendor.zip_code) && (
                        <p>
                          {vendor.city && vendor.city}
                          {vendor.city && vendor.state && ', '}
                          {vendor.state && vendor.state}
                          {vendor.zip_code && ` ${vendor.zip_code}`}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}
              {vendor.notes && (
                <div className="pt-3 border-t">
                  <p className="text-sm text-gray-500 mb-1">Notes</p>
                  <p className="text-gray-900 whitespace-pre-wrap">{vendor.notes}</p>
                </div>
              )}
            </div>
          </div>

          {/* Contacts */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <UserIcon className="h-5 w-5 mr-2 text-purple-600" />
              Contacts ({vendor.contacts?.length || 0})
            </h2>

            {!vendor.contacts || vendor.contacts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <UserIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p>No contacts added yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {vendor.contacts.map((contact) => (
                  <div
                    key={contact.id}
                    className={`p-4 rounded-lg border ${
                      contact.is_primary
                        ? 'border-purple-200 bg-purple-50'
                        : 'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-medium text-gray-900">
                            {contact.first_name} {contact.last_name}
                          </h3>
                          {contact.is_primary && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-700">
                              Primary
                            </span>
                          )}
                        </div>

                        {contact.job_title && (
                          <p className="text-sm text-gray-600 mb-2">{contact.job_title}</p>
                        )}

                        <div className="space-y-1">
                          {contact.email && (
                            <div className="flex items-center text-sm">
                              <EnvelopeIcon className="h-4 w-4 mr-2 text-gray-400" />
                              <a href={`mailto:${contact.email}`} className="text-blue-600 hover:underline">
                                {contact.email}
                              </a>
                            </div>
                          )}
                          {contact.phone && (
                            <div className="flex items-center text-sm">
                              <PhoneIcon className="h-4 w-4 mr-2 text-gray-400" />
                              <a href={`tel:${contact.phone}`} className="text-blue-600 hover:underline">
                                {contact.phone}
                              </a>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Quick Info */}
        <div className="space-y-6">
          {/* Quick Info Card */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Info</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  vendor.is_active
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}>
                  {vendor.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              {primaryContact && (
                <div>
                  <p className="text-sm text-gray-500">Primary Contact</p>
                  <p className="font-medium text-gray-900">
                    {primaryContact.first_name} {primaryContact.last_name}
                  </p>
                  {primaryContact.job_title && (
                    <p className="text-sm text-gray-600">{primaryContact.job_title}</p>
                  )}
                </div>
              )}

              {vendor.created_at && (
                <div>
                  <p className="text-sm text-gray-500">Added</p>
                  <p className="text-gray-900">
                    {new Date(vendor.created_at).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
