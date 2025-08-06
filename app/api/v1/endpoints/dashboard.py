"""
Dashboard API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.db import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        # Mock data for now
        return {
            "total_files": 15,
            "total_analyses": 48,
            "active_jobs": 2,
            "success_rate": 94.5,
            "average_processing_time": 127.3,  # seconds
            "today_uploads": 3,
            "today_analyses": 8
        }
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
async def get_recent_activities(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent activities"""
    try:
        # Mock recent activities
        activities = []
        base_time = datetime.now()
        
        for i in range(limit):
            time_offset = timedelta(minutes=i*15)
            activities.append({
                "id": f"act_{i}",
                "type": ["upload", "analysis", "download"][i % 3],
                "filename": f"test_file_{i}.xlsx",
                "user": f"user_{i % 3}",
                "timestamp": (base_time - time_offset).isoformat(),
                "status": "completed" if i > 2 else "in_progress"
            })
        
        return {
            "activities": activities,
            "total": len(activities)
        }
    except Exception as e:
        logger.error(f"Recent activities error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_performance_metrics(
    period: str = "week",  # day, week, month
    db: Session = Depends(get_db)
):
    """Get performance metrics"""
    try:
        # Mock performance data
        metrics = {
            "period": period,
            "processing_times": [
                {"date": "2024-01-20", "avg_time": 125.5, "count": 12},
                {"date": "2024-01-21", "avg_time": 132.1, "count": 15},
                {"date": "2024-01-22", "avg_time": 118.7, "count": 10},
                {"date": "2024-01-23", "avg_time": 141.3, "count": 18},
                {"date": "2024-01-24", "avg_time": 129.8, "count": 14},
            ],
            "success_rates": [
                {"date": "2024-01-20", "rate": 95.8},
                {"date": "2024-01-21", "rate": 93.3},
                {"date": "2024-01-22", "rate": 100.0},
                {"date": "2024-01-23", "rate": 88.9},
                {"date": "2024-01-24", "rate": 92.9},
            ],
            "file_types": {
                "xlsx": 75,
                "csv": 20,
                "xls": 5
            }
        }
        
        return metrics
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))