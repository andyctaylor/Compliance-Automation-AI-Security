<template>
  <v-container fluid class="auth-container d-flex align-center justify-center">
    <v-card class="auth-card elevation-8" width="800">
      <v-card-text class="pa-10">
        
        <!-- LOGO SECTION: Stays constant across all steps -->
        <div class="text-center mb-6">
          <div class="logo-container">
            <span class="logo-text">CAAS Logo</span>
          </div>
          <p class="text-subtitle-1 text-grey-darken-1 mt-2">
            Compliance Automation AI System
          </p>
        </div>

        <!-- PROGRESS STEPS: Updates based on current step -->
        <div class="d-flex justify-center align-center ga-4 mb-8">
          <!-- Step 1 -->
          <div 
            class="step-circle" 
            :class="{ 
              'step-active': currentStep === 1, 
              'step-complete': currentStep > 1 
            }"
          >
            <v-icon v-if="currentStep > 1" size="small" color="white">mdi-check</v-icon>
            <span v-else>1</span>
          </div>
          
          <div class="step-line" :class="{ 'step-line-active': currentStep > 1 }"></div>
          
          <!-- Step 2 -->
          <div 
            class="step-circle" 
            :class="{ 
              'step-active': currentStep === 2, 
              'step-complete': currentStep > 2 
            }"
          >
            <v-icon v-if="currentStep > 2" size="small" color="white">mdi-check</v-icon>
            <span v-else>2</span>
          </div>
          
          <div class="step-line" :class="{ 'step-line-active': currentStep > 2 }"></div>
          
          <!-- Step 3 -->
          <div 
            class="step-circle" 
            :class="{ 'step-active': currentStep === 3 }"
          >
            3
          </div>
        </div>

        <!-- ANIMATED CONTENT AREA: Slides between steps -->
        <transition 
          :name="transitionName" 
          mode="out-in"
          @before-leave="beforeLeave"
          @enter="enter"
          @after-enter="afterEnter"
        >
          <!-- STEP 1: Organization Information -->
          <div v-if="currentStep === 1" key="step1" class="step-content">
            <h1 class="text-h5 text-grey-darken-4 font-weight-medium text-center mb-2">
              Organization Information
            </h1>
            <p class="text-body-2 text-grey-darken-1 text-center mb-6">
              Tell us about your healthcare organization
            </p>

            <v-form ref="step1Form" v-model="step1Valid">
              <!-- Organization Name -->
              <div class="mb-4">
                <label class="field-label">Organization Name *</label>
                <v-text-field
                  v-model="formData.orgName"
                  :rules="orgNameRules"
                  placeholder="Enter your organization name"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  class="gray-field"
                />
              </div>

              <!-- Organization Type -->
              <div class="mb-4">
                <label class="field-label">Organization Type *</label>
                <v-select
                  v-model="formData.orgType"
                  :items="organizationTypes"
                  :rules="orgTypeRules"
                  placeholder="Select organization type"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  class="gray-field"
                />
              </div>

              <!-- City and State -->
              <v-row class="mb-4">
                <v-col cols="12" sm="6">
                  <label class="field-label">City</label>
                  <v-text-field
                    v-model="formData.city"
                    placeholder="Enter city"
                    variant="outlined"
                    density="comfortable"
                    hide-details="auto"
                    class="gray-field"
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <label class="field-label">State</label>
                  <v-text-field
                    v-model="formData.state"
                    placeholder="Enter state"
                    variant="outlined"
                    density="comfortable"
                    hide-details="auto"
                    class="gray-field"
                  />
                </v-col>
              </v-row>

              <!-- Admin Email -->
              <div class="mb-4">
                <label class="field-label">Admin Email Address *</label>
                <v-text-field
                  v-model="formData.adminEmail"
                  :rules="emailRules"
                  placeholder="admin@yourorganization.com"
                  type="email"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  class="gray-field"
                />
              </div>

              <!-- Phone Number -->
              <div class="mb-6">
                <label class="field-label">Phone Number</label>
                <v-text-field
                  v-model="formData.phoneNumber"
                  placeholder="+1 (555) 123-4567"
                  type="tel"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  class="gray-field"
                />
              </div>
            </v-form>
          </div>

          <!-- STEP 2: Admin Account Setup -->
          <div v-else-if="currentStep === 2" key="step2" class="step-content">
            <h1 class="text-h5 text-grey-darken-4 font-weight-medium text-center mb-2">
              Admin Account Setup
            </h1>
            <p class="text-body-2 text-grey-darken-1 text-center mb-6">
              Create your secure administrator account
            </p>

            <v-form ref="step2Form" v-model="step2Valid">
              <!-- Name Fields -->
              <v-row class="mb-4">
                <v-col cols="12" sm="6">
                  <label class="field-label">First Name *</label>
                  <v-text-field
                    v-model="formData.firstName"
                    :rules="nameRules"
                    placeholder="Enter first name"
                    variant="outlined"
                    density="comfortable"
                    hide-details="auto"
                    class="gray-field"
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <label class="field-label">Last Name *</label>
                  <v-text-field
                    v-model="formData.lastName"
                    :rules="nameRules"
                    placeholder="Enter last name"
                    variant="outlined"
                    density="comfortable"
                    hide-details="auto"
                    class="gray-field"
                  />
                </v-col>
              </v-row>

              <!-- Job Title -->
              <div class="mb-4">
                <label class="field-label">Job Title *</label>
                <v-text-field
                  v-model="formData.jobTitle"
                  :rules="jobTitleRules"
                  placeholder="e.g., IT Administrator, Compliance Officer"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  class="gray-field"
                />
              </div>

              <!-- Password Field -->
              <div class="mb-2">
                <label class="field-label">Password *</label>
                <v-text-field
                  v-model="formData.password"
                  :rules="passwordRules"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Create a strong password"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  class="gray-field"
                  @update:model-value="checkPasswordStrength"
                >
                  <template v-slot:append-inner>
                    <v-icon
                      @click="showPassword = !showPassword"
                      style="cursor: pointer;"
                    >
                      {{ showPassword ? 'mdi-eye' : 'mdi-eye-off' }}
                    </v-icon>
                  </template>
                </v-text-field>
              </div>

              <!-- Password Strength Indicator -->
              <div v-if="formData.password" class="mb-4">
                <v-progress-linear
                  :model-value="passwordStrength.score"
                  :color="passwordStrength.color"
                  height="6"
                  rounded
                  class="mb-2"
                />
                <div class="d-flex justify-space-between">
                  <span class="text-caption" :class="`text-${passwordStrength.color}`">
                    {{ passwordStrength.label }}
                  </span>
                  <span class="text-caption text-grey">
                    HIPAA requires strong passwords
                  </span>
                </div>
                
                <!-- Password Requirements -->
                <div class="password-requirements mt-3">
                  <div v-for="req in passwordRequirements" :key="req.text" class="requirement-item">
                    <v-icon 
                      :icon="req.met ? 'mdi-check-circle' : 'mdi-circle-outline'"
                      :color="req.met ? 'success' : 'grey-lighten-1'"
                      size="x-small"
                    />
                    <span class="text-caption ml-1" :class="req.met ? 'text-grey-darken-2' : 'text-grey'">
                      {{ req.text }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Confirm Password -->
              <div class="mb-4">
                <label class="field-label">Confirm Password *</label>
                <v-text-field
                  v-model="formData.confirmPassword"
                  :rules="confirmPasswordRules"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="Re-enter your password"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  class="gray-field"
                >
                  <template v-slot:append-inner>
                    <v-icon
                      @click="showConfirmPassword = !showConfirmPassword"
                      style="cursor: pointer;"
                    >
                      {{ showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off' }}
                    </v-icon>
                  </template>
                </v-text-field>
              </div>

              <!-- 2FA Setup Section -->
              <v-alert
                type="info"
                variant="tonal"
                class="mb-4"
              >
                <div class="d-flex align-center">
                  <v-icon class="mr-2">mdi-shield-lock</v-icon>
                  <div>
                    <div class="font-weight-medium">Two-Factor Authentication Required</div>
                    <div class="text-caption">HIPAA compliance requires 2FA for all admin accounts</div>
                  </div>
                </div>
              </v-alert>

              <!-- Phone Number for 2FA -->
              <div class="mb-4">
                <label class="field-label">Mobile Phone for 2FA *</label>
                <v-text-field
                  v-model="formData.mobilePhone"
                  :rules="phoneRules"
                  placeholder="+1 (555) 123-4567"
                  type="tel"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  class="gray-field"
                />
                <p class="text-caption text-grey mt-1">
                  We'll send a verification code to this number
                </p>
              </div>

              <!-- Security Question -->
              <div class="mb-4">
                <label class="field-label">Security Question *</label>
                <v-select
                  v-model="formData.securityQuestion"
                  :items="securityQuestions"
                  :rules="securityQuestionRules"
                  placeholder="Select a security question"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  class="gray-field"
                />
              </div>

              <!-- Security Answer -->
              <div class="mb-6">
                <label class="field-label">Security Answer *</label>
                <v-text-field
                  v-model="formData.securityAnswer"
                  :rules="securityAnswerRules"
                  placeholder="Enter your answer"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  class="gray-field"
                />
              </div>
            </v-form>
          </div>

          <!-- STEP 3: Terms & Agreements -->
          <div v-else-if="currentStep === 3" key="step3" class="step-content">
            <h1 class="text-h5 text-grey-darken-4 font-weight-medium text-center mb-2">
              Terms & Agreements
            </h1>
            <p class="text-body-2 text-grey-darken-1 text-center mb-6">
              Review and accept our terms
            </p>

            <v-form ref="step3Form" v-model="step3Valid">
              <!-- Terms of Service Section -->
              <div class="terms-section mb-4">
                <h3 class="text-subtitle-1 font-weight-medium mb-2">Terms of Service</h3>
                <div class="terms-content">
                  <h4 class="text-body-1 font-weight-medium mb-2">1. Acceptance of Terms</h4>
                  <p class="text-body-2 mb-3">
                    By accessing and using the CAAS (Compliance Automation AI Security) platform, you accept and agree 
                    to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, 
                    please do not use this service.
                  </p>

                  <h4 class="text-body-1 font-weight-medium mb-2">2. Healthcare Compliance</h4>
                  <p class="text-body-2 mb-3">
                    You acknowledge that CAAS is designed for healthcare organizations and must be used in compliance 
                    with all applicable healthcare regulations, including but not limited to HIPAA, HITECH Act, and 
                    state privacy laws.
                  </p>

                  <h4 class="text-body-1 font-weight-medium mb-2">3. User Responsibilities</h4>
                  <p class="text-body-2 mb-3">
                    Users are responsible for maintaining the confidentiality of their account credentials, implementing 
                    appropriate access controls, and ensuring all users within their organization comply with these terms.
                  </p>

                  <h4 class="text-body-1 font-weight-medium mb-2">4. Data Security</h4>
                  <p class="text-body-2 mb-3">
                    We implement industry-standard security measures including 256-bit encryption, secure data centers, 
                    and regular security audits. However, no method of transmission over the Internet is 100% secure.
                  </p>

                  <h4 class="text-body-1 font-weight-medium mb-2">5. Limitation of Liability</h4>
                  <p class="text-body-2 mb-3">
                    CAAS shall not be liable for any indirect, incidental, special, consequential, or punitive damages 
                    resulting from your use of or inability to use the service.
                  </p>
                </div>
              </div>

              <!-- Privacy Policy Section -->
              <div class="terms-section mb-4">
                <h3 class="text-subtitle-1 font-weight-medium mb-2">Privacy Policy</h3>
                <div class="terms-content">
                  <h4 class="text-body-1 font-weight-medium mb-2">1. Information We Collect</h4>
                  <p class="text-body-2 mb-3">
                    We collect information necessary to provide vendor risk management services, including organization 
                    details, vendor information, assessment data, and user account information.
                  </p>

                  <h4 class="text-body-1 font-weight-medium mb-2">2. Use of Information</h4>
                  <p class="text-body-2 mb-3">
                    Your information is used solely for providing and improving our services, ensuring compliance, 
                    and communicating important updates. We do not sell or rent your information to third parties.
                  </p>

                  <h4 class="text-body-1 font-weight-medium mb-2">3. Protected Health Information (PHI)</h4>
                  <p class="text-body-2 mb-3">
                    Any PHI processed through our platform is handled in strict accordance with HIPAA requirements. 
                    Access is limited to authorized personnel on a need-to-know basis.
                  </p>

                  <h4 class="text-body-1 font-weight-medium mb-2">4. Data Retention</h4>
                  <p class="text-body-2 mb-3">
                    We retain your data for as long as your account is active or as needed to provide services. 
                    Data is retained for 7 years after account closure for compliance purposes.
                  </p>
                </div>
              </div>

              <!-- HIPAA Business Associate Agreement Section -->
              <div class="terms-section mb-6">
                <h3 class="text-subtitle-1 font-weight-medium mb-2">HIPAA Business Associate Agreement (BAA)</h3>
                <div class="terms-content">
                  <h4 class="text-body-1 font-weight-medium mb-2">1. Definitions</h4>
                  <p class="text-body-2 mb-3">
                    "Business Associate" refers to CAAS Platform. "Covered Entity" refers to your healthcare organization. 
                    "Protected Health Information (PHI)" has the same meaning as in the HIPAA Privacy Rule.
                  </p>

                  <h4 class="text-body-1 font-weight-medium mb-2">2. Obligations of Business Associate</h4>
                  <p class="text-body-2 mb-3">
                    Business Associate agrees to:
                  </p>
                  <ul class="text-body-2 mb-3 ml-6">
                    <li>Not use or disclose PHI except as permitted by this Agreement or required by law</li>
                    <li>Use appropriate safeguards to prevent unauthorized use or disclosure of PHI</li>
                    <li>Report any security incident or breach within 24 hours of discovery</li>
                    <li>Ensure any subcontractors agree to the same restrictions</li>
                    <li>Make PHI available for access, amendment, and accounting as required by HIPAA</li>
                  </ul>

                  <h4 class="text-body-1 font-weight-medium mb-2">3. Permitted Uses and Disclosures</h4>
                  <p class="text-body-2 mb-3">
                    Business Associate may use or disclose PHI only for proper management and administration 
                    or to carry out legal responsibilities of the Business Associate.
                  </p>

                  <h4 class="text-body-1 font-weight-medium mb-2">4. Term and Termination</h4>
                  <p class="text-body-2 mb-3">
                    This Agreement shall remain in effect until terminated. Upon termination, Business Associate 
                    shall return or destroy all PHI, if feasible.
                  </p>
                </div>
              </div>

              <!-- Acceptance Checkboxes -->
              <v-checkbox
                v-model="formData.acceptTerms"
                :rules="acceptanceRules"
                hide-details="auto"
                class="mb-3"
              >
                <template v-slot:label>
                  <span class="text-body-2">
                    I have read and agree to the 
                    <a href="#" @click.prevent="openTermsDialog" class="text-primary">Terms of Service</a> 
                    and 
                    <a href="#" @click.prevent="openPrivacyDialog" class="text-primary">Privacy Policy</a>
                    <span class="text-error">*</span>
                  </span>
                </template>
              </v-checkbox>

              <v-checkbox
                v-model="formData.acceptBAA"
                :rules="acceptanceRules"
                hide-details="auto"
                class="mb-3"
              >
                <template v-slot:label>
                  <span class="text-body-2">
                    I am authorized to accept the 
                    <a href="#" @click.prevent="openBAADialog" class="text-primary">HIPAA Business Associate Agreement</a> 
                    on behalf of my organization
                    <span class="text-error">*</span>
                  </span>
                </template>
              </v-checkbox>

              <!-- Marketing Communications (Optional) -->
              <v-checkbox
                v-model="formData.acceptMarketing"
                hide-details="auto"
                class="mb-4"
              >
                <template v-slot:label>
                  <span class="text-body-2">
                    I would like to receive updates about new features and compliance best practices
                  </span>
                </template>
              </v-checkbox>

              <!-- Agreement Summary -->
              <v-alert
                type="info"
                variant="tonal"
                class="mb-4"
              >
                <div class="text-body-2">
                  <strong>By clicking "Complete Registration":</strong>
                  <ul class="mt-2 ml-4">
                    <li>You confirm all information provided is accurate</li>
                    <li>You accept our terms and enter into a Business Associate Agreement</li>
                    <li>You acknowledge that this creates a legally binding contract</li>
                  </ul>
                </div>
              </v-alert>
            </v-form>
          </div>
        </transition>

        <!-- NAVIGATION BUTTONS: Stay in same position -->
        <div class="navigation-buttons d-flex align-center justify-space-between mt-8 mb-6">
          <v-btn
            variant="outlined"
            size="large"
            :disabled="currentStep === 1"
            @click="previousStep"
            class="text-grey-darken-2 nav-btn"
          >
            Previous
          </v-btn>
          
          <span class="text-grey-darken-1 text-body-2 step-counter">
            Step {{ currentStep }} of 3
          </span>
          
          <v-btn
            color="primary"
            size="large"
            @click="nextStep"
            :loading="isLoading"
            class="nav-btn"
          >
            {{ currentStep === 3 ? 'Complete' : 'Next' }}
          </v-btn>
        </div>

        <!-- Sign In Link -->
        <p class="text-center text-body-2">
          Already have an account?
          <router-link to="/auth/login" class="text-primary text-decoration-none">
            Sign in here
          </router-link>
        </p>

        <!-- Security Footer -->
        <v-divider class="mt-6 mb-6" />
        <div class="security-footer">
          <div class="d-flex justify-center ga-6 mb-3 security-badges">
            <div class="d-flex align-center text-success">
              <v-icon size="small" class="mr-2">mdi-shield-check</v-icon>
              <span class="text-body-2">HIPAA Compliant</span>
            </div>
            <div class="d-flex align-center text-success">
              <v-icon size="small" class="mr-2">mdi-lock</v-icon>
              <span class="text-body-2">256-bit Encryption</span>
            </div>
          </div>
          <p class="text-center text-grey-darken-1 text-caption session-timeout">
            Session expires after 15 minutes of inactivity
          </p>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/authService'

// Router instance
const router = useRouter()

// Current step tracking
const currentStep = ref(1)  // Which step we're on
const transitionName = ref('slide-left')  // Animation direction

// Form refs and validation states
const step1Form = ref()  // Step 1 form ref
const step2Form = ref()  // Step 2 form ref
const step3Form = ref()  // Step 3 form ref
const step1Valid = ref(false)  // Step 1 validity
const step2Valid = ref(false)  // Step 2 validity
const step3Valid = ref(false)  // Step 3 validity
const isLoading = ref(false)  // Loading state

// Password visibility toggles
const showPassword = ref(false)  // Toggle password visibility
const showConfirmPassword = ref(false)  // Toggle confirm visibility

// All form data in one place
const formData = reactive({
  // Step 1 - Organization Info
  orgName: '',
  orgType: '',
  city: '',
  state: '',
  adminEmail: '',
  phoneNumber: '',
  // Step 2 - Admin Account
  firstName: '',
  lastName: '',
  jobTitle: '',
  password: '',
  confirmPassword: '',
  mobilePhone: '',
  securityQuestion: '',
  securityAnswer: '',
  // Step 3 - Terms
  acceptTerms: false,
  acceptBAA: false,
  acceptMarketing: false
})

// Password strength tracking
const passwordStrength = ref({
  score: 0,
  label: 'Very Weak',
  color: 'error'
})

// Organization types dropdown options
const organizationTypes = [
  { title: 'Hospital', value: 'hospital' },
  { title: 'Clinic', value: 'clinic' },
  { title: 'Pharmacy', value: 'pharmacy' },
  { title: 'Insurance Provider', value: 'insurance' },
  { title: 'Medical Practice', value: 'practice' },
  { title: 'Healthcare Network', value: 'network' },
  { title: 'Other Healthcare Provider', value: 'other' }
]

// Security questions array
const securityQuestions = [
  'What was the name of your first pet?',
  'In what city were you born?',
  'What is your mother\'s maiden name?',
  'What was the name of your elementary school?',
  'What was your childhood nickname?',
  'What is the name of the street you grew up on?'
]

// ===== VALIDATION RULES =====

// Organization name validation
const orgNameRules = [
  (v: any) => !!v || 'Organization name is required',
  (v: any) => (v && v.length >= 2) || 'Must be at least 2 characters',
  (v: any) => (v && v.length <= 100) || 'Must be less than 100 characters'
]

// Organization type validation
const orgTypeRules = [
  (v: any) => !!v || 'Please select your organization type'
]

// Email validation
const emailRules = [
  (v: any) => !!v || 'Email is required',
  (v: any) => !v || /.+@.+\..+/.test(v) || 'Invalid email format',
  (v: any) => !v || (!v.includes('gmail') && !v.includes('yahoo') && !v.includes('hotmail')) || 'Please use organization email'
]

// Name validation (first/last)
const nameRules = [
  (v: any) => !!v || 'This field is required',
  (v: any) => (v && v.length >= 2) || 'Must be at least 2 characters',
  (v: any) => (v && /^[a-zA-Z\s'-]+$/.test(v)) || 'Only letters, spaces, hyphens, and apostrophes allowed'
]

// Job title validation
const jobTitleRules = [
  (v: any) => !!v || 'Job title is required',
  (v: any) => (v && v.length >= 2) || 'Must be at least 2 characters',
  (v: any) => (v && v.length <= 100) || 'Must be less than 100 characters'
]

// HIPAA-compliant password rules
const passwordRules = [
  (v: any) => !!v || 'Password is required',
  (v: any) => (v && v.length >= 12) || 'Password must be at least 12 characters (HIPAA requirement)',
  (v: any) => (v && /[A-Z]/.test(v)) || 'Must contain at least one uppercase letter',
  (v: any) => (v && /[a-z]/.test(v)) || 'Must contain at least one lowercase letter',
  (v: any) => (v && /[0-9]/.test(v)) || 'Must contain at least one number',
  (v: any) => (v && /[!@#$%^&*(),.?":{}|<>]/.test(v)) || 'Must contain at least one special character'
]

// Confirm password validation
const confirmPasswordRules = [
  (v: any) => !!v || 'Please confirm your password',
  (v: any) => v === formData.password || 'Passwords do not match'
]

// Phone validation for 2FA
const phoneRules = [
  (v: any) => !!v || 'Mobile phone is required for 2FA',
  (v: any) => !v || /^\+?[1-9]\d{1,14}$/.test(v.replace(/\s/g, '')) || 'Invalid phone number format'
]

// Security question validation
const securityQuestionRules = [
  (v: any) => !!v || 'Please select a security question'
]

// Security answer validation
const securityAnswerRules = [
  (v: any) => !!v || 'Security answer is required',
  (v: any) => (v && v.length >= 3) || 'Answer must be at least 3 characters'
]

// Acceptance rules for terms checkboxes
const acceptanceRules = [
  (v: any) => !!v || 'You must accept this agreement to continue'
]

// Password requirements checklist
const passwordRequirements = computed(() => {
  const pwd = formData.password || ''
  return [
    { text: 'At least 12 characters', met: pwd.length >= 12 },
    { text: 'One uppercase letter (A-Z)', met: /[A-Z]/.test(pwd) },
    { text: 'One lowercase letter (a-z)', met: /[a-z]/.test(pwd) },
    { text: 'One number (0-9)', met: /[0-9]/.test(pwd) },
    { text: 'One special character (!@#$%^&*)', met: /[!@#$%^&*(),.?":{}|<>]/.test(pwd) }
  ]
})

// Check password strength
function checkPasswordStrength(password: string) {
  if (!password) {
    passwordStrength.value = { score: 0, label: 'Very Weak', color: 'error' }
    return
  }

  let score = 0
  
  // Length scoring
  if (password.length >= 12) score += 20
  if (password.length >= 16) score += 10
  if (password.length >= 20) score += 10
  
  // Character variety
  if (/[a-z]/.test(password)) score += 15
  if (/[A-Z]/.test(password)) score += 15
  if (/[0-9]/.test(password)) score += 15
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 15
  
  // Bonus for good mix
  const types = [/[a-z]/, /[A-Z]/, /[0-9]/, /[!@#$%^&*(),.?":{}|<>]/]
  const typeCount = types.filter(regex => regex.test(password)).length
  if (typeCount >= 3) score += 10
  if (typeCount === 4) score += 10

  // Set strength level
  if (score < 30) {
    passwordStrength.value = { score: 25, label: 'Weak', color: 'error' }
  } else if (score < 50) {
    passwordStrength.value = { score: 50, label: 'Fair', color: 'warning' }
  } else if (score < 70) {
    passwordStrength.value = { score: 75, label: 'Good', color: 'success' }
  } else {
    passwordStrength.value = { score: 100, label: 'Strong', color: 'success' }
  }
}

// Navigate to next step with validation
async function nextStep() {
  // Validate current step
  if (currentStep.value === 1) {
    const { valid } = await step1Form.value?.validate()
    if (!valid) return
  } else if (currentStep.value === 2) {
    const { valid } = await step2Form.value?.validate()
    if (!valid) return
  } else if (currentStep.value === 3) {
    const { valid } = await step3Form.value?.validate()
    if (!valid) return
  }

  // Animate forward
  transitionName.value = 'slide-left'
  
  // Move to next step or submit
  if (currentStep.value < 3) {
    currentStep.value++
  } else {
    // Submit final registration
    submitRegistration()
  }
}

// Navigate to previous step
function previousStep() {
  transitionName.value = 'slide-right'  // Animate backward
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// Animation lifecycle hooks
function beforeLeave(el: any) {
  const parent = el.parentNode
  const rect = el.getBoundingClientRect()
  const parentRect = parent.getBoundingClientRect()
  el.style.position = 'absolute'
  el.style.top = `${rect.top - parentRect.top}px`
  el.style.left = `${rect.left - parentRect.left}px`
  el.style.width = `${rect.width}px`
}

function enter(el: any) {
  el.style.position = ''
  el.style.top = ''
  el.style.left = ''
  el.style.width = ''
}

function afterEnter(el: any) {
  el.style.position = ''
}

// Submit all registration data
async function submitRegistration() {
  isLoading.value = true
  try {
    const response = await authService.register(formData)
    console.log('Registration successful:', response)
    alert('Registration successful! Please check your email to verify your account.')
    setTimeout(() => {
      router.push('/auth/login')
    }, 2000)
  } catch (error: any) {
    console.error('Registration error:', error)
    alert(error.message || 'Registration failed. Please try again.')
  } finally {
    isLoading.value = false
  }
}

// Dialog methods for full document views
function openTermsDialog() {
  // TODO: Open full terms in a dialog
  console.log('Opening terms dialog')
}

function openPrivacyDialog() {
  // TODO: Open full privacy policy in a dialog
  console.log('Opening privacy dialog')
}

function openBAADialog() {
  // TODO: Open full BAA in a dialog
  console.log('Opening BAA dialog')
}
</script>

<style scoped>
/* Blue gradient background */
.auth-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #034c81 0%, #2ca3fa 50%, #B2EBF2 100%);
}

/* Card styling */
.auth-card {
  border-radius: 16px;
  width: 800px !important;
}

/* Logo container */
.logo-container {
  display: inline-flex;
  align-items: center;
  background-color: #034c81;
  padding: 12px 24px;
  border-radius: 8px;
}

.logo-text {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

/* Progress steps */
.step-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #757575;
  transition: all 0.3s ease;
}

.step-circle.step-active {
  background-color: #034c81;
  color: white;
}

.step-circle.step-complete {
  background-color: #4caf50;
  color: white;
}

.step-line {
  height: 2px;
  width: 48px;
  background-color: #e0e0e0;
}

.step-line.step-line-active {
  background-color: #4caf50;
}

/* Field styling */
.field-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #424242;
  margin-bottom: 6px;
}

/* Gray field backgrounds */
.gray-field :deep(.v-field) {
  background-color: #f5f5f5;
  border-radius: 8px;
}

.gray-field :deep(.v-field__outline) {
  display: none;
}

.gray-field :deep(.v-field--variant-outlined) {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.gray-field :deep(.v-field--focused) {
  border-color: #1976d2;
  box-shadow: 0 0 0 1px #1976d2;
}

.gray-field :deep(.v-field__input) {
  min-height: 44px;
  padding: 0 14px;
  font-size: 15px;
}

/* Password requirements */
.password-requirements {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 8px;
}

.requirement-item {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.requirement-item:last-child {
  margin-bottom: 0;
}

/* Step content container */
.step-content {
  min-height: 400px;
  position: relative;
}

/* Navigation buttons */
.navigation-buttons {
  min-height: 48px;
}

/* Security footer */
.security-footer {
  padding-top: 16px;
}

/* Terms and agreements styling */
.terms-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
}

.terms-content {
  max-height: 200px;
  overflow-y: auto;
  padding-right: 8px;
}

/* Custom scrollbar for terms */
.terms-content::-webkit-scrollbar {
  width: 6px;
}

.terms-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.terms-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.terms-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Slide animations */
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-left-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-right-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* MOBILE RESPONSIVE FIXES */
@media (max-width: 800px) {
  /* Card takes full width on mobile */
  .auth-card {
    width: 100% !important;
    margin: 0;
    border-radius: 0;
    min-height: 100vh;
  }
  
  /* Adjust padding on mobile */
  .auth-container {
    padding: 0 !important;
  }
  
  /* Reduce card padding on mobile */
  .auth-card :deep(.v-card-text) {
    padding: 24px 16px !important;
  }
  
  /* Smaller logo on mobile */
  .logo-container {
    padding: 10px 20px;
  }
  
  .logo-text {
    font-size: 16px;
  }
  
  /* Smaller step indicators */
  .step-circle {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
  
  .step-line {
    width: 24px;
  }
  
  /* Smaller headings */
  .text-h5 {
    font-size: 1.25rem !important;
  }
  
  /* Ensure form fields work on mobile */
  .gray-field :deep(.v-field__input) {
    font-size: 16px !important; /* Prevents zoom on iOS */
  }
  
  /* Smaller field labels */
  .field-label {
    font-size: 13px;
  }
  
  /* Password requirements box */
  .password-requirements {
    padding: 8px;
  }
  
  .requirement-item {
    font-size: 12px;
  }
  
  /* Security footer adjustments */
  .security-footer .text-body-2 {
    font-size: 12px !important;
  }
}

/* Fix for step content minimum height on mobile */
@media (max-width: 600px) {
  .step-content {
    min-height: auto;
    padding-bottom: 20px;
  }
  
  /* Mobile adjustments for terms */
  .terms-content {
    max-height: 150px;
  }
  
  .terms-section {
    padding: 12px;
  }
}

/* Stack navigation buttons vertically on very small screens */
@media (max-width: 480px) {
  .navigation-buttons {
    flex-direction: column;
    gap: 12px;
  }
  
  .navigation-buttons .nav-btn {
    width: 100%;
  }
  
  .navigation-buttons .step-counter {
    order: -1; /* Move step counter to top */
    width: 100%;
    text-align: center;
  }
  
  /* Mobile-specific security footer */
  .security-badges {
    flex-direction: column !important;
    gap: 8px !important;
  }
  
  .session-timeout {
    font-size: 11px !important;
  }
}
</style>