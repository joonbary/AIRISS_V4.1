import axios, { AxiosError } from 'axios';

// API 기본 URL 설정 (Railway 호환)
// 프로덕션에서는 같은 도메인 사용 (프록시 설정됨)
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' ? '' : 'http://localhost:8003');

// axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: parseInt(process.env.REACT_APP_API_TIMEOUT || '300000'), // 5분 타임아웃
});

// 요청 인터셉터 - 인증 없음
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

// 파일 업로드 (분석 서비스 업로드 엔드포인트 사용)
export const uploadFile = async (file: File) => {
  console.log('📤 Uploading file:', {
    name: file.name,
    size: file.size,
    type: file.type,
    lastModified: new Date(file.lastModified).toISOString()
  });

  const formData = new FormData();
  formData.append('file', file);
  
  try {
    // 업로드 엔드포인트 사용
    const response = await api.post('/api/v1/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    console.log('✅ Upload response:', response.data);
    
    // Validate response
    if (!response.data.file_id) {
      console.error('❌ No file_id in response:', response.data);
      throw new Error('Upload response missing file_id');
    }
    
    if (response.data.total_records === 0) {
      console.warn('⚠️ File uploaded but has 0 records:', response.data);
    }
    
    return response.data;
  } catch (error) {
    console.error('❌ Upload failed:', error);
    throw error;
  }
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
  console.log('🔍 Starting analysis with params:', params);
  
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
  
  try {
    const response = await api.post(`/api/v1/analysis/analyze/${params.file_id}`, requestParams, {
      timeout: 600000 // 10분 타임아웃 (분석 요청 전용)
    });
    console.log('✅ Analysis started:', response.data);
    
    if (!response.data.job_id) {
      console.error('❌ No job_id in response:', response.data);
      throw new Error('Analysis response missing job_id');
    }
    
    return response.data;
  } catch (error) {
    console.error('❌ Analysis start failed:', error);
    throw error;
  }
};

// 분석 작업 목록 조회
export const getAnalysisJobs = async () => {
  const response = await api.get('/analysis/jobs');
  return response.data;
};

// 분석 상태 확인
export const getAnalysisStatus = async (jobId: string) => {
  const response = await api.get(`/api/v1/analysis/status/${jobId}`);
  return response.data;
};

// 분석 결과 조회
export const getAnalysisResults = async (jobId: string) => {
  const response = await api.get(`/api/v1/analysis/results/${jobId}`);
  return response.data;
};

// 분석 결과 파일 존재 여부 확인
export const checkResultsAvailability = async (jobId: string) => {
  const response = await api.get(`/api/v1/analysis/check-results/${jobId}`);
  return response.data;
};

// 결과 다운로드 (백엔드 경로와 완벽히 일치)
export const downloadResults = async (jobId: string, format: string = 'excel'): Promise<Blob> => {
  const response = await api.get(`/api/v1/analysis/download/${jobId}/${format}`, {
    responseType: 'blob',
  });
  return response.data;
};

// 직원 검색 - 올바른 백엔드 엔드포인트 호출 (UID 또는 등급 OR 조건)
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
    
    // 🔧 수정: 올바른 백엔드 엔드포인트 호출
    const queryString = params.toString();
    const url = `/api/v1/employee/${jobId}${queryString ? `?${queryString}` : ''}`;
    
    console.log(`🔍 직원 검색 API 호출: ${url}`);
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('❌ 직원 검색 실패:', error);
    // 에러를 다시 던져서 프론트엔드에서 적절히 처리하도록 함
    throw error;
  }
};

// 완료된 작업 목록 - 기존 API 사용
export const getCompletedJobs = async () => {
  try {
    // 기존 analysis jobs API 사용
    const response = await api.get('/analysis/jobs');
    // 완료된 작업만 필터링
    const allJobs = response.data;
    const completedJobs = Array.isArray(allJobs) 
      ? allJobs.filter((job: any) => job.status === 'completed')
      : [];
    
    return completedJobs;
  } catch (error) {
    console.error('❌ 완료된 작업 목록 조회 실패:', error);
    throw error;
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

// 파일 목록 조회
export const getFiles = async () => {
  try {
    const response = await api.get('/api/v1/files/list');
    // 백엔드에서 반환하는 배열 직접 사용
    const files = Array.isArray(response.data) ? response.data : (response.data.files || []);
    return files.map((file: any) => ({
      id: file.id,
      filename: file.filename,
      upload_time: file.upload_time,
      total_records: file.total_records,
      size: file.size || 0,
      user_id: file.user_id,
      session_id: file.session_id,
      columns: file.columns || []
    }));
  } catch (error: any) {
    console.error('❌ 파일 목록 조회 실패:', error);
    // 인증 제거됨 - 401 에러 무시
    return [];
  }
};

// 인증 기능 제거됨 - 로그인/회원가입 불필요
// Public access enabled

// 더미 함수들 (컴파일 에러 방지용)
export const register = async (data: any) => {
  console.warn('인증이 비활성화되었습니다. 회원가입이 필요하지 않습니다.');
  return { message: 'Authentication disabled' };
};

export const login = async (data: any) => {
  console.warn('인증이 비활성화되었습니다. 로그인이 필요하지 않습니다.');
  return { message: 'Authentication disabled' };
};

// 내 정보 조회
export const getMe = async () => {
  // 인증 없이 기본 사용자 정보 반환
  return {
    email: 'test@airiss.com',
    name: 'Test User',
    is_approved: true,
    is_admin: true
  };
};

// 승인 대기 사용자 목록 조회
export const getPendingUsers = async () => {
  const response = await api.get('/user/pending');
  return response.data;
};

// 사용자 승인/거부
export const approveUser = async (userId: number, isApproved: boolean) => {
  const response = await api.post('/user/approve', {
    user_id: userId,
    approve: isApproved
  });
  return response.data;
};

// 로그아웃 기능 제거됨 - Public access
export const logout = () => {
  console.warn('인증이 비활성화되었습니다. 로그아웃이 필요하지 않습니다.');
};

// 현재 사용자 정보 조회
export const getCurrentUser = async () => {
  const response = await api.get('/user/me');
  return response.data;
};

// 비밀번호 변경
export const changePassword = async (currentPassword: string, newPassword: string) => {
  const response = await api.put('/user/change-password', {
    current_password: currentPassword,
    new_password: newPassword
  });
  return response.data;
};

// 인증 기능 완전히 제거됨 - 모든 API Public access

// API_BASE_URL export 추가
export { API_BASE_URL };

export default api;