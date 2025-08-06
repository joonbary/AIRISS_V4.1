# app/api/analysis_storage.py
# 분석 결과 저장 및 조회 API 엔드포인트 - Excel 내보내기 완전 개선

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import pandas as pd
from io import BytesIO
import json

from app.services.analysis_storage_service import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/analysis-storage",
    tags=["analysis-storage"]
)

def create_excel_file(results: List[Dict[str, Any]], filename: str = "AIRISS_Report") -> BytesIO:
    """
    분석 결과를 실제 Excel 파일로 생성
    
    Args:
        results: 분석 결과 리스트
        filename: 파일명
        
    Returns:
        BytesIO: Excel 파일 바이너리 스트림
    """
    try:
        # BytesIO 스트림 생성
        excel_buffer = BytesIO()
        
        # Excel Writer 생성 (openpyxl 엔진 사용)
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            
            # 1. 메인 분석 결과 시트
            if results:
                # 분석 결과를 DataFrame으로 변환
                df_main = pd.DataFrame(results)
                
                # 필요한 컬럼만 선택 및 정리
                display_columns = []
                if 'created_at' in df_main.columns:
                    display_columns.append('created_at')
                if 'file_name' in df_main.columns:
                    display_columns.append('file_name')
                if 'uid' in df_main.columns:
                    display_columns.append('uid')
                if 'opinion' in df_main.columns:
                    display_columns.append('opinion')
                if 'hybrid_score' in df_main.columns:
                    display_columns.append('hybrid_score')
                if 'bias_score' in df_main.columns:
                    display_columns.append('bias_score')
                if 'creativity_score' in df_main.columns:
                    display_columns.append('creativity_score')
                if 'problem_solving_score' in df_main.columns:
                    display_columns.append('problem_solving_score')
                
                # 선택된 컬럼으로 DataFrame 생성
                if display_columns:
                    df_display = df_main[display_columns].copy()
                else:
                    df_display = df_main.copy()
                
                # 컬럼명 한글화
                column_mapping = {
                    'created_at': '분석 일시',
                    'file_name': '파일명',
                    'uid': '사용자 ID',
                    'opinion': '의견/피드백',
                    'hybrid_score': '종합 점수',
                    'bias_score': '편향 점수',
                    'creativity_score': '창의성 점수',
                    'problem_solving_score': '문제해결 점수'
                }
                
                df_display.rename(columns=column_mapping, inplace=True)
                
                # 메인 결과 시트에 저장
                df_display.to_excel(writer, sheet_name='분석 결과', index=False)
                
                # 워크시트 스타일링
                worksheet = writer.sheets['분석 결과']
                
                # 헤더 스타일링
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                    cell.fill = cell.fill.copy(fgColor="366092")
                
                # 컬럼 너비 자동 조정
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # 2. 통계 요약 시트
                summary_data = {
                    '항목': ['총 분석 건수', '평균 종합 점수', '최고 점수', '최저 점수', '분석 기간'],
                    '값': [
                        len(results),
                        round(df_main['hybrid_score'].mean() if 'hybrid_score' in df_main.columns else 0, 2),
                        round(df_main['hybrid_score'].max() if 'hybrid_score' in df_main.columns else 0, 2),
                        round(df_main['hybrid_score'].min() if 'hybrid_score' in df_main.columns else 0, 2),
                        f"{df_main['created_at'].min()} ~ {df_main['created_at'].max()}" if 'created_at' in df_main.columns else "N/A"
                    ]
                }
                
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='통계 요약', index=False)
                
                # 3. 점수 분포 시트 (있는 경우)
                if 'hybrid_score' in df_main.columns:
                    score_distribution = df_main['hybrid_score'].value_counts().sort_index()
                    df_scores = pd.DataFrame({
                        '점수': score_distribution.index,
                        '빈도': score_distribution.values
                    })
                    df_scores.to_excel(writer, sheet_name='점수 분포', index=False)
            
            else:
                # 결과가 없는 경우 빈 시트 생성
                empty_df = pd.DataFrame({'메시지': ['분석 결과가 없습니다.']})
                empty_df.to_excel(writer, sheet_name='분석 결과', index=False)
        
        # 버퍼 포인터를 시작으로 이동
        excel_buffer.seek(0)
        
        logger.info(f"✅ Excel 파일 생성 완료: {filename}.xlsx")
        return excel_buffer
        
    except Exception as e:
        logger.error(f"❌ Excel 파일 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Excel 파일 생성 실패: {str(e)}")

