# -*- coding: utf-8 -*-
"""
AIRISS LLM Microservice
OpenAI 기반 HR 분석 전용 마이크로서비스
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import init_db, engine
from sqlalchemy import inspect

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AIRISS LLM Microservice",
    description="AI-powered HR Analysis Service for EHR Integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration for EHR integration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """모든 요청 로깅"""
    start_time = datetime.now()
    
    # 요청 로깅
    logger.info(f"📥 {request.method} {request.url.path}")
    
    # 응답 처리
    response = await call_next(request)
    
    # 처리 시간 계산
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    
    # 처리 시간을 헤더에 추가
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Startup event
@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 초기화"""
    try:
        logger.info("🚀 AIRISS LLM Microservice 시작")
        
        # OpenAI API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logger.info(f"✅ OpenAI API 키 로드됨: {api_key[:20]}...")
        else:
            logger.warning("⚠️ OpenAI API 키가 설정되지 않음")
        
        # 데이터베이스 초기화 (선택사항)
        if os.getenv("USE_DATABASE", "false").lower() == "true":
            init_db()
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"📊 데이터베이스 테이블: {tables}")
        else:
            logger.info("💾 데이터베이스 사용 안 함 (Stateless 모드)")
        
        logger.info("✅ 서비스 초기화 완료")
        
    except Exception as e:
        logger.error(f"❌ 서비스 초기화 실패: {e}")

# Root endpoint
@app.get("/")
async def root():
    """서비스 정보"""
    return {
        "service": "AIRISS LLM Microservice",
        "version": "1.0.0",
        "status": "operational",
        "description": "AI-powered HR Analysis Service",
        "endpoints": {
            "analyze": "/api/v1/llm/analyze",
            "batch": "/api/v1/llm/batch-analyze",
            "health": "/api/v1/llm/health",
            "docs": "/docs"
        },
        "timestamp": datetime.now().isoformat()
    }

# Health check
@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "AIRISS LLM Microservice",
        "timestamp": datetime.now().isoformat()
    }

# API routers
try:
    from app.api.v1.endpoints.llm_simple import router as llm_router
    logger.info("Using simplified LLM router")
except ImportError:
    from app.api.v1.endpoints.llm_analysis import router as llm_router
    logger.info("Using standard LLM router")

# Register LLM analysis endpoints
app.include_router(llm_router, prefix="/api/v1/llm", tags=["LLM Analysis"])
logger.info("📌 LLM Analysis API 등록 완료")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 에러 핸들러"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"경로를 찾을 수 없습니다: {request.url.path}",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """500 에러 핸들러"""
    logger.error(f"Internal Server Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "서버 내부 오류가 발생했습니다",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 서버 시작: http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)