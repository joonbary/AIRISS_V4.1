# -*- coding: utf-8 -*-
"""
AIRISS v4.0 Main Application
OK Financial Group HR Analysis System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import sys
from pathlib import Path
import uvicorn

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
except Exception as e:
    logger.error(f"Database initialization error: {e}")

# FastAPI app
app = FastAPI(
    title="AIRISS v4.0 API",
    description="OK Financial Group HR Analysis System API",
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
@app.get("/")
async def root():
    return {
        "message": "AIRISS v4.0 API Server",
        "status": "running",
        "version": "4.0.0",
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

# Import routers
try:
    from app.api.v1.endpoints.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    logger.info("Auth router registered")
except ImportError as e:
    logger.error(f"Failed to import auth router: {e}")

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

# Simple auth endpoint for testing
@app.post("/api/v1/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Simple login endpoint for testing"""
    from app.core.security import verify_password, create_access_token
    from app.models.user import User
    from datetime import timedelta
    
    db = next(get_db())
    user = db.query(User).filter(User.email == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is not active")
    
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="User is not approved")
    
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(days=7)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "is_admin": user.is_admin
        }
    }

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

# Import additional modules
from datetime import datetime
from fastapi import Form

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8006))
    logger.info(f"Starting AIRISS v4.0 server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)