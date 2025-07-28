"""
Pydantic Schemas
API 요청/응답 모델 정의
"""

from .user import UserCreate, UserLogin, UserResponse, UserUpdate, Token
from .file import FileInfo, FileUploadResponse
from .analysis import (
    AnalysisCreate,
    AnalysisResponse,
    JobStatus,
    AnalysisResult,
    DimensionScores,
    AIFeedback
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserLogin", 
    "UserResponse",
    "UserUpdate",
    "Token",
    
    # File schemas
    "FileInfo",
    "FileUploadResponse",
    
    # Analysis schemas
    "AnalysisCreate",
    "AnalysisResponse",
    "JobStatus",
    "AnalysisResult",
    "DimensionScores",
    "AIFeedback"
]