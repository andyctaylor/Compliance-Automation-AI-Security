/**
 * Central API Export
 * 
 * TEACHING MOMENT: This creates a single import point for all services
 * Usage: import { api } from '@/api';
 * Then: api.auth.login(credentials)
 */

import { authService } from './services/auth.service';
import { vendorService } from './services/vendors.service';
import { documentService } from './services/documents.service';
import { assessmentService } from './services/assessments.service';
import { organizationService } from './services/organizations.service';

export const api = {
  auth: authService,
  vendors: vendorService,
  documents: documentService,
  assessments: assessmentService,
  organizations: organizationService,
};

// Re-export types
export * from '@/types';