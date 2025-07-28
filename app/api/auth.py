from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str

@router.post("/user/register")
async def register_user(request: RegisterRequest):
    return {"message": "회원가입 성공"}

# 관리자 승인 관련 모델 및 엔드포인트
class ApproveRequest(BaseModel):
    user_id: int
    approve: bool

# 승인 대기 사용자 목록 조회
@router.get("/user/pending")
async def get_pending_users():
    # TODO: 실제 DB에서 승인 대기 중인 사용자 목록을 조회해야 함
    return [
        {"user_id": 1, "email": "test@ex.com", "name": "홍길동"},
        {"user_id": 2, "email": "user2@ex.com", "name": "김철수"}
    ]

# 관리자 승인/거부 처리
@router.post("/user/approve")
async def approve_user(request: ApproveRequest):
    # TODO: 실제 DB에서 해당 user_id의 승인 상태를 변경해야 함
    if request.approve:
        # 승인 처리
        return {"message": "승인 완료"}
    else:
        # 거부 처리
        return {"message": "거부 처리됨"}

# JWT 설정 (실제로는 환경변수로 관리)
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: dict

@router.post("/user/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    로그인 처리 (username 필드로 이메일 전달됨)
    프론트엔드에서 'username', 'password' 필드로 x-www-form-urlencoded 전송
    """
    print("[DEBUG] username:", repr(form_data.username))
    print("[DEBUG] password:", repr(form_data.password))
    # TODO: 실제 DB에서 사용자 검증
    # 임시로 테스트 계정만 허용
    if form_data.username == "joonbary@naver.com" and form_data.password == "1234":
        # JWT 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": form_data.username},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "email": form_data.username,
                "name": "테스트 사용자",
                "is_approved": True,
                "is_admin": False
            }
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다 (username 필드로 이메일 전달 필요)",
            headers={"WWW-Authenticate": "Bearer"},
        )

def create_access_token(data: dict, expires_delta: timedelta = None):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/user/me")
async def get_current_user():
    """현재 로그인한 사용자 정보 반환 (임시)"""
    # TODO: JWT 토큰에서 사용자 정보 추출
    return {
        "email": "joondary@naver.com",
        "name": "테스트 사용자",
        "is_approved": True,
        "is_admin": False
    } 