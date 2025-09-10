/**
 * Assessment Management Service
 * Handles templates, questions, assessments, and responses
 */

import { apiClient } from '../axios.config';
import type { 
  Assessment, 
  AssessmentTemplate, 
  AssessmentQuestion, 
  PaginatedResponse 
} from '@/types';

interface AssessmentResponse {
  id: number;
  assessment: number;
  question: number;
  answer_text?: string;
  answer_boolean?: boolean;
  answer_number?: number;
  answer_choice?: string;
  answer_file?: string;
  notes?: string;
}

interface CreateAssessmentData {
  template: number;
  vendor: number;
  assigned_to?: number;
  expires_at: string;
  send_email?: boolean;
}

class AssessmentService {
  /**
   * Get all assessment templates
   */
  async getTemplates(params?: {
    is_active?: boolean;
    search?: string;
  }): Promise<AssessmentTemplate[]> {
    const response = await apiClient.get<AssessmentTemplate[]>('/assessment-templates/', { params });
    return response.data;
  }

  /**
   * Get single template with questions
   */
  async getTemplate(id: number): Promise<AssessmentTemplate> {
    const response = await apiClient.get<AssessmentTemplate>(`/assessment-templates/${id}/`);
    return response.data;
  }

  /**
   * Create new template
   */
  async createTemplate(data: Omit<AssessmentTemplate, 'id' | 'created_at' | 'updated_at' | 'question_count'>): Promise<AssessmentTemplate> {
    const response = await apiClient.post<AssessmentTemplate>('/assessment-templates/', data);
    return response.data;
  }

  /**
   * Update template
   */
  async updateTemplate(id: number, data: Partial<AssessmentTemplate>): Promise<AssessmentTemplate> {
    const response = await apiClient.patch<AssessmentTemplate>(`/assessment-templates/${id}/`, data);
    return response.data;
  }

  /**
   * Delete template
   */
  async deleteTemplate(id: number): Promise<void> {
    await apiClient.delete(`/assessment-templates/${id}/`);
  }

  /**
   * Get questions for a template
   */
  async getQuestions(templateId: number): Promise<AssessmentQuestion[]> {
    const response = await apiClient.get<AssessmentQuestion[]>(`/assessment-templates/${templateId}/questions/`);
    return response.data;
  }

  /**
   * Create question
   */
  async createQuestion(data: Omit<AssessmentQuestion, 'id' | 'created_at' | 'updated_at'>): Promise<AssessmentQuestion> {
    const response = await apiClient.post<AssessmentQuestion>('/assessment-questions/', data);
    return response.data;
  }

  /**
   * Update question
   */
  async updateQuestion(id: number, data: Partial<AssessmentQuestion>): Promise<AssessmentQuestion> {
    const response = await apiClient.patch<AssessmentQuestion>(`/assessment-questions/${id}/`, data);
    return response.data;
  }

  /**
   * Delete question
   */
  async deleteQuestion(id: number): Promise<void> {
    await apiClient.delete(`/assessment-questions/${id}/`);
  }

  /**
   * Reorder questions
   */
  async reorderQuestions(templateId: number, questionOrder: number[]): Promise<void> {
    await apiClient.post(`/assessment-templates/${templateId}/reorder_questions/`, {
      question_order: questionOrder
    });
  }

  /**
   * Get all assessments (paginated)
   */
  async getAssessments(params?: {
    page?: number;
    page_size?: number;
    vendor?: number;
    status?: string;
    template?: number;
    search?: string;
    ordering?: string;
  }): Promise<PaginatedResponse<Assessment>> {
    const response = await apiClient.get<PaginatedResponse<Assessment>>('/assessments/', { params });
    return response.data;
  }

  /**
   * Get single assessment with responses
   */
  async getAssessment(id: number): Promise<Assessment> {
    const response = await apiClient.get<Assessment>(`/assessments/${id}/`);
    return response.data;
  }

  /**
   * Create new assessment
   */
  async createAssessment(data: CreateAssessmentData): Promise<Assessment> {
    const response = await apiClient.post<Assessment>('/assessments/', data);
    return response.data;
  }

  /**
   * Delete assessment
   */
  async deleteAssessment(id: number): Promise<void> {
    await apiClient.delete(`/assessments/${id}/`);
  }

  /**
   * Get assessment responses
   */
  async getResponses(assessmentId: number): Promise<AssessmentResponse[]> {
    const response = await apiClient.get<AssessmentResponse[]>(`/assessments/${assessmentId}/responses/`);
    return response.data;
  }

  /**
   * Submit single response
   */
  async submitResponse(assessmentId: number, questionId: number, answer: any): Promise<AssessmentResponse> {
    const response = await apiClient.post<AssessmentResponse>(`/assessments/${assessmentId}/submit_response/`, {
      question_id: questionId,
      answer
    });
    return response.data;
  }

  /**
   * Submit all responses
   */
  async submitAllResponses(assessmentId: number, responses: Record<number, any>): Promise<Assessment> {
    const response = await apiClient.post<Assessment>(`/assessments/${assessmentId}/submit_all/`, {
      responses
    });
    return response.data;
  }

  /**
   * Complete assessment
   */
  async completeAssessment(assessmentId: number): Promise<Assessment> {
    const response = await apiClient.post<Assessment>(`/assessments/${assessmentId}/complete/`);
    return response.data;
  }

  /**
   * Send reminder email
   */
  async sendReminder(assessmentId: number): Promise<void> {
    await apiClient.post(`/assessments/${assessmentId}/send_reminder/`);
  }

  /**
   * Get assessment statistics
   */
  async getStatistics(): Promise<{
    total_assessments: number;
    completed_rate: number;
    average_score: number;
    by_status: Record<string, number>;
    by_risk_level: Record<string, number>;
  }> {
    const response = await apiClient.get('/assessments/statistics/');
    return response.data;
  }
}

export const assessmentService = new AssessmentService();