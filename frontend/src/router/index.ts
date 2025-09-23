// frontend/src/router/index.ts

/**
 * Vue Router Configuration
 * 
 * This file manages all navigation in the CAAS platform.
 * It includes:
 * - Public routes (login, register)
 * - Protected routes (dashboard, vendors, etc.)
 * - Navigation guards for security
 * - Role-based access control
 */

import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Route type with meta information for access control
type RouteMeta = {
  requiresAuth?: boolean
  roles?: string[]
  title?: string
}

/**
 * Public Routes
 * These routes are accessible without authentication
 */
const publicRoutes: RouteRecordRaw[] = [
  {
    path: '/auth',
    name: 'Auth',
    redirect: '/auth/login',
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/auth/LoginView.vue'),
        meta: {
          title: 'Login - CAAS Platform'
        }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/views/auth/RegisterView.vue'),
        meta: {
          title: 'Register - CAAS Platform'
        }
      },
      {
        path: '2fa',
        name: 'TwoFactorAuth',
        component: () => import('@/views/auth/TwoFactorAuth.vue'),
        meta: {
          title: 'Two-Factor Authentication - CAAS Platform'
        }
      },
      {
        path: 'forgot-password',
        name: 'ForgotPassword',
        component: () => import('@/views/auth/ForgotPasswordView.vue'),
        meta: {
          title: 'Reset Password - CAAS Platform'
        }
      },
      {
        path: 'reset-password/:token',
        name: 'ResetPassword',
        component: () => import('@/views/auth/ResetPasswordView.vue'),
        meta: {
          title: 'Reset Password - CAAS Platform'
        }
      },
      {
        path: 'sso/callback',
        name: 'SSOCallback',
        component: () => import('@/views/auth/SSOCallbackView.vue'),
        meta: {
          title: 'SSO Login - CAAS Platform'
        }
      }
    ]
  }
]

/**
 * Protected Routes
 * These routes require authentication
 */
const protectedRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: {
      requiresAuth: true
    },
    children: [
      // Dashboard - available to all authenticated users
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: {
          requiresAuth: true,
          title: 'Dashboard - CAAS Platform'
        }
      },
      
      // Vendor Management - for healthcare orgs and admins
      {
        path: 'vendors',
        name: 'Vendors',
        component: () => import('@/views/vendors/VendorListView.vue'),
        meta: {
          requiresAuth: true,
          roles: ['admin', 'healthcare_org'],
          title: 'Vendors - CAAS Platform'
        }
      },
      {
        path: 'vendors/new',
        name: 'VendorCreate',
        component: () => import('@/views/vendors/VendorCreateView.vue'),
        meta: {
          requiresAuth: true,
          roles: ['admin', 'healthcare_org'],
          title: 'Add Vendor - CAAS Platform'
        }
      },
      {
        path: 'vendors/:id',
        name: 'VendorDetail',
        component: () => import('@/views/vendors/VendorDetailView.vue'),
        meta: {
          requiresAuth: true,
          title: 'Vendor Details - CAAS Platform'
        }
      },
      
      // Assessments
      {
        path: 'assessments',
        name: 'Assessments',
        component: () => import('@/views/assessments/AssessmentListView.vue'),
        meta: {
          requiresAuth: true,
          title: 'Assessments - CAAS Platform'
        }
      },
      {
        path: 'assessments/:id',
        name: 'AssessmentDetail',
        component: () => import('@/views/assessments/AssessmentDetailView.vue'),
        meta: {
          requiresAuth: true,
          title: 'Assessment - CAAS Platform'
        }
      },
      
      // Documents
      {
        path: 'documents',
        name: 'Documents',
        component: () => import('@/views/documents/DocumentListView.vue'),
        meta: {
          requiresAuth: true,
          title: 'Documents - CAAS Platform'
        }
      },
      
      // User Profile
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/ProfileView.vue'),
        meta: {
          requiresAuth: true,
          title: 'My Profile - CAAS Platform'
        }
      },
      {
        path: 'profile/security',
        name: 'ProfileSecurity',
        component: () => import('@/views/profile/SecuritySettingsView.vue'),
        meta: {
          requiresAuth: true,
          title: 'Security Settings - CAAS Platform'
        }
      },
      
      // Admin only routes
      {
        path: 'admin',
        name: 'Admin',
        redirect: '/admin/users',
        meta: {
          requiresAuth: true,
          roles: ['admin']
        },
        children: [
          {
            path: 'users',
            name: 'AdminUsers',
            component: () => import('@/views/admin/UserManagementView.vue'),
            meta: {
              requiresAuth: true,
              roles: ['admin'],
              title: 'User Management - CAAS Platform'
            }
          },
          {
            path: 'audit-logs',
            name: 'AdminAuditLogs',
            component: () => import('@/views/admin/AuditLogView.vue'),
            meta: {
              requiresAuth: true,
              roles: ['admin'],
              title: 'Audit Logs - CAAS Platform'
            }
          }
        ]
      }
    ]
  }
]

/**
 * Error Routes
 * Handle 404 and other errors
 */
const errorRoutes: RouteRecordRaw[] = [
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/errors/ForbiddenView.vue'),
    meta: {
      title: 'Access Denied - CAAS Platform'
    }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/errors/NotFoundView.vue'),
    meta: {
      title: 'Page Not Found - CAAS Platform'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

/**
 * Create the router instance
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...publicRoutes,
    ...protectedRoutes,
    ...errorRoutes
  ],
  // Scroll to top on navigation
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

/**
 * Global Navigation Guard
 * This runs before every route change
 */
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Update page title
  if (to.meta.title) {
    document.title = to.meta.title as string
  }
  
  // Prevent accessing 2FA view without an active 2FA token
  if (to.name === 'TwoFactorAuth' && !authStore.twoFactorToken) {
    return next({ name: 'Login' })
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    // Initialize auth state if not already done
    if (!authStore.isAuthenticated && !authStore.isLoading) {
      await authStore.initializeAuth()
    }
    
    // Not authenticated - redirect to 2FA if pending, otherwise login
    if (!authStore.isAuthenticated) {
      if (authStore.twoFactorRequired && authStore.twoFactorToken) {
        return next({ name: 'TwoFactorAuth' })
      }
      return next({
        name: 'Login',
        query: { 
          redirect: to.fullPath,
          ...(to.query.session_expired && { session_expired: 'true' })
        }
      })
    }
    
    // Check role-based access
    const requiredRoles = to.meta.roles as string[] | undefined
    if (requiredRoles && requiredRoles.length > 0) {
      const userRole = authStore.currentUser?.role
      
      if (!userRole || !requiredRoles.includes(userRole)) {
        // User doesn't have required role - show forbidden
        return next({ name: 'Forbidden' })
      }
    }
    
    // Reset session timers on navigation (user activity)
    authStore.resetSessionTimers()
  }
  
  // Already authenticated user trying to access auth pages (except 2FA)
  if (authStore.isAuthenticated && to.path.startsWith('/auth') && to.path !== '/auth/2fa') {
    return next({ name: 'Dashboard' })
  }
  
  // All checks passed - proceed
  next()
})

/**
 * Handle errors during navigation
 */
router.onError((error) => {
  console.error('Router error:', error)
  // Could integrate with error tracking service here
})

export default router