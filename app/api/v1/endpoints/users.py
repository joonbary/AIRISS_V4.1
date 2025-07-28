"""
Users API
사용자 관리 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db, UserRepository
from app.schemas.user import UserResponse, UserUpdate
from app.core.dependencies import get_current_user

router = APIRouter()


def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """활성 사용자만 허용"""
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_superuser(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """관리자만 허용"""
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: dict = Depends(get_current_active_user)
):
    """현재 사용자 정보 조회"""
    return UserResponse(**current_user)


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """현재 사용자 정보 수정"""
    user_repo = UserRepository(db)
    
    update_data = user_update.dict(exclude_unset=True)
    updated_user = user_repo.update_user(current_user["id"], update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    return UserResponse(**updated_user)


@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_superuser)
):
    """모든 사용자 목록 조회 (관리자 전용)"""
    users = db.execute(
        "SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :skip",
        {"limit": limit, "skip": skip}
    ).fetchall()
    
    return [UserResponse(**dict(user._mapping)) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_superuser)
):
    """특정 사용자 정보 조회 (관리자 전용)"""
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_superuser)
):
    """사용자 정보 수정 (관리자 전용)"""
    user_repo = UserRepository(db)
    
    update_data = user_update.dict(exclude_unset=True)
    updated_user = user_repo.update_user(user_id, update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**updated_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_superuser)
):
    """사용자 삭제 (관리자 전용)"""
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    user_repo = UserRepository(db)
    success = user_repo.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}