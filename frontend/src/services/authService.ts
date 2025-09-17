import axios from 'axios'
import type { AxiosInstance } from 'axios'

// Define types for our registration data
interface OrganizationRegistrationData {
  // Step 1
  orgName: string
  orgType: string
  city?: string
  state?: string
  adminEmail: string
  phoneNumber?: string
  // Step 2
  firstName: string
  lastName: string
  jobTitle: string
  password: string
  mobilePhone: string
  securityQuestion: string
  securityAnswer: string
  // Step 3
  acceptTerms: boolean
  acceptBAA: boolean
  acceptMarketing?: boolean
}

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Auth service methods
export const authService = {
  // Register new organization and admin user
  async register(data: OrganizationRegistrationData) {
    try {
      const response = await apiClient.post('/auth/register/', {
        // Organization data
        organization: {
          name: data.orgName,
          type: data.orgType,
          city: data.city,
          state: data.state,
          phone: data.phoneNumber
        },
        // Admin user data
        admin: {
          email: data.adminEmail,
          password: data.password,
          first_name: data.firstName,
          last_name: data.lastName,
          job_title: data.jobTitle,
          mobile_phone: data.mobilePhone,
          security_question: data.securityQuestion,
          security_answer: data.securityAnswer
        },
        // Agreements
        agreements: {
          accept_terms: data.acceptTerms,
          accept_baa: data.acceptBAA,
          accept_marketing: data.acceptMarketing
        }
      })
      
      return response.data
    } catch (error: any) {
      // Handle specific error cases
      if (error.response?.status === 409) {
        throw new Error('An organization with this email already exists')
      } else if (error.response?.status === 400) {
        // Extract validation errors
        const errors = error.response.data
        const firstError = Object.values(errors)[0]
        throw new Error(Array.isArray(firstError) ? firstError[0] : firstError)
      }
      
      throw new Error('Registration failed. Please try again.')
    }
  },

  // Check if email is already registered
  async checkEmailExists(email: string) {
    try {
      const response = await apiClient.post('/auth/check-email/', { email })
      return response.data.exists
    } catch (error) {
      console.error('Email check failed:', error)
      return false
    }
  }
}