/**
 * Organization Management Service
 * Handles organization settings and management
 */

import { apiClient } from '../axios.config';
import type { Organization } from '@/types';

class OrganizationService {
  /**
   * Get current organization
   */
  async getCurrentOrganization(): Promise<Organization> {
    const response = await apiClient.get<Organization>('/organizations/current/');
    return response.data;
  }

  /**
   * Update organization settings
   */
  async updateSettings(settings: Record<string, any>): Promise<Organization> {
    const response = await apiClient.patch<Organization>('/organizations/current/', {
      settings
    });
    return response.data;
  }

  /**
   * Get organization statistics
   */
  async getStatistics(): Promise<{
    vendor_count: number;
    active_assessments: number;
    documents_count: number;
    compliance_rate: number;
    risk_overview: {
      low: number;
      medium: number;
      high: number;
      critical: number;
    };
  }> {
    const response = await apiClient.get('/organizations/statistics/');
    return response.data;
  }
}

export const organizationService = new OrganizationService();