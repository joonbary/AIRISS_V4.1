"""
워크플로우 오케스트레이터 - 전체 파이프라인 관리
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.task_manager import (
    ShrimpTaskManager, Task, TaskType, TaskStatus, TaskPriority
)
from app.services.workflow_tasks import WorkflowTasks
from app.db.database import get_db
from app.core.websocket_manager import ConnectionManager as WebSocketManager

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """워크플로우 오케스트레이터"""
    
    def __init__(self, db: Session, websocket_manager: Optional[WebSocketManager] = None):
        self.db = db
        self.task_manager = ShrimpTaskManager(db)
        self.workflow_tasks = WorkflowTasks()
        self.websocket_manager = websocket_manager
        self.running_jobs: Dict[str, Dict[str, Any]] = {}
        
    async def start(self):
        """오케스트레이터 시작"""
        await self.task_manager.start(num_workers=10)
        logger.info("Workflow Orchestrator started")
        
    async def stop(self):
        """오케스트레이터 중지"""
        await self.task_manager.stop()
        logger.info("Workflow Orchestrator stopped")
        
    async def create_analysis_job(
        self, 
        file_path: str, 
        original_filename: str,
        user_id: str,
        user_email: str
    ) -> str:
        """분석 작업 생성 및 실행"""
        job_id = str(uuid4())
        
        try:
            # 작업 정보 저장
            self.running_jobs[job_id] = {
                "job_id": job_id,
                "user_id": user_id,
                "user_email": user_email,
                "status": "initializing",
                "created_at": datetime.utcnow(),
                "tasks": {}
            }
            
            # 1. 업로드 태스크
            upload_task = await self._create_upload_task(
                job_id, file_path, original_filename
            )
            
            # 2. 검증 태스크 (업로드 완료 후)
            validate_task = await self._create_validate_task(
                job_id, upload_task.id
            )
            
            # 3. 통계 분석 태스크 (검증 완료 후)
            stats_task = await self._create_stats_task(
                job_id, validate_task.id
            )
            
            # 4. LLM 분석 준비 태스크 (통계 완료 후)
            llm_prep_task = await self._create_llm_prep_task(
                job_id, [validate_task.id, stats_task.id]
            )
            
            # 웹소켓 알림
            await self._send_progress_update(job_id, "Job created", 0)
            
            logger.info(f"Analysis job created: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to create job {job_id}: {e}")
            self.running_jobs[job_id]["status"] = "failed"
            self.running_jobs[job_id]["error"] = str(e)
            raise
            
    async def _create_upload_task(
        self, job_id: str, file_path: str, original_filename: str
    ) -> Task:
        """업로드 태스크 생성"""
        task = Task(
            job_id=job_id,
            task_type=TaskType.UPLOAD,
            priority=TaskPriority.HIGH,
            input_data={
                "file_path": file_path,
                "original_filename": original_filename
            },
            handler=self.workflow_tasks.upload_task,
            on_success=self._on_upload_success,
            on_failure=self._on_task_failure
        )
        
        task_id = await self.task_manager.submit_task(task)
        self.running_jobs[job_id]["tasks"]["upload"] = task_id
        return task
        
    async def _create_validate_task(
        self, job_id: str, dependency_id: str
    ) -> Task:
        """검증 태스크 생성"""
        task = Task(
            job_id=job_id,
            task_type=TaskType.VALIDATE,
            priority=TaskPriority.HIGH,
            dependencies=[dependency_id],
            handler=self.workflow_tasks.validate_task,
            on_success=self._on_validate_success,
            on_failure=self._on_task_failure
        )
        
        task_id = await self.task_manager.submit_task(task)
        self.running_jobs[job_id]["tasks"]["validate"] = task_id
        return task
        
    async def _create_stats_task(
        self, job_id: str, dependency_id: str
    ) -> Task:
        """통계 분석 태스크 생성"""
        task = Task(
            job_id=job_id,
            task_type=TaskType.ANALYZE_STATS,
            priority=TaskPriority.MEDIUM,
            dependencies=[dependency_id],
            handler=self.workflow_tasks.analyze_stats_task,
            on_success=self._on_stats_success,
            on_failure=self._on_task_failure
        )
        
        task_id = await self.task_manager.submit_task(task)
        self.running_jobs[job_id]["tasks"]["stats"] = task_id
        return task
        
    async def _create_llm_prep_task(
        self, job_id: str, dependencies: List[str]
    ) -> Task:
        """LLM 분석 준비 태스크"""
        async def prepare_llm_tasks(task: Task) -> Dict[str, Any]:
            """직원별 LLM 태스크 생성"""
            # 이전 태스크 결과 가져오기
            validate_task = await self.task_manager.get_task_status(
                dependencies[0]
            )
            stats_task = await self.task_manager.get_task_status(
                dependencies[1]
            )
            
            validated_file = validate_task.output_data.get("validated_file")
            stats_data = stats_task.output_data
            
            # 데이터 로드
            import pandas as pd
            df = pd.read_pickle(validated_file)
            
            # 부서별 평균 계산
            dept_avg = df.groupby('department')['score'].mean().to_dict()
            total_avg = df['score'].mean()
            
            # 직원별 LLM 태스크 생성
            llm_task_ids = []
            for _, employee in df.iterrows():
                # 백분위 계산
                percentile = (df['score'] < employee['score']).sum() / len(df) * 100
                
                llm_task = Task(
                    job_id=job_id,
                    task_type=TaskType.ANALYZE_LLM,
                    priority=TaskPriority.LOW,
                    input_data={
                        "employee_data": employee.to_dict(),
                        "context_data": {
                            "dept_avg": dept_avg.get(employee['department']),
                            "total_avg": total_avg,
                            "percentile": round(percentile, 1)
                        }
                    },
                    handler=self.workflow_tasks.analyze_llm_task,
                    max_retries=2,  # LLM은 재시도 횟수 줄임
                    retry_delay=10
                )
                
                task_id = await self.task_manager.submit_task(llm_task)
                llm_task_ids.append(task_id)
                
            # 모든 LLM 태스크 완료 대기 태스크 생성
            await self._create_merge_task(
                job_id, llm_task_ids, validated_file, stats_data
            )
            
            return {
                "llm_task_count": len(llm_task_ids),
                "llm_task_ids": llm_task_ids
            }
            
        task = Task(
            job_id=job_id,
            task_type=TaskType.ANALYZE_LLM,
            priority=TaskPriority.HIGH,
            dependencies=dependencies,
            handler=prepare_llm_tasks
        )
        
        task_id = await self.task_manager.submit_task(task)
        return task
        
    async def _create_merge_task(
        self, job_id: str, llm_task_ids: List[str], 
        validated_file: str, stats_data: Dict[str, Any]
    ):
        """LLM 결과 병합 및 리포트 생성 태스크"""
        async def merge_and_report(task: Task) -> Dict[str, Any]:
            # 모든 LLM 결과 수집
            llm_results = []
            failed_count = 0
            
            for task_id in llm_task_ids:
                llm_task = await self.task_manager.get_task_status(task_id)
                if llm_task.status == TaskStatus.COMPLETED:
                    llm_results.append(llm_task.output_data)
                else:
                    failed_count += 1
                    
            logger.info(f"LLM analysis completed: {len(llm_results)} success, {failed_count} failed")
            
            # 리포트 생성 태스크
            report_task = Task(
                job_id=job_id,
                task_type=TaskType.GENERATE_REPORT,
                priority=TaskPriority.HIGH,
                input_data={
                    "stats_data": stats_data,
                    "llm_results": llm_results,
                    "validated_file": validated_file
                },
                handler=self.workflow_tasks.generate_report_task,
                on_success=self._on_report_success
            )
            
            await self.task_manager.submit_task(report_task)
            return {"merged_count": len(llm_results)}
            
        merge_task = Task(
            job_id=job_id,
            task_type=TaskType.GENERATE_REPORT,
            priority=TaskPriority.MEDIUM,
            dependencies=llm_task_ids,
            handler=merge_and_report
        )
        
        await self.task_manager.submit_task(merge_task)
        
    async def _on_upload_success(self, task: Task):
        """업로드 성공 콜백"""
        # 다음 태스크에 데이터 전달
        validate_task_id = self.running_jobs[task.job_id]["tasks"].get("validate")
        if validate_task_id:
            validate_task = await self.task_manager.get_task_status(validate_task_id)
            validate_task.input_data.update(task.output_data)
            
        await self._send_progress_update(task.job_id, "Upload completed", 20)
        
    async def _on_validate_success(self, task: Task):
        """검증 성공 콜백"""
        stats_task_id = self.running_jobs[task.job_id]["tasks"].get("stats")
        if stats_task_id:
            stats_task = await self.task_manager.get_task_status(stats_task_id)
            stats_task.input_data.update(task.output_data)
            
        await self._send_progress_update(task.job_id, "Validation completed", 40)
        
    async def _on_stats_success(self, task: Task):
        """통계 분석 성공 콜백"""
        await self._send_progress_update(task.job_id, "Statistical analysis completed", 60)
        
    async def _on_report_success(self, task: Task):
        """리포트 생성 성공 콜백"""
        # 파일 저장 태스크
        store_task = Task(
            job_id=task.job_id,
            task_type=TaskType.STORE_FILE,
            priority=TaskPriority.MEDIUM,
            input_data=task.output_data,
            handler=self.workflow_tasks.store_file_task,
            on_success=self._on_store_success
        )
        
        await self.task_manager.submit_task(store_task)
        await self._send_progress_update(task.job_id, "Report generated", 80)
        
    async def _on_store_success(self, task: Task):
        """파일 저장 성공 콜백"""
        job_info = self.running_jobs.get(task.job_id, {})
        
        # 알림 태스크
        notify_task = Task(
            job_id=task.job_id,
            task_type=TaskType.NOTIFY,
            priority=TaskPriority.LOW,
            input_data={
                "download_url": task.output_data.get("download_url"),
                "user_email": job_info.get("user_email"),
                "job_summary": await self._get_job_summary(task.job_id)
            },
            handler=self.workflow_tasks.notify_task
        )
        
        await self.task_manager.submit_task(notify_task)
        await self._send_progress_update(task.job_id, "Analysis completed", 100)
        
        # 작업 상태 업데이트
        self.running_jobs[task.job_id]["status"] = "completed"
        self.running_jobs[task.job_id]["completed_at"] = datetime.utcnow()
        self.running_jobs[task.job_id]["download_url"] = task.output_data.get("download_url")
        
    async def _on_task_failure(self, task: Task):
        """태스크 실패 콜백"""
        logger.error(f"Task failed: {task.id} ({task.task_type}) - {task.error_message}")
        
        # 작업 상태 업데이트
        if task.job_id in self.running_jobs:
            self.running_jobs[task.job_id]["status"] = "failed"
            self.running_jobs[task.job_id]["error"] = task.error_message
            
        await self._send_progress_update(
            task.job_id, 
            f"Task failed: {task.task_type}", 
            -1
        )
        
    async def _send_progress_update(self, job_id: str, message: str, progress: int):
        """진행상황 업데이트 전송"""
        if self.websocket_manager:
            # WebSocket으로 진행상황 전송 (ConnectionManager 메서드에 맞게 수정)
            update_data = {
                "type": "progress",
                "job_id": job_id,
                "message": message,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat()
            }
            # 모든 연결된 클라이언트에게 전송
            for client_id in list(self.websocket_manager.active_connections.keys()):
                try:
                    await self.websocket_manager.send_personal_message(
                        json.dumps(update_data), 
                        client_id
                    )
                except:
                    pass
            
    async def _get_job_summary(self, job_id: str) -> Dict[str, Any]:
        """작업 요약 정보 생성"""
        tasks = await self.task_manager.get_job_tasks(job_id)
        
        summary = {
            "total_tasks": len(tasks),
            "completed_tasks": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for t in tasks if t.status == TaskStatus.FAILED),
            "duration": None
        }
        
        if tasks:
            start_time = min(t.created_at for t in tasks)
            end_time = max(t.completed_at for t in tasks if t.completed_at)
            if end_time:
                summary["duration"] = (end_time - start_time).total_seconds()
                
        return summary
        
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """작업 상태 조회"""
        if job_id not in self.running_jobs:
            return None
            
        job_info = self.running_jobs[job_id].copy()
        
        # 태스크 상태 추가
        tasks = await self.task_manager.get_job_tasks(job_id)
        job_info["task_summary"] = {
            "total": len(tasks),
            "by_status": {}
        }
        
        for task in tasks:
            status = task.status.value
            job_info["task_summary"]["by_status"][status] = \
                job_info["task_summary"]["by_status"].get(status, 0) + 1
                
        return job_info
        
    async def retry_failed_tasks(self, job_id: str) -> int:
        """실패한 태스크 재시도"""
        tasks = await self.task_manager.get_job_tasks(job_id)
        retry_count = 0
        
        for task in tasks:
            if task.status == TaskStatus.FAILED:
                task.status = TaskStatus.PENDING
                task.retry_count = 0
                await self.task_manager.submit_task(task)
                retry_count += 1
                
        logger.info(f"Retrying {retry_count} failed tasks for job {job_id}")
        return retry_count