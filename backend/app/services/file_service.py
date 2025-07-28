"""
File Service
파일 업로드 및 관리를 담당하는 서비스
"""

from typing import Dict, Any, List, Optional, BinaryIO
import pandas as pd
import os
import uuid
from datetime import datetime
import shutil

from .base import BaseService
from app.db.repositories import FileRepository
from app.core.config import settings


class FileService(BaseService):
    """파일 관리 서비스"""
    
    def __init__(self, db):
        super().__init__(db)
        self.file_repo = FileRepository(db)
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def upload_file(
        self,
        file_data: BinaryIO,
        filename: str,
        user_id: int,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """파일 업로드 처리"""
        try:
            # 파일 ID 생성
            file_id = str(uuid.uuid4())
            
            # 파일 저장 경로
            file_path = os.path.join(self.upload_dir, f"{file_id}_{filename}")
            
            # 파일 저장
            with open(file_path, "wb") as f:
                content = file_data.read()
                f.write(content)
            
            # 파일 크기
            file_size = len(content)
            
            # 파일 분석
            analysis_result = await self._analyze_file(file_path, filename)
            
            # DataFrame 저장 (빠른 로딩을 위해)
            if analysis_result.get('dataframe') is not None:
                pickle_path = file_path.replace('.xlsx', '.pkl').replace('.xls', '.pkl').replace('.csv', '.pkl')
                analysis_result['dataframe'].to_pickle(pickle_path)
                analysis_result['dataframe_path'] = pickle_path
            
            # 데이터베이스에 저장
            file_info = {
                'id': file_id,
                'filename': filename,
                'file_path': file_path,
                'user_id': str(user_id),
                'session_id': session_id,
                'size': file_size,
                **analysis_result
            }
            
            # DataFrame 제거 (DB 저장용)
            file_info.pop('dataframe', None)
            
            self.file_repo.save_file(file_info)
            
            return {
                'file_id': file_id,
                'filename': filename,
                'size': file_size,
                **analysis_result
            }
            
        except Exception as e:
            self.logger.error(f"File upload failed: {e}")
            # 실패시 파일 삭제
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            raise
    
    async def _analyze_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """파일 구조 분석"""
        try:
            # 파일 읽기
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # 컬럼 분석
            columns = list(df.columns)
            
            # UID 컬럼 찾기
            uid_columns = self._find_uid_columns(columns)
            
            # Opinion 컬럼 찾기
            opinion_columns = self._find_opinion_columns(columns, df)
            
            # Quantitative 컬럼 찾기
            quantitative_columns = self._find_quantitative_columns(df)
            
            # 분석 준비 상태 확인
            airiss_ready = len(uid_columns) > 0 and len(opinion_columns) > 0
            hybrid_ready = airiss_ready and len(quantitative_columns) > 0
            
            return {
                'columns': columns,
                'uid_columns': uid_columns,
                'opinion_columns': opinion_columns,
                'quantitative_columns': quantitative_columns,
                'total_records': len(df),
                'airiss_ready': airiss_ready,
                'hybrid_ready': hybrid_ready,
                'dataframe': df
            }
            
        except Exception as e:
            self.logger.error(f"File analysis failed: {e}")
            raise ValueError(f"Failed to analyze file: {str(e)}")
    
    def _find_uid_columns(self, columns: List[str]) -> List[str]:
        """UID 컬럼 찾기"""
        uid_keywords = ['uid', 'id', '사번', 'employee', 'emp_id', 'user_id', '직원']
        uid_columns = []
        
        for col in columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in uid_keywords):
                uid_columns.append(col)
        
        return uid_columns
    
    def _find_opinion_columns(self, columns: List[str], df: pd.DataFrame) -> List[str]:
        """Opinion 컬럼 찾기"""
        opinion_keywords = ['opinion', '의견', 'comment', 'feedback', 'text', '피드백', '평가']
        opinion_columns = []
        
        for col in columns:
            col_lower = col.lower()
            # 키워드 매칭
            if any(keyword in col_lower for keyword in opinion_keywords):
                opinion_columns.append(col)
            # 또는 텍스트 타입 컬럼 중 평균 길이가 긴 것
            elif df[col].dtype == 'object':
                avg_length = df[col].astype(str).str.len().mean()
                if avg_length > 50:  # 평균 50자 이상
                    opinion_columns.append(col)
        
        return opinion_columns
    
    def _find_quantitative_columns(self, df: pd.DataFrame) -> List[str]:
        """정량적 컬럼 찾기"""
        quantitative_columns = []
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                # 숫자 컬럼 중 ID가 아닌 것
                if not any(id_word in col.lower() for id_word in ['id', '번호', 'no']):
                    quantitative_columns.append(col)
        
        return quantitative_columns
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """파일 정보 조회"""
        file_info = self.file_repo.get_file(file_id)
        if file_info:
            # DataFrame은 제외
            file_info.pop('dataframe', None)
        return file_info
    
    def get_file_with_data(self, file_id: str) -> Dict[str, Any]:
        """파일 정보와 데이터 조회"""
        return self.file_repo.get_file(file_id)
    
    def list_user_files(self, user_id: int) -> List[Dict[str, Any]]:
        """사용자 파일 목록 조회"""
        return self.file_repo.list_files(user_id=str(user_id))
    
    def delete_file(self, file_id: str, user_id: int) -> bool:
        """파일 삭제"""
        file_info = self.file_repo.get_file(file_id)
        
        if not file_info:
            return False
        
        # 권한 확인
        if file_info.get('user_id') != str(user_id):
            raise PermissionError("You don't have permission to delete this file")
        
        # 물리적 파일 삭제
        for path_key in ['file_path', 'dataframe_path']:
            if file_info.get(path_key) and os.path.exists(file_info[path_key]):
                try:
                    os.remove(file_info[path_key])
                except Exception as e:
                    self.logger.warning(f"Failed to delete physical file: {e}")
        
        # DB에서 삭제
        return self.file_repo.delete_file(file_id)
    
    def cleanup_old_files(self, days: int = 30):
        """오래된 파일 정리"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 오래된 파일 찾기
        old_files = self.db.execute(
            "SELECT * FROM files WHERE upload_time < :cutoff",
            {"cutoff": cutoff_date}
        ).fetchall()
        
        deleted_count = 0
        for file_record in old_files:
            try:
                self.delete_file(file_record['id'], file_record['user_id'])
                deleted_count += 1
            except Exception as e:
                self.logger.error(f"Failed to delete old file {file_record['id']}: {e}")
        
        self.logger.info(f"Cleaned up {deleted_count} old files")
        return deleted_count