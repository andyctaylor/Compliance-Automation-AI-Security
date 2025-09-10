/**
 * Authentication Service
 * Handles login, logout, registration, and token management
 */

import { apiClient, setTokens, clearTokens } from '../axios.config';
import type { User, LoginCredentials, TokenResponse } from '@/types';

class AuthService {
  /**
   * Login user with email and password
   */
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/login/', credentials);
    
    // Save tokens
    setTokens(response.data.access, response.data.refresh);
    
    return response.data;
  }

  /**
   * Logout user and clear tokens
   */
  async logout(): Promise<void> {
    try {
      // Call logout endpoint if you have one
      await apiClient.post('/auth/logout/');
    } catch (error) {
      // Silent fail - we're logging out anyway
    } finally {
      clearTokens();
    }
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/user/');
    return response.data;
  }

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await apiClient.patch<User>('/auth/user/', data);
    return response.data;
  }

  /**
   * Change password
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  }
}

export const authService = new AuthService();