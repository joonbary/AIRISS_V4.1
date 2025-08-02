import axios from 'axios';

// Integrated Test Server API (Port 8005)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8005';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
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
  (response) => {
    console.log(`✅ API Response: ${response.config.url} - ${response.status}`);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Auth APIs
export const login = async (email: string, password: string) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await api.post('/api/v1/auth/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  // Store token
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  }
  
  return response.data;
};

export const register = async (email: string, name: string, password: string) => {
  const response = await api.post('/api/v1/auth/register', {
    email,
    name,
    password,
  });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/api/v1/auth/me');
  return response.data;
};

// Analysis APIs
export const uploadFile = async (file: File, onProgress?: (progress: number) => void) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/v1/upload', formData, {
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
};

export const getJobStatus = async (jobId: string) => {
  const response = await api.get(`/api/v1/jobs/${jobId}`);
  return response.data;
};

export const downloadResult = async (token: string) => {
  const response = await api.get(`/api/v1/download/${token}`, {
    responseType: 'blob',
  });
  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/api/v1/health');
  return response.data;
};

// WebSocket connection
export const connectWebSocket = (jobId: string) => {
  const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/ws/${jobId}`;
  return new WebSocket(wsUrl);
};

export default api;