"""
AIRISS v4 데이터베이스 마이그레이션 스크립트
results + analysis_results 테이블을 analysis_results_v2로 통합

실행 순서:
1. 백업
2. 새 테이블 생성
3. 데이터 마이그레이션
4. 뷰 생성
5. 검증
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
import json
from sqlalchemy import text
from app.db import db_service
import os
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigration:
    def __init__(self):
        self.db_service = db_service
        self.backup_dir = "./database_migration/backups"
        self.migration_log = []
        
    async def run_migration(self):
        """전체 마이그레이션 프로세스 실행"""
        logger.info("=== AIRISS v4 데이터베이스 마이그레이션 시작 ===")
        
        try:
            # 1. 사전 검사
            await self.pre_migration_check()
            
            # 2. 백업
            await self.backup_data()
            
            # 3. 새 테이블 생성
            await self.create_new_schema()
            
            # 4. 데이터 마이그레이션
            await self.migrate_data()
            
            # 5. 뷰 생성
            await self.create_compatibility_views()
            
            # 6. 검증
            await self.verify_migration()
            
            # 7. 마이그레이션 로그 저장
            await self.save_migration_log()
            
            logger.info("=== 마이그레이션 성공적으로 완료 ===")
            return True
            
        except Exception as e:
            logger.error(f"마이그레이션 실패: {e}")
            await self.rollback()
            return False
    
    async def pre_migration_check(self):
        """마이그레이션 전 사전 검사"""
        logger.info("1. 사전 검사 시작...")
        
        db = self.db_service.get_session()
        try:
            # 현재 데이터 수 확인
            results_count = db.execute(text("SELECT COUNT(*) FROM results")).scalar()
            analysis_results_count = db.execute(text("SELECT COUNT(*) FROM analysis_results")).scalar()
            
            logger.info(f"  - results 테이블: {results_count}개 레코드")
            logger.info(f"  - analysis_results 테이블: {analysis_results_count}개 레코드")
            
            # 중복 체크
            check_sql = """
                SELECT COUNT(*) FROM results r 
                WHERE EXISTS (
                    SELECT 1 FROM analysis_results ar 
                    WHERE ar.uid = r.uid
                )
            """
            duplicates = db.execute(text(check_sql)).scalar()
            logger.info(f"  - 중복 가능성 있는 레코드: {duplicates}개")
            
            self.migration_log.append({
                "step": "pre_check",
                "results_count": results_count,
                "analysis_results_count": analysis_results_count,
                "duplicates": duplicates,
                "timestamp": datetime.now().isoformat()
            })
            
        finally:
            db.close()
    
    async def backup_data(self):
        """데이터 백업"""
        logger.info("2. 데이터 백업 시작...")
        
        os.makedirs(self.backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        db = self.db_service.get_session()
        try:
            # results 테이블 백업
            results_data = db.execute(text("SELECT * FROM results")).fetchall()
            results_backup = []
            for row in results_data:
                results_backup.append(dict(row._mapping))
            
            with open(f"{self.backup_dir}/results_backup_{timestamp}.json", "w", encoding='utf-8') as f:
                json.dump(results_backup, f, default=str, ensure_ascii=False, indent=2)
            
            # analysis_results 테이블 백업
            analysis_data = db.execute(text("SELECT * FROM analysis_results")).fetchall()
            analysis_backup = []
            for row in analysis_data:
                analysis_backup.append(dict(row._mapping))
            
            with open(f"{self.backup_dir}/analysis_results_backup_{timestamp}.json", "w", encoding='utf-8') as f:
                json.dump(analysis_backup, f, default=str, ensure_ascii=False, indent=2)
            
            logger.info(f"  - 백업 완료: {self.backup_dir}")
            
            self.migration_log.append({
                "step": "backup",
                "results_backed_up": len(results_backup),
                "analysis_results_backed_up": len(analysis_backup),
                "backup_path": self.backup_dir,
                "timestamp": datetime.now().isoformat()
            })
            
        finally:
            db.close()
    
    async def create_new_schema(self):
        """새로운 통합 스키마 생성"""
        logger.info("3. 새 스키마 생성...")
        
        db = self.db_service.get_session()
        try:
            # PostgreSQL과 SQLite 구분
            db_url = str(self.db_service.engine.url)
            is_postgres = 'postgresql' in db_url
            
            if is_postgres:
                # PostgreSQL용 스키마
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS analysis_results_v2 (
                    id SERIAL PRIMARY KEY,
                    analysis_id VARCHAR(36) UNIQUE NOT NULL,
                    job_id VARCHAR(36) NOT NULL,
                    uid VARCHAR(100) NOT NULL,
                    file_id VARCHAR(100),
                    filename VARCHAR(500),
                    opinion TEXT,
                    overall_score REAL,
                    text_score REAL,
                    quantitative_score REAL,
                    confidence REAL,
                    ok_grade VARCHAR(10),
                    grade_description TEXT,
                    percentile REAL,
                    dimension_scores JSONB,
                    ai_feedback JSONB,
                    ai_strengths TEXT,
                    ai_weaknesses TEXT,
                    ai_recommendations JSONB,
                    ai_error TEXT,
                    result_data JSONB,
                    analysis_mode VARCHAR(20) DEFAULT 'hybrid',
                    version VARCHAR(10) DEFAULT '4.0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            else:
                # SQLite용 스키마
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS analysis_results_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id VARCHAR(36) UNIQUE NOT NULL,
                    job_id VARCHAR(36) NOT NULL,
                    uid VARCHAR(100) NOT NULL,
                    file_id VARCHAR(100),
                    filename VARCHAR(500),
                    opinion TEXT,
                    overall_score REAL,
                    text_score REAL,
                    quantitative_score REAL,
                    confidence REAL,
                    ok_grade VARCHAR(10),
                    grade_description TEXT,
                    percentile REAL,
                    dimension_scores TEXT,
                    ai_feedback TEXT,
                    ai_strengths TEXT,
                    ai_weaknesses TEXT,
                    ai_recommendations TEXT,
                    ai_error TEXT,
                    result_data TEXT,
                    analysis_mode VARCHAR(20) DEFAULT 'hybrid',
                    version VARCHAR(10) DEFAULT '4.0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            
            db.execute(text(create_table_sql))
            
            # 인덱스 생성
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_analysis_results_v2_job_id ON analysis_results_v2(job_id)",
                "CREATE INDEX IF NOT EXISTS idx_analysis_results_v2_uid ON analysis_results_v2(uid)",
                "CREATE INDEX IF NOT EXISTS idx_analysis_results_v2_created_at ON analysis_results_v2(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_analysis_results_v2_overall_score ON analysis_results_v2(overall_score)"
            ]
            
            for index_sql in indexes:
                db.execute(text(index_sql))
            
            db.commit()
            logger.info("  - 새 테이블 및 인덱스 생성 완료")
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def migrate_data(self):
        """데이터 마이그레이션"""
        logger.info("4. 데이터 마이그레이션 시작...")
        
        db = self.db_service.get_session()
        migrated_count = 0
        
        try:
            # 1. analysis_results 테이블 데이터 마이그레이션
            logger.info("  - analysis_results 데이터 마이그레이션...")
            
            ar_data = db.execute(text("SELECT * FROM analysis_results")).fetchall()
            
            for row in ar_data:
                data = dict(row._mapping)
                
                # job_id 찾기 (uid와 created_at 기준)
                job_id_result = db.execute(text("""
                    SELECT job_id FROM results 
                    WHERE uid = :uid 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """), {"uid": data['uid']}).fetchone()
                
                job_id = job_id_result[0] if job_id_result else data.get('file_id', '')
                
                insert_sql = """
                    INSERT INTO analysis_results_v2 (
                        analysis_id, job_id, uid, file_id, filename, opinion,
                        overall_score, text_score, quantitative_score, confidence,
                        ok_grade, grade_description, percentile,
                        dimension_scores, ai_feedback, ai_strengths, ai_weaknesses,
                        ai_recommendations, analysis_mode, version,
                        created_at, updated_at
                    ) VALUES (
                        :analysis_id, :job_id, :uid, :file_id, :filename, :opinion,
                        :overall_score, :text_score, :quantitative_score, :confidence,
                        :ok_grade, :grade_description, :percentile,
                        :dimension_scores, :ai_feedback, :ai_strengths, :ai_weaknesses,
                        :ai_recommendations, :analysis_mode, :version,
                        :created_at, :updated_at
                    )
                """
                
                params = {
                    'analysis_id': data['analysis_id'],
                    'job_id': job_id,
                    'uid': data['uid'],
                    'file_id': data.get('file_id'),
                    'filename': data.get('filename'),
                    'opinion': data.get('opinion'),
                    'overall_score': data.get('hybrid_score'),
                    'text_score': data.get('text_score'),
                    'quantitative_score': data.get('quantitative_score'),
                    'confidence': data.get('confidence'),
                    'ok_grade': data.get('ok_grade'),
                    'grade_description': data.get('grade_description'),
                    'percentile': 0,  # 나중에 계산
                    'dimension_scores': json.dumps(data.get('dimension_scores', {})) if isinstance(data.get('dimension_scores'), dict) else (data.get('dimension_scores') or '{}'),
                    'ai_feedback': json.dumps(data.get('ai_feedback', {})) if isinstance(data.get('ai_feedback'), dict) else (json.dumps({}) if not data.get('ai_feedback') else data.get('ai_feedback')),
                    'ai_strengths': data.get('ai_strengths', ''),
                    'ai_weaknesses': data.get('ai_weaknesses', ''),
                    'ai_recommendations': json.dumps(data.get('ai_recommendations', [])) if isinstance(data.get('ai_recommendations'), list) else (json.dumps([]) if not data.get('ai_recommendations') else data.get('ai_recommendations')),
                    'analysis_mode': data.get('analysis_mode', 'hybrid'),
                    'version': data.get('version', '4.0'),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at')
                }
                
                db.execute(text(insert_sql), params)
                migrated_count += 1
            
            # 2. results 테이블의 고유 데이터 마이그레이션
            logger.info("  - results 테이블 고유 데이터 확인...")
            
            unique_results = db.execute(text("""
                SELECT r.* FROM results r
                LEFT JOIN analysis_results ar ON r.uid = ar.uid
                WHERE ar.uid IS NULL
            """)).fetchall()
            
            for row in unique_results:
                data = dict(row._mapping)
                
                # analysis_id 생성
                import uuid
                analysis_id = str(uuid.uuid4())
                
                # result_data에서 정보 추출
                result_data = {}
                if data.get('result_data'):
                    try:
                        result_data = json.loads(data['result_data']) if isinstance(data['result_data'], str) else data['result_data']
                    except:
                        pass
                
                insert_sql = """
                    INSERT INTO analysis_results_v2 (
                        analysis_id, job_id, uid, overall_score, text_score,
                        quantitative_score, confidence, ok_grade, percentile,
                        dimension_scores, result_data, created_at
                    ) VALUES (
                        :analysis_id, :job_id, :uid, :overall_score, :text_score,
                        :quantitative_score, :confidence, :ok_grade, :percentile,
                        :dimension_scores, :result_data, :created_at
                    )
                """
                
                params = {
                    'analysis_id': analysis_id,
                    'job_id': data['job_id'],
                    'uid': data['uid'],
                    'overall_score': data.get('overall_score'),
                    'text_score': data.get('text_score'),
                    'quantitative_score': data.get('quantitative_score'),
                    'confidence': data.get('confidence'),
                    'ok_grade': data.get('grade'),
                    'percentile': data.get('percentile'),
                    'dimension_scores': data.get('dimension_scores'),
                    'result_data': data.get('result_data'),
                    'created_at': data.get('created_at')
                }
                
                db.execute(text(insert_sql), params)
                migrated_count += 1
            
            db.commit()
            logger.info(f"  - 총 {migrated_count}개 레코드 마이그레이션 완료")
            
            self.migration_log.append({
                "step": "data_migration",
                "migrated_count": migrated_count,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def create_compatibility_views(self):
        """호환성을 위한 뷰 생성"""
        logger.info("5. 호환성 뷰 생성...")
        
        db = self.db_service.get_session()
        try:
            # 기존 뷰 삭제
            db.execute(text("DROP VIEW IF EXISTS results_view"))
            db.execute(text("DROP VIEW IF EXISTS analysis_results_view"))
            
            # results 호환 뷰
            results_view_sql = """
                CREATE VIEW results_view AS
                SELECT 
                    CAST(id AS TEXT) as id,
                    job_id,
                    uid,
                    overall_score,
                    ok_grade as grade,
                    percentile,
                    text_score,
                    quantitative_score,
                    confidence,
                    dimension_scores,
                    result_data,
                    created_at
                FROM analysis_results_v2
            """
            
            # analysis_results 호환 뷰
            analysis_results_view_sql = """
                CREATE VIEW analysis_results_view AS
                SELECT 
                    id,
                    analysis_id,
                    uid,
                    file_id,
                    filename,
                    opinion,
                    overall_score as hybrid_score,
                    text_score,
                    quantitative_score,
                    ok_grade,
                    grade_description,
                    confidence,
                    dimension_scores,
                    ai_feedback,
                    ai_strengths,
                    ai_weaknesses,
                    ai_recommendations,
                    analysis_mode,
                    version,
                    created_at,
                    updated_at
                FROM analysis_results_v2
            """
            
            db.execute(text(results_view_sql))
            db.execute(text(analysis_results_view_sql))
            db.commit()
            
            logger.info("  - 호환성 뷰 생성 완료")
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def verify_migration(self):
        """마이그레이션 검증"""
        logger.info("6. 마이그레이션 검증...")
        
        db = self.db_service.get_session()
        try:
            # 새 테이블 레코드 수
            new_count = db.execute(text("SELECT COUNT(*) FROM analysis_results_v2")).scalar()
            
            # 원본 테이블들의 총 레코드 수
            results_count = db.execute(text("SELECT COUNT(*) FROM results")).scalar()
            analysis_count = db.execute(text("SELECT COUNT(*) FROM analysis_results")).scalar()
            
            # 뷰 작동 확인
            view_count = db.execute(text("SELECT COUNT(*) FROM results_view")).scalar()
            
            logger.info(f"  - 새 테이블 레코드: {new_count}")
            logger.info(f"  - 원본 테이블 총합: {results_count + analysis_count}")
            logger.info(f"  - 뷰 레코드: {view_count}")
            
            # 데이터 무결성 확인
            sample_check = db.execute(text("""
                SELECT uid, overall_score, ok_grade 
                FROM analysis_results_v2 
                LIMIT 5
            """)).fetchall()
            
            logger.info("  - 샘플 데이터 확인:")
            for row in sample_check:
                logger.info(f"    UID: {row.uid}, Score: {row.overall_score}, Grade: {row.ok_grade}")
            
            self.migration_log.append({
                "step": "verification",
                "new_table_count": new_count,
                "original_total": results_count + analysis_count,
                "view_count": view_count,
                "verified": True,
                "timestamp": datetime.now().isoformat()
            })
            
        finally:
            db.close()
    
    async def save_migration_log(self):
        """마이그레이션 로그 저장"""
        logger.info("7. 마이그레이션 로그 저장...")
        
        log_file = f"{self.backup_dir}/migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, "w", encoding='utf-8') as f:
            json.dump(self.migration_log, f, ensure_ascii=False, indent=2)
        
        logger.info(f"  - 로그 저장 완료: {log_file}")
    
    async def rollback(self):
        """롤백 (필요시)"""
        logger.error("롤백 시작...")
        
        db = self.db_service.get_session()
        try:
            # 새 테이블 삭제
            db.execute(text("DROP TABLE IF EXISTS analysis_results_v2"))
            db.execute(text("DROP VIEW IF EXISTS results_view"))
            db.execute(text("DROP VIEW IF EXISTS analysis_results_view"))
            db.commit()
            
            logger.info("  - 롤백 완료")
            
        except Exception as e:
            logger.error(f"롤백 실패: {e}")
        finally:
            db.close()


async def main():
    """메인 실행 함수"""
    migration = DatabaseMigration()
    
    # 사용자 확인
    print("\n=== AIRISS v4 데이터베이스 마이그레이션 ===")
    print("이 작업은 다음을 수행합니다:")
    print("1. 현재 데이터 백업")
    print("2. 새로운 통합 테이블 생성")
    print("3. 데이터 마이그레이션")
    print("4. 호환성 뷰 생성")
    print("\n계속하시겠습니까? (yes/no): ", end="")
    
    confirm = input().strip().lower()
    if confirm != 'yes':
        print("마이그레이션을 취소합니다.")
        return
    
    # 마이그레이션 실행
    success = await migration.run_migration()
    
    if success:
        print("\n✅ 마이그레이션이 성공적으로 완료되었습니다!")
        print("다음 단계:")
        print("1. 애플리케이션 코드를 새 스키마에 맞게 업데이트")
        print("2. 테스트 실행")
        print("3. 문제가 없으면 기존 테이블 삭제")
    else:
        print("\n❌ 마이그레이션이 실패했습니다. 로그를 확인하세요.")


if __name__ == "__main__":
    asyncio.run(main())