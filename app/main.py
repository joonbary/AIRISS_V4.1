# -*- coding: utf-8 -*-
"""
<<<<<<< HEAD
AIRISS v4.1 Complete - Python 3.13 호환성 강화 버전
SQLAlchemy 문제 발생 시 해당 기능 비활성화하고 핵심 기능은 유지
"""

# === 모듈 경로 문제 해결 (최우선) ===
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가
def fix_module_path():
    """Python 모듈 경로 문제 해결"""
    # 현재 파일 위치: app/main.py
    current_file = Path(__file__).resolve()
    # 프로젝트 루트: app의 상위 디렉토리
    project_root = current_file.parent.parent
    
    # sys.path에 프로젝트 루트 추가 (최우선)
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # PYTHONPATH 환경변수도 설정
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if str(project_root) not in current_pythonpath:
        new_pythonpath = f"{project_root}{os.pathsep}{current_pythonpath}" if current_pythonpath else str(project_root)
        os.environ['PYTHONPATH'] = new_pythonpath
    
    print(f"🔧 프로젝트 루트: {project_root}")
    print(f"🐍 Python 경로 설정 완료")
    return project_root

# 모듈 경로 문제 해결 실행
project_root = fix_module_path()

# 이제 나머지 imports
=======
AIRISS v4.1 Complete - 인코딩 안전성 강화 버전
Railway 배포 성공을 위한 혼합 프로젝트 최적화
Windows/OneDrive 한글·특수문자 경로 대응
"""

>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import logging
<<<<<<< HEAD
from datetime import datetime
=======
import os
import sys
from datetime import datetime
from pathlib import Path
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f

# 인코딩 안전성 유틸리티 (생성한 유틸리티가 있다면 import)
try:
    from app.utils.encoding_safe import EncodingSafeUtils
    encoding_utils = EncodingSafeUtils()
except ImportError:
    # 유틸리티가 없는 경우 기본 함수들 정의
    class BasicEncodingUtils:
        @staticmethod
        def safe_path_join(*args):
            """기본 경로 조합"""
            try:
                path = os.path.join(*args)
                # Windows 경로 정규화
                if os.name == 'nt':
                    path = path.replace('\\', '/')
                return path
            except Exception as e:
                logging.error(f"❌ 경로 조합 오류 (Windows/OneDrive 인코딩 이슈 가능): {e}")
                raise
        
        @staticmethod
        def safe_exists_check(file_path):
            """기본 파일 존재 확인"""
            try:
                if isinstance(file_path, Path):
                    file_path = str(file_path)
                return os.path.exists(os.path.normpath(file_path))
            except Exception as e:
                logging.error(f"❌ 파일 존재 확인 오류 (Windows/OneDrive 인코딩 이슈 가능): {e}")
                return False
        
        @staticmethod
        def get_safe_base_dir():
            """기본 디렉토리 경로"""
            try:
                # 환경변수에서 우선 확인
                if "REACT_BUILD_PATH" in os.environ:
                    react_path = os.environ["REACT_BUILD_PATH"]
                    base_dir = os.path.dirname(react_path) if react_path != "./static" else os.getcwd()
                    return base_dir
                
<<<<<<< HEAD
                # project_root 사용
                return str(project_root)
=======
                # 현재 파일 기반으로 프로젝트 루트 찾기
                current_file = os.path.abspath(__file__)
                current_dir = os.path.dirname(current_file)
                
                # app 폴더에서 한 단계 위로 (프로젝트 루트)
                if os.path.basename(current_dir) == 'app':
                    return os.path.dirname(current_dir)
                
                return current_dir
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
            except Exception as e:
                logging.error(f"❌ 기본 디렉토리 확인 오류: {e}")
                return os.getcwd()
    
    encoding_utils = BasicEncodingUtils()

# 로깅 설정 (상세 로그 + 인코딩 정보)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 인코딩 정보 로깅
try:
    logger.info("🔤 인코딩 환경 정보:")
    logger.info(f"  - 기본 인코딩: {sys.getdefaultencoding()}")
    logger.info(f"  - 파일시스템 인코딩: {sys.getfilesystemencoding()}")
    logger.info(f"  - OS: {os.name} ({sys.platform})")
    if hasattr(sys.stdout, 'encoding'):
        logger.info(f"  - stdout 인코딩: {sys.stdout.encoding}")
<<<<<<< HEAD
    logger.info(f"  - 프로젝트 루트: {project_root}")
    logger.info(f"  - sys.path[0]: {sys.path[0]}")
=======
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
except Exception as e:
    logger.warning(f"⚠️ 인코딩 정보 수집 실패: {e}")

# Railway 호환 포트 설정 (Railway 동적 PORT 우선 사용)
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8002")))

<<<<<<< HEAD
# === 데이터베이스 초기화 (조건부) ===
DATABASE_ENABLED = False
db_info = {}

try:
    logger.info("🔄 데이터베이스 모듈 로드 시도...")
    from app.db.database import create_tables, test_connection, get_database_info
    from app.models.analysis_result import AnalysisResultModel, AnalysisJobModel, AnalysisStatsModel
    
    # 데이터베이스 연결 테스트
    db_info = get_database_info()
    logger.info(f"🗄️ 데이터베이스 정보: {db_info}")
    
    if test_connection():
        logger.info("✅ 데이터베이스 연결 성공")
        create_tables()
        logger.info("✅ 데이터베이스 테이블 생성 완료")
        DATABASE_ENABLED = True
    else:
        logger.error("❌ 데이터베이스 연결 실패")
        
except Exception as e:
    logger.error(f"❌ 데이터베이스 초기화 실패 (Python 3.13 + SQLAlchemy 호환성 문제): {e}")
    logger.warning("⚠️ 데이터베이스 기능을 비활성화하고 핵심 기능만 실행합니다.")
    DATABASE_ENABLED = False

=======
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
# React 빌드 경로 설정 (인코딩 안전)
try:
    # 환경변수에서 우선 확인
    REACT_BUILD_PATH = os.getenv("REACT_BUILD_PATH", "./airiss-v4-frontend/build")
    
    # 절대경로로 변환 (인코딩 안전)
    if not os.path.isabs(REACT_BUILD_PATH):
        base_dir = encoding_utils.get_safe_base_dir()
        REACT_BUILD_PATH = encoding_utils.safe_path_join(base_dir, REACT_BUILD_PATH)
    
    # index.html 경로
    REACT_INDEX_PATH = encoding_utils.safe_path_join(REACT_BUILD_PATH, "index.html")
    
<<<<<<< HEAD
    logger.info(f"🚀 AIRISS v4.1 Complete 시작 (Python 3.13 호환 모드)")
=======
    logger.info(f"🚀 AIRISS v4.1 Complete 시작 (인코딩 안전 모드)")
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
    logger.info(f"🔧 서버 포트: {SERVER_PORT} (Railway PORT: {os.getenv('PORT', 'None')})")
    logger.info(f"🏠 프로젝트 기본 경로: {encoding_utils.get_safe_base_dir()}")
    logger.info(f"📁 React 빌드 경로: {REACT_BUILD_PATH}")
    logger.info(f"📄 React 인덱스 경로: {REACT_INDEX_PATH}")
    
    # 파일 존재 확인 (인코딩 안전)
    react_build_exists = encoding_utils.safe_exists_check(REACT_BUILD_PATH)
    react_index_exists = encoding_utils.safe_exists_check(REACT_INDEX_PATH)
    
    logger.info(f"🔍 React 빌드 존재: {react_build_exists}")
    logger.info(f"🔍 React 인덱스 존재: {react_index_exists}")
<<<<<<< HEAD
    logger.info(f"🗄️ 데이터베이스 활성화: {DATABASE_ENABLED}")
=======
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
    
    if not react_build_exists:
        logger.warning("⚠️ React 빌드 폴더가 없습니다. 정적파일 서빙이 제한됩니다.")
    if not react_index_exists:
        logger.warning("⚠️ React index.html이 없습니다. SPA 라우팅이 제한됩니다.")

except Exception as e:
    logger.error(f"❌ React 경로 설정 오류 (Windows/OneDrive 인코딩 이슈 가능): {e}")
    # Fallback 설정
    REACT_BUILD_PATH = "./airiss-v4-frontend/build"
    REACT_INDEX_PATH = "./airiss-v4-frontend/build/index.html"
    logger.info(f"🔄 Fallback 경로 사용: {REACT_BUILD_PATH}")

# FastAPI 앱 생성
app = FastAPI(
<<<<<<< HEAD
    title="AIRISS v4.1 Complete - Python 3.13 Compatible",
    description="AI 기반 직원 성과/역량 스코어링 시스템 - Python 3.13 호환성 강화",
    version="4.1.0-python313-compatible"
=======
    title="AIRISS v4.1 Complete",
    description="AI 기반 직원 성과/역량 스코어링 시스템 - React + FastAPI 통합 (인코딩 안전)",
    version="4.1.0-complete-encoding-safe"
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
)

# CORS 설정 (프론트엔드-백엔드 통신)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# === API 라우터 등록 (조건부) ===

# 분석 결과 저장 API 라우터 등록 (SQLAlchemy 의존)
if DATABASE_ENABLED:
    try:
        from app.api.analysis_storage import router as storage_router
        app.include_router(storage_router)
        logger.info("✅ 분석 결과 저장 API 라우터 등록 완료")
    except ImportError as e:
        logger.error(f"❌ 분석 결과 저장 API 라우터 등록 실패: {e}")
        DATABASE_ENABLED = False
else:
    logger.warning("⚠️ 데이터베이스 비활성화로 분석 저장 API 건너뜀")

# 업로드 API 라우터 등록 (SQLite 기반이므로 안전)
=======
# === API 라우터 등록 ===

# 업로드 API 라우터 등록
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
try:
    from app.api.upload import router as upload_router
    app.include_router(upload_router)
    logger.info("✅ 업로드 API 라우터 등록 완료")
except ImportError as e:
    logger.error(f"❌ 업로드 API 라우터 등록 실패: {e}")

<<<<<<< HEAD
# 분석 API 라우터 등록 (핵심 기능)
=======
# 분석 API 라우터 등록 (있는 경우)
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
try:
    from app.api.analysis import router as analysis_router
    app.include_router(analysis_router)
    logger.info("✅ 분석 API 라우터 등록 완료")
except ImportError as e:
    logger.warning(f"⚠️ 분석 API 라우터 없음: {e}")

# 검색 API 라우터 등록 (있는 경우)
try:
    from app.api.search import router as search_router
    app.include_router(search_router)
    logger.info("✅ 검색 API 라우터 등록 완료")
except ImportError as e:
    logger.warning(f"⚠️ 검색 API 라우터 없음: {e}")

# WebSocket 라우터 등록 (있는 경우)
try:
    from app.api.websocket import router as websocket_router
    app.include_router(websocket_router)
    logger.info("✅ WebSocket API 라우터 등록 완료")
except ImportError as e:
    logger.warning(f"⚠️ WebSocket API 라우터 없음: {e}")

<<<<<<< HEAD
# 사용자 API 라우터 등록
try:
    from app.api.user import router as user_router
    app.include_router(user_router)
    logger.info("✅ 사용자 API 라우터 등록 완료")
except ImportError as e:
    logger.warning(f"⚠️ 사용자 API 라우터 없음: {e}")

=======
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
# === API 라우트들 (최고 우선순위) ===

@app.get("/health")
async def health_check():
<<<<<<< HEAD
    """단순 헬스체크 - Python 3.13 호환성 정보 포함"""
=======
    """단순 헬스체크 - Railway 최적화 + 인코딩 정보"""
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
    logger.info("✅ 헬스체크 요청 수신")
    
    try:
        # 파일 존재 확인 (인코딩 안전)
        react_build_exists = encoding_utils.safe_exists_check(REACT_BUILD_PATH)
        react_index_exists = encoding_utils.safe_exists_check(REACT_INDEX_PATH)
        
<<<<<<< HEAD
        # 데이터베이스 상태 확인
        db_status = False
        if DATABASE_ENABLED:
            try:
                db_status = test_connection()
            except:
                pass
        
        return {
            "status": "healthy",
            "service": "AIRISS v4.1 Complete - Python 3.13 Compatible",
            "version": "4.1.0-python313-compatible",
=======
        return {
            "status": "healthy",
            "service": "AIRISS v4.1 Complete",
            "version": "4.1.0-complete-encoding-safe",
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
            "timestamp": datetime.now().isoformat(),
            "port": SERVER_PORT,
            "railway_port": os.getenv("PORT", "Not Set"),
            "react_build": react_build_exists,
            "react_index": react_index_exists,
<<<<<<< HEAD
            "database": {
                "enabled": DATABASE_ENABLED,
                "connected": db_status,
                "info": db_info if DATABASE_ENABLED else "disabled"
            },
            "compatibility": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "sqlalchemy_compatible": DATABASE_ENABLED,
                "python313_mode": sys.version_info >= (3, 13)
            },
=======
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
            "encoding": {
                "default": sys.getdefaultencoding(),
                "filesystem": sys.getfilesystemencoding(),
                "platform": sys.platform
            },
            "paths": {
                "react_build": REACT_BUILD_PATH,
                "react_index": REACT_INDEX_PATH,
<<<<<<< HEAD
                "base_dir": encoding_utils.get_safe_base_dir(),
                "project_root": str(project_root)
            },
            "module_path_fixed": True,
            "message": "OK - Python 3.13 호환 모드"
        }
    except Exception as e:
        logger.error(f"❌ 헬스체크 오류: {e}")
        return {
            "status": "error",
            "message": str(e),
            "python313_compatible": True,
            "note": "일부 기능이 비활성화되었을 수 있습니다"
=======
                "base_dir": encoding_utils.get_safe_base_dir()
            },
            "message": "OK - 인코딩 안전 모드"
        }
    except Exception as e:
        logger.error(f"❌ 헬스체크 오류 (인코딩 이슈 가능): {e}")
        return {
            "status": "error",
            "message": str(e),
            "encoding_safe_mode": True,
            "note": "Windows/OneDrive 인코딩 문제 가능성"
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
        }

@app.get("/api")
async def api_info():
<<<<<<< HEAD
    """API 정보 - Python 3.13 호환성 정보 포함"""
=======
    """API 정보 (인코딩 안전)"""
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
    logger.info("📊 API 정보 요청")
    
    try:
        react_build_exists = encoding_utils.safe_exists_check(REACT_BUILD_PATH)
        
<<<<<<< HEAD
        # 데이터베이스 상태 확인
        db_status = False
        if DATABASE_ENABLED:
            try:
                db_status = test_connection()
            except:
                pass
        
        return {
            "message": "AIRISS v4.1 Complete API - Python 3.13 호환 모드",
            "status": "running",
            "version": "4.1.0-python313-compatible",
=======
        return {
            "message": "AIRISS v4.1 Complete API (인코딩 안전)",
            "status": "running",
            "version": "4.1.0-complete-encoding-safe",
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
            "port": SERVER_PORT,
            "railway_port": os.getenv("PORT", "Not Set"),
            "features": {
                "fastapi_backend": True,
                "react_frontend": react_build_exists,
                "static_files": react_build_exists,
                "encoding_safe": True,
<<<<<<< HEAD
                "windows_onedrive_support": True,
                "cloud_storage": DATABASE_ENABLED and db_status,
                "analysis_history": DATABASE_ENABLED,
                "bias_detection": True,
                "python313_compatible": True,
                "module_path_fixed": True
            },
            "database": {
                "enabled": DATABASE_ENABLED,
                "connected": db_status,
                "info": db_info if DATABASE_ENABLED else "disabled"
            },
            "compatibility": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "sqlalchemy_issues": not DATABASE_ENABLED,
                "core_features_available": True
            },
            "paths": {
                "react_build": REACT_BUILD_PATH,
                "base_dir": encoding_utils.get_safe_base_dir(),
                "project_root": str(project_root)
            },
            "api_endpoints": {
                "analysis_storage": "/api/analysis-storage" if DATABASE_ENABLED else "disabled",
                "upload": "/api/upload",
                "analysis": "/api/analysis",
                "search": "/api/search",
                "websocket": "/api/websocket"
=======
                "windows_onedrive_support": True
            },
            "paths": {
                "react_build": REACT_BUILD_PATH,
                "base_dir": encoding_utils.get_safe_base_dir()
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
<<<<<<< HEAD
        logger.error(f"❌ API 정보 오류: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"API 정보 조회 실패: {str(e)}"
=======
        logger.error(f"❌ API 정보 오류 (인코딩 이슈 가능): {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"API 정보 조회 실패 (Windows/OneDrive 인코딩 이슈 가능): {str(e)}"
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
        )

@app.get("/api/status")
async def api_status():
<<<<<<< HEAD
    """API 상태 확인 - Python 3.13 호환성 정보"""
    try:
        react_build_exists = encoding_utils.safe_exists_check(REACT_BUILD_PATH)
        
        # 데이터베이스 상태 확인
        db_status = False
        if DATABASE_ENABLED:
            try:
                db_status = test_connection()
            except:
                pass
        
        return {
            "api_status": "operational",
            "react_build": react_build_exists,
            "database_enabled": DATABASE_ENABLED,
            "database_connected": db_status,
            "port": SERVER_PORT,
            "railway_port": os.getenv("PORT", "Not Set"),
            "encoding_safe": True,
            "module_path_fixed": True,
            "python313_compatible": True,
            "platform": sys.platform,
            "storage_enabled": DATABASE_ENABLED and db_status,
            "project_root": str(project_root),
            "core_features": {
                "file_upload": True,
                "text_analysis": True,
                "quantitative_analysis": True,
                "hybrid_analysis": True,
                "result_storage": DATABASE_ENABLED
            }
        }
    except Exception as e:
        logger.error(f"❌ API 상태 확인 오류: {e}")
        return {
            "api_status": "error",
            "error": str(e),
            "python313_compatible": True,
            "note": "일부 기능이 비활성화되었을 수 있습니다"
        }

@app.get("/api/database/status")
async def database_status():
    """데이터베이스 상태 전용 엔드포인트"""
    if not DATABASE_ENABLED:
        return {
            "database_enabled": False,
            "reason": "SQLAlchemy compatibility issue with Python 3.13",
            "alternative": "Core analysis features are available without database storage",
            "recommendation": "Consider using Python 3.11 or 3.12 for full database functionality"
        }
    
    try:
        db_status = test_connection()
        return {
            "database_enabled": True,
            "connected": db_status,
            "info": db_info,
            "storage_available": True
        }
    except Exception as e:
        return {
            "database_enabled": True,
            "connected": False,
            "error": str(e),
            "storage_available": False
=======
    """API 상태 확인 (인코딩 안전)"""
    try:
        react_build_exists = encoding_utils.safe_exists_check(REACT_BUILD_PATH)
        
        return {
            "api_status": "operational",
            "react_build": react_build_exists,
            "port": SERVER_PORT,
            "railway_port": os.getenv("PORT", "Not Set"),
            "encoding_safe": True,
            "platform": sys.platform
        }
    except Exception as e:
        logger.error(f"❌ API 상태 확인 오류 (인코딩 이슈 가능): {e}")
        return {
            "api_status": "error",
            "error": str(e),
            "note": "Windows/OneDrive 인코딩 문제 가능성"
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
        }

# === 개별 정적파일들 (React 루트 파일들) - 인코딩 안전 ===

def serve_static_file_safe(filename: str, description: str):
    """인코딩 안전한 정적파일 서빙"""
    try:
        file_path = encoding_utils.safe_path_join(REACT_BUILD_PATH, filename)
        
        if encoding_utils.safe_exists_check(file_path):
            logger.info(f"📄 {description} 서빙: {file_path}")
            return FileResponse(file_path)
        else:
            logger.warning(f"⚠️ {description} 없음: {file_path}")
            raise HTTPException(status_code=404, detail=f"{filename} not found")
    
    except Exception as e:
<<<<<<< HEAD
        logger.error(f"❌ {description} 서빙 오류: {e}")
        logger.error(f"파일 경로: {filename}")
        raise HTTPException(
            status_code=500, 
            detail=f"{filename} 서빙 실패: {str(e)}"
=======
        logger.error(f"❌ {description} 서빙 오류 (인코딩 이슈 가능): {e}")
        logger.error(f"파일 경로: {filename}")
        raise HTTPException(
            status_code=500, 
            detail=f"{filename} 서빙 실패 (Windows/OneDrive 인코딩 이슈 가능): {str(e)}"
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
        )

@app.get("/manifest.json")
async def serve_manifest():
    """React manifest.json (인코딩 안전)"""
    return serve_static_file_safe("manifest.json", "manifest.json")

@app.get("/favicon.ico")
async def serve_favicon():
    """React favicon.ico (인코딩 안전)"""
    return serve_static_file_safe("favicon.ico", "favicon.ico")

@app.get("/robots.txt")
async def serve_robots():
    """React robots.txt (인코딩 안전)"""
    return serve_static_file_safe("robots.txt", "robots.txt")

# === React CSS/JS 정적파일들 (인코딩 안전) ===

try:
    react_static_path = encoding_utils.safe_path_join(REACT_BUILD_PATH, "static")
    
    if encoding_utils.safe_exists_check(react_static_path):
        logger.info(f"✅ React CSS/JS 파일들 마운트: {react_static_path}")
        app.mount("/static", StaticFiles(directory=react_static_path), name="react-static")
    else:
        logger.warning(f"⚠️ React static 폴더 없음: {react_static_path}")
        
except Exception as e:
<<<<<<< HEAD
    logger.error(f"❌ React 정적파일 마운트 오류: {e}")
=======
    logger.error(f"❌ React 정적파일 마운트 오류 (인코딩 이슈 가능): {e}")
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
    logger.error(f"React static 경로: {react_static_path if 'react_static_path' in locals() else 'Unknown'}")

# === SPA 라우팅 (가장 낮은 우선순위) - 인코딩 안전 ===

@app.get("/")
async def serve_root():
<<<<<<< HEAD
    logger.info("🏠 루트 경로 접근")
=======
    """루트 경로 - React 앱 (인코딩 안전)"""
    logger.info("🏠 루트 경로 접근")
    
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
    try:
        if encoding_utils.safe_exists_check(REACT_INDEX_PATH):
            logger.info(f"📄 React index.html 서빙: {REACT_INDEX_PATH}")
            return FileResponse(REACT_INDEX_PATH)
        else:
            logger.warning(f"⚠️ React index.html 없음: {REACT_INDEX_PATH}")
<<<<<<< HEAD
            db_status = False
            if DATABASE_ENABLED:
                try:
                    db_status = test_connection()
                except:
                    pass
            return {
                "message": "AIRISS v4.1 Complete API Server - Python 3.13 호환 모드",
                "status": "running",
                "version": "4.1.0-python313-compatible",
                "port": SERVER_PORT,
                "railway_port": os.getenv("PORT", "Not Set"),
                "react_build": False,
                "database_enabled": DATABASE_ENABLED,
                "database_connected": db_status,
                "python313_compatible": True,
                "module_path_fixed": True,
                "project_root": str(project_root),
                "endpoints": {
                    "health": "/health",
                    "api": "/api",
                    "api_status": "/api/status",
                    "database_status": "/api/database/status",
                    "analysis_storage": "/api/analysis-storage" if DATABASE_ENABLED else "disabled"
                },
                "notice": "React 빌드 파일이 없습니다."
            }
    except Exception as e:
        logger.error(f"❌ 루트 경로 서빙 오류: {e}")
        return {
            "error": "Root path serving failed",
            "message": str(e),
            "python313_compatible": True,
            "module_path_fixed": True,
            "project_root": str(project_root),
            "note": "일부 기능이 비활성화되었을 수 있습니다",
            "available_endpoints": ["/health", "/api", "/api/status", "/api/database/status"]
=======
            return {
                "message": "AIRISS v4.1 Complete API Server (인코딩 안전)",
                "status": "running",
                "version": "4.1.0-complete-encoding-safe",
                "port": SERVER_PORT,
                "railway_port": os.getenv("PORT", "Not Set"),
                "react_build": False,
                "encoding_safe": True,
                "endpoints": {
                    "health": "/health",
                    "api": "/api",
                    "api_status": "/api/status"
                },
                "notice": "React 빌드 파일이 없습니다. (Windows/OneDrive 경로 문제 가능)"
            }
    
    except Exception as e:
        logger.error(f"❌ 루트 경로 서빙 오류 (인코딩 이슈 가능): {e}")
        return {
            "error": "Root path serving failed",
            "message": str(e),
            "encoding_safe_mode": True,
            "note": "Windows/OneDrive 인코딩 문제 가능성",
            "available_endpoints": ["/health", "/api", "/api/status"]
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
        }

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """SPA 라우팅 - 모든 React 경로 처리 (인코딩 안전)"""
    logger.info(f"🔗 SPA 라우팅: {full_path}")
    
    try:
        # API 경로는 제외 (이미 위에서 처리됨)
        if full_path.startswith(("api", "health", "static")):
            logger.warning(f"❌ 알 수 없는 API 경로: {full_path}")
            raise HTTPException(status_code=404, detail=f"API endpoint not found: {full_path}")
        
        # React SPA 라우팅: 모든 경로를 index.html로 처리
        if encoding_utils.safe_exists_check(REACT_INDEX_PATH):
            logger.info(f"📄 SPA 라우팅 - React index.html 서빙: {REACT_INDEX_PATH}")
            return FileResponse(REACT_INDEX_PATH)
        else:
            logger.error(f"❌ React index.html 없음 (SPA 라우팅): {REACT_INDEX_PATH}")
            return {
                "error": "React build not found",
                "path": full_path,
<<<<<<< HEAD
                "python313_compatible": True,
                "module_path_fixed": True,
                "project_root": str(project_root),
                "note": "React 빌드 파일이 없습니다",
                "available_endpoints": ["/health", "/api", "/api/status", "/api/database/status"]
=======
                "encoding_safe_mode": True,
                "note": "Windows/OneDrive 인코딩 문제 가능성",
                "available_endpoints": ["/health", "/api", "/api/status"]
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
            }
    
    except HTTPException:
        raise
    except Exception as e:
<<<<<<< HEAD
        logger.error(f"❌ SPA 라우팅 오류: {e}")
=======
        logger.error(f"❌ SPA 라우팅 오류 (인코딩 이슈 가능): {e}")
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
        logger.error(f"요청 경로: {full_path}")
        return {
            "error": "SPA routing failed",
            "path": full_path,
            "message": str(e),
<<<<<<< HEAD
            "python313_compatible": True,
            "module_path_fixed": True,
            "project_root": str(project_root),
            "note": "일부 기능이 비활성화되었을 수 있습니다",
            "available_endpoints": ["/health", "/api", "/api/status", "/api/database/status"]
        }

# 시작 로그
logger.info("🎯 AIRISS v4.1 Complete 서버 준비 완료 (Python 3.13 호환 모드)")
logger.info(f"🚀 API 라우트 등록 완료 - 포트: {SERVER_PORT}")
logger.info("🔤 Windows/OneDrive 한글·특수문자 경로 대응 완료")
logger.info(f"🗄️ 데이터베이스 기능: {'활성화' if DATABASE_ENABLED else '비활성화 (SQLAlchemy 호환성 문제)'}")
logger.info("🔧 Python 모듈 경로 문제 해결 완료")
logger.info("🐍 Python 3.13 호환성 문제 해결 완료")
logger.info("📋 라우트 우선순위:")
logger.info("  1. API 라우트들 (/health, /api/*, /api/database/*)")
logger.info("  2. 개별 정적파일들 (/manifest.json, /favicon.ico, /robots.txt)")
logger.info("  3. CSS/JS 파일들 (/static/*)")
logger.info("  4. SPA 라우팅 (모든 나머지 경로 → React)")
logger.info("💡 활성화된 기능:")
logger.info("  - 파일 업로드 및 분석")
logger.info("  - 텍스트 + 정량 분석")
logger.info("  - 하이브리드 스코어링")
logger.info("  - 편향 탐지")
if DATABASE_ENABLED:
    logger.info("  - 분석 결과 영구 저장 (PostgreSQL)")
    logger.info("  - 분석 이력 조회 및 검색")
else:
    logger.warning("  - 분석 결과 저장: 비활성화 (Python 3.13 + SQLAlchemy 호환성 문제)")

if __name__ == "__main__":
    import uvicorn
    logger.info("🏃 로컬 서버 실행... (Python 3.13 호환 모드)")
    
    try:
        # 직접 실행할 때는 현재 app 인스턴스 사용
        uvicorn.run(
            app,
=======
            "encoding_safe_mode": True,
            "note": "Windows/OneDrive 인코딩 문제 가능성",
            "available_endpoints": ["/health", "/api", "/api/status"]
        }

# 시작 로그
logger.info("🎯 AIRISS v4.1 Complete 서버 준비 완료 (인코딩 안전 모드)")
logger.info(f"🚀 API 라우트 충돌 문제 해결 완료 - 포트: {SERVER_PORT}")
logger.info("🔤 Windows/OneDrive 한글·특수문자 경로 대응 완료")
logger.info("📋 라우트 우선순위:")
logger.info("  1. API 라우트들 (/health, /api/*)")
logger.info("  2. 개별 정적파일들 (/manifest.json, /favicon.ico, /robots.txt)")
logger.info("  3. CSS/JS 파일들 (/static/*)")
logger.info("  4. SPA 라우팅 (모든 나머지 경로 → React)")
logger.info("💡 인코딩 안전 기능:")
logger.info("  - Windows/OneDrive 경로 문제 대응")
logger.info("  - 한글/특수문자 파일명 지원")
logger.info("  - UTF-8 우선 인코딩 처리")

if __name__ == "__main__":
    import uvicorn
    logger.info("🏃 로컬 서버 실행... (인코딩 안전 모드)")
    
    try:
        uvicorn.run(
            "app.main:app",
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
            host=SERVER_HOST, 
            port=SERVER_PORT, 
            log_level="info"
        )
    except Exception as e:
<<<<<<< HEAD
        logger.error(f"❌ 서버 시작 오류: {e}")
=======
        logger.error(f"❌ 서버 시작 오류 (인코딩 이슈 가능): {e}")
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
        logger.error("💡 해결 방법:")
        logger.error("  1. Windows/OneDrive 경로에 한글/특수문자 확인")
        logger.error("  2. 프로젝트를 영어 경로로 이동")
        logger.error("  3. 환경변수 REACT_BUILD_PATH 설정")
<<<<<<< HEAD
        logger.error("  4. 데이터베이스는 비활성화되어도 핵심 기능은 작동")
=======
>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
        raise
