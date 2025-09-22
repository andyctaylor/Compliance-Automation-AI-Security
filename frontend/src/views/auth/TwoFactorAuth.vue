<!-- frontend/src/views/auth/TwoFactorAuth.vue -->
<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-700 to-blue-400 flex justify-center items-center p-5">
    <div class="bg-white rounded-2xl p-8 w-full max-w-[500px] shadow-xl">
      <!-- Logo Section -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center bg-[#034c81] px-6 py-3 rounded-lg">
          <span class="text-white text-lg font-semibold">CAAS Logo</span>
        </div>
        <h2 class="text-gray-600 mt-2">Compliance Automation AI System</h2>
      </div>

      <!-- 2FA Header -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-semibold text-gray-800 mb-2">Two-Factor Authentication</h1>
        <p class="text-gray-600">Enter the 6-digit code sent to your email</p>
      </div>

      <!-- Verification Code Input -->
      <div class="mb-8">
        <div class="flex justify-center mb-6">
          <div class="inline-flex items-center gap-3 p-3 rounded-xl border border-gray-300 bg-gray-50 shadow-sm">
            <input
              v-for="(digit, index) in verificationCode"
              :key="index"
              :ref="(el) => setDigitRef(el, index)"
              type="text"
              maxlength="1"
              v-model="verificationCode[index]"
              @input="handleInput(index, $event)"
              @keydown="handleKeydown(index, $event)"
              @paste="handlePaste($event)"
              @focus="focusedIndex = index"
              @blur="focusedIndex = -1"
              :class="{
                'w-12 h-12 text-center text-2xl font-semibold border-2 rounded-md focus:outline-none transition-all duration-200 bg-white text-gray-900 shadow-sm': true,
                'border-blue-500 bg-blue-50 ring-2 ring-blue-200': focusedIndex === index,
                'border-red-500 bg-red-50 ring-2 ring-red-200': hasError,
                'border-green-500 bg-green-50 ring-2 ring-green-200': isSuccess,
                'border-gray-400': focusedIndex !== index && !hasError && !isSuccess
              }"
            />
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg mb-4 transition-all duration-300">
          <div class="flex items-center">
            <i class="fas fa-exclamation-circle mr-2"></i>
            <span>{{ errorMessage }}</span>
          </div>
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="bg-green-100 border border-green-300 text-green-700 px-4 py-3 rounded-lg mb-4 transition-all duration-300">
          <div class="flex items-center">
            <i class="fas fa-check-circle mr-2"></i>
            <span>{{ successMessage }}</span>
          </div>
        </div>

        <!-- Resend Message -->
        <div v-if="resendMessage" class="bg-blue-100 border border-blue-300 text-blue-700 px-4 py-3 rounded-lg mb-4 transition-all duration-300">
          <div class="flex items-center">
            <i class="fas fa-paper-plane mr-2"></i>
            <span>{{ resendMessage }}</span>
          </div>
        </div>
      </div>

      <!-- Timer and Attempts -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-full border-4 border-blue-200 mb-4 relative">
          <div
            class="absolute inset-0 rounded-full border-4 border-blue-500 transition-all duration-1000"
            :style="{ 'clip-path': `polygon(50% 0%, ${50 + 50 * Math.cos((progress * 360 - 90) * Math.PI / 180)}% ${50 + 50 * Math.sin((progress * 360 - 90) * Math.PI / 180)}%, 50% 50%)` }"
            style="transform: rotate(-90deg)"
          ></div>
          <span class="text-lg font-semibold text-gray-800">{{ formattedTime }}</span>
        </div>
        <p :class="{
          'text-sm': true,
          'text-red-600': remainingAttempts <= 2,
          'text-gray-600': remainingAttempts > 2
        }">
          Remaining attempts: {{ remainingAttempts }}
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="space-y-4 mb-6">
        <button
          @click="verifyCode"
          :disabled="!isCodeComplete || isLoading"
          :class="{
            'w-full py-3 rounded-lg rounded-button whitespace-nowrap cursor-pointer font-semibold transition-all duration-200': true,
            'bg-[#034c81] text-white hover:bg-blue-900': isCodeComplete && !isLoading,
            'bg-gray-300 text-gray-500 cursor-not-allowed': !isCodeComplete || isLoading
          }"
        >
          <span v-if="!isLoading">Verify Code</span>
          <span v-else class="flex items-center justify-center">
            <i class="fas fa-spinner fa-spin mr-2"></i>
            Verifying...
          </span>
        </button>

        <button
          @click="resendCode"
          :disabled="resendCooldown > 0"
          :class="{
            'w-full py-3 rounded-lg rounded-button whitespace-nowrap cursor-pointer font-semibold border-2 transition-all duration-200': true,
            'border-[#034c81] text-[#034c81] hover:bg-blue-50': resendCooldown === 0,
            'border-gray-300 text-gray-400 cursor-not-allowed': resendCooldown > 0
          }"
        >
          <span v-if="resendCooldown === 0">Resend Code</span>
          <span v-else>Resend in {{ resendCooldown }}s</span>
        </button>
      </div>

      <!-- Back to Login -->
      <div class="text-center mb-6">
        <a href="#" @click.prevent="backToLogin" class="text-blue-600 hover:underline cursor-pointer">
          <i class="fas fa-arrow-left mr-2"></i>
          Back to Login
        </a>
      </div>

      <!-- Security Footer -->
      <div class="border-t border-gray-200 pt-6">
        <div class="flex justify-center gap-6 mb-3">
          <div class="flex items-center text-green-600">
            <i class="fas fa-shield-alt mr-2"></i>
            <span class="text-sm">HIPAA Compliant</span>
          </div>
          <div class="flex items-center text-green-600">
            <i class="fas fa-lock mr-2"></i>
            <span class="text-sm">256-bit Encryption</span>
          </div>
        </div>
        <p class="text-center text-gray-600 text-sm">
          Session expires after 15 minutes of inactivity
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, type ComponentPublicInstance } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Optional logging for this view
const LOG_2FA = (import.meta as any).env?.VITE_LOG_2FA === 'true'
const log2FA = (...args: any[]) => { if (LOG_2FA) console.log(...args) }

