"""
Job Model
분석 작업 정보 모델
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from app.db.database import Base


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True)
    file_id = Column(String(36), nullable=False)
    filename = Column(String(255))
    
    status = Column(String(50), default='pending')
    sample_size = Column(Integer)
    analysis_mode = Column(String(50), default='hybrid')
    
    enable_ai_feedback = Column(Boolean, default=False)
    openai_model = Column(String(100))
    max_tokens = Column(Integer)
    
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    
    progress = Column(Float, default=0.0)
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    
    error = Column(Text)
    job_data = Column(Text)  # JSON
    results_data = Column(Text)  # JSON - Analysis results
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())