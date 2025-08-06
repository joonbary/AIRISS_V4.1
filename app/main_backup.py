# -*- coding: utf-8 -*-
"""
AIRISS v4.0 Main Application
OK Financial Group HR Analysis System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import sys
import subprocess
from pathlib import Path
import uvicorn
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Log environment variables for debugging
logger = logging.getLogger(__name__)
env_api_key = os.getenv('OPENAI_API_KEY')
if env_api_key:
    logger.info(f"✅ OPENAI_API_KEY found in environment: {env_api_key[:20]}...")
else:
    logger.warning("⚠️ OPENAI_API_KEY not found in environment variables")

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import get_db, engine, init_db
from app.models import Base
from sqlalchemy.orm import Session

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to install OpenAI if not available
try:
    import openai
    logger.info(f"✅ OpenAI already installed: {openai.__version__}")
except ImportError:
    logger.warning("⚠️ OpenAI not found, attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai==1.54.5"])
        import openai
        logger.info(f"✅ OpenAI installed successfully: {openai.__version__}")
    except Exception as e:
        logger.error(f"❌ Failed to install OpenAI: {e}")

# Initialize database tables
try:
    init_db()
    logger.info("Database tables initialized successfully")
    
    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Available tables: {tables}")
    
    if 'employee_results' in tables:
        logger.info("✅ Employee results table verified")
    else:
        logger.warning("⚠️ Employee results table not found")
        
except Exception as e:
    logger.error(f"Database initialization error: {e}")

# FastAPI app
app = FastAPI(
    title="AIRISS v4.0 API - Public Access",
    description="OK Financial Group HR Analysis System API - No Authentication Required",
    version="4.0.0"
)

# CORS middleware
# 환경 변수에서 허용할 도메인 가져오기
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
if cors_origins == ["*"]:
    # 개발 환경에서는 모든 도메인 허용
    cors_origins = ["*"]
else:
    # 프로덕션에서는 특정 도메인만 허용
    cors_origins = [origin.strip() for origin in cors_origins]
    # 로컬 개발도 허용
    cors_origins.extend([
        "http://localhost:8080", 
        "http://localhost:3000",
        "https://web-production-4066.up.railway.app",
        "https://ehrv10-production.up.railway.app"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# X-Frame-Options를 제거하여 iframe 허용
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RemoveXFrameOptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 디버깅용 로그 (Railway에서는 X-Forwarded-* 헤더 사용)
        origin = request.headers.get('origin') or request.headers.get('x-forwarded-host', 'Unknown')
        referer = request.headers.get('referer', 'Unknown')
        
        if origin != 'Unknown' or referer != 'Unknown':
            logger.debug(f"Request from: {referer}, Origin: {origin}")
        
        # X-Frame-Options 헤더 제거
        if "X-Frame-Options" in response.headers:
            del response.headers["X-Frame-Options"]
            logger.info("Removed X-Frame-Options header")
            
        # Content Security Policy 설정
        allowed_origin = os.getenv("CORS_ORIGINS", "").split(",")[0].strip()
        if allowed_origin and allowed_origin != "*":
            csp = f"frame-ancestors 'self' {allowed_origin} http://localhost:* https://localhost:*;"
            response.headers["Content-Security-Policy"] = csp
            logger.info(f"Set CSP: {csp}")
        
        return response

app.add_middleware(RemoveXFrameOptionsMiddleware)


# API Routes
@app.get("/api")
async def api_root():
    return {
        "message": "AIRISS v4.0 API Server - Public Access",
        "status": "running",
        "version": "4.0.0",
        "authentication": "disabled",
        "endpoints": {
            "health": "/api/v1/health",
            "docs": "/docs",
            "analysis": "/api/v1/analysis/*",
            "files": "/api/v1/files/*"
        }
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.commit()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy",
        "service": "AIRISS v4.0",
        "database": db_status,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "timestamp": datetime.now().isoformat()
    }

# Additional health endpoint for compatibility
@app.get("/health")
async def simple_health():
    """Simple health check for Railway and frontend"""
    return {"status": "ok"}

# Railway health check endpoint
@app.get("/healthz")
async def healthz():
    """Railway health check endpoint"""
    return {"status": "ok"}

# Note: Auth router removed - authentication is disabled

try:
    from app.api.v1.endpoints.analysis import router as analysis_router
    app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
    logger.info("Analysis router registered")
except ImportError as e:
    logger.error(f"Failed to import analysis router: {e}")

try:
    from app.api.v1.endpoints.files import router as files_router
    app.include_router(files_router, prefix="/api/v1/files", tags=["Files"])
    logger.info("Files router registered")
except ImportError as e:
    logger.error(f"Failed to import files router: {e}")

try:
    from app.api.v1.endpoints.upload import router as upload_router
    app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
    logger.info("Upload router registered")
except ImportError as e:
    logger.error(f"Failed to import upload router: {e}")

try:
    from app.api.v1.endpoints.websocket import router as websocket_router
    app.include_router(websocket_router, tags=["WebSocket"])
    logger.info("WebSocket router registered")
except ImportError as e:
    logger.error(f"Failed to import websocket router: {e}")

try:
    from app.api.v1.endpoints.health import router as health_router
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])
    logger.info("Health router registered")
except ImportError as e:
    logger.error(f"Failed to import health router: {e}")

try:
    from app.api.v1.endpoints.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
    logger.info("Dashboard router registered")
except ImportError as e:
    logger.error(f"Failed to import dashboard router: {e}")

# v4.2 Employee AI Analysis endpoints
try:
    from app.api.v1.endpoints.employees import router as employees_router
    app.include_router(employees_router, prefix="/api/v1/employees", tags=["Employees"])
    logger.info("Employees router registered - v4.2 AI Dashboard")
except ImportError as e:
    logger.error(f"Failed to import employees router: {e}")

# Opinion Analysis endpoints
try:
    from app.api.v1.endpoints.analysis_opinion import router as opinion_router
    app.include_router(opinion_router, prefix="/api/v1/analysis", tags=["Opinion Analysis"])
    logger.info("Opinion Analysis router registered")
except ImportError as e:
    logger.error(f"Failed to import opinion analysis router: {e}")

# Configuration endpoints
try:
    from app.api.v1.endpoints.config import router as config_router
    app.include_router(config_router, prefix="/api/v1/config", tags=["Configuration"])
    logger.info("Configuration router registered")
except ImportError as e:
    logger.error(f"Failed to import config router: {e}")

# OpenAI Proxy endpoints (Railway 환경용)
try:
    from app.api.v1.endpoints.openai_proxy import router as proxy_router
    app.include_router(proxy_router, prefix="/api/v1", tags=["OpenAI Proxy"])
    logger.info("OpenAI Proxy router registered - Railway 연결 문제 해결용")
except ImportError as e:
    logger.error(f"Failed to import OpenAI proxy router: {e}")

# Note: Authentication is disabled - all endpoints are public


# Serve React static files in production (after all API routes)
if os.getenv("ENVIRONMENT") == "production" or os.getenv("REACT_BUILD_PATH"):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    react_build_path = os.getenv("REACT_BUILD_PATH", "/app/airiss-v4-frontend/build")
    if os.path.exists(react_build_path):
        # Mount static files from React build
        static_path = os.path.join(react_build_path, "static")
        if os.path.exists(static_path):
            app.mount("/static", StaticFiles(directory=static_path), name="static")
        
        # Serve index.html for all non-API routes (catch-all must be last)
        @app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            """Serve React app for all non-API routes"""
            # Handle root path
            if full_path == "":
                index_path = os.path.join(react_build_path, "index.html")
                if os.path.exists(index_path):
                    return FileResponse(index_path)
                
            # Skip API routes - let them be handled by FastAPI router
            if full_path.startswith("api/") or full_path.startswith("ws") or full_path == "docs" or full_path == "openapi.json" or full_path == "health":
                # Return None to let FastAPI handle these routes
                return None
            
            # Check if it's a static file
            static_file_path = os.path.join(react_build_path, full_path)
            if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
                return FileResponse(static_file_path)
            
            # Serve index.html for React routing
            index_path = os.path.join(react_build_path, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            else:
                raise HTTPException(status_code=404, detail="React app not found")
        
        logger.info(f"✅ Serving React static files from: {react_build_path}")
    else:
        logger.warning(f"⚠️ React build path not found: {react_build_path}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting AIRISS v4.0 server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)