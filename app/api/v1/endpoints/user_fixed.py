"""
user_fixed.py - 수정된 사용자 인증 및 관리 엔드포인트
"""

from datetime import datetime, timedelta
from typing import Optional, List
import hashlib
import jwt
import bcrypt

from fastapi import APIRouter, HTTPException, Depends, status, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError

# 수정된 import 경로
from app.models.user import User
from app.db.database import get_db
from app.schemas.schemas import LoginResponse

# 기본 설정값
JWT_SECRET_KEY = 'temp-secret-key'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES = 30

router = APIRouter(tags=["user"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


def hash_password(password: str) -> str:
    """bcrypt로 비밀번호 해싱"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hash_: str) -> bool:
    """bcrypt로 비밀번호와 해시값 비교"""
    return bcrypt.checkpw(password.encode(), hash_.encode())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


class UserRegister(BaseModel):
    """회원가입 요청 스키마"""
    email: str
    name: str
    password: str


class UserLogin(BaseModel):
    """로그인 요청 스키마"""
    email: str
    password: str


class UserOut(BaseModel):
    """사용자 정보 응답 스키마"""
    id: int
    email: str
    name: str
    is_approved: bool
    is_admin: bool
    created_at: datetime


class UserApprove(BaseModel):
    """사용자 승인/거부 요청 스키마"""
    user_id: int
    approve: bool


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.post("/register", response_model=UserOut)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """회원가입 엔드포인트"""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")
    db_user = User(
        email=user.email,
        name=user.name,
        password_hash=hash_password(user.password),
        is_approved=False,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 표준 폼 기반 로그인 엔드포인트 (username에 email 입력)"""
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not db_user.is_approved:
        raise HTTPException(status_code=403, detail="관리자 승인 대기 중입니다.")
    access_token = create_access_token({
        "sub": db_user.email,
        "user_id": db_user.id,
        "is_admin": db_user.is_admin
    })
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_info={
            "id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "is_approved": db_user.is_approved,
            "is_admin": db_user.is_admin,
            "created_at": db_user.created_at.isoformat() if hasattr(db_user, 'created_at') else None
        }
    )


@router.get("/me", response_model=UserOut)
def get_me(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """내 정보 조회 엔드포인트 (토큰 필요)"""
    if not token:
        raise HTTPException(status_code=401, detail="토큰이 필요합니다.")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.") from exc
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return db_user


@router.post("/approve")
def approve_user(data: UserApprove, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """관리자: 사용자 승인/거부 엔드포인트 (토큰 필요)"""
    if not token:
        raise HTTPException(status_code=401, detail="토큰이 필요합니다.")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자만 승인할 수 있습니다.")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.") from exc
    db_user = db.query(User).filter(User.id == data.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    db_user.is_approved = data.approve
    db.commit()
    return {"user_id": db_user.id, "is_approved": db_user.is_approved}


@router.get("/pending", response_model=List[UserOut])
def get_pending_users(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """관리자: 승인 대기 사용자 목록 조회 (토큰 필요)"""
    if not token:
        raise HTTPException(status_code=401, detail="토큰이 필요합니다.")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자만 조회할 수 있습니다.")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.") from exc
    users = db.query(User).filter(User.is_approved.is_(False)).all()
    return users


@router.put("/change-password")
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """비밀번호 변경 엔드포인트 (토큰 필요)"""
    if not token:
        raise HTTPException(status_code=401, detail="토큰이 필요합니다.")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.") from exc
    
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    # 현재 비밀번호 확인
    if not verify_password(password_data.current_password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 일치하지 않습니다.")
    
    # 새 비밀번호 설정
    db_user.password_hash = hash_password(password_data.new_password)
    db.commit()
    
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}


@router.get("/test")
def test_endpoint():
    """테스트 엔드포인트"""
    return {"message": "User router is working!"}