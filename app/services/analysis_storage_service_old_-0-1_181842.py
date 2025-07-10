# app/services/analysis_storage_service.py
# 분석 결과 영구 저장 및 조회 서비스 - Python 3.13 호환 버전

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# 🔥 Python 3.13 호환성: 조건부 SQLAlchemy import
try:
    from sqlalchemy.orm import Session
    from sqlalchemy import desc, func, and_
    from app.db.database import SessionLocal
    from app.models.analysis_result import AnalysisResultModel, AnalysisJobModel, AnalysisStatsModel
    SQLALCHEMY_AVAILABLE = True
    logger.info("✅ SQLAlchemy 모듈 로드 성공")
except Exception as e:
    SQLALCHEMY_AVAILABLE = False
    logger.warning(f"⚠️ SQLAlchemy 로드 실패 (Python 3.13 호환성): {e}")
    
    # 더미 클래스들 정의
    class SessionLocal:
        pass
    
    class AnalysisResultModel:
        pass
    
    class AnalysisJobModel:
        pass
    
    class AnalysisStatsModel:
        pass

class AnalysisStorageService:
    """분석 결과 영구 저장 및 조회 서비스 - Python 3.13 호환"""
    
    def __init__(self):
        self.sqlalchemy_available = SQLALCHEMY_AVAILABLE
        self.db = None
        
        if self.sqlalchemy_available:
            try:
                self.db = SessionLocal()
                logger.info("✅ SQLite 데이터베이스 연결 성공")
            except Exception as e:
                logger.error(f"❌ 데이터베이스 연결 실패: {e}")
                self.sqlalchemy_available = False
                self.db = None
        
        if not self.sqlalchemy_available:
            logger.info("📝 SQLAlchemy 비활성화 - 메모리 기반 저장소 사용")
            self.memory_storage = {
                "analysis_results": [],
                "analysis_jobs": [],
                "analysis_stats": []
            }
    
    def __del__(self):
        if hasattr(self, 'db') and self.db:
            try:
                self.db.close()
            except:
                pass
    
    def save_analysis_result(self, analysis_data: Dict[str, Any]) -> str:
        """
        분석 결과 저장
        
        Args:
            analysis_data: 분석 결과 데이터
            
        Returns:
            저장된 분석 결과의 ID
        """
        if not self.sqlalchemy_available:
            return self._save_to_memory(analysis_data)
        
        try:
            # 기존 결과 확인 (중복 방지)
            existing = self.db.query(AnalysisResultModel).filter(
                and_(
                    AnalysisResultModel.uid == analysis_data.get('uid'),
                    AnalysisResultModel.file_id == analysis_data.get('file_id')
                )
            ).first()
            
            if existing:
                # 기존 결과 업데이트
                for key, value in analysis_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                self.db.commit()
                logger.info(f"분석 결과 업데이트: {existing.analysis_id}")
                return existing.analysis_id
            else:
                # 새 결과 저장
                new_result = AnalysisResultModel(**analysis_data)
                self.db.add(new_result)
                self.db.commit()
                self.db.refresh(new_result)
                logger.info(f"분석 결과 저장: {new_result.analysis_id}")
                return new_result.analysis_id
                
        except Exception as e:
            logger.error(f"분석 결과 저장 실패: {e}")
            if self.db:
                self.db.rollback()
            # 폴백: 메모리 저장
            return self._save_to_memory(analysis_data)
    
    def _save_to_memory(self, analysis_data: Dict[str, Any]) -> str:
        """메모리 기반 저장 (SQLAlchemy 대체)"""
        analysis_id = analysis_data.get('analysis_id', f"mem_{len(self.memory_storage['analysis_results'])}")
        
        # 기존 결과 확인
        existing_index = None
        for i, result in enumerate(self.memory_storage['analysis_results']):
            if (result.get('uid') == analysis_data.get('uid') and 
                result.get('file_id') == analysis_data.get('file_id')):
                existing_index = i
                break
        
        analysis_data['created_at'] = datetime.now().isoformat()
        analysis_data['analysis_id'] = analysis_id
        
        if existing_index is not None:
            self.memory_storage['analysis_results'][existing_index] = analysis_data
            logger.info(f"메모리 분석 결과 업데이트: {analysis_id}")
        else:
            self.memory_storage['analysis_results'].append(analysis_data)
            logger.info(f"메모리 분석 결과 저장: {analysis_id}")
        
        return analysis_id
    
    def get_analysis_results(self, 
                           file_id: Optional[str] = None,
                           uid: Optional[str] = None,
                           limit: int = 100,
                           offset: int = 0) -> List[Dict[str, Any]]:
        """
        분석 결과 조회
        """
        if not self.sqlalchemy_available:
            return self._get_from_memory(file_id, uid, limit, offset)
        
        try:
            query = self.db.query(AnalysisResultModel)
            
            if file_id:
                query = query.filter(AnalysisResultModel.file_id == file_id)
            
            if uid:
                query = query.filter(AnalysisResultModel.uid == uid)
            
            results = query.order_by(desc(AnalysisResultModel.created_at))\
                          .limit(limit)\
                          .offset(offset)\
                          .all()
            
            return [self._model_to_dict(result) for result in results]
            
        except Exception as e:
            logger.error(f"분석 결과 조회 실패: {e}")
            # 폴백: 메모리에서 조회
            return self._get_from_memory(file_id, uid, limit, offset)
    
    def _get_from_memory(self, file_id=None, uid=None, limit=100, offset=0):
        """메모리에서 분석 결과 조회"""
        results = self.memory_storage['analysis_results']
        
        # 필터링
        if file_id:
            results = [r for r in results if r.get('file_id') == file_id]
        if uid:
            results = [r for r in results if r.get('uid') == uid]
        
        # 정렬 (최신순)
        results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # 페이징
        return results[offset:offset + limit]
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """특정 분석 결과 조회"""
        if not self.sqlalchemy_available:
            for result in self.memory_storage['analysis_results']:
                if result.get('analysis_id') == analysis_id:
                    return result
            return None
        
        try:
            result = self.db.query(AnalysisResultModel)\
                          .filter(AnalysisResultModel.analysis_id == analysis_id)\
                          .first()
            
            if result:
                return self._model_to_dict(result)
            return None
            
        except Exception as e:
            logger.error(f"분석 결과 조회 실패 (ID: {analysis_id}): {e}")
            # 폴백: 메모리에서 조회
            for result in self.memory_storage['analysis_results']:
                if result.get('analysis_id') == analysis_id:
                    return result
            return None
    
    def save_analysis_job(self, job_data: Dict[str, Any]) -> str:
        """분석 작업 정보 저장"""
        if not self.sqlalchemy_available:
            job_id = job_data.get('job_id', f"job_{len(self.memory_storage['analysis_jobs'])}")
            job_data['job_id'] = job_id
            job_data['created_at'] = datetime.now().isoformat()
            
            # 기존 작업 확인
            existing_index = None
            for i, job in enumerate(self.memory_storage['analysis_jobs']):
                if job.get('job_id') == job_id:
                    existing_index = i
                    break
            
            if existing_index is not None:
                self.memory_storage['analysis_jobs'][existing_index] = job_data
            else:
                self.memory_storage['analysis_jobs'].append(job_data)
            
            logger.info(f"메모리 작업 저장: {job_id}")
            return job_id
        
        try:
            # 기존 작업 확인
            existing = self.db.query(AnalysisJobModel)\
                             .filter(AnalysisJobModel.job_id == job_data.get('job_id'))\
                             .first()
            
            if existing:
                # 기존 작업 업데이트
                for key, value in job_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                self.db.commit()
                return existing.job_id
            else:
                # 새 작업 저장
                new_job = AnalysisJobModel(**job_data)
                self.db.add(new_job)
                self.db.commit()
                self.db.refresh(new_job)
                return new_job.job_id
                
        except Exception as e:
            logger.error(f"분석 작업 저장 실패: {e}")
            if self.db:
                self.db.rollback()
            # 폴백: 메모리 저장
            job_id = job_data.get('job_id', f"job_{len(self.memory_storage['analysis_jobs'])}")
            job_data['job_id'] = job_id
            job_data['created_at'] = datetime.now().isoformat()
            self.memory_storage['analysis_jobs'].append(job_data)
            return job_id
    
    def get_analysis_jobs(self, 
                         status: Optional[str] = None,
                         limit: int = 50) -> List[Dict[str, Any]]:
        """분석 작업 목록 조회"""
        if not self.sqlalchemy_available:
            jobs = self.memory_storage['analysis_jobs']
            if status:
                jobs = [j for j in jobs if j.get('status') == status]
            return sorted(jobs, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
        
        try:
            query = self.db.query(AnalysisJobModel)
            
            if status:
                query = query.filter(AnalysisJobModel.status == status)
            
            jobs = query.order_by(desc(AnalysisJobModel.started_at))\
                       .limit(limit)\
                       .all()
            
            return [self._model_to_dict(job) for job in jobs]
            
        except Exception as e:
            logger.error(f"분석 작업 조회 실패: {e}")
            # 폴백: 메모리에서 조회
            jobs = self.memory_storage['analysis_jobs']
            if status:
                jobs = [j for j in jobs if j.get('status') == status]
            return sorted(jobs, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
    
    def get_analysis_statistics(self, 
                              days: int = 30) -> Dict[str, Any]:
        """분석 통계 조회"""
        if not self.sqlalchemy_available:
            # 메모리 기반 통계
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            results = self.memory_storage['analysis_results']
            recent_results = []
            total_score = 0
            
            for result in results:
                created_str = result.get('created_at', '')
                if created_str:
                    try:
                        created_date = datetime.fromisoformat(created_str.replace('Z', '+00:00')).date()
                        if start_date <= created_date <= end_date:
                            recent_results.append(result)
                            score = result.get('hybrid_score', 0)
                            if isinstance(score, (int, float)):
                                total_score += score
                    except:
                        continue
            
            return {
                "period": f"{start_date} ~ {end_date}",
                "total_analyses": len(recent_results),
                "average_score": round(total_score / len(recent_results), 2) if recent_results else 0,
                "grade_distribution": {},
                "daily_counts": [],
                "storage_mode": "memory"
            }
        
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # 기본 통계
            total_analyses = self.db.query(AnalysisResultModel)\
                                  .filter(AnalysisResultModel.created_at >= start_date)\
                                  .count()
            
            avg_score = self.db.query(func.avg(AnalysisResultModel.hybrid_score))\
                             .filter(AnalysisResultModel.created_at >= start_date)\
                             .scalar() or 0
            
            # 등급별 분포
            grade_distribution = self.db.query(
                AnalysisResultModel.ok_grade,
                func.count(AnalysisResultModel.ok_grade)
            ).filter(
                AnalysisResultModel.created_at >= start_date
            ).group_by(AnalysisResultModel.ok_grade).all()
            
            # 일별 분석 수
            daily_counts = self.db.query(
                func.date(AnalysisResultModel.created_at).label('date'),
                func.count(AnalysisResultModel.id).label('count')
            ).filter(
                AnalysisResultModel.created_at >= start_date
            ).group_by(
                func.date(AnalysisResultModel.created_at)
            ).all()
            
            return {
                "period": f"{start_date} ~ {end_date}",
                "total_analyses": total_analyses,
                "average_score": round(avg_score, 2),
                "grade_distribution": {grade: count for grade, count in grade_distribution},
                "daily_counts": [
                    {"date": str(date), "count": count} 
                    for date, count in daily_counts
                ],
                "storage_mode": "sqlalchemy"
            }
            
        except Exception as e:
            logger.error(f"분석 통계 조회 실패: {e}")
            return {"error": str(e), "storage_mode": "error"}
    
    def search_analysis_results(self, 
                              search_term: str,
                              search_type: str = "opinion",
                              limit: int = 50) -> List[Dict[str, Any]]:
        """분석 결과 검색"""
        if not self.sqlalchemy_available:
            # 메모리 기반 검색
            results = []
            for result in self.memory_storage['analysis_results']:
                if search_type == "opinion":
                    if search_term in result.get('opinion', ''):
                        results.append(result)
                elif search_type == "uid":
                    if search_term in result.get('uid', ''):
                        results.append(result)
                elif search_type == "filename":
                    if search_term in result.get('filename', ''):
                        results.append(result)
                
                if len(results) >= limit:
                    break
            
            return results
        
        try:
            query = self.db.query(AnalysisResultModel)
            
            if search_type == "opinion":
                query = query.filter(AnalysisResultModel.opinion.contains(search_term))
            elif search_type == "uid":
                query = query.filter(AnalysisResultModel.uid.contains(search_term))
            elif search_type == "filename":
                query = query.filter(AnalysisResultModel.filename.contains(search_term))
            
            results = query.order_by(desc(AnalysisResultModel.created_at))\
                          .limit(limit)\
                          .all()
            
            return [self._model_to_dict(result) for result in results]
            
        except Exception as e:
            logger.error(f"분석 결과 검색 실패: {e}")
            return []
    
    def get_score_distribution(self, 
                             score_type: str = "hybrid_score") -> Dict[str, Any]:
        """점수 분포 조회"""
        if not self.sqlalchemy_available:
            return {
                "score_type": score_type,
                "distribution": {},
                "statistics": {
                    "min": 0,
                    "max": 100,
                    "average": 0,
                    "total_count": len(self.memory_storage['analysis_results'])
                },
                "storage_mode": "memory"
            }
        
        try:
            score_column = getattr(AnalysisResultModel, score_type)
            
            # 점수 구간별 분포
            distribution = self.db.query(
                func.floor(score_column / 10) * 10,
                func.count(AnalysisResultModel.id)
            ).group_by(
                func.floor(score_column / 10)
            ).all()
            
            # 통계 정보
            stats = self.db.query(
                func.min(score_column),
                func.max(score_column),
                func.avg(score_column),
                func.count(AnalysisResultModel.id)
            ).first()
            
            return {
                "score_type": score_type,
                "distribution": {
                    f"{int(score_range)}-{int(score_range)+9}": count 
                    for score_range, count in distribution
                },
                "statistics": {
                    "min": stats[0],
                    "max": stats[1],
                    "average": round(stats[2], 2) if stats[2] else 0,
                    "total_count": stats[3]
                },
                "storage_mode": "sqlalchemy"
            }
            
        except Exception as e:
            logger.error(f"점수 분포 조회 실패: {e}")
            return {"error": str(e)}
    
    def _model_to_dict(self, model) -> Dict[str, Any]:
        """SQLAlchemy 모델을 딕셔너리로 변환"""
        if not model:
            return {}
        
        result = {}
        try:
            for column in model.__table__.columns:
                value = getattr(model, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
        except Exception as e:
            logger.error(f"모델 변환 오류: {e}")
            # 폴백: 기본 속성들만 추출
            for attr in ['id', 'analysis_id', 'uid', 'file_id', 'created_at', 'status']:
                if hasattr(model, attr):
                    result[attr] = getattr(model, attr)
        
        return result
    
    def cleanup_old_results(self, retention_days: int = 365):
        """오래된 분석 결과 정리"""
        if not self.sqlalchemy_available:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            original_count = len(self.memory_storage['analysis_results'])
            
            self.memory_storage['analysis_results'] = [
                result for result in self.memory_storage['analysis_results']
                if datetime.fromisoformat(result.get('created_at', datetime.now().isoformat())) > cutoff_date
            ]
            
            deleted_count = original_count - len(self.memory_storage['analysis_results'])
            logger.info(f"메모리에서 오래된 분석 결과 {deleted_count}개 삭제")
            return
        
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            deleted_count = self.db.query(AnalysisResultModel)\
                                 .filter(AnalysisResultModel.created_at < cutoff_date)\
                                 .delete()
            
            self.db.commit()
            logger.info(f"오래된 분석 결과 {deleted_count}개 삭제")
            
        except Exception as e:
            logger.error(f"분석 결과 정리 실패: {e}")
            if self.db:
                self.db.rollback()
    
    def is_available(self) -> bool:
        """저장소 서비스 사용 가능 여부"""
        return self.sqlalchemy_available or hasattr(self, 'memory_storage')
    
    def get_storage_info(self) -> Dict[str, Any]:
        """저장소 정보 조회"""
        return {
            "sqlalchemy_available": self.sqlalchemy_available,
            "storage_mode": "sqlalchemy" if self.sqlalchemy_available else "memory",
            "memory_results": len(self.memory_storage.get('analysis_results', [])) if not self.sqlalchemy_available else 0,
            "memory_jobs": len(self.memory_storage.get('analysis_jobs', [])) if not self.sqlalchemy_available else 0
        }

# 🔥 조건부 글로벌 서비스 인스턴스
try:
    storage_service = AnalysisStorageService()
    logger.info("✅ 분석 저장소 서비스 초기화 완료")
except Exception as e:
    logger.error(f"❌ 분석 저장소 서비스 초기화 실패: {e}")
    
    # 더미 서비스 제공
    class DummyStorageService:
        def __init__(self):
            self.sqlalchemy_available = False
            self.memory_storage = {"analysis_results": [], "analysis_jobs": []}
        
        def save_analysis_result(self, data):
            return f"dummy_{len(self.memory_storage['analysis_results'])}"
        
        def get_analysis_results(self, **kwargs):
            return []
        
        def is_available(self):
            return False
    
    storage_service = DummyStorageService()
    logger.info("⚠️ 더미 저장소 서비스 사용")
