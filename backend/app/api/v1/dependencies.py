"""
API Dependencies
공통 의존성 및 유틸리티
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from app.db import get_db
from app.core.config import settings
from app.core.security import decode_access_token
from app.services import UserService, FileService, AnalysisService

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    """현재 인증된 사용자 조회"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 토큰 디코드
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # 사용자 조회
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """활성 사용자만 허용"""
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """관리자만 허용"""
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Service dependencies
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """UserService 인스턴스"""
    return UserService(db)


def get_file_service(db: Session = Depends(get_db)) -> FileService:
    """FileService 인스턴스"""
    return FileService(db)


def get_analysis_service(db: Session = Depends(get_db)) -> AnalysisService:
    """AnalysisService 인스턴스"""
    return AnalysisService(db)