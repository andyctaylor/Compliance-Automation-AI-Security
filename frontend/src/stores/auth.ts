import { defineStore } from 'pinia';
import { api } from '@/api';
import { clearTokens } from '@/api/axios.config';
import type { User, LoginCredentials } from '@/types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  loginError: string | null;
  sessionTimer: NodeJS.Timeout | null;
  sessionWarningTimer: NodeJS.Timeout | null;
  sessionWarningActive: boolean;
  sessionTimeout: number;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    loginError: null,
    sessionTimer: null,
    sessionWarningTimer: null,
    sessionWarningActive: false,
    sessionTimeout: 15 * 60 * 1000,
  }),

  getters: {
    currentUser: (state): User | null => state.user,
    isAdmin: (state): boolean => state.user?.role === 'admin',
    isHealthcareOrg: (state): boolean => state.user?.role === 'healthcare_org',
    isVendor: (state): boolean => state.user?.role === 'vendor',
    userFullName: (state): string => {
      if (!state.user) return '';
      return `${state.user.first_name} ${state.user.last_name}`.trim() || state.user.email;
    },
  },

  actions: {
    async login(credentials: LoginCredentials) {
      this.isLoading = true;
      this.loginError = null;

      try {
        const response = await api.auth.login(credentials);
        this.user = response.user;
        this.isAuthenticated = true;
        localStorage.setItem('user', JSON.stringify(response.user));
        return response;
      } catch (error: any) {
        this.loginError = error.response?.data?.detail || 'Login failed';
        this.isAuthenticated = false;
        this.user = null;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async logout() {
      try {
        await api.auth.logout();
      } catch (error) {
        // Silent fail
      } finally {
        this.clearAuthState();
      }
    },

    clearAuthState() {
      this.user = null;
      this.isAuthenticated = false;
      this.loginError = null;
      clearTokens();
      localStorage.removeItem('user');
    },

    async initializeAuth() {
      const savedUser = localStorage.getItem('user');
      const accessToken = localStorage.getItem('access_token');
      
      if (savedUser && accessToken) {
        try {
          this.isLoading = true;
          const user = await api.auth.getCurrentUser();
          this.user = user;
          this.isAuthenticated = true;
          localStorage.setItem('user', JSON.stringify(user));
        } catch (error) {
          this.clearAuthState();
        } finally {
          this.isLoading = false;
        }
      }
    },

    async updateProfile(data: Partial<User>) {
      if (!this.user) throw new Error('No user logged in');
      
      const updatedUser = await api.auth.updateProfile(data);
      this.user = updatedUser;
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return updatedUser;
    },

    async changePassword(oldPassword: string, newPassword: string) {
      await api.auth.changePassword(oldPassword, newPassword);
    },

    hasPermission(permission: string): boolean {
      if (this.isAdmin) return true;
      return false;
    },
  },
});