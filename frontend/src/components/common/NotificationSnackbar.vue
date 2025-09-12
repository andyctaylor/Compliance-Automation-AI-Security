<!-- frontend/src/components/common/NotificationSnackbar.vue -->

<template>
    <!-- 
      Vuetify Snackbar Component
      This appears at the bottom of the screen with your message
    -->
    <v-snackbar
      v-model="notification.show"
      :color="notification.color"
      :timeout="notification.timeout"
      :multi-line="notification.multiLine"
      location="bottom right"
      variant="elevated"
    >
      <!-- Icon based on notification type -->
      <v-icon class="mr-2">
        {{ notificationIcon }}
      </v-icon>
      
      <!-- The message text -->
      {{ notification.message }}
      
      <!-- Close button -->
      <template #actions>
        <v-btn
          variant="text"
          size="small"
          @click="notification.show = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </template>
  
  <script setup lang="ts">
  /**
   * NotificationSnackbar Component
   * 
   * This component should be placed in your main App.vue layout
   * so it's available throughout the entire application.
   */
  
  import { computed } from 'vue'
  import { useNotification } from '@/composables/useNotification'
  
  // Get the notification state from our composable
  const { snackbar: notification } = useNotification()
  
  // Compute the appropriate icon based on notification type
  const notificationIcon = computed(() => {
    const icons: Record<string, string> = {
      success: 'mdi-check-circle',
      error: 'mdi-alert-circle',
      warning: 'mdi-alert',
      info: 'mdi-information',
    }
    return icons[notification.value.color] || 'mdi-information'
  })
  </script>