import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { jobsService } from '../services/api';
import type { JobDetail } from '../types';
import Modal from '../components/Modal';
import JobForm, { type JobFormData } from '../components/JobForm';

export default function JobDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);

  const { data: job, isLoading, error } = useQuery<JobDetail>({
    queryKey: ['job', id],
    queryFn: () => jobsService.getById(Number(id)),
    enabled: !!id,
  });

  // Update job mutation
  const updateMutation = useMutation({
    mutationFn: (data: JobFormData) => jobsService.update(Number(id), data),
    onSuccess: () => {
      // Invalidate job detail and jobs list
      queryClient.invalidateQueries({ queryKey: ['job', id] });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setIsEditModalOpen(false);
    },
    onError: (error: Error) => {
      alert(`Failed to update job: ${error.message}`);
    },
  });

  // Delete job mutation
  const deleteMutation = useMutation({
    mutationFn: () => jobsService.delete(Number(id)),
    onSuccess: () => {
      // Invalidate jobs list and navigate back
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      navigate('/jobs');
    },
    onError: (error: Error) => {
      alert(`Failed to delete job: ${error.message}`);
    },
  });

  const handleUpdateJob = (data: JobFormData) => {
    updateMutation.mutate(data);
  };

  const handleDeleteJob = () => {
    deleteMutation.mutate();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-lg text-gray-600">Loading job details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded max-w-lg">
          <p className="font-bold">Error loading job</p>
          <p className="text-sm">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-lg text-gray-600">Job not found</div>
      </div>
    );
  }

  return (
    <div>
      {/* Header with Back Button and Actions */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/jobs')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to Jobs
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            Job {job.po_number}
          </h1>
          <span
            className={`px-3 py-1 text-sm font-semibold rounded-full ${
              job.status === 'Completed'
                ? 'bg-green-100 text-green-800'
                : job.status === 'In Progress'
                ? 'bg-blue-100 text-blue-800'
                : job.status === 'Cancelled'
                ? 'bg-red-100 text-red-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}
          >
            {job.status}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setIsEditModalOpen(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Edit Job
          </button>
          <button
            onClick={() => setIsDeleteConfirmOpen(true)}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Job Details Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Information */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Basic Information</h2>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">PO Number</label>
              <div className="mt-1 flex items-center gap-2">
                <p className="text-gray-900 font-medium">{job.po_number}</p>
                {job.is_remake && (
                  <span className="px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800">
                    REMAKE
                  </span>
                )}
                {job.is_warranty && (
                  <span className="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                    WARRANTY
                  </span>
                )}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Location</label>
              <p className="mt-1 text-gray-900">
                {job.location_code === '01' && '01 - Fernandina Beach & Yulee, FL'}
                {job.location_code === '02' && '02 - Georgia'}
                {job.location_code === '03' && '03 - Jacksonville, FL'}
                {!job.location_code && '-'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Client</label>
              <p className="mt-1 text-gray-900">
                {job.client_name || `Client #${job.client_id}`}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Status</label>
              <p className="mt-1 text-gray-900">{job.status}</p>
            </div>
          </div>
        </div>

        {/* Dates */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Dates</h2>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">Job Date</label>
              <p className="mt-1 text-gray-900">
                {job.job_date ? new Date(job.job_date).toLocaleDateString() : 'Not set'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Estimated Completion</label>
              <p className="mt-1 text-gray-900">
                {job.estimated_completion_date
                  ? new Date(job.estimated_completion_date).toLocaleDateString()
                  : 'Not set'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Actual Completion</label>
              <p className="mt-1 text-gray-900">
                {job.actual_completion_date
                  ? new Date(job.actual_completion_date).toLocaleDateString()
                  : 'Not set'}
              </p>
            </div>
          </div>
        </div>

        {/* Financial Information */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Financial Information</h2>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">Total Estimate</label>
              <p className="mt-1 text-gray-900 text-lg font-semibold">
                {job.total_estimate ? `$${job.total_estimate.toLocaleString()}` : '-'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Actual Cost</label>
              <p className="mt-1 text-gray-900">
                {job.actual_cost ? `$${job.actual_cost.toLocaleString()}` : '-'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Material Cost</label>
              <p className="mt-1 text-gray-900">
                {job.material_cost ? `$${job.material_cost.toLocaleString()}` : '-'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Labor Cost</label>
              <p className="mt-1 text-gray-900">
                {job.labor_cost ? `$${job.labor_cost.toLocaleString()}` : '-'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Profit Margin</label>
              <p className="mt-1 text-gray-900">
                {job.profit_margin ? `${job.profit_margin}%` : '-'}
              </p>
            </div>
          </div>
        </div>

        {/* Site Information */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Site Information</h2>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">Address</label>
              <p className="mt-1 text-gray-900">{job.site_address || 'Not provided'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Site Contact Name</label>
              <p className="mt-1 text-gray-900">{job.site_contact_name || 'Not provided'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Site Contact Phone</label>
              <p className="mt-1 text-gray-900">{job.site_contact_phone || 'Not provided'}</p>
            </div>
          </div>
        </div>

        {/* Job Description - Full Width */}
        <div className="bg-white shadow rounded-lg p-6 lg:col-span-2">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Description</h2>
          <p className="text-gray-700 whitespace-pre-wrap">
            {job.job_description || 'No description provided'}
          </p>
        </div>

        {/* Internal Notes */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Internal Notes</h2>
          <p className="text-gray-700 whitespace-pre-wrap">
            {job.internal_notes || 'No internal notes'}
          </p>
        </div>

        {/* Customer Notes */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Customer Notes</h2>
          <p className="text-gray-700 whitespace-pre-wrap">
            {job.customer_notes || 'No customer notes'}
          </p>
        </div>

        {/* Related Items Summary - Full Width */}
        <div className="bg-white shadow rounded-lg p-6 lg:col-span-2">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Related Items</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-3xl font-bold text-blue-600">{job.work_item_count}</p>
              <p className="text-sm text-gray-600 mt-1">Work Items</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-3xl font-bold text-purple-600">{job.material_count}</p>
              <p className="text-sm text-gray-600 mt-1">Materials</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-3xl font-bold text-green-600">{job.visit_count}</p>
              <p className="text-sm text-gray-600 mt-1">Site Visits</p>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Job Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Job"
        size="xl"
      >
        <JobForm
          job={job}
          onSubmit={handleUpdateJob}
          onCancel={() => setIsEditModalOpen(false)}
          isLoading={updateMutation.isPending}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteConfirmOpen}
        onClose={() => setIsDeleteConfirmOpen(false)}
        title="Delete Job"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            Are you sure you want to delete job <strong>{job.po_number}</strong>? This action
            cannot be undone.
          </p>
          <div className="flex justify-end space-x-3 pt-4">
            <button
              onClick={() => setIsDeleteConfirmOpen(false)}
              disabled={deleteMutation.isPending}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleDeleteJob}
              disabled={deleteMutation.isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete Job'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
