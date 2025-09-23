<template>
  <v-app>
    <router-view />
    <notification-snackbar />

    <!-- Global Session Warning Modal -->
    <v-dialog v-model="showSessionWarning" persistent max-width="500">
      <v-card>
        <v-card-title class="text-h6">Session expiring soon</v-card-title>
        <v-card-text>
          For security, your session will expire in about 2 minutes due to inactivity. Do you want to stay signed in?
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" color="grey" @click="logoutNow" data-testid="session-warning-logout">Logout</v-btn>
          <v-btn color="primary" @click="staySignedIn" data-testid="session-warning-stay">Stay signed in</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNotification } from '@/composables/useNotification'
import { timeoutEvent } from '@/stores/auth'
import { useAuthStore } from '@/stores/auth'
import NotificationSnackbar from '@/components/common/NotificationSnackbar.vue'

const router = useRouter()
const { showWarning, showSuccess } = useNotification()
const authStore = useAuthStore()

// Controls the global session warning modal visibility
const showSessionWarning = ref(false)

// Handle session timeout
const handleSessionTimeout = () => {
  console.log('Session timeout event received');
  showSessionWarning.value = false
  showWarning('Your session has expired. Please sign in again.')
  router.push('/auth/login?session_expired=true')
}

// Handle session warning (13-minute mark)
const handleSessionWarning = () => {
  showSessionWarning.value = true
}

// User chooses to keep session alive
const staySignedIn = async () => {
  try {
    await authStore.continueSession()
    showSessionWarning.value = false
    showSuccess('Session extended')
  } catch (error) {
    // On failure, continueSession logs out; ensure redirect
    router.push('/auth/login')
  }
}

// User chooses to logout immediately
const logoutNow = async () => {
  await authStore.logout(false)
  showSessionWarning.value = false
  router.push('/auth/login')
}

onMounted(() => {
  timeoutEvent.addEventListener('session-timeout', handleSessionTimeout)
  timeoutEvent.addEventListener('session-warning', handleSessionWarning)
})

onUnmounted(() => {
  timeoutEvent.removeEventListener('session-timeout', handleSessionTimeout)
  timeoutEvent.removeEventListener('session-warning', handleSessionWarning)
})
</script>