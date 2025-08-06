# -*- coding: utf-8 -*-
"""
AIRISS v4.0 Main Application - Fixed Version v2
OK Financial Group HR Analysis System
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Log environment variables for debugging
env_api_key = os.getenv('OPENAI_API_KEY')
if env_api_key:
    logger.info(f"✅ OPENAI_API_KEY found in environment: {env_api_key[:20]}...")
else:
    logger.warning("⚠️ OPENAI_API_KEY not found in environment variables")

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

# Create FastAPI app
app = FastAPI(
    title="AIRISS v4.0 API",
    description="OK Financial Group HR Analysis System",
    version="4.0.2",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
    "https://localhost:3000",
    "https://ehrv10-production.up.railway.app",
    "*"  # Allow all origins for now
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# CSP headers for Railway
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # CSP header for Railway (ehrv10-production.up.railway.app 도메인 허용)
    csp_header = "frame-ancestors 'self' https://ehrv10-production.up.railway.app http://localhost:* https://localhost:*;"
    response.headers["Content-Security-Policy"] = csp_header
    
    # Log the CSP header for debugging
    logger.info(f"Set CSP: {csp_header}")
    
    return response

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables"""
    try:
        # Create all tables
        init_db()
        logger.info("Database tables initialized successfully")
        
        # List all tables for verification
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Available tables: {tables}")
        
        # Check if employee_results table exists
        if 'employee_results' in tables:
            logger.info("✅ Employee results table verified")
        else:
            logger.warning("⚠️ Employee results table not found")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Continue anyway - don't crash the app

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# API endpoint for root - return JSON for API calls
@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {"message": "AIRISS v4.0 API", "version": "4.0.2"}

# Register all API routers
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
    app.include_router(proxy_router, prefix="/api/v1/proxy/openai", tags=["OpenAI Proxy"])
    logger.info("OpenAI Proxy router registered - Railway 연결 문제 해결용")
except ImportError as e:
    logger.error(f"Failed to import OpenAI proxy router: {e}")

# Static file serving
static_path = os.getenv("REACT_BUILD_PATH", "/app/static")

# Mount static directories
if os.path.exists(static_path):
    # Mount static subdirectory
    static_files_path = os.path.join(static_path, "static")
    if os.path.exists(static_files_path):
        app.mount("/static", StaticFiles(directory=static_files_path), name="static")
        logger.info(f"✅ Mounted /static from: {static_files_path}")
    
    # Mount other static directories directly
    for subdir in ["css", "js", "fonts"]:
        subdir_path = os.path.join(static_path, subdir)
        if os.path.exists(subdir_path):
            app.mount(f"/{subdir}", StaticFiles(directory=subdir_path), name=subdir)
            logger.info(f"✅ Mounted /{subdir} from: {subdir_path}")
    
    logger.info(f"✅ Static files configured from: {static_path}")
else:
    logger.warning(f"⚠️ Static path not found: {static_path}")

# Serve React app - This MUST come after all other routes
@app.get("/")
async def serve_root():
    """Serve React app for root path"""
    if os.path.exists(static_path):
        index_path = os.path.join(static_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {"message": "AIRISS v4.0 API - HR Analysis System"}

# Catch-all for React Router - MUST BE ABSOLUTE LAST
@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """Catch-all route for React SPA"""
    # Skip if it's an API route or WebSocket
    if full_path.startswith("api/") or full_path.startswith("ws"):
        # Return 404 for undefined API routes
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Skip docs and openapi
    if full_path in ["docs", "redoc", "openapi.json"]:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Check if static path exists
    if not os.path.exists(static_path):
        raise HTTPException(status_code=404, detail="Static files not found")
    
    # Try to serve the exact file if it exists
    file_path = os.path.join(static_path, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Otherwise serve index.html for client-side routing
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting AIRISS v4.0 server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)