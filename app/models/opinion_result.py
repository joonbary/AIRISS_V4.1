"""
평가의견 분석 결과 데이터베이스 모델
Opinion analysis result database model
"""
from sqlalchemy import Column, String, Float, JSON, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class OpinionResult(Base):
    """평가의견 분석 결과 모델"""
    __tablename__ = "opinion_results"
    
    # Primary Keys
    id = Column(String, primary_key=True, index=True)
    uid = Column(String, index=True)  # Remove foreign key constraint
    job_id = Column(String, ForeignKey("jobs.id"))
    employee_result_id = Column(String, ForeignKey("employee_results.id"))  # Use proper foreign key
    
    # 원본 평가의견 데이터
    raw_opinions = Column(JSON)  # {"2023": "...", "2022": null, ...}
    years_analyzed = Column(JSON)  # ["2021", "2023"]
    
    # LLM 분석 결과
    summary = Column(Text)  # 전체 평가의견 요약
    strengths = Column(JSON)  # ["추진력", "협업", ...]
    weaknesses = Column(JSON)  # ["전략적 사고", ...]
    
    # 텍스트 기반 점수
    text_score = Column(Float)  # 0-100
    sentiment_score = Column(Float)  # -1 to 1 (부정적 to 긍정적)
    specificity_score = Column(Float)  # 0-1 (구체성)
    consistency_score = Column(Float)  # 0-1 (연도별 일관성)
    
    # 8대 역량 매핑 점수
    dimension_scores = Column(JSON)  # {"leadership": 87, "collaboration": 83, ...}
    
    # 통합 점수
    hybrid_score = Column(Float)  # 정량 + 정성 통합 점수
    confidence = Column(Float)  # 분석 신뢰도 (0-1)
    
    # 메타데이터
    model_version = Column(String, default="v1.0")
    analyzed_at = Column(DateTime, server_default=func.now())
    processing_time = Column(Float)  # 처리 시간 (초)
    
    # Relationships
    employee = relationship("EmployeeResult", back_populates="opinion_analysis", foreign_keys=[employee_result_id])


class OpinionKeyword(Base):
    """평가의견에서 추출된 키워드 모델"""
    __tablename__ = "opinion_keywords"
    
    id = Column(String, primary_key=True, index=True)
    opinion_result_id = Column(String, ForeignKey("opinion_results.id"))
    
    keyword = Column(String, index=True)
    keyword_type = Column(String)  # "strength" or "weakness"
    frequency = Column(Float)  # 출현 빈도
    importance = Column(Float)  # 중요도 점수
    
    # 8대 역량 연관도
    dimension = Column(String)  # "leadership", "collaboration", etc.
    dimension_relevance = Column(Float)  # 0-1
    
    created_at = Column(DateTime, server_default=func.now())