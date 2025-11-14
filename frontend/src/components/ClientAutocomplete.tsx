import React, { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { clientsService } from '../services/api';
import type { Client } from '../types';

interface ClientAutocompleteProps {
  selectedClientId: number | null;
  onSelectClient: (clientId: number) => void;
  onRequestNewClient: (searchTerm: string) => void;
  error?: string;
}

const ClientAutocomplete: React.FC<ClientAutocompleteProps> = ({
  selectedClientId,
  onSelectClient,
  onRequestNewClient,
  error,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [displayValue, setDisplayValue] = useState('');
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Fetch all clients
  const { data: clients = [], isLoading } = useQuery<Client[]>({
    queryKey: ['clients'],
    queryFn: clientsService.getAll,
  });

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Update display value when selected client changes
  useEffect(() => {
    if (selectedClientId && clients.length > 0) {
      const client = clients.find((c) => c.id === selectedClientId);
      if (client) {
        setDisplayValue(getClientDisplayName(client));
      }
    } else {
      setDisplayValue('');
    }
  }, [selectedClientId, clients]);

  const getClientDisplayName = (client: Client): string => {
    return `${client.client_name || 'Unnamed Client'} (ID: ${client.id})`;
  };

  // Filter clients based on search term
  const filteredClients = clients.filter((client) => {
    const searchLower = searchTerm.toLowerCase();
    const name = (client.client_name || '').toLowerCase();
    const type = (client.client_type || '').toLowerCase();
    const id = client.id.toString();
    return name.includes(searchLower) || type.includes(searchLower) || id.includes(searchLower);
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    setDisplayValue(value);
    setIsOpen(true);
  };

  const handleSelectClient = (client: Client) => {
    onSelectClient(client.id);
    setDisplayValue(getClientDisplayName(client));
    setSearchTerm('');
    setIsOpen(false);
  };

  const handleFocus = () => {
    setIsOpen(true);
    setSearchTerm(displayValue);
  };

  const hasExactMatch = filteredClients.some(
    (client) => (client.client_name || '').toLowerCase() === searchTerm.toLowerCase()
  );

  const showNoMatchMessage = searchTerm.length > 2 && filteredClients.length === 0;
  const showAddSuggestion = searchTerm.length > 2 && !hasExactMatch;

  return (
    <div ref={wrapperRef} className="relative">
      {/* Input Field */}
      <div className="relative">
        <input
          type="text"
          value={displayValue}
          onChange={handleInputChange}
          onFocus={handleFocus}
          placeholder="Search for a client..."
          className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            error ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        )}
      </div>

      {error && <p className="mt-1 text-sm text-red-500">{error}</p>}

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
          {/* Loading State */}
          {isLoading && (
            <div className="px-4 py-3 text-sm text-gray-500">Loading clients...</div>
          )}

          {/* No Results */}
          {!isLoading && showNoMatchMessage && (
            <div className="px-4 py-3">
              <p className="text-sm text-gray-700 mb-2">
                Client "{searchTerm}" doesn't exist in the system.
              </p>
              <button
                type="button"
                onClick={() => {
                  onRequestNewClient(searchTerm);
                  setIsOpen(false);
                }}
                className="w-full px-3 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                + Add "{searchTerm}" as New Client
              </button>
            </div>
          )}

          {/* Client List */}
          {!isLoading && filteredClients.length > 0 && (
            <ul className="py-1">
              {filteredClients.map((client) => (
                <li key={client.id}>
                  <button
                    type="button"
                    onClick={() => handleSelectClient(client)}
                    className="w-full px-4 py-2 text-left hover:bg-blue-50 focus:bg-blue-50 focus:outline-none"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {client.client_name || 'Unnamed Client'}
                        </div>
                        <div className="text-xs text-gray-500">
                          {client.client_type} • ID: {client.id}
                        </div>
                      </div>
                      {selectedClientId === client.id && (
                        <svg
                          className="h-5 w-5 text-blue-600"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}

          {/* Add Suggestion for Partial Matches */}
          {!isLoading && showAddSuggestion && filteredClients.length > 0 && (
            <div className="border-t border-gray-200 px-4 py-2 bg-gray-50">
              <button
                type="button"
                onClick={() => {
                  onRequestNewClient(searchTerm);
                  setIsOpen(false);
                }}
                className="w-full px-3 py-2 text-sm text-blue-600 hover:text-blue-700 text-left font-medium"
              >
                + Add "{searchTerm}" as New Client
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ClientAutocomplete;
