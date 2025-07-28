import asyncpg
import json
import uuid
import pickle
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class PostgresService:
    """PostgreSQL(Neon) 데이터베이스 서비스 클래스"""
    
    def __init__(self, database_url: str):
        # SQLAlchemy URL을 asyncpg URL로 변환
        if database_url.startswith("postgresql+psycopg2://"):
            self.database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")
        else:
            self.database_url = database_url
        logger.info(f"🐘 PostgreSQL 연결 준비: {self.database_url.split('@')[1]}")  # 비밀번호 숨김
        
    async def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            conn = await asyncpg.connect(self.database_url)
            # Files 테이블
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    upload_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    total_records INTEGER NOT NULL,
                    columns JSONB NOT NULL,
                    uid_columns JSONB NOT NULL,
                    opinion_columns JSONB NOT NULL,
                    quantitative_columns JSONB NOT NULL,
                    file_data BYTEA
                )
            """)
            # Jobs 테이블
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    file_id TEXT NOT NULL REFERENCES files(id) ON DELETE CASCADE,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    job_data JSONB NOT NULL
                )
            """)
            # Results 테이블
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
                    uid TEXT NOT NULL,
                    result_data JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 인덱스 생성
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_file_id ON jobs(file_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_results_job_id ON results(job_id)")
            await conn.close()
            logger.info("✅ PostgreSQL 데이터베이스 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 초기화 오류: {e}")
            raise

    async def save_file(self, file_data: Dict[str, Any]) -> str:
        """파일 정보를 데이터베이스에 저장"""
        try:
            file_id = str(uuid.uuid4())
            df = file_data.get('dataframe')
            file_data_blob = pickle.dumps(df) if df is not None else None
            conn = await asyncpg.connect(self.database_url)
            try:
                await conn.execute("""
                    INSERT INTO files (
                        id, filename, upload_time, total_records, 
                        columns, uid_columns, opinion_columns, 
                        quantitative_columns, file_data
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, 
                    file_id,
                    file_data['filename'],
                    datetime.now(),
                    file_data['total_records'],
                    json.dumps(file_data['columns']),
                    json.dumps(file_data['uid_columns']),
                    json.dumps(file_data['opinion_columns']),
                    json.dumps(file_data.get('quantitative_columns', [])),
                    file_data_blob
                )
            finally:
                await conn.close()
            logger.info(f"✅ 파일 저장 완료: {file_id}")
            return file_id
        except Exception as e:
            logger.error(f"❌ 파일 저장 오류: {e}")
            raise

    async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """파일 정보를 데이터베이스에서 조회"""
        try:
            conn = await asyncpg.connect(self.database_url)
            try:
                row = await conn.fetchrow("""
                    SELECT id, filename, upload_time, total_records,
                           columns, uid_columns, opinion_columns,
                           quantitative_columns, file_data
                    FROM files WHERE id = $1
                """, file_id)
                if not row:
                    return None
                df = pickle.loads(row['file_data']) if row['file_data'] is not None else None
                return {
                    'id': row['id'],
                    'filename': row['filename'],
                    'upload_time': row['upload_time'].isoformat(),
                    'total_records': row['total_records'],
                    'columns': json.loads(row['columns']),
                    'uid_columns': json.loads(row['uid_columns']),
                    'opinion_columns': json.loads(row['opinion_columns']),
                    'quantitative_columns': json.loads(row['quantitative_columns']),
                    'dataframe': df
                }
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"❌ 파일 조회 오류: {e}")
            raise

    async def list_files(self, limit: int = 100) -> List[Dict[str, Any]]:
        """파일 목록 조회"""
        try:
            conn = await asyncpg.connect(self.database_url)
            try:
                rows = await conn.fetch("""
                    SELECT id, filename, upload_time, total_records
                    FROM files 
                    ORDER BY upload_time DESC 
                    LIMIT $1
                """, limit)
                return [
                    {
                        'id': row['id'],
                        'filename': row['filename'],
                        'upload_time': row['upload_time'].isoformat() if row['upload_time'] else None,
                        'total_records': row['total_records']
                    }
                    for row in rows
                ]
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"❌ 파일 목록 조회 오류: {e}")
            return []

    async def create_analysis_job(self, job_data: Dict[str, Any]) -> str:
        """분석 작업 생성"""
        try:
            job_id = job_data.get('job_id', str(uuid.uuid4()))
            status = job_data.get('status', 'created')
            conn = await asyncpg.connect(self.database_url)
            try:
                await conn.execute("""
                    INSERT INTO jobs (
                        id, file_id, status, created_at, updated_at, job_data
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                """,
                    job_id,
                    job_data['file_id'],
                    status,
                    datetime.now(),
                    datetime.now(),
                    json.dumps(job_data)
                )
            finally:
                await conn.close()
            logger.info(f"✅ 분석 작업 생성 완료: {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"❌ 분석 작업 생성 오류: {e}")
            raise

    async def get_analysis_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """분석 작업 조회"""
        try:
            conn = await asyncpg.connect(self.database_url)
            try:
                row = await conn.fetchrow("""
                    SELECT id, file_id, status, created_at, updated_at, job_data
                    FROM jobs WHERE id = $1
                """, job_id)
                if not row:
                    return None
                job_data = json.loads(row['job_data'])
                job_data.update({
                    'job_id': row['id'],
                    'file_id': row['file_id'],
                    'status': row['status'],
                    'created_at': row['created_at'].isoformat(),
                    'updated_at': row['updated_at'].isoformat()
                })
                return job_data
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"❌ 분석 작업 조회 오류: {e}")
            return None

    async def update_analysis_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """분석 작업 업데이트"""
        try:
            conn = await asyncpg.connect(self.database_url)
            try:
                # 기존 job_data 조회
                row = await conn.fetchrow("SELECT job_data FROM jobs WHERE id = $1", job_id)
                if not row:
                    return False
                job_data = json.loads(row['job_data'])
                job_data.update(updates)
                status = job_data.get('status', 'completed')
                await conn.execute("""
                    UPDATE jobs 
                    SET status = $1, updated_at = $2, job_data = $3
                    WHERE id = $4
                """,
                    status,
                    datetime.now(),
                    json.dumps(job_data),
                    job_id
                )
            finally:
                await conn.close()
            logger.debug(f"✅ 분석 작업 업데이트 완료: {job_id}")
            return True
        except Exception as e:
            logger.error(f"❌ 분석 작업 업데이트 오류: {e}")
            return False
    # 나머지 메서드들도 동일한 패턴으로 구현
    # list_files, delete_file, save_analysis_result, get_analysis_results 등
    # SQLite 버전과 동일한 인터페이스 유지, asyncpg 문법만 사용 