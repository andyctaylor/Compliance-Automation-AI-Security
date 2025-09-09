/**
 * Main Application Entry Point
 */

import { createApp } from 'vue'
import App from './App.vue'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

// Create vuetify instance
const vuetify = createVuetify({
  components,
  directives,
})

// Create and mount app
createApp(App)
  .use(vuetify)
  .mount('#app')