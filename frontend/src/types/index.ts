/**
 * TypeScript Interfaces for CAAS Platform
 * 
 * These match our Django models to ensure type safety
 */

// Base interfaces
export interface BaseModel {
  id: number;
  created_at?: string;
  updated_at?: string;
}

// User & Auth
export interface User extends BaseModel {
  email: string;
  first_name: string;
  last_name: string;
  organization: number;
  is_active: boolean;
  is_staff: boolean;
  role: 'admin' | 'healthcare_org' | 'vendor' | 'auditor';
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;  // Optional flag for extended session duration
}

export interface TokenResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface LoginResponse {
  user?: User;
  access?: string;
  refresh?: string;
  requires2FA?: boolean;
  twoFactorToken?: string;
}

export interface TwoFactorResponse {
  user: User;
  access: string;
  refresh: string;
}

export interface ApiError {
  detail?: string;
  [field: string]: string | string[] | undefined;
}

// Organizations
export interface Organization extends BaseModel {
  name: string;
  domain: string;
  is_active: boolean;
  settings: Record<string, any>;
}

// Vendors
export interface Vendor extends BaseModel {
  organization: number;
  name: string;
  email: string;
  phone?: string;
  website?: string;
  address?: string;
  primary_contact?: string;
  risk_score: number;
  is_active: boolean;
  vendor_type: 'medical_device' | 'pharmaceutical' | 'it_service' | 'consulting' | 'other';
}

// Documents
export interface DocumentCategory extends BaseModel {
  name: string;
  description?: string;
  icon: string;
  color: string;
}

export interface DocumentTag extends BaseModel {
  name: string;
  color: string;
}

export interface Document extends BaseModel {
  vendor: number;
  vendor_name?: string;
  organization: number;
  name: string;
  document_type: 'baa' | 'insurance_coi' | 'license' | 'certification' | 'contract' | 'other';
  category?: DocumentCategory;
  tags?: DocumentTag[];
  file: string;
  file_url?: string;
  file_size: number;
  status: 'active' | 'expired' | 'pending_review' | 'rejected';
  document_date: string;
  expires_at?: string;
  is_expired: boolean;
  days_until_expiration?: number;
  version: number;
  is_latest: boolean;
  parent_document?: number;
  version_notes?: string;
}

// Assessments
export interface AssessmentTemplate extends BaseModel {
  organization: number;
  name: string;
  description?: string;
  risk_weights: Record<string, number>;
  is_active: boolean;
  question_count?: number;
}

export interface AssessmentQuestion extends BaseModel {
  template: number;
  text: string;
  question_type: 'yes_no' | 'multiple_choice' | 'scale' | 'text' | 'file_upload';
  category: string;
  risk_weight: number;
  order: number;
  is_required: boolean;
  help_text?: string;
  choices?: string[];
}

export interface Assessment extends BaseModel {
  template: number;
  template_name?: string;
  vendor: number;
  vendor_name?: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'expired';
  score?: number;
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
  assigned_by: number;
  assigned_to?: number;
  started_at?: string;
  completed_at?: string;
  expires_at: string;
  response_count?: number;
}

// API Response types
export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}