import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./airiss.db")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    API_PORT = int(os.getenv("API_PORT", "8003"))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv("FRONTEND_URL", "http://localhost:3001")
    ]

settings = Settings()
