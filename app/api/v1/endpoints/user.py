from fastapi import APIRouter, HTTPException, Depends, status, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import hashlib

from app.models.user import User
from app.core.db.database import get_db
from app.core.config.settings import Settings

router = APIRouter(prefix="/user", tags=["user"])
settings = Settings()

# 유틸: 비밀번호 해시

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hash_: str) -> bool:
    return hash_password(password) == hash_

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Pydantic 스키마
class UserRegister(BaseModel):
    email: str
    name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    is_approved: bool
    is_admin: bool
    created_at: datetime

class UserApprove(BaseModel):
    user_id: int
    approve: bool

# 회원가입
@router.post("/register", response_model=UserOut)
def register(user: UserRegister, db: Session = Depends(get_db)):
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

# 로그인
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    if not db_user.is_approved:
        raise HTTPException(status_code=403, detail="관리자 승인 대기 중입니다.")
    access_token = create_access_token({"sub": db_user.email, "user_id": db_user.id, "is_admin": db_user.is_admin})
    return {"access_token": access_token, "token_type": "bearer"}

# 내 정보
@router.get("/me", response_model=UserOut)
def get_me(db: Session = Depends(get_db), token: str = Depends(lambda: None)):
    # 실제 구현에서는 OAuth2PasswordBearer 등으로 토큰 파싱 필요
    # 여기서는 간단히 토큰에서 이메일 추출
    if not token:
        raise HTTPException(status_code=401, detail="토큰이 필요합니다.")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return db_user

# 관리자: 승인/거부
@router.post("/approve")
def approve_user(data: UserApprove, db: Session = Depends(get_db), token: str = Depends(lambda: None)):
    # 실제 구현에서는 토큰에서 is_admin 체크 필요
    if not token:
        raise HTTPException(status_code=401, detail="토큰이 필요합니다.")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자만 승인할 수 있습니다.")
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    db_user = db.query(User).filter(User.id == data.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    db_user.is_approved = data.approve
    db.commit()
    return {"user_id": db_user.id, "is_approved": db_user.is_approved}

# 승인 대기 목록
@router.get("/pending", response_model=List[UserOut])
def get_pending_users(db: Session = Depends(get_db), token: str = Depends(lambda: None)):
    # 실제 구현에서는 토큰에서 is_admin 체크 필요
    if not token:
        raise HTTPException(status_code=401, detail="토큰이 필요합니다.")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자만 조회할 수 있습니다.")
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    users = db.query(User).filter(User.is_approved == False).all()
    return users 