"""
Analysis Schemas
분석 관련 Pydantic 모델
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisCreate(BaseModel):
    """분석 작업 생성 요청"""
    file_id: str
    sample_size: Optional[int] = Field(None, ge=1, le=10000)
    analysis_mode: str = Field("hybrid", pattern="^(hybrid|text_only|quantitative_only)$")
    enable_ai_feedback: bool = False
    openai_model: Optional[str] = "gpt-3.5-turbo"
    max_tokens: Optional[int] = Field(1200, ge=100, le=4000)


class JobStatus(BaseModel):
    """작업 상태"""
    job_id: str
    status: str
    progress: float = Field(0.0, ge=0.0, le=100.0)
    message: Optional[str] = None
    processed_records: Optional[int] = 0
    total_records: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DimensionScores(BaseModel):
    """차원별 점수"""
    leadership: Optional[float] = None
    communication: Optional[float] = None
    problem_solving: Optional[float] = None
    teamwork: Optional[float] = None
    innovation: Optional[float] = None
    execution: Optional[float] = None


class AIFeedback(BaseModel):
    """AI 피드백"""
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendations: List[str] = []
    overall_assessment: Optional[str] = None


class AnalysisResult(BaseModel):
    """분석 결과"""
    analysis_id: str
    uid: str
    opinion: Optional[str] = None
    overall_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    text_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    quantitative_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    ok_grade: Optional[str] = None
    grade_description: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    percentile: Optional[float] = Field(None, ge=0.0, le=100.0)
    dimension_scores: Optional[DimensionScores] = None
    ai_feedback: Optional[AIFeedback] = None
    ai_strengths: Optional[str] = None
    ai_weaknesses: Optional[str] = None
    ai_recommendations: Optional[List[str]] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    """분석 응답"""
    job_id: str
    status: str
    results: List[AnalysisResult] = []
    summary: Optional[Dict[str, Any]] = None