log2FA(' TwoFactorAuth: Component script loading...')

// Store and router
const authStore = useAuthStore()
const router = useRouter()

// Component state
const verificationCode = ref(['', '', '', '', '', ''])
const digitRefs = ref<(HTMLInputElement | null)[]>([])
const focusedIndex = ref(0)
const hasError = ref(false)
const isSuccess = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const resendMessage = ref('')
const remainingAttempts = ref(5)
const timeRemaining = ref(300) // 5 minutes in seconds
const resendCooldown = ref(0)

// Timers
let timer: number | null = null
let resendTimer: number | null = null

// Computed properties
const isCodeComplete = computed(() => {
  return verificationCode.value.every(digit => digit !== '')
})

const formattedTime = computed(() => {
  const minutes = Math.floor(timeRemaining.value / 60)
  const seconds = timeRemaining.value % 60
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

const progress = computed(() => {
  return (300 - timeRemaining.value) / 300
})

// Get the 2FA token from auth store
const twoFactorToken = computed(() => authStore.twoFactorToken)

// Input handlers
const handleInput = (index: number, event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value
  
  // Only allow digits
  if (!/^\d*$/.test(value)) {
    target.value = ''
    verificationCode.value[index] = ''
    return
  }

  verificationCode.value[index] = value
  clearMessages()

  // Move to next input if value entered
  if (value && index < 5) {
    focusNext(index + 1)
  }

  // Auto-submit when complete
  if (isCodeComplete.value) {
    setTimeout(() => {
      verifyCode()
    }, 100)
  }
}

const handleKeydown = (index: number, event: KeyboardEvent) => {
  if (event.key === 'Backspace' && !verificationCode.value[index] && index > 0) {
    focusPrevious(index - 1)
  } else if (event.key === 'ArrowLeft' && index > 0) {
    event.preventDefault()
    focusPrevious(index - 1)
  } else if (event.key === 'ArrowRight' && index < 5) {
    event.preventDefault()
    focusNext(index + 1)
  }
}

const handlePaste = (event: ClipboardEvent) => {
  event.preventDefault()
  const pastedData = event.clipboardData?.getData('text') || ''
  const digits = pastedData.replace(/\D/g, '').slice(0, 6).split('')
  
  // Fill all digits
  for (let i = 0; i < 6; i++) {
    verificationCode.value[i] = digits[i] || ''
  }

  // Auto-submit if 6 digits pasted
  if (digits.length === 6) {
    setTimeout(() => {
      verifyCode()
    }, 100)
  }
}

// Focus management
const focusNext = (index: number) => {
  focusedIndex.value = index
  nextTick(() => {
    if (digitRefs.value[index]) {
      digitRefs.value[index]?.focus()
    }
  })
}

const focusPrevious = (index: number) => {
  focusedIndex.value = index
  nextTick(() => {
    if (digitRefs.value[index]) {
      digitRefs.value[index]?.focus()
      digitRefs.value[index]?.select()
    }
  })
}

// API calls
const verifyCode = async () => {
  if (!isCodeComplete.value || isLoading.value) return
  if (!twoFactorToken.value) {
    errorMessage.value = 'Session expired. Please login again.'
    setTimeout(() => router.push('/auth/login'), 2000)
    return
  }

  isLoading.value = true
  clearMessages()

  try {
    const code = verificationCode.value.join('')
    
    // Call the verify endpoint through auth store
    await authStore.verifyTwoFactor(code)
    
    // Success!
    isSuccess.value = true
    successMessage.value = 'Code verified successfully! Redirecting...'
    
    // Redirect to dashboard
    setTimeout(() => {
      router.push('/dashboard')
    }, 1500)
    
  } catch (error: any) {
    hasError.value = true
    
    // Handle specific error cases
    if (error.response?.status === 429) {
      errorMessage.value = error.response.data.error || 'Too many attempts. Please try again later.'
      setTimeout(() => {
        authStore.clearTwoFactorToken()
        router.push('/auth/login')
      }, 3000)
    } else if (error.response?.data?.remainingAttempts !== undefined) {
      remainingAttempts.value = error.response.data.remainingAttempts
      errorMessage.value = error.response.data.error || `Invalid code. ${remainingAttempts.value} attempts remaining.`
      
      // Clear the code for retry
      verificationCode.value = ['', '', '', '', '', '']
      focusNext(0)
    } else {
      errorMessage.value = error.response?.data?.error || 'Invalid verification code'
    }
  } finally {
    isLoading.value = false
  }
}

const resendCode = async () => {
  if (resendCooldown.value > 0) return
  if (!twoFactorToken.value) {
    errorMessage.value = 'Session expired. Please login again.'
    setTimeout(() => router.push('/auth/login'), 2000)
    return
  }

  try {
    // Call resend through auth store
    await authStore.resendTwoFactorCode()
    
    resendMessage.value = 'New verification code sent to your email.'
    remainingAttempts.value = 5 // Reset attempts
    timeRemaining.value = 300 // Reset timer
    
    // Start cooldown
    resendCooldown.value = 60
    startResendCooldown()
    clearErrorStates()
    
    // Clear code inputs
    verificationCode.value = ['', '', '', '', '', '']
    focusNext(0)

    // Clear resend message after 5 seconds
    setTimeout(() => {
      resendMessage.value = ''
    }, 5000)
    
  } catch (error: any) {
    errorMessage.value = error.response?.data?.error || 'Failed to resend code'
  }
}

// Timer functions
const startTimer = () => {
  timer = window.setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--
    } else {
      if (timer) clearInterval(timer)
      errorMessage.value = 'Verification code has expired. Please login again.'
      hasError.value = true
      // Redirect to login after showing message
      setTimeout(() => {
        authStore.clearTwoFactorToken()
        router.push('/auth/login')
      }, 2000)
    }
  }, 1000)
}

