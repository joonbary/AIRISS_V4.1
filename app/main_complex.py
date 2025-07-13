# app/main.py
# AIRISS v4.1 향상된 UI/UX 버전 - Railway 호환 포트 수정

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from contextlib import asynccontextmanager
import logging
import os
import uvicorn
from typing import Dict, List
from datetime import datetime
import traceback
import asyncio

# 프로젝트 모듈 import
from app.core.websocket_manager import ConnectionManager

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 전역 설정 - Railway 호환 포트 수정
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8002")))  # ✅ Railway PORT 지원
WS_HOST = os.getenv("WS_HOST", "localhost")

logger.info(f"🔧 서버 포트 설정: {SERVER_PORT} (환경변수: PORT={os.getenv('PORT')}, SERVER_PORT={os.getenv('SERVER_PORT')})")

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

# WebSocket 연결 관리자 인스턴스 생성
manager = ConnectionManager()

# 글로벌 서비스 인스턴스들 (lifespan에서 초기화)
sqlite_service = None
hybrid_analyzer = None

# Lifespan 컨텍스트 매니저
@asynccontextmanager
async def lifespan(app: FastAPI):
    global sqlite_service, hybrid_analyzer
    
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 AIRISS v4.1 Enhanced UI/UX Server Starting")
    logger.info(f"📡 HTTP: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"🏠 Enhanced UI: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"📊 Dashboard: http://{WS_HOST}:{SERVER_PORT}/dashboard")
    logger.info(f"📖 API Documentation: http://{WS_HOST}:{SERVER_PORT}/docs")
    logger.info("=" * 80)
    
    # SQLiteService 초기화
    try:
        logger.info("🗄️ SQLiteService 초기화 시작...")
        from app.db.sqlite_service import SQLiteService
        sqlite_service = SQLiteService()
        await sqlite_service.init_database()
        logger.info("✅ SQLiteService 초기화 완료")
    except Exception as e:
        logger.error(f"❌ SQLiteService 초기화 실패: {e}")
        sqlite_service = None
    
    # Analysis Engine 초기화
    try:
        logger.info("🧠 AIRISS v4.1 하이브리드 분석기 초기화 시작...")
        from app.api.analysis import hybrid_analyzer as ha
        hybrid_analyzer = ha
        logger.info("✅ AIRISS v4.1 하이브리드 분석기 초기화 완료")
    except Exception as e:
        logger.error(f"❌ AIRISS v4.1 하이브리드 분석기 초기화 실패: {e}")
        hybrid_analyzer = None
    
    yield
    
    # Shutdown
    logger.info("🛑 AIRISS v4.1 Enhanced Server Shutting Down")

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.1 Enhanced",
    description="AI-based Resource Intelligence Scoring System - Enhanced UI/UX Edition with Deep Learning",
    version="4.1.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static 파일 제공
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 🏠 향상된 메인 페이지 - 고급 차트 시각화 + AI 인사이트
@app.get("/", response_class=HTMLResponse)
async def enhanced_main_interface(request: Request):
    """AIRISS v4.1 향상된 메인 인터페이스 - 고급 차트 시각화 + AI 인사이트"""
    
    # 현재 상태 확인
    db_status = "정상" if sqlite_service else "오류"
    analysis_status = "정상" if hybrid_analyzer else "오류"
    db_status_class = 'status-good' if db_status == '정상' else 'status-error'
    analysis_status_class = 'status-good' if analysis_status == '정상' else 'status-error'
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "db_status": db_status,
        "analysis_status": analysis_status,
        "db_status_class": db_status_class,
        "analysis_status_class": analysis_status_class,
        "ws_host": WS_HOST,
        "server_port": SERVER_PORT
    })

# 기존 엔드포인트들 유지 (간소화)
@app.get("/api")
async def api_info():
    """API 정보"""
    return {
        "message": "AIRISS v4.1 Enhanced API Server",
        "version": "4.1.0",
        "status": "running",
        "port": SERVER_PORT,
        "description": "OK금융그룹 AI 기반 인재 분석 시스템 - Enhanced UI/UX Edition with Deep Learning",
        "features": {
            "enhanced_ui": True,
            "chart_visualization": True,
            "sqlite_database": sqlite_service is not None,
            "websocket_realtime": True,
            "airiss_analysis": hybrid_analyzer is not None,
            "hybrid_scoring": True,
            "deep_learning": True,
            "bias_detection": True,
            "performance_prediction": True
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy",
        "version": "4.1.0",
        "service": "AIRISS v4.1 Enhanced",
        "port": SERVER_PORT,
        "host": SERVER_HOST,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "fastapi": "running",
            "websocket_manager": "active",
            "connection_count": len(manager.active_connections),
            "sqlite_service": "active" if sqlite_service else "unavailable",
            "hybrid_analyzer": "active" if hybrid_analyzer else "unavailable",
            "enhanced_ui": "active",
            "ai_insights": "enabled"
        }
    }

