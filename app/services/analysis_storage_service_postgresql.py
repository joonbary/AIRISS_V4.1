# PostgreSQL Analysis Storage Service
# Complete Neon DB Integration - No SQLite Dependencies

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from app.db.database import SessionLocal, get_database_info, DATABASE_CONNECTION_TYPE
from app.models.analysis_result import AnalysisResultModel, AnalysisJobModel, AnalysisStatsModel

logger = logging.getLogger(__name__)

class PostgreSQLAnalysisStorageService:
    """PostgreSQL-only Analysis Storage Service - Complete Neon DB Integration"""
    
    def __init__(self):
        self.db_session_factory = SessionLocal
        self.connection_type = DATABASE_CONNECTION_TYPE
        
        # Verify PostgreSQL connection
        if self.connection_type != "postgresql":
            logger.warning(f"Expected PostgreSQL but got: {self.connection_type}")
            
        logger.info(f"PostgreSQL Analysis Storage Service initialized: {self.connection_type}")
    
    def _get_db_session(self) -> Session:
        """Get database session"""
        return self.db_session_factory()
    
    def save_analysis_result(self, analysis_data: Dict[str, Any]) -> str:
        """Save analysis result to PostgreSQL"""
        db = self._get_db_session()
        
        try:
            # Check for existing result (prevent duplicates)
            existing = db.query(AnalysisResultModel).filter(
                and_(
                    AnalysisResultModel.uid == analysis_data.get('uid'),
                    AnalysisResultModel.file_id == analysis_data.get('file_id')
                )
            ).first()
            
            if existing:
                # Update existing result
                for key, value in analysis_data.items():
                    if hasattr(existing, key) and key not in ['id', 'analysis_id', 'created_at']:
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                db.commit()
                
                logger.info(f"Analysis result updated: {existing.analysis_id}")
                return existing.analysis_id
            else:
                # Create new result
                # Ensure analysis_id exists
                if 'analysis_id' not in analysis_data:
                    import uuid
                    analysis_data['analysis_id'] = str(uuid.uuid4())
                
                new_result = AnalysisResultModel(**analysis_data)
                db.add(new_result)
                db.commit()
                db.refresh(new_result)
                
                logger.info(f"Analysis result saved to PostgreSQL: {new_result.analysis_id}")
                return new_result.analysis_id
                
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def get_analysis_results(self, 
                           file_id: Optional[str] = None,
                           uid: Optional[str] = None,
                           limit: int = 100,
                           offset: int = 0) -> List[Dict[str, Any]]:
        """Get analysis results from PostgreSQL"""
        db = self._get_db_session()
        
        try:
            query = db.query(AnalysisResultModel)
            
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
            logger.error(f"Failed to get analysis results: {e}")
            return []
        finally:
            db.close()
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get specific analysis result by ID"""
        db = self._get_db_session()
        
        try:
            result = db.query(AnalysisResultModel)\
                      .filter(AnalysisResultModel.analysis_id == analysis_id)\
                      .first()
            
            if result:
                return self._model_to_dict(result)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get analysis by ID {analysis_id}: {e}")
            return None
        finally:
            db.close()
    
    def save_analysis_job(self, job_data: Dict[str, Any]) -> str:
        """Save analysis job information"""
        db = self._get_db_session()
        
        try:
            # Check for existing job
            existing = db.query(AnalysisJobModel)\
                        .filter(AnalysisJobModel.job_id == job_data.get('job_id'))\
                        .first()
            
            if existing:
                # Update existing job
                for key, value in job_data.items():
                    if hasattr(existing, key) and key not in ['id', 'started_at']:
                        setattr(existing, key, value)
                db.commit()
                return existing.job_id
            else:
                # Create new job
                if 'job_id' not in job_data:
                    import uuid
                    job_data['job_id'] = str(uuid.uuid4())
                
                new_job = AnalysisJobModel(**job_data)
                db.add(new_job)
                db.commit()
                db.refresh(new_job)
                return new_job.job_id
                
        except Exception as e:
            logger.error(f"Failed to save analysis job: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def get_analysis_jobs(self, 
                         status: Optional[str] = None,
                         limit: int = 50) -> List[Dict[str, Any]]:
        """Get analysis job list"""
        db = self._get_db_session()
        
        try:
            query = db.query(AnalysisJobModel)
            
            if status:
                query = query.filter(AnalysisJobModel.status == status)
            
            jobs = query.order_by(desc(AnalysisJobModel.started_at))\
                       .limit(limit)\
                       .all()
            
            return [self._model_to_dict(job) for job in jobs]
            
        except Exception as e:
            logger.error(f"Failed to get analysis jobs: {e}")
            return []
        finally:
            db.close()
    
    def get_analysis_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get analysis statistics for specified period"""
        db = self._get_db_session()
        
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Basic statistics
            total_analyses = db.query(AnalysisResultModel)\
                              .filter(func.date(AnalysisResultModel.created_at) >= start_date)\
                              .count()
            
            avg_score = db.query(func.avg(AnalysisResultModel.hybrid_score))\
                         .filter(func.date(AnalysisResultModel.created_at) >= start_date)\
                         .scalar() or 0
            
            # Grade distribution
            grade_distribution = db.query(
                AnalysisResultModel.ok_grade,
                func.count(AnalysisResultModel.ok_grade)
            ).filter(
                func.date(AnalysisResultModel.created_at) >= start_date
            ).group_by(AnalysisResultModel.ok_grade).all()
            
            # Daily counts
            daily_counts = db.query(
                func.date(AnalysisResultModel.created_at).label('date'),
                func.count(AnalysisResultModel.id).label('count')
            ).filter(
                func.date(AnalysisResultModel.created_at) >= start_date
            ).group_by(
                func.date(AnalysisResultModel.created_at)
            ).order_by('date').all()
            
            return {
                "period": f"{start_date} to {end_date}",
                "total_analyses": total_analyses,
                "average_score": round(avg_score, 2),
                "grade_distribution": {grade: count for grade, count in grade_distribution if grade},
                "daily_counts": [
                    {"date": str(date), "count": count} 
                    for date, count in daily_counts
                ],
                "storage_mode": "postgresql",
                "database_type": self.connection_type
            }
            
        except Exception as e:
            logger.error(f"Failed to get analysis statistics: {e}")
            return {
                "error": str(e), 
                "storage_mode": "postgresql",
                "database_type": self.connection_type
            }
        finally:
            db.close()
    
    def search_analysis_results(self, 
                              search_term: str,
                              search_type: str = "opinion",
                              limit: int = 50) -> List[Dict[str, Any]]:
        """Search analysis results"""
        db = self._get_db_session()
        
        try:
            query = db.query(AnalysisResultModel)
            
            if search_type == "opinion":
                query = query.filter(AnalysisResultModel.opinion.contains(search_term))
            elif search_type == "uid":
                query = query.filter(AnalysisResultModel.uid.contains(search_term))
            elif search_type == "filename":
                query = query.filter(AnalysisResultModel.filename.contains(search_term))
            elif search_type == "all":
                query = query.filter(
                    or_(
                        AnalysisResultModel.opinion.contains(search_term),
                        AnalysisResultModel.uid.contains(search_term),
                        AnalysisResultModel.filename.contains(search_term)
                    )
                )
            
            results = query.order_by(desc(AnalysisResultModel.created_at))\
                          .limit(limit)\
                          .all()
            
            return [self._model_to_dict(result) for result in results]
            
        except Exception as e:
            logger.error(f"Failed to search analysis results: {e}")
            return []
        finally:
            db.close()
    
    def get_score_distribution(self, 
                             score_type: str = "hybrid_score") -> Dict[str, Any]:
        """Get score distribution analysis"""
        db = self._get_db_session()
        
        try:
            score_column = getattr(AnalysisResultModel, score_type, None)
            if not score_column:
                return {"error": f"Invalid score type: {score_type}"}
            
            # Score range distribution (10-point intervals)
            distribution = db.query(
                (func.floor(score_column / 10) * 10).label('score_range'),
                func.count(AnalysisResultModel.id).label('count')
            ).group_by(
                func.floor(score_column / 10)
            ).order_by('score_range').all()
            
            # Statistics
            stats = db.query(
                func.min(score_column).label('min_score'),
                func.max(score_column).label('max_score'),
                func.avg(score_column).label('avg_score'),
                func.count(AnalysisResultModel.id).label('total_count')
            ).first()
            
            return {
                "score_type": score_type,
                "distribution": {
                    f"{int(score_range)}-{int(score_range)+9}": count 
                    for score_range, count in distribution
                },
                "statistics": {
                    "min": float(stats.min_score) if stats.min_score else 0,
                    "max": float(stats.max_score) if stats.max_score else 0,
                    "average": round(float(stats.avg_score), 2) if stats.avg_score else 0,
                    "total_count": stats.total_count
                },
                "storage_mode": "postgresql",
                "database_type": self.connection_type
            }
            
        except Exception as e:
            logger.error(f"Failed to get score distribution: {e}")
            return {"error": str(e)}
        finally:
            db.close()
    
    def cleanup_old_results(self, retention_days: int = 365):
        """Clean up old analysis results"""
        db = self._get_db_session()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            deleted_count = db.query(AnalysisResultModel)\
                             .filter(AnalysisResultModel.created_at < cutoff_date)\
                             .delete()
            
            db.commit()
            logger.info(f"Cleaned up {deleted_count} old analysis results")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old results: {e}")
            db.rollback()
            return 0
        finally:
            db.close()
    
    def get_recent_high_scores(self, 
                             min_score: float = 90.0,
                             days: int = 7,
                             limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent high-scoring analysis results"""
        db = self._get_db_session()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            results = db.query(AnalysisResultModel)\
                       .filter(
                           and_(
                               AnalysisResultModel.hybrid_score >= min_score,
                               AnalysisResultModel.created_at >= cutoff_date
                           )
                       )\
                       .order_by(desc(AnalysisResultModel.hybrid_score))\
                       .limit(limit)\
                       .all()
            
            return [self._model_to_dict(result) for result in results]
            
        except Exception as e:
            logger.error(f"Failed to get recent high scores: {e}")
            return []
        finally:
            db.close()
    
    def get_storage_health(self) -> Dict[str, Any]:
        """Get storage service health information"""
        db_info = get_database_info()
        
        try:
            db = self._get_db_session()
            
            # Count total records
            total_results = db.query(AnalysisResultModel).count()
            total_jobs = db.query(AnalysisJobModel).count()
            
            # Recent activity
            recent_count = db.query(AnalysisResultModel)\
                            .filter(AnalysisResultModel.created_at >= datetime.now() - timedelta(days=1))\
                            .count()
            
            db.close()
            
            return {
                "status": "healthy",
                "database_info": db_info,
                "storage_type": "postgresql_only",
                "total_analysis_results": total_results,
                "total_analysis_jobs": total_jobs,
                "recent_activity_24h": recent_count,
                "sqlite_dependencies": False,
                "unified_storage": True
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "database_info": db_info
            }
    
    def _model_to_dict(self, model) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary"""
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
            logger.error(f"Model conversion error: {e}")
            
        return result
    
    def is_available(self) -> bool:
        """Check if storage service is available"""
        return self.connection_type == "postgresql"
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get comprehensive storage information"""
        return {
            "service_type": "PostgreSQLAnalysisStorageService",
            "connection_type": self.connection_type,
            "postgresql_only": True,
            "sqlite_removed": True,
            "unified_database": True,
            "neon_db_integrated": True
        }

# Global service instance
try:
    postgresql_storage_service = PostgreSQLAnalysisStorageService()
    logger.info("PostgreSQL Analysis Storage Service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PostgreSQL Analysis Storage Service: {e}")
    postgresql_storage_service = None