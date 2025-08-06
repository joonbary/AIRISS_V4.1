"""
File Model
업로드된 파일 정보 모델
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, BigInteger, Text
from sqlalchemy.sql import func
from app.db.database import Base


class File(Base):
    __tablename__ = "files"
    
    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    
    total_records = Column(Integer, default=0)
    columns = Column(Text)  # JSON
    uid_columns = Column(Text)  # JSON
    opinion_columns = Column(Text)  # JSON
    quantitative_columns = Column(Text)  # JSON
    
    file_path = Column(String(500))
    
    user_id = Column(String(255))
    session_id = Column(String(255))
    size = Column(BigInteger, default=0)