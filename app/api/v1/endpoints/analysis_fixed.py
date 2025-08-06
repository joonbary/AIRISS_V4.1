# app/api/v1/endpoints/analysis_fixed.py
"""
AIRISS v4.0 Fixed Analysis API Endpoints
- Proper database persistence for jobs
- Complete E2E flow support
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from app.core.websocket_manager import ConnectionManager, manager
from app.services.analysis_service_fixed import AnalysisServiceFixed

router = APIRouter()

# Dependency injection
def get_ws_manager():
    """Get WebSocket manager instance"""
    return manager

# Singleton analysis service instance
_analysis_service = None

def get_analysis_service(ws_manager: ConnectionManager = Depends(get_ws_manager)):
    """Get analysis service singleton instance"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisServiceFixed(ws_manager)
    return _analysis_service

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    service: AnalysisServiceFixed = Depends(get_analysis_service)
):
    """File upload endpoint"""
    try:
        contents = await file.read()
        result = await service.upload_file(contents, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze/{file_id}")
async def start_analysis(
    file_id: str,
    sample_size: int = 10,
    analysis_mode: str = "hybrid",
    enable_ai_feedback: bool = False,
    openai_api_key: Optional[str] = None,
    openai_model: str = "gpt-3.5-turbo",
    max_tokens: int = 1200,
    service: AnalysisServiceFixed = Depends(get_analysis_service)
):
    """Start analysis endpoint"""
    try:
        job_id = await service.start_analysis(
            file_id=file_id,
            sample_size=sample_size,
            analysis_mode=analysis_mode,
            enable_ai_feedback=enable_ai_feedback,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            max_tokens=max_tokens
        )
        return {"job_id": job_id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{job_id}")
async def get_job_status(
    job_id: str,
    service: AnalysisServiceFixed = Depends(get_analysis_service)
):
    """Get job status - properly retrieves from database"""
    status = service.get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return status

@router.get("/results/{job_id}")
async def get_results(
    job_id: str,
    service: AnalysisServiceFixed = Depends(get_analysis_service)
):
    """Get analysis results"""
    df = await service.get_analysis_results(job_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return df.to_dict(orient="records")

@router.get("/download/{job_id}/{format}")
async def download_results(
    job_id: str,
    format: str,
    service: AnalysisServiceFixed = Depends(get_analysis_service)
):
    """Download results"""
    data = await service.export_results(job_id, format)
    if data is None:
        raise HTTPException(status_code=404, detail="No data to download")
    
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
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

@router.get("/jobs")
async def list_jobs(
    service: AnalysisServiceFixed = Depends(get_analysis_service)
):
    """List all active jobs"""
    return service.list_active_jobs()