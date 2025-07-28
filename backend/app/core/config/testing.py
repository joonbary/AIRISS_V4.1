"""
Testing Configuration
테스트 환경 설정
"""

from pydantic import SecretStr
from .base import Settings


class TestingSettings(Settings):
    """테스트 환경 설정"""
    
    # Environment
    ENVIRONMENT: str = "testing"
    
    # Debug
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: SecretStr = SecretStr("test-secret-key")
    
    # Database (테스트용 인메모리 DB)
    DATABASE_URL: str = "sqlite:///:memory:"
    DB_ECHO: bool = False
    
    # Server
    RELOAD: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://testserver"]
    
    # Logging
    LOG_LEVEL: str = "ERROR"  # 테스트 중 로그 최소화
    
    # File Upload (테스트용 임시 디렉토리)
    UPLOAD_DIR: str = "/tmp/airiss_test_uploads"
    
    # AI Analysis (테스트에서는 모킹)
    OPENAI_API_KEY: SecretStr = SecretStr("test-api-key")
    
    # Admin User
    FIRST_SUPERUSER: str = "test_admin"
    FIRST_SUPERUSER_PASSWORD: SecretStr = SecretStr("test_password")
    FIRST_SUPERUSER_EMAIL: str = "test@example.com"
    
    # Disable external services
    REDIS_URL: str = None
    CELERY_BROKER_URL: str = None
    SENTRY_DSN: str = None
    
    class Config:
        env_file = ".env.test"