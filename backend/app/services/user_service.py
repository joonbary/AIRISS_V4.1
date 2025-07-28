"""
User Service
사용자 관리를 담당하는 서비스
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import jwt

from .base import BaseService
from app.db.repositories import UserRepository
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token


class UserService(BaseService):
    """사용자 관리 서비스"""
    
    def __init__(self, db):
        super().__init__(db)
        self.user_repo = UserRepository(db)
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 생성"""
        # 중복 확인
        if self.user_repo.get_user_by_username(user_data['username']):
            raise ValueError("Username already exists")
        
        if self.user_repo.get_user_by_email(user_data['email']):
            raise ValueError("Email already exists")
        
        # 사용자 생성
        user = self.user_repo.create_user(user_data)
        
        # 비밀번호 제거
        user.pop('hashed_password', None)
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """사용자 인증"""
        user = self.user_repo.verify_password(username, password)
        
        if not user:
            return None
        
        if not user.get('is_active'):
            raise ValueError("User account is inactive")
        
        return user
    
    def create_user_token(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 토큰 생성"""
        # 토큰 페이로드
        token_data = {
            "sub": user['username'],
            "user_id": user['id'],
            "is_superuser": user.get('is_superuser', False)
        }
        
        # 액세스 토큰 생성
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=token_data,
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
        }
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """ID로 사용자 조회"""
        user = self.user_repo.get_user_by_id(user_id)
        if user:
            user.pop('hashed_password', None)
        return user
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """사용자명으로 조회"""
        user = self.user_repo.get_user_by_username(username)
        if user:
            user.pop('hashed_password', None)
        return user
    
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 정보 업데이트"""
        # 이메일 중복 확인
        if 'email' in update_data:
            existing = self.user_repo.get_user_by_email(update_data['email'])
            if existing and existing['id'] != user_id:
                raise ValueError("Email already exists")
        
        # 업데이트
        user = self.user_repo.update_user(user_id, update_data)
        
        if not user:
            raise ValueError("User not found")
        
        user.pop('hashed_password', None)
        return user
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """비밀번호 변경"""
        # 현재 사용자 조회
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # 현재 비밀번호 확인
        if not verify_password(current_password, user['hashed_password']):
            raise ValueError("Current password is incorrect")
        
        # 새 비밀번호 설정
        self.user_repo.update_user(user_id, {'password': new_password})
        
        return True
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """사용자 목록 조회"""
        users = self.db.execute(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :skip",
            {"limit": limit, "skip": skip}
        ).fetchall()
        
        # 비밀번호 제거
        user_list = []
        for user in users:
            user_dict = dict(user._mapping)
            user_dict.pop('hashed_password', None)
            user_list.append(user_dict)
        
        return user_list
    
    def delete_user(self, user_id: int) -> bool:
        """사용자 삭제"""
        return self.user_repo.delete_user(user_id)
    
    def create_admin_user(self) -> Dict[str, Any]:
        """관리자 계정 생성"""
        admin_data = {
            'username': settings.FIRST_SUPERUSER,
            'email': settings.FIRST_SUPERUSER_EMAIL,
            'password': settings.FIRST_SUPERUSER_PASSWORD,
            'full_name': 'System Administrator',
            'is_active': True,
            'is_superuser': True
        }
        
        # 이미 존재하는지 확인
        existing = self.user_repo.get_user_by_username(admin_data['username'])
        if existing:
            self.logger.info("Admin user already exists")
            return existing
        
        # 생성
        admin = self.user_repo.create_user(admin_data)
        self.logger.info("Admin user created successfully")
        
        admin.pop('hashed_password', None)
        return admin
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """사용자 통계"""
        total_users = self.db.execute("SELECT COUNT(*) FROM users").scalar()
        active_users = self.db.execute("SELECT COUNT(*) FROM users WHERE is_active = true").scalar()
        admin_users = self.db.execute("SELECT COUNT(*) FROM users WHERE is_superuser = true").scalar()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'inactive_users': total_users - active_users
        }