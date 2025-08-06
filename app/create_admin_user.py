import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin_user():
    db = SessionLocal()
    try:
        # 기존 관리자 삭제(강제 덮어쓰기)
        admin = db.query(User).filter(User.email == "admin@test.com").first()
        if admin:
            db.delete(admin)
            db.commit()
        
        # 관리자 생성
        admin = User(
            email="admin@test.com",
            name="Admin User",
            is_admin=True,
            is_approved=True,
            password_hash=get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()
        print("✅ 관리자 계정 생성 완료!")
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()