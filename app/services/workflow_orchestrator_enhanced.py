"""
강화된 워크플로우 오케스트레이터 - 예외 처리 및 로깅 개선
"""
import asyncio
import os
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.task_manager import ShrimpTaskManager, Task, TaskStatus, TaskPriority
from app.core.websocket_manager_enhanced import get_websocket_manager
from app.services.workflow_tasks import (
    validate_file_task,
    extract_metadata_task,
    analyze_statistics_task,
    analyze_llm_task,
    generate_excel_report_task,
    store_to_mcp_task,
    generate_download_link_task
)
from app.models.workflow import WorkflowJob, WorkflowTask
from app.utils.json_utils import convert_to_json_serializable as convert_to_serializable

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 파일 핸들러 추가 (UTF-8 인코딩)
fh = logging.FileHandler('workflow_enhanced.log', encoding='utf-8')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class EnhancedWorkflowOrchestrator:
    """강화된 워크플로우 오케스트레이터"""
    
    def __init__(self, db: Session):
        self.db = db
        self.task_manager = ShrimpTaskManager(db)
        self.websocket_manager = get_websocket_manager()
        self.active_jobs: Dict[str, WorkflowJob] = {}
        self._running = False
        
    async def start(self):
        """오케스트레이터 시작"""
        logger.info("Enhanced Workflow Orchestrator starting...")
        await self.task_manager.start()
        self._running = True
        
        # 미완료 작업 복구
        await self._recover_incomplete_jobs()
        
    async def stop(self):
        """오케스트레이터 종료"""
        logger.info("Enhanced Workflow Orchestrator stopping...")
        self._running = False
        await self.task_manager.stop()
        
    async def _recover_incomplete_jobs(self):
        """서버 재시작 시 미완료 작업 복구"""
        try:
            incomplete_jobs = self.db.query(WorkflowJob).filter(
                WorkflowJob.status.in_(['initializing', 'running'])
            ).all()
            
            if incomplete_jobs:
                logger.info(f"Found {len(incomplete_jobs)} incomplete jobs to recover")
                
                for job in incomplete_jobs:
                    try:
                        # 작업 상태를 failed로 변경하고 재시작 옵션 제공
                        job.status = 'failed'
                        job.error = "Server restart detected. Job can be retried."
                        self.db.commit()
                        
                        # WebSocket으로 알림
                        await self._notify_job_status(job.id, 'failed', 
                            "작업이 서버 재시작으로 인해 중단되었습니다. 재시도할 수 있습니다.")
                            
                    except Exception as e:
                        logger.error(f"Failed to recover job {job.id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error during job recovery: {e}")
            
    async def create_analysis_job(self, file_path: str, original_filename: str, 
                                  user_id: str, user_email: str) -> str:
        """분석 작업 생성 (강화된 에러 처리)"""
        job_id = str(uuid4())
        
        try:
            # 파일 존재 확인
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Upload file not found: {file_path}")
                
            # 파일 크기 확인
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB 제한
                raise ValueError(f"File too large: {file_size / 1024 / 1024:.1f}MB (limit: 100MB)")
                
            # 환경 변수 검증
            if not os.getenv("OPENAI_API_KEY"):
                logger.warning("OpenAI API key not found - LLM analysis will be skipped")
                
            # 작업 생성
            job = WorkflowJob(
                id=job_id,
                user_id=user_id,
                user_email=user_email,
                file_path=file_path,
                original_filename=original_filename,
                status='initializing',
                created_at=datetime.utcnow()
            )
            
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            
            self.active_jobs[job_id] = job
            
            # 워크플로우 태스크 생성
            await self._create_workflow_tasks(job_id, file_path, original_filename)
            
            # 상태 업데이트
            job.status = 'running'
            self.db.commit()
            
            # WebSocket 알림
            await self._notify_job_status(job_id, 'running', 
                f"분석 작업이 시작되었습니다: {original_filename}")
            
            logger.info(f"Created analysis job: {job_id} for user: {user_email}")
            
            return job_id
            
        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}")
            await self._handle_job_error(job_id, "파일을 찾을 수 없습니다", str(e))
            raise
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            await self._handle_job_error(job_id, "파일 검증 실패", str(e))
            raise
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating job: {e}")
            await self._handle_job_error(job_id, "데이터베이스 오류", str(e))
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error creating job: {e}\n{traceback.format_exc()}")
            await self._handle_job_error(job_id, "예상치 못한 오류", str(e))
            raise
            
    async def _create_workflow_tasks(self, job_id: str, file_path: str, 
                                     original_filename: str):
        """워크플로우 태스크 생성 (의존성 관리 포함)"""
        
        # 1. 파일 검증 태스크
        validate_task = await self._create_task(
            job_id=job_id,
            name="파일 검증",
            handler=validate_file_task,
            params={"file_path": file_path},
            priority=TaskPriority.HIGH
        )
        
        # 2. 메타데이터 추출 태스크 (파일 검증 완료 후)
        metadata_task = await self._create_task(
            job_id=job_id,
            name="메타데이터 추출",
            handler=extract_metadata_task,
            params={"file_path": file_path},
            dependencies=[validate_task.id]
        )
        
        # 3. 통계 분석 태스크 (메타데이터 추출 완료 후)
        stats_task = await self._create_task(
            job_id=job_id,
            name="통계 분석",
            handler=analyze_statistics_task,
            params={"job_id": job_id},
            dependencies=[metadata_task.id]
        )
        
        # 4. LLM 분석 태스크들 (병렬 처리)
        # 실제 구현에서는 파일에서 직원 데이터를 읽어와야 함
        llm_tasks = []
        
        try:
            # 데이터 파일 읽기
            import pandas as pd
            df = pd.read_excel(file_path)
            
            # 직원별 LLM 태스크 생성 (최대 10명으로 제한 - 테스트)
            for idx, row in df.head(10).iterrows():
                if 'UID' in row and '의견' in row:
                    llm_task = await self._create_task(
                        job_id=job_id,
                        name=f"LLM 분석 - {row['UID']}",
                        handler=analyze_llm_task,
                        params={
                            "job_id": job_id,
                            "employee_data": {
                                "uid": row['UID'],
                                "opinion": row['의견'],
                                "row_index": idx
                            }
                        },
                        dependencies=[metadata_task.id],
                        priority=TaskPriority.MEDIUM
                    )
                    llm_tasks.append(llm_task)
                    
        except Exception as e:
            logger.error(f"Error creating LLM tasks: {e}")
            # LLM 태스크 생성 실패는 전체 워크플로우를 중단시키지 않음
            
        # 5. Excel 보고서 생성 (모든 분석 완료 후)
        all_analysis_tasks = [stats_task.id] + [t.id for t in llm_tasks]
        
        excel_task = await self._create_task(
            job_id=job_id,
            name="Excel 보고서 생성",
            handler=generate_excel_report_task,
            params={
                "job_id": job_id,
                "original_filename": original_filename
            },
            dependencies=all_analysis_tasks
        )
        
        # 6. MCP 저장 (보고서 생성 완료 후)
        mcp_task = await self._create_task(
            job_id=job_id,
            name="MCP 서버 저장",
            handler=store_to_mcp_task,
            params={"job_id": job_id},
            dependencies=[excel_task.id]
        )
        
        # 7. 다운로드 링크 생성 (MCP 저장 완료 후)
        download_task = await self._create_task(
            job_id=job_id,
            name="다운로드 링크 생성",
            handler=generate_download_link_task,
            params={"job_id": job_id},
            dependencies=[mcp_task.id]
        )
        
    async def _create_task(self, job_id: str, name: str, handler, 
                          params: Dict, dependencies: List[str] = None,
                          priority: TaskPriority = TaskPriority.MEDIUM) -> Task:
        """개별 태스크 생성 (에러 처리 포함)"""
        try:
            task = Task(
                id=f"{job_id}_{name.replace(' ', '_')}_{uuid4().hex[:8]}",
                name=name,
                handler=handler,
                params=params,
                priority=priority,
                max_retries=3,  # 재시도 횟수 설정
                dependencies=dependencies or []
            )
            
            # DB에 태스크 저장
            workflow_task = WorkflowTask(
                id=task.id,
                job_id=job_id,
                name=name,
                status='pending',
                created_at=datetime.utcnow()
            )
            
            self.db.add(workflow_task)
            self.db.commit()
            
            # 태스크 매니저에 제출
            await self.task_manager.submit_task(task)
            
            logger.info(f"Created task: {task.id} - {name}")
            
            return task
            
        except Exception as e:
            logger.error(f"Error creating task {name}: {e}")
            raise
            
    async def _handle_job_error(self, job_id: str, user_message: str, 
                               technical_error: str):
        """작업 오류 처리"""
        try:
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                job.status = 'failed'
                job.error = technical_error
                job.completed_at = datetime.utcnow()
                self.db.commit()
                
            # WebSocket으로 사용자에게 알림
            await self._notify_job_status(job_id, 'failed', user_message, 
                                        {'technical_error': technical_error})
                                        
        except Exception as e:
            logger.error(f"Error handling job error: {e}")
            
    async def _notify_job_status(self, job_id: str, status: str, 
                                message: str, details: Dict = None):
        """WebSocket을 통한 상태 알림"""
        try:
            notification = {
                'job_id': job_id,
                'status': status,
                'message': message,
                'timestamp': datetime.utcnow().isoformat(),
                'details': details or {}
            }
            
            # JSON 직렬화 가능하도록 변환
            notification = convert_to_serializable(notification)
            
            await self.websocket_manager.broadcast(
                message=notification,
                channel='workflow_status'
            )
            
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {e}")
            
    async def get_job_status(self, job_id: str) -> Dict:
        """작업 상태 조회 (강화된 정보 제공)"""
        try:
            job = self.db.query(WorkflowJob).filter(WorkflowJob.id == job_id).first()
            
            if not job:
                return {
                    'job_id': job_id,
                    'status': 'not_found',
                    'error': 'Job not found'
                }
                
            # 태스크 상태 집계
            tasks = self.db.query(WorkflowTask).filter(
                WorkflowTask.job_id == job_id
            ).all()
            
            task_summary = {
                'total': len(tasks),
                'by_status': {}
            }
            
            for task in tasks:
                status = task.status
                task_summary['by_status'][status] = task_summary['by_status'].get(status, 0) + 1
                
            # 진행률 계산
            completed_tasks = task_summary['by_status'].get('completed', 0)
            progress = (completed_tasks / task_summary['total'] * 100) if task_summary['total'] > 0 else 0
            
            return {
                'job_id': job_id,
                'status': job.status,
                'progress': round(progress, 1),
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'task_summary': task_summary,
                'download_url': job.download_url,
                'error': job.error,
                'original_filename': job.original_filename
            }
            
        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            return {
                'job_id': job_id,
                'status': 'error',
                'error': 'Failed to retrieve job status'
            }
            
    async def retry_failed_tasks(self, job_id: str) -> Dict:
        """실패한 태스크 재시도"""
        try:
            # 실패한 태스크 찾기
            failed_tasks = self.db.query(WorkflowTask).filter(
                WorkflowTask.job_id == job_id,
                WorkflowTask.status == 'failed'
            ).all()
            
            if not failed_tasks:
                return {
                    'job_id': job_id,
                    'message': 'No failed tasks to retry',
                    'retried_count': 0
                }
                
            retried_count = 0
            
            for task in failed_tasks:
                try:
                    # 태스크 재제출
                    await self.task_manager.retry_task(task.id)
                    
                    # 상태 업데이트
                    task.status = 'retrying'
                    task.retry_count = (task.retry_count or 0) + 1
                    self.db.commit()
                    
                    retried_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to retry task {task.id}: {e}")
                    
            # 작업 상태 업데이트
            job = self.db.query(WorkflowJob).filter(WorkflowJob.id == job_id).first()
            if job and job.status == 'failed':
                job.status = 'running'
                self.db.commit()
                
            # 알림
            await self._notify_job_status(job_id, 'retrying', 
                f"{retried_count}개의 태스크를 재시도합니다.")
                
            return {
                'job_id': job_id,
                'message': f'Retried {retried_count} failed tasks',
                'retried_count': retried_count
            }
            
        except Exception as e:
            logger.error(f"Error retrying failed tasks: {e}")
            return {
                'job_id': job_id,
                'error': 'Failed to retry tasks',
                'details': str(e)
            }