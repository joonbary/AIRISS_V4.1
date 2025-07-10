# AIRISS v4.0 AWS S3 다운로드 시스템 구축
# Railway 메모리 제한 문제 해결 + 확장성 확보

import boto3
import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import asyncio
from botocore.exceptions import ClientError
import tempfile

logger = logging.getLogger(__name__)

class AIRISS_S3_DownloadManager:
    """AIRISS AWS S3 다운로드 관리자"""
    
    def __init__(self):
        # AWS 설정
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2')
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'airiss-downloads')
        
        # S3 클라이언트 초기화
        self.s3_client = None
        self._init_s3_client()
        
        # 설정값
        self.download_expiry_hours = int(os.getenv('S3_DOWNLOAD_EXPIRY_HOURS', '24'))
        self.max_file_size_mb = int(os.getenv('S3_MAX_FILE_SIZE_MB', '50'))
        self.url_expiry_minutes = int(os.getenv('S3_URL_EXPIRY_MINUTES', '60'))
        
        logger.info("✅ AIRISS S3 다운로드 매니저 초기화 완료")
    
    def _init_s3_client(self):
        """S3 클라이언트 초기화"""
        try:
            if self.aws_access_key and self.aws_secret_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.aws_region
                )
                
                # 버킷 존재 확인
                self._ensure_bucket_exists()
                
                logger.info(f"✅ S3 클라이언트 초기화 성공: {self.bucket_name}")
            else:
                logger.warning("⚠️ AWS 자격증명이 없습니다 - 로컬 파일 시스템 사용")
                self.s3_client = None
        except Exception as e:
            logger.error(f"❌ S3 클라이언트 초기화 실패: {e}")
            self.s3_client = None
    
    def _ensure_bucket_exists(self):
        """S3 버킷 존재 확인 및 생성"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"✅ S3 버킷 확인됨: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # 버킷이 없으면 생성
                try:
                    if self.aws_region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.aws_region}
                        )
                    
                    # 퍼블릭 액세스 차단 설정
                    self.s3_client.put_public_access_block(
                        Bucket=self.bucket_name,
                        PublicAccessBlockConfiguration={
                            'BlockPublicAcls': True,
                            'IgnorePublicAcls': True,
                            'BlockPublicPolicy': True,
                            'RestrictPublicBuckets': True
                        }
                    )
                    
                    # 수명주기 정책 설정 (24시간 후 자동 삭제)
                    self.s3_client.put_bucket_lifecycle_configuration(
                        Bucket=self.bucket_name,
                        LifecycleConfiguration={
                            'Rules': [
                                {
                                    'ID': 'AIRISS-AutoDelete',
                                    'Status': 'Enabled',
                                    'Expiration': {'Days': 1},
                                    'Filter': {'Prefix': 'downloads/'}
                                }
                            ]
                        }
                    )
                    
                    logger.info(f"✅ S3 버킷 생성됨: {self.bucket_name}")
                except Exception as create_error:
                    logger.error(f"❌ S3 버킷 생성 실패: {create_error}")
                    raise
            else:
                logger.error(f"❌ S3 버킷 접근 오류: {e}")
                raise
    
    async def upload_file_to_s3(self, job_id: str, df: pd.DataFrame, 
                               format: str = "excel") -> Dict[str, Any]:
        """DataFrame을 S3에 업로드하고 다운로드 정보 반환"""
        try:
            if not self.s3_client:
                return await self._fallback_local_file(job_id, df, format)
            
            # 임시 파일 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"AIRISS_result_{job_id[:8]}_{timestamp}"
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                if format.lower() == "csv":
                    filename += ".csv"
                    df.to_csv(temp_file.name, index=False, encoding='utf-8-sig')
                    content_type = "text/csv"
                elif format.lower() == "json":
                    filename += ".json"
                    json_data = df.to_json(orient='records', force_ascii=False, indent=2)
                    with open(temp_file.name, 'w', encoding='utf-8') as f:
                        f.write(json_data)
                    content_type = "application/json"
                else:  # Excel
                    filename += ".xlsx"
                    df.to_excel(temp_file.name, index=False, engine='openpyxl')
                    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                
                # 파일 크기 확인
                file_size_mb = os.path.getsize(temp_file.name) / (1024 * 1024)
                if file_size_mb > self.max_file_size_mb:
                    logger.warning(f"⚠️ 파일 크기 초과: {file_size_mb:.1f}MB > {self.max_file_size_mb}MB")
                
                # S3 업로드
                s3_key = f"downloads/{job_id}/{filename}"
                
                extra_args = {
                    'ContentType': content_type,
                    'ContentDisposition': f'attachment; filename="{filename}"',
                    'Metadata': {
                        'job-id': job_id,
                        'created-at': datetime.now().isoformat(),
                        'expires-at': (datetime.now() + timedelta(hours=self.download_expiry_hours)).isoformat(),
                        'file-format': format,
                        'record-count': str(len(df))
                    }
                }
                
                self.s3_client.upload_file(
                    temp_file.name,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs=extra_args
                )
                
                # 임시 파일 삭제
                os.unlink(temp_file.name)
                
                # 사전 서명된 URL 생성
                presigned_url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': s3_key},
                    ExpiresIn=self.url_expiry_minutes * 60
                )
                
                logger.info(f"✅ S3 업로드 완료: {s3_key} ({file_size_mb:.1f}MB)")
                
                return {
                    "success": True,
                    "download_method": "s3",
                    "download_url": presigned_url,
                    "filename": filename,
                    "file_size_mb": round(file_size_mb, 2),
                    "expires_at": (datetime.now() + timedelta(minutes=self.url_expiry_minutes)).isoformat(),
                    "s3_key": s3_key
                }
                
        except Exception as e:
            logger.error(f"❌ S3 업로드 실패: {e}")
            # S3 실패 시 로컬 파일로 폴백
            return await self._fallback_local_file(job_id, df, format)
    
    async def _fallback_local_file(self, job_id: str, df: pd.DataFrame, 
                                  format: str) -> Dict[str, Any]:
        """S3 실패 시 로컬 파일 저장 폴백"""
        try:
            # uploads 디렉토리 생성
            local_dir = "uploads/downloads"
            os.makedirs(local_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"AIRISS_result_{job_id[:8]}_{timestamp}"
            
            if format.lower() == "csv":
                filename += ".csv"
                filepath = os.path.join(local_dir, filename)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            elif format.lower() == "json":
                filename += ".json"
                filepath = os.path.join(local_dir, filename)
                json_data = df.to_json(orient='records', force_ascii=False, indent=2)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json_data)
            else:  # Excel
                filename += ".xlsx"
                filepath = os.path.join(local_dir, filename)
                df.to_excel(filepath, index=False, engine='openpyxl')
            
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            
            # 로컬 파일 정보 저장 (24시간 후 자동 삭제 스케줄링)
            self._schedule_file_cleanup(filepath)
            
            logger.info(f"✅ 로컬 파일 저장 완료: {filepath} ({file_size_mb:.1f}MB)")
            
            return {
                "success": True,
                "download_method": "local",
                "download_url": f"/download-file/{job_id}/{format}",
                "filename": filename,
                "file_size_mb": round(file_size_mb, 2),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
                "filepath": filepath
            }
            
        except Exception as e:
            logger.error(f"❌ 로컬 파일 저장 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "download_method": "failed"
            }
    
    def _schedule_file_cleanup(self, filepath: str):
        """24시간 후 파일 자동 삭제 스케줄링"""
        # 실제로는 백그라운드 스케줄러나 cron job으로 구현
        # 여기서는 메타데이터만 기록
        cleanup_info = {
            "filepath": filepath,
            "created_at": datetime.now().isoformat(),
            "cleanup_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        # cleanup.json 파일에 기록
        cleanup_file = "uploads/cleanup.json"
        try:
            if os.path.exists(cleanup_file):
                with open(cleanup_file, 'r') as f:
                    cleanup_list = json.load(f)
            else:
                cleanup_list = []
            
            cleanup_list.append(cleanup_info)
            
            with open(cleanup_file, 'w') as f:
                json.dump(cleanup_list, f, indent=2)
                
        except Exception as e:
            logger.warning(f"⚠️ 정리 스케줄 기록 실패: {e}")
    
    async def get_download_status(self, job_id: str) -> Dict[str, Any]:
        """다운로드 상태 확인"""
        try:
            if self.s3_client:
                # S3에서 파일 목록 확인
                prefix = f"downloads/{job_id}/"
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )
                
                files = []
                if 'Contents' in response:
                    for obj in response['Contents']:
                        # 메타데이터 가져오기
                        metadata_response = self.s3_client.head_object(
                            Bucket=self.bucket_name,
                            Key=obj['Key']
                        )
                        
                        files.append({
                            "filename": os.path.basename(obj['Key']),
                            "size_mb": round(obj['Size'] / (1024 * 1024), 2),
                            "created_at": metadata_response.get('Metadata', {}).get('created-at', ''),
                            "expires_at": metadata_response.get('Metadata', {}).get('expires-at', ''),
                            "format": metadata_response.get('Metadata', {}).get('file-format', 'unknown')
                        })
                
                return {
                    "job_id": job_id,
                    "storage_type": "s3",
                    "files": files,
                    "total_files": len(files)
                }
            else:
                # 로컬 파일 확인
                local_dir = f"uploads/downloads"
                files = []
                
                if os.path.exists(local_dir):
                    for filename in os.listdir(local_dir):
                        if job_id[:8] in filename:
                            filepath = os.path.join(local_dir, filename)
                            stat = os.stat(filepath)
                            files.append({
                                "filename": filename,
                                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                                "format": filename.split('.')[-1]
                            })
                
                return {
                    "job_id": job_id,
                    "storage_type": "local",
                    "files": files,
                    "total_files": len(files)
                }
                
        except Exception as e:
            logger.error(f"❌ 다운로드 상태 확인 실패: {e}")
            return {
                "job_id": job_id,
                "error": str(e),
                "storage_type": "unknown"
            }
    
    async def cleanup_expired_files(self):
        """만료된 파일 정리"""
        try:
            if self.s3_client:
                # S3는 lifecycle policy로 자동 정리됨
                logger.info("S3 파일은 lifecycle policy로 자동 정리됩니다")
            else:
                # 로컬 파일 정리
                cleanup_file = "uploads/cleanup.json"
                if os.path.exists(cleanup_file):
                    with open(cleanup_file, 'r') as f:
                        cleanup_list = json.load(f)
                    
                    now = datetime.now()
                    remaining_files = []
                    
                    for item in cleanup_list:
                        cleanup_time = datetime.fromisoformat(item['cleanup_at'])
                        if now >= cleanup_time:
                            # 파일 삭제
                            try:
                                if os.path.exists(item['filepath']):
                                    os.remove(item['filepath'])
                                    logger.info(f"🗑️ 만료 파일 삭제: {item['filepath']}")
                            except Exception as e:
                                logger.warning(f"⚠️ 파일 삭제 실패: {e}")
                        else:
                            remaining_files.append(item)
                    
                    # 정리 목록 업데이트
                    with open(cleanup_file, 'w') as f:
                        json.dump(remaining_files, f, indent=2)
                        
        except Exception as e:
            logger.error(f"❌ 파일 정리 실패: {e}")

# 전역 인스턴스
s3_manager = AIRISS_S3_DownloadManager()

# FastAPI 라우터에 추가할 엔드포인트들
async def create_s3_download(job_id: str, df: pd.DataFrame, format: str = "excel"):
    """S3 다운로드 링크 생성"""
    return await s3_manager.upload_file_to_s3(job_id, df, format)

async def get_s3_download_status(job_id: str):
    """S3 다운로드 상태 조회"""
    return await s3_manager.get_download_status(job_id)

if __name__ == "__main__":
    # 테스트 코드
    import asyncio
    
    async def test_s3_manager():
        # 테스트 데이터프레임
        test_df = pd.DataFrame({
            'UID': ['TEST001', 'TEST002'],
            'Score': [85.5, 92.3],
            'Grade': ['OK A', 'OK★★']
        })
        
        # S3 업로드 테스트
        result = await s3_manager.upload_file_to_s3("test-job-123", test_df, "excel")
        print("✅ 테스트 결과:", result)
        
        # 상태 확인 테스트
        status = await s3_manager.get_download_status("test-job-123")
        print("📊 상태 확인:", status)
    
    asyncio.run(test_s3_manager())
