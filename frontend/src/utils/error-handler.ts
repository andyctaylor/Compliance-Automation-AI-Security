/**
 * Error Handling Utilities
 * 
 * Provides consistent error messages for the UI
 */

import { AxiosError } from 'axios';
import type { ApiError } from '@/types';

export class AppError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export function handleApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    const apiError = error.response?.data as ApiError;
    
    // Handle specific error formats
    if (apiError?.detail) {
      return apiError.detail;
    }
    
    // Handle field errors
    if (apiError && typeof apiError === 'object') {
      const firstError = Object.values(apiError)[0];
      if (Array.isArray(firstError)) {
        return firstError[0];
      } else if (typeof firstError === 'string') {
        return firstError;
      }
    }
    
    // Handle common HTTP errors
    switch (error.response?.status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'You are not authorized. Please login again.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return error.message || 'An unexpected error occurred.';
    }
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred.';
}