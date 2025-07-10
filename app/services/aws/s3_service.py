# app/services/aws/s3_service.py
"""
AIRISS v4.0 - AWS S3 다운로드 서비스
메모리 효율적인 대용량 파일 다운로드를 위한 S3 통합
"""

import boto3
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import pandas as pd
import io
from botocore.exceptions import NoCredentialsError, ClientError
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class S3DownloadService:
    """AWS S3를 활용한 안전하고 효율적인 다운로드 서비스"""
    
    def __init__(self):
        """S3 서비스 초기화"""
        self.enabled = os.getenv("S3_DOWNLOAD_ENABLED", "false").lower() == "true"
        
        if not self.enabled:
            logger.info("🔧 S3 다운로드 서비스 비활성화 상태")
            return
        
        # AWS 설정
        self.region = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
        self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME", "airiss-downloads")
        
        # 다운로드 설정
        self.expiry_hours = int(os.getenv("S3_DOWNLOAD_EXPIRY_HOURS", "24"))
        self.max_file_size_mb = int(os.getenv("S3_MAX_FILE_SIZE_MB", "50"))
        self.url_expiry_minutes = int(os.getenv("S3_URL_EXPIRY_MINUTES", "60"))
        
        # Thread pool for async operations
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
        
        try:
            # S3 클라이언트 초기화
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            
            # 버킷 존재 확인 (없으면 생성)
            self._ensure_bucket_exists()
            
            logger.info(f"✅ S3 다운로드 서비스 활성화 완료")
            logger.info(f"📦 버킷: {self.bucket_name}, 리전: {self.region}")
            logger.info(f"⏰ 파일 보관: {self.expiry_hours}시간, URL 유효: {self.url_expiry_minutes}분")
            
        except NoCredentialsError:
            logger.error("❌ AWS 자격 증명을 찾을 수 없습니다")
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ S3 서비스 초기화 실패: {e}")
            self.enabled = False
    
    def _ensure_bucket_exists(self):
        """S3 버킷 존재 확인 및 생성"""
        try:
            # 버킷 존재 확인
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"✅ S3 버킷 확인 완료: {self.bucket_name}")
            
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            
            if error_code == 404:
                # 버킷이 없으면 생성
                logger.info(f"📦 S3 버킷 생성 중: {self.bucket_name}")
                
                if self.region == 'us-east-1':
                    # us-east-1은 LocationConstraint 없이 생성
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                else:
                    # 다른 리전은 LocationConstraint 필요
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                
                # 수명 주기 정책 설정 (자동 정리)
                lifecycle_policy = {
                    'Rules': [
                        {
                            'ID': 'DeleteTempFiles',
                            'Status': 'Enabled',
                            'Filter': {'Prefix': 'airiss-temp/'},
                            'Expiration': {'Days': 1}  # 1일 후 자동 삭제
                        }
                    ]
                }
                
                self.s3_client.put_bucket_lifecycle_configuration(
                    Bucket=self.bucket_name,
                    LifecycleConfiguration=lifecycle_policy
                )
                
                logger.info(f"✅ S3 버킷 생성 및 정책 설정 완료: {self.bucket_name}")
                
            else:
                raise e
    
    async def upload_analysis_result_async(self, job_id: str, df: pd.DataFrame, format: str = "excel") -> Optional[Dict[str, Any]]:
        """비동기 분석 결과 업로드"""
        if not self.enabled:
            logger.warning("⚠️ S3 서비스가 비활성화되어 있습니다")
            return None
        
        try:
            # 비동기로 업로드 실행
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.thread_pool,
                self._upload_analysis_result_sync,
                job_id, df, format
            )
            return result
            
        except Exception as e:
            logger.error(f"❌ 비동기 업로드 실패: {e}")
            return None
    
    def _upload_analysis_result_sync(self, job_id: str, df: pd.DataFrame, format: str) -> Dict[str, Any]:
        """동기 방식 분석 결과 업로드"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # S3 키 생성
        s3_key = f"airiss-temp/{job_id}/{timestamp}_result.{format}"
        
        # 파일 데이터 준비
        file_data = self._prepare_file_data(df, format)
        if not file_data:
            raise Exception(f"지원하지 않는 형식: {format}")
        
        # 파일 크기 확인
        file_size_mb = len(file_data) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise Exception(f"파일 크기 초과: {file_size_mb:.1f}MB (최대: {self.max_file_size_mb}MB)")
        
        # S3 업로드
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=file_data,
            ContentType=self._get_content_type(format),
            Metadata={
                'job_id': job_id,
                'created_at': timestamp,
                'format': format,
                'records': str(len(df)),
                'file_size_mb': f"{file_size_mb:.2f}"
            }
        )
        
        logger.info(f"✅ S3 업로드 완료: {s3_key} ({file_size_mb:.1f}MB)")
        
        return {
            's3_key': s3_key,
            'file_size_mb': round(file_size_mb, 2),
            'records_count': len(df),
            'upload_time': timestamp,
            'bucket': self.bucket_name
        }
    
    def _prepare_file_data(self, df: pd.DataFrame, format: str) -> Optional[bytes]:
        """형식별 파일 데이터 준비"""
        try:
            if format.lower() == "csv":
                # CSV 형식
                output = io.StringIO()
                df.to_csv(output, index=False, encoding='utf-8')
                return output.getvalue().encode('utf-8-sig')
                
            elif format.lower() == "json":
                # JSON 형식
                json_data = df.to_json(orient='records', force_ascii=False, indent=2)
                return json_data.encode('utf-8')
                
            elif format.lower() in ["excel", "xlsx"]:
                # Excel 형식 (향상된 버전)
                output = io.BytesIO()
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # 요약 시트
                    summary_data = {
                        '항목': [
                            '분석일시', '총 분석건수', '평균 점수', '최고 점수', '최저 점수',
                            'S등급 수', 'A등급 수', 'B등급 수', 'C등급 수', 'D등급 수'
                        ]
                    }
                    
                    # 점수 컬럼 찾기
                    score_col = None
                    for col in ['AIRISS_v4_종합점수', '종합점수', 'overall_score']:
                        if col in df.columns:
                            score_col = col
                            break
                    
                    # 등급 분포 계산
                    grade_counts = {'OK★★★': 0, 'OK★★': 0, 'OK★': 0, 'OK A': 0, 'OK B+': 0, 'OK B': 0, 'OK C': 0, 'OK D': 0}
                    grade_col = None
                    for col in ['OK등급', '등급', 'grade']:
                        if col in df.columns:
                            grade_col = col
                            break
                    
                    if grade_col:
                        grade_counts = df[grade_col].value_counts().to_dict()
                    
                    summary_data['값'] = [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        len(df),
                        round(df[score_col].mean(), 1) if score_col else 'N/A',
                        df[score_col].max() if score_col else 'N/A',
                        df[score_col].min() if score_col else 'N/A',
                        grade_counts.get('OK★★★', 0),
                        grade_counts.get('OK★★', 0) + grade_counts.get('OK★', 0) + grade_counts.get('OK A', 0),
                        grade_counts.get('OK B+', 0) + grade_counts.get('OK B', 0),
                        grade_counts.get('OK C', 0),
                        grade_counts.get('OK D', 0)
                    ]
                    
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='📊 요약', index=False)
                    
                    # 상세 결과 시트
                    df.to_excel(writer, sheet_name='📋 상세결과', index=False)
                    
                    # 고득점자 시트 (90점 이상)
                    if score_col and score_col in df.columns:
                        high_performers = df[df[score_col] >= 90]
                        if not high_performers.empty:
                            high_performers.to_excel(writer, sheet_name='🌟 우수자', index=False)
                        
                        # 개선필요 시트 (60점 미만)
                        low_performers = df[df[score_col] < 60]
                        if not low_performers.empty:
                            low_performers.to_excel(writer, sheet_name='⚡ 개선필요', index=False)
                
                return output.getvalue()
            
            else:
                logger.error(f"❌ 지원하지 않는 형식: {format}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 파일 데이터 준비 실패: {e}")
            return None
    
    def _get_content_type(self, format: str) -> str:
        """형식별 Content-Type 반환"""
        content_types = {
            'csv': 'text/csv',
            'json': 'application/json',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        return content_types.get(format.lower(), 'application/octet-stream')
    
    def generate_download_url(self, s3_key: str, filename: str = None) -> Optional[str]:
        """안전한 임시 다운로드 URL 생성"""
        if not self.enabled:
            return None
        
        try:
            # 파일명 설정
            if not filename:
                filename = s3_key.split('/')[-1]
            
            # Presigned URL 생성
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key,
                    'ResponseContentDisposition': f'attachment; filename="{filename}"'
                },
                ExpiresIn=self.url_expiry_minutes * 60
            )
            
            logger.info(f"🔗 다운로드 URL 생성: {s3_key} (유효: {self.url_expiry_minutes}분)")
            return url
            
        except Exception as e:
            logger.error(f"❌ 다운로드 URL 생성 실패: {e}")
            return None
    
    def check_file_exists(self, s3_key: str) -> bool:
        """S3 파일 존재 확인"""
        if not self.enabled:
            return False
        
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False
    
    def get_file_info(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """S3 파일 정보 조회"""
        if not self.enabled:
            return None
        
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            
            return {
                'size_bytes': response['ContentLength'],
                'size_mb': round(response['ContentLength'] / (1024 * 1024), 2),
                'last_modified': response['LastModified'].isoformat(),
                'content_type': response.get('ContentType', 'unknown'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            logger.error(f"❌ 파일 정보 조회 실패: {e}")
            return None
    
    def cleanup_old_files(self, days_old: int = 1):
        """오래된 임시 파일 정리"""
        if not self.enabled:
            return
        
        try:
            # 버킷의 수명 주기 정책이 자동으로 처리하므로 별도 정리 불필요
            logger.info(f"📁 S3 수명 주기 정책으로 {days_old}일 후 자동 정리됩니다")
            
        except Exception as e:
            logger.error(f"❌ 파일 정리 실패: {e}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """S3 서비스 상태 조회"""
        return {
            'enabled': self.enabled,
            'bucket_name': self.bucket_name if self.enabled else None,
            'region': self.region if self.enabled else None,
            'max_file_size_mb': self.max_file_size_mb if self.enabled else None,
            'url_expiry_minutes': self.url_expiry_minutes if self.enabled else None,
            'auto_cleanup_hours': self.expiry_hours if self.enabled else None
        }

# 글로벌 인스턴스
s3_service = S3DownloadService()
