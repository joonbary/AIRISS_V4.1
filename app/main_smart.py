# -*- coding: utf-8 -*-
"""
AIRISS v4.1 Complete - SQLAlchemy 조건부 로딩 (Python 3.13 호환)
"""

# === 모듈 경로 문제 해결 (최우선) ===
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가
def fix_module_path():
    """Python 모듈 경로 문제 해결"""
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if str(project_root) not in current_pythonpath:
        new_pythonpath = f"{project_root}{os.pathsep}{current_pythonpath}" if current_pythonpath else str(project_root)
        os.environ['PYTHONPATH'] = new_pythonpath
    
    print(f"🔧 프로젝트 루트: {project_root}")
    print(f"🐍 Python 경로 설정 완료")
    return project_root

# 모듈 경로 문제 해결 실행
project_root = fix_module_path()

# 기본 imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import logging
from datetime import datetime

# 인코딩 안전성 유틸리티
try:
    from app.utils.encoding_safe import EncodingSafeUtils
    encoding_utils = EncodingSafeUtils()
except ImportError:
    class BasicEncodingUtils:
        @staticmethod
        def safe_path_join(*args):
            try:
                path = os.path.join(*args)
                if os.name == 'nt':
                    path = path.replace('\\', '/')
                return path
            except Exception as e:
                logging.error(f"❌ 경로 조합 오류: {e}")
                raise
        
        @staticmethod
        def safe_exists_check(file_path):
            try:
                if isinstance(file_path, Path):
                    file_path = str(file_path)
                return os.path.exists(os.path.normpath(file_path))
            except Exception as e:
                logging.error(f"❌ 파일 존재 확인 오류: {e}")
                return False
        
        @staticmethod
        def get_safe_base_dir():
            return str(project_root)
    
    encoding_utils = BasicEncodingUtils()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 인코딩 정보 로깅
logger.info("🔤 인코딩 환경 정보:")
logger.info(f"  - 기본 인코딩: {sys.getdefaultencoding()}")
logger.info(f"  - 파일시스템 인코딩: {sys.getfilesystemencoding()}")
logger.info(f"  - OS: {os.name} ({sys.platform})")
logger.info(f"  - 프로젝트 루트: {project_root}")

# SQLAlchemy 사용 가능 여부 확인
SQLALCHEMY_AVAILABLE = False
try:
    from app.db.database import create_tables, test_connection, get_database_info
    from app.models.analysis_result import AnalysisResultModel, AnalysisJobModel, AnalysisStatsModel
    
    # 데이터베이스 연결 테스트
    db_info = get_database_info()
    logger.info(f"🗄️ 데이터베이스 정보: {db_info}")
    
    if test_connection():
        logger.info("✅ 데이터베이스 연결 성공")
        create_tables()
        logger.info("✅ 데이터베이스 테이블 생성 완료")
        SQLALCHEMY_AVAILABLE = True
    else:
        logger.error("❌ 데이터베이스 연결 실패")
        
except Exception as e:
    logger.error(f"❌ SQLAlchemy 초기화 실패 (Python 3.13 호환성 문제): {e}")
    logger.warning("⚠️ SQLAlchemy 기능이 비활성화됩니다. 분석 결과 저장 기능이 제한됩니다.")

# 간단한 데이터베이스 테스트 (SQLAlchemy 없이)
def test_simple_db_connection():
    """SQLAlchemy 없이 간단한 DB 연결 테스트"""
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # 네온 DB 연결 정보
        db_config = {
            'host': 'ep-raspy-mountain-a4bgr6ya.us-east-1.aws.neon.tech',
            'database': 'airiss_v4_db',
            'user': 'airiss_v4_db_owner',
            'password': os.getenv('DB_PASSWORD', 'npg_u7NVKxXhpbL8'),
            'port': 5432,
            'sslmode': 'require'
        }
        
        # 연결 테스트
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        logger.info(f"✅ 네온 DB 직접 연결 성공")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ 데이터베이스 직접 연결 실패: {e}")
        return False

# 데이터베이스 연결 상태
db_available = SQLALCHEMY_AVAILABLE or test_simple_db_connection()

