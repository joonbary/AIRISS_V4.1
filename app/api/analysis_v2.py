"""
AIRISS v4 분석 API v2
통합 스키마를 사용하는 새로운 API 엔드포인트
기존 API와의 호환성 유지
"""

from fastapi import APIRouter, HTTPException
from app.db.db_service_v2 import db_service_v2
import logging

logger = logging.getLogger(__name__)

# 새로운 라우터 (점진적 마이그레이션용)
router_v2 = APIRouter(prefix="/analysis/v2", tags=["analysis-v2"])


@router_v2.get("/results/{job_id}")
async def get_analysis_results_v2(job_id: str):
    """분석 결과 조회 - 통합 스키마 사용"""
    try:
        logger.info(f"📊 V2 결과 조회: {job_id}")
        
        # 통합 테이블에서 조회
        results = await db_service_v2.get_analysis_results(job_id=job_id)
        
        if not results:
            # 작업이 아직 진행 중인지 확인
            from app.db import db_service
            db = db_service.get_session()
            try:
                from sqlalchemy import text
                job_data = db.execute(
                    text("SELECT status FROM jobs WHERE id = :job_id"),
                    {'job_id': job_id}
                ).fetchone()
                
                if job_data and job_data.status == "processing":
                    return {
                        "results": [],
                        "total_count": 0,
                        "job_status": "processing",
                        "message": "분석이 진행 중입니다. 잠시 후 다시 시도해주세요."
                    }
            finally:
                db.close()
            
            raise HTTPException(status_code=404, detail="분석 결과가 없습니다")
        
        # 응답 구성
        response = {
            "results": results,
            "total_count": len(results),
            "job_status": "completed",
            "analysis_mode": results[0].get('analysis_mode', 'hybrid') if results else 'hybrid',
            "version": "4.0-v2",
            "schema_version": "unified"
        }
        
        logger.info(f"✅ V2 결과 조회 성공: {len(results)}개")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ V2 결과 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"결과 조회 실패: {str(e)}")


@router_v2.get("/download/{job_id}/{format}")
async def download_results_v2(job_id: str, format: str = "excel"):
    """분석 결과 다운로드 - 통합 스키마 사용"""
    try:
        logger.info(f"📥 V2 다운로드 요청: {job_id} - 형식: {format}")
        
        # 다운로드용 데이터 조회
        results = await db_service_v2.get_results_for_download(job_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="다운로드할 결과가 없습니다")
        
        # 데이터프레임 생성
        import pandas as pd
        df = pd.DataFrame(results)
        
        # 파일 생성
        import io
        from datetime import datetime
        from fastapi.responses import StreamingResponse
        
        if format.lower() == "excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # 요약 시트
                summary_data = {
                    '항목': ['분석일시', '총 분석건수', '평균 점수', 'AI 분석 포함'],
                    '값': [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        len(results),
                        round(df['AIRISS_v4_종합점수'].mean(), 1) if 'AIRISS_v4_종합점수' in df.columns else 'N/A',
                        '예' if any(df.get('AI_종합피드백', '').notna()) else '아니오'
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='요약', index=False)
                
                # 상세 결과
                df.to_excel(writer, sheet_name='상세결과', index=False)
                
                # 스타일 적용
                workbook = writer.book
                for sheet_name in workbook.sheetnames:
                    worksheet = workbook[sheet_name]
                    # 헤더 스타일
                    for cell in worksheet[1]:
                        cell.font = writer.book.create_font(bold=True)
            
            output.seek(0)
            
            return StreamingResponse(
                io.BytesIO(output.getvalue()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=AIRISS_v2_results_{job_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                }
            )
            
        elif format.lower() == "csv":
            output = io.StringIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=AIRISS_v2_results_{job_id[:8]}.csv"
                }
            )
            
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 형식: {format}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ V2 다운로드 오류: {e}")
        raise HTTPException(status_code=500, detail=f"다운로드 실패: {str(e)}")


# 기존 API 패치 함수 (점진적 마이그레이션)
def patch_existing_analysis_api():
    """기존 analysis.py의 함수들을 새 서비스로 교체"""
    try:
        import app.api.analysis as analysis_module
        
        # get_analysis_results 함수 교체
        async def patched_get_results(job_id: str):
            return await get_analysis_results_v2(job_id)
        
        # 패치 적용
        analysis_module.get_analysis_results = patched_get_results
        
        logger.info("✅ 기존 API 패치 완료 - 통합 스키마 사용")
        
    except Exception as e:
        logger.error(f"❌ API 패치 실패: {e}")


# 마이그레이션 상태 확인
@router_v2.get("/migration/status")
async def check_migration_status():
    """마이그레이션 상태 확인"""
    try:
        db = db_service_v2.get_session()
        from sqlalchemy import text
        
        # 테이블 존재 여부 확인
        tables = {}
        for table in ['results', 'analysis_results', 'analysis_results_v2']:
            try:
                count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                tables[table] = {"exists": True, "count": count}
            except:
                tables[table] = {"exists": False, "count": 0}
        
        # 뷰 존재 여부 확인
        views = {}
        for view in ['results_view', 'analysis_results_view']:
            try:
                count = db.execute(text(f"SELECT COUNT(*) FROM {view}")).scalar()
                views[view] = {"exists": True, "count": count}
            except:
                views[view] = {"exists": False, "count": 0}
        
        db.close()
        
        return {
            "migration_ready": tables.get('analysis_results_v2', {}).get('exists', False),
            "tables": tables,
            "views": views,
            "recommendation": "마이그레이션 준비 완료" if tables.get('analysis_results_v2', {}).get('exists', False) else "마이그레이션 필요"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "migration_ready": False
        }