import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables explicitly
load_dotenv()

logger = logging.getLogger(__name__)

# Environment variables with explicit loading
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL", "")
SQLITE_DATABASE_URL = os.getenv("SQLITE_DATABASE_URL", "sqlite:///./airiss_v4.db")
DATABASE_URL = os.getenv("DATABASE_URL", "")

logger.info(f"Database Configuration:")
logger.info(f"  - Type: {DATABASE_TYPE}")
logger.info(f"  - SQLite URL: {SQLITE_DATABASE_URL}")
logger.info(f"  - PostgreSQL Available: {'Yes' if POSTGRES_DATABASE_URL else 'No'}")
logger.info(f"  - DATABASE_URL Available: {'Yes' if DATABASE_URL else 'No'}")

# Initialize variables
engine = None
FINAL_DATABASE_URL = ""
DATABASE_CONNECTION_TYPE = "unknown"

def create_postgresql_engine():
    """Create PostgreSQL engine with SQLAlchemy compatibility"""
    global engine, FINAL_DATABASE_URL, DATABASE_CONNECTION_TYPE
    
    try:
        # Determine the best PostgreSQL URL
        if DATABASE_URL and "postgresql" in DATABASE_URL:
            pg_url = DATABASE_URL
            logger.info("Using DATABASE_URL for PostgreSQL")
        elif POSTGRES_DATABASE_URL:
            pg_url = POSTGRES_DATABASE_URL
            logger.info("Using POSTGRES_DATABASE_URL for PostgreSQL")
        else:
            raise Exception("No valid PostgreSQL URL found")
        
        FINAL_DATABASE_URL = pg_url
        
        # Create PostgreSQL engine with minimal settings for compatibility
        engine = create_engine(
            pg_url,
            poolclass=NullPool,  # Recommended for Railway/Neon
            echo=False,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 30,
            }
            # Removed pool_timeout and pool_recycle for compatibility
        )
        
        # Test the connection immediately
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            test_result = result.fetchone()
            if test_result and test_result[0] == 1:
                DATABASE_CONNECTION_TYPE = "postgresql"
                logger.info("PostgreSQL connection successful!")
                return True
            else:
                raise Exception("PostgreSQL connection test failed")
                
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        engine = None
        return False

def create_sqlite_engine():
    """Create SQLite engine as fallback"""
    global engine, FINAL_DATABASE_URL, DATABASE_CONNECTION_TYPE
    
    try:
        FINAL_DATABASE_URL = SQLITE_DATABASE_URL
        DATABASE_CONNECTION_TYPE = "sqlite"
        
        engine = create_engine(
            SQLITE_DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )
        
        # Test SQLite connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            test_result = result.fetchone()
            if test_result and test_result[0] == 1:
                logger.info("SQLite connection successful (fallback)")
                return True
            else:
                raise Exception("SQLite connection test failed")
                
    except Exception as e:
        logger.error(f"SQLite connection failed: {e}")
        return False

# Enhanced connection logic with smart fallback
def initialize_database_connection():
    """Initialize database connection with PostgreSQL priority and SQLite fallback"""
    global engine, FINAL_DATABASE_URL, DATABASE_CONNECTION_TYPE
    
    logger.info("Starting enhanced database connection...")
    
    # Priority 1: Try PostgreSQL if configured
    if DATABASE_TYPE.lower() == "postgres" and (POSTGRES_DATABASE_URL or DATABASE_URL):
        logger.info("Attempting PostgreSQL connection (Priority 1)...")
        if create_postgresql_engine():
            logger.info("Successfully connected to PostgreSQL!")
            return True
        else:
            logger.warning("PostgreSQL failed, trying SQLite fallback...")
    
    # Priority 2: Fallback to SQLite
    logger.info("Attempting SQLite connection (Fallback)...")
    if create_sqlite_engine():
        logger.info("Successfully connected to SQLite!")
        return True
    
    # If both fail
    logger.error("Both PostgreSQL and SQLite connections failed!")
    return False

# Initialize the connection
connection_success = initialize_database_connection()

