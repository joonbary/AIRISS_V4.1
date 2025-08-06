"""
Database Configuration
PostgreSQL 전용 데이터베이스 설정
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
import logging

logger = logging.getLogger(__name__)

# Railway 환경에서는 dotenv를 사용하지 않음 (환경 변수 직접 사용)
# 로컬 개발에서만 .env 파일 로드
if not os.getenv("RAILWAY_ENVIRONMENT"):
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        logger.info("📂 Loaded .env file for local development")
    except ImportError:
        pass

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# URL 정리 - 줄바꿈과 공백 제거
if DATABASE_URL:
    # 줄바꿈, 탭, 여러 공백을 제거
    DATABASE_URL = DATABASE_URL.strip().replace('\n', '').replace('\r', '').replace('\t', '')
    # 연속된 공백을 제거
    import re
    DATABASE_URL = re.sub(r'\s+', '', DATABASE_URL)
    logger.info("🧹 Cleaned DATABASE_URL of any whitespace")

# 디버깅을 위한 상세 로깅
logger.info(f"🔧 Environment: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Local'}")
logger.info(f"🔧 DATABASE_URL exists: {bool(DATABASE_URL)}")
if DATABASE_URL:
    # URL 타입과 길이 확인
    logger.info(f"🔧 DATABASE_URL length: {len(DATABASE_URL)} characters")
    
    # 호스트 부분 추출하여 확인
    if "@" in DATABASE_URL and "/" in DATABASE_URL:
        try:
            host_part = DATABASE_URL.split("@")[1].split("/")[0]
            logger.info(f"🔧 Host: {host_part}")
            # 호스트에 공백이 있는지 확인
            if " " in host_part or "\t" in host_part or "\n" in host_part:
                logger.error("❌ Host contains whitespace characters!")
                logger.error(f"   Raw host: {repr(host_part)}")
        except:
            pass
    
    # URL 시작 부분만 로깅 (보안상 전체는 로깅하지 않음)
    if DATABASE_URL.startswith("postgresql://"):
        logger.info(f"🔧 DATABASE_URL type: PostgreSQL")
    elif DATABASE_URL.startswith("postgres://"):
        logger.info(f"🔧 DATABASE_URL type: Postgres (will convert)")
    elif DATABASE_URL.startswith("sqlite"):
        logger.info(f"🔧 DATABASE_URL type: SQLite")
    else:
        logger.warning(f"🔧 DATABASE_URL type: Unknown - {DATABASE_URL[:10]}...")
else:
    logger.warning("⚠️ DATABASE_URL not found in environment")
    DATABASE_URL = "sqlite:///./airiss.db"

# Validate DATABASE_URL is not empty
if not DATABASE_URL or DATABASE_URL.strip() == "":
    logger.warning("⚠️ DATABASE_URL is empty, using SQLite default")
    DATABASE_URL = "sqlite:///./airiss.db"
else:
    # Handle postgres:// to postgresql:// conversion for compatibility
    if DATABASE_URL.startswith("postgres://"):
        logger.info("🔄 Converting postgres:// to postgresql:// for SQLAlchemy compatibility")
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Railway/Neon 특별 처리 - 쿼리 파라미터 확인
    if "postgresql://" in DATABASE_URL and "?" not in DATABASE_URL:
        # SSL 모드가 없으면 추가 (Neon은 SSL 필수)
        if "sslmode=" not in DATABASE_URL:
            DATABASE_URL += "?sslmode=require"
            logger.info("🔒 Added sslmode=require for Neon compatibility")

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=False  # Set to True for SQL debugging
    )
    logger.info(f"Using SQLite database: {DATABASE_URL}")
else:
    # PostgreSQL settings
    try:
        logger.info(f"🔗 Attempting to connect to PostgreSQL...")
        logger.info(f"🔗 URL length: {len(DATABASE_URL)} characters")
        
        # URL 유효성 검사
        if not DATABASE_URL.startswith(("postgresql://", "postgres://")):
            raise ValueError(f"Invalid PostgreSQL URL format. Must start with postgresql:// or postgres://")
        
        # SQLAlchemy 엔진 생성
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_timeout=30,  # 연결 풀 타임아웃
            echo=False  # Set to True for SQL debugging
        )
        
        # 연결 테스트
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"✅ PostgreSQL connection successful!")
            logger.info(f"✅ Test query result: {result.scalar()}")
        
        logger.info(f"✅ Using PostgreSQL database")
        
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"❌ Failed to create PostgreSQL engine")
        logger.error(f"   Error type: {error_type}")
        logger.error(f"   Error message: {str(e)}")
        
        # URL 형식 문제인지 확인
        if "Could not parse" in str(e) or "Invalid" in str(e):
            logger.error("🔥 DATABASE_URL parsing failed!")
            logger.error("   Possible causes:")
            logger.error("   1. Missing or malformed DATABASE_URL in Railway")
            logger.error("   2. Special characters in password not URL-encoded")
            logger.error("   3. Incorrect PostgreSQL URL format")
            logger.error("   Expected format: postgresql://user:password@host:port/database")
        
        logger.warning("🔄 Falling back to SQLite database")
        DATABASE_URL = "sqlite:///./airiss.db"
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    Usage in FastAPI:
    
    @app.get("/items")
    def read_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from app.models import User, File, Job, AnalysisResult
    from app.models.employee import EmployeeResult
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def check_connection():
    """Check database connection"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False