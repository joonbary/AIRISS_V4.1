/**
 * AIRISS v4.2 Employee AI Analysis API Service
 */
import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' ? '' : 'http://localhost:8003');

// Types
export interface CompetencyScores {
  실행력: number;
  성장지향: number;
  협업: number;
  고객지향: number;
  전문성: number;
  혁신성: number;
  리더십: number;
  커뮤니케이션: number;
}

export interface EmployeeAIAnalysis {
  employee_id: string;
  name: string;
  department: string;
  position: string;
  profile_image?: string;
  ai_score: number;
  grade: string;
  competencies: CompetencyScores;
  strengths: string[];
  improvements: string[];
  ai_comment: string;
  career_recommendation: string[];
  education_suggestion: string[];
  analyzed_at: string;
  model_version: string;
  confidence_score?: number;
  percentile_rank?: number;
}

export interface EmployeeAIAnalysisSummary {
  employee_id: string;
  name: string;
  department: string;
  position: string;
  profile_image?: string;
  ai_score: number;
  grade: string;
  strengths_summary: string;
  improvements_summary: string;
  ai_comment_preview: string;
}

export interface EmployeeListResponse {
  items: EmployeeAIAnalysisSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  statistics?: Record<string, any>;
}

export interface AIRecommendation {
  employee_id: string;
  name: string;
  department: string;
  position: string;
  profile_image?: string;
  recommendation_type: string;
  recommendation_score: number;
  recommendation_reason: string;
  ai_score: number;
  grade: string;
  key_strengths: string[];
  risk_factors?: string[];
}

export interface DashboardStatistics {
  total_employees: number;
  grade_distribution: Record<string, number>;
  grade_percentage: Record<string, number>;
  average_score: number;
  median_score: number;
  score_range: Record<string, number>;
  competency_averages: CompetencyScores;
  top_strengths: any[];
  top_improvements: any[];
  department_stats?: Record<string, any>;
  talent_count: number;
  promotion_candidates: number;
  risk_employees: number;
}

export interface CompetencyRadarData {
  labels: string[];
  values: number[];
  average_values?: number[];
}

export interface AIFeedbackSave {
  employee_id: string;
  ai_feedback_text: string;
  action: 'save_to_record' | 'send_email' | 'create_report' | 'schedule_meeting';
  additional_data?: Record<string, any>;
  feedback_category?: string;
  is_confidential?: boolean;
  scheduled_date?: string;
}

export interface AIFeedbackResponse {
  success: boolean;
  message: string;
  feedback_id?: string;
  saved_at?: string;
}

// API Functions
class EmployeeApiService {
  private axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  /**
   * 특정 직원의 AI 분석 결과 조회
   */
  async getEmployeeAIAnalysis(employeeId: string): Promise<EmployeeAIAnalysis> {
    try {
      console.log('🔍 API 호출 - 직원 ID:', employeeId);
      console.log('📡 요청 URL:', `${API_BASE_URL}/api/v1/employees/${employeeId}/ai-analysis`);
      
      const response = await this.axiosInstance.get(
        `/api/v1/employees/${employeeId}/ai-analysis`
      );
      
      console.log('✅ API 응답:', response.data);
      console.log('👤 응답 직원 이름:', response.data.name);
      console.log('🆔 응답 직원 ID:', response.data.employee_id);
      
      return response.data;
    } catch (error) {
      console.error('Failed to fetch employee AI analysis:', error);
      throw error;
    }
  }

  /**
   * 특정 직원의 상세 정보 조회 (uid 기반)
   */
  async getEmployeeDetail(uid: string): Promise<EmployeeAIAnalysis> {
    try {
      const response = await this.axiosInstance.get(
        `/api/v1/employees/${uid}/ai-analysis`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to fetch employee detail:', error);
      throw error;
    }
  }

  /**
   * 전체 직원 AI 분석 목록 조회
   */
  async getEmployeesList(params: {
    page?: number;
    page_size?: number;
    department?: string;
    position?: string;
    grade?: string;
    min_score?: number;
    max_score?: number;
    search?: string;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<EmployeeListResponse> {
    try {
      const response = await this.axiosInstance.get('/api/v1/employees/ai-analysis/list', {
        params,
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch employees list:', error);
      throw error;
    }
  }

  /**
   * AI 추천 인재 조회
   */
  async getAIRecommendations(
    type: 'talent' | 'promotion' | 'risk' | 'leadership',
    limit: number = 10
  ): Promise<AIRecommendation[]> {
    try {
      const response = await this.axiosInstance.get('/api/v1/employees/ai-recommendation', {
        params: { type, limit },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch AI recommendations:', error);
      throw error;
    }
  }

  /**
   * AI 피드백 저장
   */
  async saveAIFeedback(feedback: AIFeedbackSave): Promise<AIFeedbackResponse> {
    try {
      const response = await this.axiosInstance.post(
        '/api/v1/employees/ai-feedback/save',
        feedback
      );
      return response.data;
    } catch (error) {
      console.error('Failed to save AI feedback:', error);
      throw error;
    }
  }

  /**
   * 직원 역량 레이더 차트 데이터 조회
   */
  async getCompetencyRadarData(employeeId: string): Promise<CompetencyRadarData> {
    try {
      const response = await this.axiosInstance.get(
        `/api/v1/employees/${employeeId}/competency-radar-data`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to fetch competency radar data:', error);
      throw error;
    }
  }

  /**
   * 대시보드 통계 데이터 조회
   */
  async getDashboardStatistics(department?: string): Promise<DashboardStatistics> {
    try {
      const response = await this.axiosInstance.get('/api/v1/employees/dashboard/statistics', {
        params: department ? { department } : undefined,
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch dashboard statistics:', error);
      throw error;
    }
  }

  /**
   * 엑셀 데이터 다운로드
   */
  async exportEmployeesData(params?: {
    department?: string;
    position?: string;
    grade?: string;
  }): Promise<Blob> {
    try {
      const response = await this.axiosInstance.get('/api/v1/employees/export', {
        params,
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error('Failed to export employees data:', error);
      throw error;
    }
  }
}

export const employeeApi = new EmployeeApiService();