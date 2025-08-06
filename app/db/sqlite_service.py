# app/db/sqlite_service.py - Job ID 불일치 완전 해결 버전
import aiosqlite
import pickle
import json
import uuid
import logging
import os
import traceback
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class SQLiteService:
    """SQLite 데이터베이스 서비스 클래스"""
    
    def __init__(self, db_path: str = None):
        # Railway 환경 호환성을 위한 데이터베이스 경로 설정
        if db_path:
            self.db_path = db_path
        else:
            # 환경변수 우선 사용
            if "DATABASE_PATH" in os.environ:
                self.db_path = os.environ["DATABASE_PATH"]
            elif "DATABASE_URL" in os.environ:
                # Railway에서 PostgreSQL URL이 있을 경우 (향후 확장용)
                self.db_path = "./airiss.db"  # SQLite fallback
            else:
                # 현재 디렉토리 기준 상대경로 사용 (인코딩 안전)
                try:
                    # 프로젝트 루트에서 airiss.db 사용
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(os.path.dirname(current_dir))  # app/db에서 2단계 위
                    self.db_path = os.path.join(project_root, "airiss.db")
                    # Windows/OneDrive 인코딩 안전성을 위한 경로 정규화
                    self.db_path = os.path.normpath(self.db_path)
                except Exception:
                    # 최종 fallback
                    self.db_path = "./airiss.db"
        
        logger.info(f"🗃️ SQLite 데이터베이스 경로: {self.db_path}")
        
    async def get_connection(self):
        """aiosqlite 연결 객체 반환 (with/as에서 사용 가능)"""
        return await aiosqlite.connect(self.db_path)

    async def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Files 테이블
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS files (
                        id TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        upload_time TIMESTAMP NOT NULL,
                        total_records INTEGER NOT NULL,
                        columns TEXT NOT NULL,
                        uid_columns TEXT NOT NULL,
                        opinion_columns TEXT NOT NULL,
                        quantitative_columns TEXT NOT NULL,
                        file_data BLOB NOT NULL
                    )
                """)
                
                # Jobs 테이블
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id TEXT PRIMARY KEY,
                        file_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        job_data TEXT NOT NULL,
                        FOREIGN KEY (file_id) REFERENCES files (id)
                    )
                """)
                
                # Results 테이블
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS results (
                        id TEXT PRIMARY KEY,
                        job_id TEXT NOT NULL,
                        uid TEXT NOT NULL,
                        result_data TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (job_id) REFERENCES jobs (id)
                    )
                """)
                
                await db.commit()
                logger.info("✅ SQLite 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 초기화 오류: {e}")
            raise

    async def save_file(self, file_data: Dict[str, Any]) -> str:
        """파일 정보를 데이터베이스에 저장"""
        try:
            file_id = str(uuid.uuid4())
            
            # DataFrame을 pickle로 직렬화
            df = file_data['dataframe']
            file_data_blob = pickle.dumps(df)
            
            # 데이터베이스 스키마에 맞는 구조로 저장
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO files (
                        id, filename, upload_time, total_records, 
                        columns, uid_columns, opinion_columns, 
                        quantitative_columns, file_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id,
                    file_data['filename'],
                    datetime.now().isoformat(),
                    file_data['total_records'],
                    json.dumps(file_data['columns']),
                    json.dumps(file_data['uid_columns']),
                    json.dumps(file_data['opinion_columns']),
                    json.dumps(file_data.get('quantitative_columns', [])),
                    file_data_blob
                ))
                await db.commit()
            
            logger.info(f"✅ 파일 저장 완료: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 오류: {e}")
            raise

    async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """파일 정보를 데이터베이스에서 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, filename, upload_time, total_records,
                           columns, uid_columns, opinion_columns,
                           quantitative_columns, file_data
                    FROM files WHERE id = ?
                """, (file_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    # bytes 변환 처리
                    file_data_blob = row[8]
                    if isinstance(file_data_blob, str):
                        # string인 경우 bytes로 변환
                        file_data_blob = file_data_blob.encode('latin1')
                    
                    # DataFrame 복원
                    df = pickle.loads(file_data_blob)
                    
                    return {
                        'id': row[0],
                        'filename': row[1],
                        'upload_time': row[2],
                        'total_records': row[3],
                        'columns': json.loads(row[4]),
                        'uid_columns': json.loads(row[5]),
                        'opinion_columns': json.loads(row[6]),
                        'quantitative_columns': json.loads(row[7]),
                        'dataframe': df
                    }
                    
        except Exception as e:
            logger.error(f"❌ 파일 조회 오류: {e}")
            raise

    async def delete_file(self, file_id: str) -> bool:
        """파일을 데이터베이스에서 삭제"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 관련 작업들도 함께 삭제
                await db.execute("DELETE FROM results WHERE job_id IN (SELECT id FROM jobs WHERE file_id = ?)", (file_id,))
                await db.execute("DELETE FROM jobs WHERE file_id = ?", (file_id,))
                await db.execute("DELETE FROM files WHERE id = ?", (file_id,))
                await db.commit()
                
                logger.info(f"✅ 파일 삭제 완료: {file_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 파일 삭제 오류: {e}")
            return False

    async def list_files(self, limit: int = 100) -> List[Dict[str, Any]]:
        """파일 목록 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, filename, upload_time, total_records
                    FROM files 
                    ORDER BY upload_time DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    return [
                        {
                            'id': row[0],
                            'filename': row[1],
                            'upload_time': row[2],
                            'total_records': row[3]
                        }
                        for row in rows
                    ]
                    
        except Exception as e:
            logger.error(f"❌ 파일 목록 조회 오류: {e}")
            return []

    # 🔥 핵심 수정: Job ID 불일치 완전 해결
    async def create_analysis_job(self, job_data: Dict[str, Any]) -> str:
        """분석 작업 생성 (Analysis API 전용) - Job ID 불일치 완전 해결"""
        try:
            # 🔥 1단계: 전달받은 job_id를 절대적으로 사용
            if 'job_id' in job_data and job_data['job_id']:
                job_id = str(job_data['job_id'])
                logger.debug(f"🎯 전달받은 job_id 사용: {job_id}")
            else:
                # job_id가 없을 경우만 새로 생성
                job_id = str(uuid.uuid4())
                job_data['job_id'] = job_id
                logger.debug(f"🆕 새로운 job_id 생성: {job_id}")
            
            # 🔥 2단계: status 필드 기본값 설정
            if 'status' not in job_data:
                job_data['status'] = 'created'
            
            # 🔥 3단계: 중복 검사 (선택적)
            async with aiosqlite.connect(self.db_path) as db:
                # 기존 job_id 확인
                async with db.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)) as cursor:
                    existing = await cursor.fetchone()
                    if existing:
                        error_msg = f"❌ 중복된 job_id: {job_id}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                
                # 🔥 4단계: DB에 저장 (job_id를 id 컬럼에 직접 저장)
                await db.execute("""
                    INSERT INTO jobs (
                        id, file_id, status, created_at, updated_at, job_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    job_id,
                    job_data['file_id'],
                    job_data['status'],
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    json.dumps(job_data)
                ))
                await db.commit()
                
                logger.info(f"✅ 분석 작업 생성 완료: {job_id}")
                return job_id
                
        except Exception as e:
            logger.error(f"❌ 분석 작업 생성 오류: {e}")
            raise

    async def get_analysis_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """분석 작업 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, file_id, status, created_at, updated_at, job_data
                    FROM jobs WHERE id = ?
                """, (job_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    job_data = json.loads(row[5])
                    job_data.update({
                        'id': row[0],
                        'file_id': row[1],
                        'status': row[2],
                        'created_at': row[3],
                        'updated_at': row[4]
                    })
                    
                    return job_data
                    
        except Exception as e:
            logger.error(f"❌ 분석 작업 조회 오류: {e}")
            return None

    async def update_analysis_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """분석 작업 업데이트"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 기존 job_data 가져오기
                async with db.execute("SELECT job_data FROM jobs WHERE id = ?", (job_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        return False
                    
                    job_data = json.loads(row[0])
                    job_data.update(updates)
                    job_data['updated_at'] = datetime.now().isoformat()
                
                # 업데이트된 job_data 저장
                await db.execute("""
                    UPDATE jobs SET status = ?, updated_at = ?, job_data = ?
                    WHERE id = ?
                """, (
                    job_data.get('status', 'unknown'),
                    job_data['updated_at'],
                    json.dumps(job_data),
                    job_id
                ))
                await db.commit()
                
                logger.info(f"✅ 분석 작업 업데이트 완료: {job_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 분석 작업 업데이트 오류: {e}")
            return False

    async def get_completed_analysis_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """완료된 분석 작업 목록 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, file_id, status, created_at, updated_at, job_data
                    FROM jobs 
                    WHERE status = 'completed'
                    ORDER BY updated_at DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    jobs = []
                    for row in rows:
                        job_data = json.loads(row[5])
                        job_data.update({
                            'id': row[0],
                            'file_id': row[1],
                            'status': row[2],
                            'created_at': row[3],
                            'updated_at': row[4]
                        })
                        jobs.append(job_data)
                    
                    return jobs
                    
        except Exception as e:
            logger.error(f"❌ 완료된 분석 작업 조회 오류: {e}")
            return []

    async def save_analysis_result(self, job_id: str, uid: str, result_data: Dict[str, Any]) -> bool:
        """분석 결과 저장"""
        try:
            result_id = str(uuid.uuid4())
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO results (
                        id, job_id, uid, result_data, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    result_id,
                    job_id,
                    uid,
                    json.dumps(result_data),
                    datetime.now().isoformat()
                ))
                await db.commit()
                
                logger.info(f"✅ 분석 결과 저장 완료: {result_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 분석 결과 저장 오류: {e}")
            return False

    async def get_analysis_results(self, job_id: str) -> List[Dict[str, Any]]:
        """분석 결과 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, job_id, uid, result_data, created_at
                    FROM results WHERE job_id = ?
                    ORDER BY created_at
                """, (job_id,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    results = []
                    for row in rows:
                        result_data = json.loads(row[3])
                        result_data.update({
                            'id': row[0],
                            'job_id': row[1],
                            'uid': row[2],
                            'created_at': row[4]
                        })
                        results.append(result_data)
                    
                    return results
                    
        except Exception as e:
            logger.error(f"❌ 분석 결과 조회 오류: {e}")
            return []

    # 기존 호환성 메서드들
    async def save_job(self, job_data: Dict[str, Any]) -> str:
        """기존 호환성을 위한 job 저장 메서드"""
        return await self.create_analysis_job(job_data)

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """기존 호환성을 위한 job 조회 메서드"""
        return await self.get_analysis_job(job_id)

    async def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """기존 호환성을 위한 job 업데이트 메서드"""
        return await self.update_analysis_job(job_id, updates)

    async def list_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 작업 목록 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, file_id, status, created_at, updated_at, job_data
                    FROM jobs 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    jobs = []
                    for row in rows:
                        job_data = json.loads(row[5])
                        job_data.update({
                            'id': row[0],
                            'file_id': row[1],
                            'status': row[2],
                            'created_at': row[3],
                            'updated_at': row[4]
                        })
                        jobs.append(job_data)
                    
                    return jobs
                    
        except Exception as e:
            logger.error(f"❌ 작업 목록 조회 오류: {e}")
            return []

    async def save_results(self, job_id: str, results: List[Dict[str, Any]]) -> bool:
        """여러 분석 결과 일괄 저장"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for result in results:
                    result_id = str(uuid.uuid4())
                    uid = result.get('uid', 'unknown')
                    
                    await db.execute("""
                        INSERT INTO results (
                            id, job_id, uid, result_data, created_at
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        result_id,
                        job_id,
                        uid,
                        json.dumps(result),
                        datetime.now().isoformat()
                    ))
                
                await db.commit()
                logger.info(f"✅ {len(results)}개 분석 결과 일괄 저장 완료")
                return True
                
        except Exception as e:
            logger.error(f"❌ 분석 결과 일괄 저장 오류: {e}")
            return False

    async def get_results(self, job_id: str) -> List[Dict[str, Any]]:
        """기존 호환성을 위한 결과 조회 메서드"""
        return await self.get_analysis_results(job_id)

    async def get_database_stats(self) -> Dict[str, Any]:
        """데이터베이스 통계 정보 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}
                
                # 파일 수
                async with db.execute("SELECT COUNT(*) FROM files") as cursor:
                    stats['total_files'] = (await cursor.fetchone())[0]
                
                # 작업 수
                async with db.execute("SELECT COUNT(*) FROM jobs") as cursor:
                    stats['total_jobs'] = (await cursor.fetchone())[0]
                
                # 결과 수
                async with db.execute("SELECT COUNT(*) FROM results") as cursor:
                    stats['total_results'] = (await cursor.fetchone())[0]
                
                # 상태별 작업 수
                async with db.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status") as cursor:
                    status_counts = await cursor.fetchall()
                    stats['jobs_by_status'] = {row[0]: row[1] for row in status_counts}
                
                return stats
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 통계 조회 오류: {e}")
            return {}

    async def cleanup_old_data(self, days: int = 30) -> bool:
        """오래된 데이터 정리"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                # 오래된 작업들 삭제
                await db.execute("DELETE FROM results WHERE job_id IN (SELECT id FROM jobs WHERE created_at < ?)", (cutoff_str,))
                await db.execute("DELETE FROM jobs WHERE created_at < ?", (cutoff_str,))
                await db.commit()
                
                logger.info(f"✅ {days}일 이전 데이터 정리 완료")
                return True
                
        except Exception as e:
            logger.error(f"❌ 데이터 정리 오류: {e}")
            return False 