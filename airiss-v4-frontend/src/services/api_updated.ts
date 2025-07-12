import axios, { AxiosError } from 'axios';

// API 기본 URL 설정 (8002 포트로 수정, /api/v1 제거)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003';

// axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: parseInt(process.env.REACT_APP_API_TIMEOUT || '30000'),
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
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
    
    // 에러 메시지 개선
    if (error.response) {
      const data: any = error.response.data;
      error.message = data.detail || data.message || error.message;
    } else if (error.request) {
      error.message = '🔗 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.';
    }
    
    return Promise.reject(error);
  }
);

// 헬스체크 - 백엔드 연결 확인
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

// 파일 업로드 (백엔드 경로와 일치)
export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
      console.log(`📤 Upload Progress: ${percentCompleted}%`);
    },
  });

  return response.data;
};

// 분석 시작 (백엔드 경로와 일치)
export const startAnalysis = async (params: {
  file_id: string;
  sample_size: number;
  analysis_mode: string;
  enable_ai_feedback?: boolean;
  openai_api_key?: string;
  openai_model?: string;
  max_tokens?: number;
}) => {
  // 백엔드 AnalysisRequest 모델과 일치하는 파라미터만 전송
  const requestParams = {
    file_id: params.file_id,
    sample_size: params.sample_size,
    analysis_mode: params.analysis_mode,
    enable_ai_feedback: params.enable_ai_feedback || false,
    openai_api_key: params.openai_api_key,
    openai_model: params.openai_model || "gpt-3.5-turbo",
    max_tokens: params.max_tokens || 1200
  };
  
  console.log('🚀 Sending analysis request:', requestParams);
  const response = await api.post('/analysis/start', requestParams);
  return response.data;
};

// 분석 작업 목록 조회
export const getAnalysisJobs = async () => {
  const response = await api.get('/analysis/jobs');
  return response.data;
};

// 분석 상태 확인
export const getAnalysisStatus = async (jobId: string) => {
  const response = await api.get(`/analysis/status/${jobId}`);
  return response.data;
};

// 분석 결과 조회
export const getAnalysisResults = async (jobId: string) => {
  const response = await api.get(`/analysis/results/${jobId}`);
  return response.data;
};

// 결과 다운로드 (백엔드 경로와 완벽히 일치)
export const downloadResults = async (jobId: string, format: string = 'excel'): Promise<Blob> => {
  const response = await api.get(`/analysis/download/${jobId}/${format}`, {
    responseType: 'blob',
  });
  return response.data;
};

// 직원 검색 - 개선된 통합 엔드포인트 (UID 또는 등급 OR 조건)
export const searchEmployee = async (jobId: string, uid?: string, grade?: string) => {
  try {
    // 쿼리 파라미터 구성
    const params = new URLSearchParams();
    if (uid?.trim()) {
      params.append('uid', uid.trim());
    }
    if (grade?.trim()) {
      params.append('grade', grade.trim());
    }
    
    // 통합 엔드포인트 호출: /api/v1/search/employee/{jobId}
    const queryString = params.toString();
    const url = `/api/v1/search/employee/${jobId}${queryString ? `?${queryString}` : ''}`;
    
    console.log(`🔍 직원 검색 API 호출: ${url}`);
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('❌ 직원 검색 실패:', error);
    // 에러를 다시 던져서 프론트엔드에서 적절히 처리하도록 함
    throw error;
  }
};

// 완료된 작업 목록 - 개선된 API 호출
export const getCompletedJobs = async () => {
  try {
    // search.py의 /jobs 엔드포인트 사용
    const response = await api.get('/api/v1/search/jobs');
    return response.data;
  } catch (error) {
    console.warn('완료된 작업 목록 API 호출 실패, 대체 API 사용:', error);
    // 폴백으로 기존 API 사용
    const fallbackResponse = await api.get('/analysis/jobs');
    return fallbackResponse.data;
  }
};

// 대시보드 데이터
export const getDashboardData = async () => {
  try {
    const healthResponse = await healthCheck();
    const jobsResponse = await getAnalysisJobs();
    
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
};

// 회원가입
export const register = async (data: { email: string; name: string; password: string }) => {
  const response = await api.post('/api/v1/user/register', data);
  return response.data;
};

// 로그인
export const login = async (data: { email: string; password: string }) => {
  const response = await api.post('/api/v1/user/login', data);
  return response.data; // { access_token: string, ... }
};

export default api;