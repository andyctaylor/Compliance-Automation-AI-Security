import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { useAuthStore } from '@/stores/auth'

// Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'

const vuetify = createVuetify()
const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(vuetify)

// Initialize auth after pinia is installed
const authStore = useAuthStore()
authStore.initializeAuth()

app.mount('#app')