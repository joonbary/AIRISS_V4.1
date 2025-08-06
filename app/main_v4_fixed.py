# -*- coding: utf-8 -*-
"""
AIRISS v4.0 Main Application - Fixed Version
OK Financial Group HR Analysis System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
import sys
import json
import uuid
import asyncio
from pathlib import Path
import uvicorn
from datetime import datetime, timedelta
import pandas as pd
import io

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import get_db, engine
from app.models import Base
from app.services.analysis_service import AnalysisService
from app.core.websocket_manager import ConnectionManager

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

# WebSocket Manager
manager = ConnectionManager()

# Request Models
class AnalysisRequest(BaseModel):
    file_id: str
    sample_size: int = 10
    analysis_mode: str = "hybrid"
    enable_ai_feedback: bool = False
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 1200

# Job storage (in-memory for development)
jobs_storage = {}

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

# WebSocket endpoint
@app.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, client_id: str, user_id: Optional[str] = None):
    """WebSocket 연결 엔드포인트"""
    await manager.connect(websocket, client_id, user_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Successfully connected to AIRISS WebSocket"
        }, client_id)
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                }, client_id)
            
            elif data.get("type") == "subscribe":
                event_type = data.get("event")
                logger.info(f"Client {client_id} subscribed to {event_type}")
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)

# Analysis API
@app.post("/api/v1/analysis/analyze/{file_id}")
async def start_analysis(file_id: str, request: AnalysisRequest):
    """분석 시작"""
    try:
        job_id = str(uuid.uuid4())
        
        # Store job info
        jobs_storage[job_id] = {
            "job_id": job_id,
            "file_id": file_id,
            "status": "processing",
            "progress": 0,
            "total": request.sample_size,
            "processed": 0,
            "created_at": datetime.now(),
            "request": request.dict()
        }
        
        # Start analysis in background
        asyncio.create_task(run_analysis(job_id, file_id, request))
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "분석이 시작되었습니다"
        }
    except Exception as e:
        logger.error(f"Analysis start error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

async def run_analysis(job_id: str, file_id: str, request: AnalysisRequest):
    """백그라운드 분석 실행"""
    try:
        # Send start message
        await manager.broadcast({
            "type": "analysis_started",
            "job_id": job_id,
            "message": "분석을 시작합니다"
        })
        
        # Simulate analysis progress
        for i in range(request.sample_size):
            await asyncio.sleep(0.5)  # Simulate processing time
            
            progress = ((i + 1) / request.sample_size) * 100
            jobs_storage[job_id]["progress"] = progress
            jobs_storage[job_id]["processed"] = i + 1
            
            # Send progress update
            await manager.broadcast({
                "type": "analysis_progress",
                "job_id": job_id,
                "progress": progress,
                "processed": i + 1,
                "total": request.sample_size,
                "current_uid": f"EMP{i+1:03d}"
            })
        
        # Complete analysis
        jobs_storage[job_id]["status"] = "completed"
        jobs_storage[job_id]["progress"] = 100
        jobs_storage[job_id]["average_score"] = 85.5
        
        await manager.broadcast({
            "type": "analysis_completed",
            "job_id": job_id,
            "total_processed": request.sample_size,
            "average_score": 85.5,
            "message": "분석이 완료되었습니다"
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        jobs_storage[job_id]["status"] = "failed"
        jobs_storage[job_id]["error"] = str(e)
        
        await manager.broadcast({
            "type": "analysis_failed",
            "job_id": job_id,
            "error": str(e)
        })

@app.get("/api/v1/analysis/status/{job_id}")
async def get_job_status(job_id: str):
    """작업 상태 조회"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_storage[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job.get("progress", 0),
        "processed": job.get("processed", 0),
        "total": job.get("total", 0),
        "average_score": job.get("average_score"),
        "error": job.get("error")
    }

@app.get("/api/v1/analysis/download/{job_id}/{format}")
async def download_results(job_id: str, format: str):
    """결과 다운로드"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Generate sample data
    data = {
        "UID": [f"EMP{i:03d}" for i in range(1, 11)],
        "Name": ["김철수", "이영희", "박민수", "정미경", "최준호", 
                 "강서연", "조현우", "윤지아", "장민석", "송예진"],
        "Score": [85.5, 78.2, 91.3, 82.7, 88.9, 
                  79.5, 86.2, 90.1, 83.4, 87.6],
        "Grade": ["A", "B+", "S", "A-", "A+", 
                  "B+", "A", "S", "A-", "A"]
    }
    
    df = pd.DataFrame(data)
    
    if format.lower() == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='분석결과')
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=AIRISS_v4_results_{job_id[:8]}.xlsx"
            }
        )
    
    elif format.lower() == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=AIRISS_v4_results_{job_id[:8]}.csv"
            }
        )
    
    elif format.lower() == "json":
        json_data = df.to_json(orient='records', force_ascii=False, indent=2)
        
        return StreamingResponse(
            io.BytesIO(json_data.encode('utf-8')),
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=AIRISS_v4_results_{job_id[:8]}.json"
            }
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

# Import routers
try:
    from app.api.v1.endpoints.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    logger.info("Auth router registered")
except ImportError as e:
    logger.error(f"Failed to import auth router: {e}")

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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8006))
    logger.info(f"Starting AIRISS v4.0 server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)