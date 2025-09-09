<template>
  <v-app>
    <!-- Application Bar -->
    <v-app-bar 
      color="primary"
      density="comfortable"
      flat
    >
      <v-app-bar-title>
        CAAS - Compliance Automation Platform
      </v-app-bar-title>
      
      <v-spacer></v-spacer>
      
      <!-- This will show connection status to backend -->
      <v-chip
        :color="isConnected ? 'success' : 'error'"
        variant="flat"
        size="small"
        class="mr-4"
      >
        <v-icon start :icon="isConnected ? 'mdi-check-circle' : 'mdi-alert-circle'"></v-icon>
        {{ isConnected ? 'Connected' : 'Disconnected' }}
      </v-chip>
    </v-app-bar>

    <!-- Main Content Area -->
    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title>Backend Health Check</v-card-title>
              <v-card-text>
                <div v-if="loading">
                  <v-progress-circular indeterminate color="primary"></v-progress-circular>
                  Checking backend connection...
                </div>
                
                <div v-else-if="healthData">
                  <v-alert type="success" variant="tonal">
                    Backend is healthy! 
                  </v-alert>
                  
                  <v-list density="comfortable">
                    <v-list-item>
                      <v-list-item-title>Status</v-list-item-title>
                      <v-list-item-subtitle>{{ healthData.status }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Django Version</v-list-item-title>
                      <v-list-item-subtitle>{{ healthData.version }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Service</v-list-item-title>
                      <v-list-item-subtitle>{{ healthData.service }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </div>
                
                <div v-else-if="error">
                  <v-alert type="error" variant="tonal">
                    {{ error }}
                  </v-alert>
                </div>
              </v-card-text>
              
              <v-card-actions>
                <v-btn 
                  color="primary" 
                  @click="checkHealth"
                  :loading="loading"
                >
                  Refresh Connection
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
/**
 * Main App Component
 * This demonstrates connection to our Django backend
 */

import { ref, onMounted } from 'vue'
import axios from 'axios'

// TypeScript interface for our health check response
interface HealthCheckResponse {
  status: string
  version: string
  service: string
}

// Reactive variables (these update the UI when they change)
const isConnected = ref(false)
const loading = ref(false)
const healthData = ref<HealthCheckResponse | null>(null)
const error = ref<string | null>(null)

// Configure axios defaults for API calls
axios.defaults.baseURL = 'http://localhost:8000'

/**
 * Check the health of our backend API
 * This demonstrates how we'll make API calls throughout the app
 */
async function checkHealth() {
  loading.value = true
  error.value = null
  
  try {
    // Make GET request to our health endpoint
    const response = await axios.get<HealthCheckResponse>('/api/v1/health/')
    
    // Update our reactive variables
    healthData.value = response.data
    isConnected.value = true
  } catch (err) {
    // Handle errors gracefully
    isConnected.value = false
    if (axios.isAxiosError(err)) {
      error.value = `Failed to connect to backend: ${err.message}`
    } else {
      error.value = 'An unexpected error occurred'
    }
  } finally {
    loading.value = false
  }
}

// Check health when component mounts
onMounted(() => {
  checkHealth()
})
</script>