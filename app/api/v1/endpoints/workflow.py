"""
워크플로우 관련 API 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

# Response 모델들
class TaskResponse(BaseModel):
    id: str
    name: str
    status: str
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class WorkflowJobResponse(BaseModel):
    job_id: str
    status: str
    progress: float = 0.0
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    task_summary: Optional[dict] = None
    download_url: Optional[str] = None
    error: Optional[str] = None
    original_filename: Optional[str] = None

class WorkflowMetrics(BaseModel):
    total_jobs: int
    total_tasks: int
    success_rate: float
    average_processing_time: Optional[float] = None

# 헬퍼 함수들 (orchestrator를 받아서 처리)
async def get_job_status(job_id: str, orchestrator) -> WorkflowJobResponse:
    """작업 상태 조회"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Workflow service not available")
    
    job_status = await orchestrator.get_job_status(job_id)
    
    if job_status.get('status') == 'not_found':
        raise HTTPException(status_code=404, detail="Job not found")
    
    return WorkflowJobResponse(**job_status)

async def get_job_tasks(job_id: str, db: Session, orchestrator) -> List[TaskResponse]:
    """작업의 태스크 목록 조회"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Workflow service not available")
    
    # DB에서 태스크 조회
    from app.models.workflow import WorkflowTask
    tasks = db.query(WorkflowTask).filter(WorkflowTask.job_id == job_id).all()
    
    return [
        TaskResponse(
            id=task.id,
            name=task.name,
            status=task.status,
            error=task.error,
            created_at=task.created_at,
            completed_at=task.completed_at
        )
        for task in tasks
    ]

async def retry_failed_tasks(job_id: str, orchestrator) -> dict:
    """실패한 태스크 재시도"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Workflow service not available")
    
    result = await orchestrator.retry_failed_tasks(job_id)
    return result

async def get_workflow_metrics(db: Session, orchestrator) -> WorkflowMetrics:
    """워크플로우 메트릭 조회"""
    from app.models.workflow import WorkflowJob, WorkflowTask
    
    total_jobs = db.query(WorkflowJob).count()
    total_tasks = db.query(WorkflowTask).count()
    
    if total_jobs > 0:
        completed_jobs = db.query(WorkflowJob).filter(WorkflowJob.status == 'completed').count()
        success_rate = (completed_jobs / total_jobs) * 100
    else:
        success_rate = 0.0
    
    return WorkflowMetrics(
        total_jobs=total_jobs,
        total_tasks=total_tasks,
        success_rate=success_rate
    )

async def list_user_jobs(skip: int, limit: int, status: Optional[str], user_id: str, orchestrator) -> List[WorkflowJobResponse]:
    """사용자의 작업 목록 조회"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Workflow service not available")
    
    # 실제 구현에서는 DB 조회
    return []

async def cancel_job(job_id: str, orchestrator) -> dict:
    """작업 취소"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Workflow service not available")
    
    # 실제 구현
    return {"message": "Job cancelled", "job_id": job_id}