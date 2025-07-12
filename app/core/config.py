from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 기존 필드 유지
    PROJECT_NAME: str = "AIRISS v4.0"
    VERSION: str = "4.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./airiss_v4.db"
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3002"]
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: list = [".csv", ".xlsx", ".xls"]
    DEFAULT_SAMPLE_SIZE: int = 25
    MAX_SAMPLE_SIZE: int = 1000
    OPENAI_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_MAX_TOKENS: int = 1200

    # 반드시 추가해야 할 11개 필드 및 기타 주요 .env 변수
    database_type: str = "postgres"
    sqlite_database_url: str = "sqlite:///./airiss_v4.db"
    postgres_database_url: Optional[str] = None
    server_host: str = "0.0.0.0"
    server_port: int = 8003
    react_app_api_url: str = ""
    enable_cloud_storage: bool = False
    analysis_retention_days: int = 365
    react_build_path: str = "./airiss-v4-frontend/build"
    environment: str = "production"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
