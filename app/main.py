# -*- coding: utf-8 -*-
"""
AIRISS v4.0 Main Application
OK Financial Group HR Analysis System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import sys
from pathlib import Path
import uvicorn
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import get_db, engine
from app.models import Base
from sqlalchemy.orm import Session

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Verify jobs table exists
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if 'jobs' in inspector.get_table_names():
        logger.info("✅ Jobs table verified")
    else:
        logger.warning("⚠️ Jobs table not found - creating...")
        from app.models.job import Job
        Job.__table__.create(engine)
        
except Exception as e:
    logger.error(f"Database initialization error: {e}")

# FastAPI app
app = FastAPI(
    title="AIRISS v4.0 API - Public Access",
    description="OK Financial Group HR Analysis System API - No Authentication Required",
    version="4.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        db = next(get_db())
        db.execute("SELECT 1")
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
    """Simple health check for frontend"""
    return {"status": "healthy", "service": "AIRISS v4.0"}

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

# Note: Authentication is disabled - all endpoints are public

# Simple upload endpoint
@app.post("/api/v1/analysis/upload")
async def upload_file(file: UploadFile = File(...)):
    """File upload endpoint"""
    import uuid
    
    try:
        # Create uploads directory
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Save file
        file_path = upload_dir / f"{job_id}_{file.filename}"
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File uploaded: {file_path}")
        
        # Return job info
        return {
            "job_id": job_id,
            "status": "uploaded",
            "filename": file.filename,
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Job status endpoint
@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    # For now, return mock completed status
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "filename": "test_file.xlsx",
        "download_url": f"/api/v1/download/{job_id}"
    }

# Download endpoint
@app.get("/api/v1/download/{token}")
async def download_result(token: str):
    """Download analysis result"""
    from fastapi.responses import FileResponse
    import pandas as pd
    from io import BytesIO
    
    try:
        # Create sample Excel file
        data = {
            "UID": ["EMP001", "EMP002", "EMP003"],
            "Name": ["김철수", "이영희", "박민수"],
            "Score": [85.5, 78.2, 91.3],
            "Grade": ["A", "B+", "S"]
        }
        
        df = pd.DataFrame(data)
        
        # Save to temp file
        temp_file = Path("temp_data") / f"result_{token}.xlsx"
        temp_file.parent.mkdir(exist_ok=True)
        
        df.to_excel(temp_file, index=False)
        
        return FileResponse(
            temp_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"airiss_result_{token[:8]}.xlsx"
        )
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analysis jobs endpoint for frontend
@app.get("/analysis/jobs")
async def get_analysis_jobs():
    """Get list of analysis jobs"""
    # Mock data for now
    return {
        "jobs": [
            {
                "job_id": "job1",
                "filename": "test1.xlsx",
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "progress": 100
            },
            {
                "job_id": "job2", 
                "filename": "test2.xlsx",
                "status": "in_progress",
                "created_at": datetime.now().isoformat(),
                "progress": 45
            }
        ],
        "total": 2
    }

# Upload endpoint without /api/v1 prefix for compatibility
@app.post("/api/upload")
async def upload_file_compat(file: UploadFile = File(...)):
    """Compatibility upload endpoint"""
    return await upload_file(file)

# Import additional modules
from datetime import datetime
from fastapi import Form

# Serve React static files in production (after all API routes)
if os.getenv("ENVIRONMENT") == "production" or os.getenv("REACT_BUILD_PATH"):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    react_build_path = os.getenv("REACT_BUILD_PATH", "/app/static")
    if os.path.exists(react_build_path):
        # Mount static files
        app.mount("/static", StaticFiles(directory=react_build_path), name="static")
        
        # Serve index.html for all non-API routes (catch-all must be last)
        @app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            """Serve React app for all non-API routes"""
            # Handle root path
            if full_path == "":
                index_path = os.path.join(react_build_path, "index.html")
                if os.path.exists(index_path):
                    return FileResponse(index_path)
                
            # Skip API routes
            if full_path.startswith("api/") or full_path.startswith("ws") or full_path == "docs" or full_path == "openapi.json" or full_path == "health":
                raise HTTPException(status_code=404, detail="Not found")
            
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
    port = int(os.getenv("PORT", 8006))
    logger.info(f"Starting AIRISS v4.0 server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)