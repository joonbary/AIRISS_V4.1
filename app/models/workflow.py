"""
워크플로우 모델 정의
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class WorkflowJob(Base):
    """워크플로우 작업"""
    __tablename__ = "workflow_jobs"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    status = Column(String, default='initializing')  # initializing, running, completed, failed
    progress = Column(Float, default=0.0)
    error = Column(Text, nullable=True)
    download_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    job_metadata = Column(JSON, nullable=True)

class WorkflowTask(Base):
    """워크플로우 태스크"""
    __tablename__ = "workflow_tasks"
    
    id = Column(String, primary_key=True)
    job_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default='pending')  # pending, running, completed, failed, retrying
    error = Column(Text, nullable=True)
    result = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)