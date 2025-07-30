"""
File Repository
파일 관련 데이터베이스 작업
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
import json
import uuid
import os
import logging
import pandas as pd
import pickle

logger = logging.getLogger(__name__)


class FileRepository:
    """파일 관리 리포지토리"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_file(self, file_data: Dict[str, Any]) -> str:
        """파일 정보 저장"""
        file_id = file_data.get('id', str(uuid.uuid4()))
        
        sql = text("""
            INSERT INTO files (
                id, filename, upload_time, total_records,
                columns, uid_columns, opinion_columns,
                quantitative_columns, file_path, user_id, session_id, size
            ) VALUES (
                :id, :filename, :upload_time, :total_records,
                :columns, :uid_columns, :opinion_columns,
                :quantitative_columns, :file_path, :user_id, :session_id, :size
            )
        """)
        
        self.db.execute(sql, {
            'id': file_id,
            'filename': file_data.get('filename'),
            'upload_time': file_data.get('upload_time', datetime.utcnow()),
            'total_records': file_data.get('total_records', 0),
            'columns': json.dumps(file_data.get('columns', [])),
            'uid_columns': json.dumps(file_data.get('uid_columns', [])),
            'opinion_columns': json.dumps(file_data.get('opinion_columns', [])),
            'quantitative_columns': json.dumps(file_data.get('quantitative_columns', [])),
            'file_path': file_data.get('file_path', ''),
            'user_id': file_data.get('user_id', ''),
            'session_id': file_data.get('session_id', ''),
            'size': file_data.get('size', 0)
        })
        
        self.db.commit()
        return file_id
    
    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """파일 정보 조회 (DataFrame 포함)"""
        result = self.db.execute(
            text("SELECT * FROM files WHERE id = :file_id"),
            {'file_id': file_id}
        ).fetchone()
        
        if not result:
            return None
        
        file_data = dict(result._mapping)
        
        # Convert datetime to string and JSON strings to lists
        for key, value in file_data.items():
            if isinstance(value, datetime):
                file_data[key] = value.isoformat()
            # Convert JSON strings to lists for column fields
            elif key in ['columns', 'uid_columns', 'opinion_columns', 'quantitative_columns']:
                if isinstance(value, str):
                    try:
                        file_data[key] = json.loads(value) if value else []
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON for {key}: {value}")
                        file_data[key] = []
                else:
                    file_data[key] = value if value else []
        
        # Load DataFrame
        file_data['dataframe'] = self._load_dataframe(file_data)
        
        return file_data
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """파일 메타데이터만 조회 (DataFrame 로드 없이)"""
        result = self.db.execute(
            text("SELECT * FROM files WHERE id = :file_id"),
            {'file_id': file_id}
        ).fetchone()
        
        if not result:
            return None
        
        file_data = dict(result._mapping)
        
        # Convert datetime to string and JSON strings to lists
        for key, value in file_data.items():
            if isinstance(value, datetime):
                file_data[key] = value.isoformat()
            # Convert JSON strings to lists for column fields
            elif key in ['columns', 'uid_columns', 'opinion_columns', 'quantitative_columns']:
                if isinstance(value, str):
                    try:
                        file_data[key] = json.loads(value) if value else []
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON for {key}: {value}")
                        file_data[key] = []
                else:
                    file_data[key] = value if value else []
        
        return file_data
    
    def _load_dataframe(self, file_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """DataFrame 로드"""
        try:
            # Try original file
            file_path = file_data.get('file_path', '')
            if not file_path:
                file_path = f'temp_data/{file_data["id"]}.pkl'
            
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info(f"Loading file: {file_path} ({file_size} bytes)")
                
                if file_size == 0:
                    logger.error(f"File is empty: {file_path}")
                    return None
                
                if file_path.endswith('.pkl'):
                    with open(file_path, 'rb') as f:
                        df = pickle.load(f)
                elif file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path, engine='openpyxl')
                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    logger.warning(f"Unsupported file format: {file_path}")
                    return None
                
                if df is not None and len(df) > 0:
                    logger.info(f"DataFrame loaded: {len(df)} rows, {len(df.columns)} columns")
                    return df
            
            logger.warning(f"Failed to load DataFrame for file {file_data.get('id')}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading DataFrame: {e}")
            return None
    
    def list_files(self, user_id: Optional[str] = None, 
                  session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """파일 목록 조회"""
        where_clauses = []
        params = {}
        
        if user_id and session_id:
            where_clauses.append("(user_id = :user_id OR session_id = :session_id)")
            params['user_id'] = user_id
            params['session_id'] = session_id
        elif user_id:
            where_clauses.append("user_id = :user_id")
            params['user_id'] = user_id
        elif session_id:
            where_clauses.append("session_id = :session_id")
            params['session_id'] = session_id
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
        sql = f"SELECT * FROM files {where_sql} ORDER BY upload_time DESC"
        
        results = self.db.execute(text(sql), params).fetchall()
        
        files = []
        for row in results:
            file_dict = dict(row._mapping)
            # Convert datetime and JSON strings
            for key, value in file_dict.items():
                if isinstance(value, datetime):
                    file_dict[key] = value.isoformat()
                # Convert JSON strings to lists for column fields
                elif key in ['columns', 'uid_columns', 'opinion_columns', 'quantitative_columns']:
                    if isinstance(value, str):
                        try:
                            file_dict[key] = json.loads(value) if value else []
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON for {key}: {value}")
                            file_dict[key] = []
                    else:
                        file_dict[key] = value if value else []
            files.append(file_dict)
        
        return files
    
    def delete_file(self, file_id: str) -> bool:
        """파일 삭제"""
        result = self.db.execute(
            text("DELETE FROM files WHERE id = :file_id"),
            {'file_id': file_id}
        )
        self.db.commit()
        return result.rowcount > 0
    
    def update_file(self, file_id: str, update_data: Dict[str, Any]) -> bool:
        """파일 정보 업데이트"""
        update_fields = []
        params = {'file_id': file_id}
        
        for key, value in update_data.items():
            if key in ['total_records', 'columns', 'uid_columns', 'opinion_columns', 'quantitative_columns', 'file_path']:
                update_fields.append(f"{key} = :{key}")
                if key in ['columns', 'uid_columns', 'opinion_columns', 'quantitative_columns']:
                    params[key] = json.dumps(value) if isinstance(value, (list, dict)) else value
                else:
                    params[key] = value
        
        if not update_fields:
            return False
        
        query = f"UPDATE files SET {', '.join(update_fields)} WHERE id = :file_id"
        result = self.db.execute(text(query), params)
        self.db.commit()
        
        return result.rowcount > 0