# Railway 호환 포트 설정
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8002")))

# React 빌드 경로 설정
try:
    REACT_BUILD_PATH = os.getenv("REACT_BUILD_PATH", "./airiss-v4-frontend/build")
    
    if not os.path.isabs(REACT_BUILD_PATH):
        base_dir = encoding_utils.get_safe_base_dir()
        REACT_BUILD_PATH = encoding_utils.safe_path_join(base_dir, REACT_BUILD_PATH)
    
    REACT_INDEX_PATH = encoding_utils.safe_path_join(REACT_BUILD_PATH, "index.html")
    
    logger.info(f"🚀 AIRISS v4.1 Complete 시작 (조건부 SQLAlchemy)")
    logger.info(f"🔧 서버 포트: {SERVER_PORT}")
    logger.info(f"🏠 프로젝트 기본 경로: {encoding_utils.get_safe_base_dir()}")
    logger.info(f"📁 React 빌드 경로: {REACT_BUILD_PATH}")
    logger.info(f"📄 React 인덱스 경로: {REACT_INDEX_PATH}")
    
    react_build_exists = encoding_utils.safe_exists_check(REACT_BUILD_PATH)
    react_index_exists = encoding_utils.safe_exists_check(REACT_INDEX_PATH)
    
    logger.info(f"🔍 React 빌드 존재: {react_build_exists}")
    logger.info(f"🔍 React 인덱스 존재: {react_index_exists}")
    
except Exception as e:
    logger.error(f"❌ React 경로 설정 오류: {e}")
    REACT_BUILD_PATH = "./airiss-v4-frontend/build"
    REACT_INDEX_PATH = "./airiss-v4-frontend/build/index.html"
    react_build_exists = False
    react_index_exists = False

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.1 Complete (Conditional SQLAlchemy)",
    description="AI 기반 직원 성과/역량 스코어링 시스템 - SQLAlchemy 조건부 로딩",
    version="4.1.0-conditional-sqlalchemy"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === API 라우터 등록 (조건부) ===

# 분석 결과 저장 API 라우터 (SQLAlchemy 사용 가능한 경우에만)
if SQLALCHEMY_AVAILABLE:
    try:
        from app.api.analysis_storage import router as storage_router
        app.include_router(storage_router)
        logger.info("✅ 분석 결과 저장 API 라우터 등록 완료")
    except ImportError as e:
        logger.error(f"❌ 분석 결과 저장 API 라우터 등록 실패: {e}")
else:
    logger.warning("⚠️ SQLAlchemy 비활성화로 인해 분석 결과 저장 API를 사용할 수 없습니다.")

# 업로드 API 라우터
try:
    from app.api.upload import router as upload_router
    app.include_router(upload_router)
    logger.info("✅ 업로드 API 라우터 등록 완료")
except ImportError as e:
    logger.error(f"❌ 업로드 API 라우터 등록 실패: {e}")

# 분석 API 라우터
try:
    from app.api.analysis import router as analysis_router
    app.include_router(analysis_router)
    logger.info("✅ 분석 API 라우터 등록 완료")
except ImportError as e:
    logger.warning(f"⚠️ 분석 API 라우터 없음: {e}")

# 검색 API 라우터
try:
    from app.api.search import router as search_router
    app.include_router(search_router)
    logger.info("✅ 검색 API 라우터 등록 완료")
except ImportError as e:
    logger.warning(f"⚠️ 검색 API 라우터 없음: {e}")

# WebSocket 라우터
try:
    from app.api.websocket import router as websocket_router
    app.include_router(websocket_router)
    logger.info("✅ WebSocket API 라우터 등록 완료")
except ImportError as e:
    logger.warning(f"⚠️ WebSocket API 라우터 없음: {e}")

# 사용자 API 라우터
try:
    from app.api.user import router as user_router
    app.include_router(user_router)
    logger.info("✅ 사용자 API 라우터 등록 완료")
except ImportError as e:
    logger.warning(f"⚠️ 사용자 API 라우터 없음: {e}")

