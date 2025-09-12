/**
 * useNotification Composable
 * 
 * This composable provides a centralized way to show notifications
 * throughout the application using Vuetify's snackbar component.
 * 
 * Think of it as your app's announcement system - it pops up
 * messages to keep users informed about what's happening.
 */

import { ref } from 'vue'

// Global state for notifications (shared across all components)
const snackbar = ref({
  show: false,
  message: '',
  color: 'success',
  timeout: 5000,
  multiLine: false,
})

export const useNotification = () => {
  /**
   * Show a success notification
   * Used for: Login success, data saved, etc.
   */
  const showSuccess = (message: string, timeout = 5000) => {
    snackbar.value = {
      show: true,
      message,
      color: 'success',
      timeout,
      multiLine: message.length > 80,
    }
  }

  /**
   * Show an error notification
   * Used for: API errors, validation failures, etc.
   */
  const showError = (message: string, timeout = 6000) => {
    snackbar.value = {
      show: true,
      message,
      color: 'error',
      timeout,
      multiLine: message.length > 80,
    }
  }

  /**
   * Show a warning notification
   * Used for: Session timeout warnings, unsaved changes, etc.
   */
  const showWarning = (message: string, timeout = 5000) => {
    snackbar.value = {
      show: true,
      message,
      color: 'warning',
      timeout,
      multiLine: message.length > 80,
    }
  }

  /**
   * Show an info notification
   * Used for: General information, tips, etc.
   */
  const showInfo = (message: string, timeout = 5000) => {
    snackbar.value = {
      show: true,
      message,
      color: 'info',
      timeout,
      multiLine: message.length > 80,
    }
  }

  /**
   * Hide the current notification
   */
  const hide = () => {
    snackbar.value.show = false
  }

  // Return the notification state and methods
  return {
    snackbar,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    hide,
  }
}