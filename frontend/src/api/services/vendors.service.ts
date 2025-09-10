/**
 * Vendor Management Service
 * Handles all vendor-related API calls
 */

import { apiClient } from '../axios.config';
import type { Vendor, PaginatedResponse } from '@/types';

class VendorService {
  /**
   * Get all vendors (paginated)
   */
  async getVendors(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    is_active?: boolean;
    vendor_type?: string;
    ordering?: string;
  }): Promise<PaginatedResponse<Vendor>> {
    const response = await apiClient.get<PaginatedResponse<Vendor>>('/vendors/', { params });
    return response.data;
  }

  /**
   * Get single vendor
   */
  async getVendor(id: number): Promise<Vendor> {
    const response = await apiClient.get<Vendor>(`/vendors/${id}/`);
    return response.data;
  }

  /**
   * Create new vendor
   */
  async createVendor(data: Omit<Vendor, 'id' | 'risk_score' | 'created_at' | 'updated_at'>): Promise<Vendor> {
    const response = await apiClient.post<Vendor>('/vendors/', data);
    return response.data;
  }

  /**
   * Update vendor
   */
  async updateVendor(id: number, data: Partial<Vendor>): Promise<Vendor> {
    const response = await apiClient.patch<Vendor>(`/vendors/${id}/`, data);
    return response.data;
  }

  /**
   * Delete vendor
   */
  async deleteVendor(id: number): Promise<void> {
    await apiClient.delete(`/vendors/${id}/`);
  }

  /**
   * Get high risk vendors
   */
  async getHighRiskVendors(): Promise<Vendor[]> {
    const response = await apiClient.get<Vendor[]>('/vendors/high_risk/');
    return response.data;
  }

  /**
   * Get vendors by risk level
   */
  async getVendorsByRiskLevel(level: 'low' | 'medium' | 'high' | 'critical'): Promise<Vendor[]> {
    const response = await apiClient.get<Vendor[]>('/vendors/by_risk_level/', {
      params: { level }
    });
    return response.data;
  }

  /**
   * Recalculate vendor risk score
   */
  async recalculateRiskScore(id: number): Promise<{ risk_score: number }> {
    const response = await apiClient.post<{ risk_score: number }>(`/vendors/${id}/recalculate_risk/`);
    return response.data;
  }

  /**
   * Bulk update vendors
   */
  async bulkUpdateVendors(vendorIds: number[], updates: Partial<Vendor>): Promise<Vendor[]> {
    const response = await apiClient.post<Vendor[]>('/vendors/bulk_update/', {
      vendor_ids: vendorIds,
      updates
    });
    return response.data;
  }

  /**
   * Export vendors to CSV
   */
  async exportVendors(format: 'csv' | 'excel' = 'csv'): Promise<Blob> {
    const response = await apiClient.get('/vendors/export/', {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  }
}

export const vendorService = new VendorService();