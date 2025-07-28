"""
Analysis API (Refactored)
서비스 레이어를 사용하는 분석 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import List
import pandas as pd
import io

from app.schemas.analysis import AnalysisCreate, JobStatus, AnalysisResult
from app.api.v1.dependencies import get_current_active_user, get_analysis_service
from app.services import AnalysisService

router = APIRouter()


@router.post("/create", response_model=JobStatus)
async def create_analysis(
    analysis_data: AnalysisCreate,
    current_user: dict = Depends(get_current_active_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """분석 작업 생성"""
    try:
        job_id = await analysis_service.create_analysis_job(
            file_id=analysis_data.file_id,
            analysis_config=analysis_data.dict(exclude={'file_id'}),
            user_id=current_user["id"]
        )
        
        return JobStatus(
            job_id=job_id,
            status="created",
            progress=0.0,
            message="Analysis job created and started"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_active_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """작업 상태 조회"""
    status_info = analysis_service.get_job_status(job_id)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return JobStatus(**status_info)


@router.get("/results/{job_id}", response_model=List[AnalysisResult])
async def get_analysis_results(
    job_id: str,
    current_user: dict = Depends(get_current_active_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """분석 결과 조회"""
    results = analysis_service.get_analysis_results(job_id)
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found for this job"
        )
    
    # AnalysisResult 스키마에 맞게 변환
    formatted_results = []
    for result in results:
        # dimension_scores 처리
        dimension_scores = result.get('dimension_scores', {})
        if isinstance(dimension_scores, str):
            import json
            try:
                dimension_scores = json.loads(dimension_scores)
            except:
                dimension_scores = {}
        
        # ai_feedback 처리
        ai_feedback = result.get('ai_feedback', {})
        if isinstance(ai_feedback, str):
            import json
            try:
                ai_feedback = json.loads(ai_feedback)
            except:
                ai_feedback = {}
        
        formatted_results.append(AnalysisResult(
            analysis_id=result['analysis_id'],
            uid=result['uid'],
            opinion=result.get('opinion'),
            overall_score=result.get('overall_score'),
            text_score=result.get('text_score'),
            quantitative_score=result.get('quantitative_score'),
            ok_grade=result.get('ok_grade'),
            grade_description=result.get('grade_description'),
            confidence=result.get('confidence'),
            percentile=result.get('percentile'),
            dimension_scores=dimension_scores,
            ai_feedback=ai_feedback,
            ai_strengths=result.get('ai_strengths'),
            ai_weaknesses=result.get('ai_weaknesses'),
            ai_recommendations=result.get('ai_recommendations', []),
            created_at=result['created_at']
        ))
    
    return formatted_results


@router.get("/download/{job_id}")
async def download_results(
    job_id: str,
    format: str = Query("excel", regex="^(excel|csv|json)$"),
    current_user: dict = Depends(get_current_active_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """결과 다운로드"""
    results = analysis_service.get_analysis_results(job_id)
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found"
        )
    
    # DataFrame 생성
    df = pd.DataFrame(results)
    
    # 다운로드할 컬럼 선택
    export_columns = [
        'uid', 'opinion', 'overall_score', 'text_score',
        'quantitative_score', 'ok_grade', 'grade_description',
        'confidence', 'ai_strengths', 'ai_weaknesses'
    ]
    
    # 존재하는 컬럼만 선택
    available_columns = [col for col in export_columns if col in df.columns]
    df_export = df[available_columns].copy()
    
    # 포맷에 따른 처리
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