"""
Authentication API (Refactored)
서비스 레이어를 사용하는 인증 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import UserCreate, UserResponse, Token
from app.api.v1.dependencies import get_user_service
from app.services import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """사용자 등록"""
    try:
        user = user_service.create_user(user_data.dict())
        return UserResponse(**user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    """사용자 로그인"""
    # 인증
    user = user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 생성
    token_data = user_service.create_user_token(user)
    
    return Token(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        user=UserResponse(**user)
    )