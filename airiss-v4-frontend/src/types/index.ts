/**
 * AIRISS v4.0 Comprehensive Type Definitions
 * Centralized type definitions for the entire application
 */

// ============================================================================
// API Response Types
// ============================================================================

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: string;
}

export interface PaginationInfo {
  page: number;
  per_page: number;
  total: number;
  pages: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationInfo;
}

// ============================================================================
// User and Authentication Types
// ============================================================================

export interface User {
  id: number;
  email: string;
  name: string;
  is_approved: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at?: string;
  last_login?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
  user_info: User;
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
  confirm_password?: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface UserApprovalRequest {
  user_id: number;
  approve: boolean;
  reason?: string;
}

// ============================================================================
// File and Upload Types
// ============================================================================

export interface FileInfo {
  id: string;
  filename: string;
  original_filename?: string;
  file_size: number;
  total_records: number;
  upload_time: string;
  user_id: string;
  session_id?: string;
  status: 'processing' | 'ready' | 'error';
  error_message?: string;
}

export interface FileUploadResponse {
  file_id: string;
  filename: string;
  total_records: number;
  columns: string[];
  uid_columns?: string[];
  opinion_columns?: string[];
  quantitative_columns?: string[];
  file_size?: number;
  upload_time?: string;
  column_info?: {
    detected_uid_columns: string[];
    detected_opinion_columns: string[];
    detected_quantitative_columns: string[];
    all_columns: string[];
  };
}

export interface FileValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  column_analysis: {
    total_columns: number;
    uid_columns: string[];
    opinion_columns: string[];
    quantitative_columns: string[];
    other_columns: string[];
  };
}

// ============================================================================
// Analysis Types
// ============================================================================

export interface AnalysisRequest {
  file_id: string;
  sample_size: number;
  analysis_mode: 'text' | 'quantitative' | 'hybrid';
  enable_ai_feedback?: boolean;
  openai_api_key?: string;
  openai_model?: string;
  max_tokens?: number;
  custom_prompt?: string;
  analysis_options?: {
    include_sentiment: boolean;
    include_themes: boolean;
    include_recommendations: boolean;
  };
}

export interface AnalysisResponse {
  job_id: string;
  message: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  estimated_duration?: number;
  queue_position?: number;
}

export interface AnalysisStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  processed: number;
  total: number;
  current_uid?: string;
  average_score?: number;
  processing_time?: string;
  error?: string;
  created_at: string;
  updated_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface AnalysisJob {
  job_id: string;
  file_id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  sample_size: number;
  analysis_mode: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  processing_time?: string;
  user_id: string;
  error_message?: string;
}

// ============================================================================
// Analysis Results Types
// ============================================================================

export interface DimensionScore {
  dimension: string;
  score: number;
  weight?: number;
  explanation?: string;
}

export interface EmployeeAnalysisResult {
  uid: string;
  overall_score: number;
  grade: string;
  dimension_scores: Record<string, number>;
  detailed_scores?: DimensionScore[];
  ai_feedback?: string;
  sentiment_analysis?: {
    overall_sentiment: 'positive' | 'neutral' | 'negative';
    sentiment_score: number;
    key_themes: string[];
  };
  recommendations?: string[];
  raw_data?: {
    original_text?: string;
    processed_text?: string;
    metadata?: Record<string, any>;
  };
}

export interface AnalysisSummary {
  total_analyzed: number;
  average_score: number;
  high_performers: number;
  low_performers: number;
  grade_distribution: Record<string, number>;
  score_distribution: {
    ranges: string[];
    counts: number[];
  };
  dimension_averages: Record<string, number>;
  completion_rate: number;
}

export interface AnalysisResult {
  job_id: string;
  file_id: string;
  filename: string;
  total_analyzed: number;
  average_score: number;
  processing_time: string;
  results: EmployeeAnalysisResult[];
  analysis_summary: AnalysisSummary;
  metadata: {
    analysis_mode: string;
    sample_size: number;
    ai_enabled: boolean;
    created_at: string;
    version: string;
  };
}

// ============================================================================
// WebSocket Types
// ============================================================================

export interface WebSocketMessage {
  type: string;
  data?: any;
  error?: string;
  timestamp?: string;
  job_id?: string;
  user_id?: string;
}

export interface AnalysisProgress {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  processed: number;
  total: number;
  current_uid?: string;
  message?: string;
  error?: string;
  timestamp?: string;
  average_score?: number;
  estimated_time_remaining?: number;
}

export interface WebSocketConnectionInfo {
  client_id: string;
  connected_at: string;
  subscribed_channels: string[];
  user_id?: string;
}

// ============================================================================
// Dashboard Types
// ============================================================================

// 첫 번째 DashboardStats 정의 제거 (아래에 다시 정의됨)

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  components: {
    database: 'healthy' | 'degraded' | 'down';
    websocket: 'healthy' | 'degraded' | 'down';
    file_storage: 'healthy' | 'degraded' | 'down';
    ai_service: 'healthy' | 'degraded' | 'down';
  };
  response_time: number;
  uptime: number;
  version: string;
}

export interface RecentActivity {
  id: string;
  type: 'file_upload' | 'analysis_start' | 'analysis_complete' | 'user_login';
  description: string;
  user_name?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

// ============================================================================
// Legacy Types (for backward compatibility)
// ============================================================================

// 직원 분석 결과 (기존 타입)
export interface EmployeeResult {
  UID: string;
  AIRISS_v4_종합점수: number;
  OK등급: string;
  등급설명: string;
  백분위: string;
  분석신뢰도: number;
  텍스트_종합점수: number;
  정량_종합점수: number;
  AI_장점?: string;
  AI_개선점?: string;
  AI_종합피드백?: string;
  [key: string]: any; // 8대 영역 점수 등 동적 필드
}

// 분석 시작 응답 (기존 타입)
export interface AnalysisStartResponse {
  job_id: string;
  status: string;
  message: string;
}

// 분석 상태 응답 (기존 타입)
export interface AnalysisStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  processed: number;
  total: number;
  error?: string;
}

export interface RecentAnalysis {
  job_id: string;
  filename: string;
  processed: number;
  average_score: number;
  created_at: string;
}

// Dashboard Stats interface
export interface DashboardStats {
  total_analyses: number;
  total_employees: number;
  average_score: number;
  recent_analyses: RecentAnalysis[];
}

// ============================================================================
// Export Default Types
// ============================================================================

// Remove default export to fix TypeScript errors
// Types are already exported individually above