if not connection_success:
    logger.error("CRITICAL: No database connection available!")
    # Create a dummy engine to prevent crashes
    engine = create_engine("sqlite:///./emergency_fallback.db")
    FINAL_DATABASE_URL = "sqlite:///./emergency_fallback.db"
    DATABASE_CONNECTION_TYPE = "emergency_fallback"

# Session creation
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Enhanced table creation with error handling
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database tables created successfully ({DATABASE_CONNECTION_TYPE})")
        return True
    except Exception as e:
        logger.error(f"Table creation error: {e}")
        return False

# Enhanced connection test
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info(f"Database connection test successful ({DATABASE_CONNECTION_TYPE})")
                return True
            else:
                logger.error(f"Database connection test failed: Invalid result")
                return False
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

# Enhanced database info
def get_database_info():
    return {
        "type": DATABASE_CONNECTION_TYPE,
        "url": FINAL_DATABASE_URL.split("@")[0] + "@***" if "@" in FINAL_DATABASE_URL else FINAL_DATABASE_URL,
        "is_connected": test_connection(),
        "engine_info": {
            "driver": str(engine.url.drivername) if engine else "None",
            "database": str(engine.url.database) if engine and hasattr(engine.url, 'database') else "Unknown",
            "host": str(engine.url.host) if engine and hasattr(engine.url, 'host') else "local"
        },
        "connection_priority": "postgresql" if DATABASE_CONNECTION_TYPE == "postgresql" else "sqlite_fallback",
        "environment": {
            "DATABASE_TYPE": DATABASE_TYPE,
            "POSTGRES_URL_SET": bool(POSTGRES_DATABASE_URL),
            "DATABASE_URL_SET": bool(DATABASE_URL)
        }
    }

# Force PostgreSQL connection (for troubleshooting)
def force_postgresql_connection():
    """Force attempt to connect to PostgreSQL for debugging"""
    logger.info("Forcing PostgreSQL connection attempt...")
    
    if not POSTGRES_DATABASE_URL and not DATABASE_URL:
        return {"success": False, "error": "No PostgreSQL URL configured"}
    
    try:
        result = create_postgresql_engine()
        if result:
            return {"success": True, "message": "PostgreSQL connection forced successfully"}
        else:
            return {"success": False, "error": "PostgreSQL connection failed during force attempt"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Database initialization with comprehensive testing
def initialize_database():
    """Complete database initialization and testing"""
    try:
        logger.info("Starting complete database initialization...")
        
        # Test current connection
        if test_connection():
            logger.info("Database connection verified")
            
            # Create tables
            if create_tables():
                logger.info("Database tables initialized")
                return True
            else:
                logger.error("Table creation failed")
                return False
        else:
            logger.error("Database connection verification failed")
            return False
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

# Router for database management
router = APIRouter()

class ApproveRequest(BaseModel):
    user_id: int
    approve: bool

@router.get("/user/pending")
async def get_pending_users():
    return [
        {"user_id": 1, "email": "test@ex.com", "name": "Test User"},
        {"user_id": 2, "email": "user2@ex.com", "name": "User Two"}
    ]

@router.post("/user/approve")
async def approve_user(request: ApproveRequest):
    if request.approve:
        return {"message": "User approved successfully"}
    else:
        return {"message": "User approval rejected"}

@router.get("/database/status")
async def get_database_status():
    """Enhanced database status endpoint"""
    try:
        db_info = get_database_info()
        return {
            "status": "success",
            "database": db_info,
            "timestamp": "2025-01-23T00:00:00",
            "enhanced": True,
            "connection_type": DATABASE_CONNECTION_TYPE
        }
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/force-postgresql")
async def force_postgresql():
    """Force PostgreSQL connection for debugging"""
    result = force_postgresql_connection()
    if result["success"]:
        return {"message": result["message"], "database_info": get_database_info()}
    else:
        raise HTTPException(status_code=500, detail=result["error"])

# Log final status
logger.info(f"Enhanced Database Module Loaded:")
logger.info(f"  - Connection Type: {DATABASE_CONNECTION_TYPE}")
logger.info(f"  - Engine Available: {engine is not None}")
logger.info(f"  - Tables Ready: {connection_success}")
logger.info(f"  - URL: {FINAL_DATABASE_URL.split('@')[0] + '@***' if '@' in FINAL_DATABASE_URL else FINAL_DATABASE_URL}")
