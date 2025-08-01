"""
멈춰있는 분석 작업 재설정
"""
import sys
sys.path.append('.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.analysis_result import AnalysisJobModel
from app.core.config import settings
from datetime import datetime, timedelta

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # 멈춰있는 작업 찾기 (10분 이상 업데이트 없음)
    stuck_jobs = db.query(AnalysisJobModel).filter(
        AnalysisJobModel.status.in_(['processing', 'pending'])
    ).all()
    
    print(f"멈춰있는 작업 수: {len(stuck_jobs)}")
    
    for job in stuck_jobs:
        print(f"\n작업 ID: {job.id}")
        print(f"상태: {job.status}")
        print(f"시작 시간: {job.created_at}")
        print(f"진행률: {job.progress}%")
        
        # 작업을 failed로 변경
        job.status = 'failed'
        job.error_message = "작업이 타임아웃되었습니다"
        
    db.commit()
    print(f"\n{len(stuck_jobs)}개의 작업을 failed로 변경했습니다.")
    
    # 현재 진행 중인 모든 작업 확인
    all_jobs = db.query(AnalysisJobModel).order_by(AnalysisJobModel.created_at.desc()).limit(5).all()
    print("\n최근 5개 작업:")
    for job in all_jobs:
        print(f"ID: {job.id[:8]}, 상태: {job.status}, 진행률: {job.progress}%, 생성: {job.created_at}")

finally:
    db.close()