"""
Development Configuration
개발 환경 설정
"""

from typing import List
from pydantic import SecretStr
from .base import Settings


class DevelopmentSettings(Settings):
    """개발 환경 설정"""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Debug
    DEBUG: bool = True
    
    # Security (개발용 기본값)
    SECRET_KEY: SecretStr = SecretStr("dev-secret-key-change-in-production")
    
    # Database
    DB_ECHO: bool = True  # SQL 로깅 활성화
    
    # Server
    RELOAD: bool = True  # 코드 변경시 자동 재시작
    
    # CORS (개발 환경에서 모든 origin 허용)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    
    # Admin User (개발용)
    FIRST_SUPERUSER_PASSWORD: SecretStr = SecretStr("admin123")
    
    # File Upload (개발 환경에서 더 큰 파일 허용)
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    class Config:
        env_file = ".env.development"