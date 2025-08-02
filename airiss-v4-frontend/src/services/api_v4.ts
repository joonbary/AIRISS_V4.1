/**
 * AIRISS v4.0 API Integration Service
 * OK Financial Group Standard
 */
import axios, { AxiosError, AxiosResponse } from 'axios';

// API Base URL - AIRISS v4.0 Backend
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' ? '' : 'http://localhost:8003');

// Create axios instance with AIRISS v4.0 configuration
const apiV4 = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: parseInt(process.env.REACT_APP_API_TIMEOUT || '60000'),
});

// Request interceptor - Add auth token
apiV4.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log(`🚀 AIRISS v4.0 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ AIRISS v4.0 Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiV4.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`✅ AIRISS v4.0 API Response: ${response.config.url} - ${response.status}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('❌ AIRISS v4.0 API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    
    // Enhanced error messages
    if (error.response) {
      const data: any = error.response.data;
      error.message = data.detail || data.message || error.message;
    } else if (error.request) {
      error.message = '🔗 AIRISS v4.0 서버에 연결할 수 없습니다. 백엔드 서버(포트 8003)가 실행 중인지 확인해주세요.';
    }
    
    return Promise.reject(error);
  }
);

// Types
export interface UserResponse {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  is_admin: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface JobResponse {
  job_id: string;
  status: string;
  progress: number;
  filename: string;
  download_url?: string;
  error?: string;
}

export interface HealthResponse {
  status: string;
  openai_configured: boolean;
  database: string;
  timestamp: string;
}

// Authentication APIs
export const authAPI = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await apiV4.post<LoginResponse>('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Store token and user info
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('token', response.data.access_token); // Backward compatibility
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  },

  getCurrentUser: async (): Promise<UserResponse> => {
    const response = await apiV4.get<UserResponse>('/api/v1/auth/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

// Analysis APIs
export const analysisAPI = {
  uploadFile: async (
    file: File, 
    onProgress?: (progress: number) => void
  ): Promise<JobResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiV4.post<JobResponse>('/api/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
    
    return response.data;
  },

  getJobStatus: async (jobId: string): Promise<JobResponse> => {
    const response = await apiV4.get<JobResponse>(`/api/v1/jobs/${jobId}`);
    return response.data;
  },

  downloadResult: async (token: string): Promise<Blob> => {
    const response = await apiV4.get(`/api/v1/download/${token}`, {
      responseType: 'blob',
    });
    return response.data;
  }
};

// System APIs
export const systemAPI = {
  healthCheck: async (): Promise<HealthResponse> => {
    const response = await apiV4.get<HealthResponse>('/api/v1/health');
    return response.data;
  },

  getServerInfo: async () => {
    const response = await apiV4.get('/');
    return response.data;
  }
};

// WebSocket URL generator
export const getWebSocketURL = (jobId?: string): string => {
  const baseWsUrl = (API_BASE_URL.replace('http', 'ws'));
  return jobId ? `${baseWsUrl}/ws/${jobId}` : `${baseWsUrl}/ws/general`;
};

// File download helper
export const downloadFile = async (token: string, filename?: string) => {
  try {
    const blob = await analysisAPI.downloadResult(token);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || `airiss_analysis_${new Date().toISOString().split('T')[0]}.xlsx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    console.error('Download failed:', error);
    throw error;
  }
};

// Error handler helper
export const handleAPIError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'Unknown error occurred';
};

export default apiV4;