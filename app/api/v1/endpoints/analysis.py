# app/api/v1/endpoints/analysis.py
"""
AIRISS v4.0 분석 API 엔드포인트
실시간 WebSocket 통합
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io
import logging

from app.core.websocket_manager import ConnectionManager, manager
from app.services.analysis_service_fixed import AnalysisServiceFixed as AnalysisService
from app.exceptions import (
    AnalysisError,
    FileProcessingError,
    ValidationError,
    ResourceNotFoundError,
    InternalServiceError
)

router = APIRouter()

# 분석 요청 모델
class AnalysisRequest(BaseModel):
    sample_size: int = 10
    analysis_mode: str = "hybrid"
    enable_ai_feedback: bool = False
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 1200

# 의존성 주입을 위한 함수
def get_ws_manager():
    """WebSocket 매니저 인스턴스 반환"""
    return manager

# 싱글톤 분석 서비스 인스턴스
_analysis_service = None

def get_analysis_service(ws_manager: ConnectionManager = Depends(get_ws_manager)):
    """분석 서비스 싱글톤 인스턴스 반환"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService(ws_manager)
    return _analysis_service

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    service: AnalysisService = Depends(get_analysis_service)
):
    """파일 업로드 엔드포인트"""
    logger = logging.getLogger(__name__)
    
    try:
        contents = await file.read()
        result = await service.upload_file(contents, file.filename)
        return result
        
    except ValidationError as e:
        logger.error(f"ValidationError in upload: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except FileProcessingError as e:
        logger.error(f"FileProcessingError in upload: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ResourceNotFoundError as e:
        logger.error(f"ResourceNotFoundError in upload: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except AnalysisError as e:
        logger.error(f"AnalysisError in upload: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/analyze/{file_id}")
async def start_analysis(
    file_id: str,
    request: AnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service)
):
    """분석 시작 엔드포인트 - JSON body로 파라미터 받기"""
    logger = logging.getLogger(__name__)
    
    try:
        # [DEBUG] 분석 트리거 API 검증
        logger.info("=" * 60)
        logger.info("[API] 분석 요청 수신")
        logger.info(f"[API] URL path file_id: {file_id}")
        logger.info(f"[API] Request body: {request.dict()}")
        
        # file_id가 request body에도 있다면 1:1 일치 확인
        if hasattr(request, 'file_id') and request.file_id:
            if file_id != request.file_id:
                logger.error(f"[ERROR] file_id 불일치! URL: {file_id}, Body: {request.file_id}")
                raise HTTPException(status_code=400, detail="file_id가 일치하지 않습니다")
        
        logger.info(f"[API] 분석 서비스로 전달할 file_id: {file_id}")
        logger.info("=" * 60)
        
        job_id = await service.start_analysis(
            file_id=file_id,
            sample_size=request.sample_size,
            analysis_mode=request.analysis_mode,
            enable_ai_feedback=request.enable_ai_feedback,
            openai_api_key=request.openai_api_key,
            openai_model=request.openai_model,
            max_tokens=request.max_tokens
        )
        return {"job_id": job_id, "status": "started", "message": "분석이 시작되었습니다"}
        
    except ResourceNotFoundError as e:
        logger.error(f"ResourceNotFoundError in analyze: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ValidationError as e:
        logger.error(f"ValidationError in analyze: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except AnalysisError as e:
        logger.error(f"AnalysisError in analyze: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{job_id}")
async def get_job_status(
    job_id: str,
    service: AnalysisService = Depends(get_analysis_service)
):
    """작업 상태 조회"""
    try:
        status = service.get_job_status(job_id)
        if status is None:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in get_job_status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/results/{job_id}")
async def get_results(
    job_id: str,
    service: AnalysisService = Depends(get_analysis_service)
):
    """분석 결과 조회"""
    df = await service.get_analysis_results(job_id)
    if df is None:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다")
    
    return df.to_dict(orient="records")

@router.get("/check-results/{job_id}")
async def check_results_availability(
    job_id: str,
    service: AnalysisService = Depends(get_analysis_service)
):
    """분석 결과 파일 존재 여부 확인"""
    try:
        # 작업 상태 확인
        job_status = service.get_job_status(job_id)
        if not job_status:
            return {"available": False, "reason": "작업을 찾을 수 없습니다"}
        
        if job_status.get('status') != 'completed':
            return {"available": False, "reason": "분석이 완료되지 않았습니다"}
        
        # 결과 데이터 확인
        df = await service.get_analysis_results(job_id)
        if df is None or df.empty:
            return {"available": False, "reason": "분석 결과가 없습니다"}
        
        # 각 형식별 파일 생성 가능 여부 확인
        formats_available = {}
        for format_type in ["excel", "csv", "json"]:
            try:
                test_data = await service.export_results(job_id, format_type)
                formats_available[format_type] = test_data is not None
            except:
                formats_available[format_type] = False
        
        return {
            "available": True,
            "job_id": job_id,
            "status": job_status.get('status'),
            "formats": formats_available,
            "record_count": len(df)
        }
    except Exception as e:
        return {"available": False, "reason": str(e)}

@router.get("/download/{job_id}/{format}")
async def download_results(
    job_id: str,
    format: str,
    service: AnalysisService = Depends(get_analysis_service)
):
    """결과 다운로드"""
    data = await service.export_results(job_id, format)
    if data is None:
        raise HTTPException(status_code=404, detail="다운로드할 데이터가 없습니다")
    
    if format.lower() == "excel":
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=AIRISS_v4_results_{job_id}.xlsx"
            }
        )
    elif format.lower() == "csv":
        return StreamingResponse(
            io.BytesIO(data),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=AIRISS_v4_results_{job_id}.csv"
            }
        )
    elif format.lower() == "json":
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=AIRISS_v4_results_{job_id}.json"
            }
        )
    else:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 형식: {format}")