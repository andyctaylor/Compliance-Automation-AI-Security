/**
 * Axios Configuration
 * 
 * TEACHING MOMENT: This sets up our HTTP client with:
 * - Base URL pointing to Django backend
 * - Automatic token injection
 * - Response/error interceptors
 * - Token refresh logic
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 15000, // 15 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Optional, env-controlled logging to reduce console noise in dev
const SHOULD_LOG = (import.meta as any).env?.VITE_LOG_API === 'true';

// Token management functions
const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
};

const getRefreshToken = (): string | null => {
  return localStorage.getItem('refresh_token');
};

const setTokens = (access: string, refresh: string): void => {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
};

const clearTokens = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

// Request interceptor - adds auth token to requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add auth token if available
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log request when enabled
    if (SHOULD_LOG) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handles errors and token refresh
apiClient.interceptors.response.use(
  // Success responses pass through
  (response) => response,
  
  // Error handling
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry && getRefreshToken()) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = getRefreshToken();
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/auth/refresh/`,
          { refresh: refreshToken }
        );
        
        // Save new tokens
        const { access } = response.data;
        setTokens(access, refreshToken!);
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
        
      } catch (refreshError) {
        // Refresh failed - redirect to login
        clearTokens();
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);
      }
    }
    
    // Log errors only when enabled and not expected user errors
    if (SHOULD_LOG && ![400, 401, 403, 404, 429].includes(error.response?.status || 0)) {
      console.error('[API Error]', error.response?.data || error.message);
    }
    
    return Promise.reject(error);
  }
);

export { apiClient, getAccessToken, getRefreshToken, setTokens, clearTokens };