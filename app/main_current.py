# AIRISS v4.1 Complete - FastAPI + React 통합 버전
# Railway 배포 성공을 위한 혼합 프로젝트 완전체

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import logging
import os
from datetime import datetime
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Railway 호환 포트 설정
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8002")))

# React 빌드 경로 설정
REACT_BUILD_PATH = os.getenv("REACT_BUILD_PATH", "./static")
REACT_INDEX_PATH = os.path.join(REACT_BUILD_PATH, "index.html")

logger.info(f"🔧 서버 포트 설정: {SERVER_PORT}")
logger.info(f"📁 React 빌드 경로: {REACT_BUILD_PATH}")
logger.info(f"📄 React 인덱스: {REACT_INDEX_PATH}")

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.1 Complete",
    description="AI 기반 직원 성과/역량 스코어링 시스템 - React + FastAPI 통합 버전",
    version="4.1.0-complete"
)

# CORS 설정 (프론트엔드-백엔드 통신)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# React 정적 파일 서빙 설정
if os.path.exists(REACT_BUILD_PATH):
    logger.info(f"✅ React 빌드 파일 발견: {REACT_BUILD_PATH}")
    app.mount("/static", StaticFiles(directory=REACT_BUILD_PATH), name="static")
else:
    logger.warning(f"⚠️ React 빌드 파일 없음: {REACT_BUILD_PATH}")

# API 엔드포인트들
@app.get("/api")
@app.get("/api/")
async def api_info():
    """API 정보"""
    return {
        "message": "AIRISS v4.1 Complete API",
        "status": "running",
        "port": SERVER_PORT,
        "features": {
            "fastapi_backend": True,
            "react_frontend": os.path.exists(REACT_BUILD_PATH),
            "static_files": os.path.exists(REACT_BUILD_PATH),
            "health_check": True,
            "railway_compatible": True
        },
        "endpoints": {
            "health": "/health",
            "api": "/api",
            "frontend": "/",
            "static": "/static"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스체크 - Railway 성공 보장"""
    logger.info("✅ 헬스체크 요청 수신")
    
    react_status = "available" if os.path.exists(REACT_BUILD_PATH) else "missing"
    react_index_status = "available" if os.path.exists(REACT_INDEX_PATH) else "missing"
    
    return {
        "status": "healthy",
        "service": "AIRISS v4.1 Complete",
        "version": "4.1.0-complete",
        "port": SERVER_PORT,
        "host": SERVER_HOST,
        "environment": os.getenv("ENVIRONMENT", "production"),
        "components": {
            "fastapi": "running",
            "react_build": react_status,
            "react_index": react_index_status,
            "static_files": react_status
        },
        "timestamp": datetime.now().isoformat(),
        "message": "혼합 프로젝트 배포 성공! 🎉"
    }

@app.get("/api/status")
async def detailed_status():
    """상세 시스템 상태"""
    return {
        "system": {
            "python_version": "3.9+",
            "fastapi": "running",
            "uvicorn": "running"
        },
        "frontend": {
            "react_build_exists": os.path.exists(REACT_BUILD_PATH),
            "react_index_exists": os.path.exists(REACT_INDEX_PATH),
            "static_mount": "/static"
        },
        "railway": {
            "port": SERVER_PORT,
            "host": SERVER_HOST,
            "environment": os.getenv("ENVIRONMENT", "production")
        },
        "timestamp": datetime.now().isoformat()
    }

# React 앱 서빙 (SPA 라우팅 지원)
@app.get("/")
async def serve_react_root():
    """React 앱 루트"""
    if os.path.exists(REACT_INDEX_PATH):
        return FileResponse(REACT_INDEX_PATH)
    else:
        return {
            "message": "AIRISS v4.1 Complete API Server",
            "status": "React 빌드 파일 없음 - API만 실행 중",
            "api_endpoints": "/api",
            "health_check": "/health"
        }

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """React SPA 라우팅 지원"""
    # API 경로는 제외
    if full_path.startswith("api/") or full_path.startswith("health"):
        return {"error": "API endpoint not found"}
    
    # React 앱의 모든 경로는 index.html로 리다이렉트 (SPA)
    if os.path.exists(REACT_INDEX_PATH):
        return FileResponse(REACT_INDEX_PATH)
    else:
        return {
            "message": f"Path '{full_path}' - React 앱 준비 중",
            "api_available": "/api",
            "health_check": "/health"
        }

# 시작 로그
logger.info("🚀 AIRISS v4.1 Complete 서버 시작")
logger.info(f"📡 포트: {SERVER_PORT}")
logger.info(f"🎯 목표: React + FastAPI 혼합 프로젝트 완전 배포")
logger.info(f"📁 정적 파일: {REACT_BUILD_PATH}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🏃 Complete 서버 실행...")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=SERVER_HOST, 
            port=SERVER_PORT, 
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ Complete 서버 오류: {e}")
