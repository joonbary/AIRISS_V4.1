"""
Production Configuration
운영 환경 설정
"""

from typing import List, Optional
from pydantic import SecretStr, validator
from .base import Settings


class ProductionSettings(Settings):
    """운영 환경 설정"""
    
    # Environment
    ENVIRONMENT: str = "production"
    
    # Debug
    DEBUG: bool = False
    
    # Security (운영 환경에서는 필수)
    SECRET_KEY: SecretStr
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v: SecretStr) -> SecretStr:
        if v.get_secret_value() == "dev-secret-key-change-in-production":
            raise ValueError("Production requires a secure SECRET_KEY")
        return v
    
    # Database
    DB_ECHO: bool = False  # SQL 로깅 비활성화
    
    # Server
    RELOAD: bool = False
    WORKERS: int = 4  # 멀티 워커
    
    # CORS (운영 환경에서는 특정 도메인만 허용)
    BACKEND_CORS_ORIGINS: List[str] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Production requires BACKEND_CORS_ORIGINS to be set")
        return v
    
    # Logging
    LOG_LEVEL: str = "WARNING"
    
    # Admin User (운영 환경에서는 강력한 비밀번호 필수)
    @validator("FIRST_SUPERUSER_PASSWORD", pre=True)
    def validate_admin_password(cls, v: SecretStr) -> SecretStr:
        if v.get_secret_value() == "admin123":
            raise ValueError("Production requires a secure admin password")
        return v
    
    # SSL/TLS
    USE_HTTPS: bool = True
    SSL_CERT_FILE: Optional[str] = None
    SSL_KEY_FILE: Optional[str] = None
    
    # Security Headers
    SECURITY_HEADERS: dict = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'"
    }
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Monitoring (운영 환경에서 활성화)
    ENABLE_METRICS: bool = True
    
    class Config:
        env_file = ".env.production"