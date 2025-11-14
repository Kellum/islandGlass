import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { clientsService, jobsService } from '../services/api';
import Spinner from '../components/Spinner';
import Modal from '../components/Modal';
import JobForm, { type JobFormData } from '../components/JobForm';
import type { Job } from '../types';
import {
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  UserIcon,
  BriefcaseIcon,
  CurrencyDollarIcon,
  ArrowLeftIcon,
  PlusIcon
} from '@heroicons/react/24/outline';

interface ClientContact {
  id: number;
  client_id: number;
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string | null;
  is_primary: boolean;
  created_at: string | null;
}

interface ClientDetail {
  id: number;
  client_type: 'residential' | 'contractor' | 'commercial';
  client_name: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zipcode: string | null;
  company_id: string | null;
  created_at: string | null;
  updated_at: string | null;
  created_by: string | null;
  updated_by: string | null;
  contacts: ClientContact[];
  job_count: number;
  total_revenue: number;
}

export default function ClientDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isCreateJobModalOpen, setIsCreateJobModalOpen] = useState(false);

  const { data: client, isLoading, error } = useQuery<ClientDetail>({
    queryKey: ['client', id],
    queryFn: () => clientsService.getById(Number(id)),
    enabled: !!id,
  });

  // Fetch client's jobs/POs
  const { data: clientJobs, isLoading: jobsLoading } = useQuery<Job[]>({
    queryKey: ['client-jobs', id],
    queryFn: () => jobsService.getByClientId(Number(id)),
    enabled: !!id,
  });

  // Create job mutation
  const createJobMutation = useMutation({
    mutationFn: (data: JobFormData) => jobsService.create(data),
    onSuccess: () => {
      // Invalidate and refetch both queries
      queryClient.invalidateQueries({ queryKey: ['client-jobs', id] });
      queryClient.invalidateQueries({ queryKey: ['client', id] });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setIsCreateJobModalOpen(false);
    },
    onError: (error: Error) => {
      alert(`Failed to create job: ${error.message}`);
    },
  });

  const handleCreateJob = (data: JobFormData) => {
    createJobMutation.mutate(data);
  };

  if (isLoading) {
    return <Spinner size="lg" className="py-12" />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded max-w-lg">
          <p className="font-bold">Error loading client</p>
          <p className="text-sm">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  if (!client) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-yellow-50 border border-yellow-400 text-yellow-700 px-4 py-3 rounded max-w-lg">
          <p className="font-bold">Client not found</p>
          <p className="text-sm">The requested client could not be found.</p>
        </div>
      </div>
    );
  }

  const primaryContact = client.contacts.find((c) => c.is_primary) || client.contacts[0];
  const additionalContacts = client.contacts.filter((c) => !c.is_primary);

  return (
    <div>
      {/* Header with Back Button */}
      <div className="mb-6 flex items-center space-x-4">
        <button
          onClick={() => navigate('/clients')}
          className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-2" />
          Back to Clients
        </button>
      </div>

      {/* Client Header */}
      <div className="bg-white shadow-sm rounded-lg p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {client.client_name || 'Unnamed Client'}
            </h1>
            <div className="flex items-center space-x-2">
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                client.client_type === 'residential'
                  ? 'bg-blue-100 text-blue-800'
                  : client.client_type === 'contractor'
                  ? 'bg-purple-100 text-purple-800'
                  : 'bg-green-100 text-green-800'
              }`}>
                {client.client_type.charAt(0).toUpperCase() + client.client_type.slice(1)}
              </span>
            </div>
          </div>
        </div>

        {/* Address */}
        {(client.address || client.city || client.state) && (
          <div className="mt-4 flex items-start text-gray-600">
            <MapPinIcon className="h-5 w-5 mr-2 mt-0.5" />
            <div>
              {client.address && <p>{client.address}</p>}
              <p>
                {client.city && client.city}
                {client.city && client.state && ', '}
                {client.state && client.state}
                {client.zipcode && ` ${client.zipcode}`}
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Contacts */}
        <div className="lg:col-span-2 space-y-6">
          {/* Primary Contact */}
          {primaryContact && (
            <div className="bg-white shadow-sm rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <UserIcon className="h-5 w-5 mr-2" />
                Primary Contact
              </h2>
              <div className="space-y-3">
                <p className="text-lg font-medium text-gray-900">
                  {primaryContact.first_name} {primaryContact.last_name}
                </p>
                {primaryContact.email && (
                  <div className="flex items-center text-gray-600">
                    <EnvelopeIcon className="h-5 w-5 mr-2" />
                    <a href={`mailto:${primaryContact.email}`} className="hover:text-purple-600">
                      {primaryContact.email}
                    </a>
                  </div>
                )}
                {primaryContact.phone && (
                  <div className="flex items-center text-gray-600">
                    <PhoneIcon className="h-5 w-5 mr-2" />
                    <a href={`tel:${primaryContact.phone}`} className="hover:text-purple-600">
                      {primaryContact.phone}
                    </a>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Additional Contacts */}
          {additionalContacts.length > 0 && (
            <div className="bg-white shadow-sm rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Additional Contacts
              </h2>
              <div className="space-y-4">
                {additionalContacts.map((contact) => (
                  <div key={contact.id} className="border-b border-gray-200 pb-4 last:border-0 last:pb-0">
                    <p className="font-medium text-gray-900">
                      {contact.first_name} {contact.last_name}
                    </p>
                    {contact.email && (
                      <div className="flex items-center text-gray-600 text-sm mt-1">
                        <EnvelopeIcon className="h-4 w-4 mr-2" />
                        <a href={`mailto:${contact.email}`} className="hover:text-purple-600">
                          {contact.email}
                        </a>
                      </div>
                    )}
                    {contact.phone && (
                      <div className="flex items-center text-gray-600 text-sm mt-1">
                        <PhoneIcon className="h-4 w-4 mr-2" />
                        <a href={`tel:${contact.phone}`} className="hover:text-purple-600">
                          {contact.phone}
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Jobs/POs Section */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <BriefcaseIcon className="h-5 w-5 mr-2" />
                Jobs & Purchase Orders
              </h2>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setIsCreateJobModalOpen(true)}
                  className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                >
                  <PlusIcon className="h-4 w-4" />
                  <span>New PO</span>
                </button>
                <button
                  onClick={() => navigate('/jobs')}
                  className="text-sm text-gray-600 hover:text-gray-900 font-medium"
                >
                  Go to All Jobs →
                </button>
              </div>
            </div>

            {jobsLoading ? (
              <div className="text-center py-4">
                <Spinner size="sm" />
              </div>
            ) : !clientJobs || clientJobs.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <BriefcaseIcon className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                <p className="text-sm">No jobs yet for this client</p>
              </div>
            ) : (
              <div className="space-y-3">
                {clientJobs.map((job) => (
                  <div
                    key={job.job_id}
                    onClick={() => navigate(`/jobs/${job.job_id}`)}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-semibold text-gray-900">{job.po_number}</span>
                          <span
                            className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                              job.status === 'Completed'
                                ? 'bg-green-100 text-green-800'
                                : job.status === 'In Progress'
                                ? 'bg-blue-100 text-blue-800'
                                : job.status === 'Cancelled' || job.status === 'On Hold'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}
                          >
                            {job.status}
                          </span>
                        </div>
                        {job.job_description && (
                          <p className="text-sm text-gray-600 mb-2 line-clamp-2">{job.job_description}</p>
                        )}
                        <div className="flex items-center text-xs text-gray-500 space-x-4">
                          {job.job_date && (
                            <span>Started: {new Date(job.job_date).toLocaleDateString()}</span>
                          )}
                          {job.estimated_completion_date && (
                            <span>Due: {new Date(job.estimated_completion_date).toLocaleDateString()}</span>
                          )}
                        </div>
                      </div>
                      {job.total_estimate && (
                        <div className="ml-4 text-right">
                          <p className="text-sm font-semibold text-gray-900">
                            ${job.total_estimate.toLocaleString()}
                          </p>
                          <p className="text-xs text-gray-500">Estimate</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Stats */}
        <div className="space-y-6">
          {/* Jobs Stats */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Statistics</h2>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center">
                  <BriefcaseIcon className="h-5 w-5 text-blue-600 mr-2" />
                  <span className="text-gray-700">Total Jobs</span>
                </div>
                <span className="text-xl font-bold text-blue-600">{client.job_count}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center">
                  <CurrencyDollarIcon className="h-5 w-5 text-green-600 mr-2" />
                  <span className="text-gray-700">Total Revenue</span>
                </div>
                <span className="text-xl font-bold text-green-600">
                  ${client.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          </div>

          {/* Client Type Info */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Client Information</h2>
            <div className="space-y-3">
              <div className="flex items-start">
                <BuildingOfficeIcon className="h-5 w-5 text-gray-400 mr-2 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Client Type</p>
                  <p className="text-gray-900 font-medium">
                    {client.client_type.charAt(0).toUpperCase() + client.client_type.slice(1)}
                  </p>
                </div>
              </div>
              {client.created_at && (
                <div>
                  <p className="text-sm text-gray-500">Member Since</p>
                  <p className="text-gray-900">
                    {new Date(client.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Create Job Modal */}
      <Modal
        isOpen={isCreateJobModalOpen}
        onClose={() => setIsCreateJobModalOpen(false)}
        title="Create New Job / PO"
        size="xl"
      >
        <JobForm
          job={{ client_id: Number(id) } as Job}
          onSubmit={handleCreateJob}
          onCancel={() => setIsCreateJobModalOpen(false)}
          isLoading={createJobMutation.isPending}
          clientLocked={true}
        />
      </Modal>
    </div>
  );
}
