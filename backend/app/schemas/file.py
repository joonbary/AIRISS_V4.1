"""
File Schemas
파일 관련 Pydantic 모델
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class FileInfo(BaseModel):
    """파일 정보"""
    id: str
    filename: str
    upload_time: datetime
    total_records: int
    columns: List[str]
    uid_columns: List[str]
    opinion_columns: List[str]
    quantitative_columns: List[str]
    size: int
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """파일 업로드 응답"""
    file_id: str
    filename: str
    total_records: int
    columns: List[str]
    uid_columns: List[str]
    opinion_columns: List[str]
    quantitative_columns: List[str]
    message: str