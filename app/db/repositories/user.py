"""
User Repository
사용자 관련 데이터베이스 작업
"""

from typing import Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """사용자 관리 리포지토리"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 생성"""
        # Hash password
        hashed_password = pwd_context.hash(user_data['password'])
        
        sql = text("""
            INSERT INTO users (
                username, email, hashed_password, full_name,
                is_active, is_superuser, created_at, updated_at
            ) VALUES (
                :username, :email, :hashed_password, :full_name,
                :is_active, :is_superuser, :created_at, :updated_at
            ) RETURNING id, username, email, full_name, is_active, is_superuser, created_at
        """)
        
        result = self.db.execute(sql, {
            'username': user_data['username'],
            'email': user_data['email'],
            'hashed_password': hashed_password,
            'full_name': user_data.get('full_name', ''),
            'is_active': user_data.get('is_active', True),
            'is_superuser': user_data.get('is_superuser', False),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }).fetchone()
        
        self.db.commit()
        
        user_dict = dict(result._mapping)
        # Convert datetime
        for key, value in user_dict.items():
            if isinstance(value, datetime):
                user_dict[key] = value.isoformat()
        
        return user_dict
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """사용자명으로 사용자 조회"""
        result = self.db.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {'username': username}
        ).fetchone()
        
        if result:
            user_dict = dict(result._mapping)
            # Convert datetime
            for key, value in user_dict.items():
                if isinstance(value, datetime):
                    user_dict[key] = value.isoformat()
            return user_dict
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """이메일로 사용자 조회"""
        result = self.db.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {'email': email}
        ).fetchone()
        
        if result:
            user_dict = dict(result._mapping)
            # Convert datetime
            for key, value in user_dict.items():
                if isinstance(value, datetime):
                    user_dict[key] = value.isoformat()
            return user_dict
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """ID로 사용자 조회"""
        result = self.db.execute(
            text("SELECT * FROM users WHERE id = :user_id"),
            {'user_id': user_id}
        ).fetchone()
        
        if result:
            user_dict = dict(result._mapping)
            # Convert datetime
            for key, value in user_dict.items():
                if isinstance(value, datetime):
                    user_dict[key] = value.isoformat()
            return user_dict
        return None
    
    def verify_password(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """사용자 인증"""
        # Try to find user by username first, then by email
        user = self.get_user_by_username(username)
        if not user:
            # If not found by username, try email
            user = self.get_user_by_email(username)
        
        if not user:
            return None
        
        if pwd_context.verify(password, user['hashed_password']):
            # Remove password from response
            user.pop('hashed_password', None)
            return user
        
        return None
    
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """사용자 정보 업데이트"""
        update_fields = []
        params = {'user_id': user_id, 'updated_at': datetime.utcnow()}
        
        for key, value in update_data.items():
            if key in ['email', 'full_name', 'is_active', 'is_superuser']:
                update_fields.append(f"{key} = :{key}")
                params[key] = value
            elif key == 'password':
                # Hash new password
                hashed_password = pwd_context.hash(value)
                update_fields.append("hashed_password = :hashed_password")
                params['hashed_password'] = hashed_password
        
        if not update_fields:
            return None
        
        update_fields.append("updated_at = :updated_at")
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = :user_id"
        result = self.db.execute(text(query), params)
        self.db.commit()
        
        if result.rowcount > 0:
            return self.get_user_by_id(user_id)
        return None
    
    def delete_user(self, user_id: int) -> bool:
        """사용자 삭제"""
        result = self.db.execute(
            text("DELETE FROM users WHERE id = :user_id"),
            {'user_id': user_id}
        )
        self.db.commit()
        return result.rowcount > 0