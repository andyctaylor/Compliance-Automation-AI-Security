<template>
  <v-app>
    <router-view />
    <notification-snackbar />
  </v-app>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotification } from '@/composables/useNotification'
import { timeoutEvent } from '@/stores/auth'
import NotificationSnackbar from '@/components/common/NotificationSnackbar.vue'

const router = useRouter()
const { showWarning } = useNotification()

// Handle session timeout
const handleSessionTimeout = () => {
  console.log('Session timeout event received');
  showWarning('Your session has expired. Please sign in again.')
  router.push('/auth/login?session_expired=true')
}

onMounted(() => {
  timeoutEvent.addEventListener('session-timeout', handleSessionTimeout)
})

onUnmounted(() => {
  timeoutEvent.removeEventListener('session-timeout', handleSessionTimeout)
})
</script>