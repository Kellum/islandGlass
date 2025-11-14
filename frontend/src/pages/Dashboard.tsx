import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { jobsService, clientsService, vendorsService } from '../services/api';
import type { Job, Client, Vendor } from '../types';
import Spinner from '../components/Spinner';
import {
  BriefcaseIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  PlusIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

export default function Dashboard() {
  const navigate = useNavigate();

  const { data: jobs, isLoading: jobsLoading } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: jobsService.getAll,
  });

  const { data: clients, isLoading: clientsLoading } = useQuery<Client[]>({
    queryKey: ['clients'],
    queryFn: clientsService.getAll,
  });

  const { data: vendors, isLoading: vendorsLoading } = useQuery<Vendor[]>({
    queryKey: ['vendors'],
    queryFn: vendorsService.getAll,
  });

  const isLoading = jobsLoading || clientsLoading || vendorsLoading;

  // Calculate stats
  const totalJobs = jobs?.length || 0;
  const activeJobs = jobs?.filter((j) => j.status === 'In Progress' || j.status === 'Scheduled')?.length || 0;
  const totalClients = clients?.length || 0;
  const totalVendors = vendors?.length || 0;

  // Get recent jobs (last 5)
  const recentJobs = jobs?.slice(0, 5) || [];

  if (isLoading) {
    return <Spinner size="lg" className="py-12" />;
  }

  const stats = [
    {
      name: 'Total Jobs',
      value: totalJobs,
      icon: BriefcaseIcon,
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      href: '/jobs',
    },
    {
      name: 'Active Jobs',
      value: activeJobs,
      icon: ClockIcon,
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      href: '/jobs',
    },
    {
      name: 'Total Clients',
      value: totalClients,
      icon: UserGroupIcon,
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      href: '/clients',
    },
    {
      name: 'Total Vendors',
      value: totalVendors,
      icon: BuildingOfficeIcon,
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600',
      href: '/vendors',
    },
  ];

  return (
    <div className="p-4">
      {/* Page Title - Asana Style */}
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard v2</h1>
      </div>

      {/* Stats Grid - Asana Style */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.name}
              onClick={() => navigate(stat.href)}
              className="bg-white rounded-lg border border-gray-200 hover:border-gray-300 p-6 hover:shadow-sm transition-all cursor-pointer"
            >
              <div className="text-center">
                <p className="text-sm font-medium text-gray-700 mb-3">{stat.name}</p>
                <p className="text-5xl font-normal text-gray-900 mb-2">{stat.value}</p>
                <div className="flex items-center justify-center text-xs text-gray-500">
                  <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  <span>No Filters</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Chart Widgets Grid - Asana Style */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {/* Jobs by Status Chart */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-gray-900">Jobs by status</h3>
            <div className="flex items-center text-xs text-gray-500">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              <span>1 Filter</span>
            </div>
          </div>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
            <div className="text-center">
              <BriefcaseIcon className="h-12 w-12 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">Chart coming soon</p>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-gray-900">Recent activity</h3>
            <div className="flex items-center text-xs text-gray-500">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              <span>No Filters</span>
            </div>
          </div>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
            <div className="text-center">
              <ClockIcon className="h-12 w-12 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">Chart coming soon</p>
            </div>
          </div>
        </div>

        {/* Clients by Type */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-gray-900">Clients by type</h3>
            <div className="flex items-center text-xs text-gray-500">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              <span>1 Filter</span>
            </div>
          </div>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
            <div className="text-center">
              <UserGroupIcon className="h-12 w-12 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">Chart coming soon</p>
            </div>
          </div>
        </div>

        {/* Revenue Overview */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-gray-900">Revenue this month</h3>
            <div className="flex items-center text-xs text-gray-500">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              <span>No Filters</span>
            </div>
          </div>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
            <div className="text-center">
              <svg className="h-12 w-12 text-gray-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-gray-500">Chart coming soon</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Jobs - Asana Style */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-gray-900">Recent jobs</h3>
          <button
            onClick={() => navigate('/jobs')}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            View all →
          </button>
        </div>

        {recentJobs.length === 0 ? (
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
            <div className="text-center">
              <BriefcaseIcon className="h-12 w-12 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">No jobs yet</p>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Job #
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Client
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentJobs.map((job) => (
                  <tr
                    key={job.job_id}
                    onClick={() => navigate(`/jobs/${job.job_id}`)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {job.po_number || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      Client #{job.client_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
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
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {job.job_date ? new Date(job.job_date).toLocaleDateString() : 'Not set'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {job.total_estimate ? `$${job.total_estimate.toLocaleString()}` : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
