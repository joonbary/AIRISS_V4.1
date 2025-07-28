"""
Base Configuration
모든 환경에서 공통으로 사용하는 설정
"""

from pydantic import BaseSettings, PostgresDsn, validator, SecretStr
from typing import Optional, List, Dict, Any, Union
import os
from pathlib import Path


class Settings(BaseSettings):
    """기본 설정"""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Project Info
    PROJECT_NAME: str = "AIRISS v4"
    VERSION: str = "4.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    
    # Security
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: Optional[Union[PostgresDsn, str]] = None
    DB_ECHO: bool = False
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        # Get individual components
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "password")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "airiss_v4")
        
        # Construct URL
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File Upload
    UPLOAD_DIR: Path = None
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".xlsx", ".xls", ".csv"]
    
    @validator("UPLOAD_DIR", pre=True, always=True)
    def set_upload_dir(cls, v: Optional[Path], values: Dict[str, Any]) -> Path:
        if v is None:
            base_dir = values.get("BASE_DIR", Path.cwd())
            return base_dir / "uploads"
        return v
    
    # AI Analysis
    OPENAI_API_KEY: Optional[SecretStr] = None
    DEFAULT_AI_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_MAX_TOKENS: int = 1200
    AI_TIMEOUT: int = 30  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: Path = None
    
    @validator("LOG_DIR", pre=True, always=True)
    def set_log_dir(cls, v: Optional[Path], values: Dict[str, Any]) -> Path:
        if v is None:
            base_dir = values.get("BASE_DIR", Path.cwd())
            return base_dir / "logs"
        return v
    
    # Email (for future use)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # First User (Admin)
    FIRST_SUPERUSER: str = "admin"
    FIRST_SUPERUSER_PASSWORD: SecretStr = SecretStr("admin123")
    FIRST_SUPERUSER_EMAIL: str = "admin@airiss.com"
    
    # Cache
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 300  # 5 minutes
    
    # Job Queue
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = False
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def get_secret_key(self) -> str:
        """Get secret key as string"""
        return self.SECRET_KEY.get_secret_value()
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key as string"""
        if self.OPENAI_API_KEY:
            return self.OPENAI_API_KEY.get_secret_value()
        return None