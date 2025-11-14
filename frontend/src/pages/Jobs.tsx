import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { jobsService } from '../services/api';
import type { Job } from '../types';
import Modal from '../components/Modal';
import JobForm, { type JobFormData } from '../components/JobForm';
import Spinner from '../components/Spinner';
import { BriefcaseIcon, MagnifyingGlassIcon, PlusIcon } from '@heroicons/react/24/outline';

type StatusFilter = 'all' | 'Quote' | 'In Progress' | 'Completed' | 'Cancelled';

export default function Jobs() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');

  const { data: jobs, isLoading, error } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: jobsService.getAll,
  });

  // Create job mutation
  const createMutation = useMutation({
    mutationFn: (data: JobFormData) => jobsService.create(data),
    onSuccess: () => {
      // Invalidate and refetch jobs list
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setIsCreateModalOpen(false);
    },
    onError: (error: Error) => {
      alert(`Failed to create job: ${error.message}`);
    },
  });

  const handleCreateJob = (data: JobFormData) => {
    createMutation.mutate(data);
  };

  // Filter jobs based on search query and status filter
  const filteredJobs = jobs?.filter((job) => {
    // Apply status filter
    if (statusFilter !== 'all' && job.status !== statusFilter) {
      return false;
    }

    // Apply search query
    if (!searchQuery.trim()) return true;

    const query = searchQuery.toLowerCase();
    return (
      job.po_number?.toLowerCase().includes(query) ||
      job.client_name?.toLowerCase().includes(query) ||
      job.job_description?.toLowerCase().includes(query) ||
      job.site_address?.toLowerCase().includes(query)
    );
  });

  // Count jobs by status
  const statusCounts = {
    all: jobs?.length || 0,
    Quote: jobs?.filter(j => j.status === 'Quote').length || 0,
    'In Progress': jobs?.filter(j => j.status === 'In Progress' || j.status === 'Scheduled' || j.status === 'Pending Materials' || j.status === 'Ready for Install' || j.status === 'Installed').length || 0,
    Completed: jobs?.filter(j => j.status === 'Completed').length || 0,
    Cancelled: jobs?.filter(j => j.status === 'Cancelled' || j.status === 'On Hold').length || 0,
  };

  if (isLoading) {
    return <Spinner size="lg" className="py-12" />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded max-w-lg">
          <p className="font-bold">Error loading jobs</p>
          <p className="text-sm">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Page Title and Actions */}
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Jobs</h1>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <PlusIcon className="h-5 w-5" />
          <span>New Job</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setStatusFilter('all')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                statusFilter === 'all'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              All Jobs
              <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                {statusCounts.all}
              </span>
            </button>
            <button
              onClick={() => setStatusFilter('Quote')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                statusFilter === 'Quote'
                  ? 'border-yellow-600 text-yellow-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Quotes
              <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                {statusCounts.Quote}
              </span>
            </button>
            <button
              onClick={() => setStatusFilter('In Progress')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                statusFilter === 'In Progress'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Active
              <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                {statusCounts['In Progress']}
              </span>
            </button>
            <button
              onClick={() => setStatusFilter('Completed')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                statusFilter === 'Completed'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Completed
              <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                {statusCounts.Completed}
              </span>
            </button>
            <button
              onClick={() => setStatusFilter('Cancelled')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                statusFilter === 'Cancelled'
                  ? 'border-red-600 text-red-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Closed
              <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                {statusCounts.Cancelled}
              </span>
            </button>
          </nav>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by PO number, client, description, or address..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Job List */}
      <div>
        {!filteredJobs || filteredJobs.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <BriefcaseIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchQuery || statusFilter !== 'all' ? 'No jobs found' : 'No jobs yet'}
            </h3>
            <p className="text-gray-500 mb-6">
              {searchQuery || statusFilter !== 'all'
                ? 'Try adjusting your search or filter criteria.'
                : 'Get started by creating your first job.'
              }
            </p>
            {!searchQuery && statusFilter === 'all' && (
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <PlusIcon className="h-5 w-5" />
                <span>Create Job</span>
              </button>
            )}
          </div>
        ) : (
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    PO #
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Client
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Start Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredJobs.map((job) => (
                  <tr
                    key={job.job_id}
                    onClick={() => navigate(`/jobs/${job.job_id}`)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {job.po_number || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {job.client_name || `Client #${job.client_id}`}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
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
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {job.job_date
                        ? new Date(job.job_date).toLocaleDateString()
                        : 'Not set'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {job.total_estimate
                        ? `$${job.total_estimate.toLocaleString()}`
                        : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
        )}
      </div>

      {/* Create Job Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Job"
        size="xl"
      >
        <JobForm
          onSubmit={handleCreateJob}
          onCancel={() => setIsCreateModalOpen(false)}
          isLoading={createMutation.isPending}
        />
      </Modal>
    </div>
  );
}
