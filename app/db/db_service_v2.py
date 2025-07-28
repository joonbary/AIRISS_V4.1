"""
AIRISS v4 데이터베이스 서비스 v2
통합 스키마(analysis_results_v2)를 사용하는 새로운 서비스 레이어
"""

import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, get_db

logger = logging.getLogger(__name__)


class DatabaseServiceV2:
    """통합 스키마를 사용하는 데이터베이스 서비스"""
    
    def __init__(self):
        self.SessionLocal = SessionLocal
        self._use_new_schema = True  # 새 스키마 사용 플래그
        
    def get_session(self) -> Session:
        """새 DB 세션 생성"""
        return self.SessionLocal()
    
    def _get_table_name(self, base_name: str) -> str:
        """테이블 이름 결정 (마이그레이션 호환성)"""
        if self._use_new_schema and base_name in ['results', 'analysis_results']:
            return 'analysis_results_v2'
        return base_name
    
    async def save_analysis_result(self, result_data: Dict[str, Any]) -> str:
        """분석 결과 저장 (통합 테이블 사용)"""
        db = self.get_session()
        try:
            # numpy 타입 변환
            def safe_convert_numpy_types(value):
                import numpy as np
                if isinstance(value, np.integer):
                    return int(value)
                elif isinstance(value, np.floating):
                    return float(value)
                elif isinstance(value, np.ndarray):
                    return value.tolist()
                elif isinstance(value, dict):
                    return {k: safe_convert_numpy_types(v) for k, v in value.items()}
                elif isinstance(value, list):
                    return [safe_convert_numpy_types(item) for item in value]
                else:
                    return value
            
            safe_result_data = safe_convert_numpy_types(result_data)
            
            # 분석 ID 생성
            analysis_id = str(uuid.uuid4())
            
            # UID 추출
            uid = (
                safe_result_data.get('UID') or 
                safe_result_data.get('uid') or 
                safe_result_data.get('employee_uid') or 
                'UNKNOWN'
            )
            
            # 디버깅 로그
            logger.info(f"[DB Save] UID 추출: UID={safe_result_data.get('UID')}, uid={safe_result_data.get('uid')}, 최종={uid}")
            logger.info(f"[DB Save] 점수: overall_score={safe_result_data.get('overall_score')}, AIRISS_v4_종합점수={safe_result_data.get('AIRISS_v4_종합점수')}")
            
            # 데이터 준비
            insert_data = {
                'analysis_id': analysis_id,
                'job_id': safe_result_data.get('job_id', ''),
                'uid': uid,
                'file_id': safe_result_data.get('file_id', ''),
                'filename': safe_result_data.get('filename', ''),
                'opinion': safe_result_data.get('원본의견', '') or safe_result_data.get('opinion', ''),
                
                # 점수 매핑 (호환성)
                'overall_score': safe_result_data.get('AIRISS_v4_종합점수') or safe_result_data.get('overall_score') or safe_result_data.get('hybrid_score'),
                'text_score': safe_result_data.get('텍스트_종합점수') or safe_result_data.get('text_score'),
                'quantitative_score': safe_result_data.get('정량_종합점수') or safe_result_data.get('quantitative_score'),
                'confidence': safe_result_data.get('분석신뢰도') or safe_result_data.get('confidence'),
                
                # 등급 정보
                'ok_grade': safe_result_data.get('OK등급') or safe_result_data.get('ok_grade'),
                'grade_description': safe_result_data.get('등급설명') or safe_result_data.get('grade_description'),
                'percentile': self._extract_percentile(safe_result_data.get('백분위', '')),
                
                # 상세 분석
                'dimension_scores': json.dumps(safe_result_data.get('dimension_scores', {})),
                
                # AI 분석 결과
                'ai_feedback': json.dumps({
                    'feedback': safe_result_data.get('AI_종합피드백', ''),
                    'generated': bool(safe_result_data.get('AI_종합피드백'))
                }),
                'ai_strengths': safe_result_data.get('AI_핵심강점', ''),
                'ai_weaknesses': safe_result_data.get('AI_개선영역', ''),
                'ai_recommendations': json.dumps(self._parse_recommendations(safe_result_data.get('AI_실행계획', ''))),
                'ai_error': safe_result_data.get('AI_피드백_오류', ''),
                
                # 전체 데이터 저장
                'result_data': json.dumps(safe_result_data),
                
                # 메타데이터
                'analysis_mode': safe_result_data.get('분석모드', 'hybrid'),
                'version': safe_result_data.get('version', '4.0'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # 통합 테이블에 저장
            table_name = self._get_table_name('analysis_results')
            
            db.execute(text(f"""
                INSERT INTO {table_name} (
                    analysis_id, job_id, uid, file_id, filename, opinion,
                    overall_score, text_score, quantitative_score, confidence,
                    ok_grade, grade_description, percentile,
                    dimension_scores, ai_feedback, ai_strengths, ai_weaknesses,
                    ai_recommendations, ai_error, result_data,
                    analysis_mode, version, created_at, updated_at
                ) VALUES (
                    :analysis_id, :job_id, :uid, :file_id, :filename, :opinion,
                    :overall_score, :text_score, :quantitative_score, :confidence,
                    :ok_grade, :grade_description, :percentile,
                    :dimension_scores, :ai_feedback, :ai_strengths, :ai_weaknesses,
                    :ai_recommendations, :ai_error, :result_data,
                    :analysis_mode, :version, :created_at, :updated_at
                )
            """), insert_data)
            
            db.commit()
            logger.info(f"분석 결과 저장 성공: analysis_id {analysis_id}")
            return analysis_id
            
        except Exception as e:
            db.rollback()
            logger.error(f"분석 결과 저장 실패: {e}")
            raise e
        finally:
            db.close()
    
    async def get_analysis_results(self, job_id: str = None, file_id: str = None, 
                                 uid: str = None) -> List[Dict[str, Any]]:
        """분석 결과 조회 (통합 테이블 사용)"""
        db = self.get_session()
        try:
            table_name = self._get_table_name('analysis_results')
            
            # 조건 구성
            where_clauses = []
            params = {}
            
            if job_id:
                where_clauses.append("job_id = :job_id")
                params['job_id'] = job_id
            if file_id:
                where_clauses.append("file_id = :file_id")
                params['file_id'] = file_id
            if uid:
                where_clauses.append("uid = :uid")
                params['uid'] = uid
            
            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
            
            # 쿼리 실행
            sql = f"""
                SELECT * FROM {table_name} 
                {where_sql} 
                ORDER BY created_at DESC
            """
            
            results = db.execute(text(sql), params).fetchall()
            
            # 결과 변환
            result_list = []
            for row in results:
                result_dict = dict(row._mapping)
                
                # datetime 변환
                for key, value in result_dict.items():
                    if isinstance(value, datetime):
                        result_dict[key] = value.isoformat()
                
                # JSON 필드 파싱
                for json_field in ['dimension_scores', 'ai_feedback', 'ai_recommendations', 'result_data']:
                    if json_field in result_dict and isinstance(result_dict[json_field], str):
                        try:
                            result_dict[json_field] = json.loads(result_dict[json_field])
                        except:
                            pass
                
                result_list.append(result_dict)
            
            return result_list
            
        except Exception as e:
            logger.error(f"분석 결과 조회 실패: {e}")
            raise e
        finally:
            db.close()
    
    async def get_results_for_download(self, job_id: str) -> List[Dict[str, Any]]:
        """다운로드용 결과 조회 (호환성 유지)"""
        results = await self.get_analysis_results(job_id=job_id)
        
        # 기존 API와의 호환성을 위한 필드 매핑
        formatted_results = []
        for result in results:
            # result_data가 있으면 그것을 사용, 없으면 현재 데이터 사용
            if result.get('result_data') and isinstance(result['result_data'], dict):
                formatted_result = result['result_data']
            else:
                # 필드 매핑
                formatted_result = {
                    'UID': result.get('uid'),
                    'AIRISS_v4_종합점수': result.get('overall_score'),
                    'OK등급': result.get('ok_grade'),
                    '등급설명': result.get('grade_description'),
                    '백분위': f"상위 {100 - (result.get('percentile', 50))}%",
                    '분석신뢰도': result.get('confidence'),
                    
                    # AI 분석 결과
                    'AI_종합피드백': result.get('ai_feedback', {}).get('feedback', '') if isinstance(result.get('ai_feedback'), dict) else '',
                    'AI_핵심강점': result.get('ai_strengths', ''),
                    'AI_개선영역': result.get('ai_weaknesses', ''),
                    'AI_실행계획': '\n'.join(result.get('ai_recommendations', [])) if isinstance(result.get('ai_recommendations'), list) else '',
                    
                    # 기타 정보
                    '원본의견': result.get('opinion', ''),
                    '분석일시': result.get('created_at', ''),
                    '분석모드': result.get('analysis_mode', 'hybrid')
                }
            
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def _extract_percentile(self, percentile_str: str) -> float:
        """백분위 문자열에서 숫자 추출"""
        if not percentile_str:
            return 50.0
        
        # "상위 20%" -> 20.0
        import re
        match = re.search(r'(\d+)', percentile_str)
        if match:
            return float(match.group(1))
        return 50.0
    
    def _parse_recommendations(self, recommendations: str) -> List[str]:
        """AI 추천사항 파싱"""
        if not recommendations:
            return []
        
        if isinstance(recommendations, list):
            return recommendations
        
        # 문자열인 경우 줄바꿈으로 분리
        lines = recommendations.strip().split('\n')
        return [line.strip() for line in lines if line.strip()]
    
    async def migrate_to_new_schema(self):
        """기존 테이블에서 새 스키마로 마이그레이션"""
        # migration_script.py의 DatabaseMigration 클래스 사용
        from database_migration.migration_script import DatabaseMigration
        migration = DatabaseMigration()
        return await migration.run_migration()


# 전역 인스턴스
db_service_v2 = DatabaseServiceV2()

# 기존 코드와의 호환성을 위한 별칭
# 점진적 마이그레이션을 위해 기존 함수 시그니처 유지
async def save_analysis_result_v2(result_data: Dict[str, Any]) -> str:
    """호환성 함수"""
    return await db_service_v2.save_analysis_result(result_data)

async def get_analysis_results_v2(job_id: str = None, **kwargs) -> List[Dict[str, Any]]:
    """호환성 함수"""
    return await db_service_v2.get_analysis_results(job_id=job_id, **kwargs)