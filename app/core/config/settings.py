"""
설정 관리 모듈
"""
from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "AIRISS v4.0"
    VERSION: str = "4.0.0"
    DATABASE_TYPE: str = "postgres"
    DATABASE_URL: Optional[str] = None
    SQLITE_DATABASE_URL: str = "sqlite:///./airiss_v4.db"
    POSTGRES_DATABASE_URL: str = ""
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8003
    REACT_APP_API_URL: str = ""
    ENABLE_CLOUD_STORAGE: bool = False
    ANALYSIS_RETENTION_DAYS: int = 365
    REACT_BUILD_PATH: str = "./airiss-v4-frontend/build"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    # 필요시 기타 대문자 환경변수 필드 추가

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }

settings = Settings()