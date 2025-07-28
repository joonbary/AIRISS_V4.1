"""
Files API (Refactored)
서비스 레이어를 사용하는 파일 관리 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List

from app.schemas.file import FileInfo, FileUploadResponse
from app.api.v1.dependencies import get_current_active_user, get_file_service
from app.services import FileService

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """파일 업로드"""
    # 파일 확장자 검증
    if not any(file.filename.endswith(ext) for ext in ['.xlsx', '.xls', '.csv']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel (.xlsx, .xls) and CSV files are supported"
        )
    
    try:
        # 파일 업로드
        result = await file_service.upload_file(
            file.file,
            file.filename,
            current_user["id"]
        )
        
        return FileUploadResponse(
            file_id=result['file_id'],
            filename=result['filename'],
            total_records=result['total_records'],
            columns=result['columns'],
            uid_columns=result['uid_columns'],
            opinion_columns=result['opinion_columns'],
            quantitative_columns=result['quantitative_columns'],
            message="File uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/list", response_model=List[FileInfo])
async def list_files(
    current_user: dict = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """파일 목록 조회"""
    files = file_service.list_user_files(current_user["id"])
    return [FileInfo(**file) for file in files]


@router.get("/{file_id}", response_model=FileInfo)
async def get_file_info(
    file_id: str,
    current_user: dict = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """파일 정보 조회"""
    file_info = file_service.get_file_info(file_id)
    
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # 권한 확인
    if file_info.get('user_id') != str(current_user['id']) and not current_user.get('is_superuser'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return FileInfo(**file_info)


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """파일 삭제"""
    try:
        success = file_service.delete_file(file_id, current_user["id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return {"message": "File deleted successfully"}
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )