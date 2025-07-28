# -*- coding: utf-8 -*-
"""
AIRISS v4.0 Main Application - Fixed Version
With proper job tracking and database persistence
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
from app.models.job import Job  # Import Job model
from sqlalchemy.orm import Session

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables (including jobs table)
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
        Job.__table__.create(engine)
        
except Exception as e:
    logger.error(f"Database initialization error: {e}")

# FastAPI app
app = FastAPI(
    title="AIRISS v4.0 API - Fixed",
    description="OK Financial Group HR Analysis System API with Job Tracking",
    version="4.0.1"
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
@app.get("/")
async def root():
    return {
        "message": "AIRISS v4.0 API Server - Fixed Version",
        "status": "running",
        "version": "4.0.1",
        "features": [
            "Persistent job tracking",
            "Database storage",
            "Complete E2E flow"
        ],
        "endpoints": {
            "health": "/api/v1/health",
            "docs": "/docs",
            "auth": "/api/v1/auth/*",
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
        
        # Check jobs table
        job_count = db.query(Job).count()
        db_status = "healthy"
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
        job_count = -1
    
    return {
        "status": "healthy",
        "service": "AIRISS v4.0 - Fixed",
        "database": db_status,
        "jobs_table": "ready" if job_count >= 0 else "error",
        "active_jobs": job_count if job_count >= 0 else None,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "timestamp": datetime.now().isoformat()
    }

# Import routers
try:
    from app.api.v1.endpoints.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    logger.info("Auth router registered")
except ImportError as e:
    logger.error(f"Failed to import auth router: {e}")

# Use the fixed analysis router
try:
    from app.api.v1.endpoints.analysis_fixed import router as analysis_router
    app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
    logger.info("✅ Fixed Analysis router registered")
except ImportError as e:
    logger.error(f"Failed to import fixed analysis router: {e}")
    # Fallback to original if fixed not available
    try:
        from app.api.v1.endpoints.analysis import router as analysis_router
        app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
        logger.info("⚠️ Using original analysis router")
    except ImportError as e2:
        logger.error(f"Failed to import any analysis router: {e2}")

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

# Job listing endpoint
@app.get("/api/v1/jobs")
async def list_all_jobs(db: Session = Depends(get_db)):
    """List all jobs from database"""
    try:
        jobs = db.query(Job).order_by(Job.created_at.desc()).limit(50).all()
        
        return {
            "total_jobs": len(jobs),
            "jobs": [
                {
                    "job_id": job.id,
                    "file_id": job.file_id,
                    "status": job.status,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "error": job.error
                }
                for job in jobs
            ]
        }
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Direct job status endpoint (backup)
@app.get("/api/v1/jobs/{job_id}/status")
async def get_job_status_direct(job_id: str, db: Session = Depends(get_db)):
    """Get job status directly from database"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job.id,
            "file_id": job.file_id,
            "status": job.status,
            "progress": job.progress,
            "start_time": job.start_time.isoformat() if job.start_time else None,
            "end_time": job.end_time.isoformat() if job.end_time else None,
            "error": job.error,
            "created_at": job.created_at.isoformat() if job.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 AIRISS v4.0 Fixed Version Starting...")
    
    # Verify database
    try:
        db = next(get_db())
        job_count = db.query(Job).count()
        logger.info(f"📊 Database ready with {job_count} existing jobs")
    except Exception as e:
        logger.error(f"❌ Database check failed: {e}")
    
    logger.info("✅ Server ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 AIRISS v4.0 shutting down...")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8006))
    
    print(f"""
    🚀 Starting AIRISS v4.0 API Server - Fixed Version
    📍 URL: http://localhost:{port}
    📚 Docs: http://localhost:{port}/docs
    ✨ Features: Persistent Job Tracking
    
    Press Ctrl+C to stop
    """)
    
    uvicorn.run(
        "app.main_fixed:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )