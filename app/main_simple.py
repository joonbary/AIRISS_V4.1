# -*- coding: utf-8 -*-
"""
AIRISS v4.0 Simplified Main Application
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import logging
import os
import sys
from pathlib import Path
import uvicorn
from datetime import datetime
import uuid

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Create required directories
Path("uploads").mkdir(exist_ok=True)
Path("temp_data").mkdir(exist_ok=True)

# In-memory storage for simplicity
jobs = {}
users = {
    "test@okfn.com": {
        "password": "password123",
        "name": "Test User",
        "is_admin": False
    },
    "admin@okfn.com": {
        "password": "admin123",
        "name": "Admin User",
        "is_admin": True
    }
}

@app.get("/")
async def root():
    return {
        "message": "AIRISS v4.0 API Server",
        "status": "running",
        "version": "4.0.0",
        "endpoints": {
            "health": "/api/v1/health",
            "docs": "/docs",
            "upload": "/api/v1/analysis/upload",
            "status": "/api/v1/jobs/{job_id}",
            "download": "/api/v1/download/{token}"
        }
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AIRISS v4.0",
        "database": "sqlite",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Simple login endpoint"""
    logger.info(f"Login attempt - username: {username}, password_length: {len(password)}")
    
    user = users.get(username)
    
    if not user:
        logger.warning(f"User not found: {username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user["password"] != password:
        logger.warning(f"Invalid password for user: {username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Simple token (in production, use JWT)
    token = f"token_{uuid.uuid4().hex}"
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": username,
            "email": username,
            "name": user["name"],
            "is_admin": user["is_admin"]
        }
    }

@app.post("/api/v1/analysis/upload")
async def upload_file(file: UploadFile = File(...)):
    """File upload endpoint"""
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Save file
        file_path = Path("uploads") / f"{job_id}_{file.filename}"
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Store job info
        jobs[job_id] = {
            "job_id": job_id,
            "status": "uploaded",
            "filename": file.filename,
            "progress": 0,
            "file_path": str(file_path)
        }
        
        logger.info(f"File uploaded: {file_path}")
        
        return {
            "job_id": job_id,
            "status": "uploaded",
            "filename": file.filename,
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    job = jobs.get(job_id)
    
    if not job:
        # Create mock job for testing
        job = {
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "filename": "test_file.xlsx"
        }
    
    # Simulate progress
    if job["status"] == "uploaded":
        job["status"] = "processing"
        job["progress"] = 50
    elif job["status"] == "processing":
        job["status"] = "completed"
        job["progress"] = 100
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "filename": job.get("filename", "unknown"),
        "download_url": f"/api/v1/download/{job_id}" if job["status"] == "completed" else None
    }

@app.get("/api/v1/download/{token}")
async def download_result(token: str):
    """Download analysis result"""
    import pandas as pd
    
    try:
        # Create sample Excel file
        data = {
            "사번": ["EMP001", "EMP002", "EMP003", "EMP004", "EMP005"],
            "이름": ["김철수", "이영희", "박민수", "최지현", "정대호"],
            "부서": ["영업팀", "마케팅팀", "개발팀", "인사팀", "재무팀"],
            "평가점수": [85.5, 78.2, 91.3, 82.7, 88.1],
            "등급": ["A", "B+", "S", "A", "A+"],
            "AI 피드백": [
                "뛰어난 팀워크와 리더십을 보여줍니다. 목표 달성 능력이 탁월합니다.",
                "창의적인 아이디어와 실행력이 좋습니다. 시간 관리 개선이 필요합니다.",
                "기술적 전문성이 매우 뛰어나며, 문제 해결 능력이 우수합니다.",
                "팀원들과의 소통이 원활하며, 업무 처리가 정확합니다.",
                "분석력이 뛰어나고 전략적 사고가 가능합니다."
            ]
        }
        
        df = pd.DataFrame(data)
        
        # Save to temp file
        temp_file = Path("temp_data") / f"result_{token}.xlsx"
        df.to_excel(temp_file, index=False)
        
        return FileResponse(
            temp_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"airiss_result_{token[:8]}.xlsx"
        )
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint (simplified)
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    try:
        await websocket.send_json({
            "type": "welcome",
            "message": f"Connected as {client_id}"
        })
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "echo",
                "data": data
            })
    except:
        pass

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8006))
    logger.info(f"Starting AIRISS v4.0 Simplified Server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)