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
    
    # OpenAI API 키 로드 (여러 소스에서 시도)
    OPENAI_API_KEY = None
    
    # 1. 시스템 환경 변수에서 시도
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # 2. 대체 환경 변수 이름들 시도
    if not OPENAI_API_KEY:
        alternative_keys = ["OPENAI_KEY", "OPEN_AI_KEY", "OPEN_AI_API_KEY"]
        for key_name in alternative_keys:
            OPENAI_API_KEY = os.getenv(key_name)
            if OPENAI_API_KEY:
                break
    
    # 3. .env 파일에서 시도
    if not OPENAI_API_KEY:
        from pathlib import Path
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('OPENAI_API_KEY=') or line.startswith('OPENAI_KEY='):
                        OPENAI_API_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                        if OPENAI_API_KEY:
                            break
    
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
        logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. Railway Variables에서 설정해주세요.")
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv("FRONTEND_URL", "http://localhost:3001")
    ]

settings = Settings()