const startResendCooldown = () => {
  resendTimer = window.setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value === 0 && resendTimer) {
      clearInterval(resendTimer)
    }
  }, 1000)
}

// Utility functions
const clearMessages = () => {
  errorMessage.value = ''
  successMessage.value = ''
  resendMessage.value = ''
  clearErrorStates()
}

const clearErrorStates = () => {
  hasError.value = false
  isSuccess.value = false
}

// Navigation
const backToLogin = () => {
  router.push('/auth/login')
}

// Lifecycle
onMounted(() => {
  log2FA(' TwoFactorAuth: Component mounted')
  
  // Check if we have a 2FA token
  if (!twoFactorToken.value) {
    log2FA(' TwoFactorAuth: No 2FA token, redirecting to login')
    router.push('/auth/login')
    return
  }
  
  startTimer()
  
  // Focus first input after mount
  nextTick(() => {
    if (digitRefs.value[0]) {
      digitRefs.value[0]?.focus()
    }
  })
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (resendTimer) clearInterval(resendTimer)
})

// Typed and stable ref setter to satisfy TS and avoid unnecessary reactive churn
const setDigitRef = (el: Element | ComponentPublicInstance | null, index: number) => {
  const input = el as HTMLInputElement | null
  if (digitRefs.value[index] !== input) {
    digitRefs.value[index] = input
  }
}
</script>

<style scoped>
/* Remove number input arrows */
input[type="text"]::-webkit-inner-spin-button,
input[type="text"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Input focus animations */
input {
  transition: all 0.2s ease-in-out;
}

input:focus {
  transform: scale(1.05);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Button hover effects */
button:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

button:not(:disabled):active {
  transform: translateY(0);
}

/* Loading spinner */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.fa-spin {
  animation: spin 1s linear infinite;
}

/* Timer pulse animation */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.timer-warning {
  animation: pulse 2s infinite;
}
</style>