"""
AIRISS v4 Main Application (Final)
완전히 리팩터링된 FastAPI 애플리케이션
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.db import init_db, check_connection
from app.api.v1 import api_router
from app.services import UserService

# 로깅 설정
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_format=settings.LOG_FORMAT,
    log_dir=settings.LOG_DIR if settings.ENVIRONMENT != "development" else None,
    use_json=settings.ENVIRONMENT == "production"
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Check database connection
    if check_connection():
        logger.info("Database connection successful")
        # Initialize database tables
        init_db()
        
        # Create admin user if not exists
        from app.db import SessionLocal
        db = SessionLocal()
        try:
            user_service = UserService(db)
            user_service.create_admin_user()
        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")
        finally:
            db.close()
    else:
        logger.error("Failed to connect to database")
    
    # Create directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Middleware
if settings.ENVIRONMENT == "production":
    # Trusted host middleware (보안)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # 실제로는 도메인 지정
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """각 요청에 고유 ID 추가"""
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # 로거에 request_id 추가
    logger = get_logger("request", request_id=request_id)
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    logger.info(f"Request completed: {response.status_code}")
    response.headers["X-Request-ID"] = request_id
    
    return response

# Security headers middleware (운영 환경)
if settings.ENVIRONMENT == "production" and hasattr(settings, "SECURITY_HEADERS"):
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        for header, value in settings.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files (if frontend build exists)
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.ENVIRONMENT != "production" else "Disabled in production"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "connected" if check_connection() else "disconnected"
    
    health_status = {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status
    }
    
    # 추가 상태 정보 (운영 환경에서는 제한)
    if settings.ENVIRONMENT != "production":
        health_status.update({
            "debug": settings.DEBUG if hasattr(settings, "DEBUG") else False,
            "workers": settings.WORKERS,
            "uptime": "N/A"  # TODO: 실제 uptime 추가
        })
    
    return health_status


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Internal server error: {exc}", extra={"request_id": request_id})
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # SSL 설정 (운영 환경)
    ssl_keyfile = None
    ssl_certfile = None
    
    if settings.ENVIRONMENT == "production" and hasattr(settings, "USE_HTTPS") and settings.USE_HTTPS:
        ssl_keyfile = getattr(settings, "SSL_KEY_FILE", None)
        ssl_certfile = getattr(settings, "SSL_CERT_FILE", None)
    
    uvicorn.run(
        "app.main_final:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile
    )