def create_csv_file(results: List[Dict[str, Any]]) -> str:
    """
    분석 결과를 BOM 포함 CSV로 생성 (Excel 한글 호환)
    
    Args:
        results: 분석 결과 리스트
        
    Returns:
        str: BOM 포함 CSV 문자열
    """
    try:
        if not results:
            return '\ufeff메시지\n분석 결과가 없습니다.\n'
        
        # DataFrame으로 변환
        df = pd.DataFrame(results)
        
        # 필요한 컬럼만 선택
        display_columns = []
        column_mapping = {
            'created_at': '분석 일시',
            'file_name': '파일명',
            'uid': '사용자 ID',
            'opinion': '의견/피드백',
            'hybrid_score': '종합 점수',
            'bias_score': '편향 점수',
            'creativity_score': '창의성 점수',
            'problem_solving_score': '문제해결 점수'
        }
        
        for col in ['created_at', 'file_name', 'uid', 'opinion', 'hybrid_score', 'bias_score', 'creativity_score', 'problem_solving_score']:
            if col in df.columns:
                display_columns.append(col)
        
        if display_columns:
            df_display = df[display_columns].copy()
            df_display.rename(columns=column_mapping, inplace=True)
        else:
            df_display = df.copy()
        
        # BOM 포함 CSV 생성 (Excel 한글 호환)
        csv_data = '\ufeff' + df_display.to_csv(index=False, encoding='utf-8')
        
        logger.info("✅ CSV 파일 생성 완료 (BOM 포함)")
        return csv_data
        
    except Exception as e:
        logger.error(f"❌ CSV 파일 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"CSV 파일 생성 실패: {str(e)}")

@router.post("/save")
async def save_analysis_result(analysis_data: Dict[str, Any]):
    """
    분석 결과 저장
    
    Args:
        analysis_data: 분석 결과 데이터
        
    Returns:
        저장된 분석 결과 ID
    """
    try:
        analysis_id = storage_service.save_analysis_result(analysis_data)
        return {
            "success": True,
            "analysis_id": analysis_id,
            "message": "분석 결과가 성공적으로 저장되었습니다."
        }
    except Exception as e:
        logger.error(f"분석 결과 저장 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results")
async def get_analysis_results(
    file_id: Optional[str] = Query(None, description="파일 ID로 필터링"),
    uid: Optional[str] = Query(None, description="사용자 ID로 필터링"),
    limit: int = Query(100, description="결과 수 제한"),
    offset: int = Query(0, description="페이지네이션 오프셋")
):
    """
    분석 결과 조회
    
    Args:
        file_id: 파일 ID 필터
        uid: 사용자 ID 필터
        limit: 결과 수 제한
        offset: 페이지네이션 오프셋
        
    Returns:
        분석 결과 리스트
    """
    try:
        results = storage_service.get_analysis_results(
            file_id=file_id,
            uid=uid,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        logger.error(f"분석 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{analysis_id}")
async def get_analysis_by_id(analysis_id: str):
    """특정 분석 결과 조회"""
    try:
        result = storage_service.get_analysis_by_id(analysis_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        return {
            "success": True,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"분석 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def get_analysis_jobs(
    status: Optional[str] = Query(None, description="작업 상태로 필터링"),
    limit: int = Query(50, description="결과 수 제한")
):
    """분석 작업 목록 조회"""
    try:
        jobs = storage_service.get_analysis_jobs(status=status, limit=limit)
        
        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs)
        }
    except Exception as e:
        logger.error(f"분석 작업 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_analysis_statistics(
    days: int = Query(30, description="통계 기간 (일)")
):
    """분석 통계 조회"""
    try:
        stats = storage_service.get_analysis_statistics(days=days)
        
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"분석 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_analysis_results(
    search_term: str = Query(..., description="검색어"),
    search_type: str = Query("opinion", description="검색 타입 (opinion, uid, filename)"),
    limit: int = Query(50, description="결과 수 제한")
):
    """분석 결과 검색"""
    try:
        results = storage_service.search_analysis_results(
            search_term=search_term,
            search_type=search_type,
            limit=limit
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "search_info": {
                "term": search_term,
                "type": search_type
            }
        }
    except Exception as e:
        logger.error(f"분석 결과 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score-distribution")
