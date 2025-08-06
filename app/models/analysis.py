"""
Analysis Result Model
분석 결과 모델
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results_v2"
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(String(36), unique=True, index=True)
    job_id = Column(String(36), index=True)
    
    uid = Column(String(100), index=True)
    file_id = Column(String(100), index=True)
    filename = Column(String(500))
    opinion = Column(Text)
    
    # Scores
    overall_score = Column(Float)
    text_score = Column(Float)
    quantitative_score = Column(Float)
    confidence = Column(Float)
    percentile = Column(Float, default=50.0)
    
    # Grade
    ok_grade = Column(String(10))
    grade_description = Column(Text)
    
    # Detailed scores and feedback
    dimension_scores = Column(JSON)
    ai_feedback = Column(JSON)
    ai_strengths = Column(Text)
    ai_weaknesses = Column(Text)
    ai_recommendations = Column(JSON)
    ai_error = Column(Text)
    
    # Full result data
    result_data = Column(JSON)
    
    # Metadata
    analysis_mode = Column(String(20), default='hybrid')
    version = Column(String(10), default='4.0')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())