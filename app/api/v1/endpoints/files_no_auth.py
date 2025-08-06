"""
Files API - No Authentication Version
파일 업로드 및 관리 엔드포인트 (인증 없음)
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import os
import uuid
from datetime import datetime

from app.db import get_db, FileRepository
from app.schemas.file import FileInfo, FileUploadResponse
from app.core.config import settings

router = APIRouter()


def analyze_file_structure(df: pd.DataFrame) -> dict:
    """파일 구조 분석"""
    columns = list(df.columns)
    
    # UID 컬럼 찾기
    uid_columns = []
    for col in columns:
        col_lower = col.lower()
        if any(uid in col_lower for uid in ['uid', '사번', 'employee', 'emp_id', 'id']):
            uid_columns.append(col)
    
    # Opinion 컬럼 찾기
    opinion_columns = []
    for col in columns:
        col_lower = col.lower()
        if any(op in col_lower for op in ['opinion', '의견', 'comment', 'feedback', 'text']):
            opinion_columns.append(col)
    
    # Quantitative 컬럼 찾기
    quantitative_columns = []
    for col in columns:
        if df[col].dtype in ['int64', 'float64']:
            quantitative_columns.append(col)
    
    return {
        "columns": columns,
        "uid_columns": uid_columns,
        "opinion_columns": opinion_columns,
        "quantitative_columns": quantitative_columns,
        "total_records": len(df)
    }


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """파일 업로드 - Public Access"""
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel (.xlsx, .xls) and CSV files are supported"
        )
    
    # Generate file ID
    file_id = str(uuid.uuid4())
    
    # Save file
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
    
    # Save uploaded file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Read and analyze file
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Analyze structure
        structure = analyze_file_structure(df)
        
        # Save DataFrame as pickle for faster loading
        pickle_path = file_path.replace('.xlsx', '.pkl').replace('.xls', '.pkl').replace('.csv', '.pkl')
        df.to_pickle(pickle_path)
        
        # Save to database (no user_id required)
        file_repo = FileRepository(db)
        file_data = {
            "id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "dataframe_path": pickle_path,
            "user_id": "public",  # Public access - no specific user
            "size": len(content),
            **structure
        }
        
        file_id = file_repo.save_file(file_data)
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            total_records=structure["total_records"],
            columns=structure["columns"],
            uid_columns=structure["uid_columns"],
            opinion_columns=structure["opinion_columns"],
            quantitative_columns=structure["quantitative_columns"],
            message="File uploaded successfully"
        )
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process file: {str(e)}"
        )


@router.get("/list", response_model=List[FileInfo])
async def list_files(
    db: Session = Depends(get_db)
):
    """파일 목록 조회 - Public Access"""
    file_repo = FileRepository(db)
    # Public access - return all files
    files = file_repo.list_files()
    
    return [FileInfo(**file) for file in files]


@router.get("/{file_id}", response_model=FileInfo)
async def get_file_info(
    file_id: str,
    db: Session = Depends(get_db)
):
    """파일 정보 조회 - Public Access"""
    file_repo = FileRepository(db)
    file_info = file_repo.get_file(file_id)
    
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Remove dataframe from response
    file_info.pop('dataframe', None)
    
    return FileInfo(**file_info)


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db)
):
    """파일 삭제 - Public Access"""
    file_repo = FileRepository(db)
    
    # Get file info first
    file_info = file_repo.get_file(file_id)
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete physical files
    for path_key in ['file_path', 'dataframe_path']:
        if file_info.get(path_key) and os.path.exists(file_info[path_key]):
            try:
                os.remove(file_info[path_key])
            except:
                pass
    
    # Delete from database
    success = file_repo.delete_file(file_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
    
    return {"message": "File deleted successfully"}