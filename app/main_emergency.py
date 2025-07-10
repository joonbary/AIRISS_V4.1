# EMERGENCY MINIMAL main.py for Railway Success
# 최소한의 기능으로 헬스체크 통과 우선

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Railway 호환 포트 설정
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8002")))

logger.info(f"🔧 서버 포트 설정: {SERVER_PORT} (환경변수: PORT={os.getenv('PORT')}, SERVER_PORT={os.getenv('SERVER_PORT')})")

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.1 Emergency",
    description="Railway 배포 성공을 위한 최소 버전",
    version="4.1.0-emergency"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """메인 페이지"""
    return {
        "message": "🚀 AIRISS v4.1 Emergency - Railway 배포 성공!",
        "status": "live",
        "version": "4.1.0-emergency",
        "port": SERVER_PORT,
        "timestamp": datetime.now().isoformat(),
        "next_steps": "모든 기능을 점진적으로 추가 예정"
    }

@app.get("/health")
async def health_check():
    """헬스체크 - Railway 성공 보장"""
    logger.info("✅ 헬스체크 요청 수신")
    return {
        "status": "healthy",
        "service": "AIRISS v4.1 Emergency",
        "version": "4.1.0-emergency",
        "port": SERVER_PORT,
        "host": SERVER_HOST,
        "environment": os.getenv("ENVIRONMENT", "production"),
        "timestamp": datetime.now().isoformat(),
        "message": "Railway 배포 성공! 🎉"
    }

@app.get("/api")
async def api_info():
    """API 정보"""
    return {
        "message": "AIRISS v4.1 Emergency API",
        "status": "running",
        "port": SERVER_PORT,
        "features": {
            "basic_api": True,
            "health_check": True,
            "railway_compatible": True,
            "ready_for_expansion": True
        },
        "timestamp": datetime.now().isoformat()
    }

# 시작 로그
logger.info("🚀 AIRISS v4.1 Emergency 서버 시작")
logger.info(f"📡 포트: {SERVER_PORT}")
logger.info(f"🎯 목표: Railway 배포 성공 후 점진적 기능 추가")

if __name__ == "__main__":
    import uvicorn
    logger.info("🏃 Emergency 서버 실행...")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=SERVER_HOST, 
            port=SERVER_PORT, 
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ Emergency 서버 오류: {e}")
