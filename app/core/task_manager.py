"""
ShrimpTaskManager - 워크플로우 태스크 관리 시스템
"""
import asyncio
import json
import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from app.db.database import get_db

logger = logging.getLogger(__name__)

Base = declarative_base()


class TaskStatus(str, Enum):
    """태스크 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(str, Enum):
    """태스크 우선순위"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(str, Enum):
    """태스크 유형"""
    UPLOAD = "upload"
    VALIDATE = "validate"
    ANALYZE_STATS = "analyze_stats"
    ANALYZE_LLM = "analyze_llm"
    GENERATE_REPORT = "generate_report"
    STORE_FILE = "store_file"
    NOTIFY = "notify"


class TaskRecord(Base):
    """태스크 상태 DB 모델"""
    __tablename__ = "workflow_tasks"
    
    id = Column(String, primary_key=True)
    job_id = Column(String, nullable=False, index=True)
    task_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(String, default=TaskPriority.MEDIUM)
    
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    error_trace = Column(Text)
    
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    parent_task_id = Column(String)
    checkpoint_data = Column(JSON)  # 복구용 체크포인트


class Task(BaseModel):
    """태스크 정의"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    
    input_data: Dict[str, Any] = {}
    output_data: Dict[str, Any] = {}
    
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    parent_task_id: Optional[str] = None
    dependencies: List[str] = []  # 의존하는 태스크 ID들
    checkpoint_data: Dict[str, Any] = {}
    
    handler: Optional[Callable] = None
    on_success: Optional[Callable] = None
    on_failure: Optional[Callable] = None
    on_retry: Optional[Callable] = None


class ShrimpTaskManager:
    """태스크 관리자"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: Set[str] = set()
        self.task_queues: Dict[TaskPriority, asyncio.Queue] = {
            priority: asyncio.Queue() for priority in TaskPriority
        }
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        
    async def start(self, num_workers: int = 5):
        """태스크 매니저 시작"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info(f"Starting ShrimpTaskManager with {num_workers} workers")
        
        # 워커 시작
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
            
    async def stop(self):
        """태스크 매니저 중지"""
        self.is_running = False
        
        # 모든 워커 중지
        for worker in self.workers:
            worker.cancel()
            
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("ShrimpTaskManager stopped")
        
    async def submit_task(self, task: Task) -> str:
        """태스크 제출"""
        # DB에 저장
        self._save_task_to_db(task)
        
        # 메모리에 저장
        self.tasks[task.id] = task
        
        # 큐에 추가
        await self.task_queues[task.priority].put(task.id)
        
        logger.info(f"Task submitted: {task.id} ({task.task_type})")
        return task.id
        
    async def _worker(self, worker_id: str):
        """워커 프로세스"""
        logger.info(f"Worker {worker_id} started")
        
        while self.is_running:
            task_id = None
            try:
                # 우선순위 순으로 태스크 가져오기
                for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, 
                               TaskPriority.MEDIUM, TaskPriority.LOW]:
                    try:
                        task_id = await asyncio.wait_for(
                            self.task_queues[priority].get(), 
                            timeout=0.1
                        )
                        break
                    except asyncio.TimeoutError:
                        continue
                        
                if task_id:
                    await self._execute_task(task_id)
                    
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                if task_id:
                    await self._handle_task_error(task_id, e)
                    
    async def _execute_task(self, task_id: str):
        """태스크 실행"""
        task = self.tasks.get(task_id)
        if not task:
            return
            
        # 의존성 체크
        if not await self._check_dependencies(task):
            # 다시 큐에 넣기
            await asyncio.sleep(1)
            await self.task_queues[task.priority].put(task_id)
            return
            
        try:
            # 상태 업데이트
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            self.running_tasks.add(task_id)
            self._update_task_in_db(task)
            
            logger.info(f"Executing task: {task_id} ({task.task_type})")
            
            # 핸들러 실행
            if task.handler:
                result = await task.handler(task)
                task.output_data = result
                
            # 성공 처리
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            self._update_task_in_db(task)
            
            if task.on_success:
                await task.on_success(task)
                
            logger.info(f"Task completed: {task_id}")
            
        except Exception as e:
            await self._handle_task_error(task_id, e)
            
        finally:
            self.running_tasks.discard(task_id)
            
    async def _handle_task_error(self, task_id: str, error: Exception):
        """태스크 에러 처리"""
        task = self.tasks.get(task_id)
        if not task:
            return
            
        task.error_message = str(error)
        task.error_trace = traceback.format_exc()
        task.retry_count += 1
        
        logger.error(f"Task failed: {task_id} - {error}")
        
        # 재시도 가능 여부 확인
        if task.retry_count < task.max_retries:
            task.status = TaskStatus.RETRYING
            self._update_task_in_db(task)
            
            if task.on_retry:
                await task.on_retry(task)
                
            # 재시도 지연
            await asyncio.sleep(task.retry_delay * task.retry_count)
            
            # 다시 큐에 추가
            await self.task_queues[task.priority].put(task_id)
            logger.info(f"Task retry scheduled: {task_id} (attempt {task.retry_count})")
            
        else:
            # 최종 실패
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            self._update_task_in_db(task)
            
            if task.on_failure:
                await task.on_failure(task)
                
            logger.error(f"Task permanently failed: {task_id}")
            
    async def _check_dependencies(self, task: Task) -> bool:
        """의존성 체크"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
        
    def _save_task_to_db(self, task: Task):
        """DB에 태스크 저장"""
        record = TaskRecord(
            id=task.id,
            job_id=task.job_id,
            task_type=task.task_type.value,
            status=task.status.value,
            priority=task.priority.value,
            input_data=task.input_data,
            output_data=task.output_data,
            retry_count=task.retry_count,
            max_retries=task.max_retries,
            parent_task_id=task.parent_task_id,
            checkpoint_data=task.checkpoint_data
        )
        self.db.add(record)
        self.db.commit()
        
    def _update_task_in_db(self, task: Task):
        """DB의 태스크 업데이트"""
        record = self.db.query(TaskRecord).filter(TaskRecord.id == task.id).first()
        if record:
            record.status = task.status.value
            record.output_data = task.output_data
            record.error_message = task.error_message
            record.error_trace = task.error_trace
            record.retry_count = task.retry_count
            record.started_at = task.started_at
            record.completed_at = task.completed_at
            record.checkpoint_data = task.checkpoint_data
            self.db.commit()
            
    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """태스크 상태 조회"""
        return self.tasks.get(task_id)
        
    async def get_job_tasks(self, job_id: str) -> List[Task]:
        """작업의 모든 태스크 조회"""
        return [task for task in self.tasks.values() if task.job_id == job_id]
        
    async def cancel_task(self, task_id: str):
        """태스크 취소"""
        task = self.tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RETRYING]:
            task.status = TaskStatus.CANCELLED
            self._update_task_in_db(task)
            logger.info(f"Task cancelled: {task_id}")
            
    async def pause_task(self, task_id: str):
        """태스크 일시중지"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.PAUSED
            # 체크포인트 저장
            task.checkpoint_data["paused_at"] = datetime.utcnow().isoformat()
            self._update_task_in_db(task)
            logger.info(f"Task paused: {task_id}")
            
    async def resume_task(self, task_id: str):
        """태스크 재개"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.PAUSED:
            task.status = TaskStatus.PENDING
            await self.task_queues[task.priority].put(task_id)
            logger.info(f"Task resumed: {task_id}")
            
    async def get_metrics(self) -> Dict[str, Any]:
        """메트릭 조회"""
        total_tasks = len(self.tasks)
        status_counts = {}
        for task in self.tasks.values():
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
            
        queue_sizes = {
            priority.value: self.task_queues[priority].qsize() 
            for priority in TaskPriority
        }
        
        return {
            "total_tasks": total_tasks,
            "running_tasks": len(self.running_tasks),
            "status_counts": status_counts,
            "queue_sizes": queue_sizes,
            "workers": len(self.workers)
        }