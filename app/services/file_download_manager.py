"""
파일 다운로드 관리자 - 다운로드 링크 생성 문제 해결
"""
import os
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple
import hashlib
import json

logger = logging.getLogger(__name__)

class FileDownloadManager:
    """파일 다운로드 생성 및 관리"""
    
    def __init__(self, base_path: str = "downloads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # 다운로드 메타데이터 저장
        self.metadata_file = self.base_path / "download_metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """메타데이터 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
        return {}
        
    def _save_metadata(self):
        """메타데이터 저장"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            
    def prepare_download_file(self, job_id: str, source_file: str, 
                             expiry_hours: int = 24) -> Tuple[bool, str, Optional[str]]:
        """
        다운로드 파일 준비
        
        Returns:
            (success, download_path_or_error, download_token)
        """
        try:
            # 소스 파일 확인
            if not os.path.exists(source_file):
                error_msg = f"Source file not found: {source_file}"
                logger.error(error_msg)
                return False, error_msg, None
                
            # 다운로드 토큰 생성
            download_token = self._generate_download_token(job_id)
            
            # 다운로드 디렉토리 생성
            job_download_dir = self.base_path / job_id
            job_download_dir.mkdir(exist_ok=True)
            
            # 파일 복사
            source_path = Path(source_file)
            dest_filename = f"{download_token}_{source_path.name}"
            dest_path = job_download_dir / dest_filename
            
            try:
                shutil.copy2(source_file, dest_path)
                logger.info(f"Copied file to download area: {dest_path}")
            except Exception as e:
                error_msg = f"Failed to copy file: {e}"
                logger.error(error_msg)
                return False, error_msg, None
                
            # 메타데이터 저장
            self.metadata[download_token] = {
                'job_id': job_id,
                'original_file': source_path.name,
                'download_path': str(dest_path),
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat(),
                'download_count': 0,
                'file_size': os.path.getsize(dest_path)
            }
            self._save_metadata()
            
            # 다운로드 URL 생성
            download_url = f"/api/v1/download/{download_token}"
            
            logger.info(f"Download file prepared: {download_token} -> {dest_path}")
            
            return True, download_url, download_token
            
        except Exception as e:
            error_msg = f"Unexpected error preparing download: {e}"
            logger.error(error_msg)
            return False, error_msg, None
            
    def _generate_download_token(self, job_id: str) -> str:
        """다운로드 토큰 생성"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{job_id}_{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
        
    def get_download_file(self, download_token: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        다운로드 파일 조회
        
        Returns:
            (success, file_path_or_error, metadata)
        """
        try:
            # 메타데이터 확인
            if download_token not in self.metadata:
                return False, "Invalid download token", None
                
            metadata = self.metadata[download_token]
            
            # 만료 확인
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if datetime.utcnow() > expires_at:
                return False, "Download link has expired", None
                
            # 파일 존재 확인
            file_path = metadata['download_path']
            if not os.path.exists(file_path):
                return False, "Download file not found", None
                
            # 다운로드 횟수 증가
            metadata['download_count'] += 1
            metadata['last_downloaded'] = datetime.utcnow().isoformat()
            self._save_metadata()
            
            return True, file_path, metadata
            
        except Exception as e:
            error_msg = f"Error retrieving download file: {e}"
            logger.error(error_msg)
            return False, error_msg, None
            
    def cleanup_expired_files(self) -> int:
        """만료된 다운로드 파일 정리"""
        cleaned_count = 0
        current_time = datetime.utcnow()
        
        tokens_to_remove = []
        
        for token, metadata in self.metadata.items():
            try:
                expires_at = datetime.fromisoformat(metadata['expires_at'])
                
                if current_time > expires_at:
                    # 파일 삭제
                    file_path = metadata['download_path']
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Removed expired file: {file_path}")
                        
                    # 빈 디렉토리 삭제
                    job_dir = Path(file_path).parent
                    if job_dir.exists() and not any(job_dir.iterdir()):
                        job_dir.rmdir()
                        
                    tokens_to_remove.append(token)
                    cleaned_count += 1
                    
            except Exception as e:
                logger.error(f"Error cleaning up token {token}: {e}")
                
        # 메타데이터에서 제거
        for token in tokens_to_remove:
            del self.metadata[token]
            
        if cleaned_count > 0:
            self._save_metadata()
            logger.info(f"Cleaned up {cleaned_count} expired downloads")
            
        return cleaned_count
        
    def get_download_stats(self) -> Dict:
        """다운로드 통계 조회"""
        total_files = len(self.metadata)
        total_size = sum(m.get('file_size', 0) for m in self.metadata.values())
        total_downloads = sum(m.get('download_count', 0) for m in self.metadata.values())
        
        active_files = 0
        expired_files = 0
        current_time = datetime.utcnow()
        
        for metadata in self.metadata.values():
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if current_time <= expires_at:
                active_files += 1
            else:
                expired_files += 1
                
        return {
            'total_files': total_files,
            'active_files': active_files,
            'expired_files': expired_files,
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'total_downloads': total_downloads
        }
        
    def verify_download_chain(self, job_id: str) -> Dict:
        """다운로드 체인 검증 - 문제 진단용"""
        verification = {
            'job_id': job_id,
            'checks': {},
            'issues': []
        }
        
        # 1. 결과 파일 존재 확인
        results_path = Path("results")
        job_files = list(results_path.glob(f"*{job_id}*"))
        
        verification['checks']['result_files_exist'] = len(job_files) > 0
        if not job_files:
            verification['issues'].append("No result files found for job")
        else:
            verification['result_files'] = [str(f) for f in job_files]
            
        # 2. 다운로드 준비 확인
        downloads_path = self.base_path / job_id
        verification['checks']['download_dir_exists'] = downloads_path.exists()
        
        if downloads_path.exists():
            download_files = list(downloads_path.glob("*"))
            verification['checks']['download_files_exist'] = len(download_files) > 0
            verification['download_files'] = [str(f) for f in download_files]
        else:
            verification['issues'].append("Download directory not created")
            
        # 3. 메타데이터 확인
        job_tokens = [token for token, meta in self.metadata.items() 
                      if meta.get('job_id') == job_id]
                      
        verification['checks']['metadata_exists'] = len(job_tokens) > 0
        if not job_tokens:
            verification['issues'].append("No download metadata found")
        else:
            verification['download_tokens'] = job_tokens
            
        # 4. 전체 상태 판단
        all_checks_passed = all(verification['checks'].values())
        verification['status'] = 'ready' if all_checks_passed else 'incomplete'
        
        return verification