import axios, { AxiosError, AxiosResponse } from 'axios';

/**
 * AIRISS v4.0 API Integration Service
 * Enhanced API service with improved error handling and type safety
 */

// Environment configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '30000');

// Type definitions
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
}

export interface AnalysisRequest {
  file_id: string;
  sample_size: number;
  analysis_mode: 'text' | 'quantitative' | 'hybrid';
  enable_ai_feedback?: boolean;
  openai_api_key?: string;
  openai_model?: string;
  max_tokens?: number;
}

export interface AnalysisResponse {
  job_id: string;
  message: string;
  status: string;
}

export interface AnalysisStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  processed: number;
  total: number;
  average_score?: number;
  processing_time?: string;
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult {
  job_id: string;
  total_analyzed: number;
  average_score: number;
  results: Array<{
    uid: string;
    overall_score: number;
    grade: string;
    dimension_scores: Record<string, number>;
    ai_feedback?: string;
  }>;
  processing_time: string;
  analysis_summary: {
    high_performers: number;
    low_performers: number;
    grade_distribution: Record<string, number>;
  };
}

export interface FileInfo {
  id: string;
  filename: string;
  upload_time: string;
  total_records: number;
  size: number;
  user_id: string;
  session_id: string;
}

export interface UserInfo {
  id: number;
  email: string;
  name: string;
  is_approved: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_info: UserInfo;
}

// Axios instance configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`✅ API Response: ${response.config.url} - ${response.status}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('❌ API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    
    // Enhanced error handling
    if (error.response) {
      const data: any = error.response.data;
      const errorMessage = data.detail || data.message || `HTTP ${error.response.status} Error`;
      
      // Handle specific status codes
      switch (error.response.status) {
        case 401:
          // Unauthorized - redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden
          error.message = '접근이 거부되었습니다. 권한을 확인해주세요.';
          break;
        case 404:
          error.message = '요청한 리소스를 찾을 수 없습니다.';
          break;
        case 500:
          error.message = '서버 내부 오류가 발생했습니다.';
          break;
        default:
          error.message = errorMessage;
      }
    } else if (error.request) {
      error.message = '서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.';
    }
    
    return Promise.reject(error);
  }
);

// API Service Class
class APIService {
  // Health check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }

  // File operations
  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    return response.data;
  }

  async getFiles(): Promise<FileInfo[]> {
    const response = await api.get('/api/files');
    return response.data.files || [];
  }

  async deleteFile(fileId: string): Promise<void> {
    await api.delete(`/api/files/${fileId}`);
  }

  // Analysis operations
  async startAnalysis(params: AnalysisRequest): Promise<AnalysisResponse> {
    const response = await api.post('/api/analysis', params);
    return response.data;
  }

  async getAnalysisStatus(jobId: string): Promise<AnalysisStatus> {
    const response = await api.get(`/api/status/${jobId}`);
    return response.data;
  }

  async getAnalysisResults(jobId: string): Promise<AnalysisResult> {
    const response = await api.get(`/api/results/${jobId}`);
    return response.data;
  }

  async getAnalysisJobs(): Promise<AnalysisStatus[]> {
    const response = await api.get('/analysis/jobs');
    return response.data;
  }

  // Download operations
  async downloadResults(jobId: string, format: 'excel' | 'csv' | 'json' = 'excel'): Promise<Blob> {
    const response = await api.get(`/api/download/${jobId}/${format}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Search operations
  async searchEmployee(jobId: string, uid?: string, grade?: string) {
    const params = new URLSearchParams();
    if (uid?.trim()) params.append('uid', uid.trim());
    if (grade?.trim()) params.append('grade', grade.trim());
    
    const queryString = params.toString();
    const url = `/api/v1/employee/${jobId}${queryString ? `?${queryString}` : ''}`;
    
    const response = await api.get(url);
    return response.data;
  }

  async searchResults(params: {
    job_id: string;
    query?: string;
    filters?: Record<string, any>;
  }) {
    const response = await api.post('/api/search/results', params);
    return response.data;
  }

  // User authentication
  async register(data: { email: string; name: string; password: string }) {
    const response = await api.post('/user/register', data);
    return response.data;
  }

  async login(data: { email: string; password: string }): Promise<LoginResponse> {
    const params = new URLSearchParams();
    params.append('username', data.email);
    params.append('password', data.password);
    
    const response = await api.post('/user/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    const result = response.data;
    
    // Update axios instance with token
    if (result.access_token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${result.access_token}`;
      localStorage.setItem('token', result.access_token);
      if (result.user_info) {
        localStorage.setItem('user', JSON.stringify(result.user_info));
      }
    }
    
    return result;
  }

  async getCurrentUser(): Promise<UserInfo> {
    const response = await api.get('/user/me');
    return response.data;
  }

  async changePassword(currentPassword: string, newPassword: string) {
    const response = await api.put('/user/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  }

  // Admin operations
  async getPendingUsers() {
    const response = await api.get('/user/pending');
    return response.data;
  }

  async approveUser(userId: number, isApproved: boolean) {
    const response = await api.post('/user/approve', {
      user_id: userId,
      approve: isApproved
    });
    return response.data;
  }

  // Dashboard data
  async getDashboardData() {
    try {
      const [healthResponse, jobsResponse] = await Promise.all([
        this.healthCheck(),
        this.getAnalysisJobs()
      ]);
      
      return {
        system_status: 'healthy',
        server_info: healthResponse,
        jobs: jobsResponse,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('❌ Dashboard data fetch error:', error);
      return {
        system_status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      };
    }
  }

  // Utility methods
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete api.defaults.headers.common['Authorization'];
    window.location.href = '/login';
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }

  getCurrentToken(): string | null {
    return localStorage.getItem('token');
  }
}

// Initialize token from localStorage
const token = localStorage.getItem('token');
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

// Export singleton instance
export const apiService = new APIService();

// Export individual functions for backward compatibility
export const {
  healthCheck,
  uploadFile,
  getFiles,
  deleteFile,
  startAnalysis,
  getAnalysisStatus,
  getAnalysisResults,
  getAnalysisJobs,
  downloadResults,
  searchEmployee,
  searchResults,
  register,
  login,
  getCurrentUser,
  changePassword,
  getPendingUsers,
  approveUser,
  getDashboardData,
  logout
} = apiService;

export default apiService;