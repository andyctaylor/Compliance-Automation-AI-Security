<!-- frontend/src/components/auth/TwoFactorDialog.vue -->

<template>
    <!-- 
      2FA Verification Dialog
      Uses v-dialog for modal behavior
    -->
    <v-dialog
      :model-value="modelValue"
      max-width="500"
      persistent
    >
      <v-card>
        <!-- Dialog Header -->
        <v-card-title class="text-h5 text-center pt-6">
          Two-Factor Authentication
        </v-card-title>
        
        <v-card-text class="text-center pb-2">
          <p class="text-body-2 text-medium-emphasis mb-6">
            Enter the 6-digit code from your authenticator app
          </p>
          
          <!-- 6-Digit Code Input -->
          <div class="d-flex justify-center ga-2 mb-4">
            <v-text-field
              v-for="(digit, index) in codeDigits"
              :key="index"
              v-model="codeDigits[index]"
              :ref="(el) => (digitRefs[index] = el)"
              variant="outlined"
              density="comfortable"
              maxlength="1"
              class="digit-input"
              :disabled="loading"
              @input="handleDigitInput(index, $event)"
              @keydown="handleKeydown(index, $event)"
              @paste="handlePaste"
              hide-details
            />
          </div>
          
          <!-- Error Message -->
          <v-alert
            v-if="errorMessage"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            {{ errorMessage }}
          </v-alert>
          
          <!-- Resend Timer -->
          <p 
            v-if="resendTimer > 0"
            class="text-body-2 text-medium-emphasis"
          >
            Resend code in {{ resendTimer }} seconds
          </p>
          <v-btn
            v-else
            variant="text"
            size="small"
            @click="resendCode"
            :loading="resending"
          >
            Resend code
          </v-btn>
        </v-card-text>
        
        <!-- Dialog Actions -->
        <v-card-actions class="pb-4">
          <v-spacer />
          <v-btn
            variant="text"
            @click="handleCancel"
            :disabled="loading"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            @click="handleVerify"
            :loading="loading"
            :disabled="!isCodeComplete"
          >
            Verify
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup lang="ts">
  /**
   * TwoFactorDialog Component
   * 
   * Handles the second factor of authentication (2FA).
   * Users must enter a 6-digit code from their authenticator app.
   * 
   * Features:
   * - Auto-advance to next digit
   * - Paste support for copying codes
   * - Resend code functionality
   * - Clear error handling
   */
  
  import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  import { useNotification } from '@/composables/useNotification'
  
  // Props and Events
  const props = defineProps<{
    modelValue: boolean
  }>()
  
  const emit = defineEmits<{
    'update:modelValue': [value: boolean]
    'verified': []
    'cancel': []
  }>()
  
  // Store and composables
  const authStore = useAuthStore()
  const { showError } = useNotification()
  
  // Component state
  const codeDigits = ref<string[]>(['', '', '', '', '', ''])
  const digitRefs = ref<any[]>([])
  const loading = ref(false)
  const resending = ref(false)
  const errorMessage = ref('')
  const resendTimer = ref(0)
  let resendInterval: number | undefined
  
  // Computed: Check if all 6 digits are entered
  const isCodeComplete = computed(() => {
    return codeDigits.value.every(digit => digit !== '')
  })
  
  // Computed: Get the full code as a string
  const fullCode = computed(() => {
    return codeDigits.value.join('')
  })
  
  /**
   * Handle input in a digit field
   * Auto-advances to next field when digit is entered
   */
  const handleDigitInput = (index: number, event: Event) => {
    const value = (event.target as HTMLInputElement).value
    
    // Only allow numbers
    if (!/^\d*$/.test(value)) {
      codeDigits.value[index] = ''
      return
    }
    
    // Auto-advance to next field
    if (value && index < 5) {
      const nextInput = digitRefs.value[index + 1]
      nextInput?.focus()
    }
    
    // Clear error when user starts typing
    if (errorMessage.value) {
      errorMessage.value = ''
    }
  }
  
  /**
   * Handle keyboard navigation
   * Backspace moves to previous field when current is empty
   */
  const handleKeydown = (index: number, event: KeyboardEvent) => {
    if (event.key === 'Backspace' && !codeDigits.value[index] && index > 0) {
      event.preventDefault()
      const prevInput = digitRefs.value[index - 1]
      prevInput?.focus()
      codeDigits.value[index - 1] = ''
    }
    
    // Handle Enter key to submit
    if (event.key === 'Enter' && isCodeComplete.value) {
      handleVerify()
    }
  }
  
  /**
   * Handle paste event
   * Allows users to paste a 6-digit code
   */
  const handlePaste = (event: ClipboardEvent) => {
    event.preventDefault()
    const pastedText = event.clipboardData?.getData('text') || ''
    const digits = pastedText.replace(/\D/g, '').slice(0, 6).split('')
    
    // Fill the digit fields
    digits.forEach((digit, index) => {
      if (index < 6) {
        codeDigits.value[index] = digit
      }
    })
    
    // Focus the last filled field or the next empty one
    const lastFilledIndex = digits.length - 1
    const focusIndex = Math.min(lastFilledIndex + 1, 5)
    digitRefs.value[focusIndex]?.focus()
  }
  
  /**
   * Verify the 2FA code
   */
  const handleVerify = async () => {
    if (!isCodeComplete.value) return
    
    loading.value = true
    errorMessage.value = ''
    
    try {
      // Call the API to verify 2FA code
      await authStore.verifyTwoFactor(fullCode.value)
      
      // Success! Emit verified event
      emit('verified')
      
      // Reset the form
      codeDigits.value = ['', '', '', '', '', '']
    } catch (error: any) {
      // Handle different error types
      if (error.response?.status === 401) {
        errorMessage.value = 'Invalid code. Please try again.'
        // Clear the code for retry
        codeDigits.value = ['', '', '', '', '', '']
        digitRefs.value[0]?.focus()
      } else if (error.response?.status === 429) {
        errorMessage.value = 'Too many attempts. Please try again later.'
      } else {
        errorMessage.value = 'An error occurred. Please try again.'
      }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Handle cancel action
   */
  const handleCancel = () => {
    if (!loading.value) {
      codeDigits.value = ['', '', '', '', '', '']
      errorMessage.value = ''
      emit('update:modelValue', false)
      emit('cancel')
    }
  }
  
  /**
   * Resend the 2FA code
   */
  const resendCode = async () => {
    resending.value = true
    
    try {
      await authStore.resendTwoFactorCode()
      showError('A new code has been sent to your authenticator app')
      startResendTimer()
    } catch (error) {
      showError('Failed to resend code. Please try again.')
    } finally {
      resending.value = false
    }
  }
  
  /**
   * Start the resend timer (60 seconds)
   */
  const startResendTimer = () => {
    resendTimer.value = 60
    resendInterval = window.setInterval(() => {
      resendTimer.value--
      if (resendTimer.value === 0) {
        clearInterval(resendInterval)
      }
    }, 1000)
  }
  
  // Start timer when dialog opens
  watch(() => props.modelValue, (newVal) => {
    if (newVal) {
      startResendTimer()
      // Focus first digit field when dialog opens
      setTimeout(() => {
        digitRefs.value[0]?.focus()
      }, 100)
    } else {
      // Clean up when dialog closes
      clearInterval(resendInterval)
      resendTimer.value = 0
    }
  })
  
  // Clean up interval on unmount
  onUnmounted(() => {
    clearInterval(resendInterval)
  })
  </script>
  
  <style scoped>
  /**
   * Styles for the 2FA dialog
   * Makes the digit inputs look like OTP fields
   */
  
  /* Individual digit input styling */
  .digit-input {
    width: 56px;
  }
  
  /* Make the input text centered and large */
  .digit-input :deep(.v-field__input) {
    text-align: center;
    font-size: 24px !important;
    font-weight: 600;
    padding: 0 !important;
  }
  
  /* Hide the field details (error messages) */
  .digit-input :deep(.v-input__details) {
    display: none;
  }
  
  /* Focus state for digit inputs */
  .digit-input :deep(.v-field--focused) {
    box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.2);
  }
  </style>