"""
Health Check and Status Endpoints
"""
from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import get_db
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """Simple health check endpoint for frontend compatibility"""
    return {
        "status": "healthy",
        "service": "AIRISS v4.0",
        "timestamp": datetime.now().isoformat()
    }

@router.get("")
async def health_check_root():
    """Root health endpoint"""
    return await health_check()

@router.get("/status")
async def status_check(db: Session = Depends(get_db)):
    """Detailed status check"""
    try:
        # Check database
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    return {
        "status": "healthy",
        "service": "AIRISS v4.0",
        "database": db_status,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "healthy",
            "database": db_status,
            "websocket": "healthy"
        }
    }