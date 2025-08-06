import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db.database import SessionLocal
from app.models.user import User


def approve_test_user():
    db = SessionLocal()
    try:
        # test@test.com 사용자 찾기
        user = db.query(User).filter(User.email == "test@test.com").first()

        if user:
            user.is_approved = True
            db.commit()
            print(f"✅ {user.email} 사용자가 승인되었습니다!")
            print(f"   Name: {user.name}")
            print(f"   Is Admin: {user.is_admin}")
            print(f"   Is Approved: {user.is_approved}")
        else:
            print("❌ test@test.com 사용자를 찾을 수 없습니다.")

    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    approve_test_user() 