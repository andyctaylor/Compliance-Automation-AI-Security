# frontend - CAAS Frontend - Vue.js Application

## Overview

The CAAS frontend is a Vue.js 3.4 single-page application built with Vite, TypeScript, and Vuetify 3.4 for a modern, accessible healthcare compliance interface.

## Development Setup

### Using Docker (Recommended)
See main README.md for Docker setup instructions.

### Local Development

1. **Install dependencies**
   npm install

2. **Start development server**
   npm run dev

3. **Build for production**
   npm run build

## Project Structure
```
frontend/
├── src/
│   ├── assets/          # Images, fonts, styles
│   ├── components/      # Reusable components
│   ├── composables/     # Vue composition functions
│   ├── layouts/         # Page layouts
│   ├── plugins/         # Plugin configurations
│   │   └── vuetify.ts   # Vuetify setup
│   ├── router/          # Vue Router config
│   ├── services/        # API services
│   ├── stores/          # Pinia state stores
│   ├── types/           # TypeScript types
│   ├── utils/           # Helper functions
│   ├── views/           # Page components
│   ├── App.vue          # Root component
│   ├── main.ts          # App entry point
│   └── style.css        # Global styles
├── public/              # Static assets
├── index.html           # HTML entry
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite configuration
└── Dockerfile.dev       # Docker development
```

## Key Technologies

### Vue.js 3.4 with Composition API

- Modern reactive framework
- TypeScript for type safety
- Single File Components (SFC)
- Script setup syntax

### Vuetify 3.4

- Material Design 3 components
- Healthcare-appropriate theme
- Accessibility built-in
- Responsive grid system

### Vite 5.0

- Lightning-fast HMR
- Optimized production builds
- TypeScript support
- Environment variables

### Pinia (State Management)

- Type-safe stores
- DevTools integration
- Modular architecture
- Composition API friendly

## Available Scripts

### Development

- npm run dev          # Start dev server (port 3000)
- npm run build        # Build for production
- npm run preview      # Preview production build

### Code Quality

- npm run lint         # Lint code
- npm run format       # Format with Prettier
- npm run type-check   # TypeScript checking

### Testing
- npm run test         # Run unit tests
- npm run test:e2e     # Run E2E tests

## Healthcare Theme Configuration

The Vuetify theme is configured for healthcare compliance:

```
// src/plugins/vuetify.ts
{
  colors: {
    primary: '#034c81',      // Trust-building navy
    secondary: '#00BCD4',    // Healthcare teal
    success: '#4CAF50',      // Positive/healthy
    warning: '#FFA000',      // Caution
    error: '#D32F2F',        // Critical
    info: '#1976D2',         // Informational
  },
  // Accessibility-friendly typography
  typography: {
    fontFamily: 'Open Sans, sans-serif'
  }
}
```

## Component Architecture

### Base Components (/components/common/)

- BaseButton.vue - Consistent button styling
- BaseCard.vue - Card container component
- BaseInput.vue - Form input with validation
- BaseDialog.vue - Modal dialogs

### Feature Components (/components/features/)

- HealthCheck.vue - API status display
- VendorList.vue - Vendor management
- AssessmentBuilder.vue - Assessment creation
- AuditLog.vue - Compliance audit viewer

## API Integration

### Service Layer (/services/)
```
    // Example: services/api.ts
    import axios from 'axios'

    const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json'
    }
    })

    // Request interceptor for auth
    api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
    })

    export default api
```

## State Management

### Pinia Stores (/stores/)
---
    // Example: stores/auth.ts
    import { defineStore } from 'pinia'

    export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const isAuthenticated = computed(() => !!user.value)
    
    async function login(credentials) {
        // Login logic
    }
    
    return { user, isAuthenticated, login }
    })
---

## Environment Variables

### Create .env.local for local development:
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=CAAS Platform
VITE_SESSION_TIMEOUT=900000  # 15 minutes in ms

## Accessibility Features

- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader friendly
- High contrast mode ready
- Focus indicators
- ARIA labels

## Performance Optimization

- Lazy loading routes
- Component code splitting
- Image optimization
- Tree shaking unused code
- Efficient bundle sizes
- PWA capabilities

## Development Guidelines

### Component Naming

- PascalCase for components
- Prefix with feature area
- Descriptive names

### Code Style

- ESLint + Prettier
- Composition API preferred
- TypeScript for new code
- Props validation

## Git Workflow
---
    git checkout -b feature/component-name
    # Make changes
    git commit -m "feat: add new component"
    git push origin feature/component-name
---
