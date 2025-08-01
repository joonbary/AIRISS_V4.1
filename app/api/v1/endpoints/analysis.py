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
from app.services.analysis_service import AnalysisService
import json
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

@router.get("/jobs")
async def get_analysis_jobs(
    service: AnalysisService = Depends(get_analysis_service)
):
    """모든 분석 작업 목록 조회"""
    logger = logging.getLogger(__name__)
    try:
        # 데이터베이스에서 작업 목록 가져오기
        db = service._get_db()
        try:
            from app.models.job import Job
            jobs_db = db.query(Job).order_by(Job.created_at.desc()).all()
            
            jobs = []
            for job in jobs_db:
                # 결과 데이터 파싱
                result = None
                if job.results_data:
                    try:
                        result = json.loads(job.results_data) if isinstance(job.results_data, str) else job.results_data
                    except:
                        result = None
                
                job_info = {
                    "id": job.id,
                    "status": job.status,
                    "created_at": job.created_at.isoformat() if job.created_at else "",
                    "filename": job.filename or "",
                    "file_id": job.file_id or "",
                    "result": result
                }
                jobs.append(job_info)
            
            return jobs
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error getting jobs list: {str(e)}")
        return []

@router.get("/results/{job_id}")
async def get_results(
    job_id: str,
    service: AnalysisService = Depends(get_analysis_service)
):
    """분석 결과 조회"""
    logger = logging.getLogger(__name__)
    logger.info(f"📊 Results requested for job: {job_id}")
    
    # Get job from database to return full result structure
    db = service._get_db()
    try:
        from app.models.job import Job
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            logger.error(f"❌ Job not found: {job_id}")
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
        
        if job.status != 'completed':
            logger.warning(f"⚠️ Job not completed: {job_id}, status: {job.status}")
            raise HTTPException(status_code=400, detail=f"작업이 아직 완료되지 않았습니다. 현재 상태: {job.status}")
        
        if job.results_data:
            # Return the full results structure
            results = json.loads(job.results_data)
            # 분석 결과는 'data' 필드에 저장됨
            analysis_results = results.get('data', [])
            logger.info(f"✅ Returning results for job {job_id}: {len(analysis_results)} results")
            
            # 첫 번째 결과 로그로 확인
            if analysis_results and len(analysis_results) > 0:
                logger.info(f"📋 첫 번째 분석 결과 샘플:")
                logger.info(f"  - UID: {analysis_results[0].get('uid')}")
                logger.info(f"  - Name: {analysis_results[0].get('name')}")
                logger.info(f"  - Score: {analysis_results[0].get('score')}")
                logger.info(f"  - Grade: {analysis_results[0].get('grade')}")
            
            # 프론트엔드 호환성을 위해 analysis_results 필드도 추가
            if 'analysis_results' not in results and analysis_results:
                results['analysis_results'] = analysis_results
            
            return results
        else:
            logger.warning(f"⚠️ No results data for job: {job_id}")
            return {"analysis_results": [], "data": [], "summary": {}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting results: {e}")
        raise HTTPException(status_code=500, detail="결과 조회 중 오류가 발생했습니다")
    finally:
        db.close()

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

@router.get("/pdf/{job_id}/{employee_id}")
async def download_employee_pdf(
    job_id: str,
    employee_id: str,
    service: AnalysisService = Depends(get_analysis_service)
):
    """개인별 분석 결과 PDF 다운로드"""
    logger = logging.getLogger(__name__)
    logger.info(f"PDF 다운로드 요청: job_id={job_id}, employee_id='{employee_id}', type={type(employee_id)}")
    logger.info(f"Employee ID 문자열 길이: {len(employee_id)}")
    logger.info(f"Employee ID에 'dtype' 포함 여부: {'dtype' in employee_id}")
    
    # pandas Series 형태 감지
    if 'dtype: object' in str(employee_id):
        logger.error(f"⚠️ Pandas Series 객체 감지! 원본: {employee_id}")
        # Series에서 실제 값 추출 시도
        try:
            import re
            # EMP001과 같은 패턴 추출
            match = re.search(r'EMP\d+', str(employee_id))
            if match:
                extracted_id = match.group()
                logger.info(f"✅ Series에서 ID 추출 성공: {extracted_id}")
                employee_id = extracted_id
            else:
                logger.error("❌ Series에서 ID 추출 실패")
                raise HTTPException(status_code=400, detail="잘못된 employee_id 형식입니다")
        except Exception as e:
            logger.error(f"❌ Series 처리 중 오류: {e}")
            raise HTTPException(status_code=400, detail="employee_id 처리 중 오류가 발생했습니다")
    
    try:
        # 작업 정보 가져오기
        db = service._get_db()
        try:
            from app.models.job import Job
            job = db.query(Job).filter(Job.id == job_id).first()
            
            if not job:
                raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
                
            if job.status != 'completed':
                raise HTTPException(status_code=400, detail="분석이 완료되지 않았습니다")
                
            # 분석 결과에서 해당 직원 데이터 찾기
            if job.results_data:
                results = json.loads(job.results_data)
                analysis_results = results.get('analysis_results', results.get('data', []))
                
                # 직원 데이터 찾기
                logger.info(f"🔍 데이터베이스에 저장된 분석 결과 개수: {len(analysis_results)}")
                logger.info(f"🔍 첫 번째 결과 샘플: {analysis_results[0] if analysis_results else 'None'}")
                
                # pandas Series에서 실제 값 추출하는 함수
                def extract_from_pandas_series(value):
                    if not isinstance(value, str):
                        return str(value)
                    
                    # pandas Series 형태 감지
                    if 'dtype: object' in value:
                        import re
                        # EMP001과 같은 패턴 추출
                        emp_id_match = re.search(r'EMP\d+', value)
                        if emp_id_match:
                            return emp_id_match.group()
                    
                    return str(value)
                
                employee_data = None
                for i, result in enumerate(analysis_results):
                    # 원본 값
                    raw_emp_id = result.get('employee_id', '')
                    raw_uid = result.get('uid', '')
                    
                    # pandas Series에서 실제 값 추출
                    result_emp_id = extract_from_pandas_series(raw_emp_id)
                    result_uid = extract_from_pandas_series(raw_uid)
                    
                    logger.info(f"🔍 결과 [{i}]: 원본_emp_id='{raw_emp_id[:50]}...', 추출된_emp_id='{result_emp_id}', 추출된_uid='{result_uid}', 비교대상='{employee_id}'")
                    logger.info(f"🔍 매치 여부: emp_id={result_emp_id == employee_id}, uid={result_uid == employee_id}")
                    
                    if result_emp_id == employee_id or result_uid == employee_id:
                        logger.info(f"✅ 매치 발견! 인덱스: {i}")
                        employee_data = result
                        break
                        
                if not employee_data:
                    raise HTTPException(status_code=404, detail=f"직원 데이터를 찾을 수 없습니다: {employee_id}")
                    
                # PDF 생성
                from app.services.pdf_service import PDFReportGenerator
                pdf_generator = PDFReportGenerator()
                pdf_bytes = pdf_generator.generate_employee_report(employee_data, job_id)
                
                # 파일명 생성 (URL 인코딩으로 한글 처리)
                from urllib.parse import quote
                employee_name = employee_data.get('name', 'unknown')
                safe_filename = f"AIRISS_v4_{employee_id}_{employee_name}_리포트.pdf"
                encoded_filename = quote(safe_filename, safe='')
                
                return StreamingResponse(
                    io.BytesIO(pdf_bytes),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
                    }
                )
            else:
                raise HTTPException(status_code=404, detail="분석 결과가 없습니다")
                
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF 생성 오류: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF 생성 중 오류가 발생했습니다: {str(e)}")