# === API 엔드포인트들 ===

@app.get("/health")
async def health_check():
    """헬스체크 - 조건부 SQLAlchemy"""
    logger.info("✅ 헬스체크 요청 수신")
    
    try:
        react_build_exists = encoding_utils.safe_exists_check(REACT_BUILD_PATH)
        react_index_exists = encoding_utils.safe_exists_check(REACT_INDEX_PATH)
        
        # 데이터베이스 상태 확인
        db_info = {}
        if SQLALCHEMY_AVAILABLE:
            try:
                db_status = test_connection()
                db_info = get_database_info()
            except:
                db_status = False
        else:
            db_status = test_simple_db_connection()
            db_info = {"type": "psycopg2 직접 연결"}
        
        return {
            "status": "healthy",
            "service": "AIRISS v4.1 Complete (Conditional SQLAlchemy)",
            "version": "4.1.0-conditional-sqlalchemy",
            "timestamp": datetime.now().isoformat(),
            "port": SERVER_PORT,
            "react_build": react_build_exists,
            "react_index": react_index_exists,
            "database": {
                "connected": db_status,
                "info": db_info
            },
            "sqlalchemy": {
                "available": SQLALCHEMY_AVAILABLE,
                "reason": "Python 3.13 호환성 문제" if not SQLALCHEMY_AVAILABLE else "정상"
            },
            "encoding": {
                "default": sys.getdefaultencoding(),
                "filesystem": sys.getfilesystemencoding(),
                "platform": sys.platform
            },
            "paths": {
                "react_build": REACT_BUILD_PATH,
                "react_index": REACT_INDEX_PATH,
                "project_root": str(project_root)
            },
            "module_path_fixed": True,
            "message": "OK - 조건부 SQLAlchemy 모드"
        }
    except Exception as e:
        logger.error(f"❌ 헬스체크 오류: {e}")
        return {
            "status": "error",
            "message": str(e),
            "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
            "module_path_fixed": True
        }