@app.get("/health/db")
async def health_check_db():
    """데이터베이스 헬스체크"""
    if not sqlite_service:
        return {"status": "unavailable", "error": "SQLiteService가 초기화되지 않았습니다", "timestamp": datetime.now().isoformat()}
    
    try:
        file_list = await sqlite_service.list_files()
        return {"status": "healthy", "database": "SQLite", "files": len(file_list), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/health/analysis")
async def health_check_analysis():
    """분석 엔진 헬스체크"""
    if not hybrid_analyzer:
        return {"status": "unavailable", "error": "AIRISS 하이브리드 분석기가 초기화되지 않았습니다", "timestamp": datetime.now().isoformat()}
    
    try:
        openai_available = getattr(getattr(hybrid_analyzer, 'text_analyzer', None), 'openai_available', False)
        
        return {
            "status": "healthy",
            "analysis_engine": "AIRISS v4.1 Enhanced",
            "framework_dimensions": 8,
            "hybrid_analysis": True,
            "openai_available": openai_available,
            "enhanced_features": True,
            "deep_learning_ready": True,
            "bias_detection": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

# WebSocket 엔드포인트들
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, channels: str = "analysis,alerts"):
    """메인 WebSocket 엔드포인트"""
    logger.info(f"🔌 Enhanced WebSocket connection: {client_id}")
    channel_list = channels.split(",") if channels else []
    
    try:
        await manager.connect(websocket, client_id, channel_list)
        while True:
            message = await websocket.receive_text()
            await manager.handle_client_message(client_id, message)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Enhanced WebSocket {client_id} disconnected")
    except Exception as e:
        logger.error(f"Enhanced WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)

# 개발자 대시보드 (기존 유지)
@app.get("/dashboard", response_class=HTMLResponse)
async def developer_dashboard():
    """개발자용 대시보드"""
    # dashboard.html 파일 읽기
    import os
    dashboard_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
    with open(dashboard_path, "r", encoding="utf-8") as f:
        dashboard_html = f.read()
    
    return HTMLResponse(content=dashboard_html)

# 🔍 검색 페이지 (새로 추가)
@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """AIRISS v4.1 고급 검색 페이지"""
    return templates.TemplateResponse("search.html", {
        "request": request,
        "ws_host": WS_HOST,
        "server_port": SERVER_PORT
    })

# 라우터 등록
logger.info("🔧 Enhanced 라우터 등록...")

try:
    from app.api.upload import router as upload_router
    app.include_router(upload_router)
    logger.info("✅ Upload router registered")
except Exception as e:
    logger.error(f"❌ Upload router error: {e}")

try:
    from app.api.analysis import router as analysis_router, init_services
    # 분석 서비스 초기화
    init_services(sqlite_service, manager)
    app.include_router(analysis_router)
    logger.info("✅ Analysis router registered")
except Exception as e:
    logger.error(f"❌ Analysis router error: {e}")

# 🔍 검색 라우터 등록 (init_search_services 호출 제거)
try:
    from app.api.search import router as search_router
    app.include_router(search_router)
    logger.info("✅ Search router registered (/search)")
except Exception as e:
    logger.error(f"❌ Search router error: {e}")

# 🔍 올바른 테이블명 검색 라우터 등록 (NEW - 패치됨)
try:
    from app.api.search_fixed import router as search_fixed_router
    app.include_router(search_fixed_router)
    logger.info("✅ Search Fixed router registered (/search-fixed)")
except Exception as e:
    logger.error(f"❌ Search Fixed router error: {e}")

# 🔧 FIXED: Employee API 직접 등록 (404 에러 해결)
try:
    from app.api.v1.endpoints.employee import router as employee_router
    app.include_router(employee_router, prefix="/api/v1/employee", tags=["employee"])
    logger.info("✅ Employee router registered directly (/api/v1/employee)")
except Exception as e:
    logger.error(f"❌ Employee router error: {e}")

# 🔧 FIXED: User API 직접 등록 (405 에러 해결)
try:
    from app.api.v1.endpoints.user import router as user_router
    app.include_router(user_router, prefix="/user", tags=["user"])
    logger.info("✅ User router registered directly (/user)")
except Exception as e:
    logger.error(f"❌ User router error: {e}")

# 기존 v1 API 라우터도 시도 (백업)
try:
    from app.api.v1.api import api_router as v1_api_router
    app.include_router(v1_api_router, prefix="/api/v1")
    logger.info("✅ v1 API router registered (/api/v1)")
except Exception as e:
    logger.warning(f"⚠️ v1 API router error (employee already registered): {e}")

# 메인 실행
if __name__ == "__main__":
    import sys
    # 명령줄 인자 처리 (--debug 등의 플래그 무시)
    sys.argv = [arg for arg in sys.argv if not arg.startswith('--')]
    
    logger.info("🚀 Starting AIRISS v4.1 Enhanced UI/UX Server...")
    logger.info(f"🎨 Enhanced UI: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"📊 Advanced Chart Visualization: Radar + Performance Prediction")
    logger.info(f"🧠 Deep Learning Features: Bias Detection + AI Insights")
    logger.info(f"🎯 User Experience: Smart Notifications + Real-time Progress")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=SERVER_HOST, 
            port=SERVER_PORT, 
            log_level="info",
            reload=False,
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ Enhanced 서버 시작 실패: {e}")
        print(f"\n❌ Enhanced 서버 오류: {e}")
