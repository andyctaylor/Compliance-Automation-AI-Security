/**
 * Authentication Service
 * Handles login, logout, registration, and token management
 */

import { apiClient, setTokens, clearTokens } from '../axios.config';
import type { User, LoginCredentials, TokenResponse, LoginResponse, TwoFactorResponse } from '@/types';

class AuthService {
  /**
   * Login user with email and password
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    // Send credentials to backend including remember me option
    const response = await apiClient.post<LoginResponse>('/auth/login/', {
      email: credentials.email,
      password: credentials.password,
      remember_me: credentials.rememberMe || false
    });
    
    // Save tokens only if 2FA is not required
    if (!response.data.requires2FA && response.data.access && response.data.refresh) {
      setTokens(response.data.access, response.data.refresh);
    }
    
    return response.data;
  }

  /**
   * Verify 2FA code
   */
  async verifyTwoFactor(data: { token: string; code: string }): Promise<TwoFactorResponse> {
    const response = await apiClient.post<TwoFactorResponse>('/auth/2fa/verify/', data);
    
    // Store new tokens if provided
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
    }
    if (response.data.refresh) {
      localStorage.setItem('refresh_token', response.data.refresh);
    }
    
    return response.data;
  }
  
  /**
   * Resend 2FA code
   */
  async resendTwoFactorCode(data: { token: string }): Promise<void> {
    await apiClient.post('/auth/2fa/resend/', data);
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