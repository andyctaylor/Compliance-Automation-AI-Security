import { defineStore } from 'pinia';
import { api } from '@/api';
import { clearTokens } from '@/api/axios.config';
import type { User, LoginCredentials, LoginResponse, TwoFactorResponse } from '@/types';

// Create event emitter for timeout
const timeoutEvent = new EventTarget();

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  loginError: string | null;
  sessionTimer: NodeJS.Timeout | null;
  sessionWarningTimer: NodeJS.Timeout | null;
  sessionWarningActive: boolean;
  sessionTimeout: number;
  twoFactorRequired: boolean;
  twoFactorToken: string | null;
  lastActivity: number;
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
    twoFactorRequired: false,
    twoFactorToken: null,
    lastActivity: Date.now(),
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
    async login(credentials: LoginCredentials): Promise<LoginResponse> {
      this.isLoading = true;
      this.loginError = null;

      try {
        const response = await api.auth.login(credentials);
        
        if (response.requires2FA) {
          this.twoFactorRequired = true;
          this.twoFactorToken = response.twoFactorToken || null;
          // Store remember me preference for after 2FA
          if (credentials.rememberMe) {
            localStorage.setItem('rememberMe', 'true');
          }
          return response;
        }
        
        // Login successful - store user data
        this.user = response.user!;
        this.isAuthenticated = true;
        
        // Handle remember me functionality
        if (credentials.rememberMe) {
          localStorage.setItem('user', JSON.stringify(response.user));
          localStorage.setItem('rememberMe', 'true');
          this.sessionTimeout = 7 * 24 * 60 * 60 * 1000;
        } else {
          sessionStorage.setItem('user', JSON.stringify(response.user));
          localStorage.removeItem('rememberMe');
          this.sessionTimeout = 15 * 60 * 1000; // 15 minutes
        }
        
        this.lastActivity = Date.now();
        this.startSessionTimers();
        this.setupActivityListeners();
        
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

    async verifyTwoFactor(code: string): Promise<void> {
      if (!this.twoFactorToken) {
        throw new Error('No 2FA token available');
      }
      
      try {
        const response = await api.auth.verifyTwoFactor({
          token: this.twoFactorToken,
          code: code
        });
        
        this.user = response.user;
        this.isAuthenticated = true;
        this.twoFactorRequired = false;
        this.twoFactorToken = null;
        
        // Check if remember me was selected during login
        const rememberMe = localStorage.getItem('rememberMe') === 'true';
        if (rememberMe) {
          localStorage.setItem('user', JSON.stringify(response.user));
          this.sessionTimeout = 7 * 24 * 60 * 60 * 1000;
        } else {
          sessionStorage.setItem('user', JSON.stringify(response.user));
          this.sessionTimeout = 15 * 60 * 1000; // 15 minutes
        }
        
        this.lastActivity = Date.now();
        this.startSessionTimers();
        this.setupActivityListeners();
      } catch (error) {
        throw error;
      }
    },

    async resendTwoFactorCode(): Promise<void> {
      if (!this.twoFactorToken) {
        throw new Error('No 2FA session active');
      }
      
      await api.auth.resendTwoFactorCode({
        token: this.twoFactorToken
      });
    },

    setupActivityListeners() {
      // Remove any existing listeners first
      this.removeActivityListeners();
      
      // Only setup for non-remember me sessions
      const rememberMe = localStorage.getItem('rememberMe') === 'true';
      if (!rememberMe && this.isAuthenticated) {
        // Track user activity
        const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart'];
        activityEvents.forEach(event => {
          window.addEventListener(event, this.handleUserActivity);
        });
      }
    },

    removeActivityListeners() {
      const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart'];
      activityEvents.forEach(event => {
        window.removeEventListener(event, this.handleUserActivity);
      });
    },

    handleUserActivity() {
      // Only reset if authenticated and not in warning period
      const authStore = useAuthStore();
      if (authStore.isAuthenticated && !authStore.sessionWarningActive) {
        authStore.resetSessionTimers();
      }
    },

    startSessionTimers() {
      this.clearSessionTimers();
      
      // Only for standard sessions, not remember me
      const rememberMe = localStorage.getItem('rememberMe') === 'true';
      if (!rememberMe) {
        // Warning at 13 minutes (2 minutes before timeout)
        this.sessionWarningTimer = setTimeout(() => {
          this.sessionWarningActive = true;
          console.log('Session warning activated - 2 minutes remaining');
          // Could show a warning dialog here
        }, 13 * 60 * 1000);
        
        // Actual timeout at 15 minutes
        this.sessionTimer = setTimeout(() => {
          console.log('Session timeout triggered');
          this.logout(true);
        }, this.sessionTimeout);
      }
    },

    clearSessionTimers() {
      if (this.sessionTimer) {
        clearTimeout(this.sessionTimer);
        this.sessionTimer = null;
      }
      if (this.sessionWarningTimer) {
        clearTimeout(this.sessionWarningTimer);
        this.sessionWarningTimer = null;
      }
      this.sessionWarningActive = false;
    },

    resetSessionTimers() {
      // Update last activity
      this.lastActivity = Date.now();
      
      // Reset the timers
      if (this.isAuthenticated) {
        console.log('Activity detected - resetting timers');
        this.startSessionTimers();
      }
    },

    async logout(isSessionTimeout = false) {
      try {
        await api.auth.logout();
      } catch (error) {
        // Silent fail
      } finally {
        this.clearAuthState();
        this.removeActivityListeners();
        // Emit event for timeout
        if (isSessionTimeout) {
          timeoutEvent.dispatchEvent(new Event('session-timeout'));
        }
      }
    },

    clearAuthState() {
      this.user = null;
      this.isAuthenticated = false;
      this.loginError = null;
      this.twoFactorRequired = false;
      this.twoFactorToken = null;
      this.clearSessionTimers();
      clearTokens();
      // Clear from both storages
      localStorage.removeItem('user');
      localStorage.removeItem('rememberMe');
      sessionStorage.removeItem('user');
    },

    async initializeAuth() {
      console.log('initializeAuth called');
      const accessToken = localStorage.getItem('access_token');
      const rememberMe = localStorage.getItem('rememberMe') === 'true';
      
      // First try to load user from storage
      const savedUserStr = rememberMe 
        ? localStorage.getItem('user')
        : sessionStorage.getItem('user');
      
      if (accessToken && savedUserStr) {
        try {
          // Load saved user first for immediate UI update
          const savedUser = JSON.parse(savedUserStr);
          this.user = savedUser;
          this.isAuthenticated = true;
          this.isLoading = false;
          
          // Set session timeout based on remember me
          if (rememberMe) {
            this.sessionTimeout = 7 * 24 * 60 * 60 * 1000;
          } else {
            this.sessionTimeout = 15 * 60 * 1000; // 15 minutes
          }
          
          this.lastActivity = Date.now();
          this.startSessionTimers();
          this.setupActivityListeners();
          
          // Then try to get fresh user data in the background
          try {
            console.log('Fetching current user...');
            const freshUser = await api.auth.getCurrentUser();
            console.log('Fresh user data:', freshUser);
            this.user = freshUser;
            
            // Update storage with fresh data
            if (rememberMe) {
              localStorage.setItem('user', JSON.stringify(freshUser));
            } else {
              sessionStorage.setItem('user', JSON.stringify(freshUser));
            }
          } catch (error) {
            console.error('Failed to fetch fresh user data:', error);
            // Keep using cached user data if API fails
          }
        } catch (error) {
          console.error('Failed to parse saved user:', error);
          this.clearAuthState();
        }
      } else if (accessToken && !savedUserStr) {
        // We have token but no user data - try to fetch it
        try {
          this.isLoading = true;
          console.log('No saved user, fetching from API...');
          const user = await api.auth.getCurrentUser();
          console.log('Fetched user:', user);
          this.user = user;
          this.isAuthenticated = true;
          
          // Save user data
          if (rememberMe) {
            localStorage.setItem('user', JSON.stringify(user));
            this.sessionTimeout = 7 * 24 * 60 * 60 * 1000;
          } else {
            sessionStorage.setItem('user', JSON.stringify(user));
            this.sessionTimeout = 15 * 60 * 1000; // 15 minutes
          }
          
          this.lastActivity = Date.now();
          this.startSessionTimers();
          this.setupActivityListeners();
        } catch (error) {
          console.error('Failed to fetch user:', error);
          this.clearAuthState();
        } finally {
          this.isLoading = false;
        }
      } else {
        // No token - ensure clean state
        console.log('No access token found');
        this.clearAuthState();
      }
    },

    async updateProfile(data: Partial<User>) {
      if (!this.user) throw new Error('No user logged in');
      
      const updatedUser = await api.auth.updateProfile(data);
      this.user = updatedUser;
      
      // Update in the appropriate storage
      const rememberMe = localStorage.getItem('rememberMe') === 'true';
      if (rememberMe) {
        localStorage.setItem('user', JSON.stringify(updatedUser));
      } else {
        sessionStorage.setItem('user', JSON.stringify(updatedUser));
      }
      
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

// Export the timeout event emitter
export { timeoutEvent };