@app.get("/api")
async def api_info():
    """API 정보"""
    logger.info("📊 API 정보 요청")
    
    try:
        react_build_exists = encoding_utils.safe_exists_check(REACT_BUILD_PATH)
        
        # 데이터베이스 상태 확인
        if SQLALCHEMY_AVAILABLE:
            try:
                db_status = test_connection()
                db_info = get_database_info()
            except:
                db_status = False
                db_info = {}
        else:
            db_status = test_simple_db_connection()
            db_info = {"type": "psycopg2 직접 연결"}
        
        available_endpoints = {
            "health": "/health",
            "upload": "/api/upload",
            "analysis": "/api/analysis",
            "search": "/api/search",
            "websocket": "/api/websocket"
        }
        
        if SQLALCHEMY_AVAILABLE:
            available_endpoints["analysis_storage"] = "/api/analysis-storage"
        
        return {
            "message": "AIRISS v4.1 Complete API (조건부 SQLAlchemy)",
            "status": "running",
            "version": "4.1.0-conditional-sqlalchemy",
            "port": SERVER_PORT,
            "features": {
                "fastapi_backend": True,
                "react_frontend": react_build_exists,
                "static_files": react_build_exists,
                "encoding_safe": True,
                "windows_onedrive_support": True,
                "cloud_storage": db_status,
                "analysis_history": SQLALCHEMY_AVAILABLE,
                "bias_detection": True,
                "module_path_fixed": True,
                "sqlalchemy_available": SQLALCHEMY_AVAILABLE
            },
            "database": {
                "connected": db_status,
                "info": db_info
            },
            "sqlalchemy": {
                "available": SQLALCHEMY_AVAILABLE,
                "reason": "Python 3.13 호환성 문제" if not SQLALCHEMY_AVAILABLE else "정상"
            },
            "paths": {
                "react_build": REACT_BUILD_PATH,
                "base_dir": encoding_utils.get_safe_base_dir(),
                "project_root": str(project_root)
            },
            "api_endpoints": available_endpoints,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ API 정보 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def api_status():
    """API 상태 확인"""
    try:
        react_build_exists = encoding_utils.safe_exists_check(REACT_BUILD_PATH)
        
        # 데이터베이스 상태 확인
        if SQLALCHEMY_AVAILABLE:
            try:
                db_status = test_connection()
            except:
                db_status = False
        else:
            db_status = test_simple_db_connection()
        
        return {
            "api_status": "operational",
            "react_build": react_build_exists,
            "database_connected": db_status,
            "port": SERVER_PORT,
            "encoding_safe": True,
            "module_path_fixed": True,
            "platform": sys.platform,
            "storage_enabled": SQLALCHEMY_AVAILABLE,
            "project_root": str(project_root),
            "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
            "python_version": sys.version
        }
    except Exception as e:
        logger.error(f"❌ API 상태 확인 오류: {e}")
        return {
            "api_status": "error",
            "error": str(e),
            "module_path_fixed": True,
            "sqlalchemy_available": SQLALCHEMY_AVAILABLE
        }

# === 데이터베이스 정보 API (조건부) ===

@app.get("/api/database/status")
async def database_status():
    """데이터베이스 상태 상세 정보"""
    try:
        if SQLALCHEMY_AVAILABLE:
            try:
                db_connected = test_connection()
                db_info = get_database_info()
                connection_type = "SQLAlchemy"
            except:
                db_connected = False
                db_info = {}
                connection_type = "SQLAlchemy (실패)"
        else:
            db_connected = test_simple_db_connection()
            db_info = {"type": "psycopg2 직접 연결"}
            connection_type = "psycopg2 직접 연결"
        
        return {
            "database_connected": db_connected,
            "connection_type": connection_type,
            "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
            "database_info": db_info,
            "storage_features": {
                "analysis_results": SQLALCHEMY_AVAILABLE,
                "analysis_jobs": SQLALCHEMY_AVAILABLE,
                "statistics": SQLALCHEMY_AVAILABLE,
                "search": SQLALCHEMY_AVAILABLE
            },
            "fallback_mode": not SQLALCHEMY_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 데이터베이스 상태 확인 오류: {e}")
        return {
            "database_connected": False,
            "error": str(e),
            "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
            "fallback_mode": True
        }

# === React 정적 파일 서빙 ===

def serve_static_file_safe(filename: str, description: str):
    """안전한 정적파일 서빙"""
    try:
        file_path = encoding_utils.safe_path_join(REACT_BUILD_PATH, filename)
        
        if encoding_utils.safe_exists_check(file_path):
            logger.info(f"📄 {description} 서빙: {file_path}")
            return FileResponse(file_path)
        else:
            logger.warning(f"⚠️ {description} 없음: {file_path}")
            raise HTTPException(status_code=404, detail=f"{filename} not found")
    
    except Exception as e:
        logger.error(f"❌ {description} 서빙 오류: {e}")
        raise HTTPException(status_code=500, detail=f"{filename} 서빙 실패: {str(e)}")

@app.get("/manifest.json")
async def serve_manifest():
    return serve_static_file_safe("manifest.json", "manifest.json")

@app.get("/favicon.ico")
async def serve_favicon():
    return serve_static_file_safe("favicon.ico", "favicon.ico")

@app.get("/robots.txt")
async def serve_robots():
    return serve_static_file_safe("robots.txt", "robots.txt")

# React CSS/JS 정적파일들
try:
    react_static_path = encoding_utils.safe_path_join(REACT_BUILD_PATH, "static")
    
    if encoding_utils.safe_exists_check(react_static_path):
        logger.info(f"✅ React CSS/JS 파일들 마운트: {react_static_path}")
        app.mount("/static", StaticFiles(directory=react_static_path), name="react-static")
    else:
        logger.warning(f"⚠️ React static 폴더 없음: {react_static_path}")
        
except Exception as e:
    logger.error(f"❌ React 정적파일 마운트 오류: {e}")

# === SPA 라우팅 ===

@app.get("/")
async def serve_root():
    logger.info("🏠 루트 경로 접근")
    try:
        if encoding_utils.safe_exists_check(REACT_INDEX_PATH):
            logger.info(f"📄 React index.html 서빙: {REACT_INDEX_PATH}")
            return FileResponse(REACT_INDEX_PATH)
        else:
            logger.warning(f"⚠️ React index.html 없음: {REACT_INDEX_PATH}")
            return {
                "message": "AIRISS v4.1 Complete API Server (조건부 SQLAlchemy)",
                "status": "running",
                "version": "4.1.0-conditional-sqlalchemy",
                "port": SERVER_PORT,
                "react_build": False,
                "database_connected": db_available,
                "encoding_safe": True,
                "module_path_fixed": True,
                "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
                "project_root": str(project_root),
                "endpoints": {
                    "health": "/health",
                    "api": "/api",
                    "api_status": "/api/status",
                    "database_status": "/api/database/status"
                },
                "notice": "React 빌드 파일이 없습니다."
            }
    except Exception as e:
        logger.error(f"❌ 루트 경로 서빙 오류: {e}")
        return {
            "error": "Root path serving failed",
            "message": str(e),
            "encoding_safe_mode": True,
            "module_path_fixed": True,
            "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
            "project_root": str(project_root),
            "available_endpoints": ["/health", "/api", "/api/status", "/api/database/status"]
        }

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """SPA 라우팅"""
    logger.info(f"🔗 SPA 라우팅: {full_path}")
    
    try:
        # API 경로는 제외
        if full_path.startswith(("api", "health", "static")):
            logger.warning(f"❌ 알 수 없는 API 경로: {full_path}")
            raise HTTPException(status_code=404, detail=f"API endpoint not found: {full_path}")
        
        # React SPA 라우팅
        if encoding_utils.safe_exists_check(REACT_INDEX_PATH):
            logger.info(f"📄 SPA 라우팅 - React index.html 서빙: {REACT_INDEX_PATH}")
            return FileResponse(REACT_INDEX_PATH)
        else:
            logger.error(f"❌ React index.html 없음 (SPA 라우팅): {REACT_INDEX_PATH}")
            return {
                "error": "React build not found",
                "path": full_path,
                "encoding_safe_mode": True,
                "module_path_fixed": True,
                "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
                "project_root": str(project_root),
                "available_endpoints": ["/health", "/api", "/api/status", "/api/database/status"]
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ SPA 라우팅 오류: {e}")
        return {
            "error": "SPA routing failed",
            "path": full_path,
            "message": str(e),
            "encoding_safe_mode": True,
            "module_path_fixed": True,
            "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
            "project_root": str(project_root),
            "available_endpoints": ["/health", "/api", "/api/status", "/api/database/status"]
        }

# 시작 로그
logger.info("🎯 AIRISS v4.1 Complete 서버 준비 완료 (조건부 SQLAlchemy)")
logger.info(f"🚀 서버 포트: {SERVER_PORT}")
logger.info("🔧 Python 모듈 경로 문제 해결 완료")
logger.info(f"🗄️ SQLAlchemy 상태: {'활성화' if SQLALCHEMY_AVAILABLE else '비활성화 (Python 3.13 호환성 문제)'}")
logger.info(f"💾 데이터베이스 연결: {'가능' if db_available else '불가능'}")
logger.info("📋 활성화된 기능:")
logger.info("  - 파일 업로드 및 분석")
logger.info("  - 실시간 WebSocket 통신")
logger.info("  - React 프론트엔드 서빙")
if SQLALCHEMY_AVAILABLE:
    logger.info("  - 분석 결과 영구 저장")
    logger.info("  - 분석 이력 조회 및 검색")
    logger.info("  - 통계 및 성과 분석")
else:
    logger.info("  - 기본 데이터베이스 연결 (psycopg2)")
    logger.warning("  ⚠️ 분석 결과 저장 기능 제한됨")

if __name__ == "__main__":
    import uvicorn
    logger.info("🏃 로컬 서버 실행... (조건부 SQLAlchemy)")
    
    try:
        uvicorn.run(
            app,
            host=SERVER_HOST, 
            port=SERVER_PORT, 
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ 서버 시작 오류: {e}")
        raise
