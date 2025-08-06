"""
User Schemas
사용자 관련 Pydantic 모델
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """사용자 기본 정보"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """사용자 생성"""
    password: str


class UserLogin(BaseModel):
    """사용자 로그인"""
    username: str
    password: str


class UserUpdate(BaseModel):
    """사용자 정보 업데이트"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """사용자 응답"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """인증 토큰"""
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    """토큰 데이터"""
    username: Optional[str] = None