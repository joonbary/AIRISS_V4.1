import os
from dotenv import load_dotenv

# 시스템 환경 변수를 우선 사용, .env는 백업용
# Railway 환경에서는 시스템 환경 변수가 우선
load_dotenv(override=False)

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./airiss.db")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    API_PORT = int(os.getenv("API_PORT", "8003"))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    # Railway 환경 변수를 우선 사용
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv("FRONTEND_URL", "http://localhost:3001")
    ]

settings = Settings()
