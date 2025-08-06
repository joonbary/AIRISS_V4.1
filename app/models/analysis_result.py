# app/models/analysis_result.py
# 분석 결과 영구 저장을 위한 SQLAlchemy 모델

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class AnalysisResultModel(Base):
    """분석 결과 저장 모델"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # 기본 정보
    uid = Column(String(100), index=True)
    file_id = Column(String(100), index=True)
    filename = Column(String(500))
    
    # 분석 결과
    opinion = Column(Text)
    hybrid_score = Column(Float)
    text_score = Column(Float)
    quantitative_score = Column(Float)
    ok_grade = Column(String(10))
    grade_description = Column(Text)
    confidence = Column(Float)
    
    # 차원별 점수 (JSON 형태로 저장)
    dimension_scores = Column(JSON)
    
    # AI 피드백 (옵션)
    ai_feedback = Column(JSON)
    ai_strengths = Column(Text, nullable=True)
    ai_weaknesses = Column(Text, nullable=True)
    ai_recommendations = Column(JSON, nullable=True)
    
    # 메타데이터
    analysis_mode = Column(String(20), default="hybrid")
    version = Column(String(10), default="4.0")
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AnalysisJobModel(Base):
    """분석 작업 정보 저장 모델"""
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(36), unique=True, index=True)
    
    # 작업 기본 정보
    file_id = Column(String(100), index=True)
    filename = Column(String(500))
    
    # 작업 상태
    status = Column(String(20), default="processing")  # processing, completed, failed
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    
    # 분석 설정
    analysis_mode = Column(String(20), default="hybrid")
    enable_ai_feedback = Column(Boolean, default=False)
    
    # 결과 통계
    average_score = Column(Float)
    processing_time = Column(Float)  # 초 단위
    
    # 오류 정보
    error_message = Column(Text)
    
    # 시간 정보
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
class AnalysisStatsModel(Base):
    """분석 통계 정보 저장 모델"""
    __tablename__ = "analysis_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 통계 기간
    date = Column(String(10), index=True)  # YYYY-MM-DD 형태
    
    # 일별 통계
    total_analyses = Column(Integer, default=0)
    total_files = Column(Integer, default=0)
    avg_score = Column(Float)
    
    # 등급별 분포
    grade_s_count = Column(Integer, default=0)
    grade_a_count = Column(Integer, default=0)
    grade_b_count = Column(Integer, default=0)
    grade_c_count = Column(Integer, default=0)
    grade_d_count = Column(Integer, default=0)
    
    # 기타 통계
    ai_feedback_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
