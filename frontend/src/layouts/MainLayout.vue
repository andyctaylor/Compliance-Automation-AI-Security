<template>
  <v-app>
    <v-app-bar color="primary" dark>
      <v-app-bar-title>CAAS Platform</v-app-bar-title>
      <v-spacer />
      <v-btn @click="logout">Logout</v-btn>
    </v-app-bar>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const logout = async () => {
  try {
    await authStore.logout()
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    // Always redirect, even if logout fails
    await router.push('/auth/login')
  }
}
</script>