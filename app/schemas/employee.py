"""
AIRISS v4.2 직원 AI 분석 스키마
Employee AI Analysis Pydantic Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class EmployeeData(BaseModel):
    """직원 데이터"""
    UID: str
    원본의견: str
    AIRISS_v2_종합점수: float
    OK등급: str
    등급설명: str
    백분위: str
    분석신뢰도: float
    텍스트_종합점수: float
    정량_종합점수: float
    정량_데이터품질: str
    AI_장점: str
    AI_개선점: str
    AI_종합피드백: str
    percentile_rank: Optional[float] = None
    score_differences: Optional[Dict[str, float]] = None
    
    class Config:
        extra = "allow"  # 8대 영역 점수 등 추가 필드 허용


class EmployeeStatistics(BaseModel):
    """전체 통계 정보"""
    total_count: int
    average_scores: Dict[str, float]
    dimension_averages: Dict[str, float]
    grade_distribution: Dict[str, int]
    top_grade_ratio: float


class EmployeeSearchResponse(BaseModel):
    """직원 검색 응답"""
    employee: EmployeeData
    statistics: EmployeeStatistics


class EmployeeListItem(BaseModel):
    """직원 목록 아이템"""
    uid: str
    grade: str
    score: float


class EmployeeListResponse(BaseModel):
    """직원 목록 응답"""
    employees: List[EmployeeListItem]


# v4.2 새로운 스키마 추가
class AIGrade(str, Enum):
    """AI 평가 등급"""
    S = "S"
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class CompetencyScores(BaseModel):
    """8대 핵심 역량 점수"""
    실행력: int = Field(..., ge=0, le=100, description="실행력 점수")
    성장지향: int = Field(..., ge=0, le=100, description="성장지향 점수")
    협업: int = Field(..., ge=0, le=100, description="협업 점수")
    고객지향: int = Field(..., ge=0, le=100, description="고객지향 점수")
    전문성: int = Field(..., ge=0, le=100, description="전문성 점수")
    혁신성: int = Field(..., ge=0, le=100, description="혁신성 점수")
    리더십: int = Field(..., ge=0, le=100, description="리더십 점수")
    커뮤니케이션: int = Field(..., ge=0, le=100, description="커뮤니케이션 점수")


class EmployeeAIAnalysis(BaseModel):
    """직원 AI 분석 상세 결과"""
    employee_id: str = Field(..., description="직원 ID")
    name: str = Field(..., description="직원 이름")
    department: str = Field(..., description="부서명")
    position: str = Field(..., description="직급")
    profile_image: Optional[str] = Field(None, description="프로필 이미지 URL")
    
    # AI 분석 결과
    ai_score: int = Field(..., ge=0, le=1000, description="AI 종합 점수")
    grade: AIGrade = Field(..., description="AI 평가 등급")
    competencies: CompetencyScores = Field(..., description="8대 역량 점수")
    
    # 강점과 개선점
    strengths: List[str] = Field(..., max_items=3, description="강점 TOP 3")
    improvements: List[str] = Field(..., max_items=2, description="개발 필요 역량 TOP 2")
    
    # AI 분석 텍스트
    ai_comment: str = Field(..., description="AI 자연어 코멘트")
    
    # 추천 사항
    career_recommendation: List[str] = Field(..., description="AI 추천 경력 방향")
    education_suggestion: List[str] = Field(..., description="교육 추천")
    
    # 메타 정보
    analyzed_at: datetime = Field(..., description="분석 일시")
    model_version: str = Field(default="v4.2", description="AI 모델 버전")
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeAIAnalysisSummary(BaseModel):
    """직원 AI 분석 요약 (목록용)"""
    employee_id: str
    name: str
    department: str
    position: str
    profile_image: Optional[str] = None
    ai_score: int
    grade: AIGrade
    strengths_summary: str = Field(..., description="강점 요약")
    improvements_summary: str = Field(..., description="개선점 요약")
    ai_comment_preview: str = Field(..., description="AI 코멘트 미리보기")
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeAIAnalysisList(BaseModel):
    """직원 AI 분석 목록 응답"""
    items: List[EmployeeAIAnalysisSummary]
    total: int = Field(..., description="전체 직원 수")
    page: int = Field(..., ge=1, description="현재 페이지")
    page_size: int = Field(..., ge=1, le=100, description="페이지 크기")
    total_pages: int = Field(..., ge=1, description="전체 페이지 수")
    
    # 통계 정보
    statistics: Optional[Dict[str, Any]] = Field(None, description="통계 정보")


class RecommendationType(str, Enum):
    """AI 추천 유형"""
    TALENT = "talent"
    PROMOTION = "promotion"
    RISK = "risk"
    LEADERSHIP = "leadership"


class AIRecommendation(BaseModel):
    """AI 추천 인재"""
    employee_id: str
    name: str
    department: str
    position: str
    profile_image: Optional[str] = None
    
    # 추천 관련
    recommendation_type: RecommendationType
    recommendation_score: float = Field(..., ge=0, le=100, description="추천 점수")
    recommendation_reason: str = Field(..., description="추천 사유")
    
    # 추가 정보
    ai_score: int
    grade: AIGrade
    key_strengths: List[str] = Field(..., max_items=3)
    risk_factors: Optional[List[str]] = Field(None, description="위험 요인 (이직 위험군)")
    
    model_config = ConfigDict(from_attributes=True)


class AIFeedbackAction(str, Enum):
    """AI 피드백 액션 타입"""
    SAVE_TO_RECORD = "save_to_record"
    SEND_EMAIL = "send_email"
    CREATE_REPORT = "create_report"
    SCHEDULE_MEETING = "schedule_meeting"


class AIFeedbackSave(BaseModel):
    """AI 피드백 저장 요청"""
    employee_id: str = Field(..., description="직원 ID")
    ai_feedback_text: str = Field(..., description="AI 피드백 텍스트")
    action: AIFeedbackAction = Field(..., description="액션 타입")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="추가 데이터")
    
    # 선택적 필드
    feedback_category: Optional[str] = Field(None, description="피드백 카테고리")
    is_confidential: bool = Field(default=False, description="기밀 여부")
    scheduled_date: Optional[datetime] = Field(None, description="예약 일시")


class AIFeedbackResponse(BaseModel):
    """AI 피드백 저장 응답"""
    success: bool
    message: str
    feedback_id: Optional[str] = None
    saved_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CompetencyRadarData(BaseModel):
    """레이더 차트용 역량 데이터"""
    labels: List[str] = Field(..., description="역량 라벨")
    values: List[int] = Field(..., description="역량 점수")
    average_values: Optional[List[float]] = Field(None, description="조직 평균 점수")
    
    model_config = ConfigDict(from_attributes=True)


class DashboardStatistics(BaseModel):
    """대시보드 통계 데이터"""
    total_employees: int = Field(..., description="전체 직원 수")
    
    # 등급 분포
    grade_distribution: Dict[str, int] = Field(..., description="등급별 인원 분포")
    grade_percentage: Dict[str, float] = Field(..., description="등급별 비율")
    
    # 점수 통계
    average_score: float = Field(..., description="평균 AI 점수")
    median_score: float = Field(..., description="중간값 AI 점수")
    score_range: Dict[str, int] = Field(..., description="점수 구간별 분포")
    
    # 역량 통계
    competency_averages: CompetencyScores = Field(..., description="역량별 평균 점수")
    top_strengths: List[Dict[str, Any]] = Field(..., description="가장 많은 강점")
    top_improvements: List[Dict[str, Any]] = Field(..., description="가장 많은 개선점")
    
    # 부서별 통계 (선택)
    department_stats: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="부서별 통계")
    
    # 추천 인재 요약
    talent_count: int = Field(..., description="Top Talent 수")
    promotion_candidates: int = Field(..., description="승진 후보자 수")
    risk_employees: int = Field(..., description="이직 위험군 수")
    
    model_config = ConfigDict(from_attributes=True)