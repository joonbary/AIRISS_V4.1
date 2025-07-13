import os
import sys
from pathlib import Path

print("🔍 === USER.PY 디버깅 시작 ===")
print(f"🗂️ 현재 작업 디렉토리: {os.getcwd()}")
print(f"🗂️ Python 경로: {sys.path[:3]}")

# .env 파일 존재 및 내용 확인
env_file = Path(".env")
print(f"📄 .env 파일 존재: {env_file.exists()}")
if env_file.exists():
    print(f"📄 .env 파일 크기: {env_file.stat().st_size} bytes")
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:10]
        print("📄 .env 파일 처음 10줄:")
        for i, line in enumerate(lines, 1):
            print(f"   {i}: {line.strip()}")

# 문제가 되는 환경변수들 직접 확인
problem_vars = [
    'database_type', 'sqlite_database_url', 'postgres_database_url',
    'server_host', 'server_port', 'react_app_api_url', 
    'enable_cloud_storage', 'analysis_retention_days', 
    'react_build_path', 'environment', 'log_level'
]
print("\n🔍 문제 환경변수 직접 확인:")
for var in problem_vars:
    lower_val = os.getenv(var.lower())
    upper_val = os.getenv(var.upper())
    print(f"   {var}: lower={lower_val}, upper={upper_val}")

print("\n⚙️ Settings import 시작...")
try:
    from app.core import config
    print(f"✅ config 모듈 위치: {config.__file__}")
    print(f"🔧 Settings 클래스 존재: {hasattr(config, 'Settings')}")
    print("🎯 Settings 객체 생성 시도...")
    settings = config.Settings()
    print("✅ Settings 객체 생성 성공!")
except Exception as e:
    print(f"❌ Settings 에러 발생: {e}")
    print(f"❌ 에러 타입: {type(e)}")
    import traceback
    print("❌ 상세 스택 트레이스:")
    traceback.print_exc()
print("🔍 === USER.PY 디버깅 완료 ===\n")

from fastapi import APIRouter, HTTPException, Depends, status, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import hashlib

from app.models.user import User
from app.core.db.database import get_db
# 기존 코드 (문제 발생)
# from app.core.config.settings import Settings
# settings = Settings()
# 임시 수정 (하드코딩으로 우회)
try:
    from app.core.config.settings import Settings
    settings = Settings()
except Exception as e:
    print(f"Settings 로딩 실패, 기본값 사용: {e}")
    settings = type('Settings', (), {
        'jwt_secret_key': 'temp-secret-key',
        'jwt_algorithm': 'HS256',
        'jwt_expire_minutes': 30,
        'admin_email': 'joonbary@naver.com',
        'admin_auto_create': True
    })()

from app.schemas import LoginResponse

router = APIRouter(prefix="", tags=["user"])

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

# 로그인 (응답 포맷 프론트와 맞춤)
@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    if not db_user.is_approved:
        raise HTTPException(status_code=403, detail="관리자 승인 대기 중입니다.")
    access_token = create_access_token({"sub": db_user.email, "user_id": db_user.id, "is_admin": db_user.is_admin})
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