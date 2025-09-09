/**
 * Vuetify Configuration - CAAS Healthcare Platform
 * Based on actual Figma designs
 */

import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Light theme matching your Figma designs
const caasLightTheme = {
  dark: false,
  colors: {
    // Primary palette from your login gradient
    primary: '#034c81',         // Your main brand blue
    'primary-darken-1': '#023a61',  // Hover state
    'primary-lighten-1': '#2ca3fa', // Mid gradient
    'primary-lighten-2': '#B2EBF2', // Light gradient
    
    // Secondary (using your dashboard blue)
    secondary: '#2563EB',
    'secondary-darken-1': '#1D4ED8',
    
    // Semantic colors from your dashboard
    success: '#10B981',     // Green - Low risk
    warning: '#F59E0B',     // Orange - Medium risk
    error: '#EF4444',       // Red - High risk
    info: '#3B82F6',        // Info blue
    
    // Surface colors
    background: '#F9FAFB',  // Gray-50
    surface: '#FFFFFF',     
    'surface-variant': '#F3F4F6', // Gray-100
    
    // Text colors
    'on-background': '#111827',  // Gray-900
    'on-surface': '#374151',     // Gray-700
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    
    // Additional grays for various UI elements
    'border': '#E5E7EB',        // Gray-200
    'input-border': '#D1D5DB',  // Gray-300
    'text-secondary': '#4B5563', // Gray-600
    'icon-inactive': '#9CA3AF',  // Gray-400
  }
}

// Dark theme for night shift
const caasDarkTheme = {
  dark: true,
  colors: {
    primary: '#2ca3fa',         // Brighter blue for dark mode
    'primary-darken-1': '#034c81',
    
    secondary: '#3B82F6',
    
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#60A5FA',
    
    // Dark mode surfaces
    background: '#0F172A',      // Very dark blue
    surface: '#1E293B',         // Dark blue-gray
    'surface-variant': '#334155', // Lighter surface
    
    // Inverted text colors
    'on-background': '#F9FAFB',
    'on-surface': '#E5E7EB',
    
    'border': '#334155',
    'input-border': '#475569',
    'text-secondary': '#9CA3AF',
  }
}

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'caasLightTheme',
    themes: {
      caasLightTheme,
      caasDarkTheme,
    }
  },
  defaults: {
    global: {
      // Match your Open Sans font
      font: {
        family: 'Open Sans, sans-serif',
      },
    },
    VCard: {
      rounded: 'lg',      // 12px radius
      elevation: 1,       // Subtle shadow like your designs
      color: 'surface',
    },
    VBtn: {
      rounded: true,      // This gives 8px radius in Vuetify
      height: 48,         // Match your button height
      elevation: 0,       // Flat buttons like your design
      style: {
        textTransform: 'none',  // No uppercase
        fontWeight: 600,        // Semibold
        letterSpacing: 'normal',
      },
    },
    VTextField: {
      variant: 'outlined',
      rounded: 'lg',
      density: 'default',   // 56px height like your inputs
      color: 'primary',
    },
    VChip: {
      rounded: 'pill',      // Fully rounded like status badges
      size: 'small',
      elevation: 0,
    },
  },
})