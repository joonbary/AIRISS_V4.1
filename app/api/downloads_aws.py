# app/api/downloads_aws.py
# AIRISS v4.0 AWS S3 다운로드 API - Railway 메모리 문제 해결

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse, FileResponse
import pandas as pd
import logging
from datetime import datetime
import os
import asyncio

# AWS S3 다운로드 매니저 import
from aws_s3_download_fix import s3_manager, create_s3_download, get_s3_download_status

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/downloads", tags=["downloads"])

@router.post("/create/{job_id}")
async def create_download_link(
    job_id: str,
    format: str = "excel",  # excel, csv, json
    background_tasks: BackgroundTasks = None
):
    """
    🚀 AWS S3 다운로드 링크 생성 API
    Railway 메모리 제한 문제 해결 + 대용량 파일 지원
    """
    try:
        logger.info(f"🔗 다운로드 링크 생성 요청: {job_id} - {format}")
        
        # 1. DB에서 분석 결과 조회
        from app.db.sqlite_service import SQLiteService
        db_service = SQLiteService()
        await db_service.init_database()
        
        # 작업 존재 확인
        job_data = await db_service.get_analysis_job(job_id)
        if not job_data:
            raise HTTPException(status_code=404, detail="분석 작업을 찾을 수 없습니다")
        
        if job_data["status"] != "completed":
            raise HTTPException(status_code=400, detail="분석이 완료되지 않았습니다")
        
        # 결과 데이터 조회
        results = await db_service.get_analysis_results(job_id)
        if not results:
            raise HTTPException(status_code=404, detail="분석 결과가 없습니다")
        
        # 2. DataFrame 생성
        result_list = []
        for result in results:
            try:
                result_data = result.get("result_data", {})
                if result_data:
                    result_list.append(result_data)
            except Exception as e:
                logger.warning(f"⚠️ 결과 데이터 파싱 오류: {e}")
                continue
        
        if not result_list:
            raise HTTPException(status_code=500, detail="유효한 분석 결과가 없습니다")
        
        df = pd.DataFrame(result_list)
        logger.info(f"📊 DataFrame 생성: {df.shape}")
        
        # 3. S3 업로드 및 다운로드 링크 생성
        upload_result = await create_s3_download(job_id, df, format)
        
        if not upload_result["success"]:
            raise HTTPException(status_code=500, detail=f"파일 생성 실패: {upload_result.get('error', 'Unknown error')}")
        
        # 4. 응답 생성
        response = {
            "job_id": job_id,
            "download_ready": True,
            "download_method": upload_result["download_method"],
            "download_url": upload_result["download_url"],
            "filename": upload_result["filename"],
            "file_size_mb": upload_result["file_size_mb"],
            "format": format,
            "expires_at": upload_result["expires_at"],
            "record_count": len(result_list),
            "message": "다운로드 준비가 완료되었습니다"
        }
        
        # S3 업로드인 경우 추가 정보
        if upload_result["download_method"] == "s3":
            response["s3_key"] = upload_result.get("s3_key")
            response["note"] = "AWS S3에 안전하게 저장되어 대용량 파일도 빠르게 다운로드 가능합니다"
        else:
            response["note"] = "로컬 파일로 저장되었습니다"
        
        logger.info(f"✅ 다운로드 링크 생성 완료: {upload_result['download_method']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 다운로드 링크 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"다운로드 링크 생성 실패: {str(e)}")

@router.get("/status/{job_id}")
async def get_download_status(job_id: str):
    """다운로드 상태 확인"""
    try:
        status = await get_s3_download_status(job_id)
        return status
    except Exception as e:
        logger.error(f"❌ 다운로드 상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{job_id}/{format}")
async def download_file_direct(job_id: str, format: str):
    """
    로컬 파일 직접 다운로드 (S3 폴백용)
    """
    try:
        logger.info(f"📥 직접 다운로드 요청: {job_id} - {format}")
        
        # 로컬 파일 경로 확인
        local_dir = "uploads/downloads"
        files = []
        
        if os.path.exists(local_dir):
            for filename in os.listdir(local_dir):
                if job_id[:8] in filename and filename.endswith(f".{format}"):
                    files.append(filename)
        
        if not files:
            raise HTTPException(status_code=404, detail="다운로드 파일을 찾을 수 없습니다")
        
        # 가장 최근 파일 선택
        files.sort(reverse=True)
        filepath = os.path.join(local_dir, files[0])
        
        # 파일 존재 확인
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다")
        
        # MIME 타입 설정
        if format.lower() == "csv":
            media_type = "text/csv"
        elif format.lower() == "json":
            media_type = "application/json"
        else:  # excel
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        logger.info(f"✅ 직접 다운로드 제공: {filepath}")
        
        return FileResponse(
            path=filepath,
            media_type=media_type,
            filename=files[0],
            headers={"Content-Disposition": f"attachment; filename={files[0]}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 직접 다운로드 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup/{job_id}")
async def cleanup_download_files(job_id: str):
    """다운로드 파일 수동 정리"""
    try:
        # S3 파일 삭제
        if s3_manager.s3_client:
            prefix = f"downloads/{job_id}/"
            response = s3_manager.s3_client.list_objects_v2(
                Bucket=s3_manager.bucket_name,
                Prefix=prefix
            )
            
            deleted_count = 0
            if 'Contents' in response:
                for obj in response['Contents']:
                    s3_manager.s3_client.delete_object(
                        Bucket=s3_manager.bucket_name,
                        Key=obj['Key']
                    )
                    deleted_count += 1
            
            logger.info(f"🗑️ S3 파일 정리 완료: {deleted_count}개")
        
        # 로컬 파일 삭제
        local_dir = "uploads/downloads"
        local_deleted = 0
        
        if os.path.exists(local_dir):
            for filename in os.listdir(local_dir):
                if job_id[:8] in filename:
                    filepath = os.path.join(local_dir, filename)
                    os.remove(filepath)
                    local_deleted += 1
        
        logger.info(f"🗑️ 로컬 파일 정리 완료: {local_deleted}개")
        
        return {
            "job_id": job_id,
            "cleaned_up": True,
            "s3_files_deleted": deleted_count if s3_manager.s3_client else 0,
            "local_files_deleted": local_deleted,
            "message": "다운로드 파일이 정리되었습니다"
        }
        
    except Exception as e:
        logger.error(f"❌ 파일 정리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def downloads_health_check():
    """다운로드 시스템 헬스체크"""
    try:
        # S3 연결 확인
        s3_status = "connected" if s3_manager.s3_client else "not_configured"
        
        # 로컬 디렉토리 확인
        local_dir = "uploads/downloads"
        local_status = "available" if os.path.exists(local_dir) else "not_found"
        
        return {
            "status": "healthy",
            "s3_connection": s3_status,
            "local_storage": local_status,
            "aws_region": s3_manager.aws_region,
            "bucket_name": s3_manager.bucket_name,
            "max_file_size_mb": s3_manager.max_file_size_mb,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# 백그라운드 정리 작업
async def background_cleanup():
    """백그라운드에서 만료된 파일 정리"""
    try:
        await s3_manager.cleanup_expired_files()
        logger.info("🧹 백그라운드 파일 정리 완료")
    except Exception as e:
        logger.error(f"❌ 백그라운드 정리 실패: {e}")

# 정기적 정리 작업 스케줄링 (FastAPI lifespan에서 호출)
async def schedule_cleanup():
    """정기적 정리 작업 스케줄링"""
    while True:
        await asyncio.sleep(3600)  # 1시간마다
        await background_cleanup()