async def get_score_distribution(
    score_type: str = Query("hybrid_score", description="점수 타입")
):
    """점수 분포 조회"""
    try:
        distribution = storage_service.get_score_distribution(score_type=score_type)
        
        return {
            "success": True,
            "distribution": distribution
        }
    except Exception as e:
        logger.error(f"점수 분포 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_old_results(
    retention_days: int = Query(365, description="보관 기간 (일)")
):
    """오래된 분석 결과 정리"""
    try:
        storage_service.cleanup_old_results(retention_days=retention_days)
        
        return {
            "success": True,
            "message": f"{retention_days}일 이전 분석 결과를 정리했습니다."
        }
    except Exception as e:
        logger.error(f"분석 결과 정리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 🚨 새로운 Excel/CSV 내보내기 엔드포인트 ====================

@router.get("/export-excel")
async def export_analysis_results_excel(
    file_id: Optional[str] = Query(None, description="파일 ID로 필터링"),
    uid: Optional[str] = Query(None, description="사용자 ID로 필터링"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    filename: str = Query("AIRISS_Report", description="다운로드 파일명")
):
    """
    🆕 실제 Excel 파일 다운로드 (브라우저에서 즉시 다운로드)
    
    사용법: 브라우저에서 URL 직접 접속하면 Excel 파일 자동 다운로드
    예시: https://airiss.railway.app/api/analysis-storage/export-excel
    """
    try:
        logger.info("📊 Excel 파일 내보내기 요청 시작")
        
        # 분석 결과 조회
        results = storage_service.get_analysis_results(
            file_id=file_id,
            uid=uid,
            limit=10000  # 대량 내보내기
        )
        
        # 날짜 필터링 (필요한 경우)
        if start_date or end_date:
            # 날짜 필터링 로직 구현 (추후 확장 가능)
            pass
        
        # 실제 Excel 파일 생성
        excel_file = create_excel_file(results, filename)
        
        # 파일명 설정 (현재 날짜 포함)
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_filename = f"{filename}_{current_date}.xlsx"
        
        logger.info(f"✅ Excel 파일 생성 완료: {download_filename} ({len(results)}건)")
        
        # 실제 Excel 파일 다운로드 응답
        return StreamingResponse(
            io=excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={download_filename}"}
        )
        
    except Exception as e:
        logger.error(f"❌ Excel 파일 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Excel 파일 생성 실패: {str(e)}")

@router.get("/export-csv")
async def export_analysis_results_csv(
    file_id: Optional[str] = Query(None, description="파일 ID로 필터링"),
    uid: Optional[str] = Query(None, description="사용자 ID로 필터링"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    filename: str = Query("AIRISS_Report", description="다운로드 파일명")
):
    """
    🆕 Excel 호환 CSV 파일 다운로드 (BOM 포함, 한글 깨짐 방지)
    
    사용법: 브라우저에서 URL 직접 접속하면 CSV 파일 자동 다운로드
    예시: https://airiss.railway.app/api/analysis-storage/export-csv
    """
    try:
        logger.info("📊 CSV 파일 내보내기 요청 시작")
        
        # 분석 결과 조회
        results = storage_service.get_analysis_results(
            file_id=file_id,
            uid=uid,
            limit=10000  # 대량 내보내기
        )
        
        # 날짜 필터링 (필요한 경우)
        if start_date or end_date:
            # 날짜 필터링 로직 구현 (추후 확장 가능)
            pass
        
        # BOM 포함 CSV 생성
        csv_data = create_csv_file(results)
        
        # 파일명 설정 (현재 날짜 포함)
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_filename = f"{filename}_{current_date}.csv"
        
        logger.info(f"✅ CSV 파일 생성 완료: {download_filename} ({len(results)}건)")
        
        # CSV 파일 다운로드 응답
        return StreamingResponse(
            io=BytesIO(csv_data.encode('utf-8-sig')),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={download_filename}"}
        )
        
    except Exception as e:
        logger.error(f"❌ CSV 파일 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"CSV 파일 생성 실패: {str(e)}")

# ==================== 기존 엔드포인트 (호환성 유지) ====================

@router.get("/export")
async def export_analysis_results(
    file_id: Optional[str] = Query(None, description="파일 ID로 필터링"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    format: str = Query("json", description="내보내기 형식 (json, csv)")
):
    """
    ⚠️ 기존 내보내기 (호환성 유지용) - 텍스트 반환
    
    ✅ 새로운 기능:
    - /export-excel : 실제 Excel 파일 다운로드
    - /export-csv : Excel 호환 CSV 다운로드
    """
    try:
        # 기본 조회
        results = storage_service.get_analysis_results(
            file_id=file_id,
            limit=10000  # 대량 내보내기를 위해 높은 제한
        )
        
        # 날짜 필터링 (필요한 경우)
        if start_date or end_date:
            # 날짜 필터링 로직 구현
            pass
        
        if format == "csv":
            # CSV 형식으로 변환
            import pandas as pd
            df = pd.DataFrame(results)
            csv_data = df.to_csv(index=False)
            
            return {
                "success": True,
                "format": "csv",
                "data": csv_data,
                "count": len(results),
                "notice": "💡 실제 Excel 파일 다운로드는 /export-excel 엔드포인트를 사용하세요!"
            }
        else:
            # JSON 형식
            return {
                "success": True,
                "format": "json",
                "data": results,
                "count": len(results),
                "notice": "💡 실제 Excel 파일 다운로드는 /export-excel 엔드포인트를 사용하세요!"
            }
            
    except Exception as e:
        logger.error(f"분석 결과 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
