import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';

export function useAuth() {
  const authStore = useAuthStore();
  const router = useRouter();
  
  // Use storeToRefs for reactive state
  const { user, isAuthenticated, isLoading, isAdmin, isHealthcareOrg, isVendor, userFullName } = storeToRefs(authStore);

  const requireAuth = () => {
    if (!authStore.isAuthenticated) {
      router.push('/login');
      return false;
    }
    return true;
  };

  const requireRole = (role: string) => {
    if (!requireAuth()) return false;
    
    if (authStore.user?.role !== role) {
      router.push('/unauthorized');
      return false;
    }
    return true;
  };

  const requireAdmin = () => requireRole('admin');

  return {
    // Reactive state
    user,
    isAuthenticated,
    isLoading,
    isAdmin,
    isHealthcareOrg,
    isVendor,
    userFullName,
    
    // Methods (not reactive, direct from store)
    login: (credentials: any) => authStore.login(credentials),
    logout: () => authStore.logout(),
    updateProfile: (data: any) => authStore.updateProfile(data),
    changePassword: (oldPass: string, newPass: string) => authStore.changePassword(oldPass, newPass),
    
    // Guards
    requireAuth,
    requireRole,
    requireAdmin,
  };
}