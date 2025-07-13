# app/schemas/__init__.py
"""
AIRISS v4.0 스키마 모듈
API 요청/응답 모델 정의
"""

from .analysis import (
    AnalysisStartRequest,
    AnalysisStartResponse,
    AnalysisStatusResponse,
    AnalysisResultsResponse,
    EmployeeAnalysisResult
)
from pydantic import BaseModel
from typing import Dict, Any

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_info: Dict[str, Any]
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_info": {
                    "username": "user@example.com",
                    "name": "홍길동",
                    "is_admin": False
                }
            }
        }

__all__ = [
    "AnalysisStartRequest",
    "AnalysisStartResponse", 
    "AnalysisStatusResponse",
    "AnalysisResultsResponse",
    "EmployeeAnalysisResult"
]