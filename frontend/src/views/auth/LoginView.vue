<template>
  <div class="login-page">
    <v-card class="login-card">
      <!-- Logo Section -->
      <div class="text-center mb-6">
        <div class="logo-container">
          <span class="logo-text">CAAS</span>
        </div>
      </div>

      <!-- Welcome Text -->
      <h1 class="welcome-title text-center">Welcome Back</h1>
      <p class="welcome-subtitle text-center mb-6">Sign in to your account</p>

      <!-- Login Form -->
      <v-form ref="loginForm" @submit.prevent="handleLogin">
        <!-- Email Field -->
        <div class="form-group">
          <label class="field-label">Email Address</label>
          <input
            type="email"
            class="custom-input"
            placeholder="Enter your email address"
            v-model="credentials.email"
            :disabled="loading"
            required
          />
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>

        <!-- Password Field -->
        <div class="form-group">
          <label class="field-label">Password</label>
          <div class="password-input-container">
            <input
              :type="showPassword ? 'text' : 'password'"
              class="custom-input"
              placeholder="Enter your password"
              v-model="credentials.password"
              :disabled="loading"
              required
            />
            <button 
              type="button"
              class="toggle-password" 
              @click="showPassword = !showPassword"
              tabindex="-1"
            >
              <v-icon :icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'" size="20" />
            </button>
          </div>
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <!-- Remember Me & Forgot Password -->
        <div class="remember-forgot-container">
          <label class="remember-me">
            <input type="checkbox" v-model="rememberMe" />
            <span>Remember me</span>
          </label>
          <a href="/auth/forgot-password" class="forgot-link">Forgot password?</a>
        </div>

        <!-- Sign In Button -->
        <v-btn
          type="submit"
          block
          class="sign-in-btn"
          :loading="loading"
          :disabled="loading || !credentials.email || !credentials.password"
        >
          Sign In
        </v-btn>
      </v-form>

      <!-- Divider -->
      <div class="divider-container my-6">
        <span class="divider-text">Or continue with</span>
      </div>

      <!-- SSO Button -->
      <v-btn
        block
        variant="outlined"
        class="google-btn"
        @click="handleSSO"
        :disabled="loading"
      >
        <v-icon icon="mdi-microsoft" class="mr-2" />
        Sign in with SSO
      </v-btn>

      <!-- Security Footer -->
      <div class="security-info mt-6">
        <div class="security-item">
          <v-icon icon="mdi-shield-check" size="18" color="success" />
          <span>HIPAA Compliant</span>
        </div>
        <div class="security-item">
          <v-icon icon="mdi-lock" size="18" color="success" />
          <span>256-bit Encryption</span>
        </div>
      </div>
      <p class="session-info">Session expires after 15 minutes of inactivity</p>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotification } from '@/composables/useNotification'
import type { LoginCredentials } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { showError, showSuccess, showWarning } = useNotification()

const loginForm = ref()
const loading = ref(false)
const showPassword = ref(false)
const rememberMe = ref(false)

const credentials = ref<LoginCredentials>({
  email: '',
  password: ''
})

const errors = ref({
  email: '',
  password: ''
})

const handleLogin = async () => {
  errors.value = { email: '', password: '' }
  
  if (!credentials.value.email || !credentials.value.password) {
    if (!credentials.value.email) errors.value.email = 'Email is required'
    if (!credentials.value.password) errors.value.password = 'Password is required'
    return
  }

  loading.value = true

  try {
    const response = await authStore.login({
      email: credentials.value.email,
      password: credentials.value.password,
      rememberMe: rememberMe.value
    })

    if (response.requires2FA) {
      // Redirect to 2FA page instead of showing dialog
      showWarning('Check your email for verification code')
      await router.push('/auth/2fa')
    } else {
      showSuccess('Welcome back!')
      const redirectTo = route.query.redirect as string || '/dashboard'
      await router.push(redirectTo)
    }
  } catch (error: any) {
    if (error.response?.status === 429) {
      // Account temporarily locked due to too many failed 2FA attempts
      errors.value.email = error.response.data?.error || 'Account temporarily locked. Please try again in 1 minute.'
    } else if (error.response?.status === 401) {
      errors.value.email = 'Invalid email or password'
    } else {
      showError('An error occurred. Please try again.')
    }
  } finally {
    loading.value = false
  }
}

const handleSSO = () => {
  loading.value = true
  const returnUrl = encodeURIComponent(window.location.origin + '/auth/sso/callback')
  window.location.href = `/api/auth/sso/login?return_url=${returnUrl}`
}

onMounted(() => {
  if (route.query.session_expired === 'true') {
    showWarning('Your session has expired. Please sign in again.')
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #0066b2 0%, #00a6ff 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 460px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.logo-container {
  display: inline-flex;
  align-items: center;
  background: #034c81;
  padding: 12px 24px;
  border-radius: 8px;
}

.logo-text {
  color: white;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.welcome-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.form-group {
  margin-bottom: 20px;
}

.field-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.custom-input {
  width: 100%;
  height: 44px;
  padding: 0 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  transition: all 0.2s ease;
  font-family: inherit;
}

.custom-input:focus {
  border-color: #0066b2;
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 102, 178, 0.1);
}

.custom-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.password-input-container {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-password:hover {
  color: #333;
}

.error-message {
  color: #d32f2f;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.remember-forgot-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
}

.remember-me input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.forgot-link {
  color: #0066b2;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
}

.sign-in-btn {
  background-color: #034c81 !important;
  color: white !important;
  height: 48px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  letter-spacing: 0.5px !important;
  border-radius: 8px !important;
  box-shadow: none !important;
}

.sign-in-btn:hover {
  background-color: #023a61 !important;
}

.divider-container {
  position: relative;
  text-align: center;
}

.divider-container::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #e0e0e0;
}

.divider-text {
  background: white;
  padding: 0 16px;
  color: #666;
  font-size: 14px;
  position: relative;
  display: inline-block;
}

.google-btn {
  border: 1px solid #e0e0e0 !important;
  background-color: white !important;
  color: #333 !important;
  height: 48px !important;
  font-size: 16px !important;
  font-weight: 500 !important;
  text-transform: none !important;
  border-radius: 8px !important;
  box-shadow: none !important;
}

.google-btn:hover {
  background-color: #f5f5f5 !important;
  border-color: #0066b2 !important;
}

.security-info {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 12px;
}

.security-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #4caf50;
  font-size: 14px;
  font-weight: 500;
}

.session-info {
  text-align: center;
  color: #666;
  font-size: 14px;
  margin: 0;
}

/* Mobile Responsive */
@media (max-width: 600px) {
  .login-card {
    padding: 24px;
    margin: 0 16px;
  }

  .welcome-title {
    font-size: 20px;
  }

  .security-info {
    flex-direction: column;
    gap: 12px;
    align-items: center;
  }
}
</style>