import axios, { type AxiosInstance, type AxiosError } from 'axios';

// API base URL - Use relative path in production, localhost in development
const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '');
const API_V1_PREFIX = '/api/v1';

// Token storage keys
const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_V1_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // If 401 and haven't retried yet, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
        if (!refreshToken) {
          // No refresh token, redirect to login
          window.location.href = '/login';
          return Promise.reject(error);
        }

        // Try to refresh the access token
        const response = await axios.post(`${API_BASE_URL}${API_V1_PREFIX}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        localStorage.setItem(TOKEN_KEY, access_token);

        // Retry the original request with new token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth service
export const authService = {
  login: async (email: string, password: string) => {
    const response = await axios.post(
      `${API_BASE_URL}${API_V1_PREFIX}/auth/login`,
      {
        email,
        password,
      }
    );

    const { access_token, refresh_token, user } = response.data;

    // Store tokens
    localStorage.setItem(TOKEN_KEY, access_token);
    if (refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
    }

    return { user, access_token };
  },

  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },

  getToken: () => localStorage.getItem(TOKEN_KEY),

  isAuthenticated: () => !!localStorage.getItem(TOKEN_KEY),
};

// Jobs service
export const jobsService = {
  getAll: async () => {
    const response = await api.get('/jobs/');
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/jobs/${id}`);
    return response.data;
  },

  getByClientId: async (clientId: number) => {
    const response = await api.get(`/jobs/`, {
      params: { client_id: clientId },
    });
    return response.data;
  },

  create: async (data: any) => {
    const response = await api.post('/jobs/', data);
    return response.data;
  },

  update: async (id: number, data: any) => {
    const response = await api.put(`/jobs/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await api.delete(`/jobs/${id}`);
    return response.data;
  },

  // Generate PO number based on client and location
  generatePO: async (params: {
    client_id: number;
    location_code: string;
    is_remake?: boolean;
    is_warranty?: boolean;
    site_address?: string | null;
  }) => {
    const response = await api.post('/jobs/generate-po', params);
    return response.data;
  },
};

// Clients service
export const clientsService = {
  getAll: async () => {
    const response = await api.get('/clients/');
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/clients/${id}`);
    return response.data;
  },

  create: async (data: any) => {
    const response = await api.post('/clients/', data);
    return response.data;
  },

  update: async (id: number, data: any) => {
    const response = await api.put(`/clients/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await api.delete(`/clients/${id}`);
    return response.data;
  },
};

// Vendors service
export const vendorsService = {
  getAll: async () => {
    const response = await api.get('/vendors/');
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/vendors/${id}`);
    return response.data;
  },

  create: async (data: any) => {
    const response = await api.post('/vendors/', data);
    return response.data;
  },

  update: async (id: number, data: any) => {
    const response = await api.put(`/vendors/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await api.delete(`/vendors/${id}`);
    return response.data;
  },
};

// Export the api instance for direct use if needed
export default api;
