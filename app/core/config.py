import os
from dotenv import load_dotenv, dotenv_values

# .env 파일에서 값을 직접 로드 (시스템 환경 변수보다 우선)
env_values = dotenv_values('.env')

# 시스템 환경 변수와 .env 파일 값을 병합 (.env 우선)
load_dotenv(override=True)

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./airiss.db")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    API_PORT = int(os.getenv("API_PORT", "8003"))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    OPENAI_API_KEY = env_values.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = env_values.get("OPENAI_MODEL") or os.getenv("OPENAI_MODEL", "gpt-4")
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv("FRONTEND_URL", "http://localhost:3001")
    ]

settings = Settings()
