"""
평가의견 분석 API 스키마 정의
Opinion analysis API schema definitions
"""
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class OpinionUploadRequest(BaseModel):
    """평가의견 업로드 요청 스키마"""
    uid: str = Field(..., description="직원 고유 ID")
    opinions: Dict[str, Optional[str]] = Field(
        ..., 
        description="연도별 평가의견 (예: {'2023': '...', '2022': null})"
    )
    
    @validator('opinions')
    def validate_years(cls, v):
        """연도 형식 검증"""
        for year in v.keys():
            try:
                year_int = int(year)
                if year_int < 2000 or year_int > 2100:
                    raise ValueError(f"Invalid year: {year}")
            except ValueError:
                raise ValueError(f"Year must be a valid integer: {year}")
        return v


class OpinionBatchUploadRequest(BaseModel):
    """평가의견 일괄 업로드 요청"""
    data: List[OpinionUploadRequest]
    force_update: bool = Field(False, description="기존 데이터 덮어쓰기 여부")


class DimensionScore(BaseModel):
    """8대 역량 점수"""
    leadership: float = Field(..., ge=0, le=100)
    collaboration: float = Field(..., ge=0, le=100)
    problem_solving: float = Field(..., ge=0, le=100)
    innovation: float = Field(..., ge=0, le=100)
    communication: float = Field(..., ge=0, le=100)
    expertise: float = Field(..., ge=0, le=100)
    execution: float = Field(..., ge=0, le=100)
    growth: float = Field(..., ge=0, le=100)


class OpinionAnalysisResult(BaseModel):
    """평가의견 분석 결과"""
    uid: str
    summary: str = Field(..., description="전체 평가의견 요약")
    strengths: List[str] = Field(..., description="강점 키워드 리스트")
    weaknesses: List[str] = Field(..., description="약점 키워드 리스트")
    
    # 점수 관련
    text_score: float = Field(..., ge=0, le=100, description="텍스트 기반 점수")
    sentiment_score: float = Field(..., ge=-1, le=1, description="감성 점수")
    specificity_score: float = Field(..., ge=0, le=1, description="구체성 점수")
    consistency_score: float = Field(..., ge=0, le=1, description="일관성 점수")
    
    # 역량 매핑
    dimension_scores: DimensionScore
    
    # 통합 점수
    hybrid_score: float = Field(..., ge=0, le=100, description="하이브리드 점수")
    confidence: float = Field(..., ge=0, le=1, description="분석 신뢰도")
    
    # 메타데이터
    years_analyzed: List[str]
    analyzed_at: datetime
    model_version: str = "v1.0"
    processing_time: Optional[float] = None
    
    class Config:
        from_attributes = True


class OpinionAnalysisResponse(BaseModel):
    """평가의견 분석 API 응답"""
    success: bool
    result: Optional[OpinionAnalysisResult] = None
    message: Optional[str] = None
    
    
class OpinionKeywordAnalysis(BaseModel):
    """키워드 분석 결과"""
    keyword: str
    keyword_type: str = Field(..., pattern="^(strength|weakness)$")
    frequency: float = Field(..., ge=0)
    importance: float = Field(..., ge=0, le=1)
    dimension: Optional[str] = None
    dimension_relevance: Optional[float] = Field(None, ge=0, le=1)


class TextCleaningConfig(BaseModel):
    """텍스트 정제 설정"""
    remove_special_chars: bool = True
    normalize_whitespace: bool = True
    remove_stopwords: bool = True
    min_length: int = Field(10, description="최소 문장 길이")
    max_length: int = Field(1000, description="최대 문장 길이")


class HybridScoreConfig(BaseModel):
    """하이브리드 점수 계산 설정"""
    quantitative_weight: float = Field(0.6, ge=0, le=1)
    text_weight: float = Field(0.4, ge=0, le=1)
    
    @validator('text_weight')
    def validate_weights(cls, v, values):
        """가중치 합이 1인지 검증"""
        if 'quantitative_weight' in values:
            if abs(values['quantitative_weight'] + v - 1.0) > 0.001:
                raise ValueError("Weights must sum to 1.0")
        return v