/**
 * Document Management Service
 * Handles all document-related API calls
 */

import { apiClient } from '../axios.config';
import type { Document, DocumentCategory, DocumentTag, PaginatedResponse } from '@/types';

class DocumentService {
  /**
   * Get all documents (paginated)
   */
  async getDocuments(params?: {
    page?: number;
    page_size?: number;
    vendor?: number;
    status?: string;
    document_type?: string;
    category?: number;
    search?: string;
  }): Promise<PaginatedResponse<Document>> {
    const response = await apiClient.get<PaginatedResponse<Document>>('/documents/', { params });
    return response.data;
  }

  /**
   * Get single document
   */
  async getDocument(id: number): Promise<Document> {
    const response = await apiClient.get<Document>(`/documents/${id}/`);
    return response.data;
  }

  /**
   * Upload new document
   */
  async uploadDocument(data: FormData): Promise<Document> {
    const response = await apiClient.post<Document>('/documents/', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Update document
   */
  async updateDocument(id: number, data: Partial<Document>): Promise<Document> {
    const response = await apiClient.patch<Document>(`/documents/${id}/`, data);
    return response.data;
  }

  /**
   * Delete document
   */
  async deleteDocument(id: number): Promise<void> {
    await apiClient.delete(`/documents/${id}/`);
  }

  /**
   * Get documents expiring soon
   */
  async getExpiringDocuments(days: number = 30): Promise<Document[]> {
    const response = await apiClient.get<Document[]>(`/documents/expiring_soon/`, {
      params: { days }
    });
    return response.data;
  }

  /**
   * Get documents by type
   */
  async getDocumentsByType(documentType: string): Promise<Document[]> {
    const response = await apiClient.get<Document[]>(`/documents/by_type/`, {
      params: { document_type: documentType }
    });
    return response.data;
  }

  /**
   * Get all categories
   */
  async getCategories(): Promise<DocumentCategory[]> {
    const response = await apiClient.get<DocumentCategory[]>('/document-categories/');
    return response.data;
  }

  /**
   * Get all tags
   */
  async getTags(): Promise<DocumentTag[]> {
    const response = await apiClient.get<DocumentTag[]>('/document-tags/');
    return response.data;
  }
}

export const documentService = new DocumentService();