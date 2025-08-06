"""
Analysis Repository
분석 결과 관련 데이터베이스 작업
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class AnalysisRepository:
    """분석 결과 리포지토리"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_job(self, job_data: Dict[str, Any]) -> str:
        """분석 작업 생성"""
        job_id = job_data.get('job_id', str(uuid.uuid4()))
        
        sql = text("""
            INSERT INTO jobs (
                id, file_id, status, sample_size, analysis_mode,
                enable_ai_feedback, openai_model, max_tokens,
                start_time, progress, total_records, processed_records,
                failed_records, job_data, created_at, updated_at
            ) VALUES (
                :id, :file_id, :status, :sample_size, :analysis_mode,
                :enable_ai_feedback, :openai_model, :max_tokens,
                :start_time, :progress, :total_records, :processed_records,
                :failed_records, :job_data, :created_at, :updated_at
            )
        """)
        
        self.db.execute(sql, {
            'id': job_id,
            'file_id': job_data['file_id'],
            'status': job_data.get('status', 'created'),
            'sample_size': job_data.get('sample_size'),
            'analysis_mode': job_data.get('analysis_mode', 'hybrid'),
            'enable_ai_feedback': job_data.get('enable_ai_feedback', False),
            'openai_model': job_data.get('openai_model'),
            'max_tokens': job_data.get('max_tokens'),
            'start_time': datetime.utcnow(),
            'progress': 0.0,
            'total_records': job_data.get('total_records', 0),
            'processed_records': 0,
            'failed_records': 0,
            'job_data': json.dumps(job_data),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        self.db.commit()
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """작업 조회"""
        result = self.db.execute(
            text("SELECT * FROM jobs WHERE id = :job_id"),
            {'job_id': job_id}
        ).fetchone()
        
        if result:
            job_dict = dict(result._mapping)
            # datetime to string conversion
            for key, value in job_dict.items():
                if isinstance(value, datetime):
                    job_dict[key] = value.isoformat()
            return job_dict
        return None
    
    def update_job(self, job_id: str, update_data: Dict[str, Any]) -> bool:
        """작업 상태 업데이트"""
        update_fields = []
        params = {'job_id': job_id, 'updated_at': datetime.utcnow()}
        
        for key, value in update_data.items():
            if key in ['status', 'progress', 'processed_records', 'failed_records', 'error', 'end_time']:
                update_fields.append(f"{key} = :{key}")
                params[key] = value
        
        if not update_fields:
            return False
        
        update_fields.append("updated_at = :updated_at")
        
        query = f"UPDATE jobs SET {', '.join(update_fields)} WHERE id = :job_id"
        result = self.db.execute(text(query), params)
        self.db.commit()
        
        return result.rowcount > 0
    
    def save_result(self, result_data: Dict[str, Any]) -> str:
        """분석 결과 저장"""
        # numpy type conversion
        def safe_convert(value):
            import numpy as np
            if isinstance(value, np.integer):
                return int(value)
            elif isinstance(value, np.floating):
                return float(value)
            elif isinstance(value, np.ndarray):
                return value.tolist()
            elif isinstance(value, dict):
                return {k: safe_convert(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [safe_convert(item) for item in value]
            return value
        
        safe_data = safe_convert(result_data)
        
        # Extract UID
        uid = (
            safe_data.get('uid') or
            safe_data.get('UID') or
            safe_data.get('사번') or
            safe_data.get('employee_id')
        )
        
        if not uid:
            logger.warning(f"UID not found in result data")
            return None
        
        analysis_id = safe_data.get('analysis_id', str(uuid.uuid4()))
        
        sql = text("""
            INSERT INTO analysis_results_v2 (
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
        """)
        
        self.db.execute(sql, {
            'analysis_id': analysis_id,
            'job_id': safe_data.get('job_id'),
            'uid': uid,
            'file_id': safe_data.get('file_id', ''),
            'filename': safe_data.get('filename', ''),
            'opinion': safe_data.get('opinion', ''),
            'overall_score': safe_data.get('hybrid_score'),
            'text_score': safe_data.get('text_score'),
            'quantitative_score': safe_data.get('quantitative_score'),
            'confidence': safe_data.get('confidence'),
            'ok_grade': safe_data.get('ok_grade') or safe_data.get('OK등급', ''),
            'grade_description': safe_data.get('grade_description') or safe_data.get('등급설명', ''),
            'percentile': safe_data.get('percentile', 50.0),
            'dimension_scores': json.dumps(safe_data.get('dimension_scores', {})),
            'ai_feedback': json.dumps(safe_data.get('ai_feedback', {})),
            'ai_strengths': safe_data.get('ai_strengths', ''),
            'ai_weaknesses': safe_data.get('ai_weaknesses', ''),
            'ai_recommendations': json.dumps(safe_data.get('ai_recommendations', [])),
            'ai_error': safe_data.get('ai_error', ''),
            'result_data': json.dumps(safe_data),
            'analysis_mode': safe_data.get('analysis_mode', 'hybrid'),
            'version': safe_data.get('version', '4.0'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        self.db.commit()
        logger.info(f"Analysis result saved: {analysis_id}")
        
        return analysis_id
    
    def get_results(self, job_id: str = None, file_id: str = None, 
                   uid: str = None) -> List[Dict[str, Any]]:
        """분석 결과 조회"""
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
        sql = f"SELECT * FROM analysis_results_v2 {where_sql} ORDER BY created_at"
        
        results = self.db.execute(text(sql), params).fetchall()
        
        result_list = []
        for row in results:
            result_dict = dict(row._mapping)
            # Convert datetime and parse JSON
            for key, value in result_dict.items():
                if isinstance(value, datetime):
                    result_dict[key] = value.isoformat()
            
            for col in ['dimension_scores', 'ai_feedback', 'ai_recommendations', 'result_data']:
                if result_dict.get(col) and isinstance(result_dict[col], str):
                    try:
                        result_dict[col] = json.loads(result_dict[col])
                    except:
                        pass
            
            result_list.append(result_dict)
        
        return result_list
    
    def get_completed_jobs(self) -> List[Dict[str, Any]]:
        """완료된 작업 목록 조회"""
        jobs = self.db.execute(
            text("SELECT * FROM jobs WHERE status = 'completed' ORDER BY updated_at DESC")
        ).fetchall()
        
        job_list = []
        for job in jobs:
            job_dict = dict(job._mapping)
            
            # Calculate average score
            avg_result = self.db.execute(
                text("SELECT AVG(overall_score) as avg_score FROM analysis_results_v2 WHERE job_id = :job_id"),
                {"job_id": job_dict.get("id")}
            ).fetchone()
            
            job_dict["average_score"] = round(avg_result["avg_score"], 1) if avg_result and avg_result["avg_score"] else 0
            
            # Convert datetime
            for key, value in job_dict.items():
                if isinstance(value, datetime):
                    job_dict[key] = value.isoformat()
            
            job_list.append(job_dict)
        
        return job_list