"""
Analysis API
분석 관련 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import io
import pandas as pd
import json

from app.db import get_db, AnalysisRepository, FileRepository
from app.schemas.analysis import (
    AnalysisCreate, 
    AnalysisResponse, 
    JobStatus, 
    AnalysisResult
)
from app.services.hybrid_analyzer import HybridAnalyzer
from app.api.v1.auth import get_current_user

router = APIRouter()


@router.post("/create", response_model=JobStatus)
async def create_analysis(
    analysis_data: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """분석 작업 생성"""
    # Check if file exists
    file_repo = FileRepository(db)
    file_info = file_repo.get_file(analysis_data.file_id)
    
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Create analysis job
    analysis_repo = AnalysisRepository(db)
    job_id = analysis_repo.create_job({
        "file_id": analysis_data.file_id,
        "sample_size": analysis_data.sample_size,
        "analysis_mode": analysis_data.analysis_mode,
        "enable_ai_feedback": analysis_data.enable_ai_feedback,
        "openai_model": analysis_data.openai_model,
        "max_tokens": analysis_data.max_tokens,
        "total_records": file_info.get("total_records", 0),
        "user_id": current_user["id"]
    })
    
    # TODO: Start async analysis task
    # asyncio.create_task(run_analysis(job_id, file_info, analysis_data))
    
    return JobStatus(
        job_id=job_id,
        status="created",
        progress=0.0,
        message="Analysis job created successfully"
    )


@router.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """작업 상태 조회"""
    analysis_repo = AnalysisRepository(db)
    job = analysis_repo.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", 0.0),
        message=job.get("error") if job.get("error") else f"Status: {job['status']}",
        processed_records=job.get("processed_records", 0),
        total_records=job.get("total_records", 0)
    )


@router.get("/results/{job_id}", response_model=List[AnalysisResult])
async def get_analysis_results(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """분석 결과 조회"""
    analysis_repo = AnalysisRepository(db)
    
    # Check job exists
    job = analysis_repo.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get results
    results = analysis_repo.get_results(job_id=job_id)
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found for this job"
        )
    
    return [AnalysisResult(**result) for result in results]


@router.get("/download/{job_id}")
async def download_results(
    job_id: str,
    format: str = Query("excel", regex="^(excel|csv|json)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """결과 다운로드"""
    analysis_repo = AnalysisRepository(db)
    
    # Get results
    results = analysis_repo.get_results(job_id=job_id)
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found"
        )
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Select relevant columns
    export_columns = [
        'uid', 'opinion', 'overall_score', 'text_score', 
        'quantitative_score', 'ok_grade', 'grade_description',
        'confidence', 'ai_strengths', 'ai_weaknesses'
    ]
    
    df_export = df[export_columns].copy()
    
    # Generate file based on format
    if format == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, sheet_name='Analysis Results', index=False)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=analysis_results_{job_id}.xlsx"
            }
        )
    
    elif format == "csv":
        output = io.StringIO()
        df_export.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=analysis_results_{job_id}.csv"
            }
        )
    
    else:  # json
        output = df_export.to_json(orient='records', force_ascii=False, indent=2)
        
        return StreamingResponse(
            io.BytesIO(output.encode('utf-8')),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=analysis_results_{job_id}.json"
            }
        )


@router.get("/history", response_model=List[JobStatus])
async def get_analysis_history(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """분석 히스토리 조회"""
    analysis_repo = AnalysisRepository(db)
    jobs = analysis_repo.get_completed_jobs()
    
    # Convert to response model
    history = []
    for job in jobs[:limit]:
        history.append(JobStatus(
            job_id=job["id"],
            status=job["status"],
            progress=100.0,
            message=f"Average score: {job.get('average_score', 0)}",
            processed_records=job.get("processed_records", 0),
            total_records=job.get("total_records", 0)
        ))
    
    return history