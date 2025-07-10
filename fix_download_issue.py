# AIRISS 다운로드 문제 해결 스크립트
# 임시 파일 저장 기능 추가

import os
import shutil
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_download_directory():
    """다운로드용 임시 디렉토리 생성"""
    download_dir = os.path.join(os.getcwd(), "downloads")
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print(f"✅ 다운로드 디렉토리 생성: {download_dir}")
    
    return download_dir

def cleanup_old_files(download_dir, hours=24):
    """오래된 임시 파일 정리"""
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for filename in os.listdir(download_dir):
            file_path = os.path.join(download_dir, filename)
            
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_time < cutoff_time:
                    os.remove(file_path)
                    print(f"🗑️ 오래된 파일 삭제: {filename}")
    
    except Exception as e:
        print(f"⚠️ 파일 정리 중 오류: {e}")

def add_file_download_to_analysis():
    """analysis.py에 파일 저장 기능 추가"""
    
    additional_code = '''
# 🔥 추가: 실제 파일 저장 기능
import os
import tempfile
from pathlib import Path

# 다운로드 디렉토리 설정
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@router.get("/download-file/{job_id}/{format}")
async def download_file_saved(job_id: str, format: str = "excel"):
    """분석 결과를 실제 파일로 저장 후 다운로드"""
    try:
        logger.info(f"📥 파일 저장 다운로드 요청: {job_id} - 형식: {format}")
        
        db_service = get_db_service()
        await db_service.init_database()
        
        # 작업 및 결과 조회
        job_data = await db_service.get_analysis_job(job_id)
        if not job_data:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
        
        results = await db_service.get_analysis_results(job_id)
        if not results:
            raise HTTPException(status_code=404, detail="분석 결과가 없습니다")
        
        # DataFrame 생성
        result_list = [result.get("result_data", {}) for result in results]
        df = pd.DataFrame(result_list)
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"AIRISS_result_{job_id[:8]}_{timestamp}"
        
        # 파일 저장
        if format.lower() == "csv":
            file_path = os.path.join(DOWNLOAD_DIR, f"{filename}.csv")
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            media_type = "text/csv"
            
        elif format.lower() == "json":
            file_path = os.path.join(DOWNLOAD_DIR, f"{filename}.json")
            df.to_json(file_path, orient='records', force_ascii=False, indent=2)
            media_type = "application/json"
            
        else:  # Excel
            file_path = os.path.join(DOWNLOAD_DIR, f"{filename}.xlsx")
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='분석결과', index=False)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        # 파일 존재 확인
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="파일 생성에 실패했습니다")
        
        logger.info(f"✅ 파일 저장 완료: {file_path}")
        
        # 파일 응답
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=os.path.basename(file_path)
        )
        
    except Exception as e:
        logger.error(f"❌ 파일 저장 다운로드 오류: {e}")
        raise HTTPException(status_code=500, detail=f"다운로드 실패: {str(e)}")

@router.get("/download-url/{job_id}")
async def get_download_url(job_id: str):
    """다운로드 URL 제공"""
    try:
        # 파일이 존재하는지 확인
        files = []
        for ext in ['xlsx', 'csv', 'json']:
            pattern = f"AIRISS_result_{job_id[:8]}_*{ext}"
            matching_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(f"AIRISS_result_{job_id[:8]}") and f.endswith(ext)]
            if matching_files:
                files.extend(matching_files)
        
        if not files:
            return {"message": "생성된 파일이 없습니다. 먼저 다운로드를 요청하세요."}
        
        # 가장 최근 파일들의 URL 반환
        base_url = "http://localhost:8002"  # 실제 서버 URL로 변경 필요
        urls = {}
        
        for file in files:
            if file.endswith('.xlsx'):
                urls['excel'] = f"{base_url}/static/downloads/{file}"
            elif file.endswith('.csv'):
                urls['csv'] = f"{base_url}/static/downloads/{file}"
            elif file.endswith('.json'):
                urls['json'] = f"{base_url}/static/downloads/{file}"
        
        return {
            "job_id": job_id,
            "download_urls": urls,
            "files_created": files
        }
        
    except Exception as e:
        logger.error(f"❌ 다운로드 URL 생성 오류: {e}")
        return {"error": str(e)}
'''
    
    print("📝 analysis.py에 추가할 코드가 준비되었습니다.")
    print("다음 단계:")
    print("1. analysis.py 파일 백업")
    print("2. 위 코드를 analysis.py 마지막에 추가")
    print("3. static/downloads 디렉토리를 웹에서 접근 가능하도록 설정")
    
    return additional_code

if __name__ == "__main__":
    print("🔧 AIRISS 다운로드 문제 해결 시작")
    
    # 1. 다운로드 디렉토리 생성
    download_dir = create_download_directory()