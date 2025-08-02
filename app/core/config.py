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
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1500"))
    
    # API 키 유효성 로깅 (보안을 위해 일부만 표시)
    if OPENAI_API_KEY:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"✅ OpenAI API 키 로드됨: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 14 else '****'}")
    else:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. Railway Variables 또는 .env 파일에 설정해주세요.")
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv("FRONTEND_URL", "http://localhost:3001")
    ]

settings = Settings()
