from fastapi import APIRouter
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