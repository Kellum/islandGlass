import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { clientsService } from '../services/api';
import type { Client } from '../types';
import Spinner from '../components/Spinner';
import NewClientModal from '../components/NewClientModal';
import { UserGroupIcon, MagnifyingGlassIcon, PlusIcon } from '@heroicons/react/24/outline';

type ClientTypeFilter = 'all' | 'residential' | 'contractor' | 'commercial';

export default function Clients() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<ClientTypeFilter>('all');

  const { data: clients, isLoading, error } = useQuery<Client[]>({
    queryKey: ['clients'],
    queryFn: clientsService.getAll,
  });

  // Filter clients based on search query and type filter
  const filteredClients = clients?.filter((client) => {
    // Apply type filter
    if (typeFilter !== 'all' && client.client_type !== typeFilter) {
      return false;
    }

    // Apply search query
    if (!searchQuery.trim()) return true;

    const query = searchQuery.toLowerCase();
    return (
      client.client_name?.toLowerCase().includes(query) ||
      client.primary_contact_email?.toLowerCase().includes(query) ||
      client.primary_contact_phone?.toLowerCase().includes(query) ||
      client.city?.toLowerCase().includes(query) ||
      client.client_type.toLowerCase().includes(query)
    );
  });

  // Debug logging
  console.log('Clients data:', clients);
  console.log('Is loading:', isLoading);
  console.log('Error:', error);

  if (isLoading) {
    return <Spinner size="lg" className="py-12" />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded max-w-lg">
          <p className="font-bold">Error loading clients</p>
          <p className="text-sm">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* New Client Modal */}
      <NewClientModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />

      {/* Page Title and Actions */}
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          <PlusIcon className="h-5 w-5" />
          <span>New Client</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setTypeFilter('all')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                typeFilter === 'all'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              All Clients
              {clients && (
                <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                  {clients.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setTypeFilter('residential')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                typeFilter === 'residential'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Residential
              {clients && (
                <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                  {clients.filter(c => c.client_type === 'residential').length}
                </span>
              )}
            </button>
            <button
              onClick={() => setTypeFilter('contractor')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                typeFilter === 'contractor'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Contractor
              {clients && (
                <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                  {clients.filter(c => c.client_type === 'contractor').length}
                </span>
              )}
            </button>
            <button
              onClick={() => setTypeFilter('commercial')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                typeFilter === 'commercial'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Commercial
              {clients && (
                <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                  {clients.filter(c => c.client_type === 'commercial').length}
                </span>
              )}
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
            placeholder="Search clients by name, email, phone, city, or type..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Client List */}
      <div>
        {!clients || clients.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <UserGroupIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No clients yet</h3>
            <p className="text-gray-500 mb-6">Get started by adding your first client.</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center space-x-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <PlusIcon className="h-5 w-5" />
              <span>Add Client</span>
            </button>
          </div>
        ) : filteredClients && filteredClients.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <MagnifyingGlassIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No clients found</h3>
            <p className="text-gray-500 mb-4">No clients match your search criteria.</p>
            <button
              onClick={() => setSearchQuery('')}
              className="text-purple-600 hover:text-purple-700 font-medium"
            >
              Clear search
            </button>
          </div>
        ) : (
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Phone
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredClients?.map((client) => {
                  console.log('Rendering client:', client);
                  return (
                    <tr
                      key={client.id}
                      onClick={() => navigate(`/clients/${client.id}`)}
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {client.client_name || 'No name'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {client.primary_contact_email || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {client.primary_contact_phone || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {client.client_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